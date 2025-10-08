# Create JSON and HTML reports for verification output

# TODO: get templates from this module instead of local class
from report_template import reportTemplate

# For identifying test cases that are known problems
from check_known_issues import check_issues

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
import re
from string import Template
import sys

sys.path.append('../testdriver')
from datasets import testType
from datasets import ICUVersionMap

# https://docs.python.org/3.6/library/string.html#template-strings

# Consider Jinja2: https://jinja.palletsprojects.com/en/3.1.x/intro/

def dict_to_html(dict_data):
    # Expands a dictionary to HTML data
    result = ['<ul>']
    for key in dict_data.keys():
        result.append('  <li>%s: %s</li>' % (key, dict_data[key]))
    result.append('</ul>')
    return ''.join(result)


def sort_dict_by_count(dict_data):
    return sorted(dict_data.items(),
                  key=lambda item: len(item[1]), reverse=True)


class result_class_data():
    # Claas containing results for a type or result, e.g.,
    # for passing, failing, error, unsupported, known_issue
    def __init__(self, class_name, test_template, summary_template, result_table_template, compute_fn):
        self.name = class_name
        self.test_template = test_template,
        self.summary_template = summary_template
        self.result_table_template = result_table_template
        self.summary_compute_fn = compute_fn


class DiffSummary:
    def __init__(self):
        self.single_diffs = {}
        self.single_diff_count = 0

        self.params_diff = {}

        logging.config.fileConfig("../logging.conf")

    def add_diff(self, num_diffs, diff_list, last_diff):
        # Record single character differences
        if num_diffs == 1:
            if last_diff in self.single_diffs:
                self.single_diffs[last_diff] += 1
            else:
                self.single_diffs[last_diff] = 1

    def diff_params(self, params):
        # Count parameter values when there's a difference
        for p in params:
            if p in self.params_diff:
                self.params_diff[p] += 1
            else:
                self.params_diff[p] = 1

        # TODO: record correlated parameters


