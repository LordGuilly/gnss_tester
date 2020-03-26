# GNSS Tester

This script is for evaluating the performance of GNSS receivers, either by capturing the data live from a serial port, or by analyzing a captured text file of NMEA sentences

It will generate an html output file, with all the positions scattered in map, placing a mark in the last reported position


## Requirements

The script was developed using Python 3.8, but can probably run with earlier Python 3 versions.

The following pythons modules are required for the script to work

`pyserial pynmea2 numpy gmplot`

For installing it's recommended to use `pip`

`py -m pip install pyserial`

`py -m pip install numpy`

`py -m pip install pynmea2`

`py -m pip install gmplot`


## Usage

The script is a command line tool, and all the available options are listed in the help

```
py gnss_tester.py --help

usage: gnss_tester.py [-h] [--infile INPUT_FILE] [--mapfile MAP_FILE] [--serial SERIAL_PORT] [--query] [--config]
                      [--coldstart] [--full-coldstart] [--duration DURATION] [--rawfile RAW_FILE]

Process NMEA files.

optional arguments:
  -h, --help            show this help message and exit
  --infile INPUT_FILE   logfile to be processed
  --mapfile MAP_FILE    name of the HTML output file
  --serial SERIAL_PORT  serial port to be used as input
  --query               dump module configuration (serial required!)
  --config              run module configuration sequence (serial required!)
  --coldstart           force a module coldstart (serial required!)
  --full-coldstart      force a full coldstart, resetting the config (serial required!)
  --duration DURATION   run the the capture for DURATION seconds (serial required!)
  --rawfile RAW_FILE    file where the raw NMEA data will be stored (serial required)
```

* parsing an existing text file with NMEA sentences:

  The following command will parse "txtfile.txt", and generate an HTML output named "outputfile.htm", which will contain the all the positions.
  
  `py gnss_tester.py --infile <txtfile.txt> --mapfile <outputfile.htm>`

* parse the information from a GNSS unit connected in a serial port

  The following command will open "serialport", and capture all the NMEA sentences in "rawfile.txt", during "duration" seconds. Then it will generatie an HTML output named "outputfile.htm", which will contain the all the positions.
  
  `py gnss_tester.py --serial <serialport> --mapfile <outputfile.htm> --duration <duration> --rawfile <rawfile.txt>`

