# -*- coding: utf-8 -*-
"""
    pyedna.serv
    ~~~~~~~~~~~~~~~
    This module contains functions within the EzDnaServApi, mainly used for
    direct interaction with eDNA services, such as pushing data in real-time.

    :copyright: (c) 2017 Eric Strong.
    :license: Refer to LICENSE.txt for more information.
"""

import os

from ctypes import cdll, byref, create_string_buffer
from ctypes import c_char_p, c_double, c_short, c_ushort, c_long, c_int

# This code should execute at the beginning of the module import, because
# all of the functions in this module require the dna_dll library to be
# loaded. If the file is not in the default location, the user must explicitly
# load it using the LoadDll function.
default_location = "C:\\Program Files (x86)\\eDNA\\EZDnaServApi64.dll"
if os.path.isfile(default_location):
    dnaserv_dll = cdll.LoadLibrary(default_location)
else:
    dnaserv_dll = None


def LoadDll(location):
    """
    If the EZDnaServApi64.dll file is not in the default location
    (C:\Program Files (x86)\eDNA\EZDnaServApi64.dll) then the user must specify
    the correct location of the file, before this module can be used.

    :param location: the full location of EZDnaServApi64.dll, including filename
    """
    global dnaserv_dll
    dnaserv_dll = cdll.LoadLibrary(location)

def AddAnalogShortIdRecord(site_service, tag, time_value, value,
                           low_warn=False, high_warn=False,
                           low_alarm=False, high_alarm=False,
                           oor_low=False, oor_high=False,
                           unreliable=False, manual=False):
    """
    This function will add an analog value to the specified eDNA service and
    tag, with many optional status definitions.

    :param site_service: The site.service where data will be pushed
    :param tag: The eDNA tag to push data. Tag only (e.g. ADE1CA01)
    :param time_value: The time of the point, which MUST be in UTC Epoch
                format. For example, "1483926416" not "2016/01/01 01:01:01".
    :param value: The value associated with the above time.
    :param low_warn: TRUE if the point is in a low warning state
    :param high_warn: TRUE if the point is in a high warning state
    :param low_alarm: TRUE if the point is in a low alarm state
    :param high_alarm: TRUE if the point is in a high alarm state
    :param oor_low: TRUE if the point is out-of-range low
    :param oor_high: TRUE if the point is out-of-range high
    :param unreliable: TRUE if the point is unreliable
    :param manual: TRUE if the point is manually set
    :return: 0, if the data push is successful
    """
    # Define all required variables in the correct ctypes format
    szService = c_char_p(site_service.encode('utf-8'))
    szPointId = c_char_p(tag.encode('utf-8'))
    tTime = c_long(int(time_value))
    dValue = c_double(value)
    bLowWarning = c_int(int(low_warn))
    bHighWarning = c_int(int(high_warn))
    bLowAlarm = c_int(int(low_alarm))
    bHighAlarm = c_int(int(high_alarm))
    bOutOfRangeLow = c_int(int(oor_low))
    bOutOfRangeHigh = c_int(int(oor_high))
    bUnReliable = c_int(int(unreliable))
    bManual = c_int(int(manual))

    # Try to push the data. Function will return 0 if successful.
    nRet = dnaserv_dll.DnaAddAnalogShortIdRecord(szService, szPointId,
                tTime, dValue, bLowWarning, bHighWarning, bLowAlarm,
                bHighAlarm, bOutOfRangeLow, bOutOfRangeHigh, bUnReliable,
                bManual)
    return nRet


def AddAnalogShortIdRecordNoStatus(site_service, tag, time_value, value):
    """
    This function will add an analog value to the specified eDNA service and
    tag, without an associated point status.

    :param site_service: The site.service where data will be pushed
    :param tag: The eDNA tag to push data. Tag only (e.g. ADE1CA01)
    :param time_value: The time of the point, which MUST be in UTC Epoch
                format. For example, "1483926416" not "2016/01/01 01:01:01".
    :param value: The value associated with the above time.
    :return: 0, if the data push is successful
    """
    # Define all required variables in the correct ctypes format
    szService = c_char_p(site_service.encode('utf-8'))
    szPointId = c_char_p(tag.encode('utf-8'))
    tTime = c_long(int(time_value))
    dValue = c_double(value)

    # Try to push the data. Function will return 0 if successful.
    nRet = dnaserv_dll.DnaAddAnalogShortIdRecordNoStatus(szService, szPointId,
                                                         tTime, dValue)
    return nRet


