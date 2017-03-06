# -*- coding: utf-8 -*-
"""
    pyedna.ezdna
    ~~~~~~~~~~~~~
    This module contains "easy" versions of common functions from the eDNA
    C++ dll. Obtain a legal copy of the C++ eDNA dll for use.

    :copyright: (c) 2017 Eric Strong.
    :license: Refer to LICENSE.txt for more information.
"""

# TODO- Test data push
# Note- all functions are in CamelCase to match the original eDNA function
# names, even though this does not follow PEP 8.

import re
import os
import numba
import warnings
import numpy as np
import pandas as pd
from unittest.mock import Mock
from ctypes import cdll, byref, create_string_buffer
from ctypes import c_char_p, c_double, c_ushort, c_long, c_ulong


def _mock_edna():
    # This function will mock all the methods that were used in the dna_dll.
    # It's necessary so that documentation can be automatically created.
    dna_dll = Mock()
    attrs = {'DnaGetHistAvgUTC.return_value': c_ulong(1),
             'DnaGetHistInterpUTC.return_value': c_ulong(1),
             'DnaGetHistMinUTC.return_value': c_ulong(1),
             'DnaGetHistMaxUTC.return_value': c_ulong(1),
             'DnaGetHistSnapUTC.return_value': c_ulong(1),
             'DnaGetHistRawUTC.return_value': c_ulong(1),
             'DoesIdExist.return_value': c_ulong(1),
             'DnaGetHSHistRawUTC.return_value': c_ulong(1),
             'DnaGetNextHSHistUTC.return_value': c_ulong(1),
             'DnaGetPointEntry.return_value': c_ulong(1),
             'DnaGetNextPointEntry.return_value': c_ulong(1),
             'DNAGetRTFull.return_value': c_ulong(1),
             'DnaSelectPoint.return_value': c_ulong(1),
             'StringToUTCTime.return_value': 1,
             'DnaGetServiceEntry.return_value': c_ulong(1),
             'DnaGetNextServiceEntry.return_value': c_ulong(1),
             'DnaHistAppendValues.return_value': c_ulong(1),
             'DnaHistUpdateInsertValues.return_value': c_ulong(1),
             'DnaCancelHistRequest.return_value': None,
             'DnaGetNextHistSmallUTC.return_value': c_ulong(1)}
    dna_dll.configure_mock(**attrs)
    return dna_dll

# This code should execute at the beginning of the module import, because
# all of the functions in this module require the dna_dll library to be
# loaded. See "LoadDll" if not in default location
default_location = "C:\\Program Files (x86)\\eDNA\\EzDnaApi64.dll"
if os.path.isfile(default_location):
    dna_dll = cdll.LoadLibrary(default_location)
else:
    warnings.warn("ERROR- no eDNA dll detected at " +
                  "C:\\Program Files (x86)\\eDNA\\EzDnaApi64.dll" +
                  " . Please manually load dll using the LoadDll function. " +
                  "Mocking dll, but all functions will fail until " +
                  "dll is manually loaded...")
    dna_dll = _mock_edna()


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


def _format_str(text):
    # Only allows a-z, 0-9, ., _, :, /, -, and spaces
    if type(text) is str:
        formatted_text = re.sub('[^-._:/\sA-Za-z0-9]+', '', text).strip()
        return formatted_text
    else:
        return text


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


def GetHistAvg(tag_name, start_time, end_time, period,
               desc_as_label=False, label=None):
    """
    Retrieves data from eDNA history for a given tag. The data will be
    averaged over the specified "period".

    :param tag_name: fully-qualified (site.service.tag) eDNA tag
    :param start_time: must be in format mm/dd/yy hh:mm:ss
    :param end_time: must be in format mm/dd/yy hh:mm:ss
    :param period: in units of seconds (e.g. 10)
    :param desc_as_label: use the tag description as the column name instead
        of the full tag
    :param label: supply a custom label to use as the DataFrame column name
    :return: a pandas DataFrame with timestamp, value, and status
    """
    return GetHist(tag_name, start_time, end_time, mode="avg", period=period,
                   desc_as_label=desc_as_label, label=label)

