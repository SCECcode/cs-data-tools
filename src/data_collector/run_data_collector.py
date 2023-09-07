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
import argparse
import urllib.request
import timeit
import struct

#Add one directory level above to path to find imports
full_path = os.path.abspath(sys.argv[0])
path_add = os.path.dirname(os.path.dirname(full_path))
sys.path.append(path_add)

import utils.utilities as utilities

debug = False

def parse_args(argv):
    global debug
    parser = argparse.ArgumentParser(prog='Data Collector', description='Takes CyberShake data request URLs, retrieves them, and extracts desired results.')
    parser.add_argument('-i', '--input-filename', dest='input_filename', action='store', default=None, help="Path to file containing the URLs and variation IDs.")
    parser.add_argument('-o', '--output-directory', dest='output_directory', action='store', default=".", help="Path to output directory to store files in.")
    parser.add_argument('-t', '--temp-directory', dest='temp_directory', action='store', default=".", help="Path to temporary directory to store files before extraction.")
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Turn on debug statements.')
    parser.add_argument('-v', '--version', dest='version', action='store_true', default=False, help="Show version number and exit.")
    args = parser.parse_args(args=argv)
    args_dict = dict()
    if args.version==True:
        print("Version: %s" % utilities.get_version())
        sys.exit(utilities.ExitCodes.NO_ERROR)
    if args.input_filename is None:
        print("Path to input file must be provided, aborting.", file=sys.stderr)
        sys.exit(utilities.ExitCodes.MISSING_ARGUMENTS)
    args_dict['input_filename'] = args.input_filename
    output_directory = args.output_directory
    if output_directory is None:
        output_directory = "."
    args_dict['output_directory'] = output_directory
    output_directory = args.output_directory
    if output_directory is None:
        output_directory = "."
    #If output_directory doesn't exist, create it
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    temp_directory = args.temp_directory
    if args.temp_directory is None:
        temp_directory = "."
    if not os.path.exists(temp_directory):
        os.makedirs(temp_directory)
    args_dict['temp_directory'] = temp_directory
    if args.debug==True:
        debug = True
    return args_dict
    

def retrieve_files(args_dict):
    global debug
    input_file = args_dict['input_filename']
    local_filenames = []
    with open(input_file, 'r') as fp_in:
        data = fp_in.readlines()
        num_files = len(data)
        for i, line in enumerate(data):
            print("Downloading file %d of %d." % (i+1, num_files))
            (url, rvs) = line.strip().split()
            #Use directory hierarchy of temp_directory/site_id/run_id
            (protocol, blank, prefix, site_name, run_id, basename) = url.split("/")
            local_directory = "%s/%s/%s" % (args_dict['temp_directory'], site_name, run_id)
            if not os.path.exists(local_directory):
                os.makedirs(local_directory)
            local_filename = "%s/%s" % (local_directory, basename)
            local_filenames.append(local_filename)
            if debug:
                print("File URL: %s" % url)
            url_data = urllib.request.urlopen(url).read()
            with open(local_filename, 'wb') as fp_out:
                fp_out.write(url_data)
                fp_out.flush()
                fp_out.close()
        fp_in.close()
    return local_filenames

def extract_rvs(args_dict):
    input_file = args_dict['input_filename']
    with open(input_file, 'r') as fp_in:
        data = fp_in.readlines()
        num_files = len(data)
        for i, line in enumerate(data):
            if (i%100==0):
                print("Extracting rupture variations from file %d of %d." % ((i+1), num_files))
            (url, rvs) = line.strip().split()
            (protocol, blank, prefix, site_name, run_id, basename) = url.split("/")
            rv_list = []
            for rv in rvs.split(","):
                rv_list.append(int(rv))
            local_rupture_directory = "%s/%s/%s" % (args_dict['temp_directory'], site_name, run_id)
            local_rupture_filename = "%s/%s" % (local_rupture_directory, url.rsplit("/", 1)[1])
            sizeof_float = 4
            num_components = 2
            with open(local_rupture_filename, 'rb') as fp_rup_in:
                while len(rv_list)>0:
                    #Read next header
                    header_str = fp_rup_in.read(56)
                    #If we're out of data
                    if header_str=='':
                        break
                    rv = struct.unpack('i', header_str[32:36])[0]
                    nt = struct.unpack('i', header_str[40:44])[0]
                    if rv in rv_list:
                        rv_data = fp_rup_in.read(num_components*sizeof_float*nt)
                        #Local RV filename is <output directory>/Seismogram_<site name>_<run_id>_<source id>_<rupture_id>_<rv_id>.grm
                        filename_pieces = basename.split(".")[0].split("_")
                        source_id = int(filename_pieces[2])
                        rupture_id = int(filename_pieces[3])
                        local_rv_filename = "%s/Seismogram_%s_%s_%s_%s_%s.grm" % (args_dict['output_directory'], site_name, run_id, source_id, rupture_id, rv)
                        with open(local_rv_filename, 'wb') as fp_out:
                            fp_out.write(header_str)
                            fp_out.write(rv_data)
                            fp_out.flush()
                            fp_out.close()
                        rv_list.remove(rv)
                    else:
                        fp_rup_in.seek(num_components*sizeof_float*nt, 1)
                if len(rv_list)!=0:
                    print("Couldn't find rupture variation(s) %s in file %s, aborting." % (str(rv_list), local_rupture_filename), file=sys.stderr)
                    fp_rup_in.close()
                    fp_in.close()
                    sys.exit(utilities.ExitCodes.FILE_PARSING_ERROR)
                fp_rup_in.close()
        fp_in.close()
    print("Finished extracting rupture variations to %s." % (args_dict['output_directory']))
    
def delete_temp_files(temp_directory, local_filenames):
    print("Removing temporary files from %s." % temp_directory)
    #Just make sure they start with 'Seismogram' and end with '.grm'
    for f in local_filenames:
        if f.find('Seismogram')>-1 and f[-4:]=='.grm':
            os.remove(f)

def run_main(argv):
    args_dict = parse_args(argv)
    local_filenames = retrieve_files(args_dict)
    extract_rvs(args_dict)
    delete_temp_files(args_dict['temp_directory'], local_filenames)

if __name__=="__main__":
    run_main(sys.argv[1:])
    sys.exit(0)