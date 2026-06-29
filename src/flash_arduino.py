# -*- coding: utf-8 -*-
"""
flash_arduino.py
================
Pure Python STK500v1 bootloader client to flash Arduino Nano (Atmega328p)
directly from Termux over USB-C serial.
Uses raw OS file descriptors and termios for zero-dependency flashing.
"""

import sys
import os
import time
import termios
import select

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

class RawSerialFD:
    def __init__(self, fd, baud=115200):
        self.fd = fd
        self.set_baud(baud)
        
    def set_baud(self, baud):
        attrs = termios.tcgetattr(self.fd)
        baud_const = termios.B115200 if baud == 115200 else termios.B57600
        attrs[4] = baud_const # ospeed
        attrs[5] = baud_const # ispeed
        
        # Raw mode settings
        attrs[0] &= ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK | termios.ISTRIP | termios.INLCR | termios.IGNCR | termios.ICRNL | termios.IXON)
        attrs[1] &= ~termios.OPOST
        attrs[2] &= ~(termios.CSIZE | termios.PARENB)
        attrs[2] |= termios.CS8
        attrs[3] &= ~(termios.ECHO | termios.ECHONL | termios.ICANON | termios.ISIG | termios.IEXTEN)
        
        # Block until at least 1 char is available, no timeout
        attrs[6][termios.VMIN] = 0
        attrs[6][termios.VTIME] = 10 # 1.0 second timeout
        
        termios.tcsetattr(self.fd, termios.TCSANOW, attrs)

    def write(self, data):
        os.write(self.fd, data)

    def read(self, size):
        # Read up to size bytes with a timeout
        buffer = bytearray()
        start = time.time()
        while len(buffer) < size:
            # Check for data available using select
            r, _, _ = select.select([self.fd], [], [], 1.0)
            if r:
                chunk = os.read(self.fd, size - len(buffer))
                if not chunk:
                    break
                buffer.extend(chunk)
            if time.time() - start > 2.0: # 2s max read timeout
                break
        return bytes(buffer)

    def flush_input(self):
        # Read and discard all available bytes in the buffer without blocking
        while True:
            r, _, _ = select.select([self.fd], [], [], 0.0)
            if r:
                try:
                    os.read(self.fd, 1024)
                except Exception:
                    break
            else:
                break

    def setDTR(self, val):
        # DTR/RTS control using ioctl on Android is sometimes restricted,
        # but we can try using standard TIOCMGET/TIOCMSET
        import fcntl
        import struct
        TIOCMGET = 0x5415
        TIOCMSET = 0x5418
        TIOCM_DTR = 0x002
        TIOCM_RTS = 0x004
        try:
            mget = struct.unpack('I', fcntl.ioctl(self.fd, TIOCMGET, struct.pack('I', 0)))[0]
            if val:
                mget |= (TIOCM_DTR | TIOCM_RTS)
            else:
                mget &= ~(TIOCM_DTR | TIOCM_RTS)
            fcntl.ioctl(self.fd, TIOCMSET, struct.pack('I', mget))
        except Exception:
            # Ignore if ioctl is not supported on this descriptor type
            pass

def parse_hex_line(line):
    if not line.startswith(':'):
        return None
    byte_count = int(line[1:3], 16)
    address = int(line[3:7], 16)
    record_type = int(line[7:9], 16)
    data = bytes.fromhex(line[9:9+byte_count*2])
    return record_type, address, data

def load_hex(hex_path):
    flash = bytearray(32256)
    max_addr = 0
    with open(hex_path, 'r') as f:
        for line in f:
            parsed = parse_hex_line(line.strip())
            if not parsed:
                continue
            record_type, address, data = parsed
            if record_type == 0:
                flash[address:address+len(data)] = data
                if address + len(data) > max_addr:
                    max_addr = address + len(data)
            elif record_type == 1:
                break
    pages = (max_addr + 127) // 128
    return bytes(flash[:pages*128])

