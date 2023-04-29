#!/usr/bin/env python3

import sys
import os
import json

VERSION = "1.0.0_04282023"

class ExitCodes:

	NO_ERROR = 0
	NO_DATAPRODUCTS = 1
	NO_FILTERS = 2
	NO_MODELS = 3
	VALUE_OUT_OF_RANGE = 4
	INVALID_ARGUMENTS = 5
	MISSING_ARGUMENTS = 6
	FILE_PARSING_ERROR = 7
	BAD_FILE_PATH = 8
	DATABASE_CONNECTION_ERROR = 9
	DATABASE_COMMAND_ERROR = 10
	FILE_WRITING_ERROR = 11


class CSJSONEncoder(json.JSONEncoder):

	def default(self, obj):
		try:
			obj_dict = obj.get_dict_representation()
		except TypeError:
			pass
		else:
			return obj_dict
		#If it's something else
		return json.JSONEncoder.default(self, obj)

#Retrieves pretty-print names for database fields
field_aliases = None

def get_field_alias(field):
	global field_aliases
	if field_aliases is None:
		#Create
		field_aliases = dict()
		field_aliases['CS_Short_Name'] = 'Site_Name'
		field_aliases['CS_Site_Lon'] = "Site_Longitude"
		field_aliases['CS_Site_Lat'] = "Site_Latitude"
		field_aliases['Prob'] = 'Probability'
		field_aliases['Mag'] = 'Magnitude'
		field_aliases['IM_Type_Value'] = 'Period'
		field_aliases['IM_Type_Component'] = 'Component'
		field_aliases['Rup_Var_ID'] = 'Rupture_Variation_ID'
	if field in field_aliases:
		return field_aliases[field]
	else:
		return field

def get_rv_seismogram_size(study_name):
	components = 2
	sizeof_float = 4
	header_size = 56
	if study_name=='Study 15.12':
		nt = 12000
	return components*nt*sizeof_float + header_size

def read_config(config_file):
    config_dict = dict()
    with open(config_file, "r") as fp_in:
        data = fp_in.readlines()
        for line in data:
            (key, value) = line.split("=")
            config_dict[key.strip()] = value.strip()
        fp_in.close()
    return config_dict

def get_version():
	return VERSION