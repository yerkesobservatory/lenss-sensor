"""
This file serves as the central runner for any data analysis processes.
"""

from night_record import NewNightRecord
from night_record import PROJECT_DATE_FORMAT
from astropy.time import Time
from datetime import datetime
from datetime import timedelta

# must be externally supplied
SENSOR_NAME = "LENSSTSL0008"
SENSOR_LAT
SENSOR_LONG

# define correction functions here


def main():
    """
    This function is the central function for any data analysis or cleaning
    processes.
    """
    today = datetime.today()
    night_date = today - timedelta(days=2)
    night_str = night_date.strftime("%Y-%m-%d")
    morning_date = today - timedelta(days=1)
    morning_str = morning_date.strftime("%Y-%m-%d")

    # TODO: will likely need to add directories to file path
    night_file = night_str + "_" + SENSOR_NAME + ".txt"
    morning_file = morning_str + "_" + SENSOR_NAME + ".txt"

    nrec = NewNightRecord(
        Time(night_str + " 12:00:00.0"),
        night_file,
        Time(morning_str + " 12:00:00.0"),
        morning_file,
        SENSOR_LAT,
        SENSOR_LONG,
    )

    nrec.grade_data()

    # each element must be a tuple of the field being corrected as a string
    # followed by a function to apply
    cor_to_apply = []
    for funct in cor_to_apply:
        nrec.apply_correction(funct[0], funct[1])

    # add directory to file path if necessary
    # currently exports locally
    nrec.rec_export(
        night_str + " to " + morning_str + " " + SENSOR_NAME + ".txt"
    )
