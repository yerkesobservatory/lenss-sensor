# LENSS-Sensor
This project contains code and documentation for the LENSS-Sensor being developed at [GLAS](https://www.glaseducation.org). Details on the projects are on the "Project Page" at [Yerkesprojects/Programs/Lenss](https://sites.google.com/a/starsatyerkes.net/yerkesprojects/programs/lenss). If you have any qestions about this page, ask Alex, Joe, Adam or Marc.

## System Architecture

## Files
  * config: text files used to store data specific to individual sensors such as ports or filenames that will be used in other programs
     * serverconfig.ini: the standard serverconfig file holds port and filename data for both the arduino and SQM-LU, has a dummy line of data used when experimenting with how the pi's programs affect data, and directs to a log monitoring the status of connected devices
    * There are additional serverconfigs for certain sensors or people such as serverconfigMGB.ini (Marc's serverconfig file)
  * arduino: code used for the operation of sensors via arduino:
    * TSL237_Uno.ino: the current program used for the arduino in Sensor0001; when dark enough, it interrupts all current processes to update a count when light hits the tsl and prints luminosity alongside temperature data
    * TSL237_32u4: the most recent version of the program; performs identical functions to the Uno but is redesigned for the hardware constraints of a feather 32u4
  * raspi: programs used for manipulating and storing data received by the sensor
    * ARD Data Logger: programs related to reading data from the arduino
      * ARDread.py: used to store data collected from the Arduino reads the serial port connected to arduino, samples data over the course of a minute, removes outliers and takes the mean to produce average data for the minute, and  stores the finalized data in a file
    * DataUploadScripts: uploads data files to the LENSS Google Drive
    * Reconfiguration: bash programs that alter config files and pathways on a pi
      * config.sh: bash script that generates local data folder as well as tailoring config pathways to the specific sensor's id number
      * setport.sh: program that isolates the port the sensor is connected to and writes it to config
    * SQM Data Logger: programs used for manipulating and storing data received by an SQM-LU
      * SQM_LU_LOGGER.py: reads and stores data from the SQM-LU in a similar fashion to ARDread.py
    * Systemd Services
      * set-ard-port.service: Runs setport.sh on system startup
      * lenss-collect.service: Starts ARDread.py on system startup after set-ard-port.service
  * server: programs operated on the central LENSShost server
    * watchdog: programs used for the monitoring of sensor operations
      * watchdog.py: accesses LENSS Google Drive folder to record which sensors uploaded the previous night; this record is the emailed to developers on the program's mailing list
  * zArchive: miscellaneous outdated codes; the z keeps it at the back of alphabetical lists
  * .gitignore: list of files such as tokens and api keys that git will not track


## Programs
List of the different programs and what they do.

