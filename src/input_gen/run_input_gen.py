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

'''Non-interactive input generator for CyberShake data requests.

Reads the request variables from command-line arguments (-m/--model,
-p/--product, repeatable --filter NAME=VALUE), validates and sanitizes
them against the available models, data products, and filters
(utils.models.create_models, utils.data_products.create_data_products,
utils.filters.create_filters), and writes a JSON data request in the same
format the interactive Filter Generator would have written.

The JSON is always written to stdout (the human-readable summary goes to
stderr), so the request can be piped directly into the data-access pipeline
or redirected to a file with '>':

	src/input_gen/run_input_gen.py -m "Study 22.12 LF" -p "Site Info" --filter SITE_NAME=USC | src/retrieve_cs_data.py -i - -o ./out -t ./tmp
	src/input_gen/run_input_gen.py -m "Study 22.12 LF" -p "Site Info" --filter SITE_NAME=USC > myrequest.json
'''

import argparse
import sys
import os
import json

#Add one directory level above to path to find imports
full_path = os.path.abspath(sys.argv[0])
path_add = os.path.dirname(os.path.dirname(full_path))
sys.path.append(path_add)

import input_gen.request_env as request_env
import utils.utilities as utilities
import utils.filters as filters
import utils.data_products as data_products
import utils.models as models

model_list = None
dp_list = None
filter_list = None


class ArgumentParser(argparse.ArgumentParser):
	#Exit with INVALID_ARGUMENTS (like the other pipeline components exit
	#for bad arguments) instead of argparse's default code 2.
	def error(self, message):
		print(message, file=sys.stderr)
		self.print_usage(sys.stderr)
		sys.exit(utilities.ExitCodes.INVALID_ARGUMENTS)


def parse_args(argv):
	parser = ArgumentParser(prog='Input Generator', description='Generates a CyberShake data-request JSON file from command-line arguments, validating them against the available models, data products, and filters.')
	#Every value flag is repeatable, and may also arrive with no value token at
	#all: a web form emits hidden empty-valued elements as bare flags
	#(e.g. "--sort-by --sort-by SITE_NAME"), so nargs='?' with const='' turns
	#an argumentless flag into an empty value instead of an argparse error.
	parser.add_argument('-m', '--model', dest='model', action='append', nargs='?', const='', default=None, metavar='MODEL', help='(Required) the CyberShake model to use, e.g. "Study 22.12 LF".  Case-insensitive.')
	parser.add_argument('-p', '--product', dest='product', action='append', nargs='?', const='', default=None, metavar='PRODUCT', help='(Required) the data product to retrieve, e.g. "Site Info".  Case-insensitive.')
	parser.add_argument('--filter', dest='filters', action='append', nargs='?', const='', metavar='NAME=VALUE', default=None, help='(Optional, repeatable) filter selection, e.g. --filter SITE_NAME=USC.  NAME is a filter name in upper case with spaces replaced by underscores; append _PARAMS for the value form (1 single value, 2 multiple values, 3 range), e.g. --filter MAGNITUDE_PARAMS=3.')
	parser.add_argument('--sort-by', dest='sort_by', action='append', nargs='?', const='', default=None, metavar='NAME', help='(Optional) sort the results on one of the selected filters, e.g. --sort-by MAGNITUDE.  Use the same NAME form as --filter.')
	parser.add_argument('--sort-order', dest='sort_order', action='append', nargs='?', const='', default=None, metavar='ASC|DESC', help="(Optional) the sort direction for --sort-by (ascending or descending; defaults to ascending).")
	parser.add_argument('-e', '--input-event-filename', dest='input_event_filename', action='append', nargs='?', const='', default=None, metavar='FILENAME', help="(Optional) path to CSV file containing src id, rup id, rup var id values.  This will bypass the event filters.")
	parser.add_argument('-v', '--version', dest='version', action='store_true', default=False, help="Show version number and exit.")
	args = parser.parse_args(args=argv)
	args_dict = dict()
	if args.version==True:
		print("Version: %s" % utilities.get_version())
		sys.exit(utilities.ExitCodes.NO_ERROR)

	#Front-end forms may emit hidden elements carrying empty values, so any
	#flag may arrive multiple times.  Keep the last non-blank value for each.
	def last_non_empty(values, flag_name):
		cleaned = list()
		for value in values:
			value = request_env.strip_value(value)
			if len(value)>0:
				cleaned.append(value)
		if len(cleaned)==0:
			return None
		unique = set(cleaned)
		if len(unique)>1:
			request_env.warn("Multiple values given for %s; the last one will be used." % flag_name)
		return cleaned[-1]

	#Collect the --filter entries into a dict; the last value for a given
	#name wins.  Blank values (empty, quoted-empty, or whitespace-only, e.g.
	#from hidden form elements) are silently dropped.
	filter_vars = dict()
	if args.filters is not None:
		for entry in args.filters:
			if len(entry)==0:
				#A bare --filter (no value token) carries no selection
				continue
			key, value = request_env.parse_filter_entry(entry)
			if len(value)==0:
				continue
			if key in filter_vars:
				request_env.warn("Multiple values given for --filter %s; the last one will be used." % key)
			filter_vars[key] = value
	args_dict['filters'] = filter_vars
	model = last_non_empty(args.model or [], '-m/--model')
	if model is not None:
		args_dict['model'] = model
	product = last_non_empty(args.product or [], '-p/--product')
	if product is not None:
		args_dict['product'] = product
	sort_by = last_non_empty(args.sort_by or [], '--sort-by')
	if sort_by is not None:
		args_dict['sort_by'] = sort_by
	sort_order = last_non_empty(args.sort_order or [], '--sort-order')
	if sort_order is not None:
		args_dict['sort_order'] = sort_order
	input_event_filename = last_non_empty(args.input_event_filename or [], '-e/--input-event-filename')
	if input_event_filename is not None:
		args_dict['input_event_filename'] = input_event_filename
	return args_dict


