import serial
import RPi.GPIO as GPIO
import time
from datetime import datetime

name=input("Please enter the name of the file to store current data or enter /time to use the current date and time:    ")

if (name=="/time"):
    now=datetime.now()
    filename=now.strftime("%Y_%b_%d_%H:%M:%S")
else:
    filename=name
    
suffilename=filename+".txt"

portin=input("Please complete current port name to allow reading:    /dev/tty")
port="/dev/tty"+portin
ser=serial.Serial(port, 115200)
#ser=serial.Serial("/dev/ttyACM1", 115200)
ser.baudrate=115200

GPIO.setmode(GPIO.BOARD)

while True:

    read_ser=ser.readline()
    read_fmtd = read_ser.decode("utf-8")
    print(read_fmtd)
    with open(suffilename, "a") as text_file:  #a for append
        print(read_fmtd, file=text_file)

#Use command line argument optionally for port & filename