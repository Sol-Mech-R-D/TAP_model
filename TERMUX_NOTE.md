# Note for the Termux Agent

## ⚡ Firmware & Tooling Updates (June 28, 2026)

We have successfully compiled, flashed, and verified the updated Arduino qubit driver on the host side, and resolved the configuration parameters for the live-stream tools.

### 1. Arduino Sketch Flashed
* **File:** [src/tap_qubit_driver/tap_qubit_driver.ino](file:///C:/TAP_model/src/tap_qubit_driver/tap_qubit_driver.ino)
* **Status:** Compiled and uploaded to the connected Arduino Nano via COM3.
* **Baud Rate:** Application runs at **`115200`** baud.
* **Changes in Firmware:**
  * Cleaned out the unused Fibonacci frequency square wave generators on Pins 3, 5, and 6.
  * Added Pin 13 LED blink sequence to show active sampling loops.
  * Reduced `SAMPLE_COUNT` to `100` for faster feedback loops.
  * Mapped state vector responses to updated coherence thresholds:
    * `amplitude > 800`: Coherent State `|1>`
    * `amplitude > 150`: Superposition `(|0> + |1>)/sqrt(2)`
    * Otherwise: Decohered / Absorbed `|0>`

### 2. Precompiled Hex Updated
* **File:** [assets/tap_qubit_driver.hex](file:///C:/TAP_model/assets/tap_qubit_driver.hex)
* **Status:** Overwritten and updated with the newly compiled hex file. You can now use `src/flash_arduino.py` to directly program target devices over Termux USB.

### 3. USB Bulk Reader Fixed
* **File:** [src/usb_direct_read.py](file:///C:/TAP_model/src/usb_direct_read.py)
* **Status:** Corrected the CH340 initialization baud rate from `57600` to **`115200`** to match the Arduino sketch application speed.
* **Live Monitor Run Command:**
  ```bash
  termux-usb -r -e 'python src/usb_direct_read.py' <device>
  ```
  This will record raw live stream data into `assets/live_qubit_data.log` at the correct speed without byte corruption.
