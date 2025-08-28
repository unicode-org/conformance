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
import re
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

# Handles problems with floating point values with no way to indicate precision
floating_point_has_trailing_zero = re.compile(r"\.[^1-9]+")


# Global KnownIssue Info types and strings
class knownIssueType(Enum):
    known_issue_nbsp_sp = 'ASCII Space instead of NBSP'
    known_issue_sp_nbsp = 'NBSP instead of ASCII Space'

    known_issue_replaced_numerals = 'Not creating non-ASCII numerals'

    known_issue_different_number_system = 'Different number systems'

    # Relative Date Time Format
    known_issue_unsupported_unit = 'Unsupported unit'  # https://github.com/unicode-org/conformance/issues/274

    # Datetime format
    datetime_fmt_at_inserted = 'Alternate formatting with "at" between time and date'
    datetime_fmt_arabic_comma = 'Arabic comma vs. ASCII comma'
    datetime_inserted_comma = 'inserted comma'

    datetime_semantic_Z = 'NodeJS always includes date or time'

    datetime_GMT_UTC = 'UTC instead of GMT'

    datetime_TZ_name = 'Using different names of timezone'

    # Likely Subtags
    likely_subtags_sr_latn = "sr_latin becoming en"

    # Language names
    langnames_fonipa = 'unsupported fonipa in locale'
    langnames_tag_option = 'unsupported option in locale'
    langnames_bracket_parens = 'brackets_vs_parentheses'

    # Number format
    # https://github.com/unicode-org/icu4x/issues/6678
    number_fmt_icu4x_small_fractional_numbers = 'icu4x#6678 small fractional numbers'
    number_fmt_inexact_rounding = 'Rounding unnecessary'

    # Plural rules
    plural_rules_floating_point_sample = 'limited floating point support'
    plural_rules_java_4_1_sample = 'ICU4J sample 4.1'

    # Collation
    collation_jsonc_bug_with_surrogates = 'JSON-C library mishandles some surrogates'
    collation_icu4x_FFFE = 'https://github.com/unicode-org/icu4x/issues/6811'

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

def diff_ascii_space_vs_nbsp(actual, expected_value):
    # Returns the ID of this if the only difference in the two strings
    # is Narrow Non-breaking Space (NBSP) in expected vs. ASCII space in the actual result.
    # Found in datetime testing.
    if not expected_value or not actual:
        return None

    # If replacing all the NBSP characdters in expected gives the actual result,
    # then the only differences were with this type of space in formatted output.
    if expected_value.replace(SP, NBSP) == actual:
        return knownIssueType.known_issue_sp_nbsp
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
    different_number_systems = False
    different_digit = False


    for diff in sm_opcodes:
        tag = diff[0]  # 'replace', 'delete', 'insert', or 'equal'
        old_val = expected[diff[1]:diff[2]]
        new_val = actual[diff[3]:diff[4]]
        if tag == 'replace':
            # expected[i1:i2] was replaced by actual[j1:j2]
            if old_val.isdigit() and new_val.isdigit() and len(old_val) == len(new_val):
                # If the same value, then its a numbering system difference
                for digit_old, digit_new in zip(old_val, new_val):
                    if unicodedata.numeric(digit_old) == unicodedata.numeric(digit_new):
                        different_number_systems = True

    if different_number_systems:
        return knownIssueType.known_issue_different_number_system
    else:
        return None

def unsupported_unit_quarter(test):
    input_data = test['input_data']
    if 'error' in test and test['error'] == 'unsupported unit':
        return True

    return None


def dt_check_for_alternate_long_form(actual, expected):
    # For datetime_fmt, is the format type "standard"?
    if actual == expected:
        return None
    new_expected = expected.replace(NBSP, SP)
    new_actual = actual.replace(NBSP, SP)

    # TODO: Make this an array of replacements
    replacements_to_try = [
        (' at', ','),  # English
        ('เวลา ', ''),  # Thai
        (' في', '،'),  # Arabic
        ('lúc ', ''),  # Vietnamese
        ('এ ', ''),  # Bengali
    ]

    for replacement in replacements_to_try:
        if new_actual.replace(replacement[0], replacement[1]) == new_expected:
            return knownIssueType.datetime_fmt_at_inserted
    return None


