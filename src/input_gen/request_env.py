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

'''Request-variable parsing and validation for the non-interactive
input generator.

The request variables are supplied as command-line arguments; filter
selections use the --filter NAME=VALUE grammar, where NAME is a filter
name in suffix form with optional _PARAMS or _SORT appended.'''

import re
import sys

import utils.utilities as utilities
import utils.filters as filters

#Env-file grammar: KEY=VALUE, with the key matching a Python identifier
ENV_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
#Strict numeric literal: optional sign, digits, optional decimal and exponent
#(rejects nan, inf, hex, etc.)
FLOAT_RE = re.compile(r"^-?[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?$")
INT_RE = re.compile(r"^-?[0-9]+$")
#Characters not allowed in string filter values
BAD_STRING_CHARS = re.compile(r'["\\,|&$`()<>;]')


def warn(msg):
	print("WARNING: %s" % msg, file=sys.stderr)


def die(code, msg):
	print(msg, file=sys.stderr)
	sys.exit(code)


def has_control_chars(s):
	for c in s:
		if ord(c)<32 or ord(c)==127:
			return True
	return False


def strip_value(raw):
	'''Normalize an argument value: strip surrounding whitespace, remove one
	pair of matching surrounding quotes if present (values may arrive with
	literal quotes from a front-end form), then strip whitespace again.'''
	raw = raw.strip()
	if len(raw)>=2 and raw[0]==raw[-1] and raw[0] in '"\'':
		raw = raw[1:-1].strip()
	return raw


def parse_filter_entry(entry):
	'''Parse one --filter KEY=VALUE argument into (key, value).  The key is
	a filter name in suffix form, with optional _PARAMS or _SORT appended.
	Splits on the first '=' only; values may contain '='.'''
	if '=' not in entry:
		die(utilities.ExitCodes.INVALID_ARGUMENTS, "Malformed --filter argument '%s'.  Use the form --filter NAME=VALUE, e.g. --filter SITE_NAME=USC." % entry)
	key, value = entry.split('=', 1)
	#Tolerate a FILTER_ prefix if the user carried it over from the old grammar
	if key.startswith('FILTER_'):
		key = key[len('FILTER_'):]
	if len(key)==0:
		die(utilities.ExitCodes.INVALID_ARGUMENTS, "Malformed --filter argument '%s': the filter name is empty." % entry)
	value = strip_value(value)
	if has_control_chars(value):
		die(utilities.ExitCodes.INVALID_ARGUMENTS, "Control character in value of --filter %s." % key)
	return (key, value)


def normalize(raw):
	'''Normalize a model or data product name for comparison: lowercase,
	with spaces, tabs, underscores, and hyphens removed, and a leading
	"study" dropped.'''
	norm = raw.lower()
	norm = norm.replace(' ', '').replace('\t', '').replace('_', '').replace('-', '')
	if norm.startswith('study'):
		norm = norm[5:]
	return norm


def env_suffix(name):
	'''The --filter variable suffix for a filter, e.g.
	"Site-Rupture Distance" -> "SITE_RUPTURE_DISTANCE".'''
	return re.sub(r'[ -]', '_', name).upper()


def split_values(raw, is_numeric):
	'''Split a raw value string into tokens.  Numeric filters split on
	commas and/or whitespace; string filters split on commas only, so
	values with spaces in them ("San Andreas") stay one value.'''
	if is_numeric:
		pieces = re.split(r'[ \t,]+', raw)
	else:
		pieces = raw.split(',')
	return [p.strip() for p in pieces if len(p.strip())>0]


