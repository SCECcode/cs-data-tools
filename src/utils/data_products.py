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
import json

#Add one directory level above to path to find imports
full_path = os.path.abspath(sys.argv[0])
path_add = os.path.dirname(os.path.dirname(full_path))
sys.path.append(path_add)

import utils.utilities as utilities
import utils.filters as filters


class DataProducts:

    def __init__(self, name, requires_file=False, relevant_filters=[], help_string="", distinct=False):
        self.name = name
        self.requires_file = requires_file
        self.select_fields = []
        self.from_tables = []
        self.metadata_select_fields = []
        self.metadata_from_tables = []
        self.relevant_filters = relevant_filters
        self.help_string = help_string
        self.distinct = distinct
        self.sort = 0

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

    def get_metadata_query(self):
        return (self.metadata_select_fields, self.metadata_from_tables)
    
    def set_sort(self, sort_order):
        if sort_order==0:
            self.sort = 0
        elif sort_order<0:
            self.sort = -1
        else:
            self.sort = 1

    def get_distinct(self):
        return self.distinct

def create_data_products():
    dp_list = []
    #Sites
    dp_sites = DataProducts('Site Info', requires_file=False, relevant_filters=[filters.FilterDataProducts.SITES], help_string="Site name, location, and velocity parameters.")
    dp_sites.set_query(fields=["CyberShake_Sites.CS_Short_Name", "CyberShake_Sites.CS_Site_Name", "CyberShake_Runs.Target_Vs30", "CyberShake_Runs.Model_Vs30", "CyberShake_Runs.Z1_0", "CyberShake_Runs.Z2_5"], tables=["CyberShake_Sites", "CyberShake_Runs"])
    dp_sites.set_metadata_query(fields=["CyberShake_Sites.CS_Site_Lat", "CyberShake_Sites.CS_Site_Lon"], tables=["CyberShake_Sites"])
    dp_list.append(dp_sites)
    #Seismograms
    dp_seismograms = DataProducts('Seismograms', requires_file=True, relevant_filters=[filters.FilterDataProducts.SITES, filters.FilterDataProducts.EVENTS, filters.FilterDataProducts.IMS], help_string="Velocity seismogram files.")
    dp_seismograms.set_query(fields=["CyberShake_Runs.Run_ID", "CyberShake_Sites.CS_Short_Name", "CyberShake_Site_Ruptures.Source_ID", "CyberShake_Site_Ruptures.Rupture_ID", "Rupture_Variations.Rup_Var_ID", "Studies.Study_Name"], tables=["CyberShake_Runs", "CyberShake_Sites", "CyberShake_Site_Ruptures", "Rupture_Variations", "Studies"])
    dp_seismograms.set_metadata_query(fields=["CyberShake_Sites.CS_Short_Name", "CyberShake_Runs.Run_ID", "Ruptures.Mag", "Ruptures.Prob", "Ruptures.Source_Name", "Rupture_Variations.Hypocenter_Lat", "Rupture_Variations.Hypocenter_Lon", "Rupture_Variations.Hypocenter_Depth"], tables=["CyberShake_Sites", "CyberShake_Runs", "Ruptures", "Rupture_Variations"])
    dp_list.append(dp_seismograms)
    #IMs
    dp_intensity_measures = DataProducts('Intensity Measures', requires_file=False, relevant_filters=[filters.FilterDataProducts.SITES, filters.FilterDataProducts.EVENTS, filters.FilterDataProducts.IMS], help_string="RotD50 intensity measure data.")
    dp_intensity_measures.set_query(fields=["PeakAmplitudes.IM_Value"], tables=["PeakAmplitudes"])
    dp_intensity_measures.set_metadata_query(fields=["CyberShake_Sites.CS_Short_Name", "PeakAmplitudes.Run_ID", "PeakAmplitudes.Source_ID", "PeakAmplitudes.Rupture_ID", "PeakAmplitudes.Rup_Var_ID", "Ruptures.Mag", "Ruptures.Prob", "Ruptures.Source_Name", "IM_Types.IM_Type_Value", "IM_Types.IM_Type_Component", "IM_Types.Units", "Rupture_Variations.Hypocenter_Lat", "Rupture_Variations.Hypocenter_Lon", "Rupture_Variations.Hypocenter_Depth"], tables=["CyberShake_Sites", "PeakAmplitudes", "Ruptures", "IM_Types", "Rupture_Variations"])
    dp_list.append(dp_intensity_measures)
    #Events
    dp_events = DataProducts('Event Info', requires_file=False, relevant_filters=[filters.FilterDataProducts.SITES, filters.FilterDataProducts.EVENTS], help_string="Metadata about individual events.", distinct=True)
    dp_events.set_metadata_query(fields=["Ruptures.Source_ID", "Ruptures.Rupture_ID", "Ruptures.Source_Name", "Ruptures.Mag", "Ruptures.Prob", "Ruptures.Start_Lat", "Ruptures.Start_Lon", "Ruptures.End_Lat", "Ruptures.End_Lon", "Rupture_Variations.Rup_Var_ID", "Rupture_Variations.Hypocenter_Lat", "Rupture_Variations.Hypocenter_Lon", "Rupture_Variations.Hypocenter_Depth"], tables=["Ruptures", "Rupture_Variations", "CyberShake_Site_Ruptures"])
    dp_list.append(dp_events)
    #Durations
    #dp_durations = DataProducts('Durations', requires_file=False, help_string="Duration data.")
    #dp_intensity_measures.set_metadata_select("select PeakAmplitudes.Run_ID, PeakAmplitudes.Source_ID, PeakAmplitudes.Rupture_ID, PeakAmplitudes.Rup_Var_ID, Ruptures.Mag, Ruptures.Prob")
    #dp_intensity_measures.set_select("select PeakAmplitudes.IM_Value")
    #dp_list.append(dp_durations)
    return dp_list