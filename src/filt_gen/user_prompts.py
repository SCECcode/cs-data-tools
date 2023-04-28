#!/usr/bin/env python3

import sys
import os

#Add one directory level above to path to find imports
full_path = os.path.abspath(sys.argv[0])
path_add = os.path.dirname(os.path.dirname(full_path))
sys.path.append(path_add)

import utils.data_products as data_products
import utils.filters as filters

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

def choose_model(model_list):
    selected_model = None
    while True:
        print("These are the available CyberShake models:")
        for i,m in enumerate(model_list):
            print("\t%d) %s" % ((i+1), m.get_name()))
        model_choice = input("\nWhich model do you want to use? ")
        model_choice_int = validate_input(model_choice, len(model_list))
        if model_choice_int>0:
            selected_model = model_list[model_choice_int-1]
            break
    print("You have selected %s.\n" % (selected_model.get_name()))
    return selected_model


def choose_data_product(dp_list):
    selected_dp = None
    while True:
        print("These are the available data products:")
        for i,d in enumerate(dp_list):
            print("\t%d) %s" % ((i+1), d.get_name()))
        dp_choice = input("\nWhich data product do you want to retrieve? ")
        dp_choice_int = validate_input(dp_choice, len(dp_list))
        if dp_choice_int>0:
            selected_dp = dp_list[dp_choice_int-1]
            break
    print("You have selected %s.\n" % (selected_dp.get_name()))
    return selected_dp


def choose_filter_value(filter):
    while True:
        print("\nHow do you want to specify value(s) for the %s filter?" % (filter.get_name()))
        print("%d) Specify single value." % filters.FilterParams.SINGLE_VALUE)
        print("%d) Specify multiple values." % filters.FilterParams.MULTIPLE_VALUES)
        max_filter_val = filters.FilterParams.MULTIPLE_VALUES
        if filter.is_numeric():
            print("%d) Specify a range of values." % filters.FilterParams.VALUE_RANGE)
            max_filter_val = filters.FilterParams.VALUE_RANGE
        max_filter_val += 1
        print("%d) Show valid values for this filter." % (max_filter_val))
        value_type_choice = input("\nHow do you want to specify filter values? ")
        value_type_choice_int = validate_input(value_type_choice, max_filter_val)
        if value_type_choice_int==max_filter_val:
            #Print valid values
            try:
                #RangeFilter?
                (min_val, max_val) = filter.get_range()
                print("Valid values are [%f, %f]." % (min_val, max_val))
                continue
            except:
                pass
            try:
                #EnumeratedFilter?
                vals_list = filter.get_values_list()
                print("Valid values are %s" % ', '.join([str(v) for v in vals_list]))
                continue
            except:
                pass
            print("No restrictions on values.")
            continue
        elif value_type_choice_int>=0:
            break
    if value_type_choice_int==filters.FilterParams.SINGLE_VALUE:
        while True:
            value = input("What value do you want to use? ")
            try:
                value_obj = filter.get_type()(value)
            except ValueError:
                print("%s filter requires values of type %s." % (filter.get_name(), str(filter.get_type())))
                continue
            if filter.set_value(value_obj)!=0:
                continue
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
            if filter.set_values(value_list)!=0:
                continue
            break
    elif value_type_choice_int==filters.FilterParams.VALUE_RANGE:
        while True:
            values = input("What range do you want to use? Specify as min, max: ")
            pieces = values.split(",")
            if len(pieces)!=2:
                print("'%s' isn't in min, max format." % values)
                continue
            (min_val, max_val) = pieces
            try:
                min_obj = filter.get_type()(min_val)
                max_obj = filter.get_type()(max_val)
            except ValueError:
                print("%s filter requires values of type %s." % (filter.get_name(), str(filter.get_type())))
                continue
            if filter.set_value_range(min_obj, max_obj)!=0:
                continue
            break
    else:
        #Print valid values
        try:
            #RangeFilter?
            (min_val, max_val) = filter.get_range()
            print("Valid values are [%f, %f]." % (min_val, max_val))
        except:
            pass
        try:
            #EnumeratedFilter?
            vals_list = filter.get_values_list()
            print("Valid values are %s" % ', '.join([str(v) for v in vals_list]))
        except:
            pass

    return filter


def choose_filters(filter_list, selected_dp):
    selected_filters = []
    remaining_filter_list = []
    filter_dps = selected_dp.get_relevant_filters()
    for f in filter_list:
        if f.get_data_product() in filter_dps:
            remaining_filter_list.append(f)
    while True:
        print("These are the available filters you can use to get a subset of CyberShake data.  You may add multiple filters:")
        for i,f in enumerate(remaining_filter_list):
            print("\t%d) %s" % ((i+1), f.get_name()))
        print("\t%d) Done adding filters" % (len(remaining_filter_list)+1))
        filt_choice = input("\nWhich filter would you like to add next? ")
        filt_choice_int = validate_input(filt_choice, len(remaining_filter_list)+1)
        if (filt_choice_int>0):
            if filt_choice_int==len(remaining_filter_list)+1:
                #Then we've chosen the 'done adding filters' option
                break
            selected_filt = remaining_filter_list[filt_choice_int-1]
            if selected_filt in selected_filters:
                print("You've already selected the %s filter." % selected_filt.get_name())
                continue
            #Need to ask user for the filter value.
            selected_filt = choose_filter_value(selected_filt)
            selected_filters.append(selected_filt)
            remaining_filter_list.remove(selected_filt)
            continue
    return selected_filters


def get_user_input(model_list, dp_list, filter_list):
    print("Welcome to the CyberShake Data Access tool.\n")
    #Model
    selected_model = choose_model(model_list)
    #Data product
    selected_dp = choose_data_product(dp_list)
    #Filter(s)
    selected_filters = choose_filters(filter_list, selected_dp)
    print("\nYou have generated the following data product request:\n")
    print("Model:")
    print("\t%s" % selected_model.get_name())
    print("\nData product:")
    print("\t%s" % selected_dp.get_name())
    print("\nFilters:")
    if len(selected_filters)==0:
        print("\tNone")
    else:
        for s in selected_filters:
            print("\t%s" % s.get_filter_string())
    return (selected_model, selected_dp, selected_filters)
    

