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

## Usage

### Getting Started 

To begin, run 

`$> cs-data-tools/src/retrieve_cs_data.py`

This will prompt you for the model, data products, and filters you desire.  To view all the command-line options, run with the help flag:

`$> cs-data-tools/src/retrieve_cs_data.py`

### Basic Usage

### Advanced Features

## Tutorial

A tutorial with examples is available [here](https://docs.google.com/document/d/1J1ou1rqpbdSexcheT22jt_XzXq6uFMumDImMGADbi1g).  Note that the tutorial mentions Docker containers, but the tutorial is for any installation of the tool.

## Support

## Citation

## Contributing

## Credits

## License
