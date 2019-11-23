/* TSL2591 Digital Light Sensor */
/* Dynamic Range: 600M:1 */
/* Maximum Lux: 88K */

//all necessary libraries
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include "Adafruit_TSL2591.h"
#include <SPI.h>
#include <SD.h>
#include "RTClib.h"

RTC_PCF8523 rtc;
const int chipSelect = 13; //Sets the SD card to pin 13; more info is on the original tutorial
volatile unsigned long cnt = 0; //positive long integer that will change while the system is interrupted for counts
unsigned long oldcnt = 0; //positive long integer to store previous counts
unsigned long t = 0; //for transferring values between iterations of the loop
unsigned long last; //the time of the last sensor reading
unsigned long hz; //frequency value

void irql()
{
  cnt++;
}

void setup(void) 
{
  Serial.begin(115200);
  pinMode(2, INPUT);
  digitalWrite(2, HIGH);
  attachInterrupt(0, irql, RISING);

  if (! rtc.begin()) {
    Serial.println("Couldn't find RTC");
    while (1);
  }

  if (! rtc.initialized()) {
    Serial.println("RTC is NOT running!");
    // following line sets the RTC to the date & time this sketch was compiled
    // rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
    // This line sets the RTC with an explicit date & time, for example to set
    // January 21, 2014 at 3am you would call:
    // rtc.adjust(DateTime(2014, 1, 21, 3, 0, 0));
  } 
  Serial.print("Initializing SD card..."); //Lets user know the card is being loaded

  // see if the card is present and can be initialized:
  if (!SD.begin(chipSelect)) { //If the SD fails to be loaded
    Serial.println("Card failed, or not present");
    // don't do anything more:
    return;
  }
  Serial.println("card initialized."); //This will only appear if it skips the above loop, meaning only when the card is loaded.

  File dataFile = SD.open("testing.csv", FILE_WRITE); //Opens a file, and stores it as dataFile
  if(dataFile) {
    dataFile.println("Date,Time,IR,Full,Visible,Lux");
  }
  else {
    Serial.println("error opening file"); //This line only activates if the file was never opened.
  }
  dataFile.close();
}

/**************************************************************************/
/*
    Show how to read IR and Full Spectrum at once and convert to lux
*/
/**************************************************************************/
void advancedRead(void)
{
  if (millis() - last >= 1000) //1 second after the last reading...
  {
    last = millis(); //sets the time this occurs at as the last value for the next iteration
    t = cnt;
    hz = t - oldcnt; //frequency is the change in counts
    Serial.println("FREQ: "); 
    Serial.print(hz);
    oldcnt = t; //the current count value is turned into the old count value.
  }

  DateTime now = rtc.now();

     // The below code will copy the readings above into a string to paste into the file created by the datalog shield.
  
  File dataFile = SD.open("testing.csv", FILE_WRITE);
  if (dataFile) { //Once the file is open, it will print the string generated in the current loop before closing until the next loop
    dataFile.print(now.month(), DEC); dataFile.print("/"); dataFile.print(now.day(), DEC); dataFile.print(","); 
    dataFile.print(now.hour(), DEC); dataFile.print(":"); dataFile.print(now.minute(), DEC); dataFile.print(":"); dataFile.print(now.second(), DEC); dataFile.print(","); dataFile.print(hz);
  }
  else {
    Serial.println("error opening file"); //This line only activates if the file was never opened.
  }
}

/**************************************************************************/
/*
    Arduino loop function, called once 'setup' is complete (your own code
    should go here)
*/
/**************************************************************************/
void loop(void) 
{  
  advancedRead();
  
  delay(400);
}
