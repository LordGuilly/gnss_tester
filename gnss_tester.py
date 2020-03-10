import time
import serial
import pynmea2
import gmplot
import logging
import argparse
import numpy as np
import re


config_check_cmd_list = [
    "PMTK605",
    "PMTK401",
    "PMTK413",
    "PQGLP,R",
    "PQVERNO,R",
    "PQVERNO,R,SUB",
    "PQFLP,R"
    ]

module_setup_cmd_list = [
    "$PMTK386,2*3E",
]

def generate_full_config_cmd(command):
    checksum = pynmea2.NMEASentence.checksum(command)
    full_command = "$" + command + "*" + format(checksum, 'x')
    logging.debug("full_command \t[" + full_command + "]")
    return full_command

def latitude_converter(lat_string, direction):
    latitude = float(lat_string[:2])
    latitude += (float(lat_string[2:9])/60)

    if direction == 'S':
        latitude = latitude * (-1)
                
    return latitude
            
def longitude_converter(lon_string, direction):
    longitude = float(lon_string[:3])
    longitude += (float(lon_string[3:10])/60)

    if direction == 'W':
        longitude = longitude * (-1)

    return longitude

def update_position_lists(msg):
    if isinstance(msg, pynmea2.types.talker.GGA) and msg.gps_qual > 0:
        lat_list.append(latitude_converter(msg.lat, msg.lat_dir))
        lon_list.append(longitude_converter(msg.lon, msg.lon_dir))

def dump_debug_info(msg):
    if isinstance(msg, pynmea2.types.talker.GGA):
        logging.info("Time[" + str(msg.timestamp) + "]\tSatellites in view[" + msg.num_sats + "]")


def force_coldstart_on_module(com):
    logging.debug("Forcing module coldstart")
    full_command = generate_full_config_cmd("PMTK103")
    com.write(bytes("\r\n",'utf-8'))
    com.write(bytes(full_command,'utf-8'))
    com.write(bytes("\r\n",'utf-8'))

    while True:
        response = com.readline().rstrip()
        if re.match('\$PMTK', response.decode('utf-8')):
            logging.info("Got\t\t[" + response.decode('utf-8') + "]")
            break

    
def dump_module_configuration(com):
    for command in config_check_cmd_list:
        full_command = generate_full_config_cmd(command)
        logging.debug("Checking \t[" + full_command + "]")

        response = com.readline()

        com.write(bytes("\r\n",'utf-8'))
        com.write(bytes(full_command,'utf-8'))
        com.write(bytes("\r\n",'utf-8'))

        while True:
            response = com.readline().rstrip()
            if re.match('\$PMTK', response.decode('utf-8')):
                logging.info("Got\t\t[" + response.decode('utf-8') + "]")
                break
            if re.match('\$PQ', response.decode('utf-8')):
                logging.info("Got\t\t[" + response.decode('utf-8') + "]")
                break
                  



def read(filename):
    with open(filename) as file_in:
        for line in file_in:
            logging.debug(line)
            try:
                msg = pynmea2.parse(line.rstrip())
                update_position_lists(msg)#
                dump_debug_info(msg)
            except pynmea2.ParseError:
                logging.error("PARSER ERROR")
            

def read_serial(com, duration):
    
    reader = pynmea2.NMEAStreamReader(errors='ignore')
    
    if duration:
        endtime = time.monotonic() + duration
    else:
        endtime = 0
    logging.info("running time [" + str(duration) + "]" )

    while (endtime != 0) and (endtime > time.monotonic()):
        try:
            data = com.readline()
            for msg in reader.next(data.decode("utf-8")):
                update_position_lists(msg)
                dump_debug_info(msg)

        except KeyboardInterrupt:
            break
            # quit
        



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    cmdline_parser = argparse.ArgumentParser(description='Process NMEA files.')
    cmdline_parser.add_argument('--infile', action='store', dest='input_file', help="logfile to be processed")
    cmdline_parser.add_argument('--mapfile', action='store', default="map.html", dest='map_file', help="name of the HTML output file")
    cmdline_parser.add_argument('--serial', action='store', dest='serial_port', help="serial port to be used as input")
    cmdline_parser.add_argument('--query', action='store_true', default=False, dest='query_config', help="dump module configuration (serial required!)")
    cmdline_parser.add_argument('--config', action='store_true', default=False, dest='set_config', help="run module configuration sequence (serial required!)")
    cmdline_parser.add_argument('--coldstart', action='store_true', default=False, dest='coldstart', help="force a module coldstart (serial required!)")
    cmdline_parser.add_argument('--duration', action='store', default=0, dest='duration', help="run the the capture for DURATION seconds (serial required!)", type=int)
    args = cmdline_parser.parse_args()
    

    lat_list = list()
    lon_list = list()
    #read_serial("COM8")
    #read("input_data.txt")
    #read("L86_data.txt")
    
    if args.input_file:
        logging.info("Using file [" + args.input_file + "] as input")
        read(args.input_file)
    elif args.serial_port:
        logging.info("Using serial comm [" + args.serial_port + "] as input")
        try:
            com = serial.Serial(args.serial_port, timeout=5.0, baudrate=9600)
        except serial.SerialException:
            logging.error('could not connect to %s' % args.serial_port)
            time.sleep(5.0)
            exit(1)
        
        if args.coldstart:
            force_coldstart_on_module(com)

        if args.query_config:
            logging.info("Just dumping module configuration")
            dump_module_configuration(com)
            com.close()
            exit(1)
        else:
            if args.set_config:
                logging.fatal("Not supported yet!")
                exit(1)
                            
            read_serial(com, args.duration)
            com.close()
    else:
        logging.fatal("No input method selected, please specify a file or a serial")
        exit(1)

    # GoogleMapPlotter return Map object 
    # Pass the center latitude and 
    # center longitude 
    logging.info("Generating [" + args.map_file + "]")
    gmap = gmplot.GoogleMapPlotter(lat_list[0], lon_list[0],19 )
    gmap.coloricon = "http://www.googlemapsmarkers.com/v1/%s/" 
    gmap.scatter( lat_list, lon_list, '# FF0000', size = 0.5, marker = False ) 
    #plot the last one in red
    logging.info("Market at lat[" + str(lat_list[-1]) +"]\tlon[" + str(lon_list[-1]) + "]")
    gmap.marker(lat_list[-1], lon_list[-1], 'red') 
    # Pass the absolute path 
    gmap.draw( args.map_file )
