"""
TODO: File level docstring.
"""

import sys
import os

import astropy.units as u
from astroplan import Observer
from astropy.time import Time

PROJECT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


class MinuteRecord:
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
        self.voltage = volt
        self.sensor_id = id


class NewNightRecord:
    """
    Create an uninitialized night record.
    """

    def __init__(
        self,
        night_date: Time,
        night_file: str,
        morning_date: Time,
        morning_file: str,
        sensor_lat: float,
        sensor_long: float,
    ):
        # let night and morning date include time as noon of their respective
        # days
        # Format Reminders: time = Time('2015-06-16 12:00:00') for assignment,
        #                          2023-01-23T06:00:00.992 on file
        self.night_of = night_date
        self.morning_of = morning_date

        sensor = Observer(
            longitude=sensor_long * u.deg,
            latitude=sensor_lat * u.deg,
            elevation=0 * u.m,
            name="Sensor",
            timezone="US/Central",
        )
        # reports time in UTC
        self.sunset = sensor.sun_set_time(night_date, which="nearest")
        self.sunrise = sensor.sun_rise_time(morning_date, which="nearest")
        self.astronomical_twilight = sensor.twilight_evening_astronomical(
            night_date, which="nearest"
        )

        # how much of the lunar surface is illuminated that night, pulled when
        # the sky is fully dark (astro. twilight) comparable to moon phase
        # (0 = new moon, ~1 = full) without the pi of obs.moon_phase
        self.moon_illumination = sensor.moon_illumination(
            self.astronomical_twilight
        )
        # future TODO: store nightly weather

        self.min_records = []

        # example line from 2023-01-23_LENSSTSL0008.txt:
        # 2023-01-23T06:00:00.992;2023-01-23T00:00:00.992;0.38;4.39;0.0;LENSS_TSL_0008
        # UTC Time; Local Time; Temperature (C); Frequency; Voltage; ID
        with open(night_file) as n_file:
            trans_str = n_file.readline()
            while len(trans_str) != 0:
                data = trans_str.split(";")
                data[0] = data[0].replace("T", " ")
                data[1] = data[1].replace("T", " ")
                m_rec = MinuteRecord(
                    Time(data[0]),
                    Time(data[1]),
                    float(data[2]),
                    float(data[3]),
                    float(data[4]),
                    data[5],
                )
                if m_rec.utc_time < self.sunset:
                    trans_str = n_file.readline()
                    continue
                self.min_records.append(m_rec)
                trans_str = n_file.readline()

        with open(morning_file) as m_file:
            trans_str = m_file.readline()
            while len(trans_str) != 0:
                data = trans_str.split(";")
                data[0] = data[0].replace("T", " ")
                data[1] = data[1].replace("T", " ")
                m_rec = MinuteRecord(
                    Time(data[0]),
                    Time(data[1]),
                    float(data[2]),
                    float(data[3]),
                    float(data[4]),
                    data[5],
                )
                if m_rec.utc_time > self.sunrise:
                    break
                self.min_records.append(m_rec)
                trans_str = m_file.readline()

        self.valid_for_use = True
        self.exclusion_reason = "None"

    def grade_data(self):
        """
        Grade quality of as based on various night conditions.
        """
        # taking the average night to be ten hours (600 minutes), if more than
        # three hours (180 minutes) are missing, invalidate the data based on
        # insufficient records
        if len(self.min_records) < 420:
            self.valid_for_use = False
            self.exclusion_reason = "Insufficient Records for Night"

        # future TODO: invalidate based on weather conditions
        # potential future TODO: grade data on a scale (good, poor, unusable,
        #  etc) instead of just valid or invalid

    def apply_correction(self, field_to_update: str, funct):
        """
        Given a function on a float, updates all temperature, frequency,
        or voltage values.
        """
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

    def rec_export(self, filename: str):
        """
        Export night record to a new file.
        """
        with open(filename, "x") as new_file:
            if not self.valid_for_use:
                new_file.write("INVALID\n" + self.exclusion_reason)
            else:
                vals = [
                    self.night_date.strftime(PROJECT_DATE_FORMAT),
                    self.morning_date.strftime(PROJECT_DATE_FORMAT),
                    self.sunrise.strftime(PROJECT_DATE_FORMAT),
                    self.sunset.strftime(PROJECT_DATE_FORMAT),
                    self.astronomical_twilight.strftime(PROJECT_DATE_FORMAT),
                    str(self.moon_illumination),
                ]
                new_file.write("\n".join(vals) + "\n")

                for rec in self.min_records:
                    vals = [
                        rec.utc_time.strftime(PROJECT_DATE_FORMAT),
                        rec.local_time.strftime(PROJECT_DATE_FORMAT),
                        str(rec.temperature),
                        str(rec.frequency),
                        str(rec.voltage),
                        rec.sensor_id,
                    ]
                    new_file.write(";".join(vals) + "\n")

