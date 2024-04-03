# -*- coding: utf-8 -*-
import os
import json
import re
import logging
import subprocess
import xml.etree.ElementTree as ET

from generators.base import DataGenerator

reblankline = re.compile("^\s*$")

class PluralGenerator(DataGenerator):
    def plurals_descriptor(self):
        # Create test list of all these
        self.test_id = 'plural_rules'
        self.categories = ['zero', 'one', 'two', 'few', 'many', 'other']

        source_url = ['https://github.com/unicode-org/cldr/blob/main/common/supplemental/plurals.xml',
                      'https://github.com/unicode-org/cldr/blob/main/common/supplemental/ordinals.xml'
                      ]

        version = '1'  #  What is this value?

        self.json_test = {
            "test_type": self.test_id,
            "Test scenario": self.test_id,
            "description": 'Plural rules tests',
            "source": {
                "repository": "conformance-test",
                "version": "trunk",
                "url": source_url,
                "source_version": version
            },
            "tests": []
        }

        self.json_verify = {
            "test_type": self.test_id,
            "verifications": []
        }

    def process_test_data(self):
        # Set up the neede values in lieu of __init__
        self.plurals_descriptor()

        result = True  # TODO: Set to False if there's an error.

        test_cardinal, verifications_cardinal = self.process_cardinal_plurals()
        if test_cardinal:
            self.json_test["tests"].extend(test_cardinal)
        if verifications_cardinal:
            self.json_verify["verifications"].extend(verifications_cardinal)

        test_ordinal, verifications_ordinal = self.process_ordinal_plurals()
        if test_ordinal:
            self.json_test["tests"].extend(test_ordinal)
        if verifications_ordinal:
           self.json_verify["verifications"].extend(verifications_ordinal)

        tests_range, verifications_range = self.process_plural_range_file()
        if tests_range:
            self.json_test["tests"].extend(tests_range)
        if verifications_range:
            self.json_verify["verifications"].extend(verifications_range)

        # And save the results
        self.saveJsonFile("plural_rules_test.json", self.json_test, 2)
        self.saveJsonFile("plural_rules_verify.json", self.json_verify)

        return result
    def process_cardinal_plurals(self):
        filename = self.icu_version + '/plurals.xml'

        return self.process_xml_file(filename, 'cardinal')

    def process_ordinal_plurals(self):
        filename = self.icu_version + '/ordinals.xml'

        return self.process_xml_file(filename, 'ordinal')

    def process_xml_file(self, filename, num_type):
        tests = []
        verifications= []

        label_num = 0

        # TODO: Check if file exists
        try:
            tree = ET.parse(filename)
        except:
            logging.info('No plurals file found: %s', filename)
            return None, None

        root = tree.getroot()

        # For each pluralRules
        # For each locale in locales
        # for each case in @integer and @decimal

        for plural_rule in root.iter('pluralRules'):
            locales = plural_rule.attrib['locales']

            # TODO: break locales into tags
            tags = locales.split()

            for rule in plural_rule.iter('pluralRule'):
                count = rule.get('count')
                text = rule.text

                samples = self.text_to_samples(text)

                # For locale, for sample, expect count
                # Parse this text to get samples
                for locale in tags:
                    for sample in samples:
                        test = {
                            'locale': locale,
                            'label': str(label_num),
                            'type': num_type,
                            'sample': sample
                        }
                        verify_item = {
                            'label': str(label_num),
                            'verify': count
                        }
                        tests.append(test)
                        verifications.append(verify_item)
                        label_num += 1

        return tests, verifications

    def text_to_samples(self, text):
        # TODO!!! Get text string to samples, applying rules =, !=, mod, .., ~
        # n, i, v, f, t, w

        # FIrst try: get the numbers following "@"
        pos_at = text.find("@")
        text_after_at = text
        if pos_at >= 0:
            text_after_at = text[pos_at:]
        samples = re.findall(r'(\d+\.?\d*)',  text_after_at)

        return samples
    def process_plural_range_file(self):
        filename = self.icu_version + '/plurals.xml'

        # TODO: Implement this

        tests = []
        verifications = []
        return tests, verifications
