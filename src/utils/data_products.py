#!/usr/bin/env python3

import sys
import os
import json

#Add one directory level above to path to find imports
full_path = os.path.abspath(sys.argv[0])
path_add = os.path.dirname(os.path.dirname(full_path))
sys.path.append(path_add)

import utils.utilities as utilities


class DataProducts:

    def __init__(self, name, requires_file=False, help_string=""):
        self.name = name
        self.requires_file = requires_file
        self.help_string = help_string
        self.select = ""
        self.metadata_select = ""

    def get_name(self):
        return self.name
    
    def get_dict_representation(self):
        obj_dict = dict()
        obj_dict['name'] = self.name
        return obj_dict

    def get_help_string(self):
        return self.help_string

    def set_select(self, select_string):
        self.select = select_string

    def set_metadata_select(self, metadata_select_string):
        self.metadata_select = metadata_select_string


def create_data_products():
    dp_list = []
    #Sites
    dp_sites = DataProducts('Site Names', requires_file=False, help_string="List of valid site names.")
    dp_sites.set_select("select CyberShake_Sites.CS_Short_Name")
    dp_list.append(dp_sites)
    #Seismograms
    dp_seismograms = DataProducts('Seismograms', requires_file=True, help_string="Velocity seismogram files.")
    dp_seismograms.set_metadata_select("select CyberShake_Sites.CS_Short_Name, CyberShake_Runs.Run_ID, Rupture_Variations.Source_ID, Rupture_Variations.Rupture_ID, Rupture_Variations.Rup_Var_ID")
    dp_list.append(dp_seismograms)
    #IMs
    dp_intensity_measures = DataProducts('Intensity Measures', requires_file=False, help_string="Intensity measure data.")
    dp_intensity_measures.set_metadata_select("select PeakAmplitudes.Run_ID, PeakAmplitudes.Source_ID, PeakAmplitudes.Rupture_ID, PeakAmplitudes.Rup_Var_ID, Ruptures.Mag, Ruptures.Prob")
    dp_intensity_measures.set_select("select PeakAmplitudes.IM_Value")
    dp_list.append(dp_intensity_measures)
    #Durations
    #dp_durations = DataProducts('Durations', requires_file=False, help_string="Duration data.")
    #dp_intensity_measures.set_metadata_select("select PeakAmplitudes.Run_ID, PeakAmplitudes.Source_ID, PeakAmplitudes.Rupture_ID, PeakAmplitudes.Rup_Var_ID, Ruptures.Mag, Ruptures.Prob")
    #dp_intensity_measures.set_select("select PeakAmplitudes.IM_Value")
    #dp_list.append(dp_durations)
    return dp_list