#exit() will close python
#highlighting text and using middle mouse will copy/paste
#TAB after some letters to autocomplete
import sys
sys.path.append('/home/pi/Documents/LENSS/python-tsl2591-master')
from tsl2591.read_tsl import Tsl2591
tsl = Tsl2591()
tsl.set_gain(0x00)
tsl.set_timing(0x00)
full, ir = tsl.get_full_luminosity()
lux = tsl.calculate_lux(full, ir)
print (lux, full, ir)