# PyeDNA
[![PyPI version](https://badge.fury.io/py/pyedna.svg)](https://badge.fury.io/py/pyedna)
[![Documentation Status](https://readthedocs.org/projects/pyedna/badge/?version=latest)](http://pyedna.readthedocs.io/en/latest/?badge=latest)

PyeDNA ("pie-dee-en-ay") is a Python wrapper library for the C++ EzDnaApi,
written for data scientists who wish to work with eDNA data in the context of a
pandas DataFrame. By converting eDNA data into a DataFrame, data analysis can 
be accomplished using familiar tools like scikit-learn, statsmodels, etc. New
functions will be added upon request.

## Disclaimer
PyeDNA is a wrapper library for the API of a data historian called eDNA. eDNA 
is developed by InStepSoftware, LLC (http://www.instepsoftware.com/), 
who holds all rights to the eDNA software. PyeDNA does not contain any 
proprietary code, and is merely a wrapper for functions that must be obtained 
from a legal, licensed version of EzDnaApi.dll.

## Dependencies
PyeDNA currently requires that a legal, licensed version of the EzDnaApi be 
located in the following directory:

C:\Program Files (x86)\eDNA\EzDnaApi64.dll

Currently, only the 64-bit version of eDNA is supported. Python 2 is not supported.

**Required libraries**: numba, numpy, pandas

## Documentation
Current documentation can be found [here](https://pyedna.readthedocs.io/en/latest/).

## Examples
All of the core data pulling functions are located in the GetHist function, 
which will return a pandas DataFrame with the timestamp, value, and status 
columns. For example, the following code will pull snap data from TESTPNT1 
over a 30-second interval:

> import pyedna.ezdna as dna

> tag = "TESTSITE.TESTSERVICE.TESTPNT1"       # format site.service.tag

> start = "12/01/16 01:01:01"                 # format mm/dd/yy hh:mm:ss

> end = "01/03/17 01:01:01"                   # format mm/dd/yy hh:mm:ss

> period = "00:00:30"                         # format hh:mm:ss

> df = dna.GetHist(tag, start, end, period=period, mode="snap")

Raw data may be obtained from TESTPNT1 using:

> df = dna.GetHist(tag, start, end, mode="raw")

Other supported pull types include Average, Interpolated, Max, and Min. Please
refer to eDNA documentation for more description about these pull types.

Multiple tags can be pulled (in Raw mode) at the same time using:

> tags = ["TESTSITE.TESTSERVICE.TESTPNT1", "TESTSITE.TESTSERVICE.TESTPNT2",
          "TESTSITE.TESTSERVICE.TESTPNT3", "TESTSITE.TESTSERVICE.TESTPNT4"]
          
> df = dna.GetMultipleTags(tags, start, end)

A list of connected services may be obtained using GetServices:

> services = dna.GetServices()

A list of point information for a given service can be found using GetPoints:

> points = dna.GetPoints("TESTSITE.TESTSERVICE")