def send_cmd(ser, cmd):
    # Flush input buffer before sending command
    ser.flush_input()
    ser.write(bytes(cmd))
    
    # Read byte by byte looking for STK_INSYNC and STK_OK
    start = time.time()
    while time.time() - start < 1.0:
        b = ser.read(1)
        if b == bytes([STK_INSYNC]):
            b2 = ser.read(1)
            if b2 == bytes([STK_OK]):
                return True
    return False

def flash_device(ser, program_bytes):
    print("  [CONN] Sending sync packages...")
    for _ in range(15):
        # Flush serial input buffer
        ser.flush_input()
        ser.write(bytes([STK_GET_SYNC, SYNC_SZ]))
        
        # Read byte by byte looking for STK_INSYNC and STK_OK
        insync_found = False
        start = time.time()
        while time.time() - start < 0.2:
            b = ser.read(1)
            if b == bytes([STK_INSYNC]):
                b2 = ser.read(1)
                if b2 == bytes([STK_OK]):
                    insync_found = True
                    break
        if insync_found:
            break
        time.sleep(0.05)
    else:
        print("  ❌ Failed to sync with Arduino. Try pressing the Reset button.")
        return False
        
    print("  ✅ Synchronized successfully.")
    
    send_cmd(ser, [STK_ENTER_PROGMODE, SYNC_SZ])
    
    page_size = 128
    total_pages = len(program_bytes) // page_size
    print(f"  [FLASH] Programming {len(program_bytes)} bytes ({total_pages} pages)...")
    
    for page in range(total_pages):
        addr = (page * page_size) // 2
        addr_low = addr & 0xFF
        addr_high = (addr >> 8) & 0xFF
        
        if not send_cmd(ser, [STK_LOAD_ADDRESS, addr_low, addr_high, SYNC_SZ]):
            print(f"  ❌ Failed to load address for page {page}.")
            return False
            
        page_data = program_bytes[page*page_size : (page+1)*page_size]
        cmd = [STK_PROG_PAGE, (page_size >> 8) & 0xFF, page_size & 0xFF, 0x46]
        ser.write(bytes(cmd) + page_data + bytes([SYNC_SZ]))
        res = ser.read(2)
        if len(res) != 2 or res[0] != STK_INSYNC or res[1] != STK_OK:
            print(f"  ❌ Failed to program page {page}.")
            return False
            
        sys.stdout.write(f"\r    Progress: {int((page+1)/total_pages*100)}%")
        sys.stdout.flush()
        
    print("\n  ✅ Flashing complete.")
    send_cmd(ser, [STK_LEAVE_PROGMODE, SYNC_SZ])
    return True

def main():
    print("=" * 80)
    print("  TAP PURE PYTHON ARDUINO FLASHER")
    print("=" * 80)
    
    if len(sys.argv) < 2:
        print("  Usage: python src/flash_arduino.py <hex_file> [fd]")
        return
        
    hex_file = sys.argv[1]
    fd = int(sys.argv[2]) if len(sys.argv) >= 3 else 0
    
    if not os.path.exists(hex_file):
        print(f"  ❌ Intel Hex file not found: {hex_file}")
        return
        
    program_bytes = load_hex(hex_file)
    print(f"  Loaded {len(program_bytes)} bytes of firmware.")
    
    for baud in [115200, 57600]:
        print(f"  [TRY] Attempting flashing at {baud} baud...")
        try:
            # Wrap fd in raw serial class
            ser = RawSerialFD(fd, baud)
            
            # Reset Arduino
            print("    [RESET] Sending hardware reset...")
            ser.setDTR(False)
            time.sleep(0.1)
            ser.setDTR(True)
            time.sleep(0.4) # wait for bootloader
            
            # Start flash sequence
            success = flash_device(ser, program_bytes)
            
            if success:
                print(f"\n  🎯 Firmware updated successfully at {baud} baud!")
                print("  You can now start the live monitor.")
                with open("/data/data/com.termux/files/home/TAP_model/assets/flash_success.tmp", "w") as sf:
                    sf.write("OK")
                return
        except Exception as e:
            print(f"    ⚠️ Flash at {baud} baud failed: {e}")
            
    print("\n  ❌ Failed to flash firmware at all supported baud rates.")

if __name__ == "__main__":
    main()
