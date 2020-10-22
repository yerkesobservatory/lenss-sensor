#!/bin/sh

# Data upload script
#
# Copies all files with a creation date older than the current date to an archive directory
# and then uploads them to Google Drive.
#
# @param $1 full path to directory containing sensor files. No trailing "/".
# Defaults to '/home/pi/SensorData'
# @param $2 full path to dirictory containing archived sensor files. No trailing "/".
# Defaults to '/home/pi/SensorDataArchive'
# @param $3 name of rclone location to use. Defaults to 'GLAS'

inputDir=$1
[ -z "inputDir" ] && inputDir="/home/pi/SensorData"
archiveDir=$2
[ -z "archiveDir" ] && archiveDir="/home/pi/SensorDataArchive"
drive=$3
[ -z "drive" ] && drive="GLAS"

# For every enty found, the date, month number, file name, and sensor number are stored.
# The month name in found in a lookup table based off of the month number. The previously
# stored variables are then used to create directories for storage and move the files to
# their appropriate location.
for output in $(find "$inputDir" -type f -printf '%T+;%p\n' | sed "/$(date +%Y-%m-%d)/d")
do
    date=$(echo $output | awk -F ";" '{print substr($1,0,10)}')
    monthNum=$(echo $date | awk '{print substr($1,6,2)}')
    month=$(grep $monthNum ./monthLookup | awk '{print $2}')
    fileName=$(echo $output | awk -F ";" '{print $2}')
    sensor=$(echo $fileName | awk -F "/" '{print $(NF-1)}')
    mkdir -p $archiveDir/$date$month/$sensor
    cp "$fileName" "$archiveDir/$date$month/$sensor/"
    rclone move "$fileName" $drive:$date$month/$sensor/
done
