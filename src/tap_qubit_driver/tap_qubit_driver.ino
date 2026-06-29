#include <Arduino.h>

const int TX_PIN = 5;   // Acoustic pulse transmitter (Pin 5)
const int RX_PIN = A1;  // Piezo feedback receiver (Analog 1)
const int SAMPLE_COUNT = 100;

bool continuous_print = false;

// Method 1: Golden Ratio Duty Cycle (38.2% / 61.8% active phase) - 5V Single-Ended
void send_pulse_golden(int cycles) {
  for (int i = 0; i < cycles; i++) {
    digitalWrite(TX_PIN, HIGH);
    delayMicroseconds(85);   // 38.2% of 222us
    digitalWrite(TX_PIN, LOW);
    delayMicroseconds(137);  // 61.8% of 222us
  }
}

// Method 2: 3:1 Cosmological Energy Partition (25% / 75% active phase) - 5V Single-Ended
void send_pulse_partition(int cycles) {
  for (int i = 0; i < cycles; i++) {
    digitalWrite(TX_PIN, HIGH);
    delayMicroseconds(55);   // 25% of 222us
    digitalWrite(TX_PIN, LOW);
    delayMicroseconds(167);  // 75% of 222us
  }
}

// Method 3: \"Exhale\" Cosmological Chirp (Geometric Pulse Expansion) - 5V Single-Ended
void send_pulse_chirp(int cycles) {
  float half_period = 111.0;
  for (int i = 0; i < cycles; i++) {
    digitalWrite(TX_PIN, HIGH);
    delayMicroseconds((int)(half_period * 0.764)); 
    digitalWrite(TX_PIN, LOW);
    delayMicroseconds((int)(half_period * 1.236)); 
    half_period *= 1.015; 
  }
}

// Method 4: Fused TAP Excitation (Chirp + Golden Ratio Energy Partition) - 5V Single-Ended
void send_pulse_fused(int cycles) {
  float period = 222.0;
  for (int i = 0; i < cycles; i++) {
    int t_high = (int)(period * 0.236);
    int t_low = (int)(period * 0.764);
    
    digitalWrite(TX_PIN, HIGH);
    delayMicroseconds(t_high);
    digitalWrite(TX_PIN, LOW);
    delayMicroseconds(t_low);
    
    period *= 1.015;
  }
}

// T2 Decay Sweep function
void run_t2_sweep(int method) {
  Serial.print("\n--- START T2 COHERENCE DECAY SWEEP (METHOD: ");
  Serial.print(method);
  Serial.println(") ---");
  
  for (int delay_ms = 0; delay_ms <= 300; delay_ms += 10) {
    if (method == 1) {
      send_pulse_golden(50);
    } else if (method == 2) {
      send_pulse_partition(50);
    } else if (method == 3) {
      send_pulse_chirp(50);
    } else if (method == 4) {
      send_pulse_fused(50);
    }
    
    digitalWrite(TX_PIN, LOW);
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
  
  // Enable internal pull-up on RX_PIN to stop floating hum!
  pinMode(RX_PIN, INPUT_PULLUP);
  
  digitalWrite(TX_PIN, LOW);
  
  Serial.println("==================================================");
  Serial.println("  TAP UNIFIED CORE (D5 -> A1) - INTERNAL PULL-UP   ");
  Serial.println("  Ready. Commands: '1'->Golden, '2'->3:1, '3'->Chirp, '4'->Fused, '0'->Toggle Monitor");
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
    } else if (cmd == '4') {
      run_t2_sweep(4);
    } else if (cmd == '0') {
      continuous_print = !continuous_print;
      if (continuous_print) {
        Serial.println("\n📡 SILENT REAL-TIME MONITOR ACTIVE");
      } else {
        Serial.println("\n🔇 SILENT REAL-TIME MONITOR DEACTIVATED");
      }
    }
  }
  
  if (continuous_print) {
    int min_val = 1023;
    int max_val = 0;
    for (int i = 0; i < SAMPLE_COUNT; i++) {
      int val = analogRead(RX_PIN);
      if (val < min_val) min_val = val;
      if (val > max_val) max_val = val;
      delayMicroseconds(5);
    }
    int amplitude = max_val - min_val;
    Serial.print("Rx Monitor | Amplitude: ");
    Serial.print(amplitude);
    Serial.print(" [Min: ");
    Serial.print(min_val);
    Serial.print(", Max: ");
    Serial.print(max_val);
    Serial.println("]");
    delay(200); 
  } else {
    digitalWrite(TX_PIN, LOW);
  }
}
