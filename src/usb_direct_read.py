# -*- coding: utf-8 -*-
"""
usb_direct_read.py
===================
Direct USB Bulk Reader using libusb via ctypes.
Bypasses PTY creation and serial bridges entirely.
Reads from Endpoint 2 (0x82) and writes to log file.
"""

import os
import sys
import time
import ctypes

LOG_PATH = "/data/data/com.termux/files/home/TAP_model/assets/live_qubit_data.log"

# Define ctypes structures and prototypes
class libusb_context(ctypes.Structure):
    pass

class libusb_device_handle(ctypes.Structure):
    pass

def write_cv(libusb, handle, req, val, index):
    # bmRequestType = 0x40 (Vendor, Device, Out)
    r = libusb.libusb_control_transfer(
        handle, 0x40, req, val, index, None, 0, 1000
    )
    return r

def ch340_init(libusb, handle, baud):
    # 1. Probe sequence
    write_cv(libusb, handle, 0xa1, 0, 0)
    write_cv(libusb, handle, 0x9a, 0x2518, 0x0050)
    write_cv(libusb, handle, 0xa1, 0x501f, 0xd90a)
    
    # 2. Set Baud Rate
    if baud == 115200:
        div1, div2 = 0xcc03, 0x0008
    elif baud == 57600:
        div1, div2 = 0x9803, 0x0010
    else:
        raise ValueError(f"Unsupported baud rate: {baud}")
        
    write_cv(libusb, handle, 0x9a, 0x1312, div1)
    write_cv(libusb, handle, 0x9a, 0x0f2c, div2)
    
    # 3. Set Flow Control (None) / DTR-RTS deasserted (0xFF)
    write_cv(libusb, handle, 0xa4, 0xFF, 0)

def main():
    if len(sys.argv) < 2:
        print("Usage: termux-usb -r -e 'python src/usb_direct_read.py' <device>")
        return
        
    fd = int(sys.argv[1])
    
    with open(LOG_PATH, "w", encoding="utf-8") as log_file:
        log_file.write("==================================================\n")
        log_file.write("  TAP DIRECT USB LOG STREAM STARTED\n")
        log_file.write(f"  Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write("==================================================\n")
        log_file.flush()
        
        try:
            # Load libusb-1.0 library
            try:
                libusb = ctypes.CDLL("libusb-1.0.so")
            except OSError:
                libusb = ctypes.CDLL("libusb.so")
                
            # Disable device discovery to allow running on Android without bus permissions
            libusb.libusb_set_option(None, 2)

            # Initialize libusb context
            ctx = ctypes.c_void_p()
            r = libusb.libusb_init(ctypes.byref(ctx))
            if r < 0:
                log_file.write(f"❌ libusb_init failed: {r}\n")
                log_file.flush()
                return
                
            # Wrap standard Android/Termux USB file descriptor
            handle = ctypes.c_void_p()
            r = libusb.libusb_wrap_sys_device(ctx, fd, ctypes.byref(handle))
            if r < 0:
                log_file.write(f"❌ libusb_wrap_sys_device failed: {r}\n")
                log_file.flush()
                return
                
            # Claim interface 0 (CH340 default interface)
            r = libusb.libusb_claim_interface(handle, 0)
            if r < 0:
                log_file.write(f"❌ libusb_claim_interface failed: {r}\n")
                log_file.flush()
                return
                
            # Initialize CH340 serial parameters and baud rate (115200 baud)
            try:
                ch340_init(libusb, handle, 115200)
                log_file.write("⚡ CH340 Serial Configured (115200 Baud, 8N1, DTR/RTS High).\n")
            except Exception as ex:
                log_file.write(f"⚠️ CH340 initialization failed: {ex}\n")
                log_file.flush()
                
            log_file.write("📡 USB Interface Claimed. Streaming data...\n")
            log_file.flush()
            
            # Buffer for bulk read
            buf = ctypes.create_string_buffer(4096)
            transferred = ctypes.c_int(0)
            
            while True:
                # Perform Bulk read on Endpoint 2 (IN direction = 0x82)
                # Timeout is 1000ms
                r = libusb.libusb_bulk_transfer(
                    handle, 
                    0x82, 
                    buf, 
                    ctypes.sizeof(buf), 
                    ctypes.byref(transferred), 
                    1000
                )
                
                # Check for successfully read bytes (r == 0 or timeout but bytes read)
                if transferred.value > 0:
                    data = buf.raw[:transferred.value]
                    text = data.decode('utf-8', errors='ignore')
                    log_file.write(text)
                    log_file.flush()
                
                # If error is not a timeout (LIBUSB_ERROR_TIMEOUT = -7), exit loop
                if r < 0 and r != -7:
                    log_file.write(f"\n❌ Bulk transfer error: {r}\n")
                    log_file.flush()
                    break
                    
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            log_file.write("\n[STOP] Direct monitor halted.\n")
            log_file.flush()
        except Exception as e:
            log_file.write(f"\n❌ General error: {e}\n")
            log_file.flush()

if __name__ == "__main__":
    main()
