# -*- coding: utf-8 -*-
"""
    pyedna
    ~~~~~
    A set of Python wrappers for functions in the eDNA API.

    :copyright: (c) 2017 by Eric Strong.
    :license: Refer to LICENSE.txt for more information.
"""

__version__ = '0.15'

from .ezdna import DoesIDExist, GetRTFull, GetHistAvg, GetHistInterp, \
                   GetHistMax, GetHistMin, GetHistRaw, GetHistSnap, \
                   SelectPoint, GetPoints, GetServices, LoadDll, \
				   GetTagDescription, GetMultipleTags, SelectPoint \
				   HistAppendValues, HistUpdateInsertValues

from .calc_config import CalcConfig