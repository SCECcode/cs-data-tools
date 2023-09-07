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

import data_collector.run_data_collector as run_data_collector

class TestDataCollector(unittest.TestCase):
    '''Unit tests for data collector'''

    @classmethod
    def setUpClass(self):
        if not os.path.exists("tmpdir"):
            os.mkdir('tmpdir')
        shutil.copy('inputs/unittest.Seis.query', 'tmpdir')
        shutil.copy('inputs/unittest.Seis.csv', 'tmpdir')
        shutil.copy('inputs/unittest.Seis.urls', 'tmpdir')
        if not os.path.exists(os.path.join('tmpdir', 'test_output')):
            os.mkdir(os.path.join('tmpdir', 'test_output'))

    @classmethod
    def tearDownClass(self):
        if os.path.exists('tmpdir'):
            shutil.rmtree('tmpdir')
        if os.path.exists('USC'):
            shutil.rmtree('USC')   

    def testDataSeismograms(self):
        input_file = 'tmpdir/unittest.Seis.urls'
        output_dir = 'tmpdir/test_output'
        reference_output_dir = 'outputs'
        args = ['-i', input_file, '-o', output_dir]
        run_data_collector.run_main(args)
        reference_output_files = ['Seismogram_USC_9306_12_0_144.grm', 'Seismogram_USC_9306_124_262_50.grm', 'Seismogram_USC_9306_124_261_38.grm', 'Seismogram_USC_9306_124_266_25.grm']
        for f in reference_output_files:
            if not os.path.exists(os.path.join(output_dir, f)):
                self.fail('Seismogram file %s was not created.' % f)
            ref_file = os.path.join(reference_output_dir, f)
            test_file = os.path.join(output_dir, f)
            self.assertTrue(filecmp.cmp(ref_file, test_file), 'Reference file %s does not match test file %s.' % (ref_file, test_file))
        
if __name__=='__main__':
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestDataCollector)
    rc = unittest.TextTestRunner(verbosity=2).run(test_suite)
    sys.exit(not rc.wasSuccessful())