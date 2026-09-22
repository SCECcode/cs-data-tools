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

import contextlib
import io
import json
import os
import shutil
import sys
import unittest

#Add src directory to find imports
full_path = os.path.abspath(sys.argv[0])
path_add = os.path.dirname(os.path.dirname(os.path.dirname(full_path)))
sys.path.append("%s/src" % path_add)

import input_gen.run_input_gen as run_input_gen
import query_build.run_query_builder as run_query_builder

#Top-level request variables the generator reads from the command line
FIXTURES = ('site_name', 'event_info', 'IMs', 'Seis')

#Command-line arguments reproducing each unit fixture's selection
FIXTURE_ARGS = {
    'site_name': ['-m', 'Study 22.12 LF', '-p', 'Site Info', '--filter', 'SITE_NAME=USC'],
    'event_info': ['-m', 'Study 22.12 LF', '-p', 'Event Info',
                   '--filter', 'SOURCE_NAME=Elsinore', '--filter', 'MAGNITUDE=7.0 7.5',
                   '--filter', 'MAGNITUDE_PARAMS=3', '--filter', 'SITE_NAME=USC'],
    'IMs': ['-m', 'Study 22.12 LF', '-p', 'Intensity Measures',
            '--filter', 'INTENSITY_MEASURE_PERIOD=2.0', '--filter', 'INTENSITY_MEASURE_PERIOD_PARAMS=1',
            '--filter', 'INTENSITY_MEASURE_VALUE=0.0 15.0', '--filter', 'INTENSITY_MEASURE_VALUE_PARAMS=3',
            '--filter', 'MAGNITUDE=7.15,7.25', '--filter', 'MAGNITUDE_PARAMS=2',
            '--filter', 'SOURCE_NAME=Elsinore', '--filter', 'SITE_NAME=USC'],
    'Seis': ['-m', 'Study 22.12 LF', '-p', 'Seismograms',
             '--filter', 'INTENSITY_MEASURE_PERIOD=2.0', '--filter', 'INTENSITY_MEASURE_PERIOD_PARAMS=1',
             '--filter', 'INTENSITY_MEASURE_VALUE=0.0 12.0', '--filter', 'INTENSITY_MEASURE_VALUE_PARAMS=3',
             '--filter', 'MAGNITUDE=7.15,7.25', '--filter', 'MAGNITUDE_PARAMS=2',
             '--filter', 'SOURCE_NAME=Elsinore', '--filter', 'SITE_NAME=USC'],
}

