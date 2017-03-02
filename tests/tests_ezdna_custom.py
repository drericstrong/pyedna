# -*- coding: utf-8 -*-
"""
    pyedna tests_ezdna_custom
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    A set of unit tests for pyedna. Currently, these tests will only work
    on a private test server.

    :copyright: (c) 2017 Eric Strong.
    :license: Refer to LICENSE.txt for more information.
"""

import unittest
import numpy as np
import pyedna.ezdna as dna


# WARNING- These tests currently require connection to a private test server.
# I do have plans to create instructions for creating your own test server,
# and ensuring that these tests match that test server, but that is future.
class TestServicePointMethods(unittest.TestCase):
    def test_getServices_retrieval(self):
        services = dna.GetServices()
        df = services[services.Name == "ANTARES.ANVCALC"]
        self.assertEqual(df.Description.values[0], "Calculation Service")
        self.assertEqual(df.Type.values[0], "SSERVER")

    def test_getServices_firstSecondPoint(self):
        services = dna.GetServices()
        first_serv = services.Name[0]
        good_serv = "ANTARES.ANVCALC"
        self.assertEqual(first_serv, good_serv)
        second_serv = services.Name[1]
        good_serv2 = "ANTARES.ANVDD"
        self.assertEqual(second_serv, good_serv2)

    def test_getPoints_retrieval(self):
        points = dna.GetPoints("MDSSCSC1.ANVCALC")
        df = points[points.Tag == "MDSSCSC1.ANVCALC.ADE1CA02"]
        self.assertEqual(df.Description.values[0], "ADE1 Percent Load")
        self.assertEqual(df.Units.values[0], "Load")

    def test_getPoints_firstSecondPoint(self):
        points = dna.GetPoints("MDSSCSC1.ANVCALC")
        first_tag = points.Tag[0]
        good_tag = "MDSSCSC1.ANVCALC._INPADDR"
        self.assertEqual(first_tag, good_tag)
        second_tag = points.Tag[1]
        good_tag2 = "MDSSCSC1.ANVCALC.ADE1CA01"
        self.assertEqual(second_tag, good_tag2)

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

    def test_getHist_badTag(self):
        tag_name = "GIBBERISH.DOESNOT1.EXIST123"
        start_time = "01/02/17 01:58"
        end_time = "01/02/17 02:00"
        df = dna.GetHist(tag_name, start_time, end_time)
        self.assertTrue(df.empty)

    def test_getHist_goodTag(self):
        tag_name = "MDSSCSC1.ANVCALC.ADE1CA02"
        start_time = "01/09/17 02:00:00"
        end_time = "01/09/17 02:00:30"
        exp_val = np.array([74.3, 71.3, 70.7, 72.2, 72.2])
        df = dna.GetHist(tag_name, start_time, end_time)
        test_val = df["MDSSCSC1.ANVCALC.ADE1CA02"].values
        self.assertEqual(exp_val.all(), test_val.all())

    def test_getHist_descAsLabel(self):
        tag_name = "MDSSCSC1.ANVCALC.ADE1CA02"
        start_time = "01/09/17 02:00:00"
        end_time = "01/09/17 02:00:30"
        df = dna.GetHist(tag_name, start_time, end_time, desc_as_label=True)
        good_val = ['ADE1 Percent Load', 'ADE1 Percent Load Status']
        test_val = list(df.columns.values)
        self.assertEqual(good_val, test_val)

    def test_getHist_label(self):
        tag_name = "MDSSCSC1.ANVCALC.ADE1CA02"
        start_time = "01/09/17 02:00:00"
        end_time = "01/09/17 02:00:30"
        df = dna.GetHist(tag_name, start_time, end_time, label="NEW")
        good_val = ['NEW', 'NEW Status']
        test_val = list(df.columns.values)
        self.assertEqual(good_val, test_val)

    def test_getHistHS_goodTag(self):
        tag_name = "MDSSCSC1.ANVDD.ADE1C1PA"
        start_time = "01/23/17"
        end_time = "01/24/17"
        df = dna.GetHist(tag_name, start_time, end_time, high_speed=True)
        good_val = np.array([0, 0, 1, -1, 1, 721])
        test_val = df["MDSSCSC1.ANVDD.ADE1C1PA"].values[0:6]
        self.assertEqual(good_val.all(), test_val.all())

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
