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
void fire_phase_pulses(int phase_delay, uint32_t cycles) {
  for (uint32_t i = 0; i < cycles; i++) {
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

// Generic pulse generator with variable frequency and phase delay
void fire_phase_pulses_variable(int freq_hz, int phase_delay_us, uint32_t cycles) {
  long period_us = 1000000L / freq_hz;
  long pulse_width = period_us / 4; // 25% duty cycle
  if (pulse_width < 2) pulse_width = 2; // safety clamp
  
  for (uint32_t i = 0; i < cycles; i++) {
    if (phase_delay_us < pulse_width) {
      digitalWrite(TX1_PIN, HIGH);
      delayMicroseconds(phase_delay_us);
      digitalWrite(TX2_PIN, HIGH);
      delayMicroseconds(pulse_width - phase_delay_us);
      digitalWrite(TX1_PIN, LOW);
      delayMicroseconds(phase_delay_us);
      digitalWrite(TX2_PIN, LOW);
      delayMicroseconds(period_us - pulse_width - phase_delay_us);
    } else {
      digitalWrite(TX1_PIN, HIGH);
      delayMicroseconds(pulse_width);
      digitalWrite(TX1_PIN, LOW);
      delayMicroseconds(phase_delay_us - pulse_width);
      digitalWrite(TX2_PIN, HIGH);
      delayMicroseconds(pulse_width);
      digitalWrite(TX2_PIN, LOW);
      long remaining = period_us - phase_delay_us - pulse_width;
      if (remaining > 0) {
        delayMicroseconds(remaining);
      } else {
        delayMicroseconds(2);
      }
    }
  }
}

// Tetrahedral Phase Sweep for the 6cap Tetrahedron (direct AC measurement)
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

// Helper function to actively drain Node 2 (C2) to GND using Pin A0 in software
void active_software_discharge() {
  pinMode(RX_PIN, OUTPUT);
  digitalWrite(RX_PIN, LOW);
  delay(200); // wait for charge to flow to GND
  pinMode(RX_PIN, INPUT); // return to high-impedance read state
  delay(20);
}

// Coupled Waveguide Phase Sweep ('c')
void run_coupled_phase_sweep() {
  Serial.println("\n--- START COUPLED WAVEGUIDE PHASE SWEEP ---");
  pinMode(RX_PIN, INPUT);
  
  for (int phase_delay = 0; phase_delay <= 115; phase_delay += 5) {
    active_software_discharge();
    fire_phase_pulses(phase_delay, 2000);
    
    int val = analogRead(RX_PIN);
    float voltage = (val / 1023.0) * 5.0;
    
    Serial.print("PhaseDelay:");
    Serial.print(phase_delay);
    Serial.print("us | ADC:");
    Serial.print(val);
    Serial.print(" | Voltage:");
    Serial.print(voltage);
    Serial.println("V");
    
    delay(100);
  }
  Serial.println("--- END COUPLED WAVEGUIDE PHASE SWEEP ---");
}

// Option 1: Resonant Spectral Sweep ('s') - Frequency Sweep
void run_resonant_spectral_sweep() {
  Serial.println("\n--- START RESONANT SPECTRAL SWEEP ---");
  pinMode(RX_PIN, INPUT);
  
  for (int freq = 1000; freq <= 15000; freq += 250) {
    active_software_discharge();
    
    // Calculate cycles to pump for a constant 400ms duration
    long period_us = 1000000L / freq;
    int cycles = 400000L / period_us;
    if (cycles < 10) cycles = 10;
    
    // Fire with 0us phase delay (fully constructive)
    fire_phase_pulses_variable(freq, 0, cycles);
    
    int val = analogRead(RX_PIN);
    float voltage = (val / 1023.0) * 5.0;
    
    Serial.print("Freq:");
    Serial.print(freq);
    Serial.print("Hz | ADC:");
    Serial.print(val);
    Serial.print(" | Voltage:");
    Serial.print(voltage);
    Serial.println("V");
    
    delay(50);
  }
  Serial.println("--- END RESONANT SPECTRAL SWEEP ---");
}

// Option 2: T1 Energy Relaxation Decay Sweep ('d')
void run_t1_relaxation_sweep() {
  Serial.println("\n--- START T1 RELAXATION SWEEP ---");
  pinMode(RX_PIN, INPUT);
  
  active_software_discharge();
  
  // 1. Pump capacitor to maximum using constructive 4.5kHz pulses for 10 seconds
  Serial.println("  [PUMP] Charging storage reservoir...");
  fire_phase_pulses(0, 45000);
  
  // 2. Shut off drivers immediately
  digitalWrite(TX1_PIN, LOW);
  digitalWrite(TX2_PIN, LOW);
  
  // 3. Monitor decay at high resolution (every 500ms for 60 seconds)
  Serial.println("  [MONITOR] Measuring decay curve...");
  for (int i = 0; i <= 120; i++) {
    int val = analogRead(RX_PIN);
    float voltage = (val / 1023.0) * 5.0;
    
    Serial.print("DecayTime:");
    Serial.print((long)i * 500);
    Serial.print("ms | ADC:");
    Serial.print(val);
    Serial.print(" | Voltage:");
    Serial.print(voltage);
    Serial.println("V");
    
    delay(500);
  }
  Serial.println("--- END T1 RELAXATION SWEEP ---");
}

// Option 3: Two-Tone Floquet Drive Sweep ('w')
// Sweeps the sub-harmonic modulation ratio (ratio of envelope period to carrier period)
void run_two_tone_floquet_sweep() {
  Serial.println("\n--- START TWO-TONE FLOQUET SWEEP ---");
  pinMode(RX_PIN, INPUT);
  
  // Sweep carrier frequency from 2kHz to 12kHz in 500Hz steps with a fixed 1:2 Floquet subharmonic pump
  for (int carrier_freq = 2000; carrier_freq <= 12000; carrier_freq += 500) {
    active_software_discharge();
    
    // We drive TX2 at carrier_freq, and TX1 at carrier_freq / 2 (sub-harmonic pump)
    long period_us = 1000000L / carrier_freq;
    int cycles = 400000L / period_us;
    
    // Phase delay is set to half the period of the subharmonic pump
    long subharmonic_delay = period_us; // 1 cycle phase delay of carrier = 0.5 cycle of subharmonic
    
    fire_phase_pulses_variable(carrier_freq / 2, subharmonic_delay, cycles / 2);
    
    int val = analogRead(RX_PIN);
    float voltage = (val / 1023.0) * 5.0;
    
    Serial.print("CarrierFreq:");
    Serial.print(carrier_freq);
    Serial.print("Hz | ADC:");
    Serial.print(val);
    Serial.print(" | Voltage:");
    Serial.print(voltage);
    Serial.println("V");
    
    delay(50);
  }
  Serial.println("--- END TWO-TONE FLOQUET SWEEP ---");
}

// Option 4: Combined 2D Spatio-Temporal Sweep ('m')
// Sweeps both Frequency (2kHz to 12kHz) and Phase Delay (0 to 80us) to map a 2D eigenmode heatmap.
void run_combined_2d_sweep() {
  Serial.println("\n--- START COMBINED 2D SWEEP ---");
  pinMode(RX_PIN, INPUT);
  
  for (int freq = 2000; freq <= 10000; freq += 1000) {
    long period_us = 1000000L / freq;
    long pulse_width = period_us / 4;
    
    for (int phase = 0; phase <= 80; phase += 10) {
      active_software_discharge();
      
      int cycles = 200000L / period_us;
      if (cycles < 10) cycles = 10;
      
      fire_phase_pulses_variable(freq, phase, cycles);
      
      int val = analogRead(RX_PIN);
      float voltage = (val / 1023.0) * 5.0;
      
      Serial.print("2D | Freq:");
      Serial.print(freq);
      Serial.print("Hz | Phase:");
      Serial.print(phase);
      Serial.print("us | ADC:");
      Serial.print(val);
      Serial.print(" | Voltage:");
      Serial.print(voltage);
      Serial.println("V");
      
      delay(20);
    }
  }
  Serial.println("--- END COMBINED 2D SWEEP ---");
}

// Ratchet Forward Sequence (pumps charge)
void run_ratchet_forward() {
  Serial.println("\n--- RATCHET SEQUENCE: FORWARD (Pumping Charge) ---");
  
  // 1. Software Discharge C2 first
  active_software_discharge();
  
  // Clean start: hold pins low first
  digitalWrite(TX1_PIN, LOW);
  digitalWrite(TX2_PIN, LOW);
  delay(100);

  // Pulse in the correct order:
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
  
  pinMode(RX_PIN, INPUT);
  digitalWrite(TX1_PIN, LOW);
  digitalWrite(TX2_PIN, LOW);
  
  Serial.println("==================================================");
  Serial.println("  TAP ACTIVE STABILIZATION CORE (D3 + D5 -> A0)   ");
  Serial.println("  Commands: 't'->Tetrahedral Sweep, '5'->Decay Sweep");
  Serial.println("            'f'->Ratchet Forward,   'b'->Ratchet Reversed");
  Serial.println("            'c'->Coupled Waveguide Phase Sweep");
  Serial.println("            's'->Resonant Spectral Sweep");
  Serial.println("            'd'->T1 Energy Relaxation Sweep");
  Serial.println("            'w'->Two-Tone Floquet Sweep");
  Serial.println("            'm'->Combined 2D Heatmap Sweep");
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
    } else if (cmd == 'c') {
      run_coupled_phase_sweep();
    } else if (cmd == 's') {
      run_resonant_spectral_sweep();
    } else if (cmd == 'd') {
      run_t1_relaxation_sweep();
    } else if (cmd == 'w') {
      run_two_tone_floquet_sweep();
    } else if (cmd == 'm') {
      run_combined_2d_sweep();
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
