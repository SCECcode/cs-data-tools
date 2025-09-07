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

import os
import sys

#Defines a CyberShake study for which we have data
class Model:
    
    def __init__(self, name):
        self.name = name
        self.custom_table_dict = dict()

    def get_name(self):
        return self.name
     
    def get_query(self):
        from_table = 'Studies'
        where_clause = 'Studies.Study_Name="%s"' % self.name
        return ([from_table], [where_clause])
    
    def get_dict_representation(self):
        obj_dict = dict()
        obj_dict['name'] = self.name
        return obj_dict
    
    #RotD50 periods we can retrieve for this model
    def set_periods(self, periods):
        self.periods = periods

    def get_periods(self):
        return self.periods
    
    #Define available data products, since not all studies support all data products
    def set_data_products(self, dps):
        self.data_products = dps

    def get_data_products(self):
        return self.data_products
    
    #Set a custom table name for one of the standard tables
    #For example, for Study 24.8 use 'PeakAmplitudes_24_8' instead of 'PeakAmplitudes'
    def set_custom_table_name(self, old_table, new_table):
        self.custom_table_dict[old_table] = new_table

    def has_custom_table_name(self):
        if len(self.custom_table_dict.keys())>0:
            return True
        return False

def create_models(dp_list):
    model_list = []
    #model1 = Model('Study 15.12')
    #model1.set_periods([0.1, 0.2, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 7.5, 10.0])
    #model_list.append(model1)
    model2 = Model('Study 22.12 LF')
    model2.set_periods([2.0, 3.0, 4.0, 5.0, 7.5, 10.0, "PGV"])
    model2.set_data_products(dp_list)
    model_list.append(model2)
    model3 = Model('Study 22.12 BB')
    model3.set_periods([0.01, 0.02, 0.03, 0.04, 0.05, 0.075, 0.1, 0.2, 0.3, 0.4, 0.5, 0.75, 1, 2, 3, 4, 5, 7.5, 10, "PGV", "PGA"])
    model3.set_data_products(dp_list)
    model_list.append(model3)
    model4 = Model('Study 24.8 LF')
    model4.set_periods([2.0, 3.0, 4.0, 5.0, 7.5, 10.0, "PGV"])
    model4_data_products = []
    for d in dp_list:
        if d.name != "Seismograms":
            model4_data_products.append(d)
    model4.set_data_products(model4_data_products)
    model4.set_custom_table_name("PeakAmplitudes", "PeakAmplitudes_24_8")
    model_list.append(model4)
    model5 = Model('Study 24.8 BB')
    model5.set_periods([0.01, 0.02, 0.03, 0.04, 0.05, 0.075, 0.1, 0.2, 0.3, 0.4, 0.5, 0.75, 1, 2, 3, 4, 5, 7.5, 10, "PGV", "PGA"])
    #Has the same data products as 24.8 LF
    model5.set_data_products(model4_data_products)
    model_list.append(model5)
    return model_list