class InheritedNightRecord(NewNightRecord):
    def __init__(self, filename: str):
        """
        Import previously exported night record.
        """
        # takes an already created object and updates it to imported values
        with open(filename) as file:
            p_str = file.readline()
            if p_str == "INVALID":
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
                self.moon_illumination = float(file.readline())

                p_str = file.readline()
                while len(p_str) != 0:
                    data = p_str.split(";")
                    m_rec = MinuteRecord(
                        Time(data[0]),
                        Time(data[1]),
                        float(data[2]),
                        float(data[3]),
                        float(data[4]),
                        data[5],
                    )
                    self.min_records.append(m_rec)
                    p_str = file.readline()


def print_example():
    """
    Prints results of the struct creation on a small sample file.
    """
    # run with "python night_record.py print_example" on
    # command line

    print("starting simple test:")
    """
    simple test will use simple_test_night.txt and simple_test_morning.txt on 
    the night of 2023/01/24 and morning of 2023/01/25, where moon illumination 
    is 9.9%, sunset is 4:55 PM CT/9:55 PM UTC, sunrise is 7:09 AM CT/12:09 PM 
    UTC, and astronomical twilight is between 05:59 PM CT/10:59 PM UTC and 6:32 
    PM CT/11:32 PM UTC in Hyde Park
    """
    print("working directory: " + os.getcwd() + "\n")
    n_rec = NewNightRecord(
        Time("2023-01-24 12:00:00.000"),
        "./test_files/simple_test_night.txt",
        Time("2023-01-25 12:00:00.000"),
        "./test_files/simple_test_morning.txt",
        41.7948,
        -87.5917,
    )
    print(
        "night date should be 23/1/24: "
        + n_rec.night_of.strftime(PROJECT_DATE_FORMAT)
    )
    print(
        "morning date should be 23/1/25: "
        + n_rec.morning_of.strftime(PROJECT_DATE_FORMAT)
        + "\n"
    )

    print(
        "sunrise, sunset, and twilight are off by one hour, likely due to "
        "daylight savings; otherwise within reasonable range (~5m)"
    )
    print(
        "sunset should be ~21:55: " + n_rec.sunset.strftime(PROJECT_DATE_FORMAT)
    )
    print(
        "sunrise should be ~12:09: "
        + n_rec.sunrise.strftime(PROJECT_DATE_FORMAT)
    )
    print(
        "twilight should be between 10:59 and 11:32: "
        + n_rec.astronomical_twilight.strftime(PROJECT_DATE_FORMAT)
        + "\n"
    )

    print(
        "illumination is way off but that could be indicative of real world "
        "conditions in Chicago rather than an error"
    )
    print("illumination should be ~9.9: " + str(n_rec.moon_illumination) + "\n")

    print("should be 2 records: " + str(len(n_rec.min_records)))
    print(
        "first record should be 23:00: "
        + n_rec.min_records[0].utc_time.strftime(PROJECT_DATE_FORMAT)
    )
    print(
        "second record should be 10:00: "
        + n_rec.min_records[1].utc_time.strftime(PROJECT_DATE_FORMAT)
        + "\n"
    )

    print("exclusion should be none: " + n_rec.exclusion_reason)


if __name__ == "__main__":
    globals()[sys.argv[1]]()
