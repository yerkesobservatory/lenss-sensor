"""
include library python-weather at https://github.com/null8626/python-weather
include astropy and astroplan (useful interface for astropy)
-> use `import python-weather` and `import astropy`, etc.
-> setup a virtual environment and download packages via `pip install [package]`

file1 = a file for some day (for evening values of a night)
file2 = the file for the subsequent day (for the morning values of a night)

use astroplan to find
Date-Time sunset_time on some day
Date-Time sunrise_time on subsequent day

ensure desired time frame is present in the file if more than some percentage
of entries is missing, report correction failure due to lack of data

use python-weather to find weather and moon phase -check the hourly forecast:
if more than some percentage of the hours between sunset and sunrise are some
degree of cloudy, report correction failure due to weather -what to do with
moon illumination besides record? adjust or invalidate data?

example line from 2023-01-23_LENSSTSL0008.txt
2023-01-23T06:00:00.992;2023-01-23T00:00:00.992;0.38;4.39;0.0;LENSS_TSL_0008
UTC Time; Local Time; Temperature (C); Frequency; Voltage; ID

starting in file1 with the first entry after sunset to the end of the file:
read each line, tokenize on semicolon, store in struct (maybe with additional
info like hourly weather?)

starting in file2 with the first entry to the last entry before sunrise: read
each line, tokenize on semicolon, store in struct (maybe with additional info
like hourly weather?)

output is a struct for the night, containing info like moon illumination and
all relevant lines from the files as their own struct within the night struct

functions to follow afterwards: -writing a night struct to Google Drive -take
a night struct and update the values on some attribute >>>eg. if a full moon
artificially brightens by 25%, reduce each frequency by 25% to make it more
accurate >>>possibly make it a general higher order function if python allows
them? -todo: check preferred organization of struct to pass along and/or
output to GDrive by data_viz """
