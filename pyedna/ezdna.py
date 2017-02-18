# -*- coding: utf-8 -*-
"""
    pyedna.ezdna
    ~~~~~~~~~~~~~~~
    This module contains "easy" versions of common functions from the eDNA
    C++ dll. Obtain a legal copy of the C++ eDNA dll for use.

    :copyright: (c) 2017 Eric Strong.
    :license: Refer to LICENSE.txt for more information.
"""

# TODO- Test data push
# Note- all functions are in CamelCase to match the original eDNA function
# names, even though this does not follow PEP 8.

import os
import warnings
import pandas as pd
from ctypes import cdll, byref, create_string_buffer
from ctypes import c_char_p, c_double, c_short, c_ushort, c_long, c_ulong

# This code should execute at the beginning of the module import, because
# all of the functions in this module require the dna_dll library to be
# loaded. See "LoadDll" if not in default location
default_location = "C:\\Program Files (x86)\\eDNA\\EzDnaApi64.dll"
if os.path.isfile(default_location):
    dna_dll = cdll.LoadLibrary(default_location)
else:
    dna_dll = None
    raise Exception("ERROR- no eDNA dll detected at " +
                    "C:\\Program Files (x86)\\eDNA\\EzDnaApi64.dll")


# If the EzDnaApi file is not in the default location, the user must explicitly
# load it using the LoadDll function.
def LoadDll(location):
    """
    If the EzDnaApi64.dll file is not in the default location
    (C:\Program Files (x86)\eDNA\EzDnaApi64.dll) then the user must specify
    the correct location of the file, before this module can be used.

    :param location: the full location of EzDnaApi64.dll, including filename
    """
    if os.path.isfile(location):
        global dna_dll
        dna_dll = cdll.LoadLibrary(location)
    else:
        raise Exception("ERROR- file does not exist at " + location)


def _GetNextHist(pulKey, nRet, tag_name, high_speed=False):
    # This is a base function that iterates over a predefined history call,
    # which may be raw, snap, max, min, etc.
    # Define all required variables in the correct ctypes format
    pdValue, nTime, nStatus = c_double(-9999), c_ushort(25), c_ushort(25)
    szTime, szStatus = create_string_buffer(25), create_string_buffer(25)
    time_array, val_array, status_array = [], [], []

    # Once nRet is not zero, the function was terminated, either due to an
    # error or due to the end of the data period.
    while nRet == 0:
        if high_speed:
            nRet = dna_dll.DnaGetNextHSHist(pulKey, byref(pdValue),
                byref(szTime), nTime, byref(szStatus), nStatus)
        else:
            nRet = dna_dll.DnaGetNextHist(pulKey, byref(pdValue),
                byref(szTime), nTime, byref(szStatus), nStatus)
        time_array.append(szTime.value.decode('utf-8'))
        val_array.append(pdValue.value)
        status_array.append(szStatus.value.decode('utf-8'))
    # The history request must be cancelled to free up network resources
    dna_dll.DnaCancelHistRequest(pulKey)

    # To construct the pandas DataFrame, the tag name will be used as the
    # column name, and the index (which is in the strange eDNA format) must be
    # converted to an actual DateTime
    d = {tag_name + ' Status': status_array,
         tag_name: val_array}
    df = pd.DataFrame.from_records(data=d, index=time_array)
    df.index = pd.to_datetime(df.index)
    return df


def DoesIDExist(tag_name):
    """
    Determines if a fully-qualified site.service.tag eDNA tag exists
    in any of the connected services.

    :param tag_name: fully-qualified (site.service.tag) eDNA tag
    :return: true if the point exists, false if the point does not exist

    Example:

    >>> DoesIDExist("Site.Service.Tag")

    """
    # the eDNA API requires that the tag_name be specified in a binary format,
    # and the ctypes library must be used to create a C++ variable type.
    szPoint = c_char_p(tag_name.encode('utf-8'))
    result = bool(dna_dll.DoesIdExist(szPoint))
    return result


