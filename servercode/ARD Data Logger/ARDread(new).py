import serial
#import RPi.GPIO as GPIO
import time
import configparser
import sys

from datetime import datetime
from datetime import date
from datetime import time
import serial.tools.list_ports
import os

# Get config file name from argument
if len(sys.argv) < 2:
    print('WARNING: Must give filepathname to valid config file')
    print('Usage:\n  python SQM_LU_LOGGER.py ../config/serverconfig.ini')
    print('  replace with your own config file as appropriate')
    exit(1)

Config_FilePathName = sys.argv[1]
config = configparser.ConfigParser()
config.read(Config_FilePathName)

# Get time
now = datetime.now()

# File name argument (log=open(now.strftime(config['sqmdatalogger']['outfilename']),'at')
log = open('./log_' + now.strftime('%Y-%m-%d') + '.txt', 'a')

def port(config):
    try:
        return config['arddatalogger']['arduinoport']
    except:
        exit(1)

#ser=serial.Serial("/dev/ttyACM0", 115200)
#ser=serial.Serial("/dev/ttyACM1", 115200)
# ttyAMA0
def serialread(config):
    ser = serial.Serial(
        port=port(config),\
        baudrate=115200,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
            timeout=1)
    read_ser=ser.readline()
    read_fmtd = read_ser.decode("utf-8")
    read_fmtd = now.strftime('%H:%M:%S')+","+read_fmtd
    print(read_fmtd)
    with log as text_file:
        print(read_fmtd, file=text_file)

#ser.baudrate=115200

#GPIO.setmode(GPIO.BOARD)

while True:
    serialread(config)
    time.sleep(1)

    #read_ser=ser.readline()
    #read_fmtd = read_ser.decode("utf-8")
    #print(read_fmtd)
    #with open("TestDoc1.txt", "a") as text_file:
        #print(read_fmtd, file=text_file)

#Send to a file
#Use command line argument optionally for port & filename
