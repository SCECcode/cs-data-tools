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

'''Utility to construct a SQLite database which tracks the number of rupture variations per rupture for a given study.
This should be much faster than hitting the database over the network when we want to estimate data sizes.'''

import sys
import os
import pymysql
import sqlite3
import argparse
import utilities

def parse_args():
    parser = argparse.ArgumentParser(prog='Construct RV DB', description='Builds a SQLite DB for quick retrieval of the # of rupture variations per rupture.')
    parser.add_argument('-c', '--config-file', dest='config_file', action='store', default='focal.cfg', help='Path to config file with connection information to DB.')
    parser.add_argument('-s', '--study-names', dest='study_names', action='store', default=None, help='Comma-separated list of study names for which to populate the DB (required).')
    parser.add_argument('-o', '--output-filename', dest='output_filename', action='store', default='num_rvs.sqlite', help="Path to output SQLite file.")
    args = parser.parse_args()
    args_dict = dict()
    if args.study_names is None:
        print("At least one study name is required, aborting.", file=sys.stderr)
        sys.exit(utilities.ExitCodes.MISSING_ARGUMENTS)
    args_dict['study_names'] = args.study_names
    args_dict['config_file'] = args.config_file
    args_dict['output_filename'] = args.output_filename
    return args_dict


def generate_db(args_dict, config_dict):
    try:
        if config_dict['type'].lower()=='mysql':
            from_conn = pymysql.connect(host=config_dict["host"], user=config_dict["user"], passwd=config_dict["password"], db=config_dict['db'])
        elif config_dict['type'].lower()=='sqlite':
            from_conn = sqlite3.connect(config_dict['db_path'])
        else:
            print("Database type %s not recognized, aborting.", file=sys.stderr)
            sys.exit(utilities.ExitCodes.DATABASE_CONNECTION_ERROR)
    except Exception as e:
        error_str = "Error connecting to %s database" % config_dict['type']
        if config_dict['type'].lower()=='mysql':
            error_str = "%s %s on host %s with username %s and password %s, aborting." % (error_str, config_dict['db'], config_dict['host'], config_dict['user'], config_dict['password'])
        elif config_dict['type'].lower()=='sqlite':
            error_str = "%s %s, aborting." % (error_str, config_dict['db_path'])
        print(error_str, file=sys.stderr)
        print(e)
        sys.exit(utilities.ExitCodes.DATABASE_CONNECTION_ERROR)
    from_cur = from_conn.cursor()
    try:
        to_conn = sqlite3.connect(args_dict['output_filename'])
    except Exception as e:
        print("Error connecting to SQLite database %s, aborting." % (config_dict['db_path']), file=sys.stderr)
        print(e)
        sys.exit(utilities.ExitCodes.DATABASE_CONNECTION_ERROR)
    to_cur = to_conn.cursor()
    studies = args_dict['study_names'].split(",")
    print(studies)
    for s in studies:
        #First, grab ERF_ID and Rup_Var_Scenario_ID for the study from one of the study runs
        query = 'select CyberShake_Runs.ERF_ID, CyberShake_Runs.Rup_Var_Scenario_ID ' \
            'from CyberShake_Runs, Studies ' \
            'where Studies.Study_Name="%s" and Studies.Study_ID=CyberShake_Runs.Study_ID ' \
            'order by CyberShake_Runs.Run_ID asc limit 1' % (s)
        print(query)
        from_cur.execute(query)
        (erf_id, rup_var_scenario_id) = from_cur.fetchone()
        query = 'select Ruptures.Source_ID, Ruptures.Rupture_ID, count(Rupture_Variations.Rup_Var_ID) ' \
            'from Ruptures, Rupture_Variations ' \
            'where Rupture_Variations.ERF_ID=Ruptures.ERF_ID and Ruptures.Source_ID=Rupture_Variations.Source_ID and Ruptures.Rupture_ID=Rupture_Variations.Rupture_ID and ' \
            'Ruptures.ERF_ID=%d and Rupture_Variations.Rup_Var_Scenario_ID=%d ' \
            'group by Rupture_Variations.Source_ID, Rupture_Variations.Rupture_ID' % (erf_id, rup_var_scenario_id)
        print(query)
        from_cur.execute(query)
        res = from_cur.fetchall()
        #Construct schema in target DB, if it doesn't exist
        create_table_cmd = 'CREATE TABLE IF NOT EXISTS Rupture_Variation_Counts ' \
            '(Study_Name TEXT, Source_ID INTEGER, Rupture_ID INTEGER, Num_Rup_Vars INTEGER)'
        to_cur.execute(create_table_cmd)
        print("Inserting values into SQLite db.")
        for r in res:
            insert_cmd = 'INSERT INTO Rupture_Variation_Counts VALUES ("%s", %d, %d, %d)' % (s, int(r[0]), int(r[1]), int(r[2]))
            to_cur.execute(insert_cmd)
        to_conn.commit()
    to_conn.close()
    from_conn.close()

def run_main():
    print(sys.argv)
    args_dict = parse_args()
    config_dict = utilities.read_config(args_dict['config_file'])
    generate_db(args_dict, config_dict)

if __name__=="__main__":
    run_main()