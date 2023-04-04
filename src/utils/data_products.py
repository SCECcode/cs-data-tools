#!/usr/bin/env python3

import sys
import os
import json

#Add one directory level above to path to find imports
full_path = os.path.abspath(sys.argv[0])
path_add = os.path.dirname(os.path.dirname(full_path))
sys.path.append(path_add)

import utils.utilities as utilities
import utils.filters as filters


class DataProducts:

    def __init__(self, name, requires_file=False, relevant_filters=[], help_string=""):
        self.name = name
        self.requires_file = requires_file
        self.select_fields = []
        self.from_tables = []
        self.metadata_select_fields = []
        self.metadata_from_tables = []
        self.relevant_filters = relevant_filters
        self.help_string = help_string

    def get_name(self):
        return self.name
    
    def get_relevant_filters(self):
        return self.relevant_filters
    
    def get_dict_representation(self):
        obj_dict = dict()
        obj_dict['name'] = self.name
        return obj_dict

    def get_help_string(self):
        return self.help_string

    def set_query(self, fields=None, tables=None):
        self.select_fields.extend(fields)
        self.from_tables.extend(tables)

    def get_query(self):
        return (self.select_fields, self.from_tables)

    def set_metadata_query(self, fields=None, tables=None):
        self.metadata_select_fields.extend(fields)
        self.metadata_from_tables.extend(tables)

def create_data_products():
    dp_list = []
    #Sites
    dp_sites = DataProducts('Site Names', requires_file=False, relevant_filters=[filters.FilterDataProducts.SITES], help_string="List of valid site names.")
    dp_sites.set_query(fields=["CyberShake_Sites.CS_Short_Name"], tables=["CyberShake_Sites"])
    dp_sites.set_metadata_query(fields=["CyberShake_Sites.CS_Site_Lat", "CyberShake_Sites.CS_Site_Lon"], tables=["CyberShake_Sites"])
    dp_list.append(dp_sites)
    #Seismograms
    dp_seismograms = DataProducts('Seismograms', requires_file=True, relevant_filters=[filters.FilterDataProducts.SITES, filters.FilterDataProducts.EVENTS, filters.FilterDataProducts.IMS], help_string="Velocity seismogram files.")
    dp_seismograms.set_query(fields=["CyberShake_Runs.Run_ID", "CyberShake_Sites.CS_Short_Name", "CyberShake_Site_Ruptures.Source_ID", "CyberShake_Site_Ruptures.Rupture_ID", "Rupture_Variations.Rup_Var_ID"], tables=["CyberShake_Runs", "CyberShake_Sites", "CyberShake_Site_Ruptures", "Rupture_Variations"])
    dp_seismograms.set_metadata_select("select CyberShake_Sites.CS_Short_Name, CyberShake_Runs.Run_ID, Rupture_Variations.Source_ID, Rupture_Variations.Rupture_ID, Rupture_Variations.Rup_Var_ID")
    dp_list.append(dp_seismograms)
    #IMs
    dp_intensity_measures = DataProducts('Intensity Measures', requires_file=False, relevant_filters=[filters.FilterDataProducts.SITES, filters.FilterDataProducts.EVENTS, filters.FilterDataProducts.IMS], help_string="Intensity measure data.")
    dp_intensity_measures.set_query(fields=["PeakAmplitudes.IM_Value"], tables=["PeakAmplitudes"])
    dp_intensity_measures.set_metadata_query(fields=["PeakAmplitudes.Run_ID", "PeakAmplitudes.Source_ID", "PeakAmplitudes.Rupture_ID", "PeakAmplitudes.Rup_Var_ID", "Ruptures.Mag", "Ruptures.Prob"], tables=["PeakAmplitudes", "Ruptures"])
    dp_list.append(dp_intensity_measures)
    #Durations
    #dp_durations = DataProducts('Durations', requires_file=False, help_string="Duration data.")
    #dp_intensity_measures.set_metadata_select("select PeakAmplitudes.Run_ID, PeakAmplitudes.Source_ID, PeakAmplitudes.Rupture_ID, PeakAmplitudes.Rup_Var_ID, Ruptures.Mag, Ruptures.Prob")
    #dp_intensity_measures.set_select("select PeakAmplitudes.IM_Value")
    #dp_list.append(dp_durations)
    return dp_list