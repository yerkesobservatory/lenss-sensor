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
int TslPwr = 8;
int IntPin = 0;
const int TempSensorPin = 0; //the analog pin the TMP36's Vout (sense) pin is connected to
unsigned long hz;

int inByte = 0; //incoming serial byte

void irq1() {
  cnt++;
}

void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ;
  }
  establishcontact();
  Serial.println("START");
  delay(1000);
  pinMode(DigPin, INPUT);
  pinMode(TslPwr, OUTPUT);
  digitalWrite(DigPin, HIGH);
  pinMode(TslPwr, HIGH);
  attachInterrupt(IntPin, irq1, RISING);

  Serial.println("Time,Light Voltage,Frequency,Temperature Voltage,Temperature (Degrees C),Temperature (Degrees F)");
}
void loop() {
  if (Serial.available() <= 0) {
    inByte = Serial.read();
    if (millis() - last >= 1000) {
      last = millis();
      t = cnt;
      unsigned long hz = t;
      Serial.print("FREQ: "); 
      Serial.print(hz);

      int reading = analogRead(TempSensorPin);
      float voltage = reading * 5.0;
      voltage /= 1024.0;
      Serial.print("\t");
      Serial.print(voltage);
      float tempC = (voltage - 0.5) * 100;
      Serial.print(tempC);
      float tempF = tempC * 1.8 + 32;
      Serial.println(tempF);

      //Write data to serial port
      Serial.write(voltage);
      Serial.write(tempC);
      Serial.write(tempF);
    
      cnt = 0;

  } else {
    // not sure yet
  }
}

void establishcontact() {
  while (Serial.available() <= 0) {
    Serial.print('A');
    delay(300);
  }
}