def GetHistInterp(tag_name, start_time, end_time, period,
                  desc_as_label=False, label=None):
    """
    Retrieves data from eDNA history for a given tag. The data will be
    linearly interpolated over the specified "period".

    :param tag_name: fully-qualified (site.service.tag) eDNA tag
    :param start_time: must be in format mm/dd/yy hh:mm:ss
    :param end_time: must be in format mm/dd/yy hh:mm:ss
    :param period: in units of seconds (e.g. 10)
    :param desc_as_label: use the tag description as the column name instead
        of the full tag
    :param label: supply a custom label to use as the DataFrame column name
    :return: a pandas DataFrame with timestamp, value, and status
    """
    return GetHist(tag_name, start_time, end_time, mode="interp",
                   period=period, desc_as_label=desc_as_label, label=label)


def GetHistMax(tag_name, start_time, end_time, period,
               desc_as_label=False, label=None):
    """
    Retrieves data from eDNA history for a given tag. The maximum of the data
    will be found over the specified "period".

    :param tag_name: fully-qualified (site.service.tag) eDNA tag
    :param start_time: must be in format mm/dd/yy hh:mm:ss
    :param end_time: must be in format mm/dd/yy hh:mm:ss
    :param period: in units of seconds (e.g. 10)
    :param desc_as_label: use the tag description as the column name instead
        of the full tag
    :param label: supply a custom label to use as the DataFrame column name
    :return: a pandas DataFrame with timestamp, value, and status
    """
    return GetHist(tag_name, start_time, end_time, mode="max",
                   period=period, desc_as_label=desc_as_label, label=label)


def GetHistMin(tag_name, start_time, end_time, period,
               desc_as_label=False, label=None):
    """
    Retrieves data from eDNA history for a given tag. The minimum of the data
    will be found over the specified "period".

    :param tag_name: fully-qualified (site.service.tag) eDNA tag
    :param start_time: must be in format mm/dd/yy hh:mm:ss
    :param end_time: must be in format mm/dd/yy hh:mm:ss
    :param period: in units of seconds (e.g. 10)
    :param desc_as_label: use the tag description as the column name instead
        of the full tag
    :param label: supply a custom label to use as the DataFrame column name
    :return: a pandas DataFrame with timestamp, value, and status
    """
    return GetHist(tag_name, start_time, end_time, mode="min",
                   period=period, desc_as_label=desc_as_label, label=label)


def GetHistRaw(tag_name, start_time, end_time, high_speed=False,
               desc_as_label=False, label=None):
    """
    Retrieves raw data from eDNA history for a given tag.

    :param tag_name: fully-qualified (site.service.tag) eDNA tag
    :param start_time: must be in format mm/dd/yy hh:mm:ss
    :param end_time: must be in format mm/dd/yy hh:mm:ss
    :param high_speed: true = pull milliseconds
    :param desc_as_label: use the tag description as the column name instead
        of the full tag
    :param label: supply a custom label to use as the DataFrame column name
    :return: a pandas DataFrame with timestamp, value, and status
    """
    return GetHist(tag_name, start_time, end_time, mode="raw",
                   desc_as_label=desc_as_label, label=label)


def GetHistSnap(tag_name, start_time, end_time, period,
                desc_as_label=False, label=None):
    """
    Retrieves data from eDNA history for a given tag. The data will be
    snapped to the last known value over intervals of the specified "period".

    :param tag_name: fully-qualified (site.service.tag) eDNA tag
    :param start_time: must be in format mm/dd/yy hh:mm:ss
    :param end_time: must be in format mm/dd/yy hh:mm:ss
    :param period: in units of seconds (e.g. 10)
    :param desc_as_label: use the tag description as the column name instead
        of the full tag
    :param label: supply a custom label to use as the DataFrame column name
    :return: a pandas DataFrame with timestamp, value, and status
    """
    return GetHist(tag_name, start_time, end_time, mode="snap",
                   period=period, desc_as_label=desc_as_label, label=label)


