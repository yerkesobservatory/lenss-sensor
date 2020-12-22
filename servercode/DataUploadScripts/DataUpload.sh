#!/bin/sh
# GDrive Upload
# Moves sensor data files from local machine to a Google Drive folder using Rclone
# Usage: ./DataUpload.sh

# Selects the date (YYYY-MM) and month name (July) from the file to be uploaded
numerical="$(find /home/pi/Documents/LENSS/sensorsdata -type f -printf '%T+ %p\n' | sort | head -n 1 | awk '{print substr($0,0,8)}')"
monthnum="$(echo | awk -v numerical="${numerical}" '{print substr(numerical,6,7)}')"
month="$(grep $monthnum /home/pi/.scripts/.monthLookup | sort | awk '{print $2}')" # gets month name from a lookup file based one the month number

# Selects the oldest file with a given prefix (ard- and sqm-) for upload
upload1="$(find /home/pi/Documents/LENSS/sensorsdata/ard* -type f -printf '%T+ %p\n' | sort | head -n 1 | awk '{print $2}')"
upload2="$(find /home/pi/Documents/LENSS/sensorsdata/sqm* -type f -printf '%T+ %p\n' | sort | head -n 1 | awk '{print $2}')"

# Uploads each selected file with Rclone
rclone move $upload1 GLAS:$numerical$month/ && rclone move $upload2 GLAS:$numerical$month/