class TestInputGen(unittest.TestCase):
    '''Unit tests for the non-interactive input generator'''

    @classmethod
    def setUpClass(self):
        if not os.path.exists('tmpdir'):
            os.mkdir('tmpdir')
        for fixture in FIXTURES:
            shutil.copy('inputs/unittest.%s.json' % fixture, 'tmpdir')
            shutil.copy('inputs/unittest.%s.query' % fixture, 'tmpdir')

    @classmethod
    def tearDownClass(self):
        if os.path.exists('tmpdir'):
            shutil.rmtree('tmpdir')

    def load_json(self, filename):
        with open(filename, 'r') as fp_in:
            return json.load(fp_in)

    def sorted_filters(self, request_dict):
        return sorted(request_dict['filters'], key=lambda f: f['name'])

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

    def run_generator(self, argv):
        '''Run the generator on the given command-line arguments and return
        the parsed request JSON from stdout.'''
        fp_out = io.StringIO()
        fp_err = io.StringIO()
        with contextlib.redirect_stdout(fp_out):
            with contextlib.redirect_stderr(fp_err):
                run_input_gen.run_main(argv)
        return json.loads(fp_out.getvalue())

    def testFixtureSiteInfo(self):
        fixture = self.load_json('tmpdir/unittest.site_name.json')
        request_dict = self.run_generator(FIXTURE_ARGS['site_name'])
        self.assertEqual(self.sorted_filters(request_dict), self.sorted_filters(fixture))
        self.assertEqual(request_dict['model'], fixture['model'])
        self.assertEqual(request_dict['products'], fixture['products'])

    def testFixtureEventInfo(self):
        fixture = self.load_json('tmpdir/unittest.event_info.json')
        request_dict = self.run_generator(FIXTURE_ARGS['event_info'])
        self.assertEqual(self.sorted_filters(request_dict), self.sorted_filters(fixture))
        self.assertEqual(request_dict['model'], fixture['model'])
        self.assertEqual(request_dict['products'], fixture['products'])

    def testFixtureIMs(self):
        fixture = self.load_json('tmpdir/unittest.IMs.json')
        request_dict = self.run_generator(FIXTURE_ARGS['IMs'])
        self.assertEqual(self.sorted_filters(request_dict), self.sorted_filters(fixture))
        self.assertEqual(request_dict['model'], fixture['model'])
        self.assertEqual(request_dict['products'], fixture['products'])

    def testFixtureSeismograms(self):
        fixture = self.load_json('tmpdir/unittest.Seis.json')
        request_dict = self.run_generator(FIXTURE_ARGS['Seis'])
        self.assertEqual(self.sorted_filters(request_dict), self.sorted_filters(fixture))
        self.assertEqual(request_dict['model'], fixture['model'])
        self.assertEqual(request_dict['products'], fixture['products'])

    def testStdoutMode(self):
        #The JSON goes to stdout and the summary to stderr
        fp_out = io.StringIO()
        fp_err = io.StringIO()
        with contextlib.redirect_stdout(fp_out):
            with contextlib.redirect_stderr(fp_err):
                run_input_gen.run_main(FIXTURE_ARGS['site_name'])
        request_dict = json.loads(fp_out.getvalue())
        fixture = self.load_json('tmpdir/unittest.site_name.json')
        self.assertEqual(self.sorted_filters(request_dict), self.sorted_filters(fixture))
        self.assertIn("You have generated the following data product request", fp_err.getvalue())

    def testStdinRoundTrip(self):
        #The generator's stdout feeds the query builder through stdin
        fp_out = io.StringIO()
        fp_err = io.StringIO()
        with contextlib.redirect_stdout(fp_out):
            with contextlib.redirect_stderr(fp_err):
                run_input_gen.run_main(FIXTURE_ARGS['site_name'])
        test_output_file = 'tmpdir/unittest.site_name.stdin.output.query'
        fp_in = io.StringIO(fp_out.getvalue())
        #No contextlib.redirect_stdin; patch sys.stdin directly
        orig_stdin = sys.stdin
        sys.stdin = fp_in
        try:
            run_query_builder.run_main(['-i', '-', '-o', test_output_file])
        finally:
            sys.stdin = orig_stdin
        self.assertTrue(self.compare_query_files('tmpdir/unittest.site_name.query', test_output_file), "Query file built from stdin JSON does not match reference.")

    def testQueryFromFileOutput(self):
        #A generated JSON round-trips through the query builder when
        #captured from stdout and written to a file
        request_dict = self.run_generator(FIXTURE_ARGS['site_name'])
        json_path = 'tmpdir/rt.json'
        with open(json_path, 'w') as fp_out:
            json.dump(request_dict, fp_out, indent=4)
        test_output_file = 'tmpdir/unittest.site_name.gen.output.query'
        run_query_builder.run_main(['-i', json_path, '-o', test_output_file])
        self.assertTrue(self.compare_query_files('tmpdir/unittest.site_name.query', test_output_file), "Query file built from generated JSON does not match reference.")

    def testEventList(self):
        events_path = os.path.join('tmpdir', 'events.csv')
        with open(events_path, 'w') as fp_out:
            fp_out.write("12,3,4\n13,4,5\n\n")
        request_dict = self.run_generator(['-m', 'Study 22.12 LF', '-p', 'Event Info', '-e', events_path])
        self.assertEqual(request_dict['event_list'], [[12, 3, 4], [13, 4, 5]])

    def testNumberFormatting(self):
        #Numeric filter values are emitted as JSON floats; enum values are
        #cast to the filter's type before the membership check
        argv = ['-m', 'Study 22.12 BB', '-p', 'Intensity Measures',
                '--filter', 'INTENSITY_MEASURE_PERIOD=1 0.075 0.1e0',
                '--filter', 'INTENSITY_MEASURE_PERIOD_PARAMS=2',
                '--filter', 'INTENSITY_MEASURE_VALUE=100',
                '--filter', 'SITE_NAME=USC']
        request_dict = self.run_generator(argv)
        for f in request_dict['filters']:
            if f['name']=='Intensity Measure Period':
                self.assertEqual(f['values'], [1.0, 0.075, 0.1])
            elif f['name']=='Site Name':
                self.assertEqual(f['values'], ['USC'])

    def testPgvCaseInsensitive(self):
        argv = ['-m', 'Study 22.12 LF', '-p', 'Intensity Measures',
                '--filter', 'INTENSITY_MEASURE_PERIOD=pgv',
                '--filter', 'SITE_NAME=USC']
        request_dict = self.run_generator(argv)
        for f in request_dict['filters']:
            if f['name']=='Intensity Measure Period':
                self.assertEqual(f['values'], ['PGV'])

    def testDuplicateFilterLastWins(self):
        #A repeated --filter for the same name keeps the last value
        argv = ['-m', 'Study 22.12 LF', '-p', 'Site Info',
                '--filter', 'SITE_NAME=USC', '--filter', 'SITE_NAME=USGS']
        request_dict = self.run_generator(argv)
        for f in request_dict['filters']:
            if f['name']=='Site Name':
                self.assertEqual(f['values'], ['USGS'])

    def testFilterWithPrefix(self):
        #A FILTER_ prefix carried over from the old variable grammar is
        #tolerated and produces the same request as the bare name
        argv = ['-m', 'Study 22.12 LF', '-p', 'Site Info', '--filter', 'FILTER_SITE_NAME=USC']
        request_dict = self.run_generator(argv)
        fixture = self.load_json('tmpdir/unittest.site_name.json')
        self.assertEqual(self.sorted_filters(request_dict), self.sorted_filters(fixture))

    def assertExitCode(self, argv, expected_code):
        with contextlib.redirect_stdout(io.StringIO()):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as cm:
                    run_input_gen.run_main(argv)
        self.assertEqual(cm.exception.code, expected_code, "Exit code %s != expected %s (argv: %s)" % (str(cm.exception.code), str(expected_code), str(argv)))

    def testUnknownModel(self):
        self.assertExitCode(['-m', 'Study 99.9 XF', '-p', 'Site Info'], 3)

    def testMissingModel(self):
        self.assertExitCode(['-p', 'Site Info'], 6)

    def testProductNotAvailableForModel(self):
        #Seismograms is not available for the 24.8 models
        self.assertExitCode(['-m', 'Study 24.8 BB', '-p', 'Seismograms'], 1)

    def testValueOutOfRange(self):
        self.assertExitCode(['-m', 'Study 22.12 LF', '-p', 'Intensity Measures',
                             '--filter', 'MAGNITUDE=9.0'], 4)

    def testRangeOnStringFilter(self):
        self.assertExitCode(['-m', 'Study 22.12 LF', '-p', 'Site Info',
                             '--filter', 'SITE_NAME=USC', '--filter', 'SITE_NAME_PARAMS=3'], 5)

    def testPgvMixed(self):
        self.assertExitCode(['-m', 'Study 22.12 LF', '-p', 'Intensity Measures',
                             '--filter', 'INTENSITY_MEASURE_PERIOD=2.0 pgv',
                             '--filter', 'INTENSITY_MEASURE_PERIOD_PARAMS=2'], 5)

    def testUnknownFilterVariable(self):
        self.assertExitCode(['-m', 'Study 22.12 LF', '-p', 'Site Info',
                             '--filter', 'FOO=1'], 5)

    def testMalformedFilterArg(self):
        self.assertExitCode(['-m', 'Study 22.12 LF', '-p', 'Site Info',
                             '--filter', 'SITE_NAME'], 5)

    def testMissingParams(self):
        #Two values without _PARAMS
        self.assertExitCode(['-m', 'Study 22.12 LF', '-p', 'Event Info',
                             '--filter', 'MAGNITUDE=7.0 8.0'], 6)

    def testMissingRequiredFilter(self):
        #Intensity Measure Value requires Intensity Measure Period
        self.assertExitCode(['-m', 'Study 22.12 LF', '-p', 'Intensity Measures',
                             '--filter', 'INTENSITY_MEASURE_VALUE=5.0'], 6)

    def testBadEventLine(self):
        events_path = os.path.join('tmpdir', 'evbad.csv')
        with open(events_path, 'w') as fp_out:
            fp_out.write("1,2\n")
        self.assertExitCode(['-m', 'Study 22.12 LF', '-p', 'Event Info',
                             '-e', events_path], 7)

    def testTooManyEvents(self):
        events_path = os.path.join('tmpdir', 'evmany.csv')
        with open(events_path, 'w') as fp_out:
            for i in range(0, 120001):
                fp_out.write("1,2,3\n")
        self.assertExitCode(['-m', 'Study 22.12 LF', '-p', 'Event Info',
                             '-e', events_path], 7)

    def testUnreadableEventFile(self):
        self.assertExitCode(['-m', 'Study 22.12 LF', '-p', 'Event Info',
                             '-e', 'tmpdir/no_such_file.csv'], 8)

    def testSortByAscending(self):
        #One filter may be chosen to sort the results on
        argv = ['-m', 'Study 22.12 LF', '-p', 'Intensity Measures',
                '--filter', 'MAGNITUDE=7.0', '--filter', 'SITE_NAME=USC',
                '--sort-by', 'MAGNITUDE', '--sort-order', 'asc']
        request_dict = self.run_generator(argv)
        for f in request_dict['filters']:
            if f['name']=='Magnitude':
                self.assertEqual(f.get('sort'), 1)
            else:
                self.assertNotIn('sort', f)

    def testSortByDescending(self):
        argv = ['-m', 'Study 22.12 LF', '-p', 'Intensity Measures',
                '--filter', 'MAGNITUDE=7.0', '--filter', 'SITE_NAME=USC',
                '--sort-by', 'MAGNITUDE', '--sort-order', 'desc']
        request_dict = self.run_generator(argv)
        for f in request_dict['filters']:
            if f['name']=='Magnitude':
                self.assertEqual(f.get('sort'), -1)
            else:
                self.assertNotIn('sort', f)

    def testSortOrderDefaultsToAscending(self):
        #--sort-by without --sort-order defaults to ascending
        argv = ['-m', 'Study 22.12 LF', '-p', 'Intensity Measures',
                '--filter', 'MAGNITUDE=7.0', '--filter', 'SITE_NAME=USC',
                '--sort-by', 'MAGNITUDE']
        request_dict = self.run_generator(argv)
        for f in request_dict['filters']:
            if f['name']=='Magnitude':
                self.assertEqual(f.get('sort'), 1)

    def testSortByUnselectedFilter(self):
        #Magnitude has no value, so the results cannot be sorted on it
        self.assertExitCode(['-m', 'Study 22.12 LF', '-p', 'Site Info',
                             '--filter', 'SITE_NAME=USC',
                             '--sort-by', 'MAGNITUDE', '--sort-order', 'asc'], 5)

    def testSortByUnknownFilter(self):
        self.assertExitCode(['-m', 'Study 22.12 LF', '-p', 'Site Info',
                             '--filter', 'SITE_NAME=USC',
                             '--sort-by', 'FOO', '--sort-order', 'asc'], 5)

    def testSortOrderIgnoredWithoutSortBy(self):
        #An orphan --sort-order (e.g. a visible direction radio paired with
        #a hidden empty --sort-by) warns and generates without sorting
        argv = ['-m', 'Study 22.12 LF', '-p', 'Site Info',
                '--filter', 'SITE_NAME=USC',
                '--sort-order', 'asc']
        request_dict = self.run_generator(argv)
        for f in request_dict['filters']:
            self.assertNotIn('sort', f)

    def testBlankParameterForms(self):
        #Hidden form elements emit blank values in various shapes; all are
        #stripped and ignored, in any position relative to the real values
        fixture = self.load_json('tmpdir/unittest.site_name.json')
        argv_templates = [
            ['-m', '', '-p', '', '-p', 'Site Info', '-m', 'Study 22.12 LF',
             '--filter', 'SITE_NAME=USC', '--filter', 'SOURCE_NAME=',
             '--filter', 'SOURCE_NAME=""', '--filter', 'SOURCE_NAME= ',
             '--filter', 'MAGNITUDE_PARAMS=""',
             '--sort-by', '', '--sort-order', ''],
            ['-m', 'Study 22.12 LF', '-p', 'Site Info', '-p', '',
             '--filter', 'SOURCE_NAME=""', '--filter', 'SITE_NAME=USC',
             '--sort-order', '', '--sort-by', ''],
        ]
        for argv in argv_templates:
            request_dict = self.run_generator(argv)
            self.assertEqual(self.sorted_filters(request_dict), self.sorted_filters(fixture))
            self.assertEqual(request_dict['model'], fixture['model'])
            self.assertEqual(request_dict['products'], fixture['products'])

    def testEmptyProductAloneIsMissing(self):
        #Stripping a blank product with no real value still reports it missing
        self.assertExitCode(['-m', 'Study 22.12 LF', '-p', ''], 6)

    def testEmptyEventFilenameIgnored(self):
        argv = ['-m', 'Study 22.12 LF', '-p', 'Event Info', '-e', '']
        request_dict = self.run_generator(argv)
        self.assertNotIn('event_list', request_dict)

    def testConflictingProductLastWins(self):
        argv = ['-m', 'Study 22.12 LF', '-p', 'Site Info', '-p', 'Event Info']
        request_dict = self.run_generator(argv)
        self.assertEqual(request_dict['products']['name'], 'Event Info')

    def testBadSortOrder(self):
        self.assertExitCode(['-m', 'Study 22.12 LF', '-p', 'Intensity Measures',
                             '--filter', 'MAGNITUDE=7.0', '--filter', 'SITE_NAME=USC',
                             '--sort-by', 'MAGNITUDE', '--sort-order', 'up'], 4)

    def testFilterSortKeyRejected(self):
        #The old per-filter _SORT keys are no longer accepted
        self.assertExitCode(['-m', 'Study 22.12 LF', '-p', 'Site Info',
                             '--filter', 'SITE_NAME=USC',
                             '--filter', 'SITE_NAME_SORT=asc'], 5)

    def testBareSortByFlags(self):
        #A web form emits hidden empty elements as bare flags with no value
        #token (e.g. "--sort-by --sort-by SITE_NAME"); the flag immediately
        #before a real value consumes it, the bare ones record empty strings
        argv = ['-m', 'Study 22.12 LF', '-p', 'Site Info',
                '--filter', 'SITE_NAME=USC',
                '--sort-by', '--sort-by', '--sort-by', 'SITE_NAME',
                '--sort-by', '--sort-order', 'ASC']
        request_dict = self.run_generator(argv)
        for f in request_dict['filters']:
            if f['name']=='Site Name':
                self.assertEqual(f.get('sort'), 1)

    def testBareModelProductEventFlags(self):
        #Bare -m/-p/-e flags at the start of a run are empty values, not errors
        request_dict = self.run_generator(['-m', '-p', 'Site Info', '-m',
                                           'Study 22.12 LF', '-e',
                                           '--filter', 'SITE_NAME=USC'])
        self.assertEqual(request_dict['model'], {'name': 'Study 22.12 LF'})
        self.assertEqual(request_dict['products'], {'name': 'Site Info'})
        self.assertNotIn('event_list', request_dict)

    def testTrailingBareFlags(self):
        #Bare flags at the very end of the argument list are tolerated
        self.run_generator(['-m', 'Study 22.12 LF', '-p', 'Site Info',
                            '--filter', 'SITE_NAME=USC',
                            '--sort-by', 'SITE_NAME', '--sort-by', '-e'])

    def testBareFilterFlag(self):
        #A bare --filter is skipped; the next real one still applies
        request_dict = self.run_generator(['-m', 'Study 22.12 LF', '-p',
                                           'Site Info', '--filter', '--filter',
                                           'SITE_NAME=USC'])
        self.assertEqual(self.sorted_filters(request_dict),
                         self.sorted_filters(self.load_json('tmpdir/unittest.site_name.json')))

if __name__=='__main__':
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestInputGen)
    rc = unittest.TextTestRunner(verbosity=2).run(test_suite)
    sys.exit(not rc.wasSuccessful())