class TestReport:
    # Holds information describing the results of running tests vs.
    # the expected results.
    # TODO: use a templating language for creating these reports
    def __init__(self, report_path, report_html_path):
        self.report = None
        self.simple_results = None
        self.failure_summaries = None
        self.debug = 0

        self.verifier_obj = None

        self.timestamp = None
        self.results = None
        self.verify = None

        self.title = ''

        self.platform_info = None
        self.test_environment = None

        self.report_directory = os.path.dirname(report_path)

        self.report_file_path = report_path
        self.report_html_path = report_html_path
        self.number_tests = 0

        self.failing_tests = []
        self.passing_tests = []
        self.test_errors = []
        self.unsupported_cases = []
        self.known_issues = []

        self.templates = templates = reportTemplate()

        # For a simple template replacement
        self.report_html_template = templates.reportOutline()

        self.error_table_template = templates.error_table_template
        self.test_error_summary_template = templates.test_error_summary_template
        self.test_error_detail_template = templates.test_error_detail_template

        self.unsupported_table_template = templates.unsupported_table_template
        self.unsupported_summary_template = templates.unsupported_table_template

        self.known_issue_table_template = templates.known_issue_table_template
        self.known_issue_summary_template = templates.known_issue_table_template

        self.fail_line_template = templates.fail_line_template


        self.passing_data = result_class_data(
            'passing',
            None,
            None,
            None,
            None)

        self.failing_data = result_class_data(
            'failing',
            None,
            templates.fail_line_template,
            templates.test_error_summary_template,
            None)

        self.error_data = result_class_data(
            'errors',
            None,
            templates.error_table_template,
            templates.test_error_summary_template,
            self.compute_test_error_summary)

        self.unsupported_data = result_class_data(
            'unsupported',
            None,  # ??self.test_unsupported_template,
            self.test_error_summary_template,
            templates.unsupported_table_template,
            self.compute_unsupported_category_summary)

        self.known_issue_data = result_class_data(
            'known_issues',
            None,
            self.known_issue_summary_template,
            templates.known_issue_table_template,
            self.compute_known_issue_category_summary)

        self.known_issues = []

        self.test_type = None
        self.exec = None
        self.library_name = None

        self.platform = None

        self.missing_verify_data = []

        self.diff_summary = DiffSummary()

        self.differ = Differ()

        # Pattern for finding AM/PM in date time formatted output
        # ??self.am_pm_pattern = re.compile(r'[\s,\u202F\b]([apAP][mM])[\s\b^]')  # AM/PM as separate item
        self.am_pm_pattern = re.compile(r'\s([apAP][mM])')  # AM/PM as separate item

        logging.config.fileConfig("../logging.conf")

    def set_title(self, executor, result_version, test_type):
        self.title = 'Test %s executed on %s with data %s' % (test_type, executor, result_version)

    def record_fail(self, test):
        self.failing_tests.append(test)

    def record_pass(self, test):
        self.passing_tests.append(test)

    def record_test_error(self, test):
        self.test_errors.append(test)

    def record_unsupported(self, test):
        self.unsupported_cases.append(test)

    def record_known_issue(self, test):
        self.known_issues.append(test)

    def record_missing_verify_data(self, test):
        self.missing_verify_data.append(test)

    def summary_status(self):
        return len(self.failing_tests) == 0 and not self.missing_verify_data

    def compute_test_error_summary(self, test_errors, group_tag):
        # For the items, count messages and arguments for each
        groups = defaultdict(list)
        for error in test_errors:
            try:
                label = error['label']
                details = error.get('error_detail', None)
                if not details:
                    # Try getting the group_tag
                    details = error.get(group_tag, None)
                if isinstance(details, str):
                    detail = details
                    group = group_tag
                else:
                    detail = details.get(group_tag, None)
                    group = group_tag

                if group:
                    if not groups.get(group, None):
                        groups[group] = {detail: []}  # insert empty list
                    if not groups[group].get(detail, None):
                        groups[group][detail] = [label]
                    else:
                        groups[group][detail].append(label)
            except:
                continue

        return dict(groups)

    def compute_unsupported_category_summary(self, unsupported_cases, group_tag):
        # For the items, count messages and arguments for each
        groups = {}
        for case in unsupported_cases:
            error_detail = case.get('error_detail', None)
            label = case['label']
            if isinstance(error_detail, str):
                detail = error_detail
            else:
                if isinstance(error_detail, dict):
                    detail = error_detail.get(group_tag, None)
                else:
                    detail = error_detail

            # Specific for unsupported options - count instances of the detail
            value = str(detail)
            if groups.get(value, None):
                groups[value].append(label)
            else:
                groups[value] = [label]
        return groups

    def compute_known_issue_category_summary(selfself, cases, group_tag):
        # TODO: Fill in for known issues
        groups = {}
        return groups

    def create_report(self):
        # Make a JSON object with the data
        report = {}

        # Fill in the important fields.
        report['title'] = self.title
        # Fix up the version if we can.
        if self.platform and self.platform_info.has('icuVersion') and self.platform_info['icuVersion'] == 'unknown':
            try:
                platform = self.platform_info['platform']
                platform_version = self.platform_info['platformVersion']
                version_map = ICUVersionMap
                map_platform = version_map[platform]
                self.platform_info['icuVersion'] = map_platform[platform_version]
            except AttributeError:
                self.platform_info['icuVersion'] = 'Unknown'

        report['platform'] = self.platform_info
        report['test_environment'] = self.test_environment
        report['timestamp'] = self.timestamp

        report['passCount'] = len(self.passing_tests)
        report['failingTests'] = self.failing_tests
        report['failCount'] = len(self.failing_tests)

        report['test_errors'] = self.test_errors
        report['test_error_count'] = len(self.test_errors)

        report['unsupported'] = self.unsupported_cases
        report['unsupportedTests'] = len(self.unsupported_cases)

        report['known_issues'] = self.known_issues
        report['known_issue_count'] = len(self.known_issues)

        report['missing_verify_data'] = self.missing_verify_data

        self.report = report

        return json.dumps(report)

    def save_report(self):
        try:
            file = open(self.report_file_path, mode='w', encoding='utf-8')
        except BaseException as err:
            sys.stderr.write('!!! Cannot write report at %s: Error = %s' % (
                self.report_file_path, err))
            return None

        report_json = self.create_report()
        file.write(report_json)
        file.close()

        # TODO: Create subdirectory for json results of each type
        self.create_json_report_tree()
        return True

    def create_json_report_tree(self):
        # In that directory, create a file for the category output as JSON
        # Close
        categories = {'pass': self.passing_tests,
                      'failing_tests': self.failing_tests,
                      'test_errors': self.test_errors,
                      'unsupported': self.unsupported_cases,
                      'known_issues': self.known_issues
                      }
        for category, case_list in categories.items():
            dir_name = self.report_directory
            # Put .json files in the same directory as the .html for the detail report
            category_dir_name = os.path.join(dir_name)

            os.makedirs(category_dir_name, exist_ok=True)  # Creates the full directory path.

            # In that directory, create a file or files for the category output as JSON
            output_name = os.path.join(category_dir_name, category + ".json")  # TODO: Change to a list of files
            try:
                file = open(output_name, mode='w', encoding='utf-8')
                file.write(json.dumps(case_list))
                file.close()
            except BaseException as err:
                sys.stderr.write('!!! Cannot write report at %s\n    Error = %s' % (
                    output_name, err))
        return

    def combine_same_sets_of_labels(self, label_sets):
        # TODO: Combine sets that have the same group of labels.
        # Group by length of label list
        if not label_sets:
            return label_sets
        keys = label_sets.keys()
        # A list of combined names and sets of labels
        combined_sets = []
        for key in keys:
            set = label_sets[key]
            merged = False
            for combined in combined_sets:
                if set == combined[1]:
                    combined[0].append(key)
                    merged = True
                    continue
            if not merged:
                combined_sets.append([[key], set])
        # TODO: Create new dictionary with combined keys
        combined_dictionary = {}
        for set in combined_sets:
            key = (', ').join(set[0])
            combined_dictionary[key] = set[1]

        return combined_dictionary


    def add_known_issues(self):
        # Call functions to identify known issues, moving things from fail, error, and unsupported
        # to known_issues as needed
        new_known_issues = check_issues(
            self.test_type,
            # Don't look at tests labeled as "unsupported"
            [self.failing_tests, self.test_errors],
            self.platform_info
        )

        if new_known_issues:
            self.known_issues.extend(new_known_issues)

    def create_html_report(self):
        # Human-readable summary of test results
        if self.platform_info['icuVersion'] == 'unknown':
            try:
                platform = self.platform_info['platform']
                platform_version = self.platform_info['platformVersion']
                map_platform = ICUVersionMap[platform]
                self.platform_info['icuVersion'] = map_platform[platform_version]
            except KeyError:
                self.platform_info['icuVersion'] = 'Unknown'

        platform_info = '%s %s - ICU %s' % (
            self.platform_info['platform'], self.platform_info['platformVersion'],
            self.platform_info['icuVersion'])
        html_map = {'test_type': self.test_type,
                    'exec': self.exec,
                    # TODO: Change to 'icu4x' instead of rust
                    'library_name': self.library_name,
                    'platform_info': platform_info,
                    'test_environment': dict_to_html(self.test_environment),
                    'timestamp': self.timestamp,
                    'total_tests': self.number_tests,
                    'passing_tests': len(self.passing_tests),
                    'failing_tests': len(self.failing_tests),
                    'error_count': len(self.test_errors),
                    'unsupported_count': len(self.unsupported_cases),
                    'known_issue_count': len(self.known_issues),
                    'known_issues': self.known_issues
                    # ...
                    }

        fail_lines = []
        max_fail_length = 0
        for fail in self.failing_tests:
            fail_result = str(fail.get('result', ''))
            if len(fail_result) > max_fail_length:
                max_fail_length = len(fail_result)

            if len(fail_result) > 30:
                # Make the actual text shorter so it doesn't distort the table column
                fail['result'] = fail_result[0:15] + ' ... ' + fail_result[-14:]
            line = self.fail_line_template.safe_substitute(fail)
            fail_lines.append(line)

        # Call functions to identify known issues, moving things from fail, error, and unsupported
        # to known_issues as needed
        new_known_issues = check_issues(
            self.test_type,
            [self.failing_tests, self.test_errors, self.unsupported_cases],
            self.platform_info
        )

        if new_known_issues:
            self.known_issues.extend(new_known_issues)


        # Characterize successes, too.
        pass_characterized = self.characterize_results_by_options(self.passing_tests, 'pass')
        flat_combined_passing = self.flatten_and_combine(pass_characterized, None)
        self.save_characterized_file(flat_combined_passing, "pass")

        # Get and save failures, errors, unsupported
        error_characterized = self.characterize_results_by_options(self.test_errors, 'error')
        flat_combined_errors = self.flatten_and_combine(error_characterized, None)
        self.save_characterized_file(flat_combined_errors, "error")

        unsupported_characterized = self.characterize_results_by_options(self.unsupported_cases, 'unsupported')
        flat_combined_unsupported = self.flatten_and_combine(unsupported_characterized, None)
        self.save_characterized_file(flat_combined_unsupported, "unsupported")

        known_issues_characterized = self.characterize_results_by_options(self.known_issues, 'known_issue')
        flat_combined_known_issues = self.flatten_and_combine(known_issues_characterized, None)
        self.save_characterized_file(flat_combined_known_issues, "known_issues")

        # TODO: Should we compute top 3-5 overlaps for each set?
        # Flatten and combine the dictionary values
        fail_characterized = self.characterize_results_by_options(self.failing_tests, 'fail')
        fail_simple_diffs = self.check_simple_text_diffs(self.failing_tests, 'fail')
        flat_combined_dict = self.flatten_and_combine(fail_characterized,
                                                      fail_simple_diffs)
        self.save_characterized_file(flat_combined_dict, "fail")

        failure_labels = []
        checkboxes = []
        for key in sorted(flat_combined_dict, key=lambda k: len(flat_combined_dict[k]), reverse=True):
            value = flat_combined_dict[key]
            count = len(value)
            count_str = '%5d' % count  # TODO: Add the counts of all the sublists
            values = {'id': key, 'name': key, 'value': value, 'count': count_str,
                      'id_div': key + '_div'}
            line = self.templates.checkbox_option_template.safe_substitute(values)
            checkboxes.append(line)
            failure_labels.append(key)
        html_map['failures_characterized'] = '<br />'.join(checkboxes)

        # A dictionary of failure info.
        # html_map['failures_characterized'] = ('\n').join(list(fail_characterized))

        html_map['characterized_failure_labels'] = failure_labels

        if self.test_errors:
            # Create a table of all test errors.
            error_lines = []
            for test_error in self.test_errors:
                line = self.test_error_detail_template.safe_substitute(test_error)
                error_lines.append(line)

            error_table = self.error_table_template.safe_substitute(
                {'test_error_table': '\n'.join(error_lines)}
            )
            html_map['error_section'] = error_table

            error_summary = self.compute_test_error_summary(self.test_errors,
                                                            'error')
            error_summary_lines = []
            try:
                errors_in_error_summary = error_summary['error']
                if error_summary and 'error' in error_summary:
                    errors_in_error_summary = error_summary['error']
                    for key, labels in errors_in_error_summary.items():
                        count = len(labels)
                        sub = {'error': key, 'count': count}
                        error_summary_lines.append(
                            self.test_error_summary_template.safe_substitute(sub))
            except:
                errors_in_error_summary = None

            html_map['test_error_labels'] = errors_in_error_summary
            table = self.templates.summary_table_template.safe_substitute(
                {'table_content': '\n'.join(error_summary_lines),
                 'type': 'Error'}
            )

            html_map['error_summary'] = table
        else:
            html_map['error_section'] = 'No test errors found'
            html_map['error_summary'] = ''

        # Bundle these things in one class for each type of result
        self.fill_templates(self.unsupported_data,
                            self.unsupported_cases,
                            self.unsupported_table_template,
                            self.unsupported_summary_template,
                            html_map
                            )
        self.fill_templates(self.known_issue_data,
                            self.known_issues,
                            self.known_issue_table_template,
                            self.known_issue_summary_template,
                            html_map
                            )

        # For each failed test base, add an HTML table element with the info
        html_output = self.report_html_template.safe_substitute(html_map)

        try:
            file = open(self.report_html_path, mode='w', encoding='utf-8')
        except BaseException as err:
            sys.stderr.write('!!!!!!! CANNOT WRITE HTML REPORT at %s\n    Error = %s' % (
                self.report_html_path, err))
            return None

        file.write(html_output)
        file.close()

        # TODO: write fail_characterized to output file
        failure_json_path = os.path.join(self.report_directory, "failure_parameters.json")
        try:
            file = open(failure_json_path, mode='w', encoding='utf-8')
            file.write(json.dumps(flat_combined_dict))
            file.close()
        except Exception as err:
            logging.warning('!! %s: Cannot write %s fail_characterized data', failure_json_path, err)

        return html_output

    def flatten_and_combine(self, input_dict, input_simple):
        if input_simple:
            all_items = input_dict | input_simple
        else:
            all_items = input_dict
        # Flatten the dictionary.
        flat_items = {}
        for key, value in all_items.items():
            if len(value) <= 0:
                continue
            if type(value) == list:
                flat_items[key] = value
            elif type(value) == set:
                flat_items[key] = sorted(value)
            else:
                for key2, value2 in value.items():
                    key_new = str(key) + '.' + str(key2)
                    flat_items[key_new] = sorted(value2)

        # Sort in reverse order by length of item
        flat_combined_dict = self.combine_same_sets_of_labels(flat_items)
        return dict(sort_dict_by_count(flat_combined_dict))

    def characterize_results_by_options(self, test_list, category):
        # User self.failing_tests, looking at options
        results = defaultdict(lambda : defaultdict(list))
        if not test_list:
            # no test --> no characterizations
            return results

        results['locale'] = {}  # Dictionary of labels for each locale

        # Look at particular test types
        if self.test_type == 'plural_rules':
            self.characterize_plural_rules_tests(test_list, results)

        if self.test_type == 'datetime_fmt':
            self.characterize_datetime_tests(test_list, results)

        for test in test_list:
            # Get input_data, if available
            input_data = test.get('input_data', None)
            if not input_data:
                # Why no data?
                continue

            if not input_data:
                # Why no data?
                continue

            label = test.get('label', '')

            key_list = ['locale', 'locale_label', 'option', 'options']
            # Special case for locales
            for key in key_list:
                locale = input_data.get('locale', None)
                if locale:
                    if locale not in results['locale']:
                        results['locale'][locale] = set()
                    results['locale'][locale].add(label)

                    options = input_data.get('options', None)
                    if options:
                        # Get each combo of key/value
                        for k, value in options.items():
                            if k not in results:
                                results[k] = {}
                            if value not in results[k]:
                                results[k][value] = set()
                            results[k][value].add(label)

            key_list = ['locale', 'locale_label', 'option', 'options',
                        'language_label',
                        # Collation
                        # 'ignorePunctuation', 'compare_result',
                        'compare_type', 'test_description', 'unsupported_options', 'rules', 'test_description',
                        'warning'
                        # Number format
                        'input_data',
                        'notation', 'compactDisplay', 'style', 'currency', 'unit', 'roundingMode',
                        # list_fmt
                        'type', 'input_list',
                        # date/time format
                        'skeleton',
                        # locale names as described in various languages
                        'language_label',  # the locale being described, e.g. es-MX for Mexican Spanish
                        'locale_label',  # the language in which this locale should be given, e.g., German words for "Mexican Spanish"
                        'option', 'locale',  # in likely_subtags
                        'language_label',
                        # Some items for collation testing
                        'compare_result', 'compare_type',
                        'ignorePunctuation',
                        'test_description',
                        'strength', 'caseFirst', 'backwards',
                        'reorder', 'maxVariable',
                        'source_file'
                        # TODO!!! Characterize by actual_options keys & values
                        ]
            for key in key_list:
                if test.get(key, None):  # For collation results
                    value = test[key]
                    if not isinstance(value, str):
                        # Make this a string for comparison
                        value = str(value)
                    if key not in results:
                        results[key] = {}
                    try:
                        if value not in results[key]:
                            results[key][value] = set()
                        results[key][value].add(label)
                    except:
                        pass

            ki_key_list = ['known_issue', 'known_issue_id']
            for key in ki_key_list:
                if test.get(key, None):  # For collation results
                    value = test[key]
                    if key not in results:
                        results[key] = {}
                    if value not in results[key]:
                        results[key][value] = set()
                    results[key][value].add(label)

            # Look at the input_data part of the test result
            # TODO: Check the error_detail and error parts, too.
            key_list = [
                'compare_type',
                'error_detail',
                'ignorePunctuation',
                'language_label',
                'languageDisplay',
                'locale_label',
                'locale',
                'options',
                'option',
                'rules',
                'test_description',
                'unsupported_options',
                'style',
                'type',
                'dateStyle',
                'timeStyle,'
                'calendar',
                'unit',
                'count',
                'source_file'
            ]

            self.add_to_results_by_key(label, results, input_data, test, key_list)
            if 'actual_options' in test:
                self.add_to_results_by_key(label, results, test['actual_options'], test, key_list)

            # Special case for input_data / options.
            special_key = 'options'
            if input_data and input_data.get(special_key, None):
                options = input_data[special_key]
                self.add_to_results_by_key(label, results, options, test, options.keys())

            error_detail = test.get('error_detail', None)
            if error_detail:
                try:
                    error_keys = error_detail.keys()  # ['options']
                    self.add_to_results_by_key(label, results, error_detail, test, error_keys)
                except AttributeError:
                    pass

            # TODO: Add substitution of [] for ()
            # TODO: Add replacing (...) with "-" for numbers
            # TODO: Find the largest intersections of these sets and sort by size

        return results


    def characterize_plural_rules_tests(self, test_list, results):
        # look for consistencies with plural rules test
        for test in test_list:
            label = test['label']
            sample = test['input_data']['sample']
            sample_type = 'integer sample'
            if sample.find('c') >= 0:
                sample_type = 'compact sample'
            elif sample.find('.') >= 0:
                sample_type = 'float sample'
            elif sample.find('e') >= 0:
                sample_type = 'exponential sample'
            results.setdefault(sample_type, []).append(label)
        return

    def characterize_datetime_tests(self, test_list, results):
        # look for consistencies with datetime_fmt test
        for test in test_list:
            label = test['label']
            if 'result' in test:
                output = test['result']
            else:
                output = 'NO RESULT'
            if 'expected' in test:
               expected = test['expected']
            else:
                expected = 'NO EXPECTED VALUE'

            if 'input_data' in test and 'skeleton' in test['input_data']:
                skeleton_str = 'skeleton: ' + test['input_data']['skeleton']
                results.setdefault(skeleton_str, []).append(label)
            if 'dateTimeFormatType' in test:
                results.setdefault('dateTimeFormatType: ' + test['dateTimeFormatType'], []).append(label)
            # Check for AM/PM difference
            if output != expected:
                result_ampm = self.am_pm_pattern.search(output)
                expected_ampm = self.am_pm_pattern.search(expected)
                if ((result_ampm and not expected_ampm) or
                        (not result_ampm and expected_ampm) or
                        (result_ampm and expected_ampm and (result_ampm.group(1) != expected_ampm.group(1)))):
                    results.setdefault('AM/PM', []).append(label)
        return

    # TODO: Use the following function to update lists.
    def add_to_results_by_key(self, label, results, input_data, test, key_list):
        if input_data:
            for key in key_list:
                try:
                    if input_data.get(key, None):  # For collation results
                        value = input_data.get(key, None)
                        if key == 'input_list':
                            if 'input_size' not in results:
                                results['input_size'] = {}
                            else:
                                results['input_size'].add(len(value))
                        if key == 'rules':
                            value = 'RULE'  # A special case to avoid over-characterization
                        if key not in results:
                            results[key] = {}
                        try:
                            if not results[key].get(value, None):
                                results[key][value] = set()
                            results[key][value].add(label)
                        except TypeError as err:
                            # value may not be hashable. This should be skipped
                            pass
                except:
                    pass

    def check_simple_text_diffs(self, test_list, category):
        results = defaultdict(list)
        all_checks = ['insert', 'delete', 'insert_digit', 'insert_space', 'delete_digit',
                      'delete_space', 'replace_digit', 'replace_dff', 'replace_diff', 'whitespace_diff',
                      'replace', 'diff_in_()', 'parens', '() --> []', '[] --> ()',
                      'comma_type', 'unexpected_comma', 'boolean_diff', 'error_in_key', 'other_list_difference']
        list_differences = defaultdict(set)
        for check in all_checks:
            results[check] = set()

        for fail in test_list:
            label = fail['label']
            actual = fail.get('result', None)
            expected = fail.get('expected', None)
            if (actual is None) or (expected is None):
                continue

            if isinstance(actual, list) and isinstance(expected, list):
                list_differences = self.check_list_differences(fail, list_differences)
                continue

            if isinstance(actual, bool) and isinstance(expected, bool) and actual != expected:
                results['boolean_diff'].add(label)
                continue
                
            if isinstance(actual, list) or isinstance(expected, list):
                continue

            # The following checks work on strings
            try:
                # Get the sequence of differences for processing
                try:
                    sm = SequenceMatcher(None, expected, actual)
                    sm_opcodes = sm.get_opcodes()
                except TypeError as err:
                    # TODO Figure this out.
                    continue

                for diff in sm_opcodes:
                    # Look for insert, delete, replace
                    kind = diff[0]
                    old_val = expected[diff[1]:diff[2]]
                    new_val = actual[diff[1]:diff[2]]
                    if old_val == [] or new_val == [] or isinstance(old_val, list) or isinstance(new_val, list):
                        continue
                    if kind == 'replace':
                        if old_val.isdigit() and new_val.isdigit():
                            results['replace_digit'].add(label)
                        elif old_val.isspace() and new_val.isspace():
                            # Difference is in type of white space
                            results['whitespace_diff'].add(label)
                        else:
                            results['replace_diff'].add(label)

                    elif kind == "delete":
                        if old_val.isdigit():
                            results['delete_digit'].add(label)
                        elif old_val.isspace():
                            results['delete_space'].add(label)
                        else:
                            results['delete'].add(label)

                    elif kind == "insert":
                        if new_val.isdigit():
                            results['insert_digit'].add(label)
                        elif old_val.isspace():
                            results['insert_space'].add(label)
                        else:
                            results['insert'].add(label)
                    else:
                        pass

                if isinstance(actual, str) and abs(len(actual) - len(expected)) <= 1:
                    comp_diff = self.differ.compare(expected, actual)
                    changes = list(comp_diff)
                    # Look for number of additions and deletions
                    num_deletes = num_inserts = 0
                    for c in changes:
                        if c[0] == '+':
                            num_inserts += 1
                        if c[0] == '-':
                            num_deletes += 1
                    if num_inserts == 1 or num_deletes == 1:
                        # Look at the results for simple insert or delete
                        for x in changes:
                            if x[0] == '+':
                                if x[2] in [' ', '\u00a0', '\u202f', '\u3000']:
                                    results['insert_space'].add(label)

                                elif x[2] in ['+', '0', '+0']:
                                    results['replace_dff'].add(label)
                                    # Check if replacement is entirely within parentheses
                                else:
                                    results['insert'].add(label)
                            if x[0] == '-':
                                if x[2] in ['+', '0', '+0']:
                                    results['replace_dff'].add(label)

                # Comma stuff
                # ASCII vs. Arabic
                if expected.replace('\u002c', '\u060c') == actual:
                    results['comma_type'].add(label);
                # Check for extra comma
                if actual.replace('\u002c', '') == expected:
                    results['unexpected_comma'].add(label);

                # Check for substituted types of parentheses, brackets, braces
                if '[' in expected and '(' in actual:
                    actual_parens = actual.replace('(', '[').replace(')', ']')
                    if actual_parens == expected:
                        results['() --> []'].add(label)
                elif '(' in expected and '[' in actual:
                    actual_parens = actual.replace('[', '(').replace(')', ']')
                    if actual_parens == expected:
                        results['[] --> ()'].add(label)
            except KeyError:
                # a non-string result
                results['error_in_key'].add(label);
                continue

        results.update(list_differences)
        return dict(results)

    def check_list_differences(self, test, results):
        # Look at data where expected and actual are lists of strings
        # Update results with new instances
        # results = defaultdict(list)
        # all_checks = ['different lengths', 'different_content', 'other list difference',
        #               'type_difference']
        # for check in all_checks:
        #     results[check] = set()

        label = test['label']
        actual = test.get('result', None)
        expected = test.get('expected', None)

        if len(actual) != len(expected):
            results['different_lengths'].add(label)
        else:
            results['other_list_difference'].add(label)

            # Same length. Check how many items are different
            diff_count = 0
            for item1, item2 in zip(expected, actual):
                if item1 != item2:
                    diff_count += 1
            results['%d diffs' % diff_count].add(label)

        return results

    def save_characterized_file(self, characterized_data, characterized_type):
        try:
            json_data = json.dumps(characterized_data)
            file_name = characterized_type + "_characterized.json"
            character_file_path = os.path.join(self.report_directory, file_name)
            file = open(character_file_path, mode='w', encoding='utf-8')
            file.write(json_data)
            file.close()
        except BaseException as error:
            logging.error("%s: CANNOT WRITE CHARACTERIZE FILE FOR %s at ",
                          error, characterized_type, character_file_path)
        return

    def create_html_diff_report(self):
        # Use difflib to create file of differences
        from_lines = []
        to_lines = []
        for fail in self.failing_tests:
            from_lines.append(fail['expected'])
            to_lines.append(fail['result'])

        htmldiff = HtmlDiff()
        html_diff_result = htmldiff.make_table(from_lines[0:100], to_lines[0:100])

        new_path = self.report_html_path.replace('.html', '_diff.html')

        try:
            file = open(new_path, mode='w', encoding='utf-8')
        except BaseException as err:
            sys.stderr.write(
                '!!!!!!! CANNOT WRITE HTML REPORT at %s\n    Error = %s' % (
                    new_path, err))
            return None

        file.write(html_diff_result)
        file.close()
        return html_diff_result

    def summarize_failures(self):
        # For failing tests, examine the options and other parameters

        # General things to check in the result:
        # a. consistent 1 character substitution
        # b. consistent n-character substitution
        # c. Unicode version vs. executor

        # Things to check depend on test_type
        # Collation:
        #  a. when characters were added to Unicode
        #  b. SMP vs. BMP
        #  c. Other?

        # LanguageNames:
        #  a. language label
        #  b. locale label

        # NumberFormat
        #  locale
        #  options: several
        #  input

        self.simple_results = {}
        self.failure_summaries = {}
        for test in self.failing_tests:
            self.analyze_simple(test)
            # self.analyze(test)

        # TODO: look at the results.
        if self.debug > 0:
            logging.info('--------- %s %s %d failures-----------',
                         self.exec, self.test_type, len(self.failing_tests))
            logging.debug('  SINGLE SUBSTITUTIONS: %s',
                          sort_dict_by_count(self.diff_summary.single_diffs))
            logging.debug('  PARAMETER DIFFERENCES: %s',
                          sort_dict_by_count(self.diff_summary.params_diff))

    def analyze_simple(self, test):
        # This depends on test_type
        if self.test_type == testType.collation.value:
            return
        if 'result' not in test or 'expected' not in test:
            return

        if not test['result'] or not test['expected']:
            # TODO: Record a NULL result?
            return

        try:
            if len(test['result']) == len(test['expected']):
                # Look for single replacement
                num_diffs, diff_list, last_diff = self.find_replacements_diff(
                    test['result'], test['expected'])
                if num_diffs == 1:
                    self.diff_summary.add_diff(
                        num_diffs, diff_list, last_diff)
        except TypeError:
            return

        # ?? Look for diffs in whitespace only
        # differ = self.differ.compare(test['result'], test['expected'])

        if self.test_type == testType.number_fmt.value:
            params = test['input_data']
            self.diff_summary.diff_params(params)

            if 'options' in test['input_data']:
                # Dig deeper into options.
                self.diff_summary.diff_params(params['options'])
            return

        if self.test_type == testType.lang_names:
            params = test['input_data']
            self.diff_summary.diff_params(params)
            return

        return

    def find_replacements_diff(self, s1, s2):
        # Compare two strings, l
        diff_count = 0
        diffs = []
        last_diff = None
        l1 = [*s1]
        l2 = [*s2]
        index = 0
        for c in l1:
            d = l2[index]
            if c != d:
                diff_count += 1
                diffs.append((c, d))
                last_diff = (c, d)
            else:
                diffs.append('')
            index += 1
        return diff_count, diffs, last_diff

    def fill_templates(self, result_data, result_cases, result_table_template, summary_template, html_map):
        # For filling in templates for cases of passing, failing, errors, unsupported, known_issue
        result_class = result_data.name
        section_name = '%s_section' % result_class
        summary_name = '%s_summary' % result_class

        # TODO: Call this for each cases instead of duplicated lines
        if result_cases:
            case_lines = []
            test_table_name = 'test_%s' % result_class
            options_name = '%s_options' % result_class
            options_string = '%s options' % result_class

            # Create a table of all test results in this category.
            for unsupported in result_cases:
                line = result_data.result_table_template.safe_substitute(unsupported)
                case_lines.append(line)

            case_line_data = '\n'.join(case_lines)
            html_map[section_name] = result_data.result_table_template.safe_substitute(
                {test_table_name: case_line_data}
            )

            case_summary = {}
            if result_data.summary_compute_fn:
                case_summary = result_data.summary_compute_fn(result_cases, options_name)

            summary_lines = []
            # ??? TODO: examine if "error" is correct below
            for key, labels in case_summary.items():
                count = len(labels)
                sub = {'known_issue': key, 'count': count}
                summary_lines.append(
                    result_data.summary_template.safe_substitute(sub)
                )
            case_table = result_data.summary_template.safe_substitute(
                {'table_content': '\n'.join(summary_lines),
                 'type': options_string}
            )

            html_map[summary_name] = case_table
        else:
            html_map[section_name] = 'No %s tests found' % result_class
            html_map[summary_name] = ''


