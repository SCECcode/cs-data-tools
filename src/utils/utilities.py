#!/usr/bin/env python3

import sys
import os
import json

class ExitCodes:

    NO_DATAPRODUCTS = 1
    NO_FILTERS = 2
    VALUE_OUT_OF_RANGE = 3
    INVALID_ARGUMENTS = 4
    MISSING_ARGUMENTS = 5
    FILE_PARSING_ERROR = 6
    BAD_FILE_PATH = 7
    DATABASE_CONNECTION_ERROR = 8
    DATABASE_COMMAND_ERROR = 9
    FILE_WRITING_ERROR = 10


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

