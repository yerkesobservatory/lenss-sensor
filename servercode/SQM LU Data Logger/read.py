#!/usr/bin/python

# Import required libraries/modules
import platform
import serial
import time
import os

# Automatically selects port syntax based on OS
# IMPORTANT!!! - Missing ability to change ports depending on machine
# and sensor!
def port():
    if str(platform.system()) == 'Windows':
        return 'COM4'
    else:
        return '/dev/tty.usbserial-A5055IX5A'

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
    log = open('./log.txt', 'a')
    print("connected to: " + ser.portstr)
    log.write("connected to: " + str(ser.portstr) + "\n")
    ser.write(str.encode("rx\n"))
    ser.flush()
    print(ser.readline())
    log.write(str(ser.readline()) + "\n")
    ser.close()
    log.close()

# Runs serialread() function every second.
while True:
    serialread()
    time.sleep(1)