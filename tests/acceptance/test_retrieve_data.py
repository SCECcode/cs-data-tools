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

#Add src directory to find imports 
full_path = os.path.abspath(sys.argv[0])
path_add = os.path.dirname(os.path.dirname(os.path.dirname(full_path)))
sys.path.append("%s/src" % path_add)

import retrieve_cs_data

class TestRetrieveData(unittest.TestCase):
    '''Test end-to-end data retrieval for the 4 products'''

    @classmethod
    def setUpClass(self):
        if not os.path.exists("tmpdir"):
            os.mkdir('tmpdir')

    @classmethod
    def tearDownClass(self):
        #if os.path.exists('tmpdir'):
        #    shutil.rmtree('tmpdir')
        if os.path.exists('USC'):
            shutil.rmtree('USC')   

    def compare_query_files(self, filename1, filename2):
        #Compare query files, ignoring the data_request_file field
        with open(filename1, 'r') as fp_in:
            data1 = fp_in.readlines()
            fp_in.close()
        with open(filename2, 'r') as fp_in:
            data2 = fp_in.readlines()
            fp_in.close()
        if len(data1)!=len(data2):
            return False
        for i in range(0, len(data1)):
            if data1[i].find("data_request_file")>-1:
                continue
            if data1[i]!=data2[i]:
                return False
        return True

    def testRetrieveEventInfo(self):
        input_file = 'inputs/accepttest.event_info.json'
        label = 'accept_event_info'
        output_dir = 'tmpdir'
        args = ['-i', input_file, '-o', output_dir, '-l', label]
        retrieve_cs_data.run_main(args)
        output_file = "tmpdir/csdata.%s.query" % (label)
        if not os.path.exists(output_file):
            self.fail("Output file %s not created." % output_file)  
        reference_output_file = 'outputs/accepttest.event_info.query'
        self.assertTrue(self.compare_query_files(reference_output_file, output_file), "Output file %s doesn't match reference file %s." % (output_file, reference_output_file))
        output_file = "tmpdir/csdata.%s.data.csv" % (label)
        if not os.path.exists(output_file):
            self.fail("Output file %s not created." % output_file)
        reference_output_file = 'outputs/accepttest.event_info.data.csv'
        self.assertTrue(filecmp.cmp(reference_output_file, output_file), "Output file %s doesn't match reference file %s." % (output_file, reference_output_file))

    def testRetrieveSiteInfo(self):
        input_file = 'inputs/accepttest.site_name.json'
        label = 'accept_site_name'
        output_dir = 'tmpdir'
        args = ['-i', input_file, '-o', output_dir, '-l', label]
        retrieve_cs_data.run_main(args)
        output_file = "tmpdir/csdata.%s.query" % (label)
        if not os.path.exists(output_file):
            self.fail("Output file %s not created." % output_file)  
        reference_output_file = 'outputs/accepttest.site_name.query'
        self.assertTrue(self.compare_query_files(reference_output_file, output_file), "Output file %s doesn't match reference file %s." % (output_file, reference_output_file))
        output_file = "tmpdir/csdata.%s.data.csv" % (label)
        if not os.path.exists(output_file):
            self.fail("Output file %s not created." % output_file)
        reference_output_file = 'outputs/accepttest.site_name.data.csv'
        self.assertTrue(filecmp.cmp(reference_output_file, output_file), "Output file %s doesn't match reference file %s." % (output_file, reference_output_file))

    def testRetrieveIMs(self):
        input_file = 'inputs/accepttest.IMs.json'
        label = 'accept_IMs'
        output_dir = 'tmpdir'
        args = ['-i', input_file, '-o', output_dir, '-l', label]
        retrieve_cs_data.run_main(args)
        output_file = "tmpdir/csdata.%s.query" % (label)
        if not os.path.exists(output_file):
            self.fail("Output file %s not created." % output_file)  
        reference_output_file = 'outputs/accepttest.IMs.query'
        self.assertTrue(self.compare_query_files(reference_output_file, output_file), "Output file %s doesn't match reference file %s." % (output_file, reference_output_file))
        output_file = "tmpdir/csdata.%s.data.csv" % (label)
        if not os.path.exists(output_file):
            self.fail("Output file %s not created." % output_file)
        reference_output_file = 'outputs/accepttest.IMs.data.csv'
        self.assertTrue(filecmp.cmp(reference_output_file, output_file), "Output file %s doesn't match reference file %s." % (output_file, reference_output_file))


    def testRetrieveSeismograms(self):
        input_file = 'inputs/accepttest.Seis.json'
        label = 'accept_Seis'
        output_dir = 'tmpdir'
        args = ['-i', input_file, '-o', output_dir, '-l', label]
        retrieve_cs_data.run_main(args)
        output_file = "tmpdir/csdata.%s.query" % (label)
        if not os.path.exists(output_file):
            self.fail("Output file %s not created." % output_file)  
        reference_output_file = 'outputs/accepttest.Seis.query'
        self.assertTrue(self.compare_query_files(reference_output_file, output_file), "Output file %s doesn't match reference file %s." % (output_file, reference_output_file))
        output_file = "tmpdir/csdata.%s.data.csv" % (label)
        if not os.path.exists(output_file):
            self.fail("Output file %s not created." % output_file)
        reference_output_file = 'outputs/accepttest.Seis.data.csv'
        self.assertTrue(filecmp.cmp(reference_output_file, output_file), "Output file %s doesn't match reference file %s." % (output_file, reference_output_file))
        output_file = "tmpdir/csdata.%s.urls" % (label)
        if not os.path.exists(output_file):
            self.fail("Output file %s not created." % output_file)
        reference_output_file = 'outputs/accepttest.Seis.urls'
        self.assertTrue(filecmp.cmp(reference_output_file, output_file), "Output file %s doesn't match reference file %s." % (output_file, reference_output_file))


if __name__=='__main__':
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestRetrieveData)
    rc = unittest.TextTestRunner(verbosity=2).run(test_suite)
    sys.exit(not rc.wasSuccessful())