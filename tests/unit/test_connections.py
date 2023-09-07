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

import os
import sys
import unittest
import shutil
import filecmp
import pymysql
import sqlite3
import requests

#Add src directory to find imports 
full_path = os.path.abspath(sys.argv[0])
path_add = os.path.dirname(os.path.dirname(os.path.dirname(full_path)))
sys.path.append("%s/src" % path_add)

import db_wrapper.run_database_wrapper as run_database_wrapper

class TestConnections(unittest.TestCase):
   '''Unit tests to test DB connection, and access to seismograms'''

   def testDBAccess(self):
      #Test the default *.cfg file in db_wrapper
      cfg_file = run_database_wrapper.get_default_config()
      try:
         #Confirm you can authenticate
         cfg_dict = run_database_wrapper.read_input(cfg_file)
         if cfg_dict['type']=='MySQL':
            conn = pymysql.connect(host=cfg_dict['host'],db=cfg_dict['db'],user=cfg_dict['user'],passwd=cfg_dict['password'])
            #Run simple query, make sure it has a PeakAmps table
            cur = conn.cursor()
            query = 'show create table PeakAmplitudes'
            cur.execute(query)
            res = cur.fetchall()
            self.assertEqual(len(res), 1, "Error checking PeakAmplitudes schema in the %s MySQL database on host %s." % (cfg_dict['db'], cfg_dict['host']))
            conn.close()
         elif cfg_dict['type']=='SQLite':
            conn = sqlite3.connect(cfg_dict['db_path'])
            cur = conn.cursor()
            query = '.schema PeakAmplitudes'
            cur.execute(query)
            res = cur.fetchall()
            self.assertEqual(len(res), 1, "Error checking PeakAmplitudes schema in the %s SQLite database." % (cfg_dict['db_path'], cfg_dict['host']))
            conn.close()           
      except:
         self.fail("Error connecting using default configuration file %s." % cfg_file)


   def testSeisAccess(self):
      for (k, v) in run_database_wrapper.globus_dict.items():
         try:
            response = requests.get(v)
            self.assertEqual(200, response.status_code, "Did not get valid response from URL %s, the prefix for seismograms from %s." % (v, k))
         except:
            self.fail("Could not connect to URL %s, the prefix for seismograms from %s." % (v, k))
      

if __name__=='__main__':
   test_suite = unittest.TestLoader().loadTestsFromTestCase(TestConnections)
   rc = unittest.TextTestRunner(verbosity=2).run(test_suite)
   sys.exit(not rc.wasSuccessful())