def GetServices():
    """
    Obtains all the connected eDNA services.

    :return: A pandas DataFrame of connected eDNA services in the form [Name,
        Description, Type, Status]
    """
    # Define all required variables in the correct ctypes format
    pulKey = c_ulong(0)
    szType = c_char_p("".encode('utf-8'))
    szStartSvcName = c_char_p("".encode('utf-8'))
    szSvcName, szSvcDesc = create_string_buffer(30), create_string_buffer(90)
    szSvcType, szSvcStat = create_string_buffer(30), create_string_buffer(30)
    szSvcName2, szSvcDesc2 = create_string_buffer(30), create_string_buffer(90)
    szSvcType2, szSvcStat2 = create_string_buffer(30), create_string_buffer(30)
    nSvcName, nSvcDesc = c_ushort(30), c_ushort(90)
    nSvcType, nSvcStat = c_ushort(30), c_ushort(30)

    # Call the eDNA function. nRet is zero if the function is successful
    nRet = dna_dll.DnaGetServiceEntry(szType, szStartSvcName, byref(pulKey),
        byref(szSvcName), nSvcName, byref(szSvcDesc), nSvcDesc,
        byref(szSvcType), nSvcType, byref(szSvcStat), nSvcStat)

    # Iterate across all the returned services
    service_results = []
    while nRet == 0:
        nRet = dna_dll.DnaGetNextServiceEntry(pulKey,
            byref(szSvcName2), nSvcName, byref(szSvcDesc2), nSvcDesc,
            byref(szSvcType2), nSvcType, byref(szSvcStat2), nSvcStat)
        # Check that the service returned was not an empty string
        if szSvcName2.value.strip():
            # Remember to decode all of the returned string values
            service_results.append([szSvcName2.value.decode('utf-8').strip(),
                                    szSvcDesc2.value.decode('utf-8').strip(),
                                    szSvcType2.value.decode('utf-8').strip(),
                                    szSvcStat2.value.decode('utf-8').strip()])

    # If no results were returned, raise a warning
    if service_results:
        df = pd.DataFrame(service_results, columns=["Name", "Description",
                                                    "Type", "Status"])
        return df
    else:
        warnings.warn("WARNING- No connected eDNA services detected. Check " +
                      "your DNASys.ini file and your network connection.")
        return pd.DataFrame()


def GetPoints(edna_service):
    """
    Obtains all the points in the edna_service, including real-time values.

    :param edna_service: The full Site.Service name of the eDNA service.
    :return: A pandas DataFrame of points in the form [Tag, Value, Time,
        Description, Units]
    """
    # Ensure that the service exists
    # service_list = GetServices()
    # if not service_list.empty:
    #     if service_list["Name"].isin()

    # Define all required variables in the correct ctypes format
    szServiceName = c_char_p(edna_service.encode('utf-8'))
    nStarting, pulKey, pdValue = c_ushort(0), c_ulong(0), c_double(-9999)
    szPoint, szTime = create_string_buffer(20), create_string_buffer(20)
    szStatus, szDesc = create_string_buffer(20), create_string_buffer(20)
    szUnits = create_string_buffer(20)
    szPoint2, szTime2 = create_string_buffer(20), create_string_buffer(20)
    szStatus2, szDesc2 = create_string_buffer(20), create_string_buffer(20)
    szUnits2, pdValue2 = create_string_buffer(20), c_double(-9999)
    nPoint, nTime, nStatus = c_ushort(20), c_ushort(20), c_ushort(20)
    nDesc, nUnits = c_ushort(20), c_ushort(20)

    # Call the eDNA function. nRet is zero if the function is successful
    nRet = dna_dll.DnaGetPointEntry(szServiceName, nStarting, byref(pulKey),
        byref(szPoint), nPoint, byref(pdValue), byref(szTime), nTime,
        byref(szStatus), nStatus, byref(szDesc), nDesc, byref(szUnits), nUnits)

    # Iterate across all the returned services
    point_results = []
    while nRet == 0:
        nRet = dna_dll.DnaGetNextPointEntry(pulKey,
            byref(szPoint2), nPoint, byref(pdValue2), byref(szTime2), nTime,
            byref(szStatus2), nStatus, byref(szDesc2), nDesc,
            byref(szUnits2), nUnits)
        # Check that the point returned was not an empty string
        if szPoint2.value.strip():
            # Remember to decode all of the returned string values
            point_results.append([szPoint2.value.decode('utf-8').strip(),
                                  pdValue.value,
                                  szTime2.value.decode('utf-8').strip(),
                                  szStatus2.value.decode('utf-8').strip(),
                                  szDesc2.value.decode('utf-8').strip(),
                                  szUnits2.value.decode('utf-8').strip()])

    # If no results were returned, raise a warning
    if point_results:
        df = pd.DataFrame(point_results, columns=["Tag", "Value",
            "Time", "Status", "Description", "Units"])
        return df
    else:
        warnings.warn("WARNING- No points were returned. Check that the " +
                      "service exists and contains points.")
        return pd.DataFrame()


