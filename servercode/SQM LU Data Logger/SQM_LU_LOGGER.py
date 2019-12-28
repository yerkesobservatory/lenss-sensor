#!/usr/bin/python

# Import required libraries/modules
from datetime import datetime
from datetime import date
from datetime import time
import platform
import serial
import serial.tools.list_ports
import time
import os

now = datetime.now()
log = open('./log_' + now.strftime('%Y-%m-%d') + '.txt', 'a')

# Automatically selects port syntax based on OS
# IMPORTANT!!! - Assumes no other devices plugged in with 'USB Serial'
# string and assumes similar model number.
def port():
    if str(platform.system()) == 'Windows':
        for p in ports:
            if 'USB Serial' in p.description:
                q = str(p)
                return(q[:4])
    else:
        return  '/dev/tty.usbserial-A5055IX5A' # /dev/ttyS(Port Number) for WSL

# Main read function. Sends a string to the defined port and
# prints the resulting output to a file "log.txt" and the terminal.
def serialread():
    ser = serial.Serial(
        port=port(),\
        baudrate=115200,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
            timeout=1)
    print("connected to: " + ser.portstr)
    log.write("connected to: " + str(ser.portstr) + "\n")
    ser.write(str.encode("rx\n"))
    ser.flush()
    print(ser.readline())
    log.write(str(ser.readline()) + "\n")
    ser.close()

# Runs serialread() function every second.
while True:
    serialread()
    time.sleep(1)
