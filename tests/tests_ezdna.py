# -*- coding: utf-8 -*-
"""
    pyedna tests_ezdna
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

if __name__ == '__main__':
    unittest.main()
