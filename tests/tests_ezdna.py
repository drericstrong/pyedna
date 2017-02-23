# -*- coding: utf-8 -*-
"""
    pyedna tests
    ~~~~~~~~~~~~~~~
    A set of unit tests for pyedna.

    :copyright: (c) 2017 Eric Strong.
    :license: Refer to LICENSE.txt for more information.
"""

import unittest
import numpy as np
import pyedna.ezdna as dna

# These tests are mainly related to helper functions or I/O. ASSUME Windows
# file/folder formatting, since eDNA is built for Windows.
class TestMiscMethods(unittest.TestCase):
    def test_format_badCharacters(self):
        orig_string = "??R°e$M%o#V@e!:-¶!?©* &._t()H,i][s/"
        test_string = dna._format_str(orig_string)
        good_string = "ReMoVe:- ._tHis/"
        self.assertEqual(test_string, good_string)

    def test_loadDll_missingFolder(self):
        bad_folder = "C:\\thisfolderdoesnotexistatleastihopeso\\EzDnaApi64.dll"
        with self.assertRaises(Exception):
            dna.LoadDll(bad_folder)

    def test_loadDll_missingFile(self):
        bad_file = "C:\\EzDnaApi64_thewrongone.dll"
        with self.assertRaises(Exception):
            dna.LoadDll(bad_file)

    def test_loadDll_goodFile(self):
        good_file = "C:\\Program Files (x86)\\eDNA\\EzDnaApi64.dll"
        dna.LoadDll(good_file)

    def test_doesIDExist_no(self):
        tag_name = "GIBBERISH.DOESNOT1.EXIST123"
        check_bool = dna.DoesIDExist(tag_name)
        self.assertFalse(check_bool)

    def test_doesIDExist_yes(self):
        tag_name = "MDSSCSC1.ANVCALC.ADE1CA02"
        check_bool = dna.DoesIDExist(tag_name)
        self.assertTrue(check_bool)

    def test_getLabel_notExists(self):
        tag_name = "GIBBERISH.DOESNOT1.EXIST123"
        test_desc = dna._GetLabel(tag_name)
        self.assertEqual(tag_name, test_desc)

    def test_getLabel_exists(self):
        tag_name = "MDSSCSC1.ANVCALC.ADE1CA02"
        test_desc = dna._GetLabel(tag_name)
        good_desc = "ADE1 Percent Load"
        self.assertEqual(test_desc, good_desc)

    def test_getTagDescription_notExists(self):
        tag_name = "GIBBERISH.DOESNOT1.EXIST123"
        test_desc = dna.GetTagDescription(tag_name)
        self.assertIsNone(test_desc)

    def test_getTagDescription_exists(self):
        tag_name = "MDSSCSC1.ANVCALC.ADE1CA02"
        test_desc = dna.GetTagDescription(tag_name)
        good_desc = "ADE1 Percent Load"
        self.assertEqual(test_desc, good_desc)

# WARNING- These tests currently require connection to a private test server.
# I do have plans to create instructions for creating your own test server,
# and ensuring that these tests match that test server, but that is future.
class TestServicePointMethods(unittest.TestCase):
    def test_getServices_retrieval(self):
        services = dna.GetServices()
        df = services[services.Name == "ANTARES.ANVCALC"]
        self.assertEqual(df.Description.values[0], "Calculation Service")
        self.assertEqual(df.Type.values[0], "SSERVER")

    def test_getPoints_retrieval(self):
        points = dna.GetPoints("MDSSCSC1.ANVCALC")
        df = points[points.Tag == "MDSSCSC1.ANVCALC.ADE1CA02"]
        self.assertEqual(df.Description.values[0], "ADE1 Percent Load")
        self.assertEqual(df.Units.values[0], "Load")

    def test_getRTFull_exists(self):
        info = dna.GetRTFull("MDSSCSC1.ANVCALC.ADE1CA02")
        self.assertIsNotNone(info)

    def test_getRTFull_notExists(self):
        info = dna.GetRTFull("GIBBERISH.DOESNOT1.EXIST123")
        self.assertIsNone(info)

