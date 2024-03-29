"""
Defines structs for manipulating data in memory.
"""

import sys
import os

from ..external.google_docs import GoogleDocs

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

        docs = GoogleDocs()
        self.min_records = []

        # example line from 2023-01-23_LENSSTSL0008.txt:
        # 2023-01-23T06:00:00.992;2023-01-23T00:00:00.992;0.38;4.39;0.0;LENSS_TSL_0008
        # UTC Time; Local Time; Temperature (C); Frequency; Voltage; ID
        n_lines = docs.get_file(night_file)
        for line in n_lines:
            data = line.split(";")
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
                continue
            self.min_records.append(m_rec)

        m_lines = docs.get_file(morning_file)
        for line in m_lines:
            data = line.split(";")
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

    def rec_export(self, file_name: str):
        """
        Export night record to Google Drive.
        """
        file_text = ""
        if not self.valid_for_use:
            file_text = "INVALID\n" + self.exclusion_reason
        else:
            vals = [
                self.night_date.strftime(PROJECT_DATE_FORMAT),
                self.morning_date.strftime(PROJECT_DATE_FORMAT),
                self.sunrise.strftime(PROJECT_DATE_FORMAT),
                self.sunset.strftime(PROJECT_DATE_FORMAT),
                self.astronomical_twilight.strftime(PROJECT_DATE_FORMAT),
                str(self.moon_illumination),
            ]
            for line in vals:
                file_text = file_text + line + "\n"

            for rec in self.min_records:
                vals = [
                    rec.utc_time.strftime(PROJECT_DATE_FORMAT),
                    rec.local_time.strftime(PROJECT_DATE_FORMAT),
                    str(rec.temperature),
                    str(rec.frequency),
                    str(rec.voltage),
                    rec.sensor_id,
                ]
                for line in vals:
                    file_text = file_text + line + "\n"

        docs = GoogleDocs()
        docs.push_file(file_name, file_text)


class InheritedNightRecord(NewNightRecord):
    def __init__(self, file_name: str):
        """
        Import previously exported night record.
        """
        docs = GoogleDocs()
        f_lines = docs.get_file(file_name)

        if f_lines[0] == "INVALID":
            self.valid_for_use = False
            self.exclusion_reason = f_lines[1]
        else:
            # night date -- 2023-01-23 06:00:00.992
            self.night_date = Time(f_lines[0])
            # morning date
            self.morning_date = Time(f_lines[1])
            # sunrise
            self.sunrise = Time(f_lines[2])
            # sunset
            self.sunset = Time(f_lines[3])
            # twilight
            self.astronomical_twilight = Time(f_lines[4])
            # illumination
            self.moon_illumination = float(f_lines[5])

            i = 6
            while i < f_lines.len():
                data = f_lines[i].split(";")
                m_rec = MinuteRecord(
                    Time(data[0]),
                    Time(data[1]),
                    float(data[2]),
                    float(data[3]),
                    float(data[4]),
                    data[5],
                )
                self.min_records.append(m_rec)
                i += 1

        self.valid_for_use = True
        self.exclusion_reason = "None"


def print_example_dead():
    """
    Prints results of the struct creation on a small sample file.
    """
    # run with "python night_record.py print_example" on
    # command line -- out of date; see below
    # NOTE: can no longer run: ran on NewNightRecord with local file
    # implementation rather than GDoc implementation; now kept as an example

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

    # Everything looks good!


if __name__ == "__main__":
    globals()[sys.argv[1]]()
