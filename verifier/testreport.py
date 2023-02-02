# Create JSON and HTLM reports for verification output

from datasets import testType

import difflib
from difflib import HtmlDiff

from datetime import datetime
import glob
import json
import os
from string import Template
import sys

import unicodedata  # for info on particular characters

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
    self.number_tests = None
    self.failing_tests = []  # Include label, result, and expected

    self.tests_fail = 0
    self.passing_tests = []
    self.test_errors = []
    self.unsupported_cases = []
    self.error_count = 0
    self.tests_pass = 0

    self.test_type = None
    self.exec = None

    self.platform = None

    self.missing_verify_data = []

    self.diff_summary = DiffSummary()

    # For a simple template replacement
    # This could be from a template file.
    self.report_html_template = Template("""<html>
  <head>
    <title>$test_type with $exec</title>
    <style>
    table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
    padding: 15px;
    text-align: center;
    }
    </style>
    <script>
    function toggleElement(id) {
      const element = document.getElementById(id);
      if (element.style.display === "none") {
        element.style.display = "block";
      } else {
        element.style.display = "none";
      }
    }
    </script>
  </head>
  <body>
    <h1>Verification report: $test_type on $exec</h1>
    <h2>Test details</h2>
    <p>$platform_info</p>
    <p>$test_environment</p>
    <p>Result file created: $timestamp
    <h2>Test summary</h2>
    <p>Total: $total_tests.
    <p>Pass: $passing_tests, Fail: $failing_tests, Errors: $error_count, Unsupported: $unsupported_count</p>
    <p><i>Click on headings below to view/hide details</i></p>
    <h2 id='testErrors' onclick="toggleElement('test_error_table');">Test Errors ($error_count)</h2>
    $error_summary
    $error_section

    <h2 id='testUnsupported' onclick="toggleElement('test_unsupported_table');">Unsupported Tests  ($unsupported_count)</h2>
    $unsupported_summary
    $unsupported_section

    <h2 id='testFailures' onclick="toggleElement('failing_tests_table');">Failing tests detail ($failing_tests)</h2>
    <table id='failing_tests_table' style="display:none">
    <tr><th style="width:10%">Label</th><th style="width:20%">Expected result</th><th style="width:20%">Actual result</th><th>Test input</th></tr>
      <!-- For each failing test, output row with columns
           label, expected, actual, difference -->
$failure_table
    </table>

  </body>
</html>
""")

    self.error_table_template = Template("""    <table id='test_error_table' style="display:none">
       <tr><th width="10%">Label</th><th width="20%">Error message</th><th>Test input</tr>
       <!-- For each failing test, output row with columns
           label, expected, actual, difference -->
      $test_error_table
    </table>
""")

    self.unsupported_table_template = Template("""    <table id='test_unsupported_table' style="display:none">
       <tr><th width="10%">Label</th><th width="20%">Unsupported message</th><th>Details</tr>
       <!-- For each failing test, output row with columns
           label, expected, actual, difference -->
      $test_unsupported_table
    </table>
""")

    self.fail_line_template = Template(
        '<tr><td>$label</td><td>$expected</td><td>$result</td><td>$input_data</td></tr>'
        )

    self.test_error_template = Template(
        '<tr><td>$label</td><td>$error</td><td>$error_detail</td></tr>'
        )

    self.test_unsupported_template = Template(
        '<tr><td>$label</td><td>$unsupported</$unsupported><td>$error_detail</td></tr>'
        )

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

  def compute_category_summary(self, items, group_tag, detail_tag):
    # TODO: remove this early exit
    return
    
    # For the items, count messages and arguments for each
    groups = {}
    for item in items:
      print('@@@@@@@@@@@ item %s' % item)
      group = item.get(group_tag)
      detail = item.get(detail_tag)
      if group:
        if not groups.get(group):
          groups[group].append(item)
        else:
          groups[group]= [item]
    print('GROUPS FOR %s %s = \n%s' % (group_tag, detail_tag, groups.keys()))

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

      if len(fail['result']) > 30:
        fail['result'] = fail_result[0:15] + ' ... ' + fail_result[-14:]
      line = self.fail_line_template.safe_substitute(fail)
      fail_lines.append(line)

    if self.debug >= 2:
      print('MAX FAIL = %s, %s, %s' % (max_label, max_fail_length, max_fail))

    html_map['failure_table'] = ('\n').join(fail_lines)

    if self.test_errors:
      # Create a table of all test errors.
      error_lines = []
      for test_error in self.test_errors:
        line = self.test_error_template.safe_substitute(test_error)
        error_lines.append(line)

      html_map['error_section'] = self.error_table_template.safe_substitute(
          {'test_error_table': ('\n').join(error_lines)}
      )
    else:
      html_map['error_section'] = 'No test errors found'

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
    else:
      html_map['unsupported_section'] = 'No unsupported tests found'

    self.compute_category_summary(self.unsupported_cases,
                                  'unsupported_options',
                                  'unsupported_detail')

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

  def create_html_diff_report(self):
    # Use difflib to createfile of differences
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