def GetTagDescription(tag_name):
    """
    Gets the current description of a point configured in a real-time eDNA
    service.

    :param tag_name: fully-qualified (site.service.tag) eDNA tag
    :return: tag description
    """
    results = GetRTFull(tag_name)
    # Ensure that results were actually returned
    if results:
        return results[4]
    else:
        return None


def GetRTFull(tag_name):
    """
    Gets current information about a point configured in a real-time
    eDNA service, including current value, time, status, description,
    and units.

    :param tag_name: fully-qualified (site.service.tag) eDNA tag
    :return: tuple of: alue, time, status, statusint, description, units

    Example:

    >>> tag_tuple = GetRTFull("Site.Service.Tag")

    """
    # Check if the point even exists
    if not DoesIDExist(tag_name):
        warnings.warn("WARNING- " + tag_name + " does not exist or " +
                      "connection was dropped. Try again if tag does exist.")
        return None

    # Define all required variables in the correct ctypes format
    szPoint = c_char_p(tag_name.encode('utf-8'))
    pdValue, ptTime = c_double(-9999), c_long(-9999)
    szValue, szTime = create_string_buffer(20), create_string_buffer(20)
    szStatus, szDesc = create_string_buffer(20), create_string_buffer(20)
    szUnits = create_string_buffer(20)
    nValue, nTime, nStatus = c_ushort(20), c_ushort(20), c_ushort(20)
    pusStatus, nDesc, nUnits = c_ushort(0), c_ushort(0), c_ushort(0)

    # Call the eDNA function. nRet is zero if the function is successful
    nRet = dna_dll.DNAGetRTFull(szPoint, byref(pdValue), byref(szValue),
        nValue, byref(ptTime), byref(szTime), nTime, byref(pusStatus),
        byref(szStatus), nStatus, byref(szDesc), nDesc, byref(szUnits), nUnits)

    # Check to make sure the function returned correctly. If not, return None
    if nRet == 0:
        return ([pdValue.value, szTime.value.decode('utf-8'),
                szStatus.value.decode('utf-8'), pusStatus.value,
                szDesc.value.decode('utf-8'), szUnits.value.decode('utf-8')])
    else:
        warnings.warn("WARNING- eDNA API failed with code " + str(nRet))
        return None


def GetHistAvg(tag_name, start_time, end_time, period):
    """
    Retrieves data from eDNA history for a given tag. The data will be
    averaged over the specified "period".

    :param tag_name: fully-qualified (site.service.tag) eDNA tag
    :param start_time: must be in format mm/dd/yy hh:mm:ss
    :param end_time: must be in format mm/dd/yy hh:mm:ss
    :param period: must be in format hh:mm:ss
    :return: a pandas DataFrame with timestamp, value, and status

    Example:

    >>> df = GetHistAvg("Site.Service.Tag", "01/01/17 01:01:01", \
                        "01/02/17 01:01:01", "00:00:01")

    """
    # Check if the point even exists
    if not DoesIDExist(tag_name):
        warnings.warn("WARNING- " + tag_name + " does not exist or " +
            "connection was dropped. Try again if tag does exist.")
        return pd.DataFrame()

    # Define all required variables in the correct ctypes format
    szPoint = c_char_p(tag_name.encode('utf-8'))
    szStart = c_char_p(start_time.encode('utf-8'))
    szEnd = c_char_p(end_time.encode('utf-8'))
    szPeriod = c_char_p(period.encode('utf-8'))
    pulKey = c_ulong(0)

    # Initialize the data pull using the specified pulKey, which is an
    # identifier that tells eDNA which data pull is occurring
    nRet = dna_dll.DnaGetHistAvg(szPoint, szStart, szEnd, szPeriod,
                                 byref(pulKey))
    # The internal function _GetNextHist iterates over the initialized pull
    df = _GetNextHist(pulKey, nRet, tag_name)
    if df.empty:
        warnings.warn('WARNING- No data retrieved for ' + tag_name + '. ' +
                      'Check eDNA connection, ensure that the start time is ' +
                      'not later than the end time, verify that the ' +
                      'DateTime formatting matches eDNA requirements, and ' +
                      'check that data exists in the query time period.')
    return df


