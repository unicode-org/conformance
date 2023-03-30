# Create JSON and HTLM reports for verification output

from datasets import testType

# TODO: get templates from this module instead of local class
from report_template import reportTemplate

from collections import defaultdict

from difflib import HtmlDiff
from difflib import Differ

from datetime import datetime
import glob
import json
import operator
import os
from string import Template
import sys

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
                key=lambda item: item[1], reverse=True)

class DiffSummary():
  def __init__(self):
    self.single_diffs = {}
    self.single_diff_count = 0

    self.params_diff = {}

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

class TestReport():
  # Holds information describing the results of running tests vs.
  # the expected results.
  # TODO: use a templating language for creating these reports
  def __init__(self):
    self.debug = 1

    self.timestamp = None
    self.results = None
    self.verify = None

    self.title = ''

    self.platform_info = None
    self.test_environment = None

    self.report_directory = None
    self.report_file_path = None
    self.report_html_path = None
    self.number_tests = 0

    self.failing_tests = []  # Include label, result, and expected
    self.tests_fail = 0

    self.passing_tests = []
    self.tests_pass = 0

    self.test_errors = []
    self.error_count = 0

    self.unsupported_cases = []

    self.test_type = None
    self.exec = None

    self.platform = None

    self.missing_verify_data = []

    self.diff_summary = DiffSummary()

    templates = reportTemplate()
    self.templates = templates

    self.differ = Differ()

    # For a simple template replacement
    self.report_html_template = templates.reportOutline()

    self.error_table_template = templates.error_table_template
    self.test_error_summary_template = templates.test_error_summary_template

    self.unsupported_table_template = templates.unsupported_table_template

    self.fail_line_template = templates.fail_line_template

    self.test_error_detail_template = templates.test_error_detail_template

    self.test_unsupported_template = templates.test_unsupported_template

  def record_fail(self, test):
    self.failing_tests.append(test)
    self.tests_fail += 1

  def record_pass(self, test):
    self.passing_tests.append(test)
    self.tests_pass += 1

  def record_test_error(self, test):
    self.test_errors.append(test)
    self.error_count +=1

  def record_unsupported(self, test):
    self.unsupported_cases.append(test)
    self.error_count +=1

  def record_missing_verify_data(self, test):
    self.missing_verify_data.append(test)

  def summary_status(self):
    return self.tests_fail == 0 and not self.missing_verify_data

  def compute_test_error_summary(self, test_errors, group_tag, detail_tag):
    # For the items, count messages and arguments for each
    groups = defaultdict(list)
    for error in test_errors:
      label = error['label']
      details = error.get('error_detail')
      if not details:
        # Try getting the group_tag
        details = error.get(group_tag)
      if isinstance(details, str):
        detail = details
        group = group_tag
      else:
        detail = details.get(group_tag)
        group = group_tag

      if group:
        if groups.get(group):
          groups[group][str(detail)].append(label)
        else:
          groups[group]= {str(detail): [label]}
    return dict(groups)

  def compute_unsupported_category_summary(self, unsupported_cases, group_tag, detail_tag):
    # For the items, count messages and arguments for each
    groups = {}
    for case in unsupported_cases:
      error_detail = case.get('error_detail')
      label = case['label']
      if isinstance(error_detail, str):
        detail = error_detail
      else:
        if isinstance(error_detail, dict):
          detail = error_detail.get(group_tag)
        else:
          detail = error_detail
      group = group_tag

      # Specific for unsupported options - count the occurrnces of the detail
      value = str(detail)
      if groups.get(value):
        groups[value].append(label)
      else:
        groups[value]= [label]
    return groups

  def createReport(self):
    # Make a JSON object with the data
    report = {}

    # Fill in the important fields.
    report['title'] = self.title
    report['platform'] = self.platform_info
    report['test_environment'] = self.test_environment
    report['timestamp'] = self.timestamp
    report['failCount'] =  "{:,}".format(self.tests_fail)
    report['passCount'] =  "{:,}".format(self.tests_pass)
    report['failingTests'] =  self.failing_tests
    report['missing_verify_data'] = self.missing_verify_data
    report['test_error_count'] =  "{:,}".format(self.error_count)

    report['test_errors'] = self.test_errors
    report['unsupported'] = self.unsupported_cases
    self.report = report

    return json.dumps(report)

  def save_report(self):
    try:
      file = open(self.report_file_path, mode='w', encoding='utf-8')
    except BaseException as err:
      sys.stderr.write('!!! Cannot write report at %s: Error = %s' % (

          self.report_file_path, err))
      return None

    self.createReport()
    file.write(json.dumps(self.report))
    file.close()
    return True

  def create_html_report(self):
    # Human readable summary of test results
    html_map = {'test_type': self.test_type,
                'exec': self.exec,
                'platform_info': dict_to_html(self.platform_info),
                'test_environment': dict_to_html(self.test_environment),
                'timestamp': self.timestamp,
                'total_tests': "{:,}".format(self.number_tests),
                'passing_tests': "{:,}".format(self.tests_pass),
                'failing_tests': "{:,}".format(self.tests_fail),
                'error_count': "{:,}".format(len(self.test_errors)),
                'unsupported_count': "{:,}".format(len(self.unsupported_cases))
                # ...
                }

    fail_lines = []
    max_fail_length = 0
    max_label = ''
    max_fail = None
    for fail in self.failing_tests:
      fail_result = fail['result']
      if len(fail_result) > max_fail_length:
        max_fail_length = len(fail_result)
        max_label = fail['label']
        max_fail = fail

      if len(fail_result) > 30:
        # Make the actual text shorter so it doesn't distort the table column
        fail['result'] = fail_result[0:15] + ' ... ' + fail_result[-14:]
      line = self.fail_line_template.safe_substitute(fail)
      fail_lines.append(line)

    html_map['failure_table_lines'] = ('\n').join(fail_lines)

    fail_characterized = self.characterizeFailuresByOptions()

    fail_simple_diffs = self.check_simple_text_diffs()

    # ?? Compute top 3-5 overlaps for each set ??

    checkboxes = []
    new_dict = {}
    for key, value in fail_characterized.items():
      new_dict[key] = value
    for key, value in fail_simple_diffs.items():
      if len(value):
        new_dict[key] = value

    failure_labels = []
    for key in sorted(new_dict, key=lambda k: len(new_dict[k]), reverse=True):
      value = new_dict[key]
      count = '%5d' % len(value)
      values = {'id': key, 'name': key, 'value': value, 'count': count}
      line = self.templates.checkbox_option_template.safe_substitute(values)
      checkboxes.append(line)
      failure_labels.append(key)
    html_map['failures_characterized'] = '<br />'.join(checkboxes)

    # A dictionary of failure info.
   # html_map['failures_characterized'] = ('\n').join(list(fail_characterized))
    new_dict = fail_characterized
    for key, val in fail_simple_diffs.items():
      new_dict[key] = val
    html_map['characterized_failure_labels'] = failure_labels

    if self.test_errors:
      # Create a table of all test errors.
      error_lines = []
      for test_error in self.test_errors:
        line = self.test_error_detail_template.safe_substitute(test_error)
        error_lines.append(line)

      error_table = self.error_table_template.safe_substitute(
          {'test_error_table': ('\n').join(error_lines)}
      )
      html_map['error_section'] = error_table

      error_summary = self.compute_test_error_summary(self.test_errors,
                                                  'error',
                                                  'error_detail')
      error_summary_lines = []
      errors_in_error_summary = error_summary['error']
      if error_summary and 'error' in error_summary:
        errors_in_error_summary = error_summary['error']
        for key, items in errors_in_error_summary.items():
          count = len(items)
          sub = {'error': key, 'count': count}
          error_summary_lines.append(
              self.test_error_summary_template.safe_substitute(sub))

      html_map['test_error_labels'] = errors_in_error_summary
      table = self.templates.summary_table_template.safe_substitute(
        {'table_content': ('\n').join(error_summary_lines),
         'type': 'Error'}
      )

      html_map['error_summary'] =  table
    else:
      html_map['error_section'] = 'No test errors found'
      html_map['error_summary'] =  ''

    unsupported_lines = []
    if self.unsupported_cases:
      # Create a table of all test errors.
      error_lines = []
      for unsupported in self.unsupported_cases:
        line = self.test_unsupported_template.safe_substitute(unsupported)
        unsupported_lines.append(line)

      unsupported_line_data = ('\n').join(unsupported_lines)
      html_map['unsupported_section'] = self.unsupported_table_template.safe_substitute(
          {'test_unsupported_table': unsupported_line_data}
      )
      unsupported_summary = self.compute_unsupported_category_summary(
          self.unsupported_cases,
          'unsupported_options',
          'unsupported_detail')

      unsupported_summary_lines = []
      for key, labels in unsupported_summary.items():
        count = len(labels)
        sub = {'error': key, 'count': count}
        unsupported_summary_lines.append(
            self.test_error_summary_template.safe_substitute(sub)
        )
      unsupported_table = self.templates.summary_table_template.safe_substitute(
          {'table_content': ('\n').join(unsupported_summary_lines),
           'type': 'Unsupported options'}
      )

      html_map['unsupported_summary'] = unsupported_table
    else:
      html_map['unsupported_section'] = 'No unsupported tests found'
      html_map['unsupported_summary'] = ''

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
    return html_output

  def characterizeFailuresByOptions(self):
    # User self.failing_tests, looking at options
    results = defaultdict(list)
    fail_combos = {}
    fail_combos = {}
    for test in self.failing_tests:
      # Get input_data, if available
      label = test['label']
      if test.get('input_data'):
        # Look at locale
        input_data = test.get('input_data')

        locale_info = input_data.get('locale')
        if locale_info:
          failure_combo = 'locale' + ':' + locale_info
          results[failure_combo].append(label)

          options = input_data.get('options')
          # Get each combo of key/value
          for key,value in options.items():
            failure_combo = key + ':' + value
            results[failure_combo].append(label)

        # Try fields in language_names
        if input_data.get('language_label'):
          key = 'language_label'
          value = input_data[key]
          failure_combo = key + ':' + value
          results[failure_combo].append(label)

        if input_data.get('locale_label'):
          key = 'locale_label'
          value = input_data[key]
          failure_combo = key + ':' + value
          results[failure_combo].append(label)

        if test.get('compare'):  # For collation results
          key = 'compare'
          value = test[key]
          failure_combo = key + ':' + str(value)
          results[failure_combo].append(label)


      # Sort these by number of items in each set.

      # Find the largest intersections of these sets and sort by size
      combo_list = [(combo, len(results[combo])) for combo in results]
      combo_list.sort(key=takeSecond, reverse=True)

    return dict(results)

  def check_simple_text_diffs(self):
    results = defaultdict(list)
    results['insert'] = []
    results['delete'] = []
    results['insert_digit'] = []
    results['insert_space'] = []
    results['delete_digit'] = []
    for fail in self.failing_tests:
      actual = fail['result']
      expected = fail['expected']
      # Special case for differing by a single character.
      # Look for white space difference
      if abs(len(actual) - len(expected)) <= 1:
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
          result = {'label': fail['label']}
          for x in changes:
            if x[0] == '+':
              if x[2] in [' ', '\u00a0']:
                results['insert_space'].append(fail['label'])
              elif x[2].isdigit():
                results['insert_digit'].append(fail['label'])
              else:
                results['insert'].append(fail['label'])
            if x[0] == '-':
              if x[2].isdigit():
                results['delete_digit'].append(fail['label'])
              else:
                results['delete'].append(fail['label'])
    return dict(results)

  def create_html_diff_report(self):
    # Use difflib to create file of differences
    fromlines = []
    tolines = []
    for fail in self.failing_tests:
      fromlines.append(fail['expected'])
      tolines.append(fail['result'])

    htmldiff = HtmlDiff()
    html_diff_result = htmldiff.make_table(fromlines[0:100], tolines[0:100])

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

  def summarizeFailures(self):
    # For failing tests, examine the options and other parameters

    # General things to check in the result:
    # a. consistent 1 characdter substitution
    # b. consisten n-character substitution
    # c. Unicode version vs. executor

    # Things to check depend on test_type
    # Collation:
    #  a. when characters were added to Unicode
    #  b. SMP vs. BMP
    #  c. Other?

    # LanguageNames:
    #  a. language label
    #  b. locale label

    # Numberformat
    #  locale
    #  options: several
    #  input

    self.simple_results = {}
    self.failure_summaries = {}
    for test in self.failing_tests:
      self.analyzeSimple(test)
      # self.analyze(test)

    # TODO: look at the results.
    if self.debug > 0:
      print('--------- %s %s %d failures-----------' % (
          self.exec, self.test_type, len(self.failing_tests)))
      print('  SINGLE SUBSTITUTIONS: %s' %
            sort_dict_by_count(
                self.diff_summary.single_diffs))
      print('  PARAMETER DIFFERENCES: %s' %
            sort_dict_by_count(
                self.diff_summary.params_diff))
      print('\n')

  def analyzeSimple(self, test):
    # This depends on test_type
    if self.test_type == testType.coll_shift.value:
      return

    if len(test['result']) == len(test['expected']):
      # Look for single replacement
      num_diffs, diff_list, last_diff = self.find_replacements_diff(
          test['result'], test['expected'])
      if num_diffs == 1:
        self.diff_summary.add_diff(
            num_diffs, diff_list, last_diff)

    # ?? Look for diffs in whitespace only
    differ = self.differ.compare(test['result'], test['expected'])

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
        diff_count +=1
        diffs.append((c,d))
        last_diff = (c,d)
      else:
        diffs.append('')
      index += 1
    return diff_count, diffs, last_diff

