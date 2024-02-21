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
import json

VERSION = "1.0.0_09052023"

#Maximum of 120K events in the event list, because otherwise the MySQL query might be too long
MAX_EVENT_LIST_LENGTH = 120000

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
	FILE_DOWNLOAD_ERROR = 12


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
		field_aliases['CS_Site_Name'] = 'Site_Long_Name'
		field_aliases['CS_Site_Lon'] = "Site_Longitude"
		field_aliases['CS_Site_Lat'] = "Site_Latitude"
		field_aliases['Prob'] = 'Rupture_Probability'
		field_aliases['Mag'] = 'Magnitude'
		field_aliases['IM_Type_Value'] = 'Period'
		field_aliases['IM_Type_Component'] = 'Component'
		field_aliases['Rup_Var_ID'] = 'Rupture_Variation_ID'
		field_aliases['Target_Vs30'] = 'Thompson_Vs30'
		field_aliases['Model_Vs30'] = '3D_CVM_Vs30'
		field_aliases['Z1_0'] = 'Z1.0'
		field_aliases['Z2_5'] = 'Z2.5'
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
	elif study_name=='Study 22.12 LF':
		nt = 8000
	elif study_name=='Study 22.12 BB':
		nt = 40000
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