from datetime import datetime
import RPi.GPIO as GPIO
import configparser
import serial.tools.list_ports
import sys
import time

GPIO.setmode(GPIO.BOARD)

if len(sys.argv) < 2:
    print("WARNING: Must give filepathname to valid config file")
    print("Usage:\n  python SQM_LU_LOGGER.py ../config/serverconfig.ini")
    print("  replace with your own config file as appropriate")
    exit(1)

Config_FilePathName = sys.argv[1]
config = configparser.ConfigParser()
config.read(Config_FilePathName)

now = datetime.now()
print(config["arddatalogger"]["arduinoport"])


def port(config):
    try:
        return config["arddatalogger"]["arduinoport"]
    except:
        exit(1)


ser = serial.Serial(
    port=port(config),
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=5,
)


def serialread(config):
    read_ser = ser.readline()
    read_fmtd = read_ser.decode("utf-8")
    print(read_fmtd)
    log = open("Feb_6_2020.txt", "a")
    log.write(read_fmtd)
    log.close()


while True:
    serialread(config)
    time.sleep(1)
