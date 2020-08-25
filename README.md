# LENSS-Sensor
This project contains code and documentation for the LENSS-Sensor being developed at [GLAS](https://www.glaseducation.org). Details on the projects are on the "Project Page" at [Yerkesprojects/Programs/Lenss](https://sites.google.com/a/starsatyerkes.net/yerkesprojects/programs/lenss). If you have any qestions about this page, ask Alex, Joe, Adam or Marc.

## System Architecture

## Files
  * *config: text files used to store data specific to individual sensors such as ports or filenames that will be used in other programs
     * serverconfig.ini: the standard serverconfig file holds port and filename data for both the arduino and SQM-LU, has a dummy line of data used when experimenting with how the pi's programs affect data, and directs to a log monitoring the status of connected devices
    * serverconfig.ini.save: another variant of the serverconfig file; as of 8/25/2020 it is missing some features necessary for the programs on the pi
    * There are additional serverconfigs for certain sensors or people such as serverconfigMGB.ini (Marc's serverconfig file)
  * *sensorcode: code used for the operation of sensors via arduino:
    * SerialCallResponse.ino: tutorial used to demonstrate how the arduino sends data to other devices, which allows the arduino to push our sensor's data to the pi
    * TSL237_Datalogging.ino: tsl237 reader code intended to be used with an adafruit feather; the code will not work with the pins available on feather
    * TSL237_Uno_CSVfmtd.ino: old program used to experiment with CSV-friendly file formatting
    * *TSL237_Arduino_Uno_Compatible.ino: THE MOST UP-TO-Date PROGRAM used for the arduino when dark enough, it interrupts all current processes to update a count when light hits the tsl and prints luminosity alongside temperature data 
    * TSL2591_Datalogging.ino: code used to read the TSL2591 lux sensor; no longer in use since the switch to tsl237
  * *servercode: programs used for manipulating and storing data received by the sensor
    * *ARD Data Logger: programs related to reading data from the arduino
      * *ARDread.py: used to store data collected from the Arduino reads the serial port connected to arduino, samples data over the course of a minute, removes outliers and takes the mean to produce average data for the minute, and  stores the finalized data in a file
      * RawData.py: program used to read what is being sent through the arduino's serial port
      * *watchdog.py: email status report for arduino reads the arduino data file when activated by crontab and emails how many seconds ago the last update was made to anyone on a list
    * Datasorter: Alex please explain
    * SQM Data Logger: programs used for manipulating and storing data received by an SQM-LU
      * SQM_LU_LOGGER.py: reads and stores data from the SQM-LU in a similar fashion to ARDread.py

stuffs: miscellaneous outdated codes

* in use

## Programs
List of the different programs and what they do.

