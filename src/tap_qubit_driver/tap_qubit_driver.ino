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
}

void loop() {
  Serial.println("\n--- STARTING T2 COHERENCE DECAY SWEEP ---");
  
  for (int delay_ms = 0; delay_ms <= 300; delay_ms += 10) {
    // 10V Differential excitation pulse train (50 cycles)
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
    
    // Coherence decay delay
    delay(delay_ms);
    
    // Read remaining wave amplitude
    int min_val = 1023;
    int max_val = 0;
    for (int i = 0; i < SAMPLE_COUNT; i++) {
      int val = analogRead(RX_PIN);
      if (val < min_val) min_val = val;
      if (val > max_val) max_val = val;
      delayMicroseconds(5);
    }
    
    int amplitude = max_val - min_val;
    
    // Print data point
    Serial.print("DecayDelay:");
    Serial.print(delay_ms);
    Serial.print("ms | Amplitude:");
    Serial.print(amplitude);
    Serial.print(" [Min: ");
    Serial.print(min_val);
    Serial.print(", Max: ");
    Serial.print(max_val);
    Serial.println("]");
    
    // Cooldown delay between trials
    delay(200);
  }
  
  Serial.println("--- T2 COHERENCE DECAY SWEEP COMPLETE ---");
  delay(5000); // 5-second wait before starting the next sweep
}
