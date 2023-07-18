# CyberShake Data Access Tool

## Description 
The CyberShake Data Access tool is an interactive pure Python tool which retrieves [CyberShake](https://www.scec.org/software/cybershake) data products.

Data products and metadata are retrieved through database queries.  Seismograms are downloaded from Globus shared collections hosted at USC CARC.

## Concepts

The CyberShake Data Access tool works by asking the user to interactively specify a hazard model, a data product, and 0 or more filters, which are used to retrieve only a subset of the data.  Filters are inclusive, so only data which meets the requirements of the filters will be included. 

Current CyberShake models supported are:
* [Study 22.12](https://strike.scec.org/scecpedia/CyberShake_Study_22.12), low-frequency
* [Study 22.12](https://strike.scec.org/scecpedia/CyberShake_Study_22.12), broadband

Current data products supported are:
* Site information
* Event information
* Intensity measures
* Seismograms

Current filters supported are:
* Intensity measure period
* Intensity measure type
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

#### Individual components

Under the hood, the CyberShake data access tool consists of 4 components:
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

This tool was developed by Scott Callaghan at the Southern California Earthquake Center (SCEC).  The CyberShake data delivered by this tool was produced by the CyberShake collaboration.

## Acknowledgements

This tool was supported by SCEC Award #22102.

## License

The CyberShake Data Access tool is distributed under the BSD 3-Clause open-source license.  Please see the LICENSE file for more information.