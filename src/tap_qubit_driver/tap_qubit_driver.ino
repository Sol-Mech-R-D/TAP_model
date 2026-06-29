#include <Arduino.h>

const int TX_PIN = 5;
const int SAMPLE_COUNT = 100;

void send_pulse_partition(int cycles) {
  for (int i = 0; i < cycles; i++) {
    digitalWrite(TX_PIN, HIGH);
    delayMicroseconds(55);   // 25% of 222us
    digitalWrite(TX_PIN, LOW);
    delayMicroseconds(167);  // 75% of 222us
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(TX_PIN, OUTPUT);
  digitalWrite(TX_PIN, LOW);
  
  // Enable internal pull-ups on all digital-capable analog pins
  pinMode(A0, INPUT_PULLUP);
  pinMode(A1, INPUT_PULLUP);
  pinMode(A2, INPUT_PULLUP);
  pinMode(A3, INPUT_PULLUP);
  pinMode(A4, INPUT_PULLUP);
  pinMode(A5, INPUT_PULLUP);
}

void loop() {
  Serial.println("\n--- ANALOG PIN ACOUSTIC SCAN ---");
  
  int pins[] = {A0, A1, A2, A3, A4, A5, A6, A7};
  
  for (int p = 0; p < 8; p++) {
    int rx_pin = pins[p];
    
    // Send 3:1 partition excitation pulse train on Pin 5
    send_pulse_partition(50);
    digitalWrite(TX_PIN, LOW);
    
    // Immediate read of this specific pin
    int min_val = 1023;
    int max_val = 0;
    for (int i = 0; i < SAMPLE_COUNT; i++) {
      int val = analogRead(rx_pin);
      if (val < min_val) min_val = val;
      if (val > max_val) max_val = val;
      delayMicroseconds(5);
    }
    int amplitude = max_val - min_val;
    
    Serial.print("Pin A");
    Serial.print(p);
    Serial.print(" | Amp: ");
    Serial.print(amplitude);
    Serial.print(" [Min: ");
    Serial.print(min_val);
    Serial.print(", Max: ");
    Serial.print(max_val);
    Serial.println("]");
    
    delay(100); // cooldown between pin scans
  }
  
  delay(3000); // repeat scan every 3 seconds
}
