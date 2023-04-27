#-> setup a virtual environment and download packages via `pip install [package]`

#include library python-weather at https://github.com/null8626/python-weather
import python-weather
#might switch to a weather api?

#include astropy and astroplan (astropy interface)
import astropy
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation

import astroplan
from astroplan import Observer

Field = Enum('Field', ['TEMP', 'FREQ', 'VOLT'])

class minute_record:

    def __init__(self, utc: Time, local: Time, temp: float, freq: float, volt: float, id: str):
        self.utc_time = utc
        self.local_time = local
        self.temperature = temp
        self.frequency = freq
        self.voltag = volt
        self.sensor_id = id

class night_record:
    def __init__(self, night_date: Time, night_file: str, morning_date: Time, morning_file: str):
        #let night and morning data include time as noon of their respective days
        #time = Time('2015-06-16 12:00:00') 2023-01-23T06:00:00.992

        self.nightof = night_date
        self.morningof = morning_date

        sensor = Observer(longitude=-155.4761*u.deg, latitude=19.825*u.deg,
                  elevation=0*u.m, name="Sensor", timezone="US/Central") #TODO Update Location
        self.sunset = sensor.subaru.sun_set_time(night_date, which='next')
        self.sunrise = sensor.subaru.sun_rise_time(night_date, which='next')
        self.astronomical_twilight = sensor.twilight_evening_astronomical(night_date, which='next')

        #how much of the lunar surface is illuminated that night, pulled when the sky is fully dark (astro. twilight)
        #comparable to moon phase (0 = new moon, ~1 = full) without the pi of obs.moon_phase
        self.moon_illumination = sensor.moon_illumination(self.astronomical_twilight)
        self.weather = 0 #TODO Update Placeholder -- how to succinctly record nightly weather?

        # example line from 2023-01-23_LENSSTSL0008.txt:
        # 2023-01-23T06:00:00.992;2023-01-23T00:00:00.992;0.38;4.39;0.0;LENSS_TSL_0008
        # UTC Time; Local Time; Temperature (C); Frequency; Voltage; ID

        self.min_records = []

        n_file = open(night_file)
        transtr = n_file.readline()
        while (len(transtr) != 0):
            data = transtr.split(';')
            data[0] = data[0].replace("T", " ")
            data[0] = data[0][0:19]
            data[1] = data[1].replace("T", " ")
            data[1] = data[1][0:19]
            m_rec = minute_record(Time(data[0]), Time(data[1]), data[2].float(), data[3].float(), data[4].float, data[5])
            if m_rec.local_time < self.sunset: #unsure if this will work or if a special time comp function is needed
                continue
            self.min_records.append(m_rec)
            n_file.readline()
        n_file.close()

        m_file = open(morning_file)
        transtr = m_file.readline()
        while (len(transtr) != 0):
            data = transtr.split(';')
            data[0] = data[0].replace("T", " ")
            data[0] = data[0][0:19]
            data[1] = data[1].replace("T", " ")
            data[1] = data[1][0:19]
            m_rec = minute_record(Time(data[0]), Time(data[1]), data[2].float(), data[3].float(), data[4].float, data[5])
            if m_rec.local_time > self.sunrise: #unsure if this will work or if a special time comp function is needed
                break
            self.min_records.append(m_rec)
            n_file.readline()
        m_file.close()

        self.valid_for_use = True
        self.exclusion_reason = "None"

    def grade_data(self):
        #taking the average night to be ten hours (600 minutes), if more than three hours (180 minutes) are missing, 
        #invalidate the data based on insufficient records
        if (len(self.min_records) < 420):
            self.valid_for_use = False
            self.exclusion_reason = "Insufficient Records for Night"

        #if the moon would have been obscured by bad weather for more then three hours, invalidate based on weather conditions
        counter = 0
        #use something other than python-weather?

    def apply_correction(self, field_to_update, funct):
        match (field_to_update):
            #TODO Adjust for Switch Case/Enum Weirdness in Python
            case TEMP:
                for rec in self.min_records:
                    rec.temperature = funct(rec.temperature)
            case FREQ:
                for rec in self.min_records:
                    rec.frequency = funct(rec.frequency)
            case VOLT:
                for rec in self.min_records:
                    rec.voltage = funct(rec.voltage)
            case _:
                #error: field not recognized/field should not be updated
    
    #export
    #check if valid for use and if not, exclusion reason