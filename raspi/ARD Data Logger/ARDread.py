#!/usr/bin/python3
""" LENSS ARDUINO Read Program ==========================

This program reads data from the Arduino that
is connected to the TSL237 sensor.

"""

### Imports / Setup
import serial
import time
from datetime import datetime
import serial.tools.list_ports
import configparser
import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
import numpy as np
import pytz

# fmt represents the number of decimal places each data point shows
fmt = ["%.2f", "%.2f", "%.1f"]

# total number of deleted data points
dltd = 0
# benchmark amount to detect if large numbers of data points were deleted
ldltd = 0
# time when program was launched to give dltd a reference
starttime = datetime.now().strftime("%H:%M:%S, %Y-%m-%d")


### Function Definitions
def getardport(config):
    # Returns the port string for the arduino
    try:
        return config["arddatalogger"]["arduinoport"]
    except:
        exit(1)


### Main program

# Checks if there are enough arguments in the command to setup config in next section
if len(sys.argv) < 2:
    print("WARNING: Must give filepathname to valid config file")
    print("Usage:\n  python SQM_LU_LOGGER.py ../config/serverconfig.ini")
    print("  replace with your own config file as appropriate")
    exit(1)

# Setup configuration
Config_FilePathName = sys.argv[1]
config = configparser.ConfigParser()
config.read(Config_FilePathName)

# Setup background logging (time of operation and deleted data points)
now = datetime.now()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
hand = TimedRotatingFileHandler(
    now.strftime(config["logging"]["ardlogfile"]), when="midnight"
)
hand.suffix = "%Y-%m-%d.log"
logformat = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
hand.setFormatter(logging.Formatter(logformat))
logger.addHandler(hand)
print(config["arddatalogger"]["arduinoport"])

# Open serial connection
if int(config["arddatalogger"]["simarduino"]):
    # We are simulating the arduino set serial to null
    ser = None
else:
    ser = serial.Serial(
        port=getardport(config),
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=5,
    )
    ser.readline()


def serialread(config):
    try:
        """Read the serial value from the arduino and writes
        it to the file.
        """
        time.sleep(1)

        global dltd
        global ldltd
        global starttime

        sl = [[] for i in range(3)]
        last = time.gmtime().tm_sec

        while True:
            time.sleep(2)
            timestamp = time.time()

            # When entering a new minute (marked by the seconds decreasing after a loop from 58 to 01 or 59 to 02 or so on)
            # the data gathered is sorted from least to greatest, the top and bottom fifths of it are removed to get rid of
            # outliers, and the rest is averaged to produce a data string for the minute.
            if last > time.gmtime().tm_sec:
                for l in range(len(sl)):
                    sl[l].sort()
                    sl[l] = sl[l][len(sl[l]) // 5 : -(len(sl[l]) // 5)]
                    sl[l] = fmt[l] % np.mean(sl[l])
                break
            # Read most recent value from Arduino
            if ser:
                read_ser = ""
                while ser.in_waiting:
                    read_ser = ser.readline()
                read_fmtd = read_ser.decode("utf-8")
            else:
                read_fmtd = config["arddatalogger"]["simardline"]

            # Read data from string and tracks the number of deleted data points
            sdata = read_fmtd.split(";")
            del sdata[-1]
            try:
                for i in range(len(sdata)):
                    sl[i].append(float(sdata[i]))
            except:
                dltd += 1
            print(sdata)
            print(time.gmtime().tm_sec)
            last = time.gmtime().tm_sec

        # Compile text for file
        read_timed = []
        read_timed.append(
            datetime.utcfromtimestamp(timestamp).isoformat(
                sep="T", timespec="milliseconds"
            )
        )
        read_timed.append(
            datetime.fromtimestamp(
                timestamp, pytz.timezone("US/Central")
            ).isoformat(sep="T", timespec="milliseconds")[:-6]
        )
        read_timed += sl
        read_timed.append(config["arddatalogger"]["ID"])
        text_timed = ";".join(read_timed)
        print(text_timed)
        print(str(dltd) + " pieces of data deleted")
        # Make filename
        fname = datetime.fromtimestamp(
            timestamp, pytz.timezone("US/Central")
        ).strftime(config["arddatalogger"]["outfilename"])
        # Save to file
        data = open(fname, "at")
        data.write(text_timed + "\r\n")
        if dltd - ldltd >= 100:
            logger.info(
                str(dltd) + " lines deleted since " + starttime + "\r\n"
            )
            ldltd = dltd
        data.close()
        logger.info("Connected to:" + str(getardport(config)))
        logger.info("Read data line")
    except:
        time.sleep(1)


while True:
    serialread(config)
    # time.sleep(1)
