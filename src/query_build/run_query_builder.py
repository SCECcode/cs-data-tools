#!/usr/bin/env python3

"""
BSD 3-Clause License

Copyright (c) 2023, University of Southern California
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.
   
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import sys
import os
import argparse
import json
import datetime

#Add one directory level above to path to find imports
full_path = os.path.abspath(sys.argv[0])
path_add = os.path.dirname(os.path.dirname(full_path))
sys.path.append(path_add)

import query_build.query_constructor as query_constructor
import utils.utilities as utilities
import utils.filters as filters
import utils.data_products as data_products
import utils.models as models

model_list = None
dp_list = None
filter_list = None

def parse_args(argv):
    parser = argparse.ArgumentParser(prog='Query Builder', description='Takes CyberShake data request and constructs database queries required to fulfill it.')
    parser.add_argument('-i', '--input-filename', dest='input_filename', action='store', default=None, help="Path to JSON file describing the data request.")
    parser.add_argument('-o', '--output-filename', dest='output_filename', action='store', default=None, help="Path to output file containing queries.")
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Turn on debug statements.')
    parser.add_argument('-v', '--version', dest='version', action='store_true', default=False, help="Show version number and exit.")
    args = parser.parse_args(args=argv)
    if args.version==True:
        print("Version: %s" % utilities.get_version())
        sys.exit(utilities.ExitCodes.NO_ERROR)
    if args.input_filename is None:
        print("Path to input file must be provided, aborting.", file=sys.stderr)
        sys.exit(utilities.ExitCodes.MISSING_ARGUMENTS)
    input_filename = args.input_filename
    if args.output_filename is None:
        dt_tuple = datetime.datetime.now().timetuple()
        output_filename = "csdata.%02d%02d%02d_%02d%02d%04d.query" % (dt_tuple.tm_hour, dt_tuple.tm_min, dt_tuple.tm_sec, dt_tuple.tm_mon, dt_tuple.tm_mday, dt_tuple.tm_year)
    else:
        output_filename = args.output_filename
    return (input_filename, output_filename)
	
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

def parse_json(input_filename):
    try:
          fp_in = open(input_filename, 'r')
          json_dict = json.load(fp_in)
    except Exception as e:
          print("Error parsing JSON file %s, aborting." % input_filename)
          print(e)
          sys.exit(utilities.ExitCodes.FILE_PARSING_ERROR)
    model_name = json_dict['model']['name']
    for m in model_list:
        if m.get_name()==model_name:
            model_selected = m
            break
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
                    #Update valid IM values based on model
                    if f.get_name()=='Intensity Measure Period':
                        #Update with periods from model
                        f.set_values_list(model_selected.get_periods())
                    if 'sort' in filt:
                        sort = filt['sort']
                        f.set_sort(sort)
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
                        selected_filt.set_value_range(values[0], values[1])
                    filters_selected.append(selected_filt)
    event_list = None
    if 'event_list' in json_dict:
        #We specified a list of specific events
        event_list = []
        for e in json_dict['event_list']:
            event_list.append(e)
    if dp_selected is None:
          print("Couldn't find a valid data product in JSON file %s, aborting." % input_filename)
          sys.exit(utilities.ExitCodes.FILE_PARSING_ERROR)
    return (model_selected, dp_selected, filters_selected, event_list)

def write_queries(query, input_filename, output_filename, dp_name):
    with open(output_filename, 'w') as fp_out:
        distinct_string = ""
        if query.get_distinct()==True:
            distinct_string = "distinct"
        fp_out.write("select = %s %s\n" % (distinct_string, query.get_select_string()))
        fp_out.write("from = %s\n" % query.get_from_string())
        fp_out.write("where = %s\n" % query.get_where_string())
        if (query.get_sort()!=""):
            fp_out.write("sort = %s\n" % query.get_sort())
        fp_out.write("data_request_file = %s\n" % input_filename)
        fp_out.write("data_product = %s\n" % dp_name)
        fp_out.flush()
        fp_out.close()

def run_main(argv):
    (input_filename, output_filename) = parse_args(argv)
    load_data()
    (model_selected, dp_selected, filters_selected, event_list) = parse_json(input_filename)
    query = query_constructor.construct_queries(model_selected, dp_selected, filters_selected, event_list)
    write_queries(query, input_filename, output_filename, dp_selected.get_name())
    print("\nYour database queries were written to %s." % output_filename)

if __name__=="__main__":
    run_main(sys.argv[1:])
    sys.exit(0)