def dt_check_arabic_comma(actual, expected):
    if expected.replace('\u002c', '\u060c') == actual:
        return knownIssueType.datetime_fmt_arabic_comma
    return None


def dt_inserted_comma(actual, expected):
    sm = SequenceMatcher(None, expected, actual)
    sm_opcodes = sm.get_opcodes()
    # Look for one additional comma
    for opcode in sm_opcodes:
        if opcode[0] == 'insert':
            j1 = opcode[3]
            j2 = opcode[4]
            if actual[j1:j2] == ',':
                return knownIssueType.datetime_inserted_comma
    return None


def dt_gmt_utc(actual, expected):
    # The difference may also include NBSP vs ASCII space
    new_expected = expected.replace(NBSP, SP)
    new_actual = actual.replace(NBSP, SP)

    # Variant followed by standard
    variations = [
        ('UTC', 'GMT'),
        ('توقيت غرينتش', 'التوقيت العالمي المنسق'),  # Arabic
        ('เวลาสากลเชิงพิกัด', 'เวลามาตรฐานกรีนิช'),  # Thai
        ('協定世界時', 'グリニッジ標準時'),  # Japanese
    ]
    # !!! FINISH
    if new_actual.replace('UTC', 'GMT') == new_expected or \
            new_actual.replace('Coordinated Universal', 'Greenwich Mean') == new_expected:
        return knownIssueType.datetime_GMT_UTC
    return None

def check_datetime_known_issues(test, platform_info):
    # Examine a single test for date/time isses
    # Returns known issues identified for this test in this category
    remove_this_one = False

    all_matching_issues = []

    try:
        try:
            result = test['result']
        except KeyError as error:
            # This lack of a result may be expected.
            return False
        expected = test['expected']
        input_data = test.get('input_data')

        # Perform each test, computing matches with known issues by means of the functions in this list
        check_fns = [dt_gmt_utc, diff_nbsp_vs_ascii_space, diff_ascii_space_vs_nbsp, numerals_replaced_by_another_numbering_system,
                  dt_check_arabic_comma, dt_inserted_comma, dt_check_for_alternate_long_form]
        for check_fn in check_fns:
            is_ki = check_fn(result, expected)
            if is_ki:
                test['known_issue_id'] = is_ki.value
                remove_this_one = True
                all_matching_issues.append(is_ki.value)

        # Check if the semantic skeleton has "Z" for NodeJS
        if platform_info['platform'] == 'NodeJS' and result:
            if input_data and 'semanticSkeleton' in input_data['options'] and \
               input_data['options']['semanticSkeleton'] == 'Z':
                test['known_issue_id'] = knownIssueType.datetime_semantic_Z.value
                remove_this_one = True
                all_matching_issues.append(knownIssueType.datetime_semantic_Z.value)


    except BaseException as err:
        # Can't get the info
        pass

    return remove_this_one

def check_rdt_known_issues(test, platform_info=None):
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


def check_likely_subtags_issues(test, platform_info=None):
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
        return knownIssueType.likely_subtags_sr_latn
    else:
        return None

# Language names
def check_langnames_issues(test, platform_info=None):
    remove_this_one = False
    try:
        result = test['result']
        expected = test['expected']
    except BaseException:
        return None

    is_ki = (langname_fonipa(test) or langname_tag_option(test) or
             langname_brackets(test))
    return is_ki


def langname_fonipa(test):
    # Fonipa - one of the less supported locale options.
    input_data = test['input_data']
    lang_label = input_data['language_label']
    if lang_label.find('fonipa') >= 0:
        return knownIssueType.langnames_fonipa
    else:
        return None


def langname_tag_option(test):
    # TODO: Add other unsupported tags
    input_data = test['input_data']
    lang_label = input_data['language_label']
    if (lang_label.find('-d0') >= 0 or
        lang_label.find('-ms') >= 0 or
        lang_label.find('u-cu') >= 0
        # Or others??
    ):
        return knownIssueType.langnames_tag_option
    else:
        return None


