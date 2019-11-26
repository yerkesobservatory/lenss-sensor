volatile unsigned long cnt = 0;
unsigned long oldcnt = 0;
unsigned long t = 0;
unsigned long last;
int DigPin = 2;
int IntPin = 0;

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
  digitalWrite(DigPin, HIGH);
  attachInterrupt(IntPin, irq1, RISING);
}

///////////////////////////////////////////////////////////////////
//
// MAIN LOOP
//
void loop() 
{
  if (millis() - last >= 1000)
  {
    last = millis();
    t = cnt;
    unsigned long hz = t - oldcnt;
    Serial.print("FREQ: "); 
    Serial.print(hz);
    Serial.print("\t = "); 
    Serial.print((hz+50)/100);  // +50 == rounding last digit
    Serial.println(" mW/m2");
    oldcnt = t;
    if (millis() % 3600000 >= 0)
    {
      cnt = 0;
      oldcnt = 0;
    }
  }
}
