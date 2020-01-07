volatile unsigned long cnt = 0;
unsigned long oldcnt = 0;
unsigned long t = 0;
unsigned long last;
int DigPin = 2;
int TslPwr = 8;
int IntPin = 0;
const int TempSensorPin = 0; //the analog pin the TMP36's Vout (sense) pin is connected to
unsigned long hz;

void irq1()
{
  cnt++;
}

///////////////////////////////////////////////////////////////////
//
// SETUP
//
void setup() 
{
  Serial.begin(115200);
  Serial.println("START");
  delay(1000);
  pinMode(DigPin, INPUT);
  pinMode(TslPwr, OUTPUT);
  digitalWrite(DigPin, HIGH);
  pinMode(TslPwr, HIGH);
  attachInterrupt(IntPin, irq1, RISING);
}

///////////////////////////////////////////////////////////////////
//
// MAIN LOOP
//
void loop() 
{
  float lux = analogRead(A5);
  float AVolt = lux * 5/1023;
  
  if (AVolt > 2.5)
  {
    digitalWrite(TslPwr, LOW);
    hz = 0;
  }
  else
  {
    digitalWrite(TslPwr, HIGH);
    if (millis() - last >= 1000)
    {
      t = cnt;
      hz = t - oldcnt;
    }
  }
  
  if (millis() - last >= 1000)
  {
    Serial.print(AVolt); Serial.print(" | ");
    last = millis();
    Serial.print("FREQ: "); 
    Serial.print(hz);
    Serial.print(" = "); 
    Serial.print((hz+50)/100);  // +50 == rounding last digit
    Serial.print(" mW/m2; ");
    oldcnt = t;

    int reading = analogRead(TempSensorPin);
    float voltage = reading * 5.0;
    voltage /= 1024.0;
    Serial.print("\t");
    Serial.print(voltage); Serial.print(" volts; ");
    float tempC = (voltage - 0.5) * 100;
    Serial.print(tempC); Serial.print(" degrees C; ");
    float tempF = 1.8 * tempC + 32;
    Serial.print(tempF); Serial.println(" degrees F");
    
    if (millis() % 3600000 == 0)
    {
      cnt = 0;
      oldcnt = 0;
    }
  }
}
