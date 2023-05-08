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

'''Class to hold details about a particular possible filter.'''

import sys
import os
import json

from enum import IntEnum

#Add one directory level above to path to find imports
full_path = os.path.abspath(sys.argv[0])
path_add = os.path.dirname(os.path.dirname(full_path))
sys.path.append(path_add)

import utils.utilities as utilities


#Enum class to specify what the filter is filtering on - IMs, events, or sites?
#This way, after the user selects the data product, we can just present relevant filters.
class FilterDataProducts(IntEnum):
	EVENTS = 1
	SITES = 2
	IMS = 3

	def get_text(fp):
		if fp==FilterDataProducts.EVENTS:
			return "events"
		elif fp==FilterDataProducts.SITES:
			return "sites"
		elif fp==FilterDataProducts.IMS:
			return "IMs"
		else:
			return "Error parsing %s into FilterDataProduct." % str(fp)
	

#Enum class to describe how the user wants to specify the filter values
#Basically, how to interpret and apply the values in the values list
class FilterParams(IntEnum):
	SINGLE_VALUE = 1
	MULTIPLE_VALUES = 2
	VALUE_RANGE = 3

	def get_text(fp):
		if fp==FilterParams.SINGLE_VALUE:
			return "single value"
		elif fp==FilterParams.MULTIPLE_VALUES:
			return "multiple values"
		elif fp==FilterParams.VALUE_RANGE:
			return "range of values"
		else:
			return "Error parsing %s into FilterParam." % str(fp)

#Base class for a filter
class Filter:

	#filt_type is datatype of filter
	def __init__(self, name, filt_type=None, data_product=None, help_string="", units=None):
		self.name = name
		self.type = filt_type
		self.values = []
		self.filter_params = FilterParams.SINGLE_VALUE
		self.where_fields = []
		self.from_tables = []
		self.data_product = data_product
		self.help_string = help_string
		self.sort = 0
		self.units = units
		#Other filters which must also be added if this filter is added
		self.requires_filters = []

	def get_name(self):
		return self.name

	def get_help_string(self):
		return self.help_string

	def get_filter_params(self):
		return self.filter_params

	def get_units(self):
		return self.units

	def add_required_filter(self, required_filter):
		self.requires_filters.append(required_filter)

	def get_required_filters(self):
		return self.requires_filters

	#The joins required to select on this filter
	def set_query(self, fields=[], tables=[], contains=False):
		self.where_fields.extend(fields)
		self.from_tables.extend(tables)
		self.contains = contains

	def get_query(self):
		return (self.where_fields, self.from_tables)

	def get_contains(self):
		return self.contains

	def set_value(self, value):
		self.values.clear()
		self.values.append(value)
		self.filter_params = FilterParams.SINGLE_VALUE
		return 0

	def get_values(self):
		return self.values

	def get_value(self):
		return self.values[0]

	def set_values(self, values):
		self.values.clear()
		for v in values:
			self.values.append(v)
		self.filter_params = FilterParams.MULTIPLE_VALUES
		return 0

	def set_value_range(self, min, max):
		#This only makes sense if the filter is a numerical datatype
		#(We don't have any sensical complex numbers in the CS filters)
		if self.is_numeric()==False:
			print("You can't specify a range for a filter which is type %s." % (str(self.get_type())))
			return -1
		if min>max:
			print("Maximum value %s needs to be greater than or equal to the minimum value %s." % (str(max), str(min)))
			return -2
		self.values.clear()
		self.values.append(min)
		self.values.append(max)
		self.filter_params = FilterParams.VALUE_RANGE
		return 0

	#Is the type of this filter a number?
	def is_numeric(self):
		if self.get_type()==float or self.get_type()==int:
			return True
		else:
			return False

	def get_type(self):
		return self.type

	def get_data_product(self):
		return self.data_product

	#Returns a dict() representation of this object, to use for JSON serialization
	def get_dict_representation(self):
		#Need to store name so we can find it later, plus user-specified values
		obj_dict = dict()
		obj_dict['name'] = self.name
		obj_dict['filter_params'] = self.filter_params
		obj_dict['values'] = self.values
		if self.sort!=0:
			obj_dict['sort'] = self.sort
		return obj_dict


	#Return a printable string describing the filter + values.
	def get_filter_string(self):
		pretty_string = "%s" % self.name
		if self.filter_params==FilterParams.SINGLE_VALUE:
			pretty_string = "%s: %s" % (pretty_string, self.values[0])
		elif self.filter_params==FilterParams.MULTIPLE_VALUES:
			pretty_string = "%s: %s" % (pretty_string, ','.join([str(v) for v in self.values]))
		elif self.filter_params==FilterParams.VALUE_RANGE:
			pretty_string = "%s: [%s,%s]" % (pretty_string, self.values[0], self.values[1])
		return pretty_string

	def set_sort(self, sort_order):
		if sort_order==0:
			self.sort = 0
		elif sort_order<0:
			self.sort = -1
		else:
			self.sort = 1

	def get_sort(self):
		return self.sort

