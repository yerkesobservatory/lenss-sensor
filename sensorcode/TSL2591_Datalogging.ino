/* TSL2591 Digital Light Sensor */
/* Dynamic Range: 600M:1 */
/* Maximum Lux: 88K */

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include "Adafruit_TSL2591.h"
#include <SPI.h>
#include <SD.h>
#include "RTClib.h"

RTC_PCF8523 rtc;
const int chipSelect = 13; //Sets the SD card to pin 13; more info is on the original tutorial

// Example for demonstrating the TSL2591 library - public domain!

// connect SCL to I2C Clock
// connect SDA to I2C Data
// connect Vin to 3.3-5V DC
// connect GROUND to common ground

Adafruit_TSL2591 tsl = Adafruit_TSL2591(2591); // pass in a number for the sensor identifier (for your use later)

/**************************************************************************/
/*
    Displays some basic information on this sensor from the unified
    sensor API sensor_t type (see Adafruit_Sensor for more information)
*/
/**************************************************************************/

void displaySensorDetails(void)
{
  sensor_t sensor;
  tsl.getSensor(&sensor);
  Serial.println(F("------------------------------------"));
  Serial.print  (F("Sensor:       ")); Serial.println(sensor.name);
  Serial.print  (F("Driver Ver:   ")); Serial.println(sensor.version);
  Serial.print  (F("Unique ID:    ")); Serial.println(sensor.sensor_id);
  Serial.print  (F("Max Value:    ")); Serial.print(sensor.max_value); Serial.println(F(" lux"));
  Serial.print  (F("Min Value:    ")); Serial.print(sensor.min_value); Serial.println(F(" lux"));
  Serial.print  (F("Resolution:   ")); Serial.print(sensor.resolution, 4); Serial.println(F(" lux"));  
  Serial.println(F("------------------------------------"));
  Serial.println(F(""));
  delay(500);
}

/**************************************************************************/
/*
    Configures the gain and integration time for the TSL2591
*/
/**************************************************************************/
void configureSensor(void)
{
  // You can change the gain on the fly, to adapt to brighter/dimmer light situations
  //tsl.setGain(TSL2591_GAIN_LOW);    // 1x gain (bright light)
  //tsl.setGain(TSL2591_GAIN_MED);      // 25x gain
  //tsl.setGain(TSL2591_GAIN_HIGH);   // 428x gain
  tsl.setGain(TSL2591_GAIN_MAX);
  
  // Changing the integration time gives you a longer time over which to sense light
  // longer timelines are slower, but are good in very low light situtations!
  //tsl.setTiming(TSL2591_INTEGRATIONTIME_100MS);  // shortest integration time (bright light)
  //tsl.setTiming(TSL2591_INTEGRATIONTIME_200MS);
  // tsl.setTiming(TSL2591_INTEGRATIONTIME_300MS);
  // tsl.setTiming(TSL2591_INTEGRATIONTIME_400MS);
  //tsl.setTiming(TSL2591_INTEGRATIONTIME_500MS);
  tsl.setTiming(TSL2591_INTEGRATIONTIME_600MS);  // longest integration time (dim light)

  /* Display the gain and integration time for reference sake */  
  Serial.println(F("------------------------------------"));
  Serial.print  (F("Gain:         "));
  tsl2591Gain_t gain = tsl.getGain();
  switch(gain)
  {
    case TSL2591_GAIN_LOW:
      Serial.println(F("1x (Low)"));
      break;
    case TSL2591_GAIN_MED:
      Serial.println(F("25x (Medium)"));
      break;
    case TSL2591_GAIN_HIGH:
      Serial.println(F("428x (High)"));
      break;
    case TSL2591_GAIN_MAX:
      Serial.println(F("9876x (Max)"));
      break;
  }
  Serial.print  (F("Timing:       "));
  Serial.print((tsl.getTiming() + 1) * 100, DEC); 
  Serial.println(F(" ms"));
  Serial.println(F("------------------------------------"));
  Serial.println(F(""));
}


