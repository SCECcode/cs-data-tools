#!/usr/bin/env python3

import sys
import os
import argparse
import pymysql
import datetime

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

def parse_args():
    parser = argparse.ArgumentParser(prog='Database Wrapper', description='Takes CyberShake data request queries, executes them, and delivers results + paths to on-disk data.')
    parser.add_argument('-i', '--input-filename', dest='input_filename', action='store', default=None, help="Path to query file describing the data request.")
    parser.add_argument('-o', '--output-filename', dest='output_filename', action='store', default=None, help="Path to output file, with query results.")
    parser.add_argument('-c', "--config-filename", dest='config_filename', action='store', default='focal.cfg', help="Path to database configuration file.")
    args = parser.parse_args()
    args_dict = dict()
    if args.input_filename is None:
        print("Path to input file must be provided, aborting.", file=sys.stderr)
        sys.exit(utilities.ExitCodes.MISSING_ARGUMENTS)
    args_dict['input_filename'] = args.input_filename
    if args.output_filename is None:
        dt_tuple = datetime.datetime.now().timetuple()
        output_filename = "csdatarequest.%02d%02d%02d_%02d%02d%04d.data" % (dt_tuple.tm_hour, dt_tuple.tm_min, dt_tuple.tm_sec, dt_tuple.tm_mday, dt_tuple.tm_mon, dt_tuple.tm_year)
    else:
        output_filename = args.output_filename
    args_dict['output_filename'] = output_filename
    if args.config_filename is None:
        config_filename = 'focal.cfg'
    else:
        config_filename = args.config_filename
    args_dict['config_filename'] = config_filename
    return args_dict

def read_config(config_file):
    config_dict = dict()
    with open(config_file, "r") as fp_in:
        data = fp_in.readlines()
        for line in data:
            (key, value) = line.split("=")
            config_dict[key.strip()] = value.strip()
        fp_in.close()
    print(config_dict)
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
        conn = pymysql.connect(host=config_dict["host"], user=config_dict["user"], passwd=config_dict["password"], db=config_dict['db'])
    except Exception as e:
        print("Error connecting to database %s on host %s, aborting." % (config_dict['db'], config_dict['host']), file=sys.stderr)
        print(e)
        sys.exit(utilities.ExitCodes.DATABASE_CONNECTION_ERROR)
    #Use DictCursor in case we're retrieving seismograms
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    query = 'select %s from %s where %s' % (input_dict['select'], input_dict['from'], input_dict['where'])
    print(query)
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

def write_results(result_set, output_filename, input_dict, output_format='csv'):
    #Write data and metadata to output file
    try:
        with open(output_filename, 'w') as fp_out:
            if output_format=='csv':
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
            else:
                print("Output format '%s' is unrecognized, aborting.", file=sys.stderr)
                fp_out.close()
                sys.exit(utilities.ExitCodes.INVALID_ARGUMENTS)
            fp_out.flush()
            fp_out.close()
    except Exception as e:
        print("Error writing data to output file %s, aborting." % (output_filename), file=sys.stderr)
        print(e)
        sys.exit(utilities.ExitCodes)
    #If we're doing seismograms, need to also write a file with all the URLs we need + rupture variations to extract
    if input_dict['data_product']=="Seismograms":
        seis_dict = dict()
        for row in result_set:
            study_name = row['Study_Name']
            study_prefix = globus_dict[study_name]
            study_suffix = ".grm"
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
        url_filename = "%s.urls" % output_filename.rsplit(".", 1)[0]
        with open(url_filename, 'w') as fp_out:
            for key in seis_dict:
                fp_out.write("%s %s\n" % (key, seis_dict[key]))
            fp_out.flush()
            fp_out.close()


def run_main():
    args_dict = parse_args()
    config_dict = read_config(args_dict['config_filename'])
    input_dict = read_input(args_dict['input_filename'])
    result_set = execute_queries(config_dict, input_dict)
    write_results(result_set, args_dict['output_filename'], input_dict)
    

if __name__=="__main__":
	run_main()