def GetHistInterp(tag_name, start_time, end_time, period):
    """
    Retrieves data from eDNA history for a given tag. The data will be
    linearly interpolated over the specified "period".

    :param tag_name: fully-qualified (site.service.tag) eDNA tag
    :param start_time: must be in format mm/dd/yy hh:mm:ss
    :param end_time: must be in format mm/dd/yy hh:mm:ss
    :param period: must be in format hh:mm:ss
    :return: a pandas DataFrame with timestamp, value, and status

    Example:

    >>> df = GetHistInterp("Site.Service.Tag", "01/01/17 01:01:01", \
                           "01/02/17 01:01:01", "00:00:01")

    """
    # Check if the point even exists
    if not DoesIDExist(tag_name):
        warnings.warn("WARNING- " + tag_name + " does not exist or " +
                      "connection was dropped. Try again if tag does exist.")
        return pd.DataFrame()

    # Define all required variables in the correct ctypes format
    szPoint = c_char_p(tag_name.encode('utf-8'))
    szStart = c_char_p(start_time.encode('utf-8'))
    szEnd = c_char_p(end_time.encode('utf-8'))
    szPeriod = c_char_p(period.encode('utf-8'))
    pulKey = c_ulong(0)

    # Initialize the data pull using the specified pulKey, which is an
    # identifier that tells eDNA which data pull is occurring
    nRet = dna_dll.DnaGetHistInterp(szPoint, szStart, szEnd, szPeriod,
                                    byref(pulKey))
    # The internal function _GetNextHist iterates over the initialized pull
    df = _GetNextHist(pulKey, nRet, tag_name)
    if df.empty:
        warnings.warn('WARNING- No data retrieved for ' + tag_name + '. ' +
                      'Check eDNA connection, ensure that the start time is ' +
                      'not later than the end time, verify that the ' +
                      'DateTime formatting matches eDNA requirements, and ' +
                      'check that data exists in the query time period.')
    return df


def GetHistMax(tag_name, start_time, end_time, period):
    """
    Retrieves data from eDNA history for a given tag. The maximum of the data
    will be found over the specified "period".

    :param tag_name: fully-qualified (site.service.tag) eDNA tag
    :param start_time: must be in format mm/dd/yy hh:mm:ss
    :param end_time: must be in format mm/dd/yy hh:mm:ss
    :param period: must be in format hh:mm:ss
    :return: a pandas DataFrame with timestamp, value, and status

    Example:

    >>> df = GetHistMax("Site.Service.Tag", "01/01/17 01:01:01", \
                        "01/02/17 01:01:01", "00:00:01")

    """
    # Check if the point even exists
    if not DoesIDExist(tag_name):
        warnings.warn("WARNING- " + tag_name + " does not exist or " +
                      "connection was dropped. Try again if tag does exist.")
        return pd.DataFrame()

    # Define all required variables in the correct ctypes format
    szPoint = c_char_p(tag_name.encode('utf-8'))
    szStart = c_char_p(start_time.encode('utf-8'))
    szEnd = c_char_p(end_time.encode('utf-8'))
    szPeriod = c_char_p(period.encode('utf-8'))
    pulKey = c_ulong(0)

    # Initialize the data pull using the specified pulKey, which is an
    # identifier that tells eDNA which data pull is occurring
    nRet = dna_dll.DnaGetHistMax(szPoint, szStart, szEnd, szPeriod,
                                 byref(pulKey))
    # The internal function _GetNextHist iterates over the initialized pull
    df = _GetNextHist(pulKey, nRet, tag_name)
    if df.empty:
        warnings.warn('WARNING- No data retrieved for ' + tag_name + '. ' +
                      'Check eDNA connection, ensure that the start time is ' +
                      'not later than the end time, verify that the ' +
                      'DateTime formatting matches eDNA requirements, and ' +
                      'check that data exists in the query time period.')
    return df


