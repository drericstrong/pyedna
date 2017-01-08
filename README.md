# PyeDNA
### Written by Eric Strong

PyeDNA ("pie-dee-en-ay") is a Python wrapper library for the C++ EzDnaApi. eDNA 
is a data historian developed by InStepSoftware, LLC (http://www.instepsoftware.com/), 
who holds all rights to the eDNA software. PyeDNA does not contain any proprietary code,
and is merely a wrapper for functions that must be obtained from a legal, licensed 
version of EzDnaApi.dll.

PyeDNA currently requires that a legal, licensed version of the EzDnaApi be 
located in the following directory:

C:\Program Files (x86)\eDNA\EzDnaApi64.dll

New functions will be added upon request.

## Dependencies
numpy, pandas, ctypes

## Example
PyeDNA is very simple to use. All of the data pulling functions (e.g. GetHistRaw)
will return a pandas DataFrame with the timestamp, value, and status.

The following code will pull snap data from ADE1CA01 over a 30-second interval:

>>> import pyedna.ezdna as dna

>>> tag = "MDSSCSC1.ANVCALC.ADE1CA01"           # format site.service.tag

>>> start = "12/01/16 01:01:01"                 # format mm/dd/yy hh:mm:ss

>>> end = "01/03/17 01:01:01"                   # format mm/dd/yy hh:mm:ss

>>> period = "00:00:30"                         # format hh:mm:ss

>>> df = dna.GetHistSnap(tag, start, end, period)

Raw data may be obtained from ADE1CA01 using:

>>> df = dna.GetHistRaw(tag, start, end)

Multiple tags can be pulled at the same time using:

>>> df = dna.GetMultipleTags(['MDSSCSC1.ANVCALC.ADE1CA02', \

>>>                           'MDSSCSC1.ANVCALC.ADE1CA03', \

>>>                           'MDSSCSC1.ANVCALC.ADE1CA04'], \

>>>                           '12/26/16 01:01:01', \

>>>                           '01/04/17 01:01:01', \ 

>>>                           sampling_rate=10, \

>>>                           fill_limit=600)


Be careful, the data will be merged and filled only up until the selected
fill_limit. After that point, the data will be empty, because it will be 
assumed that the data connection has dropped.
