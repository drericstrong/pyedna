# -*- coding: utf-8 -*-
"""
    pyedna.ezdna
    ~~~~~~~~~~~~~~~
    This module contains "easy" versions of common functions from the eDNA
    C++ dll. Obtain a legal copy of the C++ eDNA dll for use.

    :copyright: (c) 2017 Eric Strong.
    :license: Refer to LICENSE.txt for more information.
"""

import os
import pandas as pd
from ctypes import cdll, byref, create_string_buffer
from ctypes import c_char_p, c_double, c_short, c_ushort, c_long, c_ulong

# This code should execute at the beginning of the module import, because
# all of the functions in this module require the dna_dll library to be
# loaded. If the file is not in the default location, the user must explicitly
# load it using the LoadDll function.
default_location = "C:\\Program Files (x86)\\eDNA\\EzDnaApi64.dll"
if os.path.isfile(default_location):
    dna_dll = cdll.LoadLibrary(default_location)
else:
    dna_dll = None


def LoadDll(location):
    """
    If the EzDnaApi64.dll file is not in the default location
    (C:\Program Files (x86)\eDNA\EzDnaApi64.dll) then the user must specify
    the correct location of the file, before this module can be used.

    :param location: the full location of EzDnaApi64.dll, including filename
    """
    global dna_dll
    dna_dll = cdll.LoadLibrary(location)


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
    byte_string = tag_name.encode('utf-8')
    szPoint = c_char_p(byte_string)
    result = bool(dna_dll.DoesIdExist(szPoint))
    return result


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
    # Define all required variables in the correct ctypes format
    byte_string = tag_name.encode('utf-8')
    szPoint = c_char_p(byte_string)
    pdValue = c_double(-9999)
    szValue = create_string_buffer(b"                    ")
    nValue = c_ushort(20)
    ptTime = c_long(-9999)
    szTime = create_string_buffer(b"                    ")
    nTime = c_ushort(20)
    pusStatus = c_ushort(0)
    szStatus = create_string_buffer(b"                    ")
    nStatus = c_ushort(20)
    szDesc = create_string_buffer(b"                    ")
    nDesc = c_ushort(20)
    szUnits = create_string_buffer(b"                    ")
    nUnits = c_ushort(20)

    # Call the eDNA function. nRet is zero if the function is successful
    nRet = dna_dll.DNAGetRTFull(szPoint, byref(pdValue), byref(szValue), nValue,
                                byref(ptTime), byref(szTime), nTime,
                                byref(pusStatus), byref(szStatus), nStatus,
                                byref(szDesc), nDesc, byref(szUnits), nUnits)

    # Check to make sure the function returned correctly. If not, return None
    if nRet == 0:
        return (pdValue.value, szTime.value.decode('utf-8'),
                szStatus.value.decode('utf-8'), pusStatus.value,
                szDesc.value.decode('utf-8'), szUnits.value.decode('utf-8'))
    else:
        return None