def load_data():
	global model_list, dp_list, filter_list
	dp_list = data_products.create_data_products()
	if len(dp_list)==0:
		print("No data products available, aborting.", file=sys.stderr)
		sys.exit(utilities.ExitCodes.NO_DATAPRODUCTS)
	model_list = models.create_models(dp_list)
	if len(model_list)==0:
		print("No models available, aborting.", file=sys.stderr)
		sys.exit(utilities.ExitCodes.NO_MODELS)
	filter_list = filters.create_filters()
	if len(filter_list)==0:
		print("No filters available, aborting.", file=sys.stderr)
		sys.exit(utilities.ExitCodes.NO_FILTERS)


def canonicalize_model(raw):
	for m in model_list:
		if request_env.normalize(m.get_name())==request_env.normalize(raw):
			return m
	if len(request_env.normalize(raw))==0:
		request_env.die(utilities.ExitCodes.NO_MODELS, "No model specified.")
	supported = ", ".join(m.get_name() for m in model_list)
	request_env.die(utilities.ExitCodes.NO_MODELS, "Unknown model '%s'.  Supported models are %s." % (raw, supported))


def canonicalize_product(raw):
	for d in dp_list:
		if request_env.normalize(d.get_name())==request_env.normalize(raw):
			return d
	request_env.die(utilities.ExitCodes.INVALID_ARGUMENTS, "Unknown data product '%s'.  Valid products are %s." % (raw, ", ".join(d.get_name() for d in dp_list)))


