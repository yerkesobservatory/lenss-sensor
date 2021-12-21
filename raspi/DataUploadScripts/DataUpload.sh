#!/bin/sh

# Data upload script
#
# Copies all files with a creation date older than the current date to an archive directory
# and then uploads them to Google Drive.
#
# @param $1 full path to directory containing sensor files. No trailing "/".
# Defaults to '/home/pi/Local/sensorsdata'
# @param $2 full path to dirictory containing archived sensor files. No trailing "/".
# Defaults to '/home/pi/Local/SensorDataArchive'
# @param $3 name of rclone location to use. Defaults to 'GLAS'

# these should probably be set as environment variables as they never change
# this would also mean that for each sensor, as long as those variables exist, the actual paths to those directories won't matter
# I'll give example viarable names below
inputDir=$1 # SENSOR_INPUT_PATH
[ -z "inputDir" ] && inputDir="/home/pi/Local/sensorsdata"
archiveDir=$2 # SENSOR_ARCHIVE_PATH
[ -z "archiveDir" ] && archiveDir="/home/pi/Local/SensorDataArchive"
drive=$3 # SENSOR_DRIVE
[ -z "drive" ] && drive="GLAS"

# For every enty found, the date, month number, file name, and sensor number are stored.
# The month name in found in a lookup table based off of the month number. The previously
# stored variables are then used to create directories for storage and move the files to
# their appropriate location.
for output in $(find "$inputDir" -type f -printf '%T+;%p\n' | sed "/$(date +%Y-%m-%d)/d") # could we do this with ls -l instead?
do
    # It is best practice to use the numeric months instead as they allow sorting by time to be a much easier task
    date=$(echo $output | awk -F ";" '{print substr($1,0,8)}')
    monthNum=$(echo $date | awk '{print substr($1,6,2)}')
    month=$(grep $monthNum ./monthLookup | awk '{print $2}')
    fileName=$(echo $output | awk -F ";" '{print $2}')
    sensor=$(echo $fileName | awk -F "/" '{print $(NF-1)}')
    # for better organization I'd recommend making the year its own directory as well
    # additionally making the sensor the root directory would be a good idea for a few reasons
    # 1. If there isa problem with an individual sensor only that sensor's subdirectories will have that issue
    # making it easier to identify.
    # 2. As the number of sensors increase, it will become more difficult to find data for a specific sensor, as we want to compare data over time, we should make that are final path
    # ex: <sensor>/<yyyy>/<mm>/<dd>/<file>
    # 3. This makes it simple to compare data between sensors with scripts as we know all the data in a specific directory will belong to the same sensor
    mkdir -p $archiveDir/$date$month/$sensor 
    cp "$fileName" "$archiveDir/$date$month/$sensor/" 
    rclone move "$fileName" $drive:$date$month/$sensor/
done
