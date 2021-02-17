#include <OneWire.h>
#include <DallasTemperature.h>

#define TSLserialNR "LENSS_TSL_000X"
#define ONE_WIRE_BUS 2

volatile unsigned long cnt = 0;
unsigned long t = 0;
unsigned long last;

int DigPin = 3;
int TslPwr = 5;
int IntPin = 0;

unsigned long hz;
unsigned long oldcnt;
unsigned long T;
int delta;
String message;

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
  T = millis();
  delta = T - last;
  float lux = analogRead(A5);
  float AVolt = lux * 3.3/1023;
  sensors.requestTemperatures();
  
  if (AVolt > 2.5)
  {
    digitalWrite(TslPwr, LOW);
  }
  else
  {
    digitalWrite(TslPwr, HIGH);
  }
  
  if (T - last >= 1000)
  {
    last = T;
    t = cnt;
    hz = t - oldcnt;
    oldcnt = t;
    message = String(AVolt)+","+String(hz)+","+String(sensors.getTempCByIndex(0))+","+String(delta)+","+String(TSLserialNR);
    Serial.println(message);
  }
}
