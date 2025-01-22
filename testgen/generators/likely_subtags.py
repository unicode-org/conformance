# -*- coding: utf-8 -*-
import logging
from generators.base import DataGenerator


class LikelySubtagsGenerator(DataGenerator):
    def process_test_data(self):
        filename = "likelySubtags.txt"
        file_version = "2023-08-17, https://github.com/unicode-org/cldr/pull/3176"
        raw_likely_subtags_data = self.readFile(filename, self.icu_version)
        if not raw_likely_subtags_data:
            return None

        json_test = {
            "test_type": "likely_subtags",
            "source_file": filename,
            "source_version": file_version,
            "tests": [],
        }
        json_verify = {
            "test_type": "likely_subtags",
            "source_file": filename,
            "source_version": file_version,
        }
        json_verify["Test Scenario"] = json_test["Test scenario"] = "likely_subtags"
        # Generate the test and verify json
        testlines = raw_likely_subtags_data.splitlines()
        count = 0
        max_digits = self.computeMaxDigitsForCount(len(testlines))
        test_list = []
        verify_list = []
        for line in testlines:
            # Ignore blank and # comment lineslines()
            if len(line) == 0 or line[0] == "#":
                continue
            # split at ";" and ignore whitespace
            tags = list(map(str.strip, line.split(";")))

            # Flag to indicate exceptional data situation
            just_copy_input = False
            # Remove tests of language codes "reserved for local use"
            # https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Languages/List_of_ISO_639-3_language_codes_used_locally_by_Linguist_List
            lang_code = tags[0].split('-')[0]
            if lang_code >= "qaa" and lang_code <= "qtz":
                just_copy_input = True

            # Normalize to 4 tags: Source; AddLikely; RemoveFavorScript; RemoveFavorRegion
            while len(tags) < 4:
                tags.append("")
            if not tags[2]:
                tags[2] = tags[1]
            if not tags[3]:
                tags[3] = tags[2]

            # Create minimize tests - default is RemoveFavorScript
            source = tags[0]
            if not just_copy_input:
                add_likely = tags[1]
                remove_favor_script = tags[2]
                remove_favor_region = tags[3]
            else:
                # Exceptional situation where output will be same as input
                add_likely = source
                remove_favor_script = source
                remove_favor_region = source

            # And maximize from each tag
            label = str(count).rjust(max_digits, "0")
            test_max = {"label": label, "locale": source, "option": "maximize"}
            verify = {"label": label, "verify": add_likely}
            test_list.append(test_max)
            verify_list.append(verify)
            count += 1

            # Expected minimized form favoring the script
            label = str(count).rjust(max_digits, "0")
            test_min = {"label": label, "locale": source, "option": "minimizeFavorScript"}
            verify = {"label": label, "verify": remove_favor_script}
            test_list.append(test_min)
            verify_list.append(verify)
            count += 1

            # And check for minimizing with favored region is supported
            label = str(count).rjust(max_digits, "0")
            test_favor_region = {
                "label": label,
                "locale": source,
                "option": "minimizeFavorRegion",
            }
            verify = {"label": label, "verify": remove_favor_region}
            test_list.append(test_favor_region)
            verify_list.append(verify)
            count += 1

        # Add to the test and verify json data
        json_test["tests"] = self.sample_tests(test_list)
        json_verify["verifications"] = self.sample_tests(verify_list)

        # Output the files including the json dump
        self.saveJsonFile("likely_subtags_test.json", json_test, 2)
        self.saveJsonFile("likely_subtags_verify.json", json_verify, 2)
        logging.info(
            "Likely Subtags Test (%s): %d lines processed", self.icu_version, count
        )
        return