def AddDigitalShortIdRecord(site_service, tag, time_value, value,
                            status_string="OK              ",
                            warn=False, chattering=False,
                            unreliable=False, manual=False):
    """
    This function will add a digital value to the specified eDNA service and
    tag, including all default point status definitions.

    :param site_service: The site.service where data will be pushed
    :param tag: The eDNA tag to push data. Tag only (e.g. ADE1CA01)
    :param time_value: The time of the point, which MUST be in UTC Epoch
                format. For example, "1483926416" not "2016/01/01 01:01:01".
    :param value: should be either TRUE or FALSE
    :param status_string: a string that must be EXACTLY 16 characters
    :param warn: TRUE if the point is in a warning state
    :param chattering: TRUE if the point is in a chattering state
    :param unreliable: TRUE if the point is in an unreliable state
    :param manual: TRUE if the point was manually set
    :return: 0, if the data push is successful
    """
    # Define all required variables in the correct ctypes format
    szService = c_char_p(site_service.encode('utf-8'))
    szPointId = c_char_p(tag.encode('utf-8'))
    tTime = c_long(int(time_value))
    # TODO- check if the string is exactly 16 characters and convert
    szStatus = create_string_buffer(status_string.encode('utf-8'))
    bSet = c_int(int(value))
    bDigitalWarning = c_int(int(warn))
    bDigitalChattering = c_int(int(chattering))
    bUnreliable = c_int(int(unreliable))
    bManual = c_int(int(manual))

    # Try to push the data. Function will return 0 if successful.
    nRet = dnaserv_dll.DnaAddDigitalShortIdRecord(szService, szPointId,
                tTime, bSet, szStatus, bDigitalWarning, bDigitalChattering,
                bUnreliable, bManual)
    return nRet


def AddAnalogShortIdMsecRecord(site_service, tag, time_value, msec, value,
                               low_warn=False, high_warn=False,
                               low_alarm=False, high_alarm=False,
                               oor_low=False, oor_high=False,
                               unreliable=False, manual=False):
    """
    This function will add an analog value to the specified eDNA service and
    tag, with many optional status definitions.

    :param site_service: The site.service where data will be pushed
    :param tag: The eDNA tag to push data. Tag only (e.g. ADE1CA01)
    :param time_value: The time of the point, which MUST be in UTC Epoch
                format. For example, "1483926416" not "2016/01/01 01:01:01".
    :param msec: The additional milliseconds for the time_value
    :param value: The value associated with the above time.
    :param low_warn: TRUE if the point is in a low warning state
    :param high_warn: TRUE if the point is in a high warning state
    :param low_alarm: TRUE if the point is in a low alarm state
    :param high_alarm: TRUE if the point is in a high alarm state
    :param oor_low: TRUE if the point is out-of-range low
    :param oor_high: TRUE if the point is out-of-range high
    :param unreliable: TRUE if the point is unreliable
    :param manual: TRUE if the point is manually set
    :return: 0, if the data push is successful
    """
    # Define all required variables in the correct ctypes format
    szService = c_char_p(site_service.encode('utf-8'))
    szPointId = c_char_p(tag.encode('utf-8'))
    tTime = c_long(int(time_value))
    dValue = c_double(value)
    bLowWarning = c_int(int(low_warn))
    bHighWarning = c_int(int(high_warn))
    bLowAlarm = c_int(int(low_alarm))
    bHighAlarm = c_int(int(high_alarm))
    bOutOfRangeLow = c_int(int(oor_low))
    bOutOfRangeHigh = c_int(int(oor_high))
    bUnReliable = c_int(int(unreliable))
    bManual = c_int(int(manual))
    usMsec = c_ushort(msec)

    # Try to push the data. Function will return 0 if successful.
    nRet = dnaserv_dll.DnaAddAnalogShortIdMsecRecord(szService, szPointId,
                tTime, dValue, bLowWarning, bHighWarning, bLowAlarm,
                bHighAlarm, bOutOfRangeLow, bOutOfRangeHigh, bUnReliable,
                bManual, usMsec)
    return nRet


