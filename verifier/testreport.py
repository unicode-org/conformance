# Create JSON and HTLM reports for verification output

import difflib
from difflib import HtmlDiff

import json
import os
from string import Template
import sys

# https://docs.python.org/3.6/library/string.html#template-strings

# Consider Jinja2: https://jinja.palletsprojects.com/en/3.1.x/intro/

class TestReport():
  # Holds information describing the results of running tests vs.
  # the expected results.
  def __init__(self):
    self.debug = False

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
    self.error_count = 0
    self.tests_pass = 0

    self.test_type = None
    self.executor = None

    self.platform = None

    self.missing_verify_data = []

    # For a simple template replacement
    # This could be from a template file.
    self.report_html_template = Template("""<html>
  <head>
    <title>$test_type with $exec</title>
  </head>
  <body>
    <h1>$test_type</h1>
    <h2>Test details</h2>
    <p>$platform_info</p>
    <p>$test_environment</p>
    <p>Result file created: $timestamp
    <h2>Test summary</h2>
    <p>Total tests: $total_tests</p>
    <p>Passing tests: $passing_tests</p>
    <p>Failing tests: $failing_tests</p>
    <h2>Failing tests detail</h2>
    <table id='failing_tests_table'>
    <tr><th style="width"10%">Label</th><th style="width"45%">Expected</th><th style="width"45%">Result</th></tr>
      <!-- For each failing test, output row with columns
           label, expected, actual, difference -->
$failure_table
    </table>

    <h2>Test Errors</h2>
    <table id='test_error_table'>
    <tr><th style="width"10%">Label</th><th style="width"45%">Expected</th><th style="width"45%">Result</th></tr>
      <!-- For each failing test, output row with columns
           label, expected, actual, difference -->
$test_error_table
    </table>

  </body>
</html>
""")

    self.failLineTemplate = Template(
        '<tr><td>$label</td><td>$expected</td><td>$result</td><td>$input_data</td></tr>'
        )

    self.test_error_template = Template(
        '<tr><td>$label</td><td>$line</td><td>$test_error</td></td></tr>'
        )

  def recordFail(self, test):
    self.failing_tests.append(test)
    self.tests_fail += 1

  def recordPass(self, test):
    self.passing_tests.append(test)
    self.tests_pass += 1

  def recordTestError(self, test):
    self.test_errors.append(test)
    self.error_count +=1

  def recordMissingVerifyData(self, test):
    self.missing_verify_data.append(test)

  def summaryStatus(self):
    return self.tests_fail == 0 and self.missing_verify_data == []

  def createReport(self):
    # Make a JSON object with the data
    report = {}

    # Fill in the important fields.
    report['title'] = self.title

    report['platform'] = self.platform_info
    report['test_environment'] = self.testdata_environment
    report['test_errors'] = self.test_errors
    report['timestamp'] = self.timestamp
    report['failCount'] = self.tests_fail
    report['passCount'] = self.tests_pass
    report['failingTests'] = self.failing_tests
    report['missing_verify_data'] = self.missing_verify_data
    report['test_error_count'] = self.error_count
    self.report = report

    return json.dumps(report)

  def saveReport(self):
    try:
      file = open(self.report_file_path, mode='w', encoding='utf-8')
    except BaseException as err:
      sys.stderr.write('!!! Cannot write report at %s: Error = %s' % (
          self.report_file_path, err))
      return None

    self.createReport()
    file.write(json.dumps(self.report))
    file.close()

  def createHtmlReport(self):
    # Human readable summary of test results
    html_map = {'test_type': self.test_type,
                'platform_info': self.platform_info,
                'test_environment': self.testdata_environment,
                'timestamp': self.timestamp,
                'exec': self.executor,
                'total_tests': self.number_tests,
                'passing_tests': self.tests_pass,
                'failing_tests': self.tests_fail
                # ...
                }

    fail_lines = []
    for fail in self.failing_tests:
      line = self.failLineTemplate.safe_substitute(fail)
      fail_lines.append(line)

    html_map['failure_table'] = ('\n').join(fail_lines)

    error_lines = []
    for test_error in self.test_errors:
      # !!!
      print(test_error)
      line = self.test_error_template.safe_substitute(test_error)
      error_lines.append(line)

    html_map['test_error_table'] = ('\n').join(error_lines)


    # TODO: Use template and add failure lines
    # For each failed test base, add an HTML table element with the info
    html_output = self.report_html_template.safe_substitute(html_map)
    if self.debug:
      print('HTML OUTPUT= \n%s' % (html_output))

    try:
      file = open(self.report_html_path, mode='w', encoding='utf-8')
    except BaseException as err:
      sys.stderr.write('!!!!!!! CANNOT WRITE HTML REPORT at %s\n    Error = %s' % (
          self.report_html_path, err))
      return None

    file.write(html_output)
    file.close()
    return html_output

  def createHtmlDiffReport(self):
    # Use difflib to createfile of differences
    fromlines = []
    tolines = []
    for fail in self.failing_tests:
      fromlines.append(fail['expected'])
      tolines.append(fail['result'])

    if self.debug > 1:
      print('fromlines = %s' % fromlines)
      print('tolines = %s' % tolines)
    htmldiff = HtmlDiff()
    html_diff_result = htmldiff.make_table(fromlines[0:100], tolines[0:100])  #, fromdesc='expected', todesc='actual result')

    if self.debug:
      print('HTML OUTPUT= \n%s' % (html_diff_result))

    new_path = self.report_html_path.replace('.html', '_diff.html')

    try:
      file = open(new_path, mode='w', encoding='utf-8')
    except BaseException as err:
      sys.stderr.write('!!!!!!! CANNOT WRITE HTML REPORT at %s\n    Error = %s' % (
          new_path, err))
      return None

    file.write(html_diff_result)
    file.close()
    return html_diff_result

  def publishResults(self):
    # Update summary HTML page with data on latest verification
    # TODO:
    return
