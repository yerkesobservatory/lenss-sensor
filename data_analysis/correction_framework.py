# include library python-weather at https://github.com/null8626/python-weather
# might switch to a weather api?
import os

from astroplan import Observer
import astropy.units as u
from astropy.coordinates import EarthLocation
from astropy.time import Time


class minute_record:
    def __init__(
        self,
        utc: Time,
        local: Time,
        temp: float,
        freq: float,
        volt: float,
        id: str,
    ):
        self.utc_time = utc
        self.local_time = local
        self.temperature = temp
        self.frequency = freq
        self.voltag = volt
        self.sensor_id = id


class night_record:
    # create an uninitialized night record
    def __init__(self):
        self.nightof = 0
        self.morningof = 0
        self.sunset = 0
        self.sunrise = 0
        self.astronomical_twilight = 0
        self.moon_illumination = 0
        self.weather = 0
        self.min_records = []
        self.valid_for_use = False
        self.exclusion_reason = "UNITINIALIZED"

    # initialize a night record from a raw data file
    def initialize(
        self,
        night_date: Time,
        night_file: str,
        morning_date: Time,
        morning_file: str,
        sensor_long: float,
        sensor_lat: float,
    ):
        # let night and morning date include time as noon of their respective days
        # Format Reminders: time = Time('2015-06-16 12:00:00') for assignment,
        #                          2023-01-23T06:00:00.992 on file
        self.nightof = night_date
        self.morningof = morning_date

        sensor = Observer(
            longitude=sensor_long * u.deg,
            latitude=sensor_lat * u.deg,
            elevation=0 * u.m,
            name="Sensor",
            timezone="US/Central",
        )
        self.sunset = sensor.sun_set_time(night_date, which="next")
        self.sunrise = sensor.sun_rise_time(night_date, which="next")
        self.astronomical_twilight = sensor.twilight_evening_astronomical(
            night_date, which="next"
        )

        # how much of the lunar surface is illuminated that night, pulled when the sky is fully dark (astro. twilight)
        # comparable to moon phase (0 = new moon, ~1 = full) without the pi of obs.moon_phase
        self.moon_illumination = sensor.moon_illumination(
            self.astronomical_twilight
        )
        self.weather = 0  # TODO Update Placeholder -- how to succinctly record nightly weather?

        # example line from 2023-01-23_LENSSTSL0008.txt:
        # 2023-01-23T06:00:00.992;2023-01-23T00:00:00.992;0.38;4.39;0.0;LENSS_TSL_0008
        # UTC Time; Local Time; Temperature (C); Frequency; Voltage; ID

        self.min_records = []

        n_file = open(night_file)
        transtr = n_file.readline()
        while len(transtr) != 0:
            data = transtr.split(";")
            data[0] = data[0].replace("T", " ")
            data[1] = data[1].replace("T", " ")
            m_rec = minute_record(
                Time(data[0]),
                Time(data[1]),
                data[2].float(),
                data[3].float(),
                data[4].float,
                data[5],
            )
            if (
                m_rec.local_time < self.sunset
            ):  # unsure if this will work or if a special time comp function is needed
                n_file.readline()
                continue
            self.min_records.append(m_rec)
            transtr = n_file.readline()
        n_file.close()

        m_file = open(morning_file)
        transtr = m_file.readline()
        while len(transtr) != 0:
            data = transtr.split(";")
            data[0] = data[0].replace("T", " ")
            data[1] = data[1].replace("T", " ")
            m_rec = minute_record(
                Time(data[0]),
                Time(data[1]),
                data[2].float(),
                data[3].float(),
                data[4].float,
                data[5],
            )
            if (
                m_rec.local_time > self.sunrise
            ):  # unsure if this will work or if a special time comp function is needed
                m_file.readline()
                break
            self.min_records.append(m_rec)
            transtr = m_file.readline()
        m_file.close()

        self.valid_for_use = True
        self.exclusion_reason = "None"

    # mark data as invalid based on various night conditions
    def grade_data(self):
        # taking the average night to be ten hours (600 minutes), if more than three hours (180 minutes) are missing,
        # invalidate the data based on insufficient records
        if len(self.min_records) < 420:
            self.valid_for_use = False
            self.exclusion_reason = "Insufficient Records for Night"

        # if the moon would have been obscured by bad weather for more then three hours, invalidate based on weather conditions
        # use something other than python-weather?

    # given a function on a float, updates all temperature, frequency, or voltage values
    def apply_correction(self, field_to_update: str, funct):
        if field_to_update == "TEMP":
            for rec in self.min_records:
                rec.temperature = funct(rec.temperature)
        if field_to_update == "FREQ":
            for rec in self.min_records:
                rec.frequency = funct(rec.frequency)
        if field_to_update == "VOLT":
            for rec in self.min_records:
                rec.voltage = funct(rec.voltage)
        else:
            print("error: field not recognized/field should not be updated")

    # export night record to a new file
    def rec_export(self, filename: str):
        new_file = open(filename, "x")
        if self.valid_for_use == False:
            new_file.write("INVALID\n")
            new_file.write(self.exclusion_reason)
        else:
            # night date -- 2023-01-23 06:00:00.992
            new_file.write(self.night_date.strptime("%Y-%m-%d %H:%M:%S.%f"))
            new_file.write("\n")
            # morning date
            new_file.write(self.morning_date.strptime("%Y-%m-%d %H:%M:%S.%f"))
            new_file.write("\n")
            # sunrise
            new_file.write(self.sunrise.strptime("%Y-%m-%d %H:%M:%S.%f"))
            new_file.write("\n")
            # sunset
            new_file.write(self.sunset.strptime("%Y-%m-%d %H:%M:%S.%f"))
            new_file.write("\n")
            # twilight
            new_file.write(
                self.astronomical_twilight.strptime("%Y-%m-%d %H:%M:%S.%f")
            )
            new_file.write("\n")
            # illumination
            new_file.write(str(self.moon_illumination))
            new_file.write("\n")
            # weather
            # unimplemented

            for rec in self.min_records:
                new_file.write(
                    rec.utc_timesunset.strptime("%Y-%m-%d %H:%M:%S.%f")
                )
                new_file.write(";")
                new_file.write(rec.local_time.strptime("%Y-%m-%d %H:%M:%S.%f"))
                new_file.write(";")
                new_file.write(str(rec.temperature))
                new_file.write(";")
                new_file.write(str(rec.frequency))
                new_file.write(";")
                new_file.write(str(rec.voltage))
                new_file.write(";")
                new_file.write(str(rec.sensor_id))
                new_file.write("\n")
        new_file.close()

    # import previously exported night record
    def rec_import(self, filename: str):
        # takes an already created object and updates it to imported values
        file = open(filename)
        p_str = file.readline()
        if p_str == "INVALID":
            # check if this is okay for str comp?
            self.valid_for_use = False
            self.exclusion_reason = file.readline()
        else:
            # night date -- 2023-01-23 06:00:00.992
            self.night_date = Time(p_str)
            # morning date
            self.morning_date = Time(file.readline())
            # sunrise
            self.sunrise = Time(file.readline())
            # sunset
            self.sunset = Time(file.readline())
            # twilight
            self.astronomical_twilight = Time(file.readline())
            # illumination
            self.moon_illumination = file.readline().float()
            # weather
            # unimplemented

            p_str = file.readline()
            while len(p_str) != 0:
                data = p_str.split(";")
                m_rec = minute_record(
                    Time(data[0]),
                    Time(data[1]),
                    data[2].float(),
                    data[3].float(),
                    data[4].float,
                    data[5],
                )
                self.min_records.append(m_rec)
                p_str = file.readline()
        file.close()
