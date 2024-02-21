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

import utils.filters as filters
import utils.data_products as data_products
import utils.models as models

class Query:
    field_order = ['Study_Name',
                  'Run_ID', 
                    'CS_Short_Name',
                    'CS_Site_Name',
                    'CS_Site_Lon',
                    'CS_Site_Lat',
                    'Target_Vs30',
                    'Model_Vs30',
                    'Z1_0',
                    'Z2_5',
                    'Source_ID',
                    'Rupture_ID',
                    'Rup_Var_ID',
                    'Source_Name',
                    'Mag',
                    'Prob',
                    'IM_Type_Value',
                    'IM_Type_Component',
                    'IM_Type_Measure',
                    'IM_Value',
                    'Units',
                    'Start_Lat',
                    'Start_Lon',
                    'End_Lat',
                    'End_Lon',
                    'Hypocenter_Lat',
                    'Hypocenter_Lon',
                    'Hypocenter_Depth']

    def __init__(self):
        self.select_fields = set()
        self.from_tables = set()
        self.where_clauses = set()
        self.sort = ""
        self.distinct = False

    def add_select(self, select_fields):
        for s in select_fields:
            self.select_fields.add(s)

    def remove_select(self, select_fields):
        for s in select_fields:
            self.select_fields.remove(s)

    def add_from(self, from_fields):
        for f in from_fields:
            self.from_tables.add(f)

    def add_where(self, where_fields):
        for w in where_fields:
            self.where_clauses.add(w)

    def remove_where(self, where_fields):
        for w in where_fields:
            if w in self.where_clauses:
                self.where_clauses.remove(w)

    def set_sort(self, sort_clause):
        self.sort = sort_clause

    def get_sort(self):
        return self.sort

    def get_select_string(self):
        #Use the sorted version
        return ",".join(self.sort_select())
    
    def get_from_string(self):
        #Sort in alphabetical order so we know the order for tests
        return ",".join(sorted(list(self.from_tables)))
    
    def get_where_string(self):
        #Sort in alphabetical order so we know the order for tests
        return " and ".join(sorted(list(self.where_clauses)))

    def get_query_string(self):
        return "select %s from %s where %s" % (self.get_select_string(), self.get_from_string(), self.get_where_string())

    def set_distinct(self, distinct):
        self.distinct = distinct

    def get_distinct(self):
        return self.distinct

    #Sorts the select fields into preference order, returns list
    def sort_select(self):
        sorted_select_fields = []
        select_fields_list = list(self.select_fields)
        for f in self.field_order:
            for s in select_fields_list:
                #Match on suffix - don't care which table it comes from
                if f==s.split(".")[1]:
                    sorted_select_fields.append(s)
        #Add the rest to the end:
        for s in select_fields_list:
            if s not in sorted_select_fields:
                sorted_select_fields.append(s)
        return sorted_select_fields

    #Makes sure all tables are connected with joins
    def connect_tables(self):
        table_list = list(self.from_tables)
        table_list.sort()
        connected_list = []
        working_table = table_list.pop(0)
        while len(table_list)>0:
            #Run all combos
            for t in table_list:
                if t not in connected_list:
                    #print("Connecting %s and %s." % (working_table, t))
                    added_tables = self.join_tables(working_table, t)
                    if len(added_tables)>0:
                        table_list.extend(added_tables)
            connected_list.append(working_table)
            working_table = table_list.pop(0)

    #Adds joins between tables
    def join_tables(self, table1, table2):
        added_tables = []
        if table1==table2:
            return added_tables
        if table1>table2:
            #Swap tables to be in alpha order
            self.join_tables(table2, table1)
            return added_tables
        if table1=="CyberShake_Runs":
            #CyberShake_Runs, CyberShake_Sites
            if table2=="CyberShake_Sites":
                self.add_where(["CyberShake_Runs.Site_ID=CyberShake_Sites.CS_Site_ID"])
            #CyberShake_Runs, Rupture_Variations
            elif table2=="Rupture_Variations":
                self.add_where(["CyberShake_Runs.ERF_ID=Rupture_Variations.ERF_ID", "CyberShake_Runs.Rup_Var_Scenario_ID=Rupture_Variations.Rup_Var_Scenario_ID"])
            #CyberShake_Runs, Ruptures
            elif table2=="Ruptures":
                self.add_where(["CyberShake_Runs.ERF_ID=Ruptures.ERF_ID"])
            #CyberShake_Runs, PeakAmplitudes
            elif table2=="PeakAmplitudes":
                self.add_where(["CyberShake_Runs.Run_ID=PeakAmplitudes.Run_ID"])
            #CyberShake_Runs, Studies
            elif table2=="Studies":
                self.add_where(["CyberShake_Runs.Study_ID=Studies.Study_ID"])
        elif table1=="CyberShake_Site_Ruptures":
            #CyberShake_Site_Ruptures, CyberShake_Sites
            if table2=="CyberShake_Sites":
                self.add_where(["CyberShake_Site_Ruptures.CS_Site_ID=CyberShake_Sites.CS_Site_ID"])
            #CyberShake_Site_Ruptures, Ruptures
            elif table2=="Ruptures":
                self.add_where(["CyberShake_Site_Ruptures.ERF_ID=Ruptures.ERF_ID", "CyberShake_Site_Ruptures.Source_ID=Ruptures.Source_ID", "CyberShake_Site_Ruptures.Rupture_ID=Ruptures.Rupture_ID"])
        elif table1=="CyberShake_Sites":
            if table2=="Studies":
                added_tables.append("CyberShake_Runs")
                self.add_from(["CyberShake_Runs"])
                self.add_where(["CyberShake_Runs.Site_ID=CyberShake_Sites.CS_Site_ID", "CyberShake_Runs.Study_ID=Studies.Study_ID"])
        elif table1=="IM_Types":
            if table2=="PeakAmplitudes":
                self.add_where(["IM_Types.IM_Type_ID=PeakAmplitudes.IM_Type_ID"])
        elif table1=="PeakAmplitudes":
            if table2=="Ruptures":
                self.add_where(["Ruptures.Source_ID=PeakAmplitudes.Source_ID", "Ruptures.Rupture_ID=PeakAmplitudes.Rupture_ID"])
            elif table2=="Rupture_Variations":
                self.add_where(["Rupture_Variations.Source_ID=PeakAmplitudes.Source_ID", "Rupture_Variations.Rupture_ID=PeakAmplitudes.Rupture_ID", "Rupture_Variations.Rup_Var_ID=PeakAmplitudes.Rup_Var_ID"])
        elif table1=="Rupture_Variations":
            #Rupture_Variations, Ruptures
            if table2=="Ruptures":
                self.add_where(["Rupture_Variations.ERF_ID=Ruptures.ERF_ID", "Rupture_Variations.Source_ID=Ruptures.Source_ID", "Rupture_Variations.Rupture_ID=Ruptures.Rupture_ID"])
        return added_tables