def GetHist(tag_name, start_time, end_time, period=5, mode="raw",
            desc_as_label=False, label=None, high_speed=False, utc=False):
    """
    Retrieves data from eDNA history for a given tag.

    :param tag_name: fully-qualified (site.service.tag) eDNA tag
    :param start_time: must be in format mm/dd/yy hh:mm:ss
    :param end_time: must be in format mm/dd/yy hh:mm:ss
    :param period: specify the number of seconds for the pull interval
    :param mode: "raw", "snap", "avg", "interp", "max", "min"
        See eDNA documentation for more information.
    :param desc_as_label: use the tag description as the column name instead
        of the full tag
    :param label: supply a custom label to use as the DataFrame column name
    :param high_speed: if True, pull millisecond data
    :param utc: if True, use the integer time format instead of DateTime
    :return: a pandas DataFrame with timestamp, value, and status
    """
    # Check if the point even exists
    if not DoesIDExist(tag_name):
        warnings.warn("WARNING- " + tag_name + " does not exist or " +
            "connection was dropped. Try again if tag does exist.")
        return pd.DataFrame()

    # Define all required variables in the correct ctypes format
    szPoint = c_char_p(tag_name.encode('utf-8'))
    tStart = c_long(StringToUTCTime(start_time))
    tEnd = c_long(StringToUTCTime(end_time))
    tPeriod = c_long(period)
    pulKey = c_ulong(0)

    # Initialize the data pull using the specified pulKey, which is an
    # identifier that tells eDNA which data pull is occurring
    mode = mode.lower().strip()
    if not high_speed:
        if mode == "avg":
            nRet = dna_dll.DnaGetHistAvgUTC(szPoint, tStart, tEnd, tPeriod, byref(pulKey))
        if mode == "interp":
            nRet = dna_dll.DnaGetHistInterpUTC(szPoint, tStart, tEnd, tPeriod, byref(pulKey))
        if mode == "min":
            nRet = dna_dll.DnaGetHistMinUTC(szPoint, tStart, tEnd, tPeriod, byref(pulKey))
        if mode == "max":
            nRet = dna_dll.DnaGetHistMaxUTC(szPoint, tStart, tEnd, tPeriod, byref(pulKey))
        if mode == "snap":
            nRet = dna_dll.DnaGetHistSnapUTC(szPoint, tStart, tEnd, tPeriod, byref(pulKey))
        else:
            nRet = dna_dll.DnaGetHistRawUTC(szPoint, tStart, tEnd, byref(pulKey))
        time_, val, stat = _GetNextHistSmallUTC(pulKey, nRet)
    else:
        nStartMillis = c_ushort(0)
        nEndMillis = c_ushort(0)
        nRet = dna_dll.DnaGetHSHistRawUTC(szPoint, tStart, nStartMillis,
            tEnd, nEndMillis, byref(pulKey))
        time_, val, stat = _GetNextHSHistUTC(pulKey, nRet)

    # The history request must be cancelled to free up network resources
    dna_dll.DnaCancelHistRequest(pulKey)

    # To construct the pandas DataFrame, the tag name will be used as the
    # column name, and the index (which is in the strange eDNA format) must be
    # converted to an actual DateTime
    d = {tag_name + ' Status': stat, tag_name: val}
    df = pd.DataFrame(data=d, index=time_)
    if not utc:
        if not high_speed:
            df.index = pd.to_datetime(df.index, unit="s")
        else:
            df.index = pd.to_datetime(df.index, unit="ms")
    if df.empty:
        warnings.warn('WARNING- No data retrieved for ' + tag_name + '. ' +
                      'Check eDNA connection, ensure that the start time is ' +
                      'not later than the end time, verify that the ' +
                      'DateTime formatting matches eDNA requirements, and ' +
                      'check that data exists in the query time period.')

    # Check if the user would rather use the description as the column name
    if desc_as_label or label:
        if label:
            new_label = label
        else:
            new_label = _GetLabel(tag_name)
        df.rename(inplace=True, columns={tag_name: new_label,
                  tag_name + " Status": new_label + " Status"})
    return df


