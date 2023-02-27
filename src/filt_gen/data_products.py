#!/usr/bin/env python3

import sys
import os
#Add one directory level above to path to find imports
full_path = os.path.abspath(sys.argv[0])
path_add = os.path.dirname(os.path.dirname(full_path))
sys.path.append(path_add)

import utils


class DataProducts:

    def __init__(self, name, requires_file=False):
        self.name = name
        self.requires_file = requires_file

    def get_name(self):
        return self.name


def create_data_products():
    dp_list = []
    #Sites
    dp_sites = DataProducts('Site Names', False)
    dp_list.append(dp_sites)
    #Seismograms
    dp_seismograms = DataProducts('Seismograms', False)
    dp_list.append(dp_seismograms)
    #IMs
    dp_intensity_measures = DataProducts('Intensity Measures', False)
    dp_list.append(dp_intensity_measures)
    return dp_list