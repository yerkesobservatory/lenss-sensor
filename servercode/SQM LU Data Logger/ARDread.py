import serial
import RPi.GPIO as GPIO
import time

# ser=serial.Serial("/dev/ttyACM0", 115200)
ser=serial.Serial("/dev/ttyACM1", 115200)
# ttyAMA0
ser.baudrate=115200

GPIO.setmode(GPIO.BOARD)

while True:

    read_ser=ser.readline()
    print(read_ser.decode("utf-8"))
    #print(read_ser)

#Also read other SQM
#Send to a file
#Use command line argument optionally for port & filename
#(Arduino) shut off sensor when light too intense using digital pin for power
#(Arduino) use less precise photocell to determine when to power tsl