def langname_brackets(test):
    # Check if brackets were expected but we got parentheses
    result = test['result']
    expected = test['expected']
    if result.replace('(', '[').replace(')', ']') == expected:
        return knownIssueType.langnames_bracket_parens
    else:
        return None


# Number format known issues
def check_number_fmt_issues(test, platform_info):
    input_data = test['input_data']
    result = test.get('result', None)
    expected = test.get('expected', None)
    options = input_data.get('options', None)

    if not result:
        # This must be an error because no result is found
        if 'error' in test and re.match(r'Rounding is required', test['error']):
            return knownIssueType.number_fmt_inexact_rounding

    try:
        if platform_info['platform'] == 'ICU4X' and result:
            if options:
                notation = options.get('notation', None)
                input_value = input_data.get('input', None)
                if notation == 'compact' and result[0:1] == '-' and abs(float(input_value)) < 1.0:
                    return knownIssueType.number_fmt_icu4x_small_fractional_numbers

        if expected == 'Inexact' and 'roundingMode' in input_data['options']:
            if input_data['options']['roundingMode'] == 'unnecessary':
                return knownIssueType.number_fmt_inexact_rounding

    except BaseException as error:
        pass
    return None


def check_plural_rules_issues(test, platform_info=None):
    try:
        input_data = test['input_data']
        sample_string = input_data['sample']
        # Plural rules for floating point values may not be supported
        if floating_point_has_trailing_zero.search(sample_string):
            return knownIssueType.plural_rules_floating_point_sample
        elif sample_string == '4.1':
            return knownIssueType.plural_rules_java_4_1_sample
        return None
    except KeyError as e:
        print('TEST Plural rules: %s' % test)
        return None


def check_collation_issues(test, platform_info=None):
    input_data = test.get('input_data', {})

    # Check for jsonc bug with surrogates
    try:
        actual_options = test['actual_options']
        s1_actual = actual_options['s1_actual']
        s2_actual = actual_options['s2_actual']
        if ('\ufffd' in s1_actual or '\ufffd' in s2_actual or
            ('rules' in input_data and '\ufffd' in input_data.get('rules', ''))):
            return knownIssueType.collation_jsonc_bug_with_surrogates
    except KeyError:
        pass

    # Check for ICU4X FFFE issue
    s1 = input_data.get('s1', '')
    s2 = input_data.get('s2', '')
    if '\ufffe' in s1 or '\ufffe' in s2:
        return knownIssueType.collation_icu4x_FFFE

    return None


def compute_known_issues_for_single_test(test_type, test, platform_info):
    # Based on the type of test, check known issues against the expected vs. actual
    # results

    # Returns True if this single test is an example of one or more known issues,
    known_issue_found = False
    if test_type == ddt_data.testType.collation.value:
        known_issue_found = check_collation_issues(test, platform_info)
    if test_type == ddt_data.testType.datetime_fmt.value:
        known_issue_found = check_datetime_known_issues(test, platform_info)
    elif test_type == ddt_data.testType.rdt_fmt.value:
        known_issue_found = check_rdt_known_issues(test, platform_info)
    elif test_type == ddt_data.testType.likely_subtags.value:
        known_issue_found = check_likely_subtags_issues(test, platform_info)
    elif test_type == ddt_data.testType.lang_names.value:
        known_issue_found = check_langnames_issues(test, platform_info)
    elif test_type == ddt_data.testType.number_fmt.value:
        known_issue_found = check_number_fmt_issues(test, platform_info)
    elif test_type == ddt_data.testType.plural_rules.value:
        known_issue_found = check_plural_rules_issues(test, platform_info)

    # TODO: Add checks here for known issues in other test types

    return known_issue_found

def check_issues(test_type, test_results_to_check, platform_info):
    # Look at the array of test result types, failure, error, unsupported
    # Extract any tests from these that are known issues
    # Return the list of tests that are known issues
    #
    known_issues_list = []

    for category in test_results_to_check:
        test_indices_with_known_issues = set()
        index = 0

        for test in category:
            is_known_issue = compute_known_issues_for_single_test(test_type, test, platform_info)
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
