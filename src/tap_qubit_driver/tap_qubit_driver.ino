#include <Arduino.h>

const int TX_PIN = 5;   // Acoustic pulse transmitter (Pin 5)

void setup() {
  pinMode(TX_PIN, OUTPUT);
  digitalWrite(TX_PIN, LOW);
}

void loop() {
  // Continuous 4.5 kHz square wave (50% duty cycle) for multimeter measurement
  digitalWrite(TX_PIN, HIGH);
  delayMicroseconds(111);
  digitalWrite(TX_PIN, LOW);
  delayMicroseconds(111);
}
