#include <Arduino.h>

const int TX_PIN = 5;   // Acoustic pulse transmitter (Pin 5)
const int RX_PIN = A1;  // Piezo feedback receiver (Analog 1)
const int SAMPLE_COUNT = 100;

// Helper to send a pulse train of N cycles at 4.5 kHz
void send_pulse_train(int cycles) {
  for (int i = 0; i < cycles; i++) {
    digitalWrite(TX_PIN, HIGH);
    delayMicroseconds(111);
    digitalWrite(TX_PIN, LOW);
    delayMicroseconds(111);
  }
}

// Run T2 Decay Sweep
void run_t2_sweep() {
  Serial.println("\n--- START T2 COHERENCE DECAY SWEEP ---");
  for (int delay_ms = 0; delay_ms <= 300; delay_ms += 10) {
    send_pulse_train(50);
    delay(delay_ms);
    
    int min_val = 1023;
    int max_val = 0;
    for (int i = 0; i < SAMPLE_COUNT; i++) {
      int val = analogRead(RX_PIN);
      if (val < min_val) min_val = val;
      if (val > max_val) max_val = val;
      delayMicroseconds(5);
    }
    int amp = max_val - min_val;
    
    Serial.print("DecayDelay:");
    Serial.print(delay_ms);
    Serial.print("ms | Amplitude:");
    Serial.print(amp);
    Serial.print(" [Min: ");
    Serial.print(min_val);
    Serial.print(", Max: ");
    Serial.print(max_val);
    Serial.println("]");
    
    delay(200); // cooldown between trials
  }
  Serial.println("--- END T2 COHERENCE DECAY SWEEP ---");
}

// Run Phase Interference Sweep
void run_phase_sweep() {
  Serial.println("\n--- START PHASE INTERFERENCE SWEEP ---");
  for (int phase_us = 0; phase_us <= 222; phase_us += 11) {
    // Send first pulse train (25 cycles)
    for (int i = 0; i < 25; i++) {
      digitalWrite(TX_PIN, HIGH);
      delayMicroseconds(111);
      digitalWrite(TX_PIN, LOW);
      delayMicroseconds(111);
    }
    // Phase delay
    delayMicroseconds(phase_us);
    // Send second pulse train (25 cycles)
    for (int i = 0; i < 25; i++) {
      digitalWrite(TX_PIN, HIGH);
      delayMicroseconds(111);
      digitalWrite(TX_PIN, LOW);
      delayMicroseconds(111);
    }
    
    int min_val = 1023;
    int max_val = 0;
    for (int i = 0; i < SAMPLE_COUNT; i++) {
      int val = analogRead(RX_PIN);
      if (val < min_val) min_val = val;
      if (val > max_val) max_val = val;
      delayMicroseconds(5);
    }
    int amp = max_val - min_val;
    
    Serial.print("PhaseDelay:");
    Serial.print(phase_us);
    Serial.print("us | Amplitude:");
    Serial.print(amp);
    Serial.print(" [Min: ");
    Serial.print(min_val);
    Serial.print(", Max: ");
    Serial.print(max_val);
    Serial.println("]");
    
    delay(200); // cooldown
  }
  Serial.println("--- END PHASE INTERFERENCE SWEEP ---");
}

void setup() {
  Serial.begin(115200);
  pinMode(TX_PIN, OUTPUT);
  pinMode(13, OUTPUT);
  digitalWrite(TX_PIN, LOW);
  
  Serial.println("==================================================");
  Serial.println("  TAP COHERENCE CORE (D5 -> A1) - SILENT BASELINE ");
  Serial.println("  Ready. Send '1' for T2 Sweep, '2' for Phase Sweep.");
  Serial.println("==================================================");
}

void loop() {
  // Check for incoming serial commands
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == '1') {
      run_t2_sweep();
    } else if (cmd == '2') {
      run_phase_sweep();
    }
  }

  // Pin is kept LOW/silent when not executing sweeps
  digitalWrite(TX_PIN, LOW);
}
