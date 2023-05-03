# Verifier class for checking actual test output vs. expectations

from datetime import datetime, timezone
import glob
import json
import os
import sys

sys.path.append('../testdriver')

import datasets as ddtData
from ddtargs import VerifyArgs

from testreport import TestReport

from testreport import SummaryReport

class Verifier():
  def __init__(self):
    self.debug = 0  # Different levels

    self.report = None
    self.reports = []

    self.options = None
    # Set of [result filepath, verify filepath, report path]
    self.result_timestamp = None

    # All the items that will be verified
    self.verify_plans = []

  def openVerifyFiles(self):
    # Get test data, verify data, and results for a case.
    try:
      self.result_file = open(self.result_path, encoding='utf-8', mode='r')
      self.result_timestamp = datetime.fromtimestamp(
          os.path.getmtime(self.result_path)).strftime('%Y-%m-%d %H:%M')
    except BaseException as err:
      print('    *** Cannot open results file:\n        %s' % (err))
      return None

    try:
      self.verify_data_file = open(self.verify_path, encoding='utf-8', mode='r')
    except BaseException as err:
      print('    **!!* Cannot open verify file %s' % (self.verify_path))
      return None

    # Create report directory if needed
    try:
      report_dir = os.path.dirname(self.report_path)
      if not os.path.isdir(report_dir):
        os.makedirs(report_dir)
    except BaseException as err:
      sys.stderr.write('    !!! Cannot create directory %s for report file %s' %
                       (report_dir, self.report_path))
      sys.stderr.write('   !!! Error = %s' % err)
      return None

    try:
      self.report_file = open(self.report_path, encoding='utf-8', mode='w')
    except BaseException as err:
      print('*** Cannot open file %s: Error = %s' % (self.report_path, err))
      return None

    # Get the input file to explain test failures
    try:
      self.testdata_file = open(self.testdata_path, encoding='utf-8', mode='r')
    except BaseException as err:
      print('*** Cannot open testdata file %s: Error = %s' % (self.testdata_path, err))
      return None

    # Initialize values for this case.
    self.results = None
    self.expected = None
    self.testdata = None
    return True  # Indicates that data

  def parseArgs(self, args):
    # Initialize commandline arguments
    verifyInfo = VerifyArgs(args)
    if self.debug > 1:
      print('!!! ARGS = %s' % args)
      print('VERIFY INFO: %s' % verifyInfo)
    self.setVerifyArgs(verifyInfo.getOptions())

  def setVerifyArgs(self, argOptions):
    self.options = argOptions
    self.test_types = argOptions.test_type
    # Create a set of verifications based on exec and test_type

    self.input_file_names = argOptions.input_path

    self.file_base = argOptions.file_base
    if self.debug > 1:
      print('TEST TYPES = %s' % self.test_types)

    if not argOptions.summary_only:
      self.setupVerifyPlans()

  def setupVerifyPlans(self):
    # Set of [result file, verify file]

    if self.options.verify_all:
      # Generates exec and test lists from the existing files in
      # testResults directories
      summaryReport = SummaryReport(self.file_base)
      summaryReport.getJsonFiles()
      summaryReport.summarizeReports()
      executor_list = summaryReport.exec_summary.keys()
      test_list = summaryReport.type_summary.keys()
    else:
      executor_list = self.options.exec
      test_list = self.options.test_type

    for exec in executor_list:
      for test_type in test_list:

        # TODO: Run for each test_type!
        if test_type not in ddtData.testDatasets:
          print('**** WARNING: test_type %s not in testDatasets' %
                test_type)
          raise ValueError('No test dataset found for test type >%s<' %
                           self.test_type)
        else:
          # Create a test plan based on data and options
          self.testData = ddtData.testDatasets[test_type]

        testdata_path = os.path.join(self.file_base,
                                   self.options.input_path,
                                   self.testData.testDataFilename)

        verify_file_name = ddtData.testDatasets[test_type].verifyFilename

        # Set the name of the verification file. These files are
        # usually in the same directory as the test data files.
        verify_file_path = os.path.join(self.file_base,
                                        self.options.input_path,
                                        verify_file_name)

        # All the version directories of the executor results

        results_root = os.path.join(self.file_base,
                                   self.options.output_path,
                                   exec,
                                   '*'
                                  )
        version_result_directories = glob.glob(results_root)

        # Create a report plan for each version found for this executor.
        for result_version_path in version_result_directories:
          result_version = os.path.basename(result_version_path)

          # Where the results are, under the exec path.
          result_path = os.path.join(self.file_base,
                                     self.options.output_path,
                                     exec,
                                     result_version,
                                     self.testData.testDataFilename)

          # Where the HTML and JSON reports are created
          report_directory = os.path.join(
            self.file_base,
            self.options.report_path,
            exec,
            result_version)

          report_path = os.path.join(report_directory, self.testData.testDataFilename)

          # Make file.html, removing the .json part
          report_html_name = self.testData.testDataFilename.rpartition('.')[0] + '.html'
          report_html_path = os.path.join(
              self.file_base,
              self.options.report_path,
              exec,
              result_version,
              report_html_name)

          # Set the name of the verification file. These files are
          # usually in the same directory as the test data files.
          verify_file_path = os.path.join(self.file_base,
                                          self.options.input_path,
                                          verify_file_name)

          # The test report to use for verification summary.
          new_report = TestReport()
          new_report.report_file_path = report_path
          new_report.report_directory = os.path.dirname(report_path)

          new_report.report_html_path = report_html_path

          # The verify plan for this
          new_verify_plan = VerifyPlan(
              testdata_path, result_path, verify_file_path, report_path, result_version,
          )
          new_verify_plan.setTestType(test_type)
          new_verify_plan.setExec(exec)
          new_verify_plan.setReport(new_report)

          self.verify_plans.append(new_verify_plan)

  def verifyDataResults(self):
    # For each pair of files in the test plan, compare with expected
    for vplan in self.verify_plans:
      self.result_path = vplan.result_path
      self.verify_path = vplan.verify_path
      self.report_path = vplan.report_path
      self.testdata_path = vplan.testdata_path
      self.report = vplan.report_json
      self.exec = vplan.exec

      self.test_type = vplan.test_type

      if not self.openVerifyFiles():
        continue
      self.compareTestToExpected()

      # Save the results
      if not self.report.save_report():
        print('!!! Count not save report for (%s, %s)' %
              (self.test_type, self.exec))
      else:
        self.report.create_html_report()

      # Do more analysis on the failures
      self.report.summarizeFailures()

      if self.debug > 0:
        print('\nTEST RESULTS in %s for %s. %d tests found' % (
            self.exec, self.test_type, len(self.results)))
        try:
          print('     Platform: %s' % self.resultData["platform"])
          print('     %d Errors running tests' % (self.report.error_count))
        except BaseException as err:
          sys.stderr.write('### Missing fields %s, Error = %s' % (self.resultData, err))

      # Experimental
      # TODO: Finish difference analysis
      # self.report.create_html_diff_report()

  def getResultsAndVerifyData(self):
    # Get the JSON data for results
    try:
      self.resultData = json.loads(self.result_file.read())
      self.results = self.resultData['tests']
    except BaseException as err:
      sys.stderr.write('Cannot load %s result data: %s' % (self.result_path, err))
      return None

    if self.debug >= 1:
      print('^^^ Result file has %d entries' % (len(self.results)))
    self.result_file.close()

    try:
      self.verifyData = json.loads(self.verify_data_file.read())
      self.verifyExpected = self.verifyData['verifications']
    except BaseException as err:
      sys.stderr.write('Cannot load %s verify data: %s' % (self.verify_path, err))
      return None
    self.verify_data_file.close()

    # Create dictionary of expected with labels as keys
    self.verifyExpectedDict = {}
    for item in self.verifyExpected:
      self.verifyExpectedDict[item['label']] = item

    # Build dictionary of input data with labels as keys
    try:
      self.testdata = json.loads(self.testdata_file.read())
    except BaseException as err:
      sys.stderr.write('!!!!!!!!!!!!! Cannot load %s test input data: %s' % (self.testdata_path, err))
      return None
    self.testdata_file.close()

    self.testdataDict = {}
    for item in self.testdata['tests']:
      self.testdataDict[item['label']] = item

    # Sort results and verify data by the label
    try:
      self.results.sort(key=lambda x: x['label'])
    except BaseException as err:
      sys.stderr.write('!!! Cannot sort test results by label: %s' % err)
      sys.stderr.flush()

    if 'platform_error' in self.resultData:
      print('PLATFORM ERROR: %s' % self.resultData['platform error'])
      print('No verify done!!!')
      return None

  def compareTestToExpected(self):
    self.getResultsAndVerifyData()

    self.report.test_environment = self.resultData['test_environment']
    try:
      self.report.platform_info = self.resultData['platform']
    except:
      self.report.platform_info = self.report.test_environment['test_language']

    self.report.exec = self.report.test_environment['test_language']
    self.report.test_type = self.test_type
    if not self.verifyExpected:
      sys.stderr.write('No expected data in %s' % self.verify_path)
      return None

    if not self.results:
      print('*$*$*$*$* self.results = %s' % self.results)
      return None

    # Loop over all results found, comparing with the expected result.
    index = 0
    total_results = len(self.results)
    self.report.number_tests = total_results
    self.report.timestamp = self.result_timestamp  # When result was modified

    for test in self.results:
      if not test:
        print('@@@@@ no test string: %s of %s' % (test, len(self.results)))

      if index % 10000 == 0:
        print('  progress = %d / %s' % (index, total_results), end='\r')

      # The input to the test
      test_label = test['label']
      test_data = self.findTestdataWithLabel(test_label)

      # Get the result
      try:
        actual_result = test['result']
      except:
        # Add input information to the test results
        test['input_data'] = test_data
        if test.get('unsupported'):
          self.report.record_unsupported(test)
        else:
          self.report.record_test_error(test)
        continue

      verification_data = self.findExpectedWithLabel(test_label)

      if not verification_data:
        print('*** Cannot find verify data with label %s' % test_label)
        self.report.record_missing_verify_data(test)
        # Bail on this test
        continue

      expected_result = verification_data['verify']
      if self.debug > 1:
        print('VVVVV: %s actual %s, expected %s' % (
            (actual_result == expected_result),
            actual_result, expected_result))
      if actual_result == expected_result:
        self.report.record_pass(test)
      else:
        # Add expected value to the report
        test['expected'] = expected_result
        self.report.record_fail(test)
        test['input_data'] = test_data
      index += 1

    print('')
    return

  def findExpectedWithLabel(self, test_label):
    # Look for test_label in the expected data
    # Very inefficient - use Binary Search on sorted labels.
    if not self.verifyExpected:
      return None

