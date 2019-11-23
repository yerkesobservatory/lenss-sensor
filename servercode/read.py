#!/usr/bin/python

import serial
import time
import os

def serialread():
    ser = serial.Serial(
        port=interface(NIX),\ # change between NIX and DOS
        baudrate=115200,\
        parity=serial.PARITY_NONE,\
        stopbits=serial.STOPBITS_ONE,\
        bytesize=serial.EIGHTBITS,\
            timeout=1)

    print("connected to: " + ser.portstr)

    ser.write(str.encode("rx\n"))
    ser.flush()

    print(ser.readline())

    ser.close()

while True:
    serialread()
    time.sleep(1)
