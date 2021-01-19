#include <OneWire.h>
#include <DallasTemperature.h>

#define TSLserialNR "LENSS_TSL_000X"
#define ONE_WIRE_BUS 2

volatile unsigned long cnt = 0;
unsigned long t = 0;
unsigned long last;

int DigPin = 3; // Digital pin that the TSL connects to
int TslPwr = 5; // Power output pin to activate and deactivate TSL
int IntPin = 0; // Interupt number that the TSL uses (must connect to DigPin)

unsigned long hz;
unsigned long oldcnt;

int inByte = 0; //incoming serial byte

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

void irq1() {
  cnt++;
}

void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ;
  }
  Serial.println("START");
  delay(1000);
  
  pinMode(DigPin, INPUT);
  pinMode(TslPwr, OUTPUT);
  digitalWrite(DigPin, HIGH);
  pinMode(TslPwr, HIGH);
  attachInterrupt(IntPin, irq1, RISING);
  
  sensors.begin();
}

void loop() 
{
  float lux = analogRead(A5);
  float AVolt = lux * 3.3/1023;
  sensors.requestTemperatures();
  
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
    Serial.print(AVolt); Serial.print(",");
    last = millis();
    Serial.print(hz); Serial.print(",");
    oldcnt = t;

    Serial.print(sensors.getTempCByIndex(0)); Serial.print(",");
    Serial.print(millis()); Serial.print(",");
    Serial.println(TSLserialNR);
  }
}
