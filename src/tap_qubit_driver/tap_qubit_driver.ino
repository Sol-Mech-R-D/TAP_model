#include <Arduino.h>

const int TX1_PIN = 3;  // Node A (Tetrahedron) / Pump Pin D3 (Ratchet C1)
const int TX2_PIN = 5;  // Node B (Tetrahedron) / Tx Pin D5 (Ratchet D1)
const int RX_PIN = A0;  // Node C (Tetrahedron) / Read Pin A0 (Ratchet C2)
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
  pinMode(RX_PIN, INPUT_PULLUP); // enable pull-up strictly for AC sweeps
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
      digitalWrite(TX1_PIN, HIGH);
      delayMicroseconds(phase_delay);
      digitalWrite(TX2_PIN, HIGH);
      delayMicroseconds(50 - phase_delay);
      digitalWrite(TX1_PIN, LOW);
      delayMicroseconds(phase_delay);
      digitalWrite(TX2_PIN, LOW);
      delayMicroseconds(122 - phase_delay);
    } else {
      digitalWrite(TX1_PIN, HIGH);
      delayMicroseconds(50);
      digitalWrite(TX1_PIN, LOW);
      delayMicroseconds(phase_delay - 50);
      digitalWrite(TX2_PIN, HIGH);
      delayMicroseconds(50);
      digitalWrite(TX2_PIN, LOW);
      int remaining = 122 - phase_delay;
      if (remaining > 0) {
        delayMicroseconds(remaining);
      } else {
        delayMicroseconds(2);
      }
    }
  }
}

// Tetrahedral Phase Sweep for the 6cap Tetrahedron
void run_tetrahedral_phase_sweep() {
  pinMode(RX_PIN, INPUT_PULLUP); // enable pull-up strictly for AC sweeps
  Serial.println("\n--- START TETRAHEDRAL PHASE SWEEP ---");
  
  for (int phase_delay = 0; phase_delay <= 115; phase_delay += 5) {
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

// Helper function to actively drain Node 2 (C2) to GND using Pin A1 in software
void active_software_discharge() {
  pinMode(RX_PIN, OUTPUT);
  digitalWrite(RX_PIN, LOW);
  delay(200); // wait for charge to flow to GND (extended to ensure 10uF is fully drained)
  pinMode(RX_PIN, INPUT); // return to high-impedance read state
  delay(20);
}

// Ratchet Forward Sequence (pumps charge)
// Uses optimized 15us pulses to charge C1 (10nF) while maintaining charge accumulation on C2 (1uF/10uF)
void run_ratchet_forward() {
  Serial.println("\n--- RATCHET SEQUENCE: FORWARD (Pumping Charge) ---");
  
  // 1. Software Discharge C2 first
  active_software_discharge();
  
  // Clean start: hold pins low first
  digitalWrite(TX1_PIN, LOW);
  digitalWrite(TX2_PIN, LOW);
  delay(100);

  // Pulse in the correct order:
  // t1: D5 (TX2) HIGH for 15us to charge C1
  // t2: D3 (TX1) HIGH for 15us to pump charge into C2
  // t3: D5 LOW
  // t4: D3 LOW
  for (int step = 0; step < 100; step++) {
    digitalWrite(TX2_PIN, HIGH);
    delayMicroseconds(15);
    digitalWrite(TX1_PIN, HIGH);
    delayMicroseconds(15);
    digitalWrite(TX2_PIN, LOW);
    delayMicroseconds(15);
    digitalWrite(TX1_PIN, LOW);
    delayMicroseconds(15);
    
    if (step % 5 == 0) {
      int val = analogRead(RX_PIN);
      float voltage = (val / 1023.0) * 5.0;
      Serial.print("Step:");
      Serial.print(step);
      Serial.print(" | ADC:");
      Serial.print(val);
      Serial.print(" | Voltage:");
      Serial.print(voltage);
      Serial.println("V");
    }
    delay(10);
  }
  Serial.println("--- END RATCHET SEQUENCE: FORWARD ---");
}

// Ratchet Reversed Sequence (blocks charge)
void run_ratchet_backward() {
  Serial.println("\n--- RATCHET SEQUENCE: REVERSED (No Pumping) ---");
  
  // 1. Software Discharge C2 first
  active_software_discharge();
  
  digitalWrite(TX1_PIN, LOW);
  digitalWrite(TX2_PIN, LOW);
  delay(100);

  // Pulse in the wrong order:
  // t1: D3 (TX1) HIGH 
  // t2: D5 (TX2) HIGH 
  // t3: D3 LOW
  // t4: D5 LOW
  for (int step = 0; step < 100; step++) {
    digitalWrite(TX1_PIN, HIGH);
    delayMicroseconds(15);
    digitalWrite(TX2_PIN, HIGH);
    delayMicroseconds(15);
    digitalWrite(TX1_PIN, LOW);
    delayMicroseconds(15);
    digitalWrite(TX2_PIN, LOW);
    delayMicroseconds(15);
    
    if (step % 5 == 0) {
      int val = analogRead(RX_PIN);
      float voltage = (val / 1023.0) * 5.0;
      Serial.print("Step:");
      Serial.print(step);
      Serial.print(" | ADC:");
      Serial.print(val);
      Serial.print(" | Voltage:");
      Serial.print(voltage);
      Serial.println("V");
    }
    delay(10);
  }
  Serial.println("--- END RATCHET SEQUENCE: REVERSED ---");
}

void setup() {
  Serial.begin(115200);
  pinMode(TX1_PIN, OUTPUT);
  pinMode(TX2_PIN, OUTPUT);
  pinMode(13, OUTPUT);
  
  // Set RX_PIN to standard high-impedance INPUT by default (NO PULLUP)
  // to prevent charging the storage capacitor in ratchet tests
  pinMode(RX_PIN, INPUT);
  digitalWrite(TX1_PIN, LOW);
  digitalWrite(TX2_PIN, LOW);
  
  Serial.println("==================================================");
  Serial.println("  TAP ACTIVE STABILIZATION CORE (D3 + D5 -> A1)   ");
  Serial.println("  Commands: 't'->Tetrahedral Sweep, '5'->Decay Sweep");
  Serial.println("            'f'->Ratchet Forward,   'b'->Ratchet Reversed");
  Serial.println("==================================================");
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == 't') {
      run_tetrahedral_phase_sweep();
    } else if (cmd == '5') {
      run_active_tap_sweep();
    } else if (cmd == 'f') {
      run_ratchet_forward();
    } else if (cmd == 'b') {
      run_ratchet_backward();
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
