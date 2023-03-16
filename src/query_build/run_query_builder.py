#!/usr/bin/env python3

import sys
import os
import argparse
import json

#Add one directory level above to path to find imports
full_path = os.path.abspath(sys.argv[0])
path_add = os.path.dirname(os.path.dirname(full_path))
sys.path.append(path_add)

import utils.utilities as utilities
import utils.filters as filters
import utils.data_products as data_products

dp_list = None
filter_list = None

class Query:
     
    def __init__(self):
        self.select_fields = set()
        self.from_tables = set()
        self.where_fields = set()

    def add_select(self, select_fields):
        for s in select_fields:
            self.select_fields.add(s)

    def add_from(self, from_fields):
        for f in from_fields:
            self.from_tables.add(f)

    def add_where(self, where_fields):
        for w in where_fields:
            self.where_fields.add(w)

    def get_query_string(self):
        return "select %s from %s where %s" % (",".join(list(self.select_fields)), ",".join(list(self.from_tables)), ",".join(list(self.where_fields)))

def parse_args():
    parser = argparse.ArgumentParser(prog='Query Builder', description='Takes CyberShake data request and constructs database queries required to fulfill it.')
    parser.add_argument('-i', '--input-filename', dest='input_filename', action='store', default=None, help="Path to JSON file describing the data request.")
    args = parser.parse_args()
    if args.input_filename is None:
         print("Path to input file must be provided, aborting.", file=sys.stderr)
         sys.exit(utilities.ExitCodes.MISSING_ARGUMENTS)
    input_filename = args.input_filename
    return input_filename
	
def load_data():
	global dp_list, filter_list
	dp_list = data_products.create_data_products()
	if len(dp_list)==0:
		print("No data products available, aborting.", file=sys.stderr)
		sys.exit(utilities.ExitCodes.NO_DATAPRODUCTS)
	filter_list = filters.create_filters()
	if len(filter_list)==0:
		print("No filters available, aborting.", file=sys.stderr)
		sys.exit(utilities.ExitCodes.NO_FILTERS)

def parse_json(input_filename):
    try:
          fp_in = open(input_filename, 'r')
          json_dict = json.load(fp_in)
    except:
          print("Error parsing JSON file %s, aborting." % input_filename)
          sys.exit(utilities.ExitCodes.FILE_PARSING_ERROR)
    dp_name = json_dict['products']['name']
    dp_selected = None
    for d in dp_list:
          if d.get_name()==dp_name:
                dp_selected = d
                break
    filters_selected = []
    for filt in json_dict['filters']:
          name = filt['name']
          params = filt['filter_params']
          values = filt['values']
          for f in filter_list:
                if f.get_name()==name:
                    selected_filt = f
                    if params==filters.FilterParams.SINGLE_VALUE:
                        if len(values)>1:
                            print("filter_params for the filter %s specifies %s, so only one value should be given in the 'values' field in the input file %s.  Aborting." % (f.get_name(), filters.FilterParams.get_text(params), input_filename))
                            sys.exit(utilities.ExitCodes.FILE_PARSING_ERROR)
                        selected_filt.set_value(values[0])
                    elif params==filters.FilterParams.MULTIPLE_VALUES:
                        if len(values)<2:
                            print("filter_params for the filter %s specifies %s, so there should be more than 1 values in the 'values' field in the input file %s.  Aborting." % (f.get_name(), filters.FilterParams.get_text(params), input_filename))
                            sys.exit(utilities.ExitCodes.FILE_PARSING_ERROR)
                        selected_filt.set_values(values)
                    elif params==filters.FilterParams.VALUE_RANGE:
                        if len(values)!=2:
                            print("filter_params for the filter %s specifies %s, so there should be exactly 2 values in the 'values' field in the input file %s.  Aborting." % (f.get_name(), filters.FilterParams.get_text(params), input_filename))
                            sys.exit(utilities.ExitCodes.FILE_PARSING_ERROR)
                    filters_selected.append(selected_filt)
    if dp_selected is None:
          print("Couldn't find a valid data product in JSON file %s, aborting." % input_filename)
          sys.exit(utilities.ExitCodes.FILE_PARSING_ERROR)
    return (dp_selected, filters_selected)

def construct_queries(dp, filter_list):
    query = Query()
    (select_fields, from_tables) = dp.get_query()
    query.add_select(select_fields)
    query.add_from(from_tables)
    for f in filter_list:
        (where_fields, from_tables) = f.get_query()
        query.add_from(from_tables)
        fp = f.get_filter_params()
        if fp==filters.FilterParams.SINGLE_VALUE:
            query.add_where(["%s==%s" % (where_fields[0], f.get_value())])
        elif fp==filters.FilterParams.MULTIPLE_VALUES:
            where_clauses = []
            for v in f.get_values():
                where_clauses.append("%s==%s" % (where_fields[0], v))
            query.add_where([" or ".join(where_clauses)])
        elif fp==filters.FilterParams.VALUE_RANGE:
            (min, max) = f.get_values()
            where_clause = "%s>=%s and %s<=%s" % (where_fields[0], min, where_fields[0], max)
            query.add_where([where_clause])
    return query

def write_queries(query):
    pass

def run_main():
    input_filename = parse_args()
    load_data()
    (dp_selected, filters_selected) = parse_json(input_filename)
    query = construct_queries(dp_selected, filters_selected)
    print(query.get_query_string())
    write_queries(query)

if __name__=="__main__":
	run_main()