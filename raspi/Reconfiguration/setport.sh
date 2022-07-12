#!/bin/bash

port=$e(echo $(ls /dev | grep ACM))

if [[ -z "$port" ]]; then
  echo "No Arduino connected."
  exit 1
else
  sed -i "6s/.*/arduinoport = \/dev\/${port}/" /home/pi/Programs/serverconfig.ini
fi

echo "Port set successfully."
exit 0