def GetHistMin(tag_name, start_time, end_time, period):
    """
    Retrieves data from eDNA history for a given tag. The minimum of the data
    will be found over the specified "period".

    :param tag_name: fully-qualified (site.service.tag) eDNA tag
    :param start_time: must be in format mm/dd/yy hh:mm:ss
    :param end_time: must be in format mm/dd/yy hh:mm:ss
    :param period: must be in format hh:mm:ss
    :return: a pandas DataFrame with timestamp, value, and status

    Example:

    >>> df = GetHistMin("Site.Service.Tag", "01/01/17 01:01:01", \
                        "01/02/17 01:01:01", "00:00:01")

    """
    # Check if the point even exists
    if not DoesIDExist(tag_name):
        warnings.warn("WARNING- " + tag_name + " does not exist or " +
                      "connection was dropped. Try again if tag does exist.")
        return pd.DataFrame()

    # Define all required variables in the correct ctypes format
    szPoint = c_char_p(tag_name.encode('utf-8'))
    szStart = c_char_p(start_time.encode('utf-8'))
    szEnd = c_char_p(end_time.encode('utf-8'))
    szPeriod = c_char_p(period.encode('utf-8'))
    pulKey = c_ulong(0)

    # Initialize the data pull using the specified pulKey, which is an
    # identifier that tells eDNA which data pull is occurring
    nRet = dna_dll.DnaGetHistMin(szPoint, szStart, szEnd, szPeriod,
                                 byref(pulKey))
    # The internal function _GetNextHist iterates over the initialized pull
    df = _GetNextHist(pulKey, nRet, tag_name)
    if df.empty:
        warnings.warn('WARNING- No data retrieved for ' + tag_name + '. ' +
                      'Check eDNA connection, ensure that the start time is ' +
                      'not later than the end time, verify that the ' +
                      'DateTime formatting matches eDNA requirements, and ' +
                      'check that data exists in the query time period.')
    return df


def GetMultipleTags(tag_list, start_time, end_time, sampling_rate=None,
                    fill_limit=60, verify_time=False):
    """
    Retrieves raw data from eDNA history for multiple tags, merging them into
    a single DataFrame, and resampling the data according to the specified
    sampling_rate.

    :param tag_list: a list of fully-qualified (site.service.tag) eDNA tags
    :param start_time: must be in format mm/dd/yy hh:mm:ss
    :param end_time: must be in format mm/dd/yy hh:mm:ss
    :param sampling_rate: in units of seconds
    :param fill_limit: in units of data points
    :param verify_time: verify that the time is not before or after the query
    :return: a pandas DataFrame with timestamp and values
    """
    # Since we are pulling data from multiple tags, let's iterate over each
    # one. For this case, we only want to pull data using the "raw" method,
    # which will obtain all data as it is actually stored in the historian.
    # We will be resampling and forward-filling the data, so other retrieval
    # methods do not even apply.
    dfs = []
    for tag in tag_list:
        df = GetHistRaw(tag, start_time, end_time)
        if not df.empty:
            df.drop_duplicates(inplace=True)
            dfs.append(pd.DataFrame(df[tag]))

    # Next, we concatenate all the DataFrames using an outer join (default).
    # Verify integrity is slow, but it ensures that the concatenation
    # worked correctly.
    if dfs:
        merged_df = pd.concat(dfs, axis=1, verify_integrity=True)
        merged_df = merged_df.fillna(method="ffill", limit=fill_limit)
    else:
        warnings.warn('WARNING- No data retrieved for any tags. ' +
                      'Check eDNA connection, ensure that the start time is ' +
                      'not later than the end time, verify that the ' +
                      'DateTime formatting matches eDNA requirements, and ' +
                      'check that data exists in the query time period.')
        return pd.DataFrame()

    # eDNA sometimes pulls data too early or too far- let's filter out all
    # the data that is not within our original criteria.
    if verify_time:
        start_np = pd.to_datetime(start_time)
        end_np = pd.to_datetime(end_time)
        mask = (merged_df.index > start_np) & (merged_df.index <= end_np)
        merged_df = merged_df.loc[mask]

    # Finally, we resample the data at the rate requested by the user.
    if sampling_rate:
        sampling_string = str(sampling_rate) + "S"
        merged_df = merged_df.resample(sampling_string).fillna(
            method="ffill", limit=fill_limit)

    return merged_df