# Use Dictionary based on label
    try:
      return self.verifyExpectedDict[test_label]
    except BaseException as err:
      print('----- findExpectedWithLabel %s' % err)
      print('  No item with test_label = %s' % test_label)
    return True

  def findTestdataWithLabel(self, test_label):
    # Look for test_label in the expected data
    if not self.testData:
      return None

    # Use Dictionary based on label
    try:
      return self.testdataDict[test_label]
    except BaseException as err:
      print('----- findTestdataWithLabel %s' % err)
      print('  No item with test_label = %s' % test_label)

    return True

  def analyzeFailures(self):
    # Analyze the test failures for types of mistakes, missing data, etc.?
    # !!! TODO: something
    return

  def setupPaths(self, executor, testfile, verifyfile):
    baseDir = self.file_base
    if self.debug > 1:
      print('&&& FILE BASE = %s' % baseDir)
      self.resultPath = os.path.join(
          baseDir, 'testResults', executor, testfile)
      self.verifyPath = os.path.join(
          baseDir, 'testData', verifyfile)
      self.reportPath = os.path.join(
          baseDir, 'testReports', executor, testfile)
    if self.debug > 0:
      print('RESULT PATH = %s' % self.resultPath)
      print('VERIFY PATH = %s' % self.verifyPath)
      print('TESTDATA PATH = %s' % self.testdata_path)

  # Create HTML summary files
  def createSummaryReports(self):
    if not self.file_base:
      return None

    # The following gets information from all the tests
    summaryReport = SummaryReport(self.file_base)
    summaryReport.setupAllTestResults()

    # And make the output HTML results
    result = summaryReport.createSummaryHtml()
    if result == None:
      print('!!!!!! SUMMARY HTML fails')


