#!/bin/bash/

port=$(echo $(ls /dev | grep ACM))
sed "6s/.*/arduinoport = \/dev\/${port}/" /home/pi/lenss-sensor/config/serverconfig.ini
