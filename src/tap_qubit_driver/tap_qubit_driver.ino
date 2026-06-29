#include <Arduino.h>

const int TX_PIN_POS = 9;  // Acoustic pulse transmitter positive (Pin 9)
const int TX_PIN_NEG = 8;  // Acoustic pulse transmitter negative (Pin 8)
const int RX_PIN = A0;      // Piezo feedback receiver (Analog 0)
const int SAMPLE_COUNT = 100;

void play_note(int freq, int duration_ms) {
  int half_period = 500000 / freq; // half-period in microseconds
  long cycles = (long)freq * duration_ms / 1000;
  
  for (long i = 0; i < cycles; i++) {
    digitalWrite(TX_PIN_POS, HIGH);
    digitalWrite(TX_PIN_NEG, LOW);
    delayMicroseconds(half_period);
    
    digitalWrite(TX_PIN_POS, LOW);
    digitalWrite(TX_PIN_NEG, HIGH);
    delayMicroseconds(half_period);
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(TX_PIN_POS, OUTPUT);
  pinMode(TX_PIN_NEG, OUTPUT);
  pinMode(13, OUTPUT);
  
  digitalWrite(TX_PIN_POS, LOW);
  digitalWrite(TX_PIN_NEG, LOW);
  
  Serial.println("==================================================");
  Serial.println("  TAP 10V DIFFERENTIAL JINGLE TEST BURST           ");
  Serial.println("==================================================");
  
  // Blink LED warning
  for(int i=0; i<3; i++) {
    digitalWrite(13, HIGH); delay(100);
    digitalWrite(13, LOW); delay(100);
  }
  
  Serial.println("📡 PLAYING JINGLE (DO DO DOO)...");
  
  // Note 1 ("do"): 2000 Hz (500 ms)
  play_note(2000, 500);
  delay(100);
  
  // Note 2 ("do"): 3000 Hz (500 ms)
  play_note(3000, 500);
  delay(100);
  
  // Note 3 ("doo"): 4000 Hz (1000 ms)
  play_note(4000, 1000);
  
  // Silence pins
  digitalWrite(TX_PIN_POS, LOW);
  digitalWrite(TX_PIN_NEG, LOW);
  
  Serial.println("🔇 JINGLE FINISHED. SILENT.");
}

void loop() {
  // Do nothing
}
