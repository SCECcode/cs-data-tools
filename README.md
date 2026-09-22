# CyberShake Data Access Tool

## Description 
The CyberShake Data Access tool is an interactive pure Python tool which retrieves [CyberShake](https://www.scec.org/software/cybershake) data products.

Data products and metadata are retrieved through database queries.  Seismograms are downloaded from Globus shared collections hosted at USC CARC.

## Concepts

The CyberShake Data Access tool works by asking the user to interactively specify a hazard model, a data product, and 0 or more filters, which are used to retrieve only a subset of the data.  Filters are inclusive, so only data which meets the requirements of the filters will be included. 

Current CyberShake models supported are:
* [Study 22.12](https://strike.scec.org/scecpedia/CyberShake_Study_22.12), low-frequency
* [Study 22.12](https://strike.scec.org/scecpedia/CyberShake_Study_22.12), broadband
* [Study 24.8](https://strike.scec.org/scecpedia/CyberShake_Study_24.8), low-frequency
* [Study 24.8](https://strike.scec.org/scecpedia/CyberShake_Study_24.8), broadband

Current data products supported are:
* Site information
* Event information
* Intensity measures
* Seismograms (for Study 22.12)

Current filters supported are:
* Intensity measure period
* Intensity measure value
* Magnitude
* Site name
* Site-rupture distance
* Source name

## Requirements
The CyberShake Data Access tool requires an internet connection, Python 3.8 or newer, and the [pymysql library](https://pypi.org/project/pymysql/).

## Installation

To install the tool, please clone the git repository:

`git clone https://github.com/SCECcode/cs-data-tools.git`

If the prerequisites are installed, you should then be able to run it.

## Tutorial

A tutorial with examples is available [here](https://docs.google.com/document/d/1J1ou1rqpbdSexcheT22jt_XzXq6uFMumDImMGADbi1g).  Note that the tutorial mentions Docker containers, but the tutorial is for any installation of the tool.

## Usage

### Getting Started 

To begin, run 

`$> cs-data-tools/src/retrieve_cs_data.py`

This will prompt you for the model, data products, and filters you desire.  To view all the command-line options, run with the help flag:

`$> cs-data-tools/src/retrieve_cs_data.py -h`

### Basic Usage

Follow the prompts to indicate your selected hazard model, data product, and filter(s).  For each filter you choose, you'll be prompted to input either 1 value, multiple values as a comma-separated list, or a range of values by inputing the start and end (both inclusive).  After you select all your filters, you have the option to sort your results.  Then the tool will perform the necessary database queries to get your data, along with some metadata describing it.

If you selected 'Seismograms' as your output format, the tool will also download your requested seismograms.  Before beginning the download, the tool will calculate how much temporary space and output space your request needs, and will print an error message and not download the data if it exceeds the limits in data_collector/run_data_collector.py, which are 1 GB by default.  This is because CyberShake data can get very large, and it's easy to accidentally request terabytes of data.

If you make a mistake, you can use Ctrl-C to exit the application and start again.

#### Labels

To keep track of which data files go with which request, you can assign a label using the '-l' flag, like:

`$> cs-data-tools/src/retrieve_cs_data.py -l my_data_label`

#### Output and temporary directories

You can specify an output directory with the '-o' flag.  All output files -- metadata files, database output, and seismograms -- will be stored in this directory.

You can also specify a temporary directory with the '-t' flag.  Since seismograms are stored in bulk, the tool downloads a file which contains multiple individual seismograms, and then extracts a subset for your request.  The bulk files are downloaded to the temporary directory, and then deleted after the extraction.

### Advanced Features

#### Event list file

If you already know which events you want, you can provide a CSV-format file with a list of these events using the '-e <event list filename>' command-line argument.

The format for the file is one event per line, in the format
`<source id>,<rupture id>,<rupture variation id>`

Providing this file will bypass all the event filters (they will not appear in the filter list), but you will still be able to filter on IM values and sites.

Note that there is a limit of 120,000 events in an event list file, due to the maximum length of a MySQL query.

#### Database backend

By default, the tool uses the CyberShake database hosted at moment.usc.edu.  Configuration parameters to connect to this database are specified in db_wrapper/moment.cfg.  If you prefer, you can point the tool to an alternative CyberShake database by creating a new cfg file and using the '-c <config file>' command-line argument, like:

`$> cs-data-tools/src/retrieve_cs_data.py -c new_db.cfg`

The tool supports MySQL and SQLite format databases.  A sample SQLite configuration file is included in db_wrapper/sqlite.cfg.

#### Alternative output formats

By default, the tool produces database output in CSV format.  However, if you prefer, you can get output in SQLite format by using the flag '-of sqlite'.

#### Automated requests

If you want to bypass the interactive part of the request, you can use the '-i' flag to pass in a JSON file which contains a description of a data request instead.  You can examine the JSON files the tool produces for examples of the format.

#### Non-interactive data requests

The input generator, input_gen/run_input_gen.py, builds a data-request JSON without the interactive prompts, so an application can make requests programmatically.  It reads the request variables from command-line arguments, validates them against the same models, data products, and filters the interactive tool uses, and writes the JSON to stdout in exactly the format the Filter Generator would have written.  The human-readable summary is written to stderr, so stdout carries only the JSON.  It only *produces* the JSON; running the data-access pipeline is the next step.  Pipe the output directly into the data-access tool:

`$> cs-data-tools/src/input_gen/run_input_gen.py -m "Study 22.12 LF" -p "Site Info" --filter SITE_NAME=USC | cs-data-tools/src/retrieve_cs_data.py -i - -o ./out -t ./tmp`

Or into the query-construction stage alone:

`$> cs-data-tools/src/input_gen/run_input_gen.py -m "Study 22.12 LF" -p "Site Info" --filter SITE_NAME=USC | cs-data-tools/src/query_build/run_query_builder.py -i - -o my.request.query`

Or redirect it to a file with '>':

`$> cs-data-tools/src/input_gen/run_input_gen.py -m "Study 22.12 LF" -p "Site Info" --filter SITE_NAME=USC > myrequest.json`

| Flag | Meaning |
|---|---|
| `-m, --model` | Required.  `Study 22.12 LF`, `Study 22.12 BB`, `Study 24.8 LF`, or `Study 24.8 BB` (case-insensitive; the "study" prefix is optional) |
| `-p, --product` | Required.  `Site Info`, `Seismograms`, `Intensity Measures`, or `Event Info` (case-insensitive).  Seismograms are not available for the 24.8 models. |
| `--filter NAME=VALUE` | Optional, repeatable.  Filter values.  `NAME` is a filter name in upper case with spaces replaced by underscores (e.g. `SITE_NAME`, `INTENSITY_MEASURE_PERIOD_PARAMS`).  Numeric filters accept comma- and/or space-separated values; string filters (Site Name, Source Name) split on commas only, so spaces stay part of the value (quote the argument for the shell: `--filter "SOURCE_NAME=San Andreas"`).  A value with spaces must be a single quoted argument.  A blank value (empty, quoted-empty, or whitespace-only) is stripped and ignored. |
| `--filter NAME_PARAMS=VALUE` | `1` single value, `2` multiple values, `3` range.  Optional when exactly one value is given (inferred 1); required otherwise |
| `--sort-by NAME` | Optional.  Sort the results on one of the selected filters, e.g. `--sort-by MAGNITUDE` (same `NAME` form as `--filter`).  Only one filter can be sorted on, mirroring the interactive tool. |
| `--sort-order ASC\|DESC` | Optional.  The direction for `--sort-by`; defaults to ascending.  `asc`/`ascending`/`1` and `desc`/`descending`/`-1` are accepted. |
| `-e <event list filename>` | Optional CSV of `<src id>,<rup id>,<rup var id>` lines; bypasses the event filters.  Max 120000 events. |
| `-v` | Print the version. |

The filter names and valid values are those defined by the interactive tool, so they are always in sync with it:

| Filter | Type | Value forms | Valid values | Applies to |
|---|---|---|---|---|
| `Site Name` | string | 1, 2 | 3-5 character site short name | Site Info, Seismograms, Intensity Measures, Event Info |
| `Intensity Measure Period` | float or `PGV`/`PGA` | 1, 2 | one of the model's periods (below); `PGV`/`PGA` only as a single value | Seismograms, Intensity Measures |
| `Intensity Measure Value` | float (cm/sec2) | 1, 2, 3 | [0.0, 10000.0]; requires `Intensity Measure Period` | Seismograms, Intensity Measures |
| `Magnitude` | float | 1, 2, 3 | [5.0, 8.5] | Seismograms, Intensity Measures, Event Info |
| `Site-Rupture Distance` | float (km) | 1, 2, 3 | [0.0, 200.0]; requires `Site Name` | Seismograms, Intensity Measures, Event Info |
| `Source Name` | string | 1, 2 | substring match | Seismograms, Intensity Measures, Event Info |

`Intensity Measure Period` values per model (the model's RotD50 periods):

| Model | Periods |
|---|---|
| Study 22.12 LF / Study 24.8 LF | 2.0, 3.0, 4.0, 5.0, 7.5, 10.0, PGV |
| Study 22.12 BB / Study 24.8 BB | 0.01, 0.02, 0.03, 0.04, 0.05, 0.075, 0.1, 0.2, 0.3, 0.4, 0.5, 0.75, 1, 2, 3, 4, 5, 7.5, 10, PGV, PGA |

The generator fails fast: the first invalid input aborts with a message on stderr and an exit code from src/utils/utilities.py:

| Exit | Meaning |
|---|---|
| 0 | request generated successfully |
| 1 | data product not available for the model |
| 3 | unknown model |
| 4 | value outside a filter's range or enum, or invalid sort order |
| 5 | malformed `--filter` argument, unknown filter name, malformed value/illegal characters, bad `_PARAMS` value or value form, filter not applicable to the product, `--sort-by` naming an unknown or unselected filter, `--filter NAME_SORT` (no longer supported) |
| 6 | missing `-m/--model` or `-p/--product`, missing `_PARAMS` with 2+ values, unmet required filter |
| 7 | unparseable event-list CSV; over 120000 events |
| 8 | event-list file unreadable |

Notes:

- Blank parameter values are stripped and ignored: empty, quoted-empty, or whitespace-only values (e.g. `--filter SITE_NAME=`, `--filter "SOURCE_NAME="""`, `--sort-by ""`, `-m ""`, or a repeated `-m`/`-p` where one occurrence is empty) produce no warning and no effect, so front-end forms emitting hidden empty-valued elements work as-is.  An orphan `--sort-order` with no `--sort-by` is likewise ignored with a warning.
- Numeric filter values are emitted as JSON floats (e.g. `2` becomes `2.0`), matching what the interactive tool writes.
- String filter values may not contain `"`, `\`, `,`, `|`, `&`, `$`, backtick, `(`, `)`, `<`, `>`, `;`, or control characters.
- Numeric literals are strict: optional `-`, digits, optional decimals and exponent.  `nan`, `inf`, and `0x10` are rejected.

#### Individual components

Under the hood, the CyberShake data access tool consists of 5 components:
* Input Generator - reads request variables from command-line arguments and produces a JSON file describing the request, without interactive prompts.  input_gen/run_input_gen.py .
* Filter Generator - prompts the user for the hazard model, data product, and filters, and produces a JSON file describing the request.  filt_gen/run_filter_generator.py .
* Query Constructor - takes in the JSON file and produces a query file, describing the database queries which must be run to get the needed data and metadata.  query_build/run_query_builder.py .
* Database Wrapper - runs the queries and writes the results to a data output file.  db_wrapper/run_database_wrapper.py .
* Data Collector - retrieves seismograms, if needed.  data_collector/run_data_collector.py .

Each of these components can be run individually, if needed, by running the corresponding python script.

## File formats

The tool produces both metadata files which describe your request, and data files which contain the results of your request.

### Metadata files

The JSON file contains a human-readable description of your request.  This can be useful if you want to check later to see exactly what your data request was.

The query file contains the query that will be run against the database.

If seismograms are requested, the URL file will contain a list of the seismogram URLs for downloading, and the rupture variations requested from each.

### Data files

Data from the database is delivered in a spreadsheet-type format, where the first row contains the headers, and then each following row contains information for one entry.  The default format is CSV, but SQLite database format is also an option.

Seismograms are stored in CyberShake seismogram format.  Details about the format are available [here](https://strike.scec.org/scecpedia/Accessing_CyberShake_Seismograms#Seismogram_Format), including sample C and Python code to read it.  Basically, the seismograms consist of a header with information about the site, event, dt (timestep size) and nt (number of timesteps) in the seismogram, followed by the X-data, then Y-data, in binary 4-byte floats.

## Support

Users can submit bug reports or request new features through the [Github issue tracker](https://github.com/SCECcode/cs-data-tools/issues).  You can also contact the SCEC Software Development Team at software@scec.org.  If you are reporting a bug, please include your JSON and query files, as well as any error messages.

## Contributing

## Credits

This tool was developed by Scott Callaghan at the Statewide California Earthquake Center (SCEC).  The CyberShake data delivered by this tool was produced by the CyberShake collaboration.

## Acknowledgements

This tool was supported by SCEC Award #22102.

## License

The CyberShake Data Access tool is distributed under the BSD 3-Clause open-source license.  Please see the LICENSE file for more information.
