// TODO:
//
// Add more comments for what functions do
// -or-
// Create README for the program with info on what 
// each function does and some clarification on 
// pin assignments

volatile unsigned long cnt = 0;
unsigned long t = 0;
unsigned long last;
int DigPin = 2;
int IntPin = 0;
const int TempSensorPin = 0; //the analog pin the TMP36's Vout (sense) pin is connected to

int inByte = 0; //incoming serial byte

void irq1() {
  cnt++;
}

///////////////////////////////////////////////////////////////////
//
// SETUP: Start and wait for serial connection, assign pins, and 
// setup attatch interupt.
//
///////////////////////////////////////////////////////////////////
void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ;
  }
  establishcontact();
  Serial.println("START");
  delay(1000);
  pinMode(DigPin, INPUT);
  digitalWrite(DigPin, HIGH);
  attachInterrupt(IntPin, irq1, RISING);
}

///////////////////////////////////////////////////////////////////
//
// MAIN LOOP: Something goes here
//
///////////////////////////////////////////////////////////////////
void loop() {
  if (Serial.available() <= 0) {
    if (millis() - last >= 1000) {
      last = millis();
      t = cnt;
      unsigned long hz = t;
      Serial.print("FREQ: "); 
      Serial.print(hz);
      Serial.print(" = "); 
      Serial.print((hz+50)/100);  // +50 == rounding last digit
      Serial.print(" mW/m2; ");

      int reading = analogRead(TempSensorPin);
      float voltage = reading * 5.0;
      voltage /= 1024.0;
      Serial.print("\t");
      Serial.print(voltage); Serial.print(" volts; ");
      float tempC = (voltage - 0.5) * 100;
      Serial.print(tempC); Serial.print(" degrees C; ");
      float tempF = tempC * 1.8 + 32;
      Serial.print(tempF); Serial.println(" degrees F");
    
      cnt = 0;

  } else {
    // not sure yet
  }
}

///////////////////////////////////////////////////////////////////
//
// Establish Contact: send 'calibration' character for recieving 
// program
//
///////////////////////////////////////////////////////////////////
void establishcontact() {
  while (Serial.available() <= 0) {
    Serial.print('A');
    delay(300);
  }
}
