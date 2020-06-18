import configparser
import time
import serial
import sys

Config_FilePathName = sys.argv[1]
config = configparser.ConfigParser()
config.read(Config_FilePathName)

Port = config['arddatalogger']['arduinoport']
print(Port)

ser = serial.Serial(
    port = Port,
    baudrate = 9600,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS,
    timeout=5)

print(ser)
while True:
    time.sleep(1)
    read = ser.readline()
    print(read)
