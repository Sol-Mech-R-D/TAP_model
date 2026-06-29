#include <Arduino.h>

const int TX_PIN = 5;   // Acoustic pulse transmitter (Pin 5)
const int RX_PIN = A1;  // Piezo feedback receiver (Analog 1)
const int SAMPLE_COUNT = 100;

bool continuous_print = false;

// Send a single pulse train using 3:1 partition (Method 2)
void send_pulse_partition(int cycles) {
  for (int i = 0; i < cycles; i++) {
    digitalWrite(TX_PIN, HIGH);
    delayMicroseconds(55);   // 25% of 222us
    digitalWrite(TX_PIN, LOW);
    delayMicroseconds(167);  // 75% of 222us
  }
}

// Method 5: Multi-Pulse Stacking (CPMG Coherent Stacking)
// Fires 3 consecutive wave packets with precise sub-millisecond delays to build up cavity amplitude
void send_pulse_stacked() {
  send_pulse_partition(15);
  delayMicroseconds(100);  // wait for acoustic reflections to set up
  send_pulse_partition(15);
  delayMicroseconds(100);
  send_pulse_partition(20);
}

// Floquet Sub-Harmonic Pump at 2.25 kHz
// Actively pumps the boundary interface during the decay delay to stabilize the qubit state
void run_floquet_pump(int duration_ms) {
  if (duration_ms <= 0) return;
  
  unsigned long start_time = millis();
  while (millis() - start_time < (unsigned long)duration_ms) {
    // 2.25 kHz pump wave (half-harmonic of 4.5 kHz) with ultra-low duty cycle (13.5%)
    // This injects weak parametric energy to hold the resonance without saturating the sensor
    digitalWrite(TX_PIN, HIGH);
    delayMicroseconds(30);
    digitalWrite(TX_PIN, LOW);
    delayMicroseconds(414);
  }
}

// Active TAP Decay Sweep (Method 5)
// Combines CPMG multi-pulse stacking with Floquet sub-harmonic parametric pumping during decay
void run_active_tap_sweep() {
  Serial.println("\n--- START ACTIVE TAP STABILIZATION SWEEP (METHOD: 5) ---");
  
  for (int delay_ms = 0; delay_ms <= 300; delay_ms += 10) {
    // 1. Excitation: Multi-Pulse Stacking
    send_pulse_stacked();
    
    // 2. Decay Phase: Run Floquet sub-harmonic pump
    run_floquet_pump(delay_ms);
    
    // Shut off transmitter pins
    digitalWrite(TX_PIN, LOW);
    
    // 3. Sensor Read: Sample receiver pin A1
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
  Serial.println("--- END ACTIVE TAP STABILIZATION SWEEP (METHOD: 5) ---");
}

void setup() {
  Serial.begin(115200);
  pinMode(TX_PIN, OUTPUT);
  pinMode(13, OUTPUT);
  
  // Enable internal pull-up on RX_PIN to stop floating hum
  pinMode(RX_PIN, INPUT_PULLUP);
  digitalWrite(TX_PIN, LOW);
  
  Serial.println("==================================================");
  Serial.println("  TAP ACTIVE STABILIZATION CORE (D5 -> A1)         ");
  Serial.println("  Commands: '5'->Active TAP Sweep, '0'->Toggle Monitor");
  Serial.println("==================================================");
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == '5') {
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
    digitalWrite(TX_PIN, LOW);
  }
}
