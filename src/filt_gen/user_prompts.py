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
    print("You have selected %s." % (selected_dp.get_name()))
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
            input_string = "What value do you want to use? "
            if filter.get_units() is not None:
                input_string = "What value do you want to use (units %s)? " % filter.get_units()
            value = input(input_string)
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
            input_string = "What values (comma-separated) do you want to use? "
            if filter.get_units() is not None:
                input_string = "What values (comma-separated) do you want to use (units %s)? " % filter.get_units()
            values = input(input_string)
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
            input_string = "What range do you want to use? Specify as min, max: "
            if filter.get_units() is not None:
                input_string = "What range do you want to use? Specify as min, max (units %s): " % filter.get_units()
            values = input(input_string)
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


def choose_filters(filter_list, selected_dp, selected_model):
    selected_filters = []
    remaining_filter_list = []
    filter_dps = selected_dp.get_relevant_filters()
    for f in filter_list:
        if f.get_name()=='Intensity Measure Period':
            #Update with periods from model
            f.set_values_list(selected_model.get_periods())
        if f.get_data_product() in filter_dps:
            remaining_filter_list.append(f)
    while True:
        print("\nThese are the available filters you can use to get a subset of CyberShake data.  You may add multiple filters:")
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
            #Also need to prompt for any required filters
            for s in selected_filt.get_required_filters():
                print("\nSince you selected the %s filter, you also need to use the %s filter." % (selected_filt.get_name(), s.get_name()))
                s = choose_filter_value(s)
                selected_filters.append(s)
                remaining_filter_list.remove(s)
            continue
    return selected_filters

def choose_sort_order(sort_item):
    while True:
        print("\nYou've chosen to sort on %s." % sort_item.get_name())
        print("\t1) Ascending order")
        print("\t2) Descending order")
        order_choice = input("What order do you want to sort in? ")
        order_choice_int = validate_input(order_choice, 2)
        if order_choice_int>0:
            if order_choice_int==1:
                sort_item.set_sort(1)
            elif order_choice_int==2:
                sort_item.set_sort(-1)
            break

def choose_sort(selected_filters):
    do_sort = False
    while True:
        do_sort_choice = input("\nWould you like to sort your results (y/n)? ")
        if do_sort_choice.lower()=='n':
            break
        elif do_sort_choice.lower()=='y':
            do_sort = True
            break
        else:
            print("'%s' is not a valid option." % do_sort_choice)
    #Not sorting today
    if do_sort==False:
        return
    while True:
        print("You can sort on one of the following criteria:")
        for i,f in enumerate(selected_filters):
            print("\t%d) %s" % ((i+1), f.get_name()))
        sort_choice = input("What would you like to sort on? ")
        sort_choice_int = validate_input(sort_choice, len(selected_filters))
        if (sort_choice_int>0):
            sort_item = selected_filters[sort_choice_int-1]
            choose_sort_order(sort_item)
            break


def get_user_input(model_list, dp_list, filter_list):
    print("Welcome to the CyberShake Data Access tool.\n")
    #Model
    selected_model = choose_model(model_list)
    #Data product
    selected_dp = choose_data_product(dp_list)
    #Filter(s)
    selected_filters = choose_filters(filter_list, selected_dp, selected_model)
    #Optional sort
    if len(selected_filters)>0:
        choose_sort(selected_filters)
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
            if s.get_sort()<0:
                print("\t%s, sort descending" % s.get_filter_string())
            elif s.get_sort()>0:
                print("\t%s, sort ascending" % s.get_filter_string())
            else:
                print("\t%s" % s.get_filter_string())
    return (selected_model, selected_dp, selected_filters)
    

