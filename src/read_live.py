# -*- coding: utf-8 -*-
"""
read_live.py
=============
Reads raw serial data directly from standard input (fd 0) using unbuffered os.read
and writes it directly to the local log file.
"""

import os
import sys
import time

LOG_PATH = "/data/data/com.termux/files/home/TAP_model/assets/live_qubit_data.log"

def main():
    with open(LOG_PATH, "w", encoding="utf-8") as log_file:
        log_file.write("==================================================\n")
        log_file.write("  TAP LIVE UNBUFFERED LOG STREAM STARTED\n")
        log_file.write(f"  Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write("==================================================\n")
        log_file.flush()
        
        try:
            while True:
                # Read raw bytes directly from standard input (descriptor 0)
                chunk = os.read(0, 1024)
                if not chunk:
                    log_file.write("\n  [DISCONN] End of input stream.\n")
                    log_file.flush()
                    break
                # Decode and write immediately
                text = chunk.decode('utf-8', errors='ignore')
                log_file.write(text)
                log_file.flush()
                
        except KeyboardInterrupt:
            log_file.write("\n  [STOP] Live monitor halted.\n")
            log_file.flush()
        except Exception as e:
            log_file.write(f"\n  ❌ Read error: {e}\n")
            log_file.flush()

if __name__ == "__main__":
    main()
