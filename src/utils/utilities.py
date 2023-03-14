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
