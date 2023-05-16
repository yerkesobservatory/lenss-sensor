"""
This file serves as the central runner for any data analysis processes.
"""

from night_record import NewNightRecord
from astropy.time import Time
from datetime import datetime
from datetime import timedelta

# this is an example; to pull from all sensor data, this will need to
# be externally supplied by the call
SENSOR_NAME = "LENSS_TSL_0008"
# rough coodinates near geneva lake
# may want to set to for each sensor's exact location in the future
SENSOR_LAT = 42.57
SENSOR_LONG = -88.542

# define correction functions here
# then add to list of corrects to automatically run

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

    nrec.rec_export(
        night_str + " to " + morning_str + " " + SENSOR_NAME + ".txt"
    )
