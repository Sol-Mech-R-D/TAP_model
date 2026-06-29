#include <Arduino.h>

const int TX_PIN_POS = 9;  // Acoustic pulse transmitter positive (Pin 9)
const int TX_PIN_NEG = 8;  // Acoustic pulse transmitter negative (Pin 8)
const int RX_PIN = A0;      // Piezo feedback receiver (Analog 0)
const int SAMPLE_COUNT = 100;

void setup() {
  Serial.begin(115200);
  pinMode(TX_PIN_POS, OUTPUT);
  pinMode(TX_PIN_NEG, OUTPUT);
  pinMode(13, OUTPUT);
  
  // Set initial states to LOW
  digitalWrite(TX_PIN_POS, LOW);
  digitalWrite(TX_PIN_NEG, LOW);
}

void loop() {
  // Differential 10V Peak-to-Peak 4.5 kHz pulse train (50 cycles)
  for (int i = 0; i < 50; i++) {
    digitalWrite(TX_PIN_POS, HIGH);
    digitalWrite(TX_PIN_NEG, LOW);
    delayMicroseconds(111);
    
    digitalWrite(TX_PIN_POS, LOW);
    digitalWrite(TX_PIN_NEG, HIGH);
    delayMicroseconds(111);
  }
  
  // Return pins to LOW to discharge the piezo
  digitalWrite(TX_PIN_POS, LOW);
  digitalWrite(TX_PIN_NEG, LOW);
  
  // Immediate inline read
  int min_val = 1023;
  int max_val = 0;
  for (int i = 0; i < SAMPLE_COUNT; i++) {
    int val = analogRead(RX_PIN);
    if (val < min_val) min_val = val;
    if (val > max_val) max_val = val;
    delayMicroseconds(5);
  }
  
  int amplitude = max_val - min_val;
  
  // Blink Pin 13 LED
  digitalWrite(13, HIGH);
  delay(50);
  digitalWrite(13, LOW);
  
  // Print status
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
