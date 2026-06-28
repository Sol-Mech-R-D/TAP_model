# -*- coding: utf-8 -*-
"""
read_qubit.py
==============
Reads raw serial data from the USB file descriptor passed by termux-usb.
Parses the live qubit amplitude and prints the output.
"""

import sys
import os
import serial

def main():
    print("=" * 80)
    print("  TAP LIVE QUBIT MONITOR")
    print("=" * 80)
    
    # Termux passes the file descriptor as an integer in sys.argv
    # or we can read it directly from standard input.
    # Typically: termux-usb passes the FD to stdin or argv.
    # Let's check sys.argv
    if len(sys.argv) < 2:
        print("  ❌ No USB File Descriptor provided by Termux.")
        print("  Usage: termux-usb -r <device> -e 'python src/read_qubit.py'")
        return
        
    try:
        fd = int(sys.argv[1])
        print(f"  [CONN] Connected to USB File Descriptor: {fd}")
        
        # Open serial port using the file descriptor
        ser = serial.Serial()
        ser.port = f"socket://{fd}" # pyserial can bind to fd or socket url
        # Or open fd directly:
        ser = serial.Serial(port=None)
        ser.fd = fd
        ser.baudrate = 115200
        ser.open()
        
        print("  [LIVE] Streaming qubit coherence metrics...")
        print("  Press Ctrl+C to stop.\n")
        
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"  📡 {line}")
    except KeyboardInterrupt:
        print("\n  [STOP] Live monitor halted.")
    except Exception as e:
        print(f"  ❌ Error reading serial port: {e}")
        print("  Note: If pySerial fd binding fails, you can read from stdout using termux-usb directly.")

if __name__ == "__main__":
    main()
