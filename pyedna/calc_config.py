# -*- coding: utf-8 -*-
"""
    pyedna.calc_config
    ~~~~~~~~~~~~~~~~~~
    This module is meant to parse a calc config file from an eDNA service.

    :copyright: (c) 2017 Eric Strong.
    :license: Refer to LICENSE.txt for more information.
"""

import re
import pandas as pd
from sqlalchemy import create_engine
from sqlite3 import dbapi2 as sqlite


class CalcConfig:
    def __init__(self, filename, site_override=None):
        """
        A class is meant to parse an eDNA CM.DB file that contains
        calculations. The CM.DB file is simply a sqlite database, but the
        'Equation' field inside may contain references to other eDNA tags. It
        is useful to know which tags are associated with which calculations.

        :param filename: the filename of the CM.DB file
        :param site_override: a way to override the 'Site' field of the CB.DB
        """
        sql_file = 'sqlite+pysqlite:///' + filename
        engine = create_engine(sql_file, module=sqlite)
        sql = "SELECT id,site,service,point_id,desc,equation from points;"
        self.config = pd.read_sql(sql, engine)
        self._create_full_tags(site_override)
        self._find_tags_in_calc()

    def _create_full_tags(self, site_override=None):
        # This function will concatenate the Site, Service, and Point_ID fields
        # so that the full site.service.tag is created.
        original_site = self.config['Site'].str.strip()
        site = site_override if site_override else original_site
        service = self.config['Service'].str.strip()
        tag = self.config['Point_ID'].str.strip()
        self.config['FullTag'] = '.'.join([site, service, tag])

    def _find_tags_in_calc(self):
        # This function will find all eDNA tags that are mentioned within the
        # 'Equation' field. eDNA tags are always preceded by dnagetrtvalue(
        # so the function will find all locations for that function.
        search_string = 'dnagetrtvalue\("(.*?)"\)'
        for ii, row in self.config.iterrows():
            equation = row['Equation'].lower()
            results = []
            for tag in re.findall(search_string, equation):
                results.append(tag)
            joined_results = ';'.join(results)
            self.config.ix[ii, 'TagsInCalc'] = joined_results

    def _write_relationships_flat(self, writer):
        # Write relationships in flat form, e.g.
        # ADE1CA01, ADE1PI01, ADE1PI02
        for ii, row in self.config.iterrows():
            calc_tag = row['FullTag'].lower()
            for associated_tag in row['TagsInCalc'].split(';'):
                if associated_tag:
                    writer.write(','.join([calc_tag, associated_tag]) + '\n')

    def _write_relationships_non_flat(self, writer):
        # Write relationships in non-flat form, e.g.
        # ADE1CA01, ADE1PI01
        # ADE1CA01, ADE1PI02
        for ii, row in self.config.iterrows():
            calc_tag = row['FullTag'].lower()
            associated_tag = row['TagsInCalc']
            if associated_tag:
                writer.write(','.join([calc_tag, associated_tag]))

    def get_relationships(self):
        """
        Gets the relationships between calc tags and all associated tags.

        :return: a pandas DataFrame with columns:
                 'FullTag' = calculation tag
                 'TagsInCalc' = the tags that appear in the calculation
        """
        results = self.config[['FullTag', 'TagsInCalc']]
        return results

    def write_relationships(self, file_name, flat=True):
        """
        This module will output the eDNA tags which are used inside each
        calculation.

        If flat=True, data will be written flat, like:
            ADE1CA01, ADE1PI01, ADE1PI02

        If flat=False, data will be written in the non-flat way, like:
            ADE1CA01, ADE1PI01
            ADE1CA01, ADE1PI02

        :param file_name: the output filename to write the relationships,
                          which should include the '.csv' extension
        :param flat: True or False
        """
        with open(file_name, 'w') as writer:
            if flat:
                self._write_relationships_flat(writer)
            else:
                self._write_relationships_non_flat(writer)
