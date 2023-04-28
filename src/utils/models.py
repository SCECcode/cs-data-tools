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


def create_models():
    model_list = []
    model_list.append(Model('Study 15.12'))
    model_list.append(Model('Study 22.12 LF'))
    model_list.append(Model('Study_22.12 BB'))
    return model_list
