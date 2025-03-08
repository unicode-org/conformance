# Functions to handle Known Issue category of results


from report_template import reportTemplate

from collections import defaultdict
from enum import Enum

from difflib import HtmlDiff
from difflib import Differ
from difflib import SequenceMatcher

from datetime import datetime

import glob
import json
import logging
import logging.config
import os
from string import Template
import sys

sys.path.append('../testdriver')
import datasets as ddt_data

# For information on characters and scripts
import unicodedata

# Handle known issues database

# Automatically compute some known issues with certain patterns of differences
# in actual output vs. expected

# E.g., NBSP vs SP in NodeJS DateTime in ICU73, ...

# Constants
NBSP = '\u202f'
SP = '\u0020'


# Global KnownIssue Info types and strings
class knownIssueType(Enum):
    known_issue_nbsp_sp = 'ASCII Space instead of NBSP'
    known_issue_replaced_numerals = 'Not creating non-ASCII numerals'

    # Relative Date Time Format
    known_issue_unsupported_unit = 'Unsupported unit'  # https://github.com/unicode-org/conformance/issues/274

    # Datetime format
    datetime_fmt_at_inserted = 'Alternate formatting with "at" between time and date'
    # Likely Subtags
    likely_subtags_sr_latn = "sr_latin becoming en"

# TODO! Load known issues from file of known problems rather than hardcoding the detection in each test

# Tests for specific kinds of known issues
def diff_nbsp_vs_ascii_space(actual, expected_value):
    # Returns the ID of this if the only difference in the two strings
    # is Narrow Non-breaking Space (NBSP) in expected vs. ASCII space in the actual result.
    # Found in datetime testing.
    if not expected_value or not actual:
        return None

    # If replacing all the NBSP characdters in expected gives the actual result,
    # then the only differences were with this type of space in formatted output.
    if expected_value.replace(NBSP, SP) == actual:
        return knownIssueType.known_issue_nbsp_sp
    else:
        return None


def numerals_replaced_by_another_numbering_system(expected, actual):
    # If the only difference are one type of digit
    # where other digits were expected, return True
    # Found in datetime testing.
    # Returns an known issue ID (or string) if the the numbering system changed

    # sm_opcodes describe the change to turn expected string into the actual string
    # See https://docs.python.org/3/library/difflib.html#difflib.SequenceMatcher.get_opcodes
    sm = SequenceMatcher(None, expected, actual)
    sm_opcodes = sm.get_opcodes()

    digit_replace = False
    non_digit_replacement = False

    # sm_opcodes describe the changes to turn expected string into the actual string
    # See https://docs.python.org/3/library/difflib.html#difflib.SequenceMatcher.get_opcodes
    # The tuple is [tag, i1, i2, j1, j2]
    # Tag indicates the type of change.
    # i1:i2 is the range of the substring in expected
    # j1:j2 is the range of the substring in actual

    for diff in sm_opcodes:
        tag = diff[0]  # 'replace', 'delete', 'insert', or 'equal'
        old_val = expected[diff[1]:diff[2]]
        new_val = actual[diff[3]:diff[4]]
        if tag == 'replace':
            # expected[i1:i2] was replaced by actual[j1:j2]
            if old_val.isdigit() and new_val.isdigit():
                # TODO!! : check the value of the numeral
                # If the same value, then its a numbering system difference
                if unicodedata.numeric(old_val) == unicodedata.numeric(new_val):
                    digit_replace = True
                else:
                    # Both were digits but different numeric values
                    non_digit_replacement = True
            else:
                # a digit was replaced with a non-digit
                non_digit_replacement = True

    # Only true if the only changes were replacing digits
    if digit_replace and not non_digit_replace:
        return knownIssueType.known_issue_replaced_numerals
    else:
        return None

def unsupported_unit_quarter(test):
    input_data = test['input_data']
    if 'error' in test and test['error'] == 'unsupported unit':
        return True

    return None


def dt_check_for_alternate_long_form(test, actual, expected):
    # For datetime_fmt, is the format type "standard"?
    if actual == expected:
        return None
    if 'dateTimeFormatType' in test['input_data'] and test['input_data'] ['dateTimeFormatType'] == 'standard':
        return knownIssueType.datetime_fmt_at_inserted
    return None


def check_datetime_known_issues(test):
    # Examine a single test for date/time isses
    # Returns known issues identified for this test in this category
    remove_this_one = False
    try:
        result = test['result']
        expected = test['expected']
        is_ki = diff_nbsp_vs_ascii_space(result, expected)
        if is_ki:
            # Mark the test with this issue
            test['known_issue'] = knownIssueType.known_issue_nbsp_sp.value
            remove_this_one = True

        is_ki = numerals_replaced_by_another_numbering_system(result, expected)
        if is_ki:
            test['known_issue_id'] = knownIssueType.known_issue_replaced_numerals.value
            remove_this_one = True

        is_ki = dt_check_for_alternate_long_form(test, result, expected)
        if is_ki:
            test['known_issue_id'] = is_ki.value
            remove_this_one = True

    except BaseException as err:
        # Can't get the info
        pass

    return remove_this_one

def check_rdt_known_issues(test):
    # ??? Do wwe need platform ID and/or icu version?
    remove_this_one = False
    try:
        try:
            result = test['result']
        except BaseException:
            result = None

        try:
            expected = test['expected']
        except BaseException:
            expected = None

        is_ki = unsupported_unit_quarter(test)
        if is_ki:
            test['known_issue_id'] = knownIssueType.known_issue_unsupported_unit.value
            remove_this_one = True

    except BaseException as err:
        pass

    return remove_this_one


def check_likely_subtags_issues(test):
    remove_this_one = False
    try:
        result = test['result']
        expected = test['expected']
    except BaseException:
        return None

    is_ki = sr_latin_likely_subtag(test)
    return is_ki


def sr_latin_likely_subtag(test):
    # FINISH
    expected = test['expected']
    result = test['result']
    if (expected.find('sr-Latn') >= 0 and
            result.find('en-') == 0):
        return likely_subtags_sr_latn
    else:
        return None



def compute_known_issues_for_single_test(test_type, test):
    # Based on the type of test, check known issues against the expected vs. actual
    # results

    # Returns True if this single test is an example of one or moore known issues,
    known_issue_found = False
    if test_type == ddt_data.testType.datetime_fmt.value:
        known_issue_found = check_datetime_known_issues(test)
    elif test_type == ddt_data.testType.rdt_fmt.value:
        known_issue_found = check_rdt_known_issues(test)
    elif test_type == ddt_data.testType.likely_subtags.value:
        known_issue_found = check_likely_subtags_issues(test)

    # TODO: Add checks here for known issues in other test types

    return known_issue_found

def check_issues(test_type, test_results_to_check):
    # Look at the array of test result types, failure, error, unsupported
    # Extract any tests from these that are known issues
    # Return the list of tests that are known issues
    #
    known_issues_list = []

    for category in test_results_to_check:
        test_indices_with_known_issues = set()
        index = 0

        for test in category:
            is_known_issue = compute_known_issues_for_single_test(test_type, test)
            if is_known_issue:
                known_issues_list.append(test)
                test_indices_with_known_issues.add(index)
            index += 1

        # Remove those that were marked as known issues
        # Reverse order to not confuse the position while deleting
        rev_indices = sorted(test_indices_with_known_issues, reverse=True)
        for index in rev_indices:
            del category[index]

    return known_issues_list
