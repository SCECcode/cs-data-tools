#!/usr/bin/env python3

import sys
import os
import argparse
import datetime

#Add directory level to path to find imports
full_path = os.path.abspath(sys.argv[0])
path_add = os.path.dirname(full_path)
sys.path.append(path_add)

import filt_gen.run_filter_generator
import query_build.run_query_builder
import db_wrapper.run_database_wrapper
import data_collector.run_data_collector
import utils.utilities as utilities

def parse_args():
    parser = argparse.ArgumentParser(prog='CyberShake Data Access Tool', description='Performs CyberShake data retrieval.')
    parser.add_argument('-n', "--request-label", dest='request_label', action='store', default=None, help="Label identifying the request (optional).")
    parser.add_argument('-fl', '--filter-list', dest='print_filters', action='store_true', default=False, help="Print information about available filters and exit.")
    parser.add_argument('-pl', '--products-list', dest='print_products', action='store_true', default=False, help="Print information about available data products and exit.")
    parser.add_argument('-c', "--config-filename", dest='config_filename', action='store', default='src/db_wrapper/focal.cfg', help="Path to database configuration file (optional, default: focal.cfg)")
    parser.add_argument('-o', '--output-directory', dest='output_directory', action='store', default=".", help="Path to output directory to store files in (optional, default is current working directory).")
    parser.add_argument('-t', '--temp-directory', dest='temp_directory', action='store', default=".", help="Path to temporary directory to store files before extraction (optional, default is current working directory).")
    parser.add_argument('-i', '--input-filename', dest='input_filename', action='store', default=None, help="Path to JSON file describing desired data products and filters to apply, in format outputted by Filter Generator step.  If supplied, Filter Generator is bypassed.  (optional)")
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Turn on debug statements.')
    parser.add_argument('-v', '--version', dest='version', action='store_true', default=False, help="Show version number and exit.")
    args_dict = dict()
    args = parser.parse_args()
    if args.version==True:
        print("Version: %s" % utilities.get_version())
        sys.exit(utilities.ExitCodes.NO_ERROR)
    if args.request_label is not None:
        args_dict['request_label'] = args.request_label
    else:
        dt_tuple = datetime.datetime.now().timetuple()
        args_dict['request_label'] = "%02d%02d%02d_%02d%02d%04d" % (dt_tuple.tm_hour, dt_tuple.tm_min, dt_tuple.tm_sec, dt_tuple.tm_mon, dt_tuple.tm_mday, dt_tuple.tm_year)
    if args.print_filters is True:
        args_dict['print_filters'] = True
    else:
        args_dict['print_filters'] = False
    if args.print_products is True:
        args_dict['print_products'] = True
    else:
        args_dict['print_products'] = False
    args_dict['config_filename'] = args.config_filename
    args_dict['output_directory'] = args.output_directory
    args_dict['temp_directory'] = args.temp_directory
    args_dict['input_filename'] = args.input_filename
    args_dict['debug'] = args.debug
    return args_dict

def run_filter_generator(args_dict):
    arg_string = ""
    if args_dict['print_filters']==True:
        arg_string = "%s -fl" % arg_string
    if args_dict['print_products']==True:
        arg_string = "%s -pl" % arg_string
    if args_dict['debug']==True:
        arg_string = "%s -d" % arg_string
    arg_string = "%s -o csdata.%s.json" % (arg_string, args_dict['request_label'])
    print(arg_string)
    filt_gen.run_filter_generator.run_main(arg_string.split())

def run_query_builder(args_dict):
    if args_dict['input_filename'] is not None:
        arg_string = '-i %s' % (args_dict['input_filename'])
    else:
        arg_string = '-i csdata.%s.json' % (args_dict['request_label'])
    if args_dict['debug']==True:
        arg_string = "%s -d" % arg_string
    arg_string = "%s -o csdata.%s.query" % (arg_string, args_dict['request_label'])
    query_build.run_query_builder.run_main(arg_string.split())

def run_database_wrapper(args_dict):
    arg_string = "-i csdata.%s.query -o csdata.%s.data -c %s" % (args_dict['request_label'], args_dict['request_label'], args_dict['config_filename'])
    if args_dict['debug']==True:
        arg_string = "%s -d" % arg_string
    db_wrapper.run_database_wrapper.run_main(arg_string.split())

def run_data_collector(args_dict, url_file):
    arg_string = "-i %s -o %s -t %s" % (url_file, args_dict['output_directory'], args_dict['temp_directory'])
    if args_dict['debug']==True:
        arg_string = "%s -d" % arg_string
    data_collector.run_data_collector.run_main(arg_string.split())

def run_main():
    args_dict = parse_args()
    if args_dict['input_filename'] is None:
        run_filter_generator(args_dict)
    run_query_builder(args_dict)
    run_database_wrapper(args_dict)
    url_file = 'csdata.%s.urls' % (args_dict['request_label'])
    #By checking if this file exists, we're checking both that we want seismograms and also that the storage requirements are low enough.
    if os.path.exists(url_file):
        run_data_collector(args_dict, url_file)
    print("\nData retrieval is complete!")

if __name__=='__main__':
    run_main()