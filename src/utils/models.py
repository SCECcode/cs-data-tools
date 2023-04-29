#!/usr/bin/env python3

import os
import sys

#Defines a CyberShake study for which we have data
class Model:
    
    def __init__(self, name):
        self.name = name

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


def create_models():
    model_list = []
    model1 = Model('Study 15.12')
    model1.set_periods([0.1, 0.2, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 7.5, 10.0])
    model_list.append(model1)
    model2 = Model('Study 22.12 LF')
    model2.set_periods([2.0, 3.0, 4.0, 5.0, 7.5, 10.0])
    model_list.append(model2)
    #model_list.append(Model('Study 22.12 LF'))
    #model_list.append(Model('Study_22.12 BB'))
    return model_list
