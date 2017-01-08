# -*- coding: utf-8 -*-
"""
    pyedna.dna
    ~~~~~~~~~~~~~~~
    This module is a Python wrapper for the C++ eDNA library.
    Obtain a legal copy of the C++ eDNA dll for use.

    :copyright: (c) 2017 Eric Strong.
    :license: Refer to LICENSE.txt for more information.
"""

from ctypes import c_char_p, c_double, c_ushort, c_long, c_ulong
from ctypes import cdll, byref, create_string_buffer
import pandas as pd

location = "C:\\Program Files (x86)\\eDNA\\EzDnaApi64.dll"
dnadll = cdll.LoadLibrary(location)


def DoesIDExist(tag_name):
    """
    Determines if a fully-qualified site.service.tag eDNA tag exists
    in any of the connected services.

    :param tag_name: fully-qualified (site.service.tag) eDNA tag
    :return: true if the point exists, false if the point does not exist

    Example:

    >>> DoesIDExist("Site.Service.Tag")

    """
    byte_string = tag_name.encode('utf-8')
    szPoint = c_char_p(byte_string)
    result = bool(dnadll.DoesIdExist(szPoint))
    return result


def GetRTFull(tag_name):
    """
    Gets current information about a point configured in a real-time
    eDNA service, including current value, time, status, description,
    and units.

    :param tag_name: fully-qualified (site.service.tag) eDNA tag
    :return: value, time, status, statusint, description, units

    Example:

    >>> value, time, status, statusint, description, units = GetRTFull("Site.Service.Tag")

    """
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
    nRet = dnadll.DNAGetRTFull(szPoint, byref(pdValue), byref(szValue), nValue,
                               byref(ptTime), byref(szTime), nTime,
                               byref(pusStatus), byref(szStatus), nStatus,
                               byref(szDesc), nDesc, byref(szUnits), nUnits)
    if nRet == 0:
        return pdValue.value, \
            szTime.value.decode('utf-8'), \
            szStatus.value.decode('utf-8'), \
            pusStatus.value, \
            szDesc.value.decode('utf-8'), \
            szUnits.value.decode('utf-8')
    else:
        return None


def _GetNextHist(pulKey, nRet, tag_name):
    pdValue = c_double(-9999)
    szTime = create_string_buffer(b"                    ")
    nTime = c_ushort(20)
    szStatus = create_string_buffer(b"                    ")
    nStatus = c_ushort(20)
    time_array = []
    val_array = []
    status_array = []
    while nRet == 0:
        nRet = dnadll.DnaGetNextHist(pulKey, byref(pdValue), byref(szTime),
                                     nTime, byref(szStatus), nStatus)
        time_array.append(szTime.value.decode('utf-8'))
        val_array.append(pdValue.value)
        status_array.append(szStatus.value.decode('utf-8'))
    dnadll.DnaCancelHistRequest(pulKey)
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
    byte_tag = tag_name.encode('utf-8')
    byte_start= start_time.encode('utf-8')
    byte_end = end_time.encode('utf-8')
    byte_period = period.encode('utf-8')
    szPoint = c_char_p(byte_tag)
    szStart = c_char_p(byte_start)
    szEnd = c_char_p(byte_end)
    szPeriod = c_char_p(byte_period)
    pulKey = c_ulong(0)
    nRet = dnadll.DnaGetHistAvg(szPoint, szStart, szEnd, szPeriod, byref(pulKey))
    return _GetNextHist(pulKey, nRet, tag_name)


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
    byte_tag = tag_name.encode('utf-8')
    byte_start = start_time.encode('utf-8')
    byte_end = end_time.encode('utf-8')
    byte_period = period.encode('utf-8')
    szPoint = c_char_p(byte_tag)
    szStart = c_char_p(byte_start)
    szEnd = c_char_p(byte_end)
    szPeriod = c_char_p(byte_period)
    pulKey = c_ulong(0)
    nRet = dnadll.DnaGetHistInterp(szPoint, szStart, szEnd, szPeriod,
                                   byref(pulKey))
    return _GetNextHist(pulKey, nRet, tag_name)


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
    byte_tag = tag_name.encode('utf-8')
    byte_start = start_time.encode('utf-8')
    byte_end = end_time.encode('utf-8')
    byte_period = period.encode('utf-8')
    szPoint = c_char_p(byte_tag)
    szStart = c_char_p(byte_start)
    szEnd = c_char_p(byte_end)
    szPeriod = c_char_p(byte_period)
    pulKey = c_ulong(0)
    nRet = dnadll.DnaGetHistMax(szPoint, szStart, szEnd, szPeriod,
                                byref(pulKey))
    return _GetNextHist(pulKey, nRet, tag_name)


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
    byte_tag = tag_name.encode('utf-8')
    byte_start = start_time.encode('utf-8')
    byte_end = end_time.encode('utf-8')
    byte_period = period.encode('utf-8')
    szPoint = c_char_p(byte_tag)
    szStart = c_char_p(byte_start)
    szEnd = c_char_p(byte_end)
    szPeriod = c_char_p(byte_period)
    pulKey = c_ulong(0)
    nRet = dnadll.DnaGetHistMin(szPoint, szStart, szEnd, szPeriod,
                                byref(pulKey))
    return _GetNextHist(pulKey, nRet, tag_name)


def GetMultipleTags(tag_list, start_time, end_time, sampling_rate=5, fill_limit=600):
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
    start_np = pd.to_datetime(start_time)
    end_np = pd.to_datetime(end_time)
    samp_string = str(sampling_rate) + "S"
    df_list = []
    for tag in tag_list:
        df = GetHistRaw(tag, start_time, end_time)
        df_list.append(pd.DataFrame(df[tag]))
    merged_df = pd.concat(df_list)

    mask = (merged_df.index > start_np) & (merged_df.index <= end_np)
    merged_df = merged_df.loc[mask]

    merged_df.ffill(inplace=True)
    merged_df = merged_df.groupby(merged_df.index).first()
    merged_df = merged_df.resample(samp_string).fillna(method="ffill", limit=fill_limit)
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
    byte_tag = tag_name.encode('utf-8')
    byte_start = start_time.encode('utf-8')
    byte_end = end_time.encode('utf-8')
    szPoint = c_char_p(byte_tag)
    szStart = c_char_p(byte_start)
    szEnd = c_char_p(byte_end)
    pulKey = c_ulong(0)
    nRet = dnadll.DnaGetHistRaw(szPoint, szStart, szEnd, byref(pulKey))
    return _GetNextHist(pulKey, nRet, tag_name)


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
    byte_tag = tag_name.encode('utf-8')
    byte_start= start_time.encode('utf-8')
    byte_end = end_time.encode('utf-8')
    byte_period = period.encode('utf-8')
    szPoint = c_char_p(byte_tag)
    szStart = c_char_p(byte_start)
    szEnd = c_char_p(byte_end)
    szPeriod = c_char_p(byte_period)
    pulKey = c_ulong(0)
    nRet = dnadll.DnaGetHistSnap(szPoint, szStart, szEnd, szPeriod, byref(pulKey))
    return _GetNextHist(pulKey, nRet, tag_name)


def SelectPoint():
    """
    Opens an eDNA point picker, where the user can select a single tag.

    :return: selected tag name

    Example:

    >>> tag = SelectPoint()

    """
    pszPoint = create_string_buffer(b"                    ")
    nPoint = c_ushort(20)
    dnadll.DnaSelectPoint(byref(pszPoint), nPoint)
    return pszPoint.value.decode('utf-8')
