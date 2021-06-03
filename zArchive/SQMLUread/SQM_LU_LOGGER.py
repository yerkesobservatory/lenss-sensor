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
import  platform
import  serial
import serial.tools.list_ports
import configparser
import  time
import  os
import sys

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
log = open('./Feb_6_2020.txt', 'a')
#log=open(now.strftime(config['sqmdatalogger']['outfilename']),'at')

# Automatically selects port syntax based on OS
# IMPORTANT!!! - Assumes no other devices plugged in with 'USB Serial'
# string and assumes similar model number.

def port(config):
    try:
        return config['sqmludatalogger']['sqmport']
    except:
        exit(1)
    if str(platform.system()) == 'Windows':
        for  p  in  ports :
            if 'USB Serial' in p.description:
                q = str(p)
                return(q[:4])
    else:
        return  '/dev/tty.usbserial-A5055IX5A' # /dev/ttyS(Port Number) for WSL

# Main read function. Sends a string to the defined port and
# prints the resulting output to a file "log.txt" and the terminal.
def serialread(config):
    ser  =  serial . Serial (
        port=port(config),\
        baudrate=115200,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
            timeout=5)
    print("connected to: " + ser.portstr)
    log.write("connected to: " + str(ser.portstr) + "\n")
    ser.write(str.encode("rx\n"))
    ser.flush()
    print(str(ser.readline()))
    log.write(str(ser.readline()) + "\n")
    ser.close()

# Runs serialread() function every second.
while True:
    serialread(config)
    time.sleep(1)