def takeSecond(elem):
  return elem[1]

class SummaryReport():
  # TODO: use a templating language for creating these reports
  def __init__(self, file_base):
    self.file_base = file_base
    self.report_dir_name = 'testReports'
    self.raw_reports = None
    self.debug = 0

    self.exec_summary = {}
    self.type_summary = {}

    self.templates = reportTemplate()

    if self.debug > 1:
      print('SUMMARYREPORT base = %s' % (self.file_base))

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

  def getJsonFiles(self):
    # For each executor directory in testReports,
    #  Get each json report file
    self.raw_reports = glob.glob(
        os.path.join(self.file_base, self.report_dir_name, '*', '*.json'))
    if self.debug > 1:
      print('SUMMARY JSON RAW FILES = %s' % (self.raw_reports))
    return self.raw_reports

  def setupAllTestResults(self):
    self.getJsonFiles()  # From testResults files.
    self.summarizeReports()  # Initializes exec_summary and test_summary

  def summarizeReports(self):
    # Get summary data by executor for each test and by test for each executor
    for filename in self.raw_reports:
      file = open(filename, encoding='utf-8', mode='r')
      html_name = os.path.basename(filename) + '.html'

      test_json = json.loads(file.read())

      test_environment = test_json['test_environment']
      executor = ''
      try:
        executor = test_environment['test_language']
        test_type = test_environment['test_type']

        test_results = {
            'exec': executor,
            'test_type': test_type,
            'date_time': test_environment['datetime'],
            'test_count': test_environment['test_count'],
            'fail_count': test_json['failCount'],
            'pass_count': test_json['passCount'],
            'error_count': test_json['test_error_count'],
            'missing_verify_count': len(test_json['missing_verify_data']),
            'json_file_name': filename,
            'html_file_name': os.path.join(executor, html_name)
        }

      except BaseException as err:
        print('SUMMARIZE REPORTS for file %s. Error:  %s' % (filename, err))

      try:
        # Categorize by executor and test_type
        if executor not in self.exec_summary:
          self.exec_summary[executor] = [test_results]
        else:
          self.exec_summary[executor].append(test_results)

        if test_type not in self.type_summary:
          self.type_summary[test_type] = [test_results]
        else:
          self.type_summary[test_type].append(test_results)

      except BaseException as err:
        print('SUMMARIZE REPORTS in exec_summary %s, %s. Error: %s' % (
            executor, test_type, err))

  def getStats(self, entry):
    # Process items in a map to give HTML table value
    outList = []
    outList.append('Test count: %s' % entry['test_count'])
    outList.append('Succeeded: %s' % entry['pass_count'])
    outList.append('Failed: %s' % entry['fail_count'])
    outList.append('Errors: %s' % entry['error_count'])
    outList.append('Missing verify: %s' % entry['missing_verify_count'])
    outList.append('<a href="%s"  target="_blank">Details</a>' %
                   entry['html_file_name'])
    return '    \n<br>'.join(outList) + '</a>'

  def createSummaryHtml(self):
    # Generate HTML page containing this information
    # Create the template
    html_map = {
        'all_platforms': ', '.join(list(self.exec_summary.keys())),
        'all_tests': ', '.join(list(self.type_summary.keys())),
        'datetime':  datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    # Create header for each executor
    header_line = ''  # TODO
    html_map['header_line'] = header_line

    # Create row for each test
    detail_lines = []
    html_map['detail_lines'] = detail_lines

    # Set of executors
    exec_set = set()
    for exec in self.exec_summary:
      exec_set.add(exec)

    exec_list = sorted(list(exec_set))
    # Build the table header
    header_list = ['<th>Test type</th>']
    for exec in exec_list:
      header_vals = {'header_data': exec}
      header_list.append(self.header_item_template.safe_substitute(header_vals))

    html_map['exec_header_line'] = self.line_template.safe_substitute(
        { 'column_data': '\n'.join(header_list) }
    )

    # Generate a row containing the test data, including the test type
    # and results for each test in its column
    data_rows = []
    for test in sorted(self.type_summary):
      row_items = ['<td>%s</td>' % test]  # First column with test id
      for exec in exec_list:
        row_items.append('<td>NOT TESTED</td>')

      index = 1
      for exec in exec_list:
        # Generate a TD element with the test data
        for entry in self.type_summary[test]:
          if entry['test_type'] == test and entry['exec'] == exec:
            try:
              test_results = self.getStats(entry)
              # Add data
              row_items[index] = self.entry_template.safe_substitute(
                  {'report_detail': test_results})
            except BaseException as err:
              print('!!!!! Error = %s' % err)
              print('&&& TEST: %s, EXEC: %s, row_items: %s, index: %s' %
                    (test, exec, row_items, index))
        index += 1

      data_rows.append(self.line_template.safe_substitute(
          {'column_data': '\n'.join(row_items)}))

    html_map['detail_lines'] = '\n'.join(data_rows)

    # output_name = 'summary_report.html'
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
      print('HTML OUTPUT =\n%s' % (html_output))
      print('HTML OUTPUT FILEPATH =%s' % (self.summary_html_path))
    file.write(html_output)
    file.close()
    return html_output

  def publish_results(self):
    # Update summary HTML page with data on latest verification
    # TODO: keep history of changes
    return
