#!/bin/sh

# Data upload script
#
# Copies all files with a creation date older than the current date to an archive directory
# and then uploads them to Google Drive.
#
# Relies on the following environment variables stored in /etc/environment:
# SENSOR_INPUT_PATH --> Location of directory that contains the sensor data files
# SENSOR_ARCHIVE_PATH --> Location of archive directory
# SENSOR_DRIVE --> Name of Rclone remote where the sensor data is stored

# For every enty found, the date, month number, file name, and sensor number are stored.
# The month name in found in a lookup table based off of the month number. The previously
# stored variables are then used to create directories for storage and move the files to
# their appropriate location.
for file in $(find "$SENSOR_INPUT_PATH" -type f -printf '%P\n' | sed "/$(date +%Y-%m-%d)/d")
do
    year=$(echo "$file" | awk '{print substr($0,1,4)}')
    month=$(echo "$file" | awk '{print substr($0,6,2)}')
    sensor="LENSS_TSL_$(echo $HOSTNAME | cut -c7-10)"
    mkdir -p "$SENSOR_ARCHIVE_PATH/$sensor/$year/$month"
    cp "$SENSOR_INPUT_PATH/$file" "$SENSOR_ARCHIVE_PATH/$sensor/$year/$month/"
    rclone move "$SENSOR_INPUT_PATH/$file" "$SENSOR_DRIVE:$sensor/$year/$month/"
done