def construct_queries(model, dp, filter_list, event_list):
    query = Query()
    #Add model
    (from_tables, where_clauses) = model.get_query()
    query.add_from(from_tables)
    query.add_where(where_clauses)
    #Add data product
    (select_fields, from_tables) = dp.get_query()
    query.add_select(select_fields)
    query.add_from(from_tables)
    if dp.get_distinct()==True:
        query.set_distinct(True)
    #Add metadata tables
    (metadata_select, metadata_from) = dp.get_metadata_query()
    query.add_select(metadata_select)
    query.add_from(metadata_from)
    for f in filter_list:
        #If we're filtering on IMs, restrict to RotD50, unless it's PGA or PGV
        if f.get_data_product()==filters.FilterDataProducts.IMS:
            query.add_from(["IM_Types"])
            query.add_where(["IM_Types.IM_Type_Component='RotD50'"])
        (where_fields, from_tables) = f.get_query()
        #print("Filter %s adds from tables %s and where fields %s." % (f.get_name(), from_tables, where_fields))
        query.add_from(from_tables)
        fp = f.get_filter_params()
        quote = ""
        if not f.is_numeric():
            quote = "'" 
        if fp==filters.FilterParams.SINGLE_VALUE:
            if f.get_contains()==True:
                query.add_where(["%s LIKE %s%%%s%%%s" % (where_fields[0], quote, f.get_value(), quote)])
            else:
                #Check for PGA, PGV - if so, remove the RotD50 match, use 'IM_Type_Measure' for the where,
                #and change the select from IM_Types.IM_Type_Value and IM_Types.IM_Type_Component to IM_Types.IM_Type_Measure
                if f.get_name()=="Intensity Measure Period" and (f.get_value()=='PGA' or f.get_value()=='PGV'):
                    query.remove_select(['IM_Types.IM_Type_Value','IM_Types.IM_Type_Component'])
                    query.add_select(['IM_Types.IM_Type_Measure'])
                    query.remove_where(["IM_Types.IM_Type_Component='RotD50'"])
                    query.add_where(["IM_Type_Measure='%s'" % f.get_value()])
                else:
                    query.add_where(["%s=%s%s%s" % (where_fields[0], quote, f.get_value(), quote)])
        elif fp==filters.FilterParams.MULTIPLE_VALUES:
            where_clauses = []
            for v in f.get_values():
                if f.get_contains()==True:
                    where_clauses.append(["%s LIKE %s%%%s%%%s" % (where_fields[0], quote, v, quote)])
                else:
                    where_clauses.append("%s=%s%s%s" % (where_fields[0], quote, v, quote))
            query.add_where(["(%s)" % " or ".join(where_clauses)])
        elif fp==filters.FilterParams.VALUE_RANGE:
            #This filter makes no sense with a contains, so let's not worry about it
            (min, max) = f.get_values()
            where_clause = "%s>=%s%s%s and %s<=%s%s%s" % (where_fields[0], quote, min, quote, where_fields[0], quote, max, quote)
            query.add_where([where_clause])
        #Check sort
        if f.get_sort()<0:
            #Sort in reverse
            sort_clause = 'order by %s desc' % (f.where_fields[0])
            query.set_sort(sort_clause)
        elif f.get_sort()>0:
            #Sort in ascending
            sort_clause = 'order by %s asc' % (f.where_fields[0])
            query.set_sort(sort_clause)
    #If specific events are specified, add these
    if event_list is not None:
        #Use Rupture_Variations table to do the filtering
        query.add_from(["Rupture_Variations"])
        where_clauses = []
        for e in event_list:
            where_clause = '(Rupture_Variations.Source_ID=%d and Rupture_Variations.Rupture_ID=%d and Rupture_Variations.Rup_Var_ID=%d)' % (e[0], e[1], e[2])
            where_clauses.append(where_clause)
        query.add_where(['(%s)' % (" OR ".join(where_clauses))])
    #Need to join any unconnected tables
    query.connect_tables()
    return query