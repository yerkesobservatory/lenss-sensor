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
hand = TimedRotatingFileHandler(now.strftime(config['logging']['logfile']), when="midnight")
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
    """ Read the serial value from the arduino and writes
        it to the file.
    """
    lvolt = []
    hz = []
    tvolt = []
    tFahr = []
    tCels = []
    while True:
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

        sdata = read_fmtd.split(",")
        lvolt += sdata[1]
        hz += sdata[2]
        tvolt += sdata[3]
        tFahr += sdata[4]
        tCels += sdata[5]

        if (now.strftime("%S") == "59"):
            read_timed = timestring+str(statistics.median(lvolt))+str(statistics.median(hz))+str(statistics.median(tvolt))+str(stastics.median(tFahr))+str(statistics.median(tCels))

    read_timed = timestring+read_fmtd
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
    time.sleep(1)
