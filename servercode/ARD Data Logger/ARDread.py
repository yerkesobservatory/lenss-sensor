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
    now=datetime.now()
    """tim=time.localtime()
    for element in tim:
            element = str(element)
            if len(element) < 2:
                element = "0" + element"""
    #timestring=str(tim[3])+":"+str(tim[4])+":"+str(tim[5])+", "
    timestring=now.strftime("%H:%M:%S,")
    # Read value from Arduino
    read_ser=ser.readline()
    #print(repr(read_ser))
    read_fmtd = read_ser.decode("utf-8")
    read_timed = timestring+read_fmtd
    print(read_timed)
    # Make filename
    fname = now.strftime(config['arddatalogger']['outfilename'])
    # Save to file
    log = open(fname, 'at')
    log.write(read_timed)
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
        baudrate=115200,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
            timeout=5)
        
while True:

    serialread(config)
    time.sleep(1)
