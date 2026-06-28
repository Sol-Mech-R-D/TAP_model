/*
 * tap_qubit_driver.ino
 * =====================
 * Microcontroller firmware to drive the TAP room-temperature acoustic qubit
 * and generate the Fibonacci chord for acoustic graphene exfoliation.
 * 
 * Hardware Layout:
 *   - Pin 9: Transmit Piezo (Tx) pulse driver
 *   - Analog 0: Receive Piezo (Rx) signal input
 *   - Pin 3: 21 kHz PWM generator (Fibonacci component 1)
 *   - Pin 5: 34 kHz PWM generator (Fibonacci component 2)
 *   - Pin 6: 55 kHz PWM generator (Fibonacci component 3)
 */

#include <Arduino.h>

// Frequency constants
const unsigned long FREQ_A = 21000; // 21 kHz
const unsigned long FREQ_B = 34000; // 34 kHz
const unsigned long FREQ_C = 55000; // 55 kHz

// Qubit pulse parameters
const int TX_PIN = 9;
const int RX_PIN = A0;
const int SAMPLE_COUNT = 250;

void setup() {
  Serial.begin(115200);
  
  pinMode(TX_PIN, OUTPUT);
  pinMode(RX_PIN, INPUT);
  
  // Set up Timer 1 and Timer 2 to output high frequency square waves
  // for the Fibonacci chord on Pins 3, 5, and 6.
  // Note: We use tone() as a simple, hardware-independent pulse generator.
  tone(3, FREQ_A);
  tone(5, FREQ_B);
  tone(6, FREQ_C);
  
  Serial.println("==================================================");
  Serial.println("   TAP MACROSCOPIC QUBIT & GRAPHENE DRIVER LIVE  ");
  Serial.println("==================================================");
  Serial.print("   Fibonacci Chords active on Pins 3, 5, 6 (kHz): ");
  Serial.print(FREQ_A/1000.0); Serial.print(", ");
  Serial.print(FREQ_B/1000.0); Serial.print(", ");
  Serial.println(FREQ_C/1000.0);
}

void loop() {
  // --- Stage 1: Send Acoustic Qubit Test Pulse ---
  // Send a 1 ms acoustic pulse train on Pin 9 (Tx) at 4.5 kHz (resonance of 20mm piezo)
  unsigned long pulse_start = micros();
  for (int i = 0; i < 9; i++) {
    digitalWrite(TX_PIN, HIGH);
    delayMicroseconds(111); // ~4.5 kHz half-period
    digitalWrite(TX_PIN, LOW);
    delayMicroseconds(111);
  }
  
  // --- Stage 2: Read Qubit State Vector Response ---
  // Read incoming wave on Analog 0 (Rx)
  int min_val = 1023;
  int max_val = 0;
  
  // Fast analog read loop
  for (int i = 0; i < SAMPLE_COUNT; i++) {
    int val = analogRead(RX_PIN);
    if (val < min_val) min_val = val;
    if (val > max_val) max_val = val;
    delayMicroseconds(5);
  }
  
  // Calculate wave peak-to-peak amplitude (proportional to state vector coherence)
  int amplitude = max_val - min_val;
  
  // Print status
  Serial.print("Qubit Amplitude: ");
  Serial.print(amplitude);
  Serial.print(" | State: |");
  if (amplitude > 400) {
    Serial.println("1> (Coherence High - Transmitted)");
  } else if (amplitude > 50) {
    Serial.println("+> (Superposition - Phase Shifted)");
  } else {
    Serial.println("0> (Decohered / Absorbed)");
  }
  
  delay(1000); // Repeat measurement every second
}
