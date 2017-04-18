===============================
 3. Configuration Information
===============================
PyeDNA contains a number of functions which allow the user to pull configuration
information from current eDNA services and points. These functions are located in
the pyedna.ezdna namespace.

**Warning**- One of the most common mistakes when using PyeDNA is not to specify the
full eDNA tag when using the module. Unless otherwise specified, tags should always
be specified by their full Site.Service.Tag designation.

All code in this section assumes that PyeDNA has been imported using:

**import pyedna.ezdna as dna**

Service Information
--------------------
eDNA contains a number of services, which each contain many tags. When PyeDNA is
imported, it attempts to connect to all available services and will print the 
number of available eDNA services. 

A list of all connection services can be obtained using:

**dna.GetServices()**

The above function will return a pandas DataFrame with the following columns:

* Name
* Description
* Type
* Status

Tag Information
----------------
Each service contains a number of tags, which define a block of time-based data
storage. Connecting to a service allows access to all of its tags, which can be
found using the following command:

**dna.GetPoints("EDNA_SERVICE")**

The above function will return a pandas DataFrame with all the points from the
eDNA service, also including information such as:

* Tag
* Current Value
* Current Time
* Current Status
* Description
* Units

More specific information about a single point can be obtained using:

**dna.GetRTFull("SITE.SERVICE.TAG")**

The tag description alone can be found by:

**dna.GetTagDescription("SITE.SERVICE.TAG")**

Determining if a tag exists in any connected service can be accomplished by:

**dna.DoesIDExist("SITE.SERVICE.TAG")**

The above function will return either TRUE or FALSE. Ensure that proper spelling
and the full Site.Service.Tag format is used.

Tag Picker
-----------
A dialog box containing the native eDNA "tag picker" can be brought up using:

**dna.SelectPoint()**

Unfortunately, only the single point version is supported at this time. Support
for multiple tags is expected to be available in the future.