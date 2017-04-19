====================
 2. Getting Started
====================

Installation
--------------
If Python is already installed on your computer, PyeDNA can be installed using 
PyPI by opening a command window and typing:

**pip install pyedna**

Upgrading to a new version of pyedna can be accomplished by:

**pip install pyedna --upgrade**

The source code of pyedna is hosted on GitHub at:

https://github.com/drericstrong/pyedna

eDNA Requirements
--------------------
PyeDNA currently requires that a legal, licensed version of the EzDnaApi be 
located in the following directory:

**C:\Program Files (x86)\eDNA\EzDnaApi64.dll**

If your EzDNAApi is in a different location, each namespace contains a method
called LoadDll which can be used to specify the correct location:

**LoadDll("CORRECT_LOCATION")**

Python Requirements
--------------------
**Required libraries**: numba, numpy, pandas

A requirements.txt document is located in the GitHub repository, and all 
package requirements can be installed using the following line in a
command window:

**pip install -r requirements.txt**

Numba is required to significantly speed up the base-level data pull, and
numpy and pandas are used for ease of data processing. It is very unlikely
that these requirements will change in the future.

Python Version Support
------------------------
Currently, PyeDNA only supports Python 3.2+ and is not compatible with
Python 2. Testing confirms that PyeDNA will not work on Python 2 without
some adjustments to the codebase. If this is important to you, please 
make a pull request at:

https://github.com/drericstrong/pyedna

The package maintainer welcomes collaboration.

eDNA Version Support
----------------------
Only the 64-bit version of the eDNA API is supported in the current 
release. I am having trouble getting the 32-bit version to work. It may
be an issue with my particular API file. Again, if 32-bit support is 
important to you, please contact me for collaboration. 

Importing PyeDNA
-----------------
PyeDNA is usually imported into a script using the following line:

**import pyedna.ezdna as dna**

**Warning**- since pyedna is connection-based, importing PyeDNA will 
always have direct side effects. When the module is imported, PyeDNA
will attempt to connect to all available eDNA services. If none are 
available, a warning will be thrown, and the user's eDNA connection 
should be checked. If services are available, the number of available
services will be printed to the console (the maintainer apologizes for
this intrusion, but it was determined to be necessary to provide 
visibility for connection issues unrelated to PyeDNA behavior).