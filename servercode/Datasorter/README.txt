# # # # # # # # # # # # # # #
# Overview of datasorter.sh #
# # # # # # # # # # # # # # #

Type: 	POSIX compliant shell script

About:	This script is designed to automatically sort 
	incoming data into separate files under folders 
	with the ID of the original sending device. 

	It reads the newest file in the specified input 
	folder, separates the data lines, sets up directories 
	for any new collection devices found in the file, 
	and moves the data for each device into its appropriate 
	folder in a file labled <date>_<device_id>_raw.csv

	The date is found by pulling the first 10 characters 
	of the input file to accommodate a YYYY-MM-DD format. 
	
	-------------
	!!! NOTES !!!
	-------------

	The first column in the input file needs to be the ID 
	of the device, or an identifier of a certain length. 
	It is currently set to a length of 4. If a longer 
	identifier is required, it must be changed in the 
	script. 

	The first line of the input file should be a header 

	All entries should be space separated. This default 
	delimiter can be changed manually in the script. 

	The script will break if the located input file does 
	not have a 10 character long prefix.

	The script will break if specified paths contain 
	whitespace or trailing '/'s.

Arguments: $1 - <INPUT_FOLDER>
		Default: /home/pi/indata

	   $2 - <OUTPUT_FOLDER>
		Default: /home/pi/outdata

Usage: sh datasorter.sh ~/share/input_directory ~/Documents/output_directory

Setting Up Testing Environment 
______________________________

Download the full 'Datasorter' folder, extract the folder, and cd into the folder 
such that 'indata', 'outdata', 'datasorter.sh', and 'README.txt' are in your 
working directory. 

Run 'sh datasorter.sh ./indata ./outdata'
