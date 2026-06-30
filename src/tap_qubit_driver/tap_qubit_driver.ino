#include <Arduino.h>

const int TX1_PIN = 3;  // Primary transmitter (Node A)
const int TX2_PIN = 5;  // Floquet pump / Secondary transmitter (Node B)
const int RX_PIN = A1;  // Tetrahedral feedback receiver (Node C)
const int SAMPLE_COUNT = 100;

bool continuous_print = false;

// Method 2: Send pulse train using 3:1 partition (25% active duty cycle)
void send_pulse_partition(int pin, int cycles) {
  for (int i = 0; i < cycles; i++) {
    digitalWrite(pin, HIGH);
    delayMicroseconds(55);   // 25% of 222us
    digitalWrite(pin, LOW);
    delayMicroseconds(167);  // 75% of 222us
  }
}

// Method 5: Multi-Pulse Stacking (CPMG Coherent Stacking)
void send_pulse_stacked(int pin) {
  send_pulse_partition(pin, 15);
  delayMicroseconds(100);  
  send_pulse_partition(pin, 15);
  delayMicroseconds(100);
  send_pulse_partition(pin, 20);
}

// Floquet Sub-Harmonic Pump at 2.25 kHz
void run_floquet_pump(int pin, int duration_ms) {
  if (duration_ms <= 0) return;
  unsigned long start_time = millis();
  while (millis() - start_time < (unsigned long)duration_ms) {
    digitalWrite(pin, HIGH);
    delayMicroseconds(30);
    digitalWrite(pin, LOW);
    delayMicroseconds(414);
  }
}

// Active TAP Decay Sweep (Method 5)
void run_active_tap_sweep() {
  Serial.println("\n--- START ACTIVE TAP STABILIZATION SWEEP (METHOD: 5) ---");
  for (int delay_ms = 0; delay_ms <= 300; delay_ms += 10) {
    send_pulse_stacked(TX2_PIN);
    run_floquet_pump(TX2_PIN, delay_ms);
    digitalWrite(TX2_PIN, LOW);
    
    // Sample receiver pin A1
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
    
    delay(200); 
  }
  Serial.println("--- END ACTIVE TAP STABILIZATION SWEEP (METHOD: 5) ---");
}

// Helper to fire overlapping phase-delayed pulses at 4.5 kHz (222 us period)
void fire_phase_pulses(int phase_delay, int cycles) {
  for (int i = 0; i < cycles; i++) {
    if (phase_delay < 50) {
      // Overlapping:
      // t = 0: TX1 -> HIGH
      // t = phase_delay: TX2 -> HIGH
      // t = 50: TX1 -> LOW
      // t = 50 + phase_delay: TX2 -> LOW
      digitalWrite(TX1_PIN, HIGH);
      delayMicroseconds(phase_delay);
      digitalWrite(TX2_PIN, HIGH);
      delayMicroseconds(50 - phase_delay);
      digitalWrite(TX1_PIN, LOW);
      delayMicroseconds(phase_delay);
      digitalWrite(TX2_PIN, LOW);
      delayMicroseconds(122 - phase_delay); // 122 + 50 + 50 = 222 us total period
    } else {
      // Non-overlapping:
      // t = 0: TX1 -> HIGH
      // t = 50: TX1 -> LOW
      // t = phase_delay: TX2 -> HIGH
      // t = phase_delay + 50: TX2 -> LOW
      digitalWrite(TX1_PIN, HIGH);
      delayMicroseconds(50);
      digitalWrite(TX1_PIN, LOW);
      delayMicroseconds(phase_delay - 50);
      digitalWrite(TX2_PIN, HIGH);
      delayMicroseconds(50);
      digitalWrite(TX2_PIN, LOW);
      // Wait remaining time to keep period exactly at 222 us
      int remaining = 122 - phase_delay;
      if (remaining > 0) {
        delayMicroseconds(remaining);
      } else {
        delayMicroseconds(2);
      }
    }
  }
}

// New: Tetrahedral Phase Sweep for the 6cap Tetrahedron
// Sweeps the phase delay between Node A (Pin 3) and Node B (Pin 5)
// to show constructive (0us) and destructive (111us) wave interference.
void run_tetrahedral_phase_sweep() {
  Serial.println("\n--- START TETRAHEDRAL PHASE SWEEP ---");
  
  for (int phase_delay = 0; phase_delay <= 115; phase_delay += 5) {
    // Fire phase-interfered cycles
    fire_phase_pulses(phase_delay, 30);
    
    // Sample receiver Node C (Pin A1)
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
    Serial.print(phase_delay);
    Serial.print("us | Amplitude:");
    Serial.print(amp);
    Serial.print(" [Min: ");
    Serial.print(min_val);
    Serial.print(", Max: ");
    Serial.print(max_val);
    Serial.println("]");
    
    delay(100); 
  }
  
  Serial.println("--- END TETRAHEDRAL PHASE SWEEP ---");
}

void setup() {
  Serial.begin(115200);
  pinMode(TX1_PIN, OUTPUT);
  pinMode(TX2_PIN, OUTPUT);
  pinMode(13, OUTPUT);
  
  // Enable internal pull-up on RX_PIN to stop floating hum
  pinMode(RX_PIN, INPUT_PULLUP);
  digitalWrite(TX1_PIN, LOW);
  digitalWrite(TX2_PIN, LOW);
  
  Serial.println("==================================================");
  Serial.println("  TAP ACTIVE STABILIZATION CORE (D3 + D5 -> A1)   ");
  Serial.println("  Commands: 't'->Tetrahedral Sweep, '5'->Decay Sweep");
  Serial.println("==================================================");
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == 't') {
      run_tetrahedral_phase_sweep();
    } else if (cmd == '5') {
      run_active_tap_sweep();
    } else if (cmd == '0') {
      continuous_print = !continuous_print;
      if (continuous_print) {
        Serial.println("\n        SILENT REAL-TIME MONITOR ACTIVE");
      } else {
        Serial.println("\n        SILENT REAL-TIME MONITOR DEACTIVATED");
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
    digitalWrite(TX1_PIN, LOW);
    digitalWrite(TX2_PIN, LOW);
  }
}
