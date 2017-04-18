==================
 5. Pushing Data
==================
PyeDNA contains the ability to push data *to* an eDNA database. The functions
in this section are primarily contained in the "serv" namepace.

**Warning-** This namespace is still under development, but many of the main
functions should be working correctly.

All code in this section assumes that PyeDNA has been imported using:

**import pyedna.serv as serv**

Serv Capabilities
------------------
PyeDNA exposes the following eZDNAServApi functions:

* AddAnalogShortIdRecord
* AddAnalogShortIdRecordNoStatus
* AddDigitalShortIdRecord
* AddAnalogShortIdMsecRecord
* AddAnalogShortIdMsecRecordNoStatus
* AddDigitalShortIdMsecRecord
* FlushShortIdRecords

More information about these functions can be found in eDNA documentation.