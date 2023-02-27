#!/usr/bin/env python3

import sys
import os

import data_products
import filters

#Will return a negative number if the input is not valid
#Otherwise, returns int with value
def validate_input(user_input, max_ok_val):
    try:
        input_int = int(user_input)
    except ValueError:
        print('"%s" is not a valid selection.' % user_input)
        return -1
    if input_int<1 or input_int>max_ok_val:
        print('"%s" is not a valid selection.' % user_input)
        return -2
    return input_int


def choose_data_product(dp_list):
    selected_dp = None
    while True:
        print("These are the available data products:")
        for i,d in enumerate(dp_list):
            print("\t%d) %s" % ((i+1), d.get_name()))
        dp_choice = input("Which data product do you want? ")
        dp_choice_int = validate_input(dp_choice, len(dp_list))
        if dp_choice_int>0:
            selected_dp = dp_list[dp_choice_int-1]
            break
    print("You have selected %s." % (selected_dp.get_name()))
    return selected_dp


def choose_filter_value(filter):
    print("What value(s) do you want to use for the %s filter?" % (filter.get_name()))
    print("%d) Specify single value." % filters.FilterParams.SINGLE_VALUE)
    print("%d) Specify multiple values." % filters.FilterParams.MULTIPLE_VALUES)
    max_filter_val = filters.FilterParams.MULTIPLE_VALUES
    if filter.is_numeric():
        print("%d) Specify a range of values." % filters.FilterParams.VALUE_RANGE)
        max_filter_val = filters.FilterParams.VALUE_RANGE
    value_type_choice = input("How do you want to specify filter values? ")
    value_type_choice_int = validate_input(value_type_choice, max_filter_val)
    #Import builtins so we can instantiate the value objects appropriately
    #Assume Python3
    if value_type_choice_int==filters.FilterParams.SINGLE_VALUE:
        while True:
            value = input("What value do you want to use? ")
            try:
                value_obj = filter.get_type()(value)
            except ValueError:
                print("%s filter requires values of type %s." % (filter.get_name(), str(filter.get_type())))
                continue
            filter.set_value(value_obj)
            break
    elif value_type_choice_int==filters.FilterParams.MULTIPLE_VALUES:
        while True:
            values = input("What values (comma-separated) do you want to use? ")
            pieces = values.split(',')
            value_list = []
            for p in pieces:
                try:
                    value_obj = filter.get_type()(p.strip())
                except ValueError:
                    print("%s filter requires values of type %s." % (filter.get_name(), str(filter.get_type())))
                    continue
                value_list.append(value_obj)
            filter.set_values(value_list)
            break
    elif value_type_choice_int==filters.FilterParams.VALUE_RANGE:
        while True:
            values = input("What range do you want to use? Specify as min, max. ")
            if values.find(",")<0:
                #Didn't provide a comma
                print("'%s' isn't in min, max format." % values)
                continue
            (min_val, max_val) = values.split(',')
            try:
                min_obj = filter.get_type()(min_val)
                max_obj = filter.get_type()(max_val)
            except ValueError:
                print("%s filter requires values of type %s." % (filter.get_name(), str(filter.get_type())))
                continue
            filter.set_value_range(min_obj, max_obj)
            break
    return filter


def choose_filters(filter_list):
    selected_filters = []
    while True:
        print("These are the available filters you can use to get a subset of the data.  You may add multiple filters:")
        for i,f in enumerate(filter_list):
            print("\t%d) %s" % ((i+1), f.get_name()))
        print("\t%d) Done adding filters" % (len(filter_list)+1))
        filt_choice = input("Which filter would you like to add next? ")
        filt_choice_int = validate_input(filt_choice, len(filter_list)+1)
        if (filt_choice_int>0):
            if filt_choice_int==len(filter_list)+1:
                #Then we've chosen the 'done adding filters' option
                break
            selected_filt = filter_list[filt_choice_int-1]
            if selected_filt in selected_filters:
                print("You've already selected the %s filter." % selected_filt.get_name())
                continue
            #Need to ask user for the filter value.
            selected_filt = choose_filter_value(selected_filt)
            selected_filters.append(selected_filt)
            continue
    print("You have selected the following filters:")
    if len(selected_filters)==0:
        print("\tNone")
    else:
        for s in selected_filters:
            print("\t%s" % s.get_filter_string())
    return selected_filters


def get_user_input(dp_list, filter_list):
    print("Welcome to the CyberShake Data Access tool.")
    #Data product
    selected_dp = choose_data_product(dp_list)
    #Filter(s)
    selected_filters = choose_filters(filter_list)
    

