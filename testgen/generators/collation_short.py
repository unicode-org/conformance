# -*- coding: utf-8 -*-
import re
import logging
from generators.base import DataGenerator

reblankline = re.compile("^\s*$")


class CollationShortGenerator(DataGenerator):

    def set_patterns(self):
        self.root_locale = re.compile("@ root")
        self.locale_string = re.compile("@ locale (\S+)")

        self.test_line = re.compile("^\*\* test:(.*)")
        self.rule_header_pattern = re.compile("^@ rules")
        self.compare_pattern = re.compile("^\* compare(.*)")
        self.comparison_line = re.compile("^([<=]\S*)(\s*)(\S*)(\s*)(.*)")

        self.comment_pattern = re.compile("^(\S+)(\s*)#(.*)")
        self.attribute_test = re.compile("^% (\S+)\s*=\s*(.+)")
        self.reorder_test = re.compile("^% (reorder)\s+(.+)")

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
        strength = None

    def parse_compare(self, line_index, lines):
        # Handles lines in a compare region
        # Test sections ("* compare") are terminated by
        # definitions of new collators, changing attributes, or new test sections.
        tests = []
        line_in = lines[line_index]
        if not self.compare_pattern.match(line_in):
            return None, line_index

        string1 = ''
        line_index += 1
        while line_index < len(lines):
            line_in = lines[line_index]

            if self.compare_pattern.match(line_in):
                break
            if self.locale_string.match(line_in):
                break
            if self.root_locale.match(line_in):
                break
            if self.attribute_test.match(line_in):
                break
            if self.reorder_test.match(line_in):
                break
            if self.rule_header_pattern.match(line_in):
                break
            if self.test_line.match(line_in):
                break

            # It's a blank line, comment, or a comparison
            # ignore comment at end of this rulrule_match.group(1)e line
            if line_in == '' or line_in[0] == '#':
                # Skip blank lines
                line_index += 1
                continue

            is_comparison_match = self.comparison_line.match(line_in)
            if is_comparison_match:
                compare_type = is_comparison_match.group(1)
                # TODO !!! Check string2 for \u vs \U inm the line
                raw_string2 = is_comparison_match.group(3)
                string2 = ''
                try:
                    string2 = raw_string2.encode().decode("unicode_escape")
                except:
                    # Catch an error
                    pass

                compare_comment = is_comparison_match.group(5)
                # ??? re-encode to get excaped version of s2?
                new_test = {
                    'compare_type': compare_type,
                    's1': string1,
                    's2': string2,
                    'line': line_index,
                }
                if compare_comment:
                    new_test['compare_comment'] = compare_comment

                # Remember the previous string
                string1 = string2
                tests.append(new_test)
            line_index += 1

        return tests, line_index

    def parse_rule(self, line_index, lines):
        # Given the lines, process a rule and return the rule string,
        # rule comments, and the new line index
        # ignore comment at end of this rulrule_match.group(1)e line

        rule_list = []
        rule_comments = []

        # Check if it's really the start of rules
        line_in = lines[line_index]
        if not self.rule_header_pattern.match(line_in):
            return None, line_index

        line_index += 1
        while line_index < len(lines):
            line_in = lines[line_index]
            if self.compare_pattern.match(line_in):
                break
            if self.locale_string.match(line_in):
                break
            if self.root_locale.match(line_in):
                break

            line_index +=1
            if line_in == '' or line_in[0] == '#':
                # Skip blank lines
                continue

            # It must be a rule line
            # Remove any comments in the line preced&9<\x00                         # NUL not ignorableed by '#'
            comment_start = line_in.find("#")
            if comment_start == 0:
                continue

            # ignore comment at end of this rulrule_match.group(1)e line
            rule_match = self.comment_pattern.match(line_in)
            if rule_match:
                rule_list.append(rule_match.group(1))
                rule_comments.append(rule_match.group(3))

        # Stop at "* compare", ""@ Locale", "@ root"

        rules = ' '.join(rule_list)
        rule_comment = ', '.join(rule_comments)
        return rules, rule_comments, line_index

    def generateCollTestData2(self, filename, icu_version, start_count=0):
        # Read raw data from complex test file, e.g., collation_test.txt

        self.set_patterns()

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
        test_line = re.compile("^\*\* test:is_attribute(.*)")
        compare_pattern = re.compile("^\* compare(.*)")

        comparison_pattern = re.compile(
            "(\S+)\s+(\S+)\s*(#?.*)"
        )  # compare operator followed by string

        rules = ""
        case_first = None
        case_level = None
        numeric = None
        backwards = None

        # Ignore comment lines
        string1 = ""
        string2 = ""
        attributes = {}
        test_description = ""

        locale = ""
        line_number = 0  # Starts at one for actual lines
        num_lines = len(raw_testdata_list)
        while line_number < num_lines:
            # line_number += 1
            line_in = raw_testdata_list[line_number]

            is_comment = recommentline.match(line_in)
            if line_in[0:1] == "#" or is_comment or reblankline.match(line_in):
                line_number += 1
                continue

            if root_locale.match(line_in):
                # Reset the parameters for collation
                locale = 'root'
                rules = []
                locale = ""
                attributes = {}

                case_first = None
                case_level = None
                numeric = None
                backwards = None
                line_number += 1
                continue

            locale_match = locale_string.match(line_in)
            if locale_match:
                # Reset the parameters for collation
                locale = locale_match.group(1)
                rules = []
                locale = ""
                attributes = {}
                case_first = None
                case_level = None
                numeric = None
                backwards = None

                line_number += 1

                continue

            # Find "** test" section. Simply reset the description but leave rules alone.
            is_test_line = self.test_line.match(line_in)
            if is_test_line:
                # Get the description for subsequent tests
                test_description = is_test_line.group(1)
                line_number += 1
                continue

            # Handle rules, to be applied in subsequent tests
            is_rules = self.rule_header_pattern.match(line_in)
            if is_rules:
                rules, rule_comments, line_number = self.parse_rule(line_number, raw_testdata_list)
                line_in = raw_testdata_list[line_number]
                locale = ""
                attributes = {}
                case_first = None
                case_level = None
                numeric = None
                backwards = None

                numeric = None

            # Handle attribute settings
            is_attribute = self.attribute_test.match(line_in)
            if is_attribute:
                key = is_attribute.group(1)
                value = is_attribute.group(2)
                attributes[key] = value
                line_number += 1
                continue

            is_reorder = self.reorder_test.match(line_in)
            if is_reorder:
                key = is_reorder.group(1)
                value = is_reorder.group(2)
                attributes[key] = value
                line_number += 1
                continue

            is_compare = compare_pattern.match(line_in)
            if is_compare:
                ### Start comparisons
                new_tests, line_number = self.parse_compare(line_number, raw_testdata_list)

                # Fill in the test cases found
                for test in new_tests:
                    label = str(label_num).rjust(max_digits, "0")
                    label_num += 1

                    # # If either string has unpaired surrogates, ignore the case and record an encoding error.
                    if (self.check_unpaired_surrogate_in_string(test['s1']) or
                        self.check_unpaired_surrogate_in_string(test['s2'])):
                        # Record the problem and skip the test
                        encode_errors.append([line_number, line_in])
                    else:
                        # No unpaired surrogates. Record this test with all the attributes
                        test_case = {
                            "label": label,
                            "s1": test['s1'],
                            "s2": test['s2'],
                        }

                        # To match test output to specific tests
                        if 'line' in test:
                            test_case['line'] = test['line']
                        test_case['source_file'] = filename

                        if 'compare_comment' in test and test['compare_comment']:
                            test_case['compare_comment'] = test['compare_comment']

                        # Add info to the test case.
                        if locale:
                            test_case["locale"] = locale

                        if 'compare_type' in test:
                            test_case["compare_type"] = test['compare_type']

                        if test_description:
                            test_case["test_description"] = test_description

                        if rules:
                            test_case["rules"] = rules  # Already joined!

                        if attributes:
                            for key, value in attributes.items():
                                test_case[key] = value

                        # Test case is complete
                        test_list.append(test_case)
                        # We always expect True as the result
                        verify_list.append({"label": label, "verify": True})
            # End of compare cases
            pass

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
