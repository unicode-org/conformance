# -*- coding: utf-8 -*-
import os
import json
import re
import logging
from generators.base import DataGenerator

RE_BLANK_LINE = re.compile(r"^\s*$")
RE_COMMENT_LINE = re.compile(r"^\s*#")

class LocaleNamesGenerator(DataGenerator):
    json_test = {"test_type": "lang_names"}
    json_verify = {"test_type": "lang_names"}


    def process_test_data(self):
        self.languageNameDescr()
        # Data constructed from CLDR data
        filename = "localeDisplayName.txt"
        raw_locale_display_names_testdata = self.readFile(filename, self.icu_version)

        if not raw_locale_display_names_testdata:
            # File may not exist
            return None

        # TODO: add standard vs. dialect vs. alternate names
        self.generateLanguageNameTestDataObjects(raw_locale_display_names_testdata)
        self.generateTestHashValues(self.json_test)
        output_path = os.path.join(self.icu_version, "lang_names_test_file.json")
        lang_names_test_file = open(output_path, "w", encoding="UTF-8")
        json.dump(self.json_test, lang_names_test_file, indent=1)
        lang_names_test_file.close()

        output_path = os.path.join(self.icu_version, "lang_names_verify_file.json")
        lang_names_verify_file = open(output_path, "w", encoding="UTF-8")
        json.dump(self.json_verify, lang_names_verify_file, indent=1)
        lang_names_verify_file.close()

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
        set_locale = re.compile(r"@locale=(\w+)")
        set_languageDisplay = re.compile(r"@languageDisplay=(\w+)")

        count = 0

        jtests = []
        jverify = []

        # Compute max size needed for label number
        test_lines = rawtestdata.splitlines()
        num_samples = len(test_lines)
        max_digits = self.computeMaxDigitsForCount(num_samples)

        language_label = 'und'
        language_display = 'standard'

        for item in test_lines:
            if not (RE_COMMENT_LINE.match(item) or RE_BLANK_LINE.match(item)):

                locale_match = set_locale.match(item)
                if locale_match:
                    locale_label = locale_match.group(1)
                    continue

                language_display_match = set_languageDisplay.match(item)
                if language_display_match:
                    language_display = language_display_match.group(1)
                    continue

                test_data = self.parseLanguageNameData(item)
                if test_data == None:
                    logging.debug(
                        "  LanguageNames (%s): Line '%s' not recognized as valid test data entry",
                        self.icu_version,
                        item,
                    )
                    continue
                else:
                    # Ignore the root locale
                    if locale_label == 'root':
                        logging.debug('testgen/generator/localeDisplayNames: %s ignored for %s, %s',
                                     locale_label, test_data[0], language_display)
                        continue
                    label = str(count).rjust(max_digits, "0")
                    test_json = {
                        "label": label,
                        "language_label": test_data[0],
                        "locale_label": locale_label,
                        "languageDisplay": language_display
                    }
                    jtests.append(test_json)
                    jverify.append({"label": label, "verify": test_data[1]})
                    count += 1

        self.json_test["tests"] = self.sample_tests(jtests)
        self.json_verify["verifications"] = self.sample_tests(jverify)

        logging.info("LocaleDisplayNames Test (%s): %d lines processed", self.icu_version, count)
        return

    def parseLanguageNameData(self, rawtestdata):
        reformat = re.compile(r"(\w+(\-\w+)*);\s*(.+)$")

        test_match = reformat.search(rawtestdata)

        if test_match != None:
            return (test_match.group(1), test_match.group(3))
        else:
            return None