def validate_and_apply(filt, rawval, params_raw):
	'''Validate the value(s) of one selected filter against the filter
	object's own metadata (type, enum list, or range), then apply them to
	the object.  Exits with the appropriate ExitCodes value on error.'''
	name = filt.get_name()
	suffix = env_suffix(name)
	is_numeric = filt.is_numeric()
	raw_values = split_values(rawval, is_numeric)
	if len(raw_values)==0:
		die(utilities.ExitCodes.INVALID_ARGUMENTS, "No valid values provided for the %s filter." % name)

	#Value form (filter_params)
	if len(params_raw)==0:
		if len(raw_values)!=1:
			die(utilities.ExitCodes.MISSING_ARGUMENTS, "The %s filter has %d values, but --filter %s_PARAMS is not set.  Please specify 1 (single value), 2 (multiple values), or 3 (value range)." % (name, len(raw_values), suffix))
		params = 1
	else:
		params_text = params_raw.strip()
		if params_text not in ('1', '2', '3'):
			die(utilities.ExitCodes.INVALID_ARGUMENTS, "--filter %s_PARAMS must be 1 (single value), 2 (multiple values), or 3 (value range), not '%s'." % (suffix, params_text))
		params = int(params_text)
	#A range is only allowed for numeric filters (checked before
	#cardinality, so a range request on a string filter exits with
	#INVALID_ARGUMENTS regardless of how many values were given)
	if params==3 and not is_numeric:
		die(utilities.ExitCodes.INVALID_ARGUMENTS, "You can't specify a range for a filter which is a string type (the %s filter)." % name)
	#Cardinality
	if params==1 and len(raw_values)!=1:
		die(utilities.ExitCodes.MISSING_ARGUMENTS, "The %s filter has %d value(s), but filter_params 1 (single value) requires exactly one value." % (name, len(raw_values)))
	if params==2 and len(raw_values)<2:
		die(utilities.ExitCodes.MISSING_ARGUMENTS, "The %s filter has %d value(s), but filter_params 2 (multiple values) requires at least two values." % (name, len(raw_values)))
	if params==3 and len(raw_values)!=2:
		die(utilities.ExitCodes.MISSING_ARGUMENTS, "The %s filter has %d value(s), but filter_params 3 (value range) requires exactly two values." % (name, len(raw_values)))

	#Per-value validation and casting
	values = []
	if isinstance(filt, filters.EnumeratedFilter):
		#Enumerated filter: values must be members of the filter's list
		#(the model's periods, injected before this call).  PGV/PGA are
		#strings and can only be used as a single value.
		for tok in raw_values:
			if tok.upper()=='PGV' or tok.upper()=='PGA':
				if params!=1:
					die(utilities.ExitCodes.INVALID_ARGUMENTS, "Currently we don't support combining %s with other intensity measures.  Please submit separate data requests instead." % tok.upper())
				values.append(tok.upper())
			elif FLOAT_RE.match(tok):
				value_obj = filt.get_type()(tok)
				if value_obj not in filt.get_values_list():
					die(utilities.ExitCodes.VALUE_OUT_OF_RANGE, "%s isn't a possible value for the %s filter." % (tok, name))
				values.append(value_obj)
			else:
				die(utilities.ExitCodes.VALUE_OUT_OF_RANGE, "%s isn't a possible value for the %s filter." % (tok, name))
	elif is_numeric:
		#Range filter: values must be numbers within the filter's bounds
		(min_val, max_val) = filt.get_range()
		for tok in raw_values:
			if not FLOAT_RE.match(tok):
				die(utilities.ExitCodes.INVALID_ARGUMENTS, "The %s filter requires values of type float.  '%s' is not a number." % (name, tok))
			value_obj = filt.get_type()(tok)
			if value_obj<min_val or value_obj>max_val:
				die(utilities.ExitCodes.VALUE_OUT_OF_RANGE, "The %s filter can only take values [%s, %s]." % (name, str(min_val), str(max_val)))
			values.append(value_obj)
	else:
		#String filter
		for tok in raw_values:
			if has_control_chars(tok):
				die(utilities.ExitCodes.INVALID_ARGUMENTS, "Control character in value for the %s filter." % name)
			if BAD_STRING_CHARS.search(tok):
				die(utilities.ExitCodes.INVALID_ARGUMENTS, "The value '%s' for the %s filter contains a character which is not allowed." % (tok, name))
			values.append(tok)

	#Apply to the filter object; its own validators re-check the values.
	#The values must be set on the object so it can be serialized with the
	#same encoder the interactive tool uses.
	if params==1:
		return_code = filt.set_value(values[0])
	elif params==2:
		return_code = filt.set_values(values)
	else:
		return_code = filt.set_value_range(values[0], values[1])
	if return_code!=0:
		#The object's own validation rejected the values; it has already
		#printed its message.
		die(utilities.ExitCodes.VALUE_OUT_OF_RANGE, "Invalid value(s) for the %s filter." % name)


def parse_sort(sort_raw, name):
	'''Parse a --sort-order value for the filter with the given name;
	returns 0, 1, or -1.'''
	if len(sort_raw)==0:
		return 0
	sort_text = sort_raw.strip().lower()
	if sort_text=='1' or sort_text=='asc' or sort_text=='ascending':
		return 1
	if sort_text=='-1' or sort_text=='desc' or sort_text=='descending':
		return -1
	die(utilities.ExitCodes.VALUE_OUT_OF_RANGE, "'%s' is not a valid sort order for the %s filter.  Use 1 (ascending) or -1 (descending)." % (sort_raw, name))


def parse_event_list(path):
	'''Parse a CSV event list of src,rup,rv lines into a list of
	[int, int, int] triples.'''
	try:
		fp_in = open(path, 'r', encoding='utf-8-sig')
		lines = fp_in.readlines()
		fp_in.close()
	except OSError:
		die(utilities.ExitCodes.BAD_FILE_PATH, "Error reading from input file %s, aborting." % path)
	events = []
	for line in lines:
		line = line.strip()
		if len(line)==0:
			continue
		pieces = line.split(',')
		valid = len(pieces)==3
		if valid:
			for p in pieces:
				if not INT_RE.match(p.strip()):
					valid = False
		if not valid:
			die(utilities.ExitCodes.FILE_PARSING_ERROR, "Error parsing CSV event list file %s.\nThis file should be in the format <src id>,<rup id>,<rup var id>.  Offending line: %s" % (path, line))
		events.append([int(pieces[0]), int(pieces[1]), int(pieces[2])])
	if len(events)>utilities.MAX_EVENT_LIST_LENGTH:
		die(utilities.ExitCodes.FILE_PARSING_ERROR, "The event file %s contains %d events, which is greater than the maximum allowed event list length of %d." % (path, len(events), utilities.MAX_EVENT_LIST_LENGTH))
	return events