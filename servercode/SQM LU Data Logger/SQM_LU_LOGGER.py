"""
LENSS SQM Readout Program
=========================

This program reads data from the Sky Quality Meter (SQM) USB and
save the data to disk.

"""

#!/usr/bin/python

# Import required libraries/modules
from datetime import datetime
from datetime import date
from datetime import time
import platform
import serial
import serial.tools.list_ports
import configparser
import time
import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler

# Get config file name from argument
if len(sys.argv) < 2:
    print('WARNING: Must give filepathname to valid config file')
    print('Usage:\n  python SQM_LU_LOGGER.py ../config/serverconfig.ini')
    print('  replace with your own config file as appropriate')
    exit(1)

Config_FilePathName = sys.argv[1]
config = configparser.ConfigParser()
config.read(Config_FilePathName)

now = datetime.now()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
hand = TimedRotatingFileHandler(now.strftime(config['logging']['sqmlogfile']),when="midnight")
hand.suffix = "%Y-%m-%d.log"
logformat = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
hand.setFormatter(logging.Formatter(logformat))
logger.addHandler(hand)
#log = open('./sqmlu_' + now.strftime('%Y-%m-%d') + '.txt', 'a')

# Automatically selects port syntax based on OS
# IMPORTANT!!! - Assumes no other devices plugged in with 'USB Serial'
# string and assumes similar model number.
def port(config):
    try:
        return config['sqmludatalogger']['sqmport']
    except:
        pass
    if str(platform.system()) == 'Windows':
        for p in ports:
            if 'USB Serial' in p.description:
                q = str(p)
                return(q[:4])
    else:
        return  '/dev/tty.usbserial-A5055IX5A' # /dev/ttyS(Port Number) for WSL

# Main read function. Sends a string to the defined port and
# prints the resulting output to a file "log.txt" and the terminal.
def serialread(config):
    now = datetime.now()
    filename = now.strftime(config['sqmludatalogger']['outfilename'])
    timestring = now.strftime("%H:%M:%S,")
    ser = serial.Serial(
        port=port(config),\
        baudrate=115200,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
            timeout=1)
    print("connected to: " + ser.portstr)
    logger.info('Connected to:' + str(ser.portstr))
    ser.write(str.encode("rx\n"))
    ser.flush()
    serline = ser.readline()
    serline_utf = serline.decode("utf-8")
    dataline=timestring+serline_utf+"\n"
    print(dataline)
    # log.write(str(ser.readline()) + "\n")
    logfile = open(filename, 'at')
    logfile.write(timestring+serline_utf+"\n")
    logger.info('Read data line')
    logfile.close()

# Runs serialread() function every second.
while True:
    serialread(config)
    time.sleep(60)
