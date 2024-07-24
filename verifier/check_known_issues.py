# Functions to handle Known Issue category of results


from report_template import reportTemplate

from collections import defaultdict

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

import unicodedata

# Handle known issues database

# Automatically compute some known issues with certain patterns of differences
# in actual output vs. expected

# E.g., NBSP vs SP in NodeJS DateTime in ICU73, ...

class known_issue():
    # Stores information on a single known issue.
    # Ths may be stored in file or database
    def __init__(self):
        self.description = None
        self.url_ref = None
        self.test_type = None
        self.instances = []
        self.filter_fn = None
        self.date_posted = None

        self.issue_list = []

# Constants
NBSP = '\u202f'
SP = '\u0020'

# Global KI Info.
# TODO: add this to a class
known_issue_nbsp_sp = 'ASCII Space instead of NBSP'
known_issue_replaced_numerals = 'Not creating non-ASCII numerals'

class compute_known_issue():
    def __init__(self):
        return

    def diff_nbsp_vs_sp(self, actual, expected):
        # Returns true the only difference in the two strings
        # is NBSP in expected vs. ASCII space in the actual result
        if not expected or not actual:
            return None

        if expected.replace(NBSP, SP) == actual:
            return True
        return None

    def numerals_replaced(self, expected, actual):
        # If the only difference are one type of digit
        # where other digits were expected, return True
        sm = SequenceMatcher(None, expected, actual)
        sm_opcodes = sm.get_opcodes()

        digit_replace = False
        non_digit_replacement = False
        for diff in sm_opcodes:
            kind = diff[0]
            old_val = expected[diff[1]:diff[2]]
            new_val = actual[diff[1]:diff[2]]
            if kind == 'replace':
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
        return digit_replace and not non_digit_replace

def check_datetime(test_results):
    known_issues_list = []
    comp_ki = compute_known_issue()
    for category in test_results:
        indices_to_remove = set()
        index = 0
        for test in category:
            try:
                result = test['result']
                expected = test['expected']
                is_ki = comp_ki.diff_nbsp_vs_sp(result, expected)
                if is_ki:
                    # Mark the test with this issue
                    test['known_issue'] = known_issue_nbsp_sp

                    # TODO: remove this test from category
                    indices_to_remove.add(index)
                    # Add to known_issues_list
                    known_issues_list.append(test)

                is_ki = comp_ki.numerals_replaced(result, expected)
                if is_ki:
                    # TODO: remove this test from categoryadd_known_issues
                    test['known_issue'] = known_issue_replaced_numerals
                    indices_to_remove.add(index)
                    # Add to known_issues_list
                    known_issues_list.append(test)

            except BaseException as err:
                # Can't get the info
                pass
            index += 1

        # Remove those that were marked as known issues
        # Reverse order to not confuse the position while deleting
        rev_indices = sorted(indices_to_remove, reverse=True)
        for index in rev_indices:
            del category[index]
        pass
    return known_issues_list

def check_issues(test_type, test_results_to_check):
    # Look at the array of test result types.
    # Extract
    #
    known_issues_list = []

    if test_type == 'datetime_fmt':
        known_issues_list = check_datetime(test_results_to_check)
        # TODO: Add more types of tests
    else:
        pass

    return known_issues_list
