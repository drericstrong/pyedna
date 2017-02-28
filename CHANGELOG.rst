Version 0.14
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- FEATURE- GetServices allows you to get all connected eDNA service information
- FEATURE- GetPoints allows you to get information about all points in a service
- FEATURE- Number of connected services are printed when library is imported
- Better error handling for eDNA connection drops
- Before a data pull, there is now error checking to see if a point exists
- GetMultipleTags no longer automatically resamples and forward-fills data. The user should be in control of this.

Version 0.15
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- FEATURE- In the pulling functions, you can now use the desc_as_label parameter to use the point description as the DataFrame column name.
- FEATURE- In the pulling functions, you can now specify a custom column label.
- Better handling of non-ASCII characters in descriptions and units
- GetRTFull never returned a point description- alternative written
- Improved handling of unicode errors- non-Unicode characters are now ignored
- Consistency between ezdna and serv file formatting and dll calls
- Beginnings of a unit test framework
- Miscellaneous code cleanup

Version 0.16
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- MAJOR- Refactoring of all GetHistX methods into GetHist. Please use the "mode" parameter to specify the type of history call. Old methods still available.
- New DEPENDENCY- Numba
- Significant speed increase due to JIT compilation
- Bugfix in __init__ header
- Project documentation

Version 0.17
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Bugfix in GetHist related to "switch" statement
- Minor documentation fixes
- Mocking the dna_dll variable so that RTD documentation can be automatically created