@numba.jit
def _GetNextHistSmallUTC(pulKey, nRet):
    # This is a base function that iterates over a predefined history call,
    # which may be raw, snap, max, min, etc.
    pdValue, ptTime, pusStatus = c_double(-9999), c_long(-9999), c_ushort(0)
    refVal, refTime, refStat = byref(pdValue), byref(ptTime), byref(pusStatus)
    val = np.empty(0)
    time_ = np.empty(0)
    stat = np.empty(0)

    # Once nRet is not zero, the function was terminated, either due to an
    # error or due to the end of the data period.
    nRet = dna_dll.DnaGetNextHistSmallUTC(pulKey, refVal, refTime, refStat)
    while nRet == 0:
        val = np.append(val, pdValue.value)
        time_ = np.append(time_, ptTime.value)
        stat = np.append(stat, pusStatus.value)
        nRet = dna_dll.DnaGetNextHistSmallUTC(pulKey, refVal, refTime, refStat)
    return time_, val, stat


@numba.jit
def _GetNextHSHistUTC(pulKey, nRet):
    # This is a base function that iterates over a predefined history call,
    # which may be raw, snap, max, min, etc.
    pdValue, ptTime, pnMillis = c_double(-9999), c_long(-9999), c_ushort(0)
    szStatus, nStatus = create_string_buffer(20), c_ushort(20)
    refVal, refTime, refMillis = byref(pdValue), byref(ptTime), byref(pnMillis)
    refStatus = byref(szStatus)
    val = np.empty(0)
    time_ = np.empty(0)
    stat = np.empty(0)

    # Once nRet is not zero, the function was terminated, either due to an
    # error or due to the end of the data period.
    nRet = dna_dll.DnaGetNextHSHistUTC(pulKey, refVal, refTime, refMillis,
                                       refStatus, nStatus)
    while nRet == 0:
        val = np.append(val, pdValue.value)
        time_ = np.append(time_, ptTime.value * 1000 + pnMillis.value)
        stat = np.append(stat, 3)
        nRet = dna_dll.DnaGetNextHSHistUTC(pulKey, refVal, refTime, refMillis,
                                           refStatus, nStatus)
    return time_, val, stat


def _GetLabel(tag_name):
    # This function tries to get the tag description to use as the label for
    # the variable in the pandas DataFrame. It removes any special characters
    # and trims whitespace before and after. If the label is blank, the
    # tag name will be returned again instead.
    label = GetTagDescription(tag_name)
    if label:
        return label
    else:
        return tag_name


