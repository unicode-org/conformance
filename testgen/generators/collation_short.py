# -*- coding: utf-8 -*-
import re
import logging
from generators.base import DataGenerator

reblankline = re.compile("^\s*$")


class CollationShortGenerator(DataGenerator):
    def process_test_data(self):
        # Get each kind of collation tests and create a unified data set
        json_test = {"test_type": "collation_short", "tests": [], "data_errors": []}
        json_verify = {"test_type": "collation_short", "verifications": []}
        self.insert_collation_header([json_test, json_verify])

        data_error_list = []

        start_count = 0

        # Data from more complex tests in github's unicode-org/icu repository
        # icu4c/source/test/testdata/collationtest.txt
        test_complex, verify_complex, encode_errors = self.generateCollTestData2(
            "collationtest.txt", self.icu_version, start_count=len(json_test["tests"])
        )

        if verify_complex:
            json_verify["verifications"].extend(verify_complex)

        if test_complex:
            json_test["tests"].extend(test_complex)

        data_error_list.extend(encode_errors)

        # Collation ignoring punctuation
        test_ignorable, verify_ignorable, data_errors = (
            self.generateCollTestDataObjects(
                "CollationTest_SHIFTED_SHORT.txt",
                self.icu_version,
                ignorePunctuation=True,
                start_count=len(json_test["tests"]),
            )
        )

        json_test["tests"].extend(test_ignorable)
        json_verify["verifications"].extend(verify_ignorable)
        data_error_list.extend(data_errors)

        # Collation considering punctuation
        test_nonignorable, verify_nonignorable, data_errors = (
            self.generateCollTestDataObjects(
                "CollationTest_NON_IGNORABLE_SHORT.txt",
                self.icu_version,
                ignorePunctuation=False,
                start_count=len(json_test["tests"]),
            )
        )

        # Resample as needed
        json_test["tests"].extend(test_nonignorable)
        json_test["tests"] = self.sample_tests(json_test["tests"])
        data_error_list.extend(data_errors)

        # Store data errors with the tests
        json_test["data_errors"] = data_error_list

        json_verify["verifications"].extend(verify_nonignorable)
        json_verify["verifications"] = self.sample_tests(json_verify["verifications"])
        # TODO: Store data errors with the tests

        # And write the files
        self.saveJsonFile("collation_test.json", json_test, 1)
        self.saveJsonFile("collation_verify.json", json_verify, 1)

    def insert_collation_header(self, test_objs):
        for obj in test_objs:
            obj["Test scenario"] = "collation_short"
            obj["description"] = (
                "UCA conformance test. Compare the first data string with the second and with strength = identical level (using S3.10). If the second string is greater than the first string, then stop with an error."
            )

    def reset_test_data(self, rules, locale, attributes, strength):
        rules = []
        locale = ""
        attributes = []
        strength = None

    def generateCollTestData2(self, filename, icu_version, start_count=0):
        # Read raw data from complex test file, e.g., collation_test.txt
        label_num = start_count

        test_list = []
        verify_list = []
        encode_errors = []

        rawcolltestdata = self.readFile(filename, icu_version)
        if not rawcolltestdata:
            return test_list, verify_list, encode_errors

        raw_testdata_list = rawcolltestdata.splitlines()
        max_digits = 1 + self.computeMaxDigitsForCount(
            len(raw_testdata_list)
        )  # Approximate
        recommentline = re.compile("^[\ufeff\s]*#(.*)")

        root_locale = re.compile("@ root")
        locale_string = re.compile("@ locale (\S+)")
        test_line = re.compile("^\*\* test:(.*)")
        rule_header_pattern = re.compile("^@ rules")
        rule_pattern = re.compile("^&.*")
        strength_pattern = re.compile("% strength=(\S+)")
        alternate_pattern = re.compile("% alternate=(\S+)")
        reorder_pattern = re.compile("^\% reorder(.*)")
        numeric_pattern = re.compile("% numeric=(\S+)")
        case_level_pattern = re.compile("% caseLevel=(\S+)*")
        case_first_pattern = re.compile("% caseFirst=(\S+)*")
        compare_pattern = re.compile("^\* compare(.*)")

        comparison_pattern = re.compile(
            "(\S+)\s+(\S+)\s*(\#?.*)"
        )  # compare operator followed by string

        attribute_test = re.compile("^\% (\S+)\s*=\s*(\S+)")
        rules = ""
        strength = None
        alternate = None
        reorder = None
        case_first = None
        case_level = None

        # Ignore comment lines
        string1 = ""
        string2 = ""
        attributes = []
        test_description = ""

        # Get @ root or @ locale ...
        # Check for "@ rules"
        # Handle % options, e.g., strengt=h, reorder=, backwards=, caseFirst=,
        #  ...
        # Find "* compare" section and create list of tests for this,
        # starting comparison with empty string ''.
        # Handle compre options =, <, <1, <2, <3, <4

        locale = ""
        line_number = 0  # Starts at one for actual lines
        num_lines = len(raw_testdata_list)
        while line_number < num_lines:
            line_number += 1
            line_in = raw_testdata_list[line_number]

            is_comment = recommentline.match(line_in)
            if line_in[0:1] == "#" or is_comment or reblankline.match(line_in):
                continue

            if root_locale.match(line_in):
                # Reset the parameters for collation
                # locale = "und"
                rules = []
                locale = ""
                attributes = []
                strength = None
                continue

            locale_match = locale_string.match(line_in)
            if locale_match:
                # Reset the parameters for collation
                locale = locale_match.group(1)
                rules = []
                locale = ""
                attributes = []
                strength = None
                continue

            # Find "** test" section. Simply reset the description but leave rules alone.
            is_test_line = test_line.match(line_in)
            if is_test_line:
                # Get the description for subsequent tests
                test_description = is_test_line.group(1)
                continue

            # Handle rules, to be applied in subsequent tests
            is_rules = rule_header_pattern.match(line_in)
            if is_rules:
                # Read rule lines until  a "*" line is found
                rules = []
                locale = "und"
                rules = []
                locale = ""
                attributes = []
                strength = None
                numeric = None
                compare_type = None

                # Proces rule lines, Skip comments
                # Terminate the rule on empty lines or lines with '*' or '%'
                while line_number < num_lines:
                    # Increment line_number here?
                    line_number += 1
                    if line_number >= num_lines:
                        break
                    line_in = raw_testdata_list[line_number]
                    if len(line_in) == 0 or line_in[0] == "#":
                        # Keep building the rule
                        continue
                    is_compare = compare_pattern.match(line_in)
                    if is_compare or line_in[0] == "%":
                        break

                    is_test_line = test_line.match(line_in)
                    if is_test_line:
                        # Update the description, but don't add to rule
                        test_description = is_test_line.group(1)
                        continue

                    # Remove any comments in the line preceded by '#'
                    comment_start = line_in.find("#")
                    if comment_start >= 0:
                        # ignore comment at end of this rule line
                        line_in = line_in[0:comment_start]
                    rules.append(line_in.strip())
                # Done getting the rule parts.
                pass
            if len(line_in) == 0:
                continue

            is_strength = strength_pattern.match(line_in)
            if is_strength:
                strength = is_strength.group(1)

            is_alternate = alternate_pattern.match(line_in)
            if is_alternate:
                altername = is_alternate.group(1)

            is_reorder = reorder_pattern.match(line_in)
            if is_reorder:
                reorder = is_reorder.group(1)

            is_case_first = case_first_pattern.match(line_in)
            if is_case_first:
                case_first = is_case_first.group(1)

            is_case_level = case_level_pattern.match(line_in)
            if is_case_level:
                case_level = is_case_level.group(1)

            is_reorder = reorder_pattern.match(line_in)
            if is_reorder:
                reorder = is_reorder.group(1)

            # TODO: Use this!
            is_numeric = numeric_pattern.match(line_in)
            if is_numeric:
                use_numeric = is_numeric.group(1)

            is_compare = compare_pattern.match(line_in)
            if is_compare:
                compare_type = None
                # Initialize string1 to the empty string.
                string1 = ""
                while line_number < num_lines:
                    line_number += 1
                    if line_number >= num_lines:
                        break
                    line_in = raw_testdata_list[line_number]

                    if len(line_in) == 0 or line_in[0] == "#":
                        continue
                    if line_in[0] == "*":
                        break

                    is_comparison = comparison_pattern.match(line_in)
                    # Handle compare options =, <, <1, <2, <3, <4
                    if is_comparison:
                        compare_type = is_comparison.group(1)
                        compare_string = is_comparison.group(2)
                        # Note that this doesn't seem to handle \x encoding, however.
                        compare_comment = is_comparison.group(3)
                        # Generate the test case
                        try:
                            string2 = compare_string.encode().decode("unicode_escape")
                        except (BaseException, UnicodeEncodeError) as err:
                            logging.error(
                                "%s: line: %d. PROBLEM ENCODING", err, line_number
                            )
                            continue

                        compare_comment = is_comparison.group(3)

                    label = str(label_num).rjust(max_digits, "0")
                    label_num += 1

                    # # If either string has unpaired surrogates, ignore the case and record it.
                    if not self.check_unpaired_surrogate_in_string(
                        string1
                    ) and not self.check_unpaired_surrogate_in_string(string2):
                        test_case = {
                            "label": label,
                            "s1": string1,
                            "s2": string2,
                        }

                        # Add info to the test case.
                        if locale:
                            test_case["locale"] = locale
                        # To match test output to specific tests
                        test_case['line'] = line_number

                        if compare_type:
                            if type(compare_type) in [list, tuple]:
                                test_case["compare_type"] = compare_type[0]
                            else:
                                test_case["compare_type"] = compare_type
                        if test_description:
                            test_case["test_description"] = test_description

                        if compare_comment:
                            test_case["compare_comment"] = compare_comment
                        if rules:
                            test_case["rules"] = "".join(rules)
                        if attributes:
                            test_case["attributes"] = attributes

                        if strength:
                            test_case["strength"] = strength

                        if alternate:
                            test_case["alternate"] = alternate

                        if numeric:
                            test_case["numeric"] = numeric

                        if reorder:
                            test_case["reorder"] = reorder

                        if case_first:
                            test_case["case_first"] = case_first

                        if case_level:
                            test_case["case_level"] = case_level

                        test_list.append(test_case)
                        # We always expect True as the result

                        verify_list.append({"label": label, "verify": True})
                    else:
                        # Record the problem and skip
                        encode_errors.append([line_number, line_in])
                        pass

                    # Keep this for the next comparison test
                    string1 = string2
                continue

            is_attribute = attribute_test.match(line_in)
            if is_attribute:
                attributes.append([is_attribute.group(1), is_attribute.group(2)])
                continue
        if encode_errors:
            logging.debug(
                "!! %s File has %s ENCODING ERRORS: %s",
                filename,
                len(encode_errors),
                encode_errors,
            )
        return test_list, verify_list, encode_errors

    def generateCollTestDataObjects(
        self, filename, icu_version, ignorePunctuation, start_count=0
    ):
        test_list = []
        verify_list = []
        data_errors = []  # Items with malformed Unicode

        # Read raw data
        rawcolltestdata = self.readFile(filename, icu_version)

        if not rawcolltestdata:
            return test_list, verify_list, data_errors

        raw_testdata_list = rawcolltestdata.splitlines()

        # Handles lines of strings to be compared with collation.
        # Adds field for ignoring punctuation as needed.
        recommentline = re.compile("^\s*#")

        max_digits = 1 + self.computeMaxDigitsForCount(
            len(raw_testdata_list)
        )  # Approximately correct
        count = start_count

        prev = None
        index = 0
        line_number = 0
        for item in raw_testdata_list[1:]:
            line_number += 1
            if recommentline.match(item) or reblankline.match(item):
                continue
            # It's a data line.
            if not prev:
                # Just getting started.
                prev = self.parseCollTestData(item)
                continue

            # Get the code points for each test
            next = self.parseCollTestData(item)

            if not next:
                # This is a problem with the data input. D80[0-F] is the high surrogate
                data_errors.append([index, item])
                continue

            label = str(count).rjust(max_digits, "0")
            new_test = {"label": label, "s1": prev, "s2": next, "line": line_number}
            if ignorePunctuation:
                new_test["ignorePunctuation"] = True
            test_list.append(new_test)

            verify_list.append({"label": label, "verify": True})

            prev = next  # set up for next pair
            count += 1
            index += 1

        logging.info("Coll Test: %d lines processed", len(test_list))
        if data_errors:
            logging.debug(
                "!! %s File has %s DATA ERRORS: %s",
                filename,
                len(data_errors),
                data_errors,
            )

        return test_list, verify_list, data_errors

    def parseCollTestData(self, testdata):
        testdata = testdata.encode().decode("unicode_escape")
        recodepoint = re.compile(r"[0-9a-fA-F]{4,6}")

        return_list = []
        codepoints = recodepoint.findall(testdata)
        for code in codepoints:
            num_code = int(code, 16)
            if num_code >= 0xD800 and num_code <= 0xDFFF:
                return None
            return_list.append(self.stringifyCode(num_code))
        return "".join(return_list)

    def stringifyCode(self, cp):
        # Just include character and escaping will work in JSONification
        try:
            teststring = chr(cp)
        except ValueError as err:
            teststring = cp

        return teststring

    high_surrogate_pattern = re.compile(r"([\ud800-\udbff])")
    low_surrogate_pattern = re.compile(r"([\udc00-\udfff])")

    def check_unpaired_surrogate_in_string(self, text):
        # Look for unmatched high/low surrogates in the text
        # high_surrogate_pattern = re.compile(r'([\ud800-\udbff])')
        # low_surrogate_pattern = re.compile(r'([\udc00-\udfff])')

        match_high = self.high_surrogate_pattern.findall(text)
        match_low = self.low_surrogate_pattern.findall(text)

        if not match_high and not match_low:
            return False

        if match_high and not match_low:
            return True

        if not match_high and match_low:
            return True

        if len(match_high) != len(match_low):
            return True

        # TODO: Check if each high match is immediately followed by a low match
        # Now, assume that they are paired

        return False
