#!/usr/bin/env python3

'''Filter Generator, which gets information from user about what data products and filters to apply in retrieving CyberShake data.'''

import argparse
import sys
import os
import json
import datetime

#Add one directory level above to path to find imports
full_path = os.path.abspath(sys.argv[0])
path_add = os.path.dirname(os.path.dirname(full_path))
sys.path.append(path_add)

import filt_gen.user_prompts as user_prompts
import utils.utilities as utilities
import utils.filters as filters
import utils.data_products as data_products
import utils.models as models

model_list = None
dp_list = None
filter_list = None

def parse_args(argv):
	parser = argparse.ArgumentParser(prog='Filter Generator', description='Gets information from user about CyberShake data retrieval request.')
	parser.add_argument('-fl', '--filter-list', dest='print_filters', action='store_true', default=False, help="Print information about available filters and exit.")
	parser.add_argument('-pl', '--products-list', dest='print_products', action='store_true', default=False, help="Print information about available data products and exit.")
	parser.add_argument('-o', '--output-filename', dest='output_filename', action='store', default=None, help="Path to JSON file describing the data request.")
	parser.add_argument('-no', '--no-output-file', dest='write_output', action='store_false', default=True, help="Don't write an output JSON file.")
	parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Turn on debug statements.')
	parser.add_argument('-v', '--version', dest='version', action='store_true', default=False, help="Show version number and exit.")
	args = parser.parse_args(args=argv)
	exit = False
	args_dict = dict()
	if args.print_filters==True:
		exit = True
		load_data()
		print("These are the available filters.\n")
		for f in filter_list:
			print("\t%s: %s" % (f.get_name(), f.get_help_string()))
	if args.print_products==True:
		exit = True
		load_data()
		print("These are the available data products.\n")
		for d in dp_list:
			print("\t%s: %s" % (d.get_name(), d.get_help_string()))
	if args.version==True:
		exit = True
		print("Version: %s" % utilities.get_version())
	if exit==True:
		sys.exit(utilities.ExitCodes.NO_ERROR)
	if args.output_filename is not None:
		if args.write_output is False:
			print("Both --output-filename and --no-output-file were specified.  Please only select one.  Aborting.")
			sys.exit(utilities.ExitCodes.INVALID_ARGUMENTS)
		output_filename = args.output_filename
		#Add json extension
		if output_filename[-5:]!='.json':
			output_filename = "%s.json" % output_filename
	elif args.write_output is True:
		dt_tuple = datetime.datetime.now().timetuple()
		output_filename = "csdata.%02d%02d%02d_%02d%02d%04d.json" % (dt_tuple.tm_hour, dt_tuple.tm_min, dt_tuple.tm_sec, dt_tuple.tm_mon, dt_tuple.tm_mday, dt_tuple.tm_year)
	else:
		#args.write_output is false, and output_filename wasn't set
		output_filename = None
	args_dict['output_filename'] = output_filename
	return args_dict


def load_data():
	global model_list, dp_list, filter_list
	model_list = models.create_models()
	if len(model_list)==0:
		print("No models available, aborting.", file=sys.stderr)
		sys.exit(utilities.ExitCodes.NO_MODELS)
	dp_list = data_products.create_data_products()
	if len(dp_list)==0:
		print("No data products available, aborting.", file=sys.stderr)
		sys.exit(utilities.ExitCodes.NO_DATAPRODUCTS)
	filter_list = filters.create_filters()
	if len(filter_list)==0:
		print("No filters available, aborting.", file=sys.stderr)
		sys.exit(utilities.ExitCodes.NO_FILTERS)

def prompt_user():
	return user_prompts.get_user_input(model_list, dp_list, filter_list)

def write_filter_file(selected_model, selected_dp, selected_filters, output_filename):
	if output_filename is None:
		#Don't write a file
		return
	
	#Assemble dictionary
	request_dict = dict()
	request_dict['model'] = selected_model
	request_dict['products'] = selected_dp
	request_dict['filters'] = selected_filters

	json_obj = json.dumps(request_dict, cls=utilities.CSJSONEncoder, indent=4)

	with open(output_filename, 'w') as fp_out:
		fp_out.write(json_obj)
		fp_out.flush()
		fp_out.close()

def run_main(argv):
	args_dict = parse_args(argv)
	load_data()
	(selected_model, selected_dp, selected_filters) = prompt_user()
	write_filter_file(selected_model, selected_dp, selected_filters, args_dict['output_filename'])
	print("\nYour data request was written to %s." % args_dict['output_filename'])

if __name__=="__main__":
	run_main(sys.argv[1:])
	sys.exit(0)