class TestPullMethods(unittest.TestCase):
    def test_getHistRaw_badTag(self):
        tag_name = "GIBBERISH.DOESNOT1.EXIST123"
        start_time = "01/02/17 01:58"
        end_time = "01/02/17 02:00"
        df = dna.GetHistRaw(tag_name, start_time, end_time)
        self.assertTrue(df.empty)

    def test_getHistRaw_goodTag(self):
        tag_name = "MDSSCSC1.ANVCALC.ADE1CA02"
        start_time = "01/09/17 02:00:00"
        end_time = "01/09/17 02:00:30"
        exp_val = np.array([74.3, 71.3, 70.7, 72.2, 72.2])
        df = dna.GetHistRaw(tag_name, start_time, end_time)
        test_val = df["MDSSCSC1.ANVCALC.ADE1CA02"].values
        self.assertEqual(exp_val.all(), test_val.all())

    def test_getHistRaw_descAsLabel(self):
        tag_name = "MDSSCSC1.ANVCALC.ADE1CA02"
        start_time = "01/09/17 02:00:00"
        end_time = "01/09/17 02:00:30"
        df = dna.GetHistRaw(tag_name, start_time, end_time, desc_as_label=True)
        good_val = ['ADE1 Percent Load', 'ADE1 Percent Load Status']
        test_val = list(df.columns.values)
        self.assertEqual(good_val, test_val)

    def test_getHistRaw_label(self):
        tag_name = "MDSSCSC1.ANVCALC.ADE1CA02"
        start_time = "01/09/17 02:00:00"
        end_time = "01/09/17 02:00:30"
        df = dna.GetHistRaw(tag_name, start_time, end_time, label="NEW")
        good_val = ['NEW', 'NEW Status']
        test_val = list(df.columns.values)
        self.assertEqual(good_val, test_val)

    def test_getMultiple_allBadTags(self):
        tags = ["GIBBERISH.DOESNOT1.EXIST123", "GIBBERISH.DOESNOT1.EXIST125"]
        start_time = "01/02/17 01:58"
        end_time = "01/02/17 02:00"
        df = dna.GetMultipleTags(tags, start_time, end_time)
        self.assertTrue(df.empty)

    def test_getMultiple_oneBadTag(self):
        tags = ["GIBBERISH.DOESNOT1.EXIST123", "MDSSCSC1.ANVCALC.ADE1CA02"]
        start_time = "01/02/17 01:58"
        end_time = "01/02/17 02:00"
        df = dna.GetMultipleTags(tags, start_time, end_time)
        self.assertFalse(df.empty)

    def test_getMultiple_goodTags(self):
        tags = ["MDSSCSC1.ANVCALC.ADE1CA02", "MDSSCSC1.ANVCALC.ADE1CA03"]
        start_time = "01/09/17 02:00:00"
        end_time = "01/09/17 02:00:30"
        df = dna.GetMultipleTags(tags, start_time, end_time)
        vals1 = np.array([74.3, 71.3, 70.7, 72.2, 72.2])
        vals2 = np.array([420, 419, 413, 415])
        test_val1 = df["MDSSCSC1.ANVCALC.ADE1CA02"].values
        test_val2 = df["MDSSCSC1.ANVCALC.ADE1CA03"].values
        self.assertEqual(vals1.all(), test_val1.all())
        self.assertEqual(vals2.all(), test_val2.all())

    def test_getMultiple_goodTags_resample(self):
        tags = ["MDSSCSC1.ANVCALC.ADE1CA02", "MDSSCSC1.ANVCALC.ADE1CA03"]
        start_time = "01/09/17 02:00:00"
        end_time = "01/09/17 02:00:30"
        df = dna.GetMultipleTags(tags, start_time, end_time, sampling_rate=5)
        vals1 = np.array([74.3, 74.3, 71.3, 71.3, 70.7, 70.7, 72.2])
        vals2 = np.array([420, 420, 419, 419, 413, 413, 415])
        test_val1 = df["MDSSCSC1.ANVCALC.ADE1CA02"].values
        test_val2 = df["MDSSCSC1.ANVCALC.ADE1CA03"].values
        self.assertEqual(vals1.all(), test_val1.all())
        self.assertEqual(vals2.all(), test_val2.all())

    def test_getMultiple_descAsLabel(self):
        tags = ["MDSSCSC1.ANVCALC.ADE1CA02", "MDSSCSC1.ANVCALC.ADE1CA03"]
        start_time = "01/09/17 02:00:00"
        end_time = "01/09/17 02:00:30"
        df = dna.GetMultipleTags(tags, start_time, end_time,
                                 desc_as_label=True)
        good_columns = ["ADE1 Percent Load", "ADE1 Max EGT"]
        test_columns = list(df.columns.values)
        self.assertEqual(test_columns, good_columns)

if __name__ == '__main__':
    unittest.main()