def GetMultipleTags(tag_list, start_time, end_time, sampling_rate=None,
                    fill_limit=99999, verify_time=False, desc_as_label=False):
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
    :param desc_as_label: use the tag description as the column name instead
        of the full tag
    :return: a pandas DataFrame with timestamp and values
    """
    # Since we are pulling data from multiple tags, let's iterate over each
    # one. For this case, we only want to pull data using the "raw" method,
    # which will obtain all data as it is actually stored in the historian.
    dfs = []
    columns_names = []
    for tag in tag_list:
        df = GetHist(tag, start_time, end_time)
        if not df.empty:
            # Sometimes a duplicate index/value pair is retrieved from
            # eDNA, which will cause the concat to fail if not removed
            # df.drop_duplicates(inplace=True)
            df = df[~df.index.duplicated(keep='first')]
            # If the user wants to use descriptions as labels, we need to
            # ensure that only unique labels are used
            label = tag
            if desc_as_label:
                orig_label = _GetLabel(tag)
                label = orig_label
                rename_number = 2
                while label in columns_names:
                    label = orig_label + str(rename_number)
                    rename_number += 1
                columns_names.append(label)
                df.rename(columns={tag: label}, inplace=True)
            # Add the DataFrame to the list, to be concatenated later
            dfs.append(pd.DataFrame(df[label]))

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


def _FormatPoints(szPoint, pdValue, szTime, szStatus, szDesc, szUnits):
    # Returns an array of properly-formatted points from the GetPoints function
    tag = _format_str(szPoint.value.decode(errors='ignore'))
    value = pdValue.value
    time_ = _format_str(szTime.value.decode(errors='ignore'))
    status = _format_str(szStatus.value.decode(errors='ignore'))
    desc = _format_str(szDesc.value.decode(errors='ignore'))
    units = _format_str(szUnits.value.decode(errors='ignore'))
    if szPoint.value.strip():
        return [tag, value, time_, status, desc, units]


def GetPoints(edna_service):
    """
    Obtains all the points in the edna_service, including real-time values.

    :param edna_service: The full Site.Service name of the eDNA service.
    :return: A pandas DataFrame of points in the form [Tag, Value, Time,
        Description, Units]
    """
    # Define all required variables in the correct ctypes format
    szServiceName = c_char_p(edna_service.encode('utf-8'))
    nStarting, pulKey, pdValue = c_ushort(0), c_ulong(0), c_double(-9999)
    szPoint, szTime = create_string_buffer(30), create_string_buffer(30)
    szStatus, szDesc = create_string_buffer(20), create_string_buffer(90)
    szUnits = create_string_buffer(20)
    szPoint2, szTime2 = create_string_buffer(30), create_string_buffer(30)
    szStatus2, szDesc2 = create_string_buffer(20), create_string_buffer(90)
    szUnits2, pdValue2 = create_string_buffer(20), c_double(-9999)
    nPoint, nTime, nStatus = c_ushort(30), c_ushort(30), c_ushort(20)
    nDesc, nUnits = c_ushort(90), c_ushort(20)

    # Call the eDNA function. nRet is zero if the function is successful.
    points = []
    nRet = dna_dll.DnaGetPointEntry(szServiceName, nStarting, byref(pulKey),
        byref(szPoint), nPoint, byref(pdValue), byref(szTime), nTime,
        byref(szStatus), nStatus, byref(szDesc), nDesc, byref(szUnits), nUnits)
    tag = _FormatPoints(szPoint, pdValue, szTime, szStatus, szDesc, szUnits)
    if tag:
        points.append(tag)

    # Iterate across all the returned services
    while nRet == 0:
        nRet = dna_dll.DnaGetNextPointEntry(pulKey, byref(szPoint2), nPoint,
            byref(pdValue2), byref(szTime2), nTime, byref(szStatus2), nStatus,
            byref(szDesc2), nDesc, byref(szUnits2), nUnits)
        # We want to ensure only UTF-8 characters are returned. Ignoring
        # characters is slightly unsafe, but they should only occur in the
        # units or description, so it's not a huge issue.
        tag = _FormatPoints(szPoint2, pdValue2, szTime2, szStatus2, szDesc2,
                            szUnits2)
        if tag:
            points.append(tag)

    # If no results were returned, raise a warning
    df = pd.DataFrame()
    if points:
        df = pd.DataFrame(points, columns=["Tag", "Value", "Time", "Status",
                                           "Description", "Units"])
    else:
        warnings.warn("WARNING- No points were returned. Check that the " +
                      "service exists and contains points.")
    return df


def GetRTFull(tag_name):
    """
    Gets current information about a point configured in a real-time
    eDNA service, including current value, time, status, description,
    and units.

    :param tag_name: fully-qualified (site.service.tag) eDNA tag
    :return: tuple of: alue, time, status, statusint, description, units
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

