#include <Arduino.h>

const int TX_PIN = 5;   // Acoustic pulse transmitter (Pin 5)
const int RX_PIN = A1;  // Piezo feedback receiver (Analog 1)
const int SAMPLE_COUNT = 100;

// Method 1: Golden Ratio Duty Cycle (38.2% HIGH, 61.8% LOW)
void send_pulse_golden(int cycles) {
  for (int i = 0; i < cycles; i++) {
    digitalWrite(TX_PIN, HIGH);
    delayMicroseconds(85);   // 38.2% of 222us
    digitalWrite(TX_PIN, LOW);
    delayMicroseconds(137);  // 61.8% of 222us
  }
}

// Method 2: 3:1 Cosmological Energy Partition (25% HIGH, 75% LOW)
void send_pulse_partition(int cycles) {
  for (int i = 0; i < cycles; i++) {
    digitalWrite(TX_PIN, HIGH);
    delayMicroseconds(55);   // 25% of 222us
    digitalWrite(TX_PIN, LOW);
    delayMicroseconds(167);  // 75% of 222us
  }
}

// Method 3: "Exhale" Cosmological Chirp (Geometric Pulse Expansion)
void send_pulse_chirp(int cycles) {
  float half_period = 111.0;
  for (int i = 0; i < cycles; i++) {
    // Pulse with expanding period
    digitalWrite(TX_PIN, HIGH);
    delayMicroseconds((int)(half_period * 0.764)); // 38.2% duty cycle of growing period
    digitalWrite(TX_PIN, LOW);
    delayMicroseconds((int)(half_period * 1.236)); // 61.8% duty cycle of growing period
    
    half_period *= 1.015; // Geometrically expand period by 1.5% each cycle
  }
}

// T2 Decay Sweep function
void run_t2_sweep(int method) {
  Serial.print("\n--- START T2 COHERENCE DECAY SWEEP (METHOD: ");
  Serial.print(method);
  Serial.println(") ---");
  
  for (int delay_ms = 0; delay_ms <= 300; delay_ms += 10) {
    // Trigger excitation based on method
    if (method == 1) {
      send_pulse_golden(50);
    } else if (method == 2) {
      send_pulse_partition(50);
    } else if (method == 3) {
      send_pulse_chirp(50);
    }
    
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
  Serial.print("--- END T2 COHERENCE DECAY SWEEP (METHOD: ");
  Serial.print(method);
  Serial.println(") ---");
}

void setup() {
  Serial.begin(115200);
  pinMode(TX_PIN, OUTPUT);
  pinMode(13, OUTPUT);
  digitalWrite(TX_PIN, LOW);
  
  Serial.println("==================================================");
  Serial.println("  TAP THREE-METHOD ASYMMETRIC CORE (D5 -> A1)      ");
  Serial.println("  Commands: '1' -> Golden Ratio, '2' -> 3:1 Energy, '3' -> Exhale Chirp");
  Serial.println("==================================================");
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == '1') {
      run_t2_sweep(1);
    } else if (cmd == '2') {
      run_t2_sweep(2);
    } else if (cmd == '3') {
      run_t2_sweep(3);
    }
  }
  
  // Remain silent by default
  digitalWrite(TX_PIN, LOW);
}
