# -*- coding: utf-8 -*-
import os
import json
import logging
import re
from generators.base import DataGenerator

reblankline = re.compile("^\s*$")

# Global constants
# Values to be formatted in number format tests
NUMBERS_TO_TEST = ["0", "91827.3645", "-0.22222"]

# Which locales are selected for this testing.
# This selects es-MX, zh-TW, bn-BD
NUMBERFORMAT_LOCALE_INDICES = [3, 7, 11]


class NumberFmtGenerator(DataGenerator):
    def process_test_data(self):
        filename = "dcfmtest.txt"
        rawdcmlfmttestdata = self.readFile(filename, self.icu_version)
        if rawdcmlfmttestdata:
            BOM = "\xef\xbb\xbf"
            if rawdcmlfmttestdata.startswith(BOM):
                rawdcmlfmttestdata = rawdcmlfmttestdata[3:]

        filename = "numberpermutationtest.txt"
        rawnumfmttestdata = self.readFile(filename, self.icu_version)
        if rawnumfmttestdata:
            num_testdata_object_list, num_verify_object_list, count = (
                self.generateNumberFmtTestDataObjects(rawnumfmttestdata)
            )
            if rawdcmlfmttestdata:
                dcml_testdata_object_list, dcml_verify_object_list, count = (
                    self.generateDcmlFmtTestDataObjects(rawdcmlfmttestdata, count)
                )

            test_list = num_testdata_object_list + dcml_testdata_object_list
            verify_list = num_verify_object_list + dcml_verify_object_list
            json_test, json_verify = self.insertNumberFmtDescr(test_list, verify_list)

            json_test["tests"] = self.sample_tests(json_test["tests"])
            json_verify["verifications"] = self.sample_tests(
                json_verify["verifications"]
            )

            self.saveJsonFile("num_fmt_test_file.json", json_test)

            output_path = os.path.join(self.icu_version, "num_fmt_verify_file.json")
            # TODO: Change these saves to use saveJsonFile with output_path ??
            num_fmt_verify_file = open(output_path, "w", encoding="UTF-8")
            json.dump(json_verify, num_fmt_verify_file, indent=1)
            num_fmt_verify_file.close()

            logging.info(
                "NumberFormat Test (%s): %s tests created", self.icu_version, count
            )
        return

    def generateNumberFmtTestDataObjects(self, rawtestdata, count=0):
        # Returns 2 lists JSON-formatted: all_tests_list, verify_list
        original_count = count
        entry_types = {
            "compact-short": "notation",
            "scientific/+ee/sign-always": "notation",
            "percent": "unit",
            "currency/EUR": "unit",  ## TODO: Change the unit
            "measure-unit/length-meter": "unit",
            "measure-unit/length-furlong": "unit",
            "unit-width-narrow": "unit-width",
            "unit-width-full-name": "unit-width",
            "precision-integer": "precision",
            ".000": "precision",
            ".##/@@@+": "precision",
            "@@": "precision",
            "rounding-mode-floor": "rounding-mode",
            "integer-width/##00": "integer-width",
            "scale/0.5": "scale",
            "group-on-aligned": "grouping",
            "latin": "symbols",
            "sign-accounting-except-zero": "sign-display",
            "decimal-always": "decimal-separator-display",
        }
        test_list = self.parseNumberFmtTestData(rawtestdata)
        ecma402_options_start = ['"options": {\n']

        all_tests_list = []
        verify_list = []

        expected_count = (
            len(test_list) * len(NUMBERFORMAT_LOCALE_INDICES) * len(NUMBERS_TO_TEST)
            + count
        )
        max_digits = self.computeMaxDigitsForCount(expected_count)

        for test_options in test_list:
            # The first three specify the formatting.
            # Example: compact-short percent unit-width-full-name
            part1 = entry_types[test_options[0]]
            part2 = entry_types[test_options[1]]
            part3 = entry_types[test_options[2]]

            # TODO: use combinations of part1, part2, and part3 to generate options.
            # Locales are in element 3, 7, and 11 of parsed structure.

            for locale_idx in NUMBERFORMAT_LOCALE_INDICES:
                for number_idx in range(len(NUMBERS_TO_TEST)):
                    ecma402_options = []
                    label = str(count).rjust(max_digits, "0")
                    expected = test_options[locale_idx + 1 + number_idx]
                    verify_json = {"label": label, "verify": expected}
                    verify_list.append(verify_json)

                    # TODO: Use JSON module instead of print formatting
                    skeleton = "%s %s %s" % (
                        test_options[0],
                        test_options[1],
                        test_options[2],
                    )
                    entry = {
                        "label": label,
                        "locale": test_options[locale_idx],
                        "skeleton": skeleton,
                        "input": NUMBERS_TO_TEST[number_idx],
                    }

                    try:
                        options_dict = self.mapFmtSkeletonToECMA402(
                            [test_options[0], test_options[1], test_options[2]]
                        )
                    except KeyError as error:
                        logging.warning(
                            "Looking up Skeletons: %s [0-2] = %s, %s %s",
                            error,
                            test_options[0],
                            test_options[1],
                            test_options[2],
                        )
                    if not options_dict:
                        logging.warning("$$$ OPTIONS not found for %s", label)
                    # TODO: Look at the items in the options_dict to resolve conflicts and set up things better.
                    resolved_options_dict = self.resolveOptions(
                        options_dict, test_options
                    )
                    # include these options in the entry
                    entry = entry | {"options": resolved_options_dict}

                    all_tests_list.append(entry)  # All the tests in JSON form
                    count += 1
        logging.info(
            "  generateNumberFmtTestDataObjects gives %d tests",
            (count - original_count),
        )
        return all_tests_list, verify_list, count

    def parseNumberFmtTestData(self, rawtestdata):
        renumformat = re.compile(
            r"([\w/@\+\-\#\.]+) ([\w/@\+\-\#\.]+) ([\w/@\+\-\#\.]+)\n\s*(\w\w\-\w\w)\n\s*(.*?)\n\s*(.*?)\n\s*(.*?)\n\s*(\w\w\-\w\w)\n\s*(.*?)\n\s*(.*?)\n\s*(.*?)\n\s*(\w\w\-\w\w)\n\s*(.*?)\n\s*(.*?)\n\s*(.*?)\n"
        )

        return renumformat.findall(rawtestdata)

    # Count is the starting point for the values
    # Use older Decimal Format specifications
    # Source data: https://github.com/unicode-org/icu/blob/main/icu4c/source/test/testdata/dcfmtest.txt
    def generateDcmlFmtTestDataObjects(self, rawtestdata, count=0):
        original_count = count
        recommentline = re.compile("^\s*#")
        test_list = rawtestdata.splitlines()

        all_tests_list = []
        verify_list = []

        # Transforming patterns to skeltons
        pattern_to_skeleton = {
            "0.0000E0": "scientific .0000",
            "0.000E0": "scientific .000",
            "0.00E0": "scientific .00",
            "0.0##E0": "scientific .0##",  # ??
            "00.##E0": "scientific .##",  # ??
            "0.#E0": "scientific .0",  # ??
            "0.##E0": "scientific .00",  # ???
            ".0E0": "scientific .0",  # ??
            ".0#E0": "scientific .0#",  # ??
            ".0##E0": "scientific .0##",  # ??
            "00": "integer-width/##00 precision-integer group-off",
            "0.0": ".0",
            '0.00': '.00',
            '0.0##': '.0##',
            '0.00##': '.00##',
            "@@@": "@@@ group-off",
            "@@###": "@@### group-off",
            "#": "precision-integer group-off",
            "#.#": ".# group-off",
            "@@@@E0": "scientific/+e @@@@",
            "0.0##@E0": "scientific/+e .##/@@+",
            "0005": "integer-width/0000 precision-increment/0005 group-off",
            "@@@@@@@@@@@@@@@@@@@@@@@@@": "@@@@@@@@@@@@@@@@@@@@@@@@@ group-off"
        }

        expected = len(test_list) + count
        max_digits = self.computeMaxDigitsForCount(expected)

        for item in test_list[1:]:
            if not (recommentline.match(item) or reblankline.match(item)):
                # Ignore parse for now.
                if item == "" or item[0:5] == "parse":
                    continue

                pattern, round_mode, test_input, expected = self.parseDcmlFmtTestData(
                    item
                )
                if pattern == None:
                    continue

                label = str(count).rjust(max_digits, "0")

                # TODO!!: Look up the patterns to make skeletons
                if pattern in pattern_to_skeleton:
                    skeleton = pattern_to_skeleton[pattern]
                    if round_mode:
                        skeleton += ' ' + self.mapRoundingToSkeleton(round_mode)
                else:
                    logging.error('Pattern %s not converted to skelection', pattern)
                    skeleton = None

                if skeleton:
                    entry = {
                        "label": label,
                        "op": "format",
                        "pattern": pattern,
                        "skeleton": skeleton,
                        "input": test_input,
                        "options": {},
                    }
                else:
                    # Unknown skeleton
                    entry = {
                        "label": label,
                        "op": "format",
                        "pattern": pattern,
                        "input": test_input,
                        "options": {},
                    }

                json_part = self.mapFmtSkeletonToECMA402([pattern])

                resolved_options_dict = self.resolveOptions(json_part, None)
                # None of these old patterns use groupings
                resolved_options_dict["useGrouping"] = False

                if round_mode:
                    ecma_rounding_mode = self.mapRoundingToECMA402(round_mode)
                    entry["options"]["roundingMode"] = ecma_rounding_mode
                else:
                    # Default if not specified
                    entry["options"]["roundingMode"] = self.mapRoundingToECMA402(
                        "halfeven"
                    )

                entry["options"] |= resolved_options_dict  # ??? json_part

                all_tests_list.append(entry)
                verify_list.append({"label": label, "verify": expected})
                count += 1

        logging.info(
            "  generateDcmlFmtTestDataObjects gives %d tests", (count - original_count)
        )
        return all_tests_list, verify_list, count

    def parseDcmlFmtTestData(self, rawtestdata):
        reformat = re.compile(
            r"format +([\d.E@\#]+) +(default|ceiling|floor|down|up|halfeven|halfdown|halfup|halfodd|halfceiling|halffloor|unnecessary) +\"(-?[\d.E]+)\" +\"(-?[\d.E]+|Inexact)\""
        )
        # TODO: ignore 'parse' line
        try:
            test_match = reformat.search(rawtestdata)
        except AttributeError as error:
            logging.warning("** parseDcmlFmtTestData: %s", error)
        if not test_match:
            logging.warning("No test match with rawtestdata = %s", rawtestdata)
            return None, None, None, None
        return (
            test_match.group(1),
            test_match.group(2),
            test_match.group(3),
            test_match.group(4),
        )

    def mapFmtSkeletonToECMA402(self, options):
        ecma402_map = {
            "compact-short": {"notation": "compact", "compactDisplay": "short"},
            "scientific/+ee/sign-always": {
                "notation": "scientific",
                "conformanceExponent": "+ee",
                "conformanceSign": "always",
            },
            # Percent with word "percent":
            "percent": {"style": "unit", "unit": "percent"},  # "style": "percent",
            "currency/EUR": {
                "style": "currency",
                "currencyDisplay": "symbol",
                "currency": "EUR",
            },
            "measure-unit/length-meter": {"style": "unit", "unit": "meter"},
            "measure-unit/length-furlong": {"style": "unit", "unit": "furlong"},
            "unit-width-narrow": {
                "unitDisplay": "narrow",
                "currencyDisplay": "narrowSymbol",
            },
            "unit-width-full-name": {"unitDisplay": "long", "currencyDisplay": "name"},
            # "unit-width-full-name": {"unitDisplay": "long"},
            "precision-integer": {
                "maximumFractionDigits": 0,
                "minimumFractionDigits": 0,
                "roundingType": "fractionDigits",
            },
            ".000": {"maximumFractionDigits": 3, "minimumFractionDigits": 3},
            # Use maximumFractionDigits: 2, maximumSignificantDigits: 3, roundingPriority: "morePrecision"
            ".##/@@@+": {
                "maximumFractionDigits": 2,
                "maximumSignificantDigits": 3,
                "roundingPriority": "morePrecision",
            },
            "@@": {"maximumSignificantDigits": 2, "minimumSignificantDigits": 2},
            "rounding-mode-floor": {"roundingMode": "floor"},
            "integer-width/##00": {
                "maximumIntegerDigits": 4,
                "minimumIntegerDigits": 2,
            },
            "group-on-aligned": {"useGrouping": True},
            "latin": {"numberingSystem": "latn"},
            "sign-accounting-except-zero": {
                "signDisplay": "exceptZero",
                "currencySign": "accounting",
            },
            # These are all patterns...
            "0.0000E0": {
                "notation": "scientific",
                "minimumIntegerDigits": 1,
                "minimumFractionDigits": 4,
                "maximumFractionDigits": 4,
            },
            "00": {"minimumIntegerDigits": 2, "maximumFractionDigits": 0},
            "#.#": {"maximumFractionDigits": 1},
            "@@@": {"minimumSignificantDigits": 3, "maximumSignificantDigits": 3},
            "@@###": {"minimumSignificantDigits": 2, "maximumSignificantDigits": 5},
            "@@@@E0": {
                "notation": "scientific",
                "minimumSignificantDigits": 4,
                "maximumSignificantDigits": 4,
            },
            "0.0##E0": {
                "notation": "scientific",
                "minimumIntegerDigits": 1,
                "minimumFractionDigits": 1,
                "maximumFractionDigits": 3,
            },
            "00.##E0": {
                "notation": "scientific",
                "minimumIntegerDigits": 2,
                "minimumFractionDigits": 1,
                "maximumFractionDigits": 3,
            },
            "0005": {
                "minimumIntegerDigits": 4,
                "roundingIncrement": 5,
                "maximumFractionDigits": 0,
                "roundingPriority": "auto",
                "roundingIncrement": 5},
            "0.00": {
                "minimumIntegerDigits": 1,
                "minimumFractionDigits": 2,
                "maximumFractionDigits": 2,
            },
            "0.000E0": {
                "notation": "scientific",
                "minimumIntegerDigits": 1,
                "minimumFractionDigits": 3,
                "maximumFractionDigits": 3,
            },
            "0.0##": {
                "minimumIntegerDigits": 1,
                "minimumFractionDigits": 1,
                "maximumFractionDigits": 3,
            },
            "#": {"minimumIntegerDigits": 1, "maximumFractionDigits": 0},
            "0.#E0": {
                "notation": "scientific",
                "minimumIntegerDigits": 1,
                "maximumFractionDigits": 1,
            },
            "0.##E0": {
                "notation": "scientific",
                "minimumIntegerDigits": 1,
                "maximumFractionDigits": 2,
            },
            ".0E0": {
                "notation": "scientific",
                "minimumFractionDigits": 1,
                "maximumFractionDigits": 1,
            },
            ".0#E0": {
                "notation": "scientific",
                "minimumFractionDigits": 1,
                "maximumFractionDigits": 2,
            },
            "@@@@@@@@@@@@@@@@@@@@@@@@@": {
                "minimumSignificantDigits": 21,
                "maximumSignificantDigits": 21,
            },
            "0.0": {
                "minimumIntegerDigits": 1,
                "minimumFractionDigits": 1,
                "maximumFractionDigits": 1,
            },
        }

        ecma402_options = []

        options_dict = {}
        # Which combinatins of skeleton entries need modificiation?
        # Look at the expected output...
        for option in options:
            if option != "scale/0.5" and option != "decimal-always":
                option_detail = ecma402_map[option]
                options_dict = options_dict | option_detail
            if option[0:5] == "scale":
                options_dict = options_dict | {"conformanceScale": option[6:]}
            if option == "decimal-always":
                options_dict = options_dict | {"conformanceDecimalAlways": True}

        # TODO: resolve some combinations of entries that are in conflict
        return options_dict

    def mapRoundingToECMA402(self, rounding):
        ecma402_rounding_map = {
            "default": "halfEven",
            "halfeven": "halfEven",
            "halfodd": "halfOdd",
            "halfdown": "halfTrunc",
            "halfup": "halfExpand",
            "down": "trunc",
            "up": "expand",
            "halfceiling": "halfCeil",
            "halffloor": "halfFloor",
            "floor": "floor",
            "ceiling": "ceil",
            "unnecessary": "unnecessary",
        }
        return ecma402_rounding_map[rounding]

    def mapRoundingToSkeleton(self, rounding):
        ecma402_rounding_map = {
            "default": "rounding-mode-half-even",
            "halfeven": "rounding-mode-half-even",
            "halfodd": "rounding-mode-half-odd",   # valid??
            "halfdown": "rounding-mode-half-down",
            "halfup": "rounding-mode-half-up",
            "down": "rounding-mode-down",
            "up": "rounding-mode-up",
            "halfceiling": "rounding-mode-half-up",  # correct?
            "halffloor": "rounding-mode-half-down",  # correct?
            "ceiling": "rounding-mode-ceiling",
            "floor": "rounding-mode-floor",
            "unnecessary": "rounding-mode-unnecessary",
        }
        return ecma402_rounding_map[rounding]


    def resolveOptions(self, raw_options, skeleton_list):
        # Resolve conflicts with options before putting them into the test's options.
        # TODO: fix all the potential conflicts
        resolved = raw_options
        if (
            "minimumSignificantDigits" in resolved
            and "maximumFractionDigits" in resolved
        ):
            resolved.pop("minimumSignificantDigits")

        # Set up default maximumFractionDigits if if not compact or currency
        if (
            "maximumFractionDigits" not in resolved
            and ("notation" not in resolved or resolved["notation"] != "compact")
            and ("style" not in resolved or resolved["style"] != "currency")
        ):
            resolved["maximumFractionDigits"] = 6

        if "maximumFractionDigits" not in resolved and (
            "notation" in resolved and resolved["notation"] == "compact"
        ):
            pass
            # NOT NECESSARY resolved['maximumFractionDigits'] = 2

        if skeleton_list and "percent" in skeleton_list:
            resolved["style"] = "unit"
            resolved["unit"] = "percent"
        if skeleton_list and "unit-width-full-name" in skeleton_list:
            resolved["currencyDisplay"] = "name"
            resolved["unitDisplay"] = "long"
        return resolved

    def insertNumberFmtDescr(self, tests_obj, verify_obj):
        # returns JSON data for tests and verification
        test_scenario = "number_fmt"
        test_data = {
            "Test scenario": test_scenario,
            "test_type": "number_fmt",
            "description": "Number formatter test cases. The skeleton entry corresponds to the formatting specification used by ICU while the option entries adhere to ECMA-402 syntax.",
            "source": {"repository": "icu", "version": "trunk"},
            "url": "https://raw.githubusercontent.com/unicode-org/icu/main/icu4c/source/test/testdata/numberpermutationtest.txt",
            "tests": tests_obj,
        }
        verify_data = {
            "Test scenario": test_scenario,
            "test_type": "number_fmt",
            "verifications": verify_obj,
        }
        return test_data, verify_data
