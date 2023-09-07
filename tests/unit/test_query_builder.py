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
import filecmp
import shutil

#Add src directory to find imports 
full_path = os.path.abspath(sys.argv[0])
path_add = os.path.dirname(os.path.dirname(os.path.dirname(full_path)))
sys.path.append("%s/src" % path_add)

import query_build.run_query_builder as run_query_builder

class TestQueryBuilder(unittest.TestCase):
    '''Unit tests for query builder'''

    @classmethod
    def setUpClass(self):
        if not os.path.exists('tmpdir'):
            os.mkdir('tmpdir')
        shutil.copy('inputs/unittest.site_name.json', 'tmpdir')
        shutil.copy('inputs/unittest.site_name.query', 'tmpdir')
        shutil.copy('inputs/unittest.event_info.json', 'tmpdir')
        shutil.copy('inputs/unittest.event_info.query', 'tmpdir')
        shutil.copy('inputs/unittest.IMs.json', 'tmpdir')
        shutil.copy('inputs/unittest.IMs.query', 'tmpdir')
        shutil.copy('inputs/unittest.Seis.json', 'tmpdir')
        shutil.copy('inputs/unittest.Seis.query', 'tmpdir')

    @classmethod
    def tearDownClass(self):
        if os.path.exists('tmpdir'):
            shutil.rmtree('tmpdir')

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

    def testQuerySiteInfo(self):
        input_file = 'tmpdir/unittest.site_name.json'
        reference_output_file = 'tmpdir/unittest.site_name.query'
        test_output_file = 'tmpdir/unittest.site_name.output.query'
        argv = ['-i', input_file, '-o', test_output_file]
        run_query_builder.run_main(argv)
        if not os.path.exists(test_output_file):
            self.fail("Output file %s was not created." % test_output_file)
        self.assertTrue(self.compare_query_files(reference_output_file, test_output_file), "Test query file %s does not match reference file %s." % (test_output_file, reference_output_file))

    def testQueryEventInfo(self):
        input_file = 'tmpdir/unittest.event_info.json'
        reference_output_file = 'tmpdir/unittest.event_info.query'
        test_output_file = 'tmpdir/unittest.event_info.output.query'
        argv = ['-i', input_file, '-o', test_output_file]
        run_query_builder.run_main(argv)
        if not os.path.exists(test_output_file):
            self.fail("Output file %s was not created." % test_output_file)
        self.assertTrue(self.compare_query_files(reference_output_file, test_output_file), "Test query file %s does not match reference file %s." % (test_output_file, reference_output_file))

    def testQueryIMs(self):
        input_file = 'tmpdir/unittest.IMs.json'
        reference_output_file = 'tmpdir/unittest.IMs.query'
        test_output_file = 'tmpdir/unittest.IMs.output.query'
        argv = ['-i', input_file, '-o', test_output_file]
        run_query_builder.run_main(argv)
        if not os.path.exists(test_output_file):
            self.fail("Output file %s was not created." % test_output_file)
        self.assertTrue(self.compare_query_files(reference_output_file, test_output_file), "Test query file %s does not match reference file %s." % (test_output_file, reference_output_file))
    
    def testQuerySeismograms(self):
        input_file = 'tmpdir/unittest.Seis.json'
        reference_output_file = 'tmpdir/unittest.Seis.query'
        test_output_file = 'tmpdir/unittest.Seis.output.query'
        argv = ['-i', input_file, '-o', test_output_file]
        run_query_builder.run_main(argv)
        if not os.path.exists(test_output_file):
            self.fail("Output file %s was not created." % test_output_file)
        self.assertTrue(self.compare_query_files(reference_output_file, test_output_file), "Test query file %s does not match reference file %s." % (test_output_file, reference_output_file))

if __name__=='__main__':
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestQueryBuilder)
    rc = unittest.TextTestRunner(verbosity=2).run(test_suite)
    sys.exit(not rc.wasSuccessful())