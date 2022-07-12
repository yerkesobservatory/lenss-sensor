#!/bin/bash

# Fetch ID number
id=$(echo $HOSTNAME | cut -c7-10)

# Make sensor directory
mkdir /home/pi/SensorData/LENSS_TSL_$id

# Change to appropriate sensor number in serverconfig.ini
sed -i "s/å/${id}/g" /home/pi/Programs/serverconfig.ini
