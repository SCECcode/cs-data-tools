#!/usr/bin/env python3

import sys
import os
import argparse
import pymysql
import datetime
import sqlite3

#Add one directory level above to path to find imports
full_path = os.path.abspath(sys.argv[0])
path_add = os.path.dirname(os.path.dirname(full_path))
sys.path.append(path_add)

import utils.utilities as utilities
import utils.filters as filters
import utils.data_products as data_products

globus_dict = dict()
globus_dict['Study 15.12'] = "https://g-41ed52.a78b8.36fe.data.globus.org"

suffix_dict = dict()
suffix_dict['Study 15.12'] = "_bb"
suffix_dict['Study 22.12 BB'] = "_bb"

def parse_args(argv):
    parser = argparse.ArgumentParser(prog='Database Wrapper', description='Takes CyberShake data request queries, executes them, and delivers results + paths to on-disk data.')
    parser.add_argument('-i', '--input-filename', dest='input_filename', action='store', default=None, help="Path to query file describing the data request.")
    parser.add_argument('-o', '--output-filename', dest='output_filename', action='store', default=None, help="Path to output file, with query results.")
    parser.add_argument('-c', "--config-filename", dest='config_filename', action='store', default='focal.cfg', help="Path to database configuration file.")
    parser.add_argument('-of', '--output-format', dest='output_format', action='store', default='csv', help='Output format for database results (either "csv" or "sqlite")')
    args = parser.parse_args(args=argv)
    args_dict = dict()
    if args.input_filename is None:
        print("Path to input file must be provided, aborting.", file=sys.stderr)
        sys.exit(utilities.ExitCodes.MISSING_ARGUMENTS)
    args_dict['input_filename'] = args.input_filename
    if args.output_filename is None:
        dt_tuple = datetime.datetime.now().timetuple()
        output_filename = "csdata.%02d%02d%02d_%02d%02d%04d.data" % (dt_tuple.tm_hour, dt_tuple.tm_min, dt_tuple.tm_sec, dt_tuple.tm_mday, dt_tuple.tm_mon, dt_tuple.tm_year)
    else:
        output_filename = args.output_filename
    args_dict['output_filename'] = output_filename
    if args.config_filename is None:
        config_filename = 'focal.cfg'
    else:
        config_filename = args.config_filename
    args_dict['config_filename'] = config_filename
    args_dict['output_format'] = args.output_format
    return args_dict

def read_config(config_file):
    config_dict = dict()
    with open(config_file, "r") as fp_in:
        data = fp_in.readlines()
        for line in data:
            (key, value) = line.split("=")
            config_dict[key.strip()] = value.strip()
        fp_in.close()
    return config_dict

def read_input(input_filename):
    try:
        input_dict = dict()
        with open(input_filename, 'r') as fp_in:
            data = fp_in.readlines()
            for line in data:
                #Can have values which also contain '=', so only split into 2 pieces
                (key, value) = line.strip().split("=", 1)
                input_dict[key.strip()] = value.strip()
            fp_in.close()
    except Exception as e:
        print("Error reading from input file %s, aborting." % input_filename, file=sys.stderr)
        print(e)
        sys.exit(utilities.ExitCodes.BAD_FILE_PATH)
    return input_dict

def execute_queries(config_dict, input_dict):
    try:
        if config_dict['type'].lower()=='mysql':
            conn = pymysql.connect(host=config_dict["host"], user=config_dict["user"], passwd=config_dict["password"], db=config_dict['db'])
        elif config_dict['type'].lower()=='sqlite':
            conn = sqlite3.connect(config_dict['db_path'])
        else:
            print("Database type %s not recognized, aborting.", file=sys.stderr)
            sys.exit(utilities.ExitCodes.DATABASE_CONNECTION_ERROR)
    except Exception as e:
        print("Error connecting to database %s on host %s, aborting." % (config_dict['db'], config_dict['host']), file=sys.stderr)
        print(e)
        sys.exit(utilities.ExitCodes.DATABASE_CONNECTION_ERROR)
    #Use DictCursor in case we're retrieving seismograms
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    query = 'select %s from %s where %s' % (input_dict['select'], input_dict['from'], input_dict['where'])
    try:
        cur.execute(query)
    except Exception as e:
        print("Error executing database query '%s', aborting." % query)
        cur.close()
        conn.close()
        print(e)
        sys.exit(utilities.ExitCodes.DATABASE_COMMAND_ERROR)
    res = cur.fetchall()
    #Results length 0 isn't necessarily an error
    cur.close()
    conn.close()
    return res

