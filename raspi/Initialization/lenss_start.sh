#!/bin/bash

#fetch ID number
id=$(echo $HOSTNAME | cut -c7-10)

#make directories
mkdir -p /home/pi/Local/sensorsdata/LENSS_TSL_$id/
mkdir /home/pi/Local/SensorDataArchive
mkdir /home/pi/Local/logging

#edit serverconfig.ini
sed -i "s/å/${id}/g" /home/pi/lenss-sensor/config/serverconfig.ini
