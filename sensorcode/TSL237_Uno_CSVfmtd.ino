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
  Serial.println("Light Sensor Voltage (volts),,Frequency (hz),Luminosity (mW/m2),,Temp Sensor Voltage (volts),Temperature (Degrees C),Temperature (Degrees F)");
  delay(1000);
  pinMode(DigPin, INPUT); //Sets the corresponding pin to receive data from the light-to-frequency (tsl) sensor
  pinMode(TslPwr, OUTPUT); //Sets the power pin of the tsl to draw power from a digital pin on the arduino
  digitalWrite(DigPin, HIGH); //Turns on DigPin
  pinMode(TslPwr, HIGH); //Turns on TslPwr
  attachInterrupt(IntPin, irq1, RISING); //Every time the interrupt pin of the tsl registers, the arduino will drop everything and bump up the frequency before proceeding.
}

///////////////////////////////////////////////////////////////////
//
// MAIN LOOP
//
void loop() 
{
  float lux = analogRead(A5);
  float AVolt = lux * 5/1023; //Converts from within the 0-1023 bounds of analog data to the 0-5 bounds of voltage
  
  if (AVolt > 2.5) //Sets an upper bound for what the light sensor is allowed to have to prevent overload
  {
    digitalWrite(TslPwr, LOW); //Kills tsl sensor if bound exceeded
    hz = 0;
  }
  else
  {
    digitalWrite(TslPwr, HIGH);
    if (millis() - last >= 1000) //Used to measure 1 second around interrupts
    {
      t = cnt;
      hz = t - oldcnt;
    }
  }
  
  if (millis() - last >= 1000)
  {
    Serial.print(AVolt); Serial.print(",,"); //Commas used for separating columns in a csv file
    last = millis();
    Serial.print(hz); Serial.print(",");
    Serial.print((hz+50)/100); Serial.print(",,"); //The original creator of this chunk of the code used 1/100 as a reasonable conversion factor for hz-->mW/m2. 
                                                   //Integer division just moves place values and cuts the decimal, so +50 allows the number to round and remain an integer.
    oldcnt = t;

    int reading = analogRead(TempSensorPin);
    float voltage = reading * 5.0;
    voltage /= 1024.0; //Converts to volts similarly to how the analog voltage readings from the light sensor did earlier did earlier
    Serial.print(voltage); Serial.print(",");
    float tempC = (voltage - 0.5) * 100;
    Serial.print(tempC); Serial.print(",");
    float tempF = 1.8 * tempC + 32;
    Serial.println(tempF);
    
    if (millis() % 3600000 == 0) //Every hour...
    {
      cnt = 0;
      oldcnt = 0;
    }
  }
}
