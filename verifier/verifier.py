# Verifier class for checking actual test output vs. expectations

import json
import os
import sys

from testreport import TestReport

class Verifier():
  def __init__(self, test_type, result_path, verify_path, report_path=None):
    self.debug = True
    self.report = TestReport()
    self.test_type = test_type
    self.result_path = result_path
    self.verify_path = verify_path
    self.report_path = report_path

    try:
      self.result_file = open(self.result_path, encoding='utf-8', mode='r')
    except BaseException as err:
      print('*** Cannot open results file %s: err = %s' % (result_path, err))
      return None

    try:
      self.verify_data_file = open(self.verify_path, encoding='utf-8', mode='r')
    except BaseException as err:
      print('**!!* Cannot open verify file %s' % (self.verify_path,))
      return None

    # Default filename for report
    self.report_filename = os.path.split(result_path)[-1]
    try:
      if not report_path:
        report_directory = os.path.commonprefix(result_path, verify_path)
        self.report_path = os.path.join(report_directory, self.report_filename)
        self.report_file = open(self.report_filename, encoding='utf-8', mode='w')
    except BaseException as err:
      print('*** Cannot open verify file %s' % (self.report_filename,))
      return None

    self.results = None
    self.expected = None

  def compareTestToExpected(self):
    # Get the JSON data for results
    try:
      self.resultData = json.loads(self.result_file.read())
    except BaseException as err:
      sys.stderr.write('Cannot load %s result data: %s' % (self.result_path, err))
      return None
    self.result_file.close()

    try:
      self.verifyData = json.loads(self.verify_data_file.read())
    except BaseException as err:
      sys.stderr.write('Cannot load %s verify data: %s' % (self.verify_path, err))
      return None
    self.verify_data_file.close()

    # Compare each results with the apprpriate verification data.
    try:
      self.results = self.resultData['tests']
    except BaseException as err:
      sys.stderr.write('No tests in result %s, Error = %s' % (self.result_path, err))
      return None

    # TODO: !!! Sort by label value

    if 'platform_error' in self.resultData:
      print('PLATFORM ERROR: %s' % self.resultData['platform error'])
      print('No verify done!!!')
      return None

    if self.debug:
      print('\nTEST RESULTS for %s. %d tests found' % (self.test_type, len(self.results)))
      try:
        print('     Platform: %s' % self.resultData["platform"])
        print('     %s Errors running tests' % self.resultData["errorInfo"])
      except BaseException as err:
        sys.stderr.write('### Missing fields %s, Error = %s' % (self.resultData, err))

      try:
        self.expected = self.verifyData['verifications']
        # self.expected = sort(self.verifyData['verifications'],
        #                     key=lambda item: item['label'])
      except BaseException as err:
        sys.stderr.write('No verifications in verify %s' % self.result_path)

    verifyIndex = 0

    if not self.expected:
      sys.stderr.write('No expected data in %s' % self.verify_path)
      return None

    if not self.results:
      print('*$*$*$*$* self.results = %s' % self.results)

      return None

    for testStr in self.results:
      if not testStr:
        print('@@@@@ no test string: %s of %s' % (testStr, len(self.results)))
      if self.debug:
        print('*$*$*$*$* testStr = %s' % testStr)

      test = testStr  # What's up?
      #test = json.loads(testStr)  # !!! This should not be necessary

      # Get the result
      try:
        actual_result = test['result']
        test_label = test['label']
      except:
        print('^^^^^ SKIPPING: Error with test results: %s' % testStr)
        continue

      verdata = self.findExpectedWithLabel(test_label)

      if not verdata:
        print('*** Cannot find verify data with label %s' % test_label)
        self.report.recordMissingVerifyData(test)
        # Bail on this test
        continue

      expected_result = verdata['verify']
      # if self.debug:
      #   print('VVVVV: %s actual %s, expected %s' % (
      #       (actual_result == expected_result),
      #       actual_result, expected_result))
      if actual_result == expected_result:
        self.report.recordPass(test)
      else:
        self.report.recordFail(test)

    return

  def findExpectedWithLabel(self, test_label):
    # Look for test_label in the expected data
    # Very inefficient - use Binary Search on sorted labels.
    # if self.debug:
    #  print(' look for test_label %s' % test_label)
    if not self.expected:
      return None
    for item in self.expected:
      if item['label'] == test_label:
        if self.debug:
          print('  Found label %s' % item)
        return item
    print('NO RETURN from findExpectedWithLabel with test_label = %s' %
           test_label)
    return True

  def analyzeFailures(self):
    # Analyze the test failures for types of mistakes, missing data, etc.?
    # !!! TODO: something
    return


class Tester():
  def __init__(self, title=None):
    self.title = title
    self.test_type = None
    self.verifier = None

  def setupPathsAndRun(self, exec, testfile, verifyfile):
    baseDir = '.'
    resultPath = os.path.join(baseDir, 'testResults', exec, testfile)
    verifyPath = os.path.join(baseDir, 'testData', verifyfile)
    reportPath = os.path.join(baseDir, 'testReports', exec, testfile)

    self.verifier = Verifier(self.test_type, resultPath, verifyPath, reportPath)

    result = self.verifier.compareTestToExpected()

    self.printResult()

    return result

  def collationExec(self, exec):
    # Set up paths and run verify
    self.title = exec.upper() + ' COLL_SHIFT_SHORT'
    self.test_type = 'coll_shift_short'
    result = self.setupPathsAndRun(
        exec, 'coll_test_shift.json', 'coll_verify_shift.json')

  def decimalFmtExec(self, exec):
    self.title = exec.upper() + ' DECIMAL_FMT'
    self.test_type = 'decimal_fmt'
    result = self.setupPathsAndRun(
        exec, 'dcml_fmt_test_file.json', 'dcml_fmt_verify.json')

  def displayNamesExec(self, exec):
    self.title = exec.upper() + ' DISPLAY_NAMES'
    self.test_type = 'display_names'
    result = self.setupPathsAndRun(
        exec, 'display_names.json', 'display_names_verify.json')

  def printResult(self):
    print('\n  Test Report for %s' % self.title)
    testReport = self.verifier.report
    reportData = testReport.createReport()
    print('  Report: %s' % reportData)


# For testing
def main(args):
  execs = ['nodejs', 'rust']

  for exec in execs:
    testerCollNode = Tester()
    testerCollNode.collationExec(exec)

    testerDecimalFmt = Tester()
    testerDecimalFmt.decimalFmtExec(exec)

    testerDisplayNames = Tester()
    testerDisplayNames.displayNamesExec(exec)


if __name__ == '__main__':
  main(sys.argv)
