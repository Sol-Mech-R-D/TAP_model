# -*- coding: utf-8 -*-
"""
flash_arduino.py
================
Pure Python STK500v1 bootloader client to flash Arduino Nano (Atmega328p)
directly from Termux over USB-C serial.
Bypasses the need for avrdude.
"""

import sys
import os
import time
import serial

# STK500v1 constants
STK_OK = 0x10
STK_INSYNC = 0x14
STK_GET_SYNC = 0x30
STK_SET_DEVICE = 0x42
STK_ENTER_PROGMODE = 0x50
STK_LOAD_ADDRESS = 0x55
STK_PROG_PAGE = 0x64
STK_LEAVE_PROGMODE = 0x51
SYNC_SZ = 0x20

def parse_hex_line(line):
    # Parses a single Intel Hex record line
    if not line.startswith(':'):
        return None
    byte_count = int(line[1:3], 16)
    address = int(line[3:7], 16)
    record_type = int(line[7:9], 16)
    data = bytes.fromhex(line[9:9+byte_count*2])
    checksum = int(line[9+byte_count*2:9+byte_count*2+2], 16)
    return record_type, address, data

def load_hex(hex_path):
    # Loads Intel Hex file and returns program data as a continuous bytearray
    flash = bytearray(32256) # max program size for Atmega328p Optiboot
    max_addr = 0
    with open(hex_path, 'r') as f:
        for line in f:
            parsed = parse_hex_line(line.strip())
            if not parsed:
                continue
            record_type, address, data = parsed
            if record_type == 0:  # Data record
                flash[address:address+len(data)] = data
                if address + len(data) > max_addr:
                    max_addr = address + len(data)
            elif record_type == 1:  # EOF record
                break
    # Round to page size (128 bytes)
    pages = (max_addr + 127) // 128
    return bytes(flash[:pages*128])

def send_cmd(ser, cmd):
    ser.write(bytes(cmd))
    res = ser.read(2)
    if len(res) == 2 and res[0] == STK_INSYNC and res[1] == STK_OK:
        return True
    return False

def flash_device(ser, program_bytes):
    print("  [CONN] Sending sync packages...")
    # Get sync
    for _ in range(5):
        ser.write(bytes([STK_GET_SYNC, SYNC_SZ]))
        res = ser.read(2)
        if len(res) == 2 and res[0] == STK_INSYNC and res[1] == STK_OK:
            break
        time.sleep(0.05)
    else:
        print("  ❌ Failed to sync with Arduino. Try pressing the Reset button.")
        return False
        
    print("  ✅ Synchronized successfully.")
    
    # Enter programming mode
    send_cmd(ser, [STK_ENTER_PROGMODE, SYNC_SZ])
    
    # Flash pages
    page_size = 128
    total_pages = len(program_bytes) // page_size
    print(f"  [FLASH] Programming {len(program_bytes)} bytes ({total_pages} pages)...")
    
    for page in range(total_pages):
        addr = (page * page_size) // 2  # Address is in 16-bit words
        addr_low = addr & 0xFF
        addr_high = (addr >> 8) & 0xFF
        
        # Load address
        if not send_cmd(ser, [STK_LOAD_ADDRESS, addr_low, addr_high, SYNC_SZ]):
            print(f"  ❌ Failed to load address for page {page}.")
            return False
            
        # Program page
        page_data = program_bytes[page*page_size : (page+1)*page_size]
        cmd = [STK_PROG_PAGE, (page_size >> 8) & 0xFF, page_size & 0xFF, 0x46] # 'F' for Flash
        ser.write(bytes(cmd) + page_data + bytes([SYNC_SZ]))
        res = ser.read(2)
        if len(res) != 2 or res[0] != STK_INSYNC or res[1] != STK_OK:
            print(f"  ❌ Failed to program page {page}.")
            return False
            
        # Progress indicator
        sys.stdout.write(f"\r    Progress: {int((page+1)/total_pages*100)}%")
        sys.stdout.flush()
        
    print("\n  ✅ Flashing complete.")
    send_cmd(ser, [STK_LEAVE_PROGMODE, SYNC_SZ])
    return True

def main():
    print("=" * 80)
    print("  TAP PURE PYTHON ARDUINO FLASHER")
    print("=" * 80)
    
    if len(sys.argv) < 3:
        print("  Usage: termux-usb -r <device> -e 'python src/flash_arduino.py <hex_file>'")
        return
        
    # Termux automatically appends the open USB file descriptor as the LAST argument.
    # So if we run: python src/flash_arduino.py assets/tap_qubit_driver.hex
    # argv[1] is the hex file, and argv[2] is the file descriptor.
    hex_file = sys.argv[1]
    fd = int(sys.argv[2])
    
    if not os.path.exists(hex_file):
        print(f"  ❌ Intel Hex file not found: {hex_file}")
        return
        
    program_bytes = load_hex(hex_file)
    print(f"  Loaded {len(program_bytes)} bytes of firmware.")
    
    try:
        # Open serial port using file descriptor passed by termux-usb
        ser = serial.Serial(port=None)
        ser.fd = fd
        ser.baudrate = 115200 # Standard Arduino Nano v3 bootloader speed
        ser.timeout = 1.0
        ser.open()
        
        # Reset Arduino using DTR/RTS lines
        print("  [RESET] Sending hardware reset...")
        ser.dtr = False
        ser.rts = False
        time.sleep(0.1)
        ser.dtr = True
        ser.rts = True
        time.sleep(0.4) # wait for bootloader to activate
        ser.reset_input_buffer()
        
        # Start flash sequence
        success = flash_device(ser, program_bytes)
        ser.close()
        
        if success:
            print("\n  🎯 Firmware updated successfully!")
            print("  You can now start the live monitor.")
    except Exception as e:
        print(f"\n  ❌ Serial flash error: {e}")

if __name__ == "__main__":
    main()