/**************************************************************************/
/*
    Program entry point for the Arduino sketch
*/
/**************************************************************************/
void setup(void) 
{
  Serial.begin(9600);
  
  Serial.println(F("Starting Adafruit TSL2591 Test!"));

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
  
  if (tsl.begin()) 
  {
    Serial.println(F("Found a TSL2591 sensor"));
  } 
  else 
  {
    Serial.println(F("No sensor found ... check your wiring?"));
    while (1);
  }
    
  /* Display some basic information on this sensor */
  displaySensorDetails();
  
  /* Configure the sensor */
  configureSensor();

  // Now we're ready to get readings ... move on to loop()!

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
    Shows how to perform a basic read on visible, full spectrum or
    infrared light (returns raw 16-bit ADC values)
*/
/**************************************************************************/
void simpleRead(void)
{
  // Simple data read example. Just read the infrared, fullspecrtrum diode 
  // or 'visible' (difference between the two) channels.
  // This can take 100-600 milliseconds! Uncomment whichever of the following you want to read
  uint16_t x = tsl.getLuminosity(TSL2591_VISIBLE);
  //uint16_t x = tsl.getLuminosity(TSL2591_FULLSPECTRUM);
  //uint16_t x = tsl.getLuminosity(TSL2591_INFRARED);

  Serial.print(F("[ ")); Serial.print(millis()); Serial.print(F(" ms ] "));
  Serial.print(F("Luminosity: "));
  Serial.println(x, DEC);
}

/**************************************************************************/
/*
    Show how to read IR and Full Spectrum at once and convert to lux
*/
/**************************************************************************/
void advancedRead(void)
{
  // More advanced data read example. Read 32 bits with top 16 bits IR, bottom 16 bits full spectrum
  // That way you can do whatever math and comparisons you want!

  DateTime now = rtc.now();

  uint32_t lum = tsl.getFullLuminosity();
  uint16_t ir, full;
  ir = lum >> 16;
  full = lum & 0xFFFF;
  Serial.print(F("[ ")); Serial.print(millis()); Serial.print(F(" ms ] "));
  Serial.print(F("IR: ")); Serial.print(ir);  Serial.print(F("  "));
  Serial.print(F("Full: ")); Serial.print(full); Serial.print(F("  "));
  Serial.print(F("Visible: ")); Serial.print(full - ir); Serial.print(F("  "));
  Serial.print(F("Lux: ")); Serial.println(tsl.calculateLux(full, ir), 6);

     // The below code will copy the readings above into a string to paste into the file created by the datalog shield.
  
  File dataFile = SD.open("testing.csv", FILE_WRITE);
  if (dataFile) { //Once the file is open, it will print the string generated in the current loop before closing until the next loop
    dataFile.print(now.month(), DEC); dataFile.print("/"); dataFile.print(now.day(), DEC); dataFile.print(","); 
    dataFile.print(now.hour(), DEC); dataFile.print(":"); dataFile.print(now.minute(), DEC); dataFile.print(":"); dataFile.print(now.second(), DEC); dataFile.print(","); dataFile.print(ir, 5); 
    dataFile.print(","); dataFile.print(full, 5); dataFile.print(","); dataFile.print(full-ir, 5); dataFile.print(","); dataFile.print(tsl.calculateLux(full, ir), 5); dataFile.println("");
    dataFile.close();
  }
  else {
    Serial.println("error opening file"); //This line only activates if the file was never opened.
  }
}

/**************************************************************************/
/*
    Performs a read using the Adafruit Unified Sensor API.
*/
/**************************************************************************/
void unifiedSensorAPIRead(void)
{
  /* Get a new sensor event */ 
  sensors_event_t event;
  tsl.getEvent(&event);
 
  /* Display the results (light is measured in lux) */
  Serial.print(F("[ ")); Serial.print(event.timestamp); Serial.print(F(" ms ] "));
  if ((event.light == 0) |
      (event.light > 4294966000.0) | 
      (event.light <-4294966000.0))
  {
    /* If event.light = 0 lux the sensor is probably saturated */
    /* and no reliable data could be generated! */
    /* if event.light is +/- 4294967040 there was a float over/underflow */
    Serial.println(F("Invalid data (adjust gain or timing)"));
  }
  else
  {
    Serial.print(event.light); Serial.println(F(" lux"));
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
  //simpleRead(); 
  advancedRead();
  // unifiedSensorAPIRead();
  
  delay(400);
}