def write_results(result_set, args_dict, input_dict, config_dict):
    #Mapping of Python types to SQLite types
    sqlite_type_dict = dict()
    sqlite_type_dict['str'] = 'TEXT'
    sqlite_type_dict['int'] = 'INTEGER'
    sqlite_type_dict['float'] = 'REAL'
    #Write data and metadata to output file
    try:
        if args_dict['output_format'].lower()=='csv':
            filename = args_dict['output_filename']
            if filename[-3:]!='csv':
                filename = "%s.csv" % (filename)
            with open(filename, 'w') as fp_out:
                #Write headers
                columns = input_dict['select'].split(",")
                columns_pretty = []
                for c in columns:
                    columns_pretty.append(utilities.get_field_alias(c.split(".")[1]))
                fp_out.write("%s\n" % ",".join(columns_pretty))
                #Write data
                for row in result_set:
                    #Quote any string datatypes
                    line_strs = []
                    #row.values() because we're using a DictCursor
                    for r in row.values():
                        if type(r)==str:
                            line_strs.append('"%s"' % r)
                        else:
                            line_strs.append(str(r))
                    fp_out.write("%s\n" % ",".join(line_strs))
                fp_out.flush()
                fp_out.close()
        elif args_dict['output_format'].lower()=='sqlite':
            print("Using sqlite format.")
            filename = args_dict['output_filename']
            if filename[-6:]!='sqlite':
                filename = "%s.sqlite" % (filename)
            conn = sqlite3.connect(filename)
            cur = conn.cursor()
            #Create schema
            create_table_cmd = 'CREATE TABLE CyberShake_Data'
            #Figure out datatype from first row of results
            #If results is empty, just make everything TEXT
            if len(result_set)>0:
                row_vals = []
                for r in result_set[1].values():
                    row_vals.append(r)
            create_columns = []
            columns = input_dict['select'].split(",")
            for i, c in enumerate(columns):
                column_type = type(row_vals[i]).__name__
                if column_type in sqlite_type_dict:
                    sqlite_type = sqlite_type_dict[column_type]
                else:
                    sqlite_type = 'TEXT'
                create_columns.append("%s %s" % (c.split('.')[1], sqlite_type))
            create_table_cmd = "%s (%s)" % (create_table_cmd, ', '.join(create_columns))
            cur.execute(create_table_cmd)
            for row in result_set:
                #Quote any string datatypes
                line_strs = []
                #row.values() because we're using a DictCursor
                for r in row.values():
                    if type(r)==str:
                        line_strs.append('"%s"' % r)
                    else:
                        line_strs.append(str(r))
                value_string = ", ".join(line_strs)
                insert_cmd = 'insert into CyberShake_Data values (%s)' % value_string
                cur.execute(insert_cmd)
            conn.commit()
            conn.close()
        else:
            print("Output format '%s' is unrecognized, aborting." % args_dict['output_format'], file=sys.stderr)
            sys.exit(utilities.ExitCodes.INVALID_ARGUMENTS)
    except Exception as e:
        print("Error writing data to output file %s, aborting." % (args_dict['output_filename']), file=sys.stderr)
        print(e)
        sys.exit(utilities.ExitCodes.FILE_WRITING_ERROR)
    #If we're doing seismograms, need to also write a file with all the URLs we need + rupture variations to extract
    #Also estimate data size
    if input_dict['data_product']=="Seismograms":
        seis_dict = dict()
        rup_file_total_mb = 0.0
        #Open connection to query # of rupture variations
        if config_dict['type'].lower()=='mysql':
            conn = pymysql.connect(host=config_dict["host"], user=config_dict["user"], passwd=config_dict["password"], db=config_dict['db'])
        elif config_dict['type'].lower()=='sqlite':
            conn = sqlite3.connect(config_dict['db_path'])
        cur = conn.cursor()
        for row in result_set:
            study_name = row['Study_Name']
            study_prefix = globus_dict[study_name]
            study_suffix = ".grm"
            rv_seis_size = utilities.get_rv_seismogram_size(study_name)
            #Add the '_bb' to seismogram filenames for broadband studies
            if study_name in suffix_dict:
                study_suffix = "%s%s" % (suffix_dict[study_name], study_suffix)
            #Need site name, run ID, source_ID, rupture_ID, rup_var_ID
            site_name = row['CS_Short_Name']
            run_id = row['Run_ID']
            source_id = row['Source_ID']
            rupture_id = row['Rupture_ID']
            rup_var_id = row['Rup_Var_ID']
            full_url = '%s/%s/%d/Seismogram_%s_%d_%d%s' % (study_prefix, site_name, run_id, site_name, source_id, rupture_id, study_suffix)
            if full_url in seis_dict:
                seis_dict[full_url] = "%s,%d" % (seis_dict[full_url], rup_var_id)
            else:
                seis_dict[full_url] = "%d" % (rup_var_id)
                #Figure out size
                num_rvs_query = 'select Studies.Study_Name, count(*) from Rupture_Variations, CyberShake_Runs, Studies ' \
                    'where Studies.Study_ID=CyberShake_Runs.Study_ID and CyberShake_Runs.Run_ID=%d and CyberShake_Runs.ERF_ID=Rupture_Variations.ERF_ID and CyberShake_Runs.Rup_Var_Scenario_ID=Rupture_Variations.Rup_Var_Scenario_ID and Rupture_Variations.Source_ID=%d and Rupture_Variations.Rupture_ID=%d' \
                    % (run_id, source_id, rupture_id)
                print(num_rvs_query)
                cur.execute(num_rvs_query)
                (study_name, num_rvs) = cur.fetchone()
                rup_file_total_mb += num_rvs*rv_seis_size/(1000000.0)
        conn.close()
        print("Temporary disk space required to download seismograms: %.1f MB" % (rup_file_total_mb))
        print("Disk space required for requested seismograms: %f MB" % (rv_seis_size*len(result_set)/(1000000.0)))
        url_filename = "%s.urls" % args_dict['output_filename'].rsplit(".", 1)[0]
        with open(url_filename, 'w') as fp_out:
            for key in seis_dict:
                fp_out.write("%s %s\n" % (key, seis_dict[key]))
            fp_out.flush()
            fp_out.close()


#Estimate both data size to download and extracted data
def estimate_data_size(result_set):

    for row in result_set:
        source_id = row['Source_ID']
        rupture_id = row['Rupture_ID']
            
        

def run_main(argv):
    args_dict = parse_args(argv[1:])
    config_dict = read_config(args_dict['config_filename'])
    input_dict = read_input(args_dict['input_filename'])
    result_set = execute_queries(config_dict, input_dict)
    write_results(result_set, args_dict, input_dict, config_dict)
    if input_dict['data_product']=='Seismograms':
        estimate_data_size(result_set)

if __name__=="__main__":
    run_main(sys.argv)
    sys.exit(0)