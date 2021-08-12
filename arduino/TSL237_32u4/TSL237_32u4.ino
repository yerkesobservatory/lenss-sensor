#include <OneWire.h> //temperature Sensor Libraries
#include <DallasTemperature.h> 

#define TSLserialNR "LENSS_TSL_000X" //establishes fixed ID number
#define ONE_WIRE_BUS 2 //data pin for the temp sensor

volatile unsigned long cnt = 0; //preps variables; cnt is photon count,
unsigned long t = 0; //t is used to copy values from other variables,
unsigned long last = 0; //last is the benchmark for how much time passes

int DigPin = 3; //DigPin and IntPin refer to the same spot, but interrupt and digital pins have different names
int TslPwr = 5; //digital pin used to power tsl for convenient on/off switch
int IntPin = 0;

unsigned long hz; //frequency of photon counts per second
unsigned long oldcnt; //last recorded photon count
unsigned long T, Tlast; //time storage: T is current time and Tlast is the time from last loop
int delta; //time elapsed since last data point
String message; //message carried to pi
float lux; //raw output from photoresistor circuit
float volt; //output converted to voltage

int inByte = 0; //incoming serial byte

OneWire oneWire(ONE_WIRE_BUS); //sets the temp sensor from a oneWire port
DallasTemperature sensors(&oneWire);

void irq1() {
  cnt++; //simple increase by one each time irql gets called
}

void setup() { //setup is a special function that runs once at the start of an arduino code
  Serial.begin(9600); //begins serial operation at 9600 baudrate
  while (!Serial) {
    ; //cease operations if data won't reach pi
  }
  pinMode(DigPin, INPUT); //sets up digital pins; outputs send power, inputs receive info
  pinMode(TslPwr, OUTPUT);
  digitalWrite(DigPin, HIGH); //TSL switched on
  pinMode(TslPwr, HIGH);
  attachInterrupt(IntPin, irq1, RISING); //interrupt to run irql (cnt++) every time data comes from the interrupt pin
  
  sensors.begin(); //initializes temp sensor
}

void loop() //loop is the other special function of arduinos; it repeats indefinitely
{
 
  lux = analogRead(A5); //reads A5
  volt = lux * 3.3/1023; //corrects lux from a scale of 1023 (analog scale) to 3.3 (voltage received)
  sensors.requestTemperatures(); //reads temp sensor
  
  if (volt > 2.0)
  {
    digitalWrite(TslPwr, LOW); //shuts down tsl when it's too bright
  }
  else
  {
    digitalWrite(TslPwr, HIGH); //switches back on when dark enough
  }

  T = millis(); //store the time before check
  delta = T - last;  //gets elapsed time stored in delta
  if (delta >= 1000) //after 1 second
  {
    while( T-last > 1000) { last += 1000; } //increases last by 1 second intervals; while loop prioritizes action
    t = cnt; //because interrupt is incredibly fast, t stores the count right when the reading is taken
    hz = round((t - oldcnt)*1000/(T-Tlast)); //takes photon counts and puts them in Hz (#/s)
    oldcnt = t; //remembers last count to calculate Hz next loop
    message = String(volt)+","+String(hz)+","+String(sensors.getTempCByIndex(0))+","+
              String(TSLserialNR);
    Serial.println(message); //assembles message and sends it to the pi
    Tlast = T;
  }
}