def _GetNextHist(pulKey, nRet, tag_name):
    # This is a base function that iterates over a predefined history call,
    # which may be raw, snap, max, min, etc.
    # Define all required variables in the correct ctypes format
    pdValue = c_double(-9999)
    szTime = create_string_buffer(b"                    ")
    nTime = c_ushort(20)
    szStatus = create_string_buffer(b"                    ")
    nStatus = c_ushort(20)
    time_array = []
    val_array = []
    status_array = []

    # Once nRet is not zero, the function was terminated, either due to an
    # error or due to the end of the data period.
    while nRet == 0:
        nRet = dna_dll.DnaGetNextHist(pulKey, byref(pdValue), byref(szTime),
                                     nTime, byref(szStatus), nStatus)
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
    # Define all required variables in the correct ctypes format
    byte_tag = tag_name.encode('utf-8')
    byte_start= start_time.encode('utf-8')
    byte_end = end_time.encode('utf-8')
    byte_period = period.encode('utf-8')
    szPoint = c_char_p(byte_tag)
    szStart = c_char_p(byte_start)
    szEnd = c_char_p(byte_end)
    szPeriod = c_char_p(byte_period)
    pulKey = c_ulong(0)

    # Initialize the data pull using the specified pulKey, which is an
    # identifier that tells eDNA which data pull is occurring
    nRet = dna_dll.DnaGetHistAvg(szPoint, szStart, szEnd, szPeriod,
                                 byref(pulKey))
    # The internal function _GetNextHist iterates over the initialized pull
    df = _GetNextHist(pulKey, nRet, tag_name)
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
    # Define all required variables in the correct ctypes format
    byte_tag = tag_name.encode('utf-8')
    byte_start = start_time.encode('utf-8')
    byte_end = end_time.encode('utf-8')
    byte_period = period.encode('utf-8')
    szPoint = c_char_p(byte_tag)
    szStart = c_char_p(byte_start)
    szEnd = c_char_p(byte_end)
    szPeriod = c_char_p(byte_period)
    pulKey = c_ulong(0)

    # Initialize the data pull using the specified pulKey, which is an
    # identifier that tells eDNA which data pull is occurring
    nRet = dna_dll.DnaGetHistInterp(szPoint, szStart, szEnd, szPeriod,
                                    byref(pulKey))
    # The internal function _GetNextHist iterates over the initialized pull
    df = _GetNextHist(pulKey, nRet, tag_name)
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
    # Define all required variables in the correct ctypes format
    byte_tag = tag_name.encode('utf-8')
    byte_start = start_time.encode('utf-8')
    byte_end = end_time.encode('utf-8')
    byte_period = period.encode('utf-8')
    szPoint = c_char_p(byte_tag)
    szStart = c_char_p(byte_start)
    szEnd = c_char_p(byte_end)
    szPeriod = c_char_p(byte_period)
    pulKey = c_ulong(0)

    # Initialize the data pull using the specified pulKey, which is an
    # identifier that tells eDNA which data pull is occurring
    nRet = dna_dll.DnaGetHistMax(szPoint, szStart, szEnd, szPeriod,
                                 byref(pulKey))
    # The internal function _GetNextHist iterates over the initialized pull
    df = _GetNextHist(pulKey, nRet, tag_name)
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
    # Define all required variables in the correct ctypes format
    byte_tag = tag_name.encode('utf-8')
    byte_start = start_time.encode('utf-8')
    byte_end = end_time.encode('utf-8')
    byte_period = period.encode('utf-8')
    szPoint = c_char_p(byte_tag)
    szStart = c_char_p(byte_start)
    szEnd = c_char_p(byte_end)
    szPeriod = c_char_p(byte_period)
    pulKey = c_ulong(0)

    # Initialize the data pull using the specified pulKey, which is an
    # identifier that tells eDNA which data pull is occurring
    nRet = dna_dll.DnaGetHistMin(szPoint, szStart, szEnd, szPeriod,
                                 byref(pulKey))
    # The internal function _GetNextHist iterates over the initialized pull
    df = _GetNextHist(pulKey, nRet, tag_name)
    return df