def GetHistRaw(tag_name, start_time, end_time, high_speed=False):
    """
    Retrieves raw data from eDNA history for a given tag.

    :param tag_name: fully-qualified (site.service.tag) eDNA tag
    :param start_time: must be in format mm/dd/yy hh:mm:ss
    :param end_time: must be in format mm/dd/yy hh:mm:ss
    :param high_speed: true = pull milliseconds
    :return: a pandas DataFrame with timestamp, value, and status

    Example:

    >>> df = GetHistRaw("Site.Service.Tag", "01/01/17 01:01:01", \
                        "01/02/17 01:01:01")

    """
    # Check if the point even exists
    if not DoesIDExist(tag_name):
        warnings.warn("WARNING- " + tag_name + " does not exist or " +
                      "connection was dropped. Try again if tag does exist.")
        return pd.DataFrame()

    # Define all required variables in the correct ctypes format
    szPoint = c_char_p(tag_name.encode('utf-8'))
    szStart = c_char_p(start_time.encode('utf-8'))
    szEnd = c_char_p(end_time.encode('utf-8'))
    pulKey = c_ulong(0)

    # Initialize the data pull using the specified pulKey, which is an
    # identifier that tells eDNA which data pull is occurring
    if high_speed:
        nRet = dna_dll.DnaGetHSHistRaw(szPoint, szStart, szEnd, byref(pulKey))
    else:
        nRet = dna_dll.DnaGetHistRaw(szPoint, szStart, szEnd, byref(pulKey))
    # The internal function _GetNextHist iterates over the initialized pull
    df = _GetNextHist(pulKey, nRet, tag_name, high_speed)
    if df.empty:
        warnings.warn('WARNING- No data retrieved for ' + tag_name + '. ' +
                      'Check eDNA connection, ensure that the start time is ' +
                      'not later than the end time, verify that the ' +
                      'DateTime formatting matches eDNA requirements, and ' +
                      'check that data exists in the query time period.')
    return df


def GetHistSnap(tag_name, start_time, end_time, period):
    """
    Retrieves data from eDNA history for a given tag. The data will be
    snapped to the last known value over intervals of the specified "period".

    :param tag_name: fully-qualified (site.service.tag) eDNA tag
    :param start_time: must be in format mm/dd/yy hh:mm:ss
    :param end_time: must be in format mm/dd/yy hh:mm:ss
    :param period: must be in format hh:mm:ss
    :return: a pandas DataFrame with timestamp, value, and status

    Example:

    >>> df = GetHistSnap("Site.Service.Tag", "01/01/17 01:01:01", \
                         "01/02/17 01:01:01", "00:00:01")

    """
    # Check if the point even exists
    if not DoesIDExist(tag_name):
        warnings.warn("WARNING- " + tag_name + " does not exist or " +
                      "connection was dropped. Try again if tag does exist.")
        return pd.DataFrame()

    # Define all required variables in the correct ctypes format
    szPoint = c_char_p(tag_name.encode('utf-8'))
    szStart = c_char_p(start_time.encode('utf-8'))
    szEnd = c_char_p(end_time.encode('utf-8'))
    szPeriod = c_char_p(period.encode('utf-8'))
    pulKey = c_ulong(0)
    # Initialize the data pull using the specified pulKey, which is an
    # identifier that tells eDNA which data pull is occurring
    nRet = dna_dll.DnaGetHistSnap(szPoint, szStart, szEnd, szPeriod,
                                  byref(pulKey))
    # The internal function _GetNextHist iterates over the initialized pull
    df = _GetNextHist(pulKey, nRet, tag_name)
    if df.empty:
        warnings.warn('WARNING- No data retrieved for ' + tag_name + '. ' +
                      'Check eDNA connection, ensure that the start time is ' +
                      'not later than the end time, verify that the ' +
                      'DateTime formatting matches eDNA requirements, and ' +
                      'check that data exists in the query time period.')
    return df


