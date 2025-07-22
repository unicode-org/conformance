# -*- coding: utf-8 -*-
import common

import os
import json
import re
import logging
from generators.base import DataGenerator

class LangNamesGenerator(DataGenerator):
    json_test = {"test_type": "lang_names"}
    json_verify = {"test_type": "lang_names"}


    def process_test_data(self):
        self.languageNameDescr()
        filename = "languageNameTable.txt"
        rawlangnametestdata = self.readFile(filename, self.icu_version)

        if not rawlangnametestdata:
            return None

        # TODO: add standard vs. dialect vs. alternate names
        self.generateLanguageNameTestDataObjects(rawlangnametestdata)
        self.generateTestHashValues(self.json_test)
        output_path = os.path.join(self.icu_version, "lang_name_test_file.json")
        lang_name_test_file = open(output_path, "w", encoding="UTF-8")
        json.dump(self.json_test, lang_name_test_file, indent=1)
        lang_name_test_file.close()

        output_path = os.path.join(self.icu_version, "lang_name_verify_file.json")
        lang_name_verify_file = open(output_path, "w", encoding="UTF-8")
        json.dump(self.json_verify, lang_name_verify_file, indent=1)
        lang_name_verify_file.close()

        return True

    def languageNameDescr(self):
        # Adds information to LanguageName tests and verify JSON
        descr = "Language display name test cases. The first code declares the language whose display name is requested while the second code declares the locale to display the language name in."
        test_id = "lang_names"
        source_url = "No URL yet."
        version = "unspecified"
        self.json_test = {
            "test_type": test_id,
            "Test scenario": test_id,
            "description": descr,
            "source": {
                "repository": "conformance-test",
                "version": "trunk",
                "url": source_url,
                "source_version": version,
            },
        }
        return

    def generateLanguageNameTestDataObjects(self, rawtestdata):
        # Get the JSON data for tests and verification for language names
        count = 0

        jtests = []
        jverify = []

        # Compute max size needed for label number
        test_lines = rawtestdata.splitlines()
        num_samples = len(test_lines)
        max_digits = self.computeMaxDigitsForCount(num_samples)
        for item in test_lines:
            if not (common.RE_COMMENT_LINE.match(item) or common.RE_BLANK_LINE.match(item)):
                test_data = self.parseLanguageNameData(item)
                if test_data == None:
                    logging.debug(
                        "  LanguageNames (%s): Line '%s' not recognized as valid test data entry",
                        self.icu_version,
                        item,
                    )
                    continue
                else:
                    label = str(count).rjust(max_digits, "0")
                    test_json = {
                        "label": label,
                        "language_label": test_data[0],
                        "locale_label": test_data[1],
                    }
                    jtests.append(test_json)
                    jverify.append({"label": label, "verify": test_data[2]})
                    count += 1

        self.json_test["tests"] = self.sample_tests(jtests)
        self.json_verify["verifications"] = self.sample_tests(jverify)

        logging.info("LangNames Test (%s): %d lines processed", self.icu_version, count)
        return

    def parseLanguageNameData(self, rawtestdata):
        reformat = re.compile(r"(\w*);(\w*);(.*)")

        test_match = reformat.search(rawtestdata)

        if test_match != None:
            return (test_match.group(1), test_match.group(2), test_match.group(3))
        else:
            return None
