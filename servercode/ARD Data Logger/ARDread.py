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
import logging
from logging.handlers import TimedRotatingFileHandler
import numpy as np

### Function Definitions
def getardport(config):
    """ Returns the port string for the arduino
    """
    try:
        return config['arddatalogger']['arduinoport']
    except:
        exit(1)
        
### Main program

if len(sys.argv) < 2:
    print('WARNING: Must give filepathname to valid config file')
    print('Usage:\n  python SQM_LU_LOGGER.py ../config/serverconfig.ini')
    print('  replace with your own config file as appropriate')
    exit(1)

Config_FilePathName = sys.argv[1]
config = configparser.ConfigParser()
config.read(Config_FilePathName)

now=datetime.now()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
hand = TimedRotatingFileHandler(now.strftime(config['logging']['ardlogfile']), when="midnight")
hand.suffix = "%Y-%m-%d.log"
logformat = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
hand.setFormatter(logging.Formatter(logformat))
logger.addHandler(hand)

print(config['arddatalogger']['arduinoport'])

ser  =  serial . Serial (
        port=getardport(config),\
        baudrate=115200,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
            timeout=5)
        
def serialread(config):
    time.sleep(1)
    """ Read the serial value from the arduino and writes
        it to the file.
    """
    lvolt = []
    hz = []
    tvolt = []
    tFahr = []
    tCels = []
    while True:
        time.sleep(1)
        now=datetime.now()
        #timestring=str(tim[3])+":"+str(tim[4])+":"+str(tim[5])+", "
        timestring=now.strftime("%H:%M:%S,")
        # Read value from Arduino
        read_ser=ser.readline()
        #print(repr(read_ser))
        read_fmtd = read_ser.decode("utf-8")

        sdata = read_fmtd.split(",")
        sdata[4].strip()
        
        sl = ([] for i in range(len(sdata)))
        for i in sdata:
            sl[i].append(float(sdata[i]))

        if (time.gmtime().tm_sec == 0):
            for l in sl:
                sl[l]=np.median(sl[l])
            break

    read_timed = []
    read_timed.append(timestring)
    read_timed += sl
    print(read_timed)
    # Make filename
    fname = now.strftime(config['arddatalogger']['outfilename'])
    # Save to file
    log = open(fname, 'at')
    log.write(read_timed)
    log.close()
    logger.info('Connected to:' + str(getardport(config)))
    logger.info('Read data line')

while True:

    serialread(config)
    #time.sleep(1)