def HistAppendValues(site_service, tag_name, times, values, statuses):
    """
    Appends a value to an eDNA history service. Take very careful note of the
    following required parameters. Any deviation from this exact format WILL
    cause the function to fail.

    This function will append values to history, only if they are LATER than
    the current time of the last written data point. If this is not true, no
    data will be appended.

    This value is strongly preferred over HistUpdateInsertValues, which will
    slow down data retrieval if it is used too often.

    :param site_service: This is the history service for the eDNA tag, NOT
                         the site.service of the tag itself. For instance,
                         ANTARES.HISTORY, not ANTARES.ANVCALC
    :param tag_name:     This is the full site.service.tag. For instance,
                         ANTARES.ANVCALC.ADE1CA02
    :param times:        This is a Python array of times in UTC Epoch format.
                         For example, "1483926416" not "2016/01/01 01:01:01".
                         This must be an array.
    :param values:       A Python array of data point values for each times.
    :param statuses:     The status of the point. Refer to eDNA documentation
                         for more information. Usually use '3', which is 'OK'.
    """
    # Define all required variables in the correct ctypes format
    szService = c_char_p(site_service.encode('utf-8'))
    szPoint = c_char_p(tag_name.encode('utf-8'))
    nCount = c_ushort(1)

    # Iterate over each user-supplied data point
    for dttime, value, status in zip(times, values, statuses):
        # Define all required variables in the correct ctypes format
        PtTimeList = c_long(dttime)
        PusStatusList = c_ushort(status)
        PszValueList = c_char_p(str(value).encode('utf-8'))
        szError = create_string_buffer(20)
        nError = c_ushort(20)
        # Call the history append file
        nRet = dna_dll.DnaHistAppendValues(szService, szPoint,
                    nCount, byref(PtTimeList), byref(PusStatusList),
                    byref(PszValueList), byref(szError), nError)


def HistUpdateInsertValues(site_service, tag_name, times, values, statuses):
    """
    CAUTION- Use HistAppendValues instead of this function, unless you know
    what you are doing.

    Inserts a value to an eDNA history service. Take very careful note of the
    following required parameters. Any deviation from this exact format WILL
    cause the function to fail.

    :param site_service: This is the history service for the eDNA tag, NOT
                         the site.service of the tag itself. For instance,
                         ANTARES.HISTORY, not ANTARES.ANVCALC
    :param tag_name:     This is the full site.service.tag. For instance,
                         ANTARES.ANVCALC.ADE1CA02
    :param times:        This is a Python array of times in UTC Epoch format.
                         For example, "1483926416" not "2016/01/01 01:01:01".
                         This must be an array.
    :param values:       A Python array of data point values for each times.
    :param statuses:     The status of the point. Refer to eDNA documentation
                         for more information. Usually use '3', which is 'OK'.
    """
    # Define all required variables in the correct ctypes format
    szService = c_char_p(site_service.encode('utf-8'))
    szPoint = c_char_p(tag_name.encode('utf-8'))
    nCount = c_ushort(1)

    # Iterate over each user-supplied data point
    for dttime, value, status in zip(times, values, statuses):
        # Define all required variables in the correct ctypes format
        PtTimeList = c_long(dttime)
        PusStatusList = c_ushort(status)
        PszValueList = c_char_p(str(value).encode('utf-8'))
        szError = create_string_buffer(20)
        nError = c_ushort(20)
        # Call the history append file
        nRet = dna_dll.DnaHistUpdateInsertValues(szService, szPoint,
                    nCount, byref(PtTimeList), byref(PusStatusList),
                    byref(PszValueList), byref(szError), nError)


def SelectPoint():
    """
    Opens an eDNA point picker, where the user can select a single tag.

    :return: selected tag name

    Example:

    >>> tag = SelectPoint()

    """
    # Define all required variables in the correct ctypes format
    pszPoint = create_string_buffer(20)
    nPoint = c_ushort(20)
    # Opens the point picker
    dna_dll.DnaSelectPoint(byref(pszPoint), nPoint)
    tag_result = pszPoint.value.decode('utf-8')
    return tag_result


# At the end of the module, we need to check that at least one eDNA service
# is connected. Otherwise, there is a problem with the eDNA connection.
service_array = GetServices()
if not service_array.empty:
    num_services = str(len(service_array))
    print("Successfully connected to " + num_services + " eDNA services.")
# Cleanup the unncessary variables
del(service_array, num_services, default_location)
