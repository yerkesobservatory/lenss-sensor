import serial
import RPi.GPIO as GPIO
import time

ser=serial.Serial("/dev/ttyACM0", 115200)
#ser=serial.Serial("/dev/ttyACM1", 115200)
# ttyAMA0
ser.baudrate=115200

GPIO.setmode(GPIO.BOARD)

while True:

    read_ser=ser.readline()
    read_fmtd = read_ser.decode("utf-8")
    print(read_fmtd)
    with open("TestDoc1.txt", "a") as text_file:
        print(read_fmtd, file=text_file)

#Send to a file
#Use command line argument optionally for port & filename