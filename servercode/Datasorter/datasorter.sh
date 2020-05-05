#!/bin/sh

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 			Sensor Data Sorting Script			  #
# ======================================================================= #
# This script sorts the combined data of all sensors into files for each  #
# sensor.								  #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

#IFS="$(printf '\n\t')" # May remove. Didn't seem to help

# Input and output directory argumentes. A bit sketchy at the moment because 
# it will not deal with spaces or any special characters, and you can't have
# a trailing "/" on OUTFOLDER.
INFOLDER=$1
[ -z "$INFOLDER" ] && INFOLDER="/home/pi/indata"
OUTFOLDER=$2
[ -z "$OUTFOLDER" ] && INFOLDER="/home/pi/outdata"

# Selects the newest file in $INFOLDER and sets it to $NEWFILE
NEWFILE="$(find "$INFOLDER" -printf "%T@ %p\n" | sort -nr | sed '\:'"$INFOLDER"'$:d' | sed -n 1p | awk '{print $2}')"
echo "Selected:" "$NEWFILE" # Peace of mind

# Selects the date of the file from the first 10 characters of $NEWFILE
DATE="$(echo "${NEWFILE}" | sed -e 's:'"$INFOLDER"'::g;s:/::g' | awk '{ print substr($0, 1, 10) }')"
echo "Date:" "$DATE" # Peace of mind

# Splits data within $NEWFILE into separate files based on the first column 
# (device ID) Under a directory with the device ID. Currently only looks at 
# first 4 characters. ID length can be changing 4 to the length of device ID 
# required.
awk -v out="$OUTFOLDER" 'BEGIN { FS = "," } ; NR==1{ h=$0 }NR>1{ print out"/"$1 }' $NEWFILE | xargs mkdir -vp && \
awk -v out="$OUTFOLDER" -v date="$DATE" 'BEGIN { FS = "," } ; NR==1{ h=$0 }NR>1{ print (!a[$1]++? h ORS $0 : $0) > out"/"substr($1, 1, 4)"/"date"_"substr($1, 1, 4)"_raw.csv" }' $NEWFILE && \
echo "Done"
