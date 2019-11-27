#!/usr/bin/python3
import serial
ser = serial.Serial('/dev/ttyACM0', 9600)
# read from Arduino
input = ser.read()
print ("Read input " + input.decode("utf-8") + " from Arduino")
# write something back
ser.write(b'A')
# read response back from Arduino
for i in range (0,3):
        input = ser.read()
        input_number = ord(input)
        print ("Read input back: " + str(input_number))








#While loop implementation
#!/usr/bin/python3
import serial
import time
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=5)
# read from Arduino
input = ser.read()
print ("Read input " + input.decode("utf-8") + " from Arduino")

while 1:
        # write something back
        ser.write(b'A')
        # read response back from Arduino
        for i in range (0,3):
                input = ser.read()
                input_number = ord(input)
                print ("Read input back: " + str(input_number))
        time.sleep(1)