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

# TODO! Load known issues from file of known problems rather than hardcoding

def compute_known_issues(test_type, test, known_issue_list):
    # Based on the type of test, check known issues against the expected vs. actual
    # results

    # Returns list of known issues identified for this single test
    known_issue_found = False
    if test_type == ddt_data.testType.datetime_fmt.value:
        known_issue_found = check_datetime_test(test, known_issue_list)

    # TODO: Add checks here for known issues in other test types

    return known_issue_found


# Tests for specific kinds of known issues
def diff_nbsp_vs_sp(actual, expected_value):
    # Returns the ID of this if the only difference in the two strings
    # is NBSP in expected vs. ASCII space in the actual result
    if not expected_value or not actual:
        return None

    # If replacing all the NBSP characdters in expected gives the actual result,
    # then the only differences were with this type of space in formatted output.
    if expected_value.replace(NBSP, SP) == actual:
        return knownIssueType.known_issue_nbsp_sp
    else:
        return None


def numerals_replaced(expected, actual):
    # If the only difference are one type of digit
    # where other digits were expected, return True
    # Returns and ID (or string) if the the numbering system changed

    # sm_opcodes describe the change to turn expected string into the actual string
    # See https://docs.python.org/3/library/difflib.html#difflib.SequenceMatcher.get_opcodes
    sm = SequenceMatcher(None, expected, actual)
    sm_opcodes = sm.get_opcodes()

    digit_replace = False
    non_digit_replacement = False

    # sm_opcodes describe the changes to turn expected string into the actual string
    # See https://docs.python.org/3/library/difflib.html#difflib.SequenceMatcher.get_opcodes
    # The tuple is [tag, i1, i2, j1, k2]
    # Tag indicates the type of change.
    # i1:i2 is the range of the substring in expected
    # j1:j2 is the range of the substring in actual

    for diff in sm_opcodes:
        tag = diff[0]  # 'replace', 'delete', 'insert', or 'equal'
        old_val = expected[diff[1]:diff[2]]
        new_val = actual[diff[1]:diff[2]]
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


def check_datetime_test(test_data, known_issues_list):
    # Examine a single test for date/time isses
    # Returns known issues identified for this test in this category
    remove_this_one = False
    try:
        result = test_data['result']
        expected = test_data['expected']
        is_ki = diff_nbsp_vs_sp(result, expected)
        if is_ki:
            # Mark the test with this issue
            test_data['known_issue'] = knownIssueType.known_issue_nbsp_sp.value
            remove_this_one = True

        is_ki = numerals_replaced(result, expected)
        if is_ki:
            test_data['known_issue_id'] = knownIssueType.known_issue_replaced_numerals.value
            remove_this_one = True

    except BaseException as err:
        # Can't get the info
        pass
        pass

    if remove_this_one:
        known_issues_list.append(test_data)

    return remove_this_one


def check_issues(test_type, test_results_to_check):
    # Look at the array of test result types, failure, error, unsupported
    # Extract any tests from these that are known issues
    # Return the list of tests that are known issues
    #
    known_issues_list = []

    for category in test_results_to_check:
        indices_to_remove = set()
        index = 0
        for test in category:
            is_known_issue = compute_known_issues(test_type, test, known_issues_list)
            if is_known_issue:
                indices_to_remove.add(index)
            index += 1

        # Remove those that were marked as known issues
        # Reverse order to not confuse the position while deleting
        # Find the locations of these labels in the  category
        rev_indices = sorted(indices_to_remove, reverse=True)
        for index in rev_indices:
            del category[index]

    return known_issues_list
