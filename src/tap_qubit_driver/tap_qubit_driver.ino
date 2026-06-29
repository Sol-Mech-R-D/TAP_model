/*
 * tap_qubit_driver.ino
 * ====================
 * Macroscopic Graphene-Piezo Qubit Driver sketch with advanced diagnostic sweeps:
 *   - Mode 0: Continuous baseline monitoring (50-cycle excitation, raw min/max/amplitude).
 *   - Mode 1: T2 coherence decay sweep (varies delay, maps amplitude decay).
 *   - Mode 2: Dual-pulse phase interference sweep (varies phase delay, maps constructive/destructive interference).
 */

#include <Arduino.h>

const int TX_PIN = 9;   // Acoustic pulse transmitter (Pin 9)
const int RX_PIN = A0;  // Piezo feedback receiver (Analog 0)
const int SAMPLE_COUNT = 100;

void setup() {
  Serial.begin(115200);
  pinMode(TX_PIN, OUTPUT);
  pinMode(13, OUTPUT);
  Serial.println("==================================================");
  Serial.println("  TAP MACROSCOPIC QUBIT DRIVER & DIAGNOSTIC CORE  ");
  Serial.println("  Ready. Send '0' for Baseline, '1' for T2 Sweep, '2' for Phase Sweep.");
  Serial.println("==================================================");
}

// Helper to send a pulse train of N cycles at 4.5 kHz
void send_pulse_train(int cycles) {
  for (int i = 0; i < cycles; i++) {
    digitalWrite(TX_PIN, HIGH);
    delayMicroseconds(111);
    digitalWrite(TX_PIN, LOW);
    delayMicroseconds(111);
  }
}

// Helper to read the receiver amplitude
int read_amplitude() {
  int min_val = 1023;
  int max_val = 0;
  for (int i = 0; i < SAMPLE_COUNT; i++) {
    int val = analogRead(RX_PIN);
    if (val < min_val) min_val = val;
    if (val > max_val) max_val = val;
    delayMicroseconds(5);
  }
  return max_val - min_val;
}

// Run T2 Decay Sweep
void run_t2_sweep() {
  Serial.println("\n--- START T2 COHERENCE DECAY SWEEP ---");
  for (int delay_ms = 0; delay_ms <= 300; delay_ms += 10) {
    send_pulse_train(50);
    delay(delay_ms);
    int amp = read_amplitude();
    Serial.print("DecayDelay:");
    Serial.print(delay_ms);
    Serial.print("ms | Amplitude:");
    Serial.println(amp);
    delay(100); // cooldown between trials
  }
  Serial.println("--- END T2 COHERENCE DECAY SWEEP ---");
}

// Run Phase Interference Sweep
void run_phase_sweep() {
  Serial.println("\n--- START PHASE INTERFERENCE SWEEP ---");
  // 4.5 kHz period is ~222 microseconds
  for (int phase_us = 0; phase_us <= 222; phase_us += 11) {
    // Send first pulse train (25 cycles)
    send_pulse_train(25);
    // Phase delay
    delayMicroseconds(phase_us);
    // Send second pulse train (25 cycles)
    send_pulse_train(25);
    
    int amp = read_amplitude();
    Serial.print("PhaseDelay:");
    Serial.print(phase_us);
    Serial.print("us | Amplitude:");
    Serial.println(amp);
    delay(100); // cooldown
  }
  Serial.println("--- END PHASE INTERFERENCE SWEEP ---");
}

void loop() {
  // Check for incoming serial commands
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == '1') {
      run_t2_sweep();
    } else if (cmd == '2') {
      run_phase_sweep();
    } else if (cmd == '0') {
      Serial.println("\n--- SWITCHED TO CONTINUOUS BASELINE ---");
    }
  }

  // Continuous baseline mode (runs by default)
  send_pulse_train(50);
  
  // Read feedback wave response
  int min_val = 1023;
  int max_val = 0;
  for (int i = 0; i < SAMPLE_COUNT; i++) {
    int val = analogRead(RX_PIN);
    if (val < min_val) min_val = val;
    if (val > max_val) max_val = val;
    delayMicroseconds(5);
  }
  
  int amplitude = max_val - min_val;
  
  // Blink Pin 13 LED to show active coherence cycles
  digitalWrite(13, HIGH);
  delay(50);
  digitalWrite(13, LOW);
  
  // Print status to serial
  Serial.print("Qubit Amplitude: ");
  Serial.print(amplitude);
  Serial.print(" [Min: ");
  Serial.print(min_val);
  Serial.print(", Max: ");
  Serial.print(max_val);
  Serial.print("] | State: ");
  if (amplitude > 100) {
    Serial.println("|1> (Coherent State)");
  } else if (amplitude > 30) {
    Serial.println("(|0> + |1>)/sqrt(2) (Superposition)");
  } else {
    Serial.println("|0> (Decohered / Absorbed)");
  }
  
  delay(1000);
}