class SummaryReport():
  # TODO: use a templating language for creating these reports
  def __init__(self, file_base):
    self.file_base = file_base
    self.report_dir_name = 'testReports'
    self.raw_reports = None
    self.debug = 0

    self.exec_summary = {}
    self.type_summary = {}

    if self.debug > 1:
      print('SUMMARYREPORT base = %s' % (self.file_base))

    self.summary_html_path = None
    self.summary_html_template = Template("""<html>
  <head>
    <title>DDT Summary</title>
    <style>
    table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
    padding: 15px;
    text-align: center;
    }
    </style>
    <script>
    function toggleElement(id) {
      const element = document.getElementById(id);
      if (element.style.display === "none") {
        element.style.display = "block";
      } else {
        element.style.display = "none";
      }
    }
    </script>
  </head>
  <body>
    <h1>Data Driven Test Summary</h1>
    <h3>Report generated: $datetime</h3>
    <h2>Tests and platforms</h2>
    <p>Executors verified: $all_platforms</p>
    <p>Tests verified: $all_tests</p>
    <h2>All Tests Summary</h2>
    <table id='exec_test_table'>
    $exec_header_line
    $detail_lines
    </table>
  </body>
</html>
""")
    self.header_item_template = Template(
        '<th>$header_data</th>'
        )
    self.line_template = Template(
        '<tr>$column_data</tr>'
        )
    self.entry_template = Template(
        '<td>$report_detail</td>'
        )

class SummaryReport():
  # TODO: use a templating language for creating these reports
  def __init__(self, file_base):
    self.file_base = file_base
    self.report_dir_name = 'testReports'
    self.raw_reports = None
    self.debug = 0

    self.exec_summary = {}
    self.type_summary = {}

    if self.debug > 1:
      print('SUMMARYREPORT base = %s' % (self.file_base))

    self.summary_html_path = None
    self.summary_html_template = Template("""<html>
  <head>
    <title>DDT Summary</title>
    <style>
    table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
    padding: 15px;
    text-align: center;
    }
    </style>
    <script>
    function toggleElement(id) {
      const element = document.getElementById(id);
      if (element.style.display === "none") {
        element.style.display = "block";
      } else {
        element.style.display = "none";
      }
    }
    </script>
  </head>
  <body>
    <h1>Data Driven Test Summary</h1>
    <h3>Report generated: $datetime</h3>
    <h2>Tests and platforms</h2>
    <p>Executors verified: $all_platforms</p>
    <p>Tests verified: $all_tests</p>
    <h2>All Tests Summary</h2>
    <table id='exec_test_table'>
    $exec_header_line
    $detail_lines
    </table>
  </body>
</html>
""")
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
    return '<br>'.join(outList) + '</a>'

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
        { 'column_data': ''.join(header_list) }
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
          {'column_data': ''.join(row_items)}))

    html_map['detail_lines'] = '\n'.join(data_rows)

    output_name = 'summary_report_' + datetime.now().strftime(
        '%Y%m%d_%H%M%S') + '.html'
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

    html_output = self.summary_html_template.safe_substitute(html_map)

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