def _FormatServices(szSvcName, szSvcDesc, szSvcType, szSvcStat):
    # Returns an array of properly-formatted services from the
    # GetServices function
    name = _format_str(szSvcName.value.decode(errors='ignore'))
    desc = _format_str(szSvcDesc.value.decode(errors='ignore'))
    type_ = _format_str(szSvcType.value.decode(errors='ignore'))
    status = _format_str(szSvcStat.value.decode(errors='ignore'))
    if name:
        return [name, desc, type_, status]

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

    # Call the eDNA function. nRet is zero if the function is successful.
    services = []
    nRet = dna_dll.DnaGetServiceEntry(szType, szStartSvcName, byref(pulKey),
        byref(szSvcName), nSvcName, byref(szSvcDesc), nSvcDesc,
        byref(szSvcType), nSvcType, byref(szSvcStat), nSvcStat)
    serv = _FormatServices(szSvcName, szSvcDesc, szSvcType, szSvcStat)
    if serv:
        services.append(serv)

    # Iterate across all the returned services
    while nRet == 0:
        nRet = dna_dll.DnaGetNextServiceEntry(pulKey,
            byref(szSvcName2), nSvcName, byref(szSvcDesc2), nSvcDesc,
            byref(szSvcType2), nSvcType, byref(szSvcStat2), nSvcStat)
        # We want to ensure only UTF-8 characters are returned. Ignoring
        # characters is slightly unsafe, but they should only occur in the
        # units or description, so it's not a huge issue.
        serv = _FormatServices(szSvcName2, szSvcDesc2, szSvcType2, szSvcStat2)
        if serv:
            services.append(serv)

    # If no results were returned, raise a warning
    df = pd.DataFrame()
    if services:
        df = pd.DataFrame(services, columns=["Name", "Description", "Type",
                                             "Status"])
    else:
        warnings.warn("WARNING- No connected eDNA services detected. Check " +
                      "your DNASys.ini file and your network connection.")
    return df


def GetTagDescription(tag_name):
    """
    Gets the current description of a point configured in a real-time eDNA
    service.

    :param tag_name: fully-qualified (site.service.tag) eDNA tag
    :return: tag description
    """
    # Check if the point even exists
    if not DoesIDExist(tag_name):
        warnings.warn("WARNING- " + tag_name + " does not exist or " +
                      "connection was dropped. Try again if tag does exist.")
        return None

    # To get the point information for the service, we need the Site.Service
    split_tag = tag_name.split(".")
    # If the full Site.Service.Tag was not supplied, return the tag_name
    if len(split_tag) < 3:
        warnings.warn("WARNING- Please supply the full Site.Service.Tag.")
        return tag_name
    # The Site.Service will be the first two split strings
    site_service = split_tag[0] + "." + split_tag[1]

    # GetPoints will return a DataFrame with point information
    points = GetPoints(site_service)
    if tag_name in points.Tag.values:
        description = points[points.Tag == tag_name].Description.values[0]
        if description:
            return description
        else:
            return tag_name
    else:
        warnings.warn("WARNING- " + tag_name + " not found in service.")
        return None


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
    """
    # Define all required variables in the correct ctypes format
    pszPoint = create_string_buffer(20)
    nPoint = c_ushort(20)
    # Opens the point picker
    dna_dll.DnaSelectPoint(byref(pszPoint), nPoint)
    tag_result = pszPoint.value.decode('utf-8')
    return tag_result


def StringToUTCTime(time_string):
    """
    Turns a DateTime string into UTC time.

    :param time_string: Must be the format "MM/dd/yy hh:mm:ss"
    :return: an integer representing the UTC int format
    """
    szTime = c_char_p(time_string.encode('utf-8'))
    res = dna_dll.StringToUTCTime(szTime)
    return res


# At the end of the module, we need to check that at least one eDNA service
# is connected. Otherwise, there is a problem with the eDNA connection.
service_array = GetServices()
num_services = 0
if not service_array.empty:
    num_services = str(len(service_array))
    print("Successfully connected to " + num_services + " eDNA services.")
# Cleanup the unnecessary variables
del(service_array, num_services, default_location)
