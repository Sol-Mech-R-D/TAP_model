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
  
  digitalWrite(TX_PIN_POS, LOW);
  digitalWrite(TX_PIN_NEG, LOW);
  
  Serial.println("==================================================");
  Serial.println("  TAP 10V DIFFERENTIAL 5-SECOND LOUD TEST TONE    ");
  Serial.println("==================================================");
  
  // Blink LED to warn of start
  for(int i=0; i<3; i++) {
    digitalWrite(13, HIGH); delay(100);
    digitalWrite(13, LOW); delay(100);
  }
  
  Serial.println("📡 STARTING 5-SECOND TONE BURST (4.5 kHz, 10V)...");
  
  // 150 trials of 100 cycles each ≈ 5.0 seconds of continuous tone
  for (int trial = 0; trial < 150; trial++) {
    // Pulse 100 cycles at 4.5 kHz
    for (int i = 0; i < 100; i++) {
      digitalWrite(TX_PIN_POS, HIGH);
      digitalWrite(TX_PIN_NEG, LOW);
      delayMicroseconds(111);
      
      digitalWrite(TX_PIN_POS, LOW);
      digitalWrite(TX_PIN_NEG, HIGH);
      delayMicroseconds(111);
    }
    
    // Immediate read of the active wave response
    int min_val = 1023;
    int max_val = 0;
    for (int i = 0; i < SAMPLE_COUNT; i++) {
      int val = analogRead(RX_PIN);
      if (val < min_val) min_val = val;
      if (val > max_val) max_val = val;
      delayMicroseconds(5);
    }
    int amplitude = max_val - min_val;
    
    // Print live feedback during the tone
    Serial.print("Live Tone | Amplitude: ");
    Serial.print(amplitude);
    Serial.print(" [Min: ");
    Serial.print(min_val);
    Serial.print(", Max: ");
    Serial.print(max_val);
    Serial.println("]");
  }
  
  // Turn off transmitter pins (silence)
  digitalWrite(TX_PIN_POS, LOW);
  digitalWrite(TX_PIN_NEG, LOW);
  
  Serial.println("🔇 TONE BURST FINISHED. SILENT.");
}

void loop() {
  // Do nothing in the loop so it only runs once per reset
}
