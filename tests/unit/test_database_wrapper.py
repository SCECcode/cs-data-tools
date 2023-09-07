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

import db_wrapper.run_database_wrapper as run_database_wrapper

class TestDatabaseWrapper(unittest.TestCase):
    '''Unit tests for database wrapper'''
    
    @classmethod
    def setUpClass(self):
        if not os.path.exists("tmpdir"):
            os.mkdir('tmpdir')
        shutil.copy('inputs/unittest.site_name.query', 'tmpdir')
        shutil.copy('inputs/unittest.site_name.csv', 'tmpdir')
        shutil.copy('inputs/unittest.event_info.query', 'tmpdir')
        shutil.copy('inputs/unittest.event_info.csv', 'tmpdir')
        shutil.copy('inputs/unittest.IMs.query', 'tmpdir')
        shutil.copy('inputs/unittest.IMs.csv', 'tmpdir')
        shutil.copy('inputs/unittest.Seis.query', 'tmpdir')
        shutil.copy('inputs/unittest.Seis.csv', 'tmpdir')
        shutil.copy('inputs/unittest.Seis.urls', 'tmpdir')
        

    @classmethod
    def tearDownClass(self):
        if os.path.exists('tmpdir'):
            shutil.rmtree('tmpdir')

    def testDBSiteInfo(self):
        input_file = 'tmpdir/unittest.site_name.query'
        reference_output_file = 'tmpdir/unittest.site_name.csv'
        test_output_file = 'tmpdir/unittest.site_name.output.csv'
        argv = ['-i', input_file, '-o', test_output_file]
        run_database_wrapper.run_main(argv)
        if not os.path.exists(test_output_file):
            self.fail("Output file %s was not created." % test_output_file)
        self.assertTrue(filecmp.cmp(reference_output_file, test_output_file), "Test query file %s does not match reference file %s." % (test_output_file, reference_output_file))


    def testDBEventInfo(self):
        input_file = 'tmpdir/unittest.event_info.query'
        reference_output_file = 'tmpdir/unittest.event_info.csv'
        test_output_file = 'tmpdir/unittest.event_info.output.csv'
        argv = ['-i', input_file, '-o', test_output_file]
        run_database_wrapper.run_main(argv)
        if not os.path.exists(test_output_file):
            self.fail("Output file %s was not created." % test_output_file)
        self.assertTrue(filecmp.cmp(reference_output_file, test_output_file), "Test query file %s does not match reference file %s." % (test_output_file, reference_output_file))


    def testDBIMs(self):
        input_file = 'tmpdir/unittest.IMs.query'
        reference_output_file = 'tmpdir/unittest.IMs.csv'
        test_output_file = 'tmpdir/unittest.IMs.output.csv'
        argv = ['-i', input_file, '-o', test_output_file]
        run_database_wrapper.run_main(argv)
        if not os.path.exists(test_output_file):
            self.fail("Output file %s was not created." % test_output_file)
        self.assertTrue(filecmp.cmp(reference_output_file, test_output_file), "Test query file %s does not match reference file %s." % (test_output_file, reference_output_file))


    def testDBSeismograms(self):
        input_file = 'tmpdir/unittest.Seis.query'
        reference_output_file = 'tmpdir/unittest.Seis.csv'
        test_output_file = 'tmpdir/unittest.Seis.output.csv'
        argv = ['-i', input_file, '-o', test_output_file]
        run_database_wrapper.run_main(argv)
        if not os.path.exists(test_output_file):
            self.fail("Output file %s was not created." % test_output_file)
        self.assertTrue(filecmp.cmp(reference_output_file, test_output_file), "Test query file %s does not match reference file %s." % (test_output_file, reference_output_file))
        #Check URL files also
        if not os.path.exists('tmpdir/unittest.Seis.urls'):
            self.fail("Output file unittest.Seis.urls was not created.")
        self.assertTrue(filecmp.cmp(reference_output_file, test_output_file), "Test query file %s does not match reference file %s." % (test_output_file, reference_output_file))


if __name__=='__main__':
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestDatabaseWrapper)
    rc = unittest.TextTestRunner(verbosity=2).run(test_suite)
    sys.exit(not rc.wasSuccessful())