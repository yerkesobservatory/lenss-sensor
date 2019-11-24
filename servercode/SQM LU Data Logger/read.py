#!/usr/bin/python3

# Import required libraries/modules
import serial
import time
import os

# Main read function. Sends a string to the defined port and
# prints the resulting output to a file "log.txt" and the terminal.
def serialread():
    ser = serial.Serial(
        port='/dev/tty',\
        baudrate=115200,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
            timeout=1)

    log = open("log.txt", "a")

    print("connected to: " + ser.portstr, file=log)

    ser.write(str.encode("rx\n"))
    ser.flush()

    print(ser.readline(), file=log)

    ser.close()

    log.close()

# Runs serialread() function every second.
while True:
    serialread()
    time.sleep(1)
