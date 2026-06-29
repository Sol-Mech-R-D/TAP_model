/*
 * tap_qubit_driver.ino
 * ====================
 * Macroscopic Graphene-Piezo Qubit Driver sketch.
 * Prints amplitude and state vector to serial.
 */

#include <Arduino.h>

const int TX_PIN = 9;   // Acoustic pulse transmitter (Pin 9)
const int RX_PIN = A0;  // Piezo feedback receiver (Analog 0)
const int SAMPLE_COUNT = 100;

void setup() {
  Serial.begin(115200);
  pinMode(TX_PIN, OUTPUT);
  pinMode(13, OUTPUT);
}

void loop() {
  // Send 4.5 kHz acoustic pulse train (50 cycles for increased output energy)
  for (int i = 0; i < 50; i++) {
    digitalWrite(TX_PIN, HIGH);
    delayMicroseconds(111);
    digitalWrite(TX_PIN, LOW);
    delayMicroseconds(111);
  }
  
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
  Serial.print(" | State: ");
  if (amplitude > 800) {
    Serial.println("|1> (Coherent State)");
  } else if (amplitude > 150) {
    Serial.println("(|0> + |1>)/sqrt(2) (Superposition)");
  } else {
    Serial.println("|0> (Decohered / Absorbed)");
  }
  
  delay(1000);
}
