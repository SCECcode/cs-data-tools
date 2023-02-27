#!/usr/bin/env python3

'''Class to hold details about a particular possible filter.'''

import sys
import os
from enum import IntEnum

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
	def __init__(self, name, filt_type=None):
		self.name = name
		self.type = filt_type
		self.values = []
		self.filter_params = FilterParams.SINGLE_VALUE
	
	def get_name(self):
		return self.name

	def set_value(self, value):
		self.values.clear()
		self.values.append(value)
		self.filter_params = FilterParams.SINGLE_VALUE

	def set_values(self, values):
		self.values.clear()
		for v in values:
			self.values.append(v)
		self.filter_params = FilterParams.MULTIPLE_VALUES

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

	#Return a printable string describing the filter.
	def get_filter_string(self):
		pass



#Class for a filter which has a preset list of possible values
class EnumeratedFilter(Filter):
	
	def __init__(self, name, filt_type=None, values_list=None):
		super().__init__(name, filt_type=filt_type)
		self.values_list = values_list

	def set_values_list(self, values_list=None):
		self.values_list = values_list

	def set_value(self, value):
		if value not in self.values_list:
			print("%s isn't a possible value for the %s filter." % (value, self.name))
			return -1
		super().set_value(value)
		return 0


#Class for a filter which has a range of possible values
class RangeFilter(Filter):

	def __init__(self, name, filt_type=None, min=None, max=None):
		super().__init__(name, filt_type=filt_type)
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
			print("Filter %s can only take values [%s, %s]" % (self.name, str(self.min), str(self.max)))
			return -1
		super().set_value(value)
		return 0
		

def create_filters():
	filters = []
	#Magnitude
	mag_filter = RangeFilter('Magnitude', filt_type=float)
	mag_filter.set_range(min=5.0, max=8.5)
	filters.append(mag_filter)
	#IM values
	im_filter = EnumeratedFilter('Intensity Measure Type', filt_type=str)
	im_filter.set_values_list(['RotD50', 'RotD100', 'PGV'])
	filters.append(im_filter)
	return filters