class VerifyPlan():
# Details of a verification plan
  def __init__(self,
               testdata_path, result_path, verify_path, report_path, report_version):
    self.testdata_path = testdata_path
    self.result_path = result_path
    self.verify_path = verify_path
    self.report_path = report_path
    self.report_directory = os.path.dirname(report_path)
    self.report_version = report_version
    self.exec = None
    self.test_type = None

    # The generated data
    self.report_json = None

  def setExec(self, executor):
    self.exec = executor

  def setTestType(self, test_type):
    self.test_type = test_type

  def setReport(self, new_report):
    self.report_json = new_report


class Tester():
  def __init__(self, title=None):
    self.title = title
    self.test_type = None
    self.verifier = None

  def setupPathsAndRun(self, executor, testfile, verifyfile):
    baseDir = '.'
    self.resultPath = os.path.join(baseDir, 'testResults', executor, testfile)
    self.verifyPath = os.path.join(baseDir, 'testData', verifyfile)
    self.reportPath = os.path.join(baseDir, 'testReports', executor, testfile)

    result = self.openVerifyFiles()

    self.printResult()

    return result

  def collationExec(self, executor):
    # Set up paths and run verify
    self.title = executor.upper() + ' COLL_SHIFT_SHORT'
    self.test_type = 'coll_shift_short'
    result = self.setupPathsAndRun(
        executor, 'coll_test_shift.json', 'coll_verify_shift.json')

  def decimalFmtExec(self, executor):
    self.title = executor.upper() + ' DECIMAL_FMT'
    self.test_type = 'decimal_fmt'
    result = self.setupPathsAndRun(
        executor, 'dcml_fmt_test_file.json', 'dcml_fmt_verify.json')

  def displayNamesExec(self, executor):
    self.title = executor.upper() + ' DISPLAY_NAMES'
    self.test_type = 'display_names'
    result = self.setupPathsAndRun(
        executor, 'display_names.json', 'display_names_verify.json')

  def printResult(self):
    print('\n  Test Report for %s' % self.title)
    testReport = self.verifier.report
    reportData = testReport.createReport()
    print('  Report: %s' % reportData)


# Test basic verifier functions
def runVerifierTests(verifier):
  execs = ['node', 'rust']

  for executor in execs:
    testerCollNode = Tester()
    testerCollNode.collationExec(executor)

    testerDecimalFmt = Tester()
    testerDecimalFmt.decimalFmtExec(executor)

    testerDisplayNames = Tester()
    testerDisplayNames.displayNamesExec(executor)

# For testing
def main(args):

  verifier = Verifier()
  verifier.parseArgs(args[1:])

  if verifier.options.test_verifier:
    # Simply run tests on the verify. No real data
    runVerifierTests(verifier)
    return

  if not verifier.options.summary_only:
    # Run the tests on the provided parameters.
    print('Verifier starting on %d verify cases' %(len(verifier.verify_plans)))
    verifier.verifyDataResults()
    print('Verifier completed %d data reports' %(len(verifier.verify_plans)))

  # TODO: Should this be optional?
  verifier.createSummaryReports()
  print('Verifier completed summary report')


if __name__ == '__main__':
  main(sys.argv)
