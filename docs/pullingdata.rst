==================
 4. Pulling Data
==================
Data from each defined eDNA tag can be obtained by the functions in this section. 

**Warning**- One of the most common mistakes when using PyeDNA is not to specify the
full eDNA tag when using the module. Unless otherwise specified, tags should always
be specified by their full Site.Service.Tag designation.

**Danger**- Please read the data compression section to understand what is actually
happening when data is pulled in "raw" mode- it **will** affect your data analysis.

All code in this section assumes that PyeDNA has been imported using:

**import pyedna.ezdna as dna**

Types of Data Pulls
--------------------
As defined by eDNA, several different types of data pulls may be accomplished:

* Avg: Finds the arithmetic mean of values over a window defined by the time span.
* Interp: Interpolates values over a window defined by the time span.
* Min: Finds the minimum value over a window defined by the time span.
* Max: Finds the maximum value over a window defined by the time span.
* Raw: Pulls data exactly as it is stored in the database (read data compression below)
* Snap: Finds the last data point over a window defined by the time span.

PyeDNA provides functionality for all of these methods.

eDNA Data Compression
----------------------
The eDNA database only stores data points when either the value or status of the point
changes. This allows the data files to be compressed, which is advantageous for transfer
over a low-speed or expensive medium. However, this compression presents some issues for
data analysis that the user must be aware of.

First, data gaps may occur over the time period if data transfer is interrupted in some 
way. These data gaps may be hard to notice in practice, especially if the user is pulling
data with the "Snap" method. Since "Snap" will find the last data point at each time window,
the "last" data point will be the data point right before the data gap. This causes a 
"flat-lining" behavior that is usually obvious if the data gap is large enough. It is 
strongly recommended that the user implement some kind of gap-detection algorithm if gaps
are frequent and "Snap" mode is being used.

Second, data pulled using "Raw" mode is not appropriate for many types of statistical
analysis. Since "Raw" mode pulls *compressed* data as it is actually stored in the database,
the frequency of common data points is reduced compared to uncommon data points. Hence,
statistical analysis will be skewed *towards* outliers. It is recommended that the user
typically use "Snap" mode to prevent this situation, especially if the data sampling rate
is known *a priori*. However, take care about data gaps when using "Snap" mode, as 
mentioned above.

Please refer to eDNA documentation for more information.

GetHist 
--------
The main data pulling functionality is contained in the dna.GetHist function. GetHist will return
a pandas DataFrame with the requested data, providing easy access to more advanced data 
analysis tools in Python. 

The start date and end date of the data pull must be specified as input parameters. **Warning**-
eDNA prefers the date in this format: 

**mm/dd/yy hh:mm:ss**

While other formats may work, please specify your dates in this format, for safety.

By default, the column label of the DataFrame will be the eDNA tag name, but by specifying 
the parameter **desc_as_label=True**, the eDNA description can be used instead. Otherwise, 
a custom label can be specified by **label="CUSTOM_LABEL"**.

Each of the six data pulling methods mentioned above are supported in this function 
by supplying the parameter **mode="X"**. The default data pulling mode is **raw**:

* avg
* interp
* min
* max
* raw
* snap

By default, the data returned in the pandas DataFrame will use a numpy DateTime as the index.
However, if the native eDNA UTC time is requested using **utc=True**, the index will be an
integer instead. The speed of the data pull will actually be slightly improved if 
**utc=True** is selected.

High-speed data can be obtained using the parameter **high_speed=True**. Take care that high
speed data is required, because it can significantly slow down the data pull.

Legacy data pulling functions are still available, but have been consolidated into GetHist:

* dna.GetHistAvg
* dna.GetHistInterp
* dna.GetHistMax
* dna.GetHistMin
* dna.GetHistRaw
* dna.GetHistSnap

GetMultipleTags
----------------
dna.GetMultipleTags is a convenience function designed to prepare data from multiple tags 
simultaneously. It may save the user a large amount of time, but it's important to understand
what's happening behind the scenes to determine if this function will meet your needs.

The core behavior of GetMultipleTags is to:

1. Pull data from multiple eDNA tags (supplied via a list) using **GetHist(mode="raw")**
2. Remove any duplicated indices (this happens sometimes in eDNA and will cause the concatenation to fail)
3. Concatenate all the DataFrames using an **outer join** (time indices which are not shared will be filled with None)
4. Fill the None values using a "fill-forward" algorithm

If data is to be used for statistical analysis, it is strongly recommended that the user 
adjust the parameter **sampling_rate="X"**, since data is being pulled using "Raw" mode
in this function. The format of the **sampling_rate** parameter uses pandas resampling
notation. For instance, "1S" means 1 second, and "5M" means 5 minutes. Refers to pandas
documentation for more information.

The parameter **fill_limit** can be used to specify how many data points are filled-forward
in step 4 above. If fill_limit is set to 0, the data will not be filled-forward at all.

**verify_time=True** can be used to ensure that no duplicate time indices exist after the
concatenation, which will sometimes occur when more than 10 tags are being concatenated.
Unfortunately, this will significantly slow down the data pull.

As with GetHist above, the parameters **desc_as_label** and **utc** may also be specified.