def build_request(args_dict):
	'''Read and validate the request variables, and return
	(selected_model, selected_dp, selected_filters, event_list).'''
	filter_vars = args_dict['filters']

	#Model and data product are required.
	model_raw = args_dict.get('model', '')
	if len(model_raw)==0:
		request_env.die(utilities.ExitCodes.MISSING_ARGUMENTS, "No model specified (-m/--model).  Please specify the CyberShake model to use.")
	selected_model = canonicalize_model(model_raw)

	product_raw = args_dict.get('product', '')
	if len(product_raw)==0:
		request_env.die(utilities.ExitCodes.MISSING_ARGUMENTS, "No data product specified (-p/--product).  Please specify the data product to retrieve.")
	selected_dp = canonicalize_product(product_raw)
	if selected_dp not in selected_model.get_data_products():
		available = ", ".join(d.get_name() for d in selected_model.get_data_products())
		request_env.die(utilities.ExitCodes.NO_DATAPRODUCTS, "The %s data product is not available for %s.  Available products: %s." % (selected_dp.get_name(), selected_model.get_name(), available))

	#Inject the model's periods into the enumerated Intensity Measure
	#Period filter, as the interactive tool does before offering filters.
	for f in filter_list:
		if isinstance(f, filters.EnumeratedFilter) and f.get_values_list() is None:
			f.set_values_list(selected_model.get_periods())

	#Unknown filter variables: a value referencing a filter which does
	#not exist is an error.
	suffix_map = dict()
	for f in filter_list:
		suffix_map[request_env.env_suffix(f.get_name())] = f
	for key in sorted(filter_vars.keys()):
		base = key
		if base.endswith('_PARAMS') or base.endswith('_SORT'):
			base = base.rsplit('_', 1)[0]
		if base not in suffix_map:
			valid = ", ".join(f.get_name() for f in filter_list)
			request_env.die(utilities.ExitCodes.INVALID_ARGUMENTS, "Unknown filter variable %s.  Valid filters for %s are: %s." % (key, selected_model.get_name(), valid))
		if key.endswith('_SORT'):
			request_env.die(utilities.ExitCodes.INVALID_ARGUMENTS, "--filter %s is no longer supported.  Use --sort-by %s and --sort-order ASC|DESC." % (key, base))

	#Collect and validate the selected filters, in the order the filters
	#are defined in utils.filters.create_filters().
	selected_filters = []
	for f in filter_list:
		suffix = request_env.env_suffix(f.get_name())
		rawval = filter_vars.get(suffix, '')
		params_raw = filter_vars.get('%s_PARAMS' % suffix, '')

		if len(rawval)==0:
			if len(params_raw)>0:
				request_env.warn("--filter %s_PARAMS is set, but --filter %s has no value; ignoring." % (suffix, suffix))
			continue

		if f.get_data_product() not in selected_dp.get_relevant_filters():
			applicable = ", ".join(d.get_name() for d in dp_list if f.get_data_product() in d.get_relevant_filters() and d in selected_model.get_data_products())
			request_env.die(utilities.ExitCodes.INVALID_ARGUMENTS, "The %s filter cannot be applied to the %s data product.  Applicable products: %s." % (f.get_name(), selected_dp.get_name(), applicable))

		request_env.validate_and_apply(f, rawval, params_raw)
		selected_filters.append(f)

	#Required-filter dependencies.
	for f in selected_filters:
		for req in f.get_required_filters():
			if req not in selected_filters:
				request_env.die(utilities.ExitCodes.MISSING_ARGUMENTS, "Since you selected the %s filter, you also need to use the %s filter." % (f.get_name(), req.get_name()))

	#Sort: one of the selected filters may be chosen to sort the results on,
	#mirroring the interactive tool, which offers a single sort choice.
	sort_by = args_dict.get('sort_by', '')
	sort_order = args_dict.get('sort_order', '')
	if len(sort_order)>0 and len(sort_by)==0:
		#A hidden form element may emit a sort direction with no sort filter;
		#warn and generate the request without sorting.
		request_env.warn("--sort-order is set, but --sort-by is not; ignoring sort.")
		sort_order = ''
	if len(sort_by)>0:
		sort_filter = None
		for f in selected_filters:
			if request_env.env_suffix(f.get_name())==sort_by:
				sort_filter = f
				break
		if sort_filter is None:
			#Distinguish an unselected filter from an unknown one
			for f in filter_list:
				if request_env.env_suffix(f.get_name())==sort_by:
					request_env.die(utilities.ExitCodes.INVALID_ARGUMENTS, "The %s filter is not selected, so the results cannot be sorted on it." % f.get_name())
			valid = ", ".join(f.get_name() for f in filter_list)
			request_env.die(utilities.ExitCodes.INVALID_ARGUMENTS, "Unknown sort filter %s.  Valid filters for %s are: %s." % (sort_by, selected_model.get_name(), valid))
		if len(sort_order)==0:
			sort_order = 'asc'
		sortval = request_env.parse_sort(sort_order, sort_filter.get_name())
		sort_filter.set_sort(sortval)

	#Event list.
	event_list = None
	event_path = args_dict.get('input_event_filename', '')
	if len(event_path)>0:
		event_list = request_env.parse_event_list(event_path)
		#The interactive tool does not prompt for event filters when an
		#event list is provided; warn if the user supplied both.
		for f in selected_filters:
			if f.get_data_product()==filters.FilterDataProducts.EVENTS:
				request_env.warn("The %s filter is an event filter.  The interactive tool does not combine event filters with an event list; the request will use both." % f.get_name())

	return (selected_model, selected_dp, selected_filters, event_list)


def print_summary(selected_model, selected_dp, selected_filters, event_list, fp_out):
	#Summary, mirroring the interactive tool's request recap
	#(src/filt_gen/user_prompts.py).
	print("\nYou have generated the following data product request:\n", file=fp_out)
	print("Model:", file=fp_out)
	print("\t%s" % selected_model.get_name(), file=fp_out)
	print("\nData product:", file=fp_out)
	print("\t%s" % selected_dp.get_name(), file=fp_out)
	print("\nFilters:", file=fp_out)
	if len(selected_filters)==0:
		print("\tNone", file=fp_out)
	else:
		for s in selected_filters:
			if s.get_sort()<0:
				print("\t%s, sort descending" % s.get_filter_string(), file=fp_out)
			elif s.get_sort()>0:
				print("\t%s, sort ascending" % s.get_filter_string(), file=fp_out)
			else:
				print("\t%s" % s.get_filter_string(), file=fp_out)
	if event_list is not None:
		print("\nEvents specified in file:", file=fp_out)
		for e in event_list:
			print("\tSrc %d, Rup %d, RV %d" % (e[0], e[1], e[2]), file=fp_out)


def emit_request(selected_model, selected_dp, selected_filters, event_list):
	#Assemble the request dictionary and serialize it with the same encoder
	#the interactive Filter Generator uses, so the output format matches
	#exactly (src/filt_gen/run_filter_generator.py write_filter_file).
	request_dict = dict()
	request_dict['model'] = selected_model
	request_dict['products'] = selected_dp
	request_dict['filters'] = selected_filters
	if event_list is not None:
		request_dict['event_list'] = event_list
	json_obj = json.dumps(request_dict, cls=utilities.CSJSONEncoder, indent=4)

	#The JSON goes to stdout, the summary to stderr, so a pipe (or the main
	#application reading our stdout) carries only the JSON.
	print_summary(selected_model, selected_dp, selected_filters, event_list, sys.stderr)
	print(json_obj)


def run_main(argv):
	args_dict = parse_args(argv)
	load_data()
	(selected_model, selected_dp, selected_filters, event_list) = build_request(args_dict)
	emit_request(selected_model, selected_dp, selected_filters, event_list)


if __name__=='__main__':
	run_main(sys.argv[1:])