def take_second(elem):
    return elem[1]


class SummaryReport:
    # TODO: use a templating language for creating these reports
    def __init__(self, file_base):
        self.version_directories = None
        self.file_base = file_base
        self.report_dir_name = 'testReports'
        self.raw_reports = None
        self.debug = 0

        self.verifier_obj = None

        self.exec_summary = {}
        self.summary_by_test_type = {}
        self.type_summary = {}
        self.report_filename = 'verifier_test_report.json'

        self.templates = reportTemplate()

        # Default
        self.platform_order = \
            ['ICU4C', 'ICU4J', 'ICU4X', 'NodeJS', 'Dart_Web', 'Dart_Native']

        if self.debug > 1:
            logging.info('SUMMARY REPORT base = %s', self.file_base)

        self.summary_html_path = None

        self.header_item_template = Template(
            '<th>$header_data</th>'
        )
        self.line_template = Template(
            '<tr>$column_data</tr>'
        )
        self.entry_template = Template(
            '<td>$report_detail</td>'
        )

        logging.config.fileConfig("../logging.conf")

    def get_json_files(self):
        # For each executor directory in testReports,
        #  Get each json report file
        report_dir_base = os.path.join(self.file_base, self.report_dir_name)
        version_join = os.path.join(report_dir_base, '*', '*')
        self.version_directories = glob.glob(version_join)

        json_raw_join = os.path.join(version_join, '*', self.report_filename)
        raw_reports = glob.glob(json_raw_join)
        self.raw_reports = raw_reports
        self.raw_reports.sort()
        if self.debug > 1:
            logging.info('SUMMARY JSON RAW FILES = %s', self.raw_reports)
        return self.raw_reports

    def setup_all_test_results(self):
        self.get_json_files()  # From testResults files.
        self.summarize_reports()  # Initializes exec_summary and test_summary

    def summarize_reports(self):

        reports_base_dir = os.path.join(self.file_base, self.report_dir_name)

        # Get summary data by executor for each test and by test for each executor
        for filename in self.raw_reports:
            file = open(filename, encoding='utf-8', mode='r')
            # Remove the .json part of the name
            filename_base = filename.rpartition('.')[0]
            dir_path = os.path.dirname(filename_base)
            html_name = os.path.basename(filename_base) + '.html'
            # Get the relative path for the link
            html_path = os.path.join(dir_path, html_name)
            relative_html_path = os.path.relpath(html_path, reports_base_dir)
            test_json = json.loads(file.read())

            try:
                test_environment = test_json['test_environment']
                platform = test_json['platform']
            except KeyError:
                test_environment = {}
                platform = test_json['platform']

            executor = ''

            icu_version = os.path.basename(os.path.dirname(dir_path))
            results = defaultdict(lambda: defaultdict(list))
            test_type = None
            test_results = {}
            try:
                executor = test_environment['test_language']
                test_type = test_environment['test_type']
                if 'cldr_version' in platform:
                    cldr_version = platform['cldrVersion']
                else:
                    cldr_version = 'unspecified'

                test_results = {
                    'exec': executor,
                    'exec_version': '%s_%s\n%s' % (executor, platform['platformVersion'], icu_version),
                    'exec_icu_version': platform['icuVersion'],
                    'exec_cldr_version': cldr_version,
                    'test_type': test_type,
                    'date_time': test_environment['datetime'],
                    'test_count': int(test_environment['test_count']),
                    'fail_count': int(test_json['failCount']),
                    'pass_count': int(test_json['passCount']),
                    'error_count': int(test_json['test_error_count']),
                    'unsupported_count': len(test_json['unsupported']),
                    'known_issue_count': int(test_json['known_issue_count']),
                    'missing_verify_count': len(test_json['missing_verify_data']),
                    'json_file_name': filename,
                    'html_file_name': relative_html_path,  # Relative to the report base
                    'version': platform,
                    'icu_version': icu_version,
                    'platform_version': '%s %s' % (platform['platform'], platform['platformVersion'])
                }
            except BaseException as err:
                logging.error('SUMMARIZE REPORTS for file %s. Error:  %s' % (filename, err))

            if test_type not in self.summary_by_test_type:
                self.summary_by_test_type[test_type] = [test_results]
            else:
                self.summary_by_test_type[test_type].append(test_results)

            try:
                # Categorize by executor and test_type
                # TODO: Add detail of version, too
                test_version_info = test_results['version']
                slot = '%s_%s' % (executor, test_version_info['platformVersion'])
                if executor not in self.exec_summary:
                    # TESTING
                    self.exec_summary[slot] = [test_results]
                    # self.exec_summary[executor] = [test_results]
                else:
                    self.exec_summary[executor].append(test_results)

                if test_type not in self.type_summary:
                    self.type_summary[test_type] = [test_results]
                else:
                    self.type_summary[test_type].append(test_results)

            except BaseException as err:
                logging.error('SUMMARIZE REPORTS in exec_summary %s, %s. Error: %s',
                              executor, test_type, err)

    def create_summary_html(self):
        # Generate HTML page containing this information
        # Create the template

        # Make a string that looks like a JS list.
        order_of_platforms = '[' + "".join([f"\'{item}\', " for item in self.platform_order]) + ']'

        html_map = {
            'all_platforms': ', '.join(list(self.exec_summary.keys())),
            'all_icu_versions': None,  # TEMP!!!
            'all_tests': ', '.join(list(self.type_summary.keys())),
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'platform_order': order_of_platforms,
        }
        # Create header for each executor
        header_line = ''  # TODO
        html_map['header_line'] = header_line

        # Create row for each test
        detail_lines = []
        html_map['detail_lines'] = detail_lines

        # Set of executors
        exec_set = set()
        platform_version_list = set()
        for executor in self.exec_summary:
            exec_set.add(executor)
            version = self.exec_summary[executor][0]['version']
            platform_version_list.add(
                '%s %s' % (version['platform'], version['platformVersion']))

        exec_list = sorted(list(exec_set))
        platform_version_list = sorted(platform_version_list)
        # Build the table header

        header_list = ['<th>Test type</th>']
        for platform in platform_version_list:
            header_vals = {'header_data': platform}
            header_list.append(self.header_item_template.safe_substitute(header_vals))

        html_map['exec_header_line'] = self.line_template.safe_substitute(
            {'column_data': '\n'.join(header_list)}
        )

        # Generate a row containing the test data, including the test type
        # and results for each test in its column
        data_rows = []
        for test in sorted(self.type_summary):
            row_items = ['<td>%s</td>' % test]  # First column with test id
            for i in range(len(exec_list)):
                # initialize in case test was not run
                row_items.append('<td>NOT TESTED</td>')

            index = 1
            for platform_version in platform_version_list:
                # Generate a TD element with the test data
                for entry in self.type_summary[test]:
                    exec_version = entry['exec_version'].split('\n')[0]
                    # TODO: icu_version = entry['exec_version'].split('\n')[1]
                    if entry['test_type'] == test and entry['platform_version'] == platform_version:
                        try:
                            # TODO: Add ICU version and detail link
                            link_info = '<a href="%s" target="_blank">Details</a>' % entry['html_file_name']
                            icu_version_and_link = '%s\n%s' % (entry['icu_version'], link_info)
                            row_items[index] = self.entry_template.safe_substitute(
                                {'report_detail': icu_version_and_link})
                        except BaseException as err:
                            logging.error('&&& TEST: %s, EXEC: %s, row_items: %s, index: %s. Error = %s',
                                          test, executor, row_items, index, err)
                index += 1

            data_rows.append(self.line_template.safe_substitute(
                {'column_data': '\n'.join(row_items)}))

        html_map['detail_lines'] = '\n'.join(data_rows)

        output_name = 'index.html'
        # Write HTML output
        self.summary_html_path = os.path.join(self.file_base,
                                              self.report_dir_name,
                                              output_name)
        try:
            file = open(self.summary_html_path, mode='w', encoding='utf-8')
        except BaseException as err:
            sys.stderr.write(
                '!!!!!!! CANNOT WRITE SUMMARY_HTML REPORT at %s\n    Error = %s' % (
                    self.summary_html_path, err))
            return None

        html_output = self.templates.summary_html_template.safe_substitute(html_map)

        if self.debug > 1:
            logging.debug('HTML OUTPUT =\n%s', html_output)
            logging.debug('HTML OUTPUT FILEPATH =%s', self.summary_html_path)
        file.write(html_output)
        file.close()

        # Save the exec_summary.json
        exec_summary_json_path = os.path.join(self.file_base,
                                              self.report_dir_name,
                                              'exec_summary.json')
        try:
            exec_json_file = open(exec_summary_json_path, mode='w', encoding='utf-8')
            summary_by_test_type = json.dumps(self.summary_by_test_type)
            exec_json_file.write(summary_by_test_type)
            os.fsync(exec_json_file)
            exec_json_file.close()
        except BaseException as err:
            sys.stderr.write('!!! %s: Cannot write exec_summary.json' % err)

        return html_output

    def publish_results(self):
        # Update summary HTML page with data on latest verification
        # TODO: keep history of changes
        return
