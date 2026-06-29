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
  Serial.println("\n--- STARTING 10V DIFFERENTIAL FREQUENCY SWEEP ---");
  
  // Sweep frequency from 1 kHz to 10 kHz in 100 Hz steps
  for (int freq = 1000; freq <= 10000; freq += 100) {
    int half_period = 500000 / freq; // half-period in microseconds
    
    // Send 10V Differential excitation pulse train (50 cycles at target frequency)
    for (int i = 0; i < 50; i++) {
      digitalWrite(TX_PIN_POS, HIGH);
      digitalWrite(TX_PIN_NEG, LOW);
      delayMicroseconds(half_period);
      
      digitalWrite(TX_PIN_POS, LOW);
      digitalWrite(TX_PIN_NEG, HIGH);
      delayMicroseconds(half_period);
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
    
    // Print data point
    Serial.print("Freq:");
    Serial.print(freq);
    Serial.print("Hz | Amplitude:");
    Serial.print(amplitude);
    Serial.print(" [Min: ");
    Serial.print(min_val);
    Serial.print(", Max: ");
    Serial.print(max_val);
    Serial.println("]");
    
    // Brief cooldown delay between frequencies (keeps sweep speed audible)
    delay(50);
  }
  
  Serial.println("--- 10V DIFFERENTIAL FREQUENCY SWEEP COMPLETE ---");
  delay(10000); // 10-second wait before repeating
}
