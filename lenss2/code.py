import time, board, busio, sdcardio, storage, ds1307, adafruit_tsl2591, alarm, supervisor
import adafruit_ltr329_ltr303 as adafruit_ltr329
import digitalio

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

#try:
#SD Stuff

spi = busio.SPI(board.GP10, MOSI=board.GP11, MISO=board.GP12)
cs = board.GP9
sdcard = sdcardio.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

#RTC Stuff

i2cRTC = busio.I2C(board.GP17, board.GP16) # uses board.SCL and board.SDA
rtc = ds1307.DS1307(i2cRTC)
time.sleep(0.1)
t = rtc.datetime

#TSL Stuff

i2c = busio.I2C(board.GP15, board.GP14) #Set GP pins to the pins used on the pico
time.sleep(0.1) #TSL needs a second to boot
sensor = adafruit_tsl2591.TSL2591(i2c)
sensor.gain = adafruit_tsl2591.GAIN_LOW

time.sleep(1)
low_gain = sensor.lux
if low_gain >= 60:
    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 1797.8)
    #time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 2)
    #print("Too bright!")
    #print("Low Gain: " + str(low_gain))
if low_gain < 60:
    sensor.gain = adafruit_tsl2591.GAIN_MED
    time.sleep(1)
    medium_gain = sensor.lux
    #print("Medium Gain: " + str(medium_gain))
    if medium_gain < 20:
        sensor.gain = adafruit_tsl2591.GAIN_HIGH
        time.sleep(1)
        #print("Dark enough to operate")
        high_gain = sensor.lux
        #print("High Gain: " + str(high_gain))
        time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 595.8)
        #time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 2)
    if medium_gain >= 50:
        time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 896.8)
        #time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 2)
        #print("Still a little too bright")
        
time.sleep(1)
#try:            
#t = rtc.datetime
format_days = "{}-{}-{}".format(t.tm_year, t.tm_mon, t.tm_mday)
#print(format_days)
format_minutes = "{}:{:02}:{:02}".format(t.tm_hour, t.tm_min, t.tm_sec)
#print(format_minutes)
lux = sensor.lux
#print("Total light: {0}lux".format(lux))
# You can also read the raw infrared and visible light levels.
# These are unsigned, the higher the number the more light of that type.
# There are no units like lux.
# Infrared levels range from 0-65535 (16-bit)
infrared = sensor.infrared
#print("Infrared light: {0}".format(infrared))
# Visible-only levels range from 0-2147483647 (32-bit)
visible = sensor.visible
#print("Visible light: {0}".format(visible))
# Full spectrum (visible + IR) also range from 0-2147483647 (32-bit)
full_spectrum = sensor.full_spectrum
#print("Full spectrum (IR + visible) light: {0}".format(full_spectrum))
#format_days = t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min


time.sleep(0.1)

#Reading twice to possibly stop the sensor from reading 0

lux = sensor.lux
infrared = sensor.infrared
visible = sensor.visible
full_spectrum = sensor.full_spectrum


#print(lux, infrared, visible)

with open("/sd/testing_primary.txt", "a") as f:
    f.write(format_days + "; "  + format_minutes + "; " + "Total light: {0} lux".format(lux) + "; "  + "IR light: {0}".format(infrared) + "; " + "Visible light: {0}".format(visible) + "\n")
with open("/sd/testing_secondary.txt", "a") as f:
    f.write(format_days + "; "  + format_minutes + "; " + str(lux) + "; " + str(infrared) + "; " + str(visible) + "\n")

led.value = True
time.sleep(0.5)
led.value = False
time.sleep(0.2)
led.value = True
time.sleep(0.5)
led.value = False
time.sleep(0.2)
led.value = True
time.sleep(0.5)
led.value = False
time.sleep(0.2)
led.value = True
time.sleep(0.5)
led.value = False
time.sleep(0.2)
led.value = True
time.sleep(0.2)
led.value = False
time.sleep(0.2)
led.value = True
time.sleep(0.5)
led.value = False
time.sleep(0.2)





# except:
#     led.value = True
#     time.sleep(0.2)
#     led.value = False
#     time.sleep(0.2)
#     led.value = True
#     time.sleep(0.2)
#     led.value = False
#     time.sleep(0.2)
#     led.value = True
#     time.sleep(0.2)
#     led.value = False
#     time.sleep(0.2)
#     led.value = True
#     time.sleep(0.5)
#     led.value = False
#     time.sleep(0.2)
#     led.value = True
#     time.sleep(0.5)
#     led.value = False
#     time.sleep(0.2)
#     led.value = True
#     time.sleep(0.5)
#     led.value = False
#     time.sleep(0.2)
#     led.value = True
#     time.sleep(0.2)
#     led.value = False
#     time.sleep(0.2)
#     led.value = True
#     time.sleep(0.2)
#     led.value = False
#     time.sleep(0.2)
#     led.value = True
#     time.sleep(0.2)
#     led.value = False
#     time.sleep(1)
#     supervisor.reload()
# 
# if 
# 
# 
#time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 600)
#
alarm.exit_and_deep_sleep_until_alarms(time_alarm)

# except Exception as e:
#     spi = busio.SPI(board.GP10, MOSI=board.GP11, MISO=board.GP12)
#     cs = board.GP9
#     sdcard = sdcardio.SDCard(spi, cs)
#     vfs = storage.VfsFat(sdcard)
#     storage.mount(vfs, "/sd")
#     with open("/sd/error.txt", "a") as f:
#         f.write(str(e) + "\n")

