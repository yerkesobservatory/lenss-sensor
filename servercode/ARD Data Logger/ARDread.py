"""
LENSS ARDUINO Read Program
==========================

This program reads data from the Arduino that
is connected to the TSL237 sensor.

"""

### Imports / Setup
import serial
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

# Setup configuration
Config_FilePathName = sys.argv[1]
config = configparser.ConfigParser()
config.read(Config_FilePathName)

# Setup logging
now=datetime.now()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
hand = TimedRotatingFileHandler(now.strftime(config['logging']['ardlogfile']), when="midnight")
hand.suffix = "%Y-%m-%d.log"
logformat = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
hand.setFormatter(logging.Formatter(logformat))
logger.addHandler(hand)
print(config['arddatalogger']['arduinoport'])

# Open serial connection
if int(config['arddatalogger']['simarduino']):
    # We are simulating the arduino set serial to null
    ser = None
else:
    ser  =  serial . Serial ( port=getardport(config),\
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
    """lvolt = []
    hz = []
    tvolt = []
    tFahr = []
    tCels = []
    while True:
        time.sleep(1)
        now=datetime.now()"""
       #timestring=str(tim[3])+":"+str(tim[4])+":"+str(tim[5])+", "
    timestring=now.strftime("%H:%M:%S,")
    # Read value from Arduino
    if ser:
        read_ser=ser.readline()
        #print(repr(read_ser))
        read_fmtd = read_ser.decode("utf-8")
    else:
        read_fmtd = config['arddatalogger']['simardline']

    """ sdata = read_fmtd.split(",")
        sdata[4].strip("\r\n")
        
        lvolt += sdata[0]
        hz += sdata[1]
        tvolt += sdata[2]
        tFahr += sdata[3]
        tCels += sdata[4]

        if (time.gmtime().tm_sec == 0):
            read_timed = timestring+","
            read_timed += str(statistics.median(lvolt))+","
            read_timed += str(statistics.median(hz))+","
            read_timed += str(statistics.median(tvolt))+","
            read_timed += str(stastics.median(tFahr))+","
            read_timed += str(statistics.median(tCels))
            break"""

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
    #time.sleep(1)
