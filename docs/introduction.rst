====================
 1. Introduction
====================
PyeDNA ("pie-dee-en-ay") is a Python wrapper library for the C++ EzDnaApi,
written for data analysts who wish to work with eDNA data in the context of a
pandas DataFrame. By converting eDNA data into a DataFrame, data analysis can 
be accomplished using familiar tools like scikit-learn, statsmodels, etc. New
functions will be added upon request.

Disclaimer
------------
PyeDNA is a wrapper library for the API of a data historian called eDNA. eDNA 
is developed by InStepSoftware, LLC (http://www.instepsoftware.com/), 
who holds all rights to the eDNA software. PyeDNA does not contain any 
proprietary code, and is merely a wrapper for functions that must be obtained 
from a legal, licensed version of EzDnaApi.dll.

This is fan-supported project and is not affiliated in any way with InStepSoftware, LLC.
The maintainer enjoys working with eDNA and wishes them the best. :)

Package Organization
----------------------
PyeDNA is organized into several namespaces, including:

* calc_config
* ezdna
* serv

The namespace of most interest to the typical user will be the *ezdna* namespace,
which contains methods that are meant to translate the eDNA API to Pythonic syntax 
and common libraries, such as pandas. For instance, all the data pulling and 
configuration information functions are in this namespace.

The other two namespaces, calc_config and serv, contain more specialized functions.
Serv contains functions from the EzDNAServAPI that are meant to push data into eDNA. 
These functions are not entirely converted to familiar syntax, behaving in a more 
low-level fashion. Calc_config is a namespace meant for parsing a CM.DB file (a sqlite
database), which each eDNA service contains. Calculations defined in eDNA may be 
difficult to parse, and this class is meant to determine which tags are located in which
calculations, to determine a dependency structure.

Basic Examples
---------------
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

> tags = ["TESTSITE.TESTSERVICE.TESTPNT1", "TESTSITE.TESTSERVICE.TESTPNT2", "TESTSITE.TESTSERVICE.TESTPNT3", "TESTSITE.TESTSERVICE.TESTPNT4"]
          
> df = dna.GetMultipleTags(tags, start, end)

A list of connected services may be obtained using GetServices:

> services = dna.GetServices()

A list of point information for a given service can be found using GetPoints:

> points = dna.GetPoints("TESTSITE.TESTSERVICE")