def GetMultipleTags(tag_list, start_time, end_time, sampling_rate=5,
                    fill_limit=600):
    """
    Retrieves raw data from eDNA history for multiple tags, merging them into
    a single DataFrame, and resampling the data according to the specified
    sampling_rate.

    :param tag_list: a list of fully-qualified (site.service.tag) eDNA tags
    :param start_time: must be in format mm/dd/yy hh:mm:ss
    :param end_time: must be in format mm/dd/yy hh:mm:ss
    :param sampling_rate: in units of seconds
    :param fill_limit: in units of data points
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
        dfs.append(pd.DataFrame(df[tag]))

    # Next, we concatenate all the DataFrames using an outer join (default).
    merged_df = pd.concat(dfs)

    # eDNA sometimes pulls data too early or too far- let's filter out all
    # the data that is not within our original criteria.
    start_np = pd.to_datetime(start_time)
    end_np = pd.to_datetime(end_time)
    mask = (merged_df.index > start_np) & (merged_df.index <= end_np)
    merged_df = merged_df.loc[mask]

    # The data must first be forward filled, and all duplicate indices
    # removed (this sometimes occurs during the pandas concat), or otherwise
    # the subsequent functions will fail
    merged_df.ffill(inplace=True)
    merged_df = merged_df.groupby(merged_df.index).first()

    # Finally, we resample the data at the rate requested by the user.
    sampling_string = str(sampling_rate) + "S"
    merged_df = merged_df.resample(sampling_string).fillna(method="ffill",
                                                           limit=fill_limit)
    return merged_df


def GetHistRaw(tag_name, start_time, end_time):
    """
    Retrieves raw data from eDNA history for a given tag.

    :param tag_name: fully-qualified (site.service.tag) eDNA tag
    :param start_time: must be in format mm/dd/yy hh:mm:ss
    :param end_time: must be in format mm/dd/yy hh:mm:ss
    :return: a pandas DataFrame with timestamp, value, and status

    Example:

    >>> df = GetHistRaw("Site.Service.Tag", "01/01/17 01:01:01", \
                        "01/02/17 01:01:01")

    """
    # Define all required variables in the correct ctypes format
    byte_tag = tag_name.encode('utf-8')
    byte_start = start_time.encode('utf-8')
    byte_end = end_time.encode('utf-8')
    szPoint = c_char_p(byte_tag)
    szStart = c_char_p(byte_start)
    szEnd = c_char_p(byte_end)
    pulKey = c_ulong(0)
    # Initialize the data pull using the specified pulKey, which is an
    # identifier that tells eDNA which data pull is occurring
    nRet = dna_dll.DnaGetHistRaw(szPoint, szStart, szEnd, byref(pulKey))
    # The internal function _GetNextHist iterates over the initialized pull
    df = _GetNextHist(pulKey, nRet, tag_name)
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
    # Define all required variables in the correct ctypes format
    byte_tag = tag_name.encode('utf-8')
    byte_start = start_time.encode('utf-8')
    byte_end = end_time.encode('utf-8')
    byte_period = period.encode('utf-8')
    szPoint = c_char_p(byte_tag)
    szStart = c_char_p(byte_start)
    szEnd = c_char_p(byte_end)
    szPeriod = c_char_p(byte_period)
    pulKey = c_ulong(0)
    # Initialize the data pull using the specified pulKey, which is an
    # identifier that tells eDNA which data pull is occurring
    nRet = dna_dll.DnaGetHistSnap(szPoint, szStart, szEnd, szPeriod,
                                  byref(pulKey))
    # The internal function _GetNextHist iterates over the initialized pull
    df = _GetNextHist(pulKey, nRet, tag_name)
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
    byte_service = site_service.encode('utf-8')
    byte_tag = tag_name.encode('utf-8')
    szService = c_char_p(byte_service)
    szPoint = c_char_p(byte_tag)
    nCount = c_ushort(1)

    # Iterate over each user-supplied data point
    for dttime, value, status in zip(times, values, statuses):
        # Define all required variables in the correct ctypes format
        PtTimeList = c_long(dttime)
        PusStatusList = c_ushort(status)
        byte_value = str(value).encode('utf-8')
        PszValueList = c_char_p(byte_value)
        szError = create_string_buffer(b"                    ")
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
    byte_service = site_service.encode('utf-8')
    byte_tag = tag_name.encode('utf-8')
    szService = c_char_p(byte_service)
    szPoint = c_char_p(byte_tag)
    nCount = c_ushort(1)

    # Iterate over each user-supplied data point
    for dttime, value, status in zip(times, values, statuses):
        # Define all required variables in the correct ctypes format
        PtTimeList = c_long(dttime)
        PusStatusList = c_ushort(status)
        byte_value = str(value).encode('utf-8')
        PszValueList = c_char_p(byte_value)
        szError = create_string_buffer(b"                    ")
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
    pszPoint = create_string_buffer(b"                    ")
    nPoint = c_ushort(20)
    # Opens the point picker
    dna_dll.DnaSelectPoint(byref(pszPoint), nPoint)
    tag_result = pszPoint.value.decode('utf-8')
    return tag_result
