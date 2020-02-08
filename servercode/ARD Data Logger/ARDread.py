"""
LENSS ARDUINO Read Program
==========================

This program reads data from the Arduino that
is connected to the TSL237 sensor.

"""

### Imports / Setup
import serial
import RPi.GPIO as GPIO
import time
from datetime import datetime
import serial.tools.list_ports
import configparser
import  os
import sys

### Function Definitions
def getardport(config):
    """ Returns the port string for the arduino
    """
    try:
        return config['arddatalogger']['arduinoport']
    except:
        exit(1)
        
def serialread(config):
    """ Read the serial value from the arduino and writes
        it to the file.
    """
    # Read value from Arduino
    read_ser=now.strftime('%H:%M:%S')+","+ser.readline()
    read_fmtd = read_ser.decode("utf-8")
    print(read_fmtd)
    # Make filename
    now = datetime.now()
    fname = now.strftime(config['arddatalogger']['outfilename'])
    # Save to file
    log = open(fname, 'at')
    log.write(read_fmtd)
    log.close()

### Main program

if len(sys.argv) < 2:
    print('WARNING: Must give filepathname to valid config file')
    print('Usage:\n  python SQM_LU_LOGGER.py ../config/serverconfig.ini')
    print('  replace with your own config file as appropriate')
    exit(1)

Config_FilePathName = sys.argv[1]
config = configparser.ConfigParser()
config.read(Config_FilePathName)


now = datetime.now()
print(config['arddatalogger']['arduinoport'])


ser  =  serial . Serial (
        port=getardport(config),\
        baudrate=9600,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
            timeout=5)
        
while True:

    serialread(config)
    time.sleep(1)