def AddAnalogShortIdMsecRecordNoStatus(site_service, tag, time_value, msec,
                                       value):
    """
    This function will add an analog value to the specified eDNA service and
    tag, without an associated point status.

    :param site_service: The site.service where data will be pushed
    :param tag: The eDNA tag to push data. Tag only (e.g. ADE1CA01)
    :param time_value: The time of the point, which MUST be in UTC Epoch
                format. For example, "1483926416" not "2016/01/01 01:01:01".
    :param msec: The additional milliseconds for the time_value
    :param value: The value associated with the above time.
    :return: 0, if the data push is successful
    """
    # Define all required variables in the correct ctypes format
    szService = c_char_p(site_service.encode('utf-8'))
    szPointId = c_char_p(tag.encode('utf-8'))
    tTime = c_long(int(time_value))
    dValue = c_double(value)
    usMsec = c_ushort(msec)

    # Try to push the data. Function will return 0 if successful.
    nRet = dnaserv_dll.DnaAddAnalogShortIdMsecRecordNoStatus(szService,
                szPointId, tTime, dValue, usMsec)
    return nRet


def AddDigitalShortIdMsecRecord(site_service, tag, time_value, msec,
                                value, status_string="OK              ",
                                warn=False, chattering=False,
                                unreliable=False, manual=False):
    """
    This function will add a digital value to the specified eDNA service and
    tag, including all default point status definitions.

    :param site_service: The site.service where data will be pushed
    :param tag: The eDNA tag to push data. Tag only (e.g. ADE1CA01)
    :param time_value: The time of the point, which MUST be in UTC Epoch
                format. For example, "1483926416" not "2016/01/01 01:01:01".
    :param msec: The additional milliseconds for the time_value
    :param value: should be either TRUE or FALSE
    :param status_string: a string that must be EXACTLY 16 characters
    :param warn: TRUE if the point is in a warning state
    :param chattering: TRUE if the point is in a chattering state
    :param unreliable: TRUE if the point is in an unreliable state
    :param manual: TRUE if the point was manually set
    :return: 0, if the data push is successful
    """
    # Define all required variables in the correct ctypes format
    szService = c_char_p(site_service.encode('utf-8'))
    szPointId = c_char_p(tag.encode('utf-8'))
    tTime = c_long(int(time_value))
    szStatus = create_string_buffer(status_string.encode('utf-8'))
    bSet = c_int(int(value))
    bDigitalWarning = c_int(int(warn))
    bDigitalChattering = c_int(int(chattering))
    bUnreliable = c_int(int(unreliable))
    bManual = c_int(int(manual))
    usMsec = c_ushort(msec)

    # Try to push the data. Function will return 0 if successful.
    nRet = dnaserv_dll.DnaAddDigitalShortIdMsecRecord(szService, szPointId,
                tTime, bSet, szStatus, bDigitalWarning, bDigitalChattering,
                bUnreliable, bManual, usMsec)
    return nRet


def FlushShortIdRecords(site_service):
    """
    Flush all the queued records.

    :param site_service: The site.service where data was pushed
    :return: message whether function was successful
    """
    # Define all required variables in the correct ctypes format
    szService = c_char_p(site_service.encode('utf-8'))
    szMessage = create_string_buffer(b"                    ")
    nMessage = c_ushort(20)

    # Try to flush the data. Function will return message regarding success.
    nRet = dnaserv_dll.DnaFlushShortIdRecords(szService, byref(szMessage),
                                              nMessage)
    return str(nRet) + szMessage.value.decode('utf-8')


