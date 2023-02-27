#!/usr/bin/env python3

'''Filter Generator, which gets information from user about what data products and filters to apply in retrieving CyberShake data.'''

import argparse
import sys
import os
import json

import filters
import data_products
import user_prompts

#Add one directory level above to path to find imports
full_path = os.path.abspath(sys.argv[0])
path_add = os.path.dirname(os.path.dirname(full_path))
sys.path.append(path_add)

import utils

dp_list = None
filter_list = None

def parse_args():
	parser = argparse.ArgumentParser(prog='Filter Generator', description='Gets information from user about CyberShake data retrieval request.')

def load_data():
	global dp_list, filter_list
	dp_list = data_products.create_data_products()
	if len(dp_list)==0:
		print("No data products available, aborting.", file=sys.stderr)
		sys.exit(utils.ExitCodes.NO_DATAPRODUCTS)
	filter_list = filters.create_filters()
	if len(filter_list)==0:
		print("No filters available, aborting.", file=sys.stderr)
		sys.exit(utils.ExitCodes.NO_FILTERS)

def prompt_user():
	user_prompts.get_user_input(dp_list, filter_list)

def write_filter_file():
	pass

def run_main():
	parse_args()
	load_data()
	prompt_user()
	write_filter_file()

if __name__=="__main__":
	run_main()