#Class for a filter which has a preset list of possible values - checks user input
class EnumeratedFilter(Filter):
	
	def __init__(self, name, filt_type=None, values_list=None, data_product=None, help_string="", units=None):
		super().__init__(name, filt_type=filt_type, data_product=data_product, help_string=help_string, units=units)
		self.values_list = values_list

	def set_values_list(self, values_list=None):
		self.values_list = values_list

	def set_value(self, value):
		if value not in self.values_list:
			print("%s isn't a possible value for the %s filter." % (value, self.name))
			return -1
		super().set_value(value)
		return 0
	
	def get_values_list(self):
		return self.values_list

	def get_help_string(self):
		help_str = "%s  Possible values:" % super().get_help_string()
		if self.values_list is not None:
			values_str = ', '.join([str(v) for v in self.values_list])
			help_str = "%s %s" % (help_str, values_str)
		return help_str
			


#Class for a filter which has a range of possible values - checks user input
class RangeFilter(Filter):

	def __init__(self, name, filt_type=None, min=-1e99, max=1e99, data_product=None, help_string="", units=None):
		super().__init__(name, filt_type=filt_type, data_product=data_product, help_string=help_string, units=units)
		self.min = min
		self.max = max
		self.value = None

	def set_range(self, min=None, max=None):
		self.min = min
		self.max = max

	def get_range(self):
		return (self.min, self.max)

	def set_value(self, value):
		if value<self.min or value>self.max:
			print("The %s filter can only take values [%s, %s]." % (self.name, str(self.min), str(self.max)))
			return utilities.ExitCodes.VALUE_OUT_OF_RANGE
		return super().set_value(value)
	
	def set_values(self, values):
		for v in values:
			if v<self.min or v>self.max:
				print("The %s filter can only take values [%s, %s]." % (self.name, str(self.min), str(self.max)))
				return utilities.ExitCodes.VALUE_OUT_OF_RANGE
		return super().set_values(values)
	
	def set_value_range(self, min, max):
		if min<self.min or max>self.max:
			print("The %s filter can only take values [%s, %s]." % (self.name, str(self.min), str(self.max)))
			return utilities.ExitCodes.VALUE_OUT_OF_RANGE
		return super().set_value_range(min, max)


def create_filters():
	filters = []
	#IM type
	im_type_filter = EnumeratedFilter('Intensity Measure Period', filt_type=float, data_product=FilterDataProducts.IMS, help_string="Type of intensity measure.")
	#im_type_filter.set_values_list([2.0, 3.0, 4.0, 5.0, 7.5, 10.0, "PGV"])
	im_type_filter.set_query(fields=["IM_Types.IM_Type_Value"], tables=["IM_Types"])
	filters.append(im_type_filter)
	#IM value
	im_value_filter = RangeFilter('Intensity Measure Value', filt_type=float, data_product=FilterDataProducts.IMS, help_string="Value of intensity measure, in cm/s2.", units='cm/sec2')
	im_value_filter.set_range(min=0.0, max=10000.0)
	im_value_filter.set_query(fields=["PeakAmplitudes.IM_Value"], tables=["PeakAmplitudes"])
	im_value_filter.add_required_filter(im_type_filter)
	filters.append(im_value_filter)
	#Magnitude
	mag_filter = RangeFilter('Magnitude', filt_type=float, data_product=FilterDataProducts.EVENTS, help_string="Magnitude of the earthquake.")
	mag_filter.set_range(min=5.0, max=8.5)
	mag_filter.set_query(fields=["Ruptures.Mag"], tables=['Ruptures'])
	filters.append(mag_filter)
	#Sites
	sites_filter = Filter('Site Name', filt_type=str, data_product=FilterDataProducts.SITES, help_string="3-5 character site name.")
	#sites_filter.set_values_list(["USC", "PAS", "WNGC", "STNI"])
	sites_filter.set_query(fields=["CyberShake_Sites.CS_Short_Name"], tables=['CyberShake_Sites'])
	filters.append(sites_filter)
	#Site-Rupture dist
	site_rup_dist_filter = RangeFilter('Site-Rupture Distance', filt_type=float, data_product=FilterDataProducts.EVENTS, help_string="Site-rupture distance, which is determined by calculating the distance between the site and each point on the rupture surface and taking the minimum.", units="km")
	site_rup_dist_filter.set_range(min=0.0, max=200.0)
	site_rup_dist_filter.set_query(fields=["CyberShake_Site_Ruptures.Site_Rupture_Dist"], tables=["CyberShake_Site_Ruptures"])
	site_rup_dist_filter.add_required_filter(sites_filter)
	filters.append(site_rup_dist_filter)
	#Probability
	#prob_filter = RangeFilter('Rupture Probability', filt_type=float, help_string="The probability of the rupture occuring, as specified by the ERF.  Note that if the rupture has multiple rupture variations, this probability will be distributed among the rupture variations.")
	#prob_filter.set_range(min=0.0, max=1.0)
	#filters.append(prob_filter)
	#Source name
	source_name_filter = Filter('Source Name', filt_type=str, data_product=FilterDataProducts.EVENTS, help_string="Name of the source.  Any sources which contain this string will be selected.")
	source_name_filter.set_query(fields=["Ruptures.Source_Name"], tables=["Ruptures"], contains=True)
	filters.append(source_name_filter)
	return filters

