# Verifier class for checking actual test output vs. expectations

import datetime
import glob
import json
import logging
import logging.config
import os
import shutil
import sys

from testreport import TestReport
from testreport import SummaryReport

sys.path.append('../testdriver')
import datasets as ddt_data
from ddtargs import VerifyArgs

# Global constants
VERIFIER_REPORT_NAME = 'verifier_test_report.json'


class Verifier:
    def __init__(self):
        self.testdataDict = None
        self.verifyExpectedDict = None
        self.verifyExpected = None
        self.test_type = None
        self.report_path = None
        self.verify_path = None
        self.result_path = None
        self.testData = None
        self.testdata = None
        self.test_types = None
        self.input_file_names = None
        self.file_base = None
        self.testdata_file = None
        self.expected = None
        self.report_file = None
        self.verify_data_file = None
        self.report_file_name = 'testReports'
        self.result_file = None
        self.reportPath = None
        self.verifyPath = None
        self.resultPath = None
        self.results = None
        self.verifyData = None
        self.resultData = None
        self.exec = None
        self.testdata_path = None
        self.debug = 0  # Different levels

        self.report = None
        self.reports = []

        self.options = None
        # Set of [result filepath, verify filepath, report path]
        self.result_timestamp = None

        # All the items that will be verified
        self.verify_plans = []

        # Filename used for the json version of verifier output
        self.report_filename = VERIFIER_REPORT_NAME

        logging.config.fileConfig("../logging.conf")

    def open_verify_files(self):
        # Get test data, verify data, and results for a case.
        try:
            self.result_file = open(self.result_path, encoding='utf-8', mode='r')
            file_time = os.path.getmtime(self.result_path)
            self.result_timestamp = datetime.datetime.fromtimestamp(file_time).strftime('%Y-%m-%d %H:%M')
        except BaseException as err:
            logging.error('    *** Cannot open results file %s:\n        %s', self.result_path, err)
            return None

        try:
            self.verify_data_file = open(self.verify_path, encoding='utf-8', mode='r')
        except BaseException as err:
            logging.error('    **!!* %s: Cannot open verify file %s', err, self.verify_path)
            return None

        # Create report directory if needed
        report_dir = os.path.dirname(self.report_path)
        try:
            if not os.path.isdir(report_dir):
                os.makedirs(report_dir)
        except BaseException as err:
            sys.stderr.write('    !!! Cannot create directory %s for report file %s' %
                             (report_dir, self.report_path))
            sys.stderr.write('   !!! Error = %s' % err)

            logging.error('    !!! Cannot create directory %s for report file %s',
                             report_dir, self.report_path)
            logging.error('   !!! Error = %s', err)
            
            return None

        try:
            self.report_file = open(self.report_path, encoding='utf-8', mode='w')
        except BaseException as err:
            print('*** Cannot open file %s: Error = %s' % (self.report_path, err))
            logging.error('*** Cannot open file %s: Error = %s', self.report_path, err)
            return None

        # Get the input file to explain test failures
        try:
            self.testdata_file = open(self.testdata_path, encoding='utf-8', mode='r')
        except BaseException as err:
            print('*** Cannot open testdata file %s: Error = %s' % (self.testdata_path, err))
            logging.error('*** Cannot open testdata file %s: Error = %s', self.testdata_path, err)
            return None

        # Initialize values for this case.
        self.results = None
        self.expected = None
        self.testdata = None
        return True  # Indicates that data

    def parseargs(self, args):
        # Initialize commandline arguments
        verify_info = VerifyArgs(args)
        if self.debug > 1:
            logging.debug('!!! ARGS = %s', args)
            logging.debug('VERIFY INFO: %s', verify_info)
        self.set_verify_args(verify_info.getOptions())

    def set_verify_args(self, arg_options):
        self.options = arg_options
        self.test_types = arg_options.test_type
        # Create a set of verifications based on exec and test_type

        self.input_file_names = arg_options.input_path

        self.file_base = arg_options.file_base
        if self.debug > 1:
            logging.debug('TEST TYPES = %s', self.test_types)

        if not arg_options.summary_only:
            self.setup_verify_plans()

    def setup_verify_plans(self):
        # Set of [result file, verify file]

        if self.options.verify_all:
            # Generates exec and test lists from the existing files in
            # testResults directories
            summary_report = SummaryReport(self.file_base)
            summary_report.summarize_reports()
            executor_list = summary_report.exec_summary.keys()
            test_list = summary_report.type_summary.keys()
        else:
            executor_list = self.options.exec
            test_list = self.options.test_type

        for executor in executor_list:
            for test_type in test_list:

                # TODO: Run for each test_type!
                if test_type not in ddt_data.testDatasets:
                    logging.warning('**** WARNING: test_type %s not in testDatasets',
                          test_type)
                    raise ValueError('No test dataset found for test type >%s<' %
                                     self.test_type)
                else:
                    # Create a test plan based on data and options
                    self.testData = ddt_data.testDatasets[test_type]

                verify_file_name = ddt_data.testDatasets[test_type].verifyFilename

                # All the version directories of the executor results
                results_root = os.path.join(self.file_base,
                                            self.options.output_path,
                                            executor,
                                            '*'
                                            )
                # All the result directories for this executor.
                version_result_directories = glob.glob(results_root)

                # Create a report plan for each version found for this executor.
                for result_version_path in version_result_directories:
                    result_version = os.path.basename(result_version_path)

                    # Get the ICU version and compute the location of the verify data
                    # Set the name of the verification file. These files are
                    # usually in the same directory as the test data files.
                    test_version = os.path.basename(result_version)
                    verify_file_path = os.path.join(self.file_base,
                                                    self.options.input_path,
                                                    test_version,
                                                    verify_file_name)

                    testdata_path = os.path.join(self.file_base,
                                                 self.options.input_path,
                                                 test_version,
                                                 self.testData.testDataFilename)

                    # Where the results are, under the exec path.
                    result_path = os.path.join(result_version_path,
                                               self.testData.testDataFilename)

                    # Where the HTML and JSON reports are created
                    report_directory = os.path.join(
                        self.file_base,
                        self.options.report_path,
                        executor, result_version, test_type)

                    report_path = os.path.join(report_directory,
                                               self.report_filename)  # self.testData.testDataFilename)

                    # Make name for html detail file with standard name
                    report_html_path = os.path.join(
                        report_directory, self.report_filename.replace('.json', '.html'))

                    # The test report to use for verification summary.
                    new_report = TestReport(report_path, report_html_path)
                    new_report.verifier_obj = self
                    new_report.set_title(executor, result_version, test_type)

                    # The verify plan for this
                    new_verify_plan = VerifyPlan(
                        testdata_path, result_path, verify_file_path, report_path, result_version,
                    )
                    new_verify_plan.verifier_obj = self
                    new_verify_plan.set_test_type(test_type)
                    new_verify_plan.set_exec(executor)
                    new_verify_plan.set_report(new_report)

                    if os.path.isfile(new_verify_plan.result_path):
                        self.verify_plans.append(new_verify_plan)
                    else:
                        logging.warning('** No results for %s, %s, %s', executor, test_type, result_version)

    def verify_data_results(self):
        # For each pair of files in the test plan, compare with expected
        for vplan in self.verify_plans:
            self.result_path = vplan.result_path
            self.verify_path = vplan.verify_path

            self.report_path = vplan.report_path
            self.testdata_path = vplan.testdata_path
            self.report = vplan.report_json
            self.exec = vplan.exec
            # GET FROM DATA
            if vplan.exec == 'rust':
                self.library_name = 'ICU4X'
            else:
                self.library_name = self.exec

            self.test_type = vplan.test_type

            logging.info('VERIFY %s: %s %s', vplan.exec, self.test_type, vplan.result_path)
            if not self.open_verify_files():
                continue
            self.compare_test_to_expected()

            # Save the results
            if not self.report.save_report():
                logging.error('!!! Could not save report for (%s, %s)',
                      vplan.test_type, self.exec)
            else:
                self.report.create_html_report()

            # Do more analysis on the failures
            self.report.summarize_failures()

            if self.debug > 0:
                logging.debug('\nTEST RESULTS in %s for %s. %d tests found', 
                    self.exec, vplan.test_type, len(self.results))
                try:
                    logging.info('     Platform: %s', self.resultData["platform"])
                    logging.info('     %d Errors running tests', self.report.error_count)
                except BaseException as err:
                    sys.stderr.write('### Missing fields %s, Error = %s' % (self.resultData, err))
                    logging.error('### Missing fields %s, Error = %s', self.resultData, err)

            # Experimental
            # TODO: Finish difference analysis
            # self.report.create_html_diff_report()

    def get_results_and_verify_data(self):
        # Get the JSON data for results
        try:
            self.resultData = json.loads(self.result_file.read())
            self.results = self.resultData['tests']
        except BaseException as err:
            sys.stderr.write('Cannot load %s result data: %s' % (self.result_path, err))
            logging.error('Cannot load %s result data: %s',  self.result_path, err)
            return None

        if self.debug >= 1:
            logging.debug('^^^ Result file has %d entries', len(self.results))
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
            logging.error('!!! Cannot sort test results by label: %s', err)

        if 'platform_error' in self.resultData:
            logging.error('PLATFORM ERROR: %s', self.resultData['platform error'])
            logging.error('No verify done!!!')
            return None

    def compare_test_to_expected(self):
        # TODO: Use vplan to get information rather than from the verifier
        self.get_results_and_verify_data()

        try:
            self.report.test_environment = self.resultData['test_environment']
        except KeyError:
            self.report.test_environment = {'test_language': self.exec}

        try:
            self.report.platform_info = self.resultData['platform']
        except KeyError:
            self.report.platform_info = self.report.test_environment['test_language']

        self.report.test_environment['platform'] = self.report.platform_info

        self.report.exec = self.report.test_environment['test_language']
        self.report.library_name = self.library_name

        self.report.test_type = self.test_type
        if not self.verifyExpected:
            sys.stderr.write('No expected data in %s' % self.verify_path)
            logging.error('No expected data in %s', self.verify_path)
            return None

        if not self.results:
            logging.error('*$*$*$*$* self.results = %s', self.results)
            return None

        # Loop over all results found, comparing with the expected result.
        index = 0
        total_results = len(self.results)
        self.report.number_tests = total_results
        self.report.timestamp = self.result_timestamp  # When result was modified

        for test in self.results:
            if not test:
                logging.debug('@@@@@ no test string: %s of %s', test, len(self.results))

            if index % 10000 == 0:
                logging.debug('  progress = %d / %s', index, total_results)

            # The input to the test
            try:
                test_label = test['label']
            except:
                test_label = ''
                logging.warning(test)

            test_data = self.find_testdata_with_label(test_label)

            # Get the result
            try:
                actual_result = test['result']
            except (AttributeError, KeyError):
                # Add input information to the test results
                test['input_data'] = test_data
                if test.get('unsupported'):
                    self.report.record_unsupported(test)
                else:
                    self.report.record_test_error(test)
                continue

            verification_data = self.find_expected_with_label(test_label)

            if verification_data is None:
                logging.warning('*** Cannot find verify data with label %s', test_label)
                self.report.record_missing_verify_data(test)
                # Bail on this test
                continue

            try:
                expected_result = verification_data['verify']
            except:
                expected_result = 'UNKNOWN'
            if self.debug > 1:
                logging.debug('VVVVV: %s actual %s, expected %s',
                    (actual_result == expected_result),
                    actual_result, expected_result)
            # Remember details about the test
            test['input_data'] = test_data
            test['expected'] = expected_result
            if actual_result == expected_result:
                self.report.record_pass(test)
            else:
                self.report.record_fail(test)

            index += 1

        return

    def find_expected_with_label(self, test_label):
        # Look for test_label in the expected data
        # Very inefficient - use Binary Search on sorted labels.
        if not self.verifyExpected:
            return None

        # Use Dictionary based on label
        try:
            return self.verifyExpectedDict[test_label]
        except BaseException as err:
            logging.error('----- find_expected_with_label %s', err)
            logging.error('  No expected item with test_label = %s', test_label)
        return True

    def find_testdata_with_label(self, test_label):
        # Look for test_label in the expected data
        if not self.testData:
            return None

        # Use Dictionary based on label
        try:
            return self.testdataDict[test_label]
        except BaseException as err:
            logging.error('----- findTestdataWithLabel %s', err)
            logging.error('  No test data item with test_label = %s', test_label)
            logging.error('  SUGGESTION: Check if test results are synced with test data!')

        return True

    def analyze_failures(self):
        # Analyze the test failures for types of mistakes, missing data, etc.?
        # !!! TODO: something
        return

    def setup_paths(self, executor, testfile, verify_file):
        base_dir = self.file_base
        if self.debug > 1:
            logging.deubg('&&& FILE BASE = %s', base_dir)
            # Check on the path defined here
            test_output_dir = 'testOutput'
            self.resultPath = os.path.join(
                base_dir, test_output_dir, executor, testfile)
            self.verifyPath = os.path.join(
                base_dir, 'testData', verify_file)
            self.reportPath = os.path.join(
                base_dir, 'testReports', executor, testfile)
        if self.debug > 0:
            logging.debug('RESULT PATH = %s', self.resultPath)
            logging.debug('VERIFY PATH = %s', self.verifyPath)
            logging.debug('TESTDATA PATH = %s', self.testdata_path)

    # Create HTML summary files
    def create_summary_reports(self):
        if not self.file_base:
            return None

        # The following gets information from all the tests
        summary_report = SummaryReport(self.file_base)
        summary_report.setup_all_test_results()

        # Get schema summary data to the testReport head
        schema_validation_list = self.schema_results()

        # And make the output HTML results
        result = summary_report.create_summary_html()
        if not result:
            logging.error('!!!!!! SUMMARY HTML fails')

    def schema_results(self):
        # Locate the files in schema, testData, and testOutput
        schema_validation_name = 'schema_validation_summary.json'
        conformance_base = os.path.dirname(self.file_base)
        schema_validation = os.path.join(conformance_base, 'schema', schema_validation_name)
        if os.path.exists(schema_validation):
            # Copy to report path
            validation_copy = os.path.join(self.file_base, self.report_file_name, schema_validation_name)
            try:
                shutil.copyfile(schema_validation, validation_copy)
            except BaseException as error:
                logging.warning('%s. Cannot copy schema validation file from %s to %s',
                                error,schema_validation, validation_copy)

        generated_data_validation_name = 'test_data_validation_summary.json'
        generated_validation = os.path.join(self.file_base, 'testData', generated_data_validation_name)
        if os.path.exists(generated_validation):
            # Copy to report path
            validation_copy = os.path.join(self.file_base, self.report_file_name, generated_data_validation_name)
            try:
                shutil.copyfile(generated_validation, validation_copy)
            except BaseException as error:
                logging.warning('%s. Cannot copy schema validation file from %s to %s',
                                error, generated_data_validation_name, validation_copy)

        test_output_validation_name = 'test_output_validation_summary.json'
        test_output_validation = os.path.join(self.file_base, 'testOutput', test_output_validation_name)
        if os.path.exists(test_output_validation):
            # Copy to report path
            # Copy to report path
            validation_copy = os.path.join(self.file_base, self.report_file_name, test_output_validation_name)
            try:
                shutil.copyfile(test_output_validation, validation_copy)
            except BaseException as error:
                logging.warning('%s. Cannot copy schema validation file from %s to %s',
                                error, test_output_validation, validation_copy)

        return [schema_validation_name, generated_data_validation_name, test_output_validation_name]

class VerifyPlan:
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

        self.verifier_obj = None  # TODO: Can I get this from the caller?

        # The generated data
        self.report_json = None

    def set_exec(self, executor):
        self.exec = executor

    def set_test_type(self, test_type):
        self.test_type = test_type

    def set_report(self, new_report):
        self.report_json = new_report


class Tester:
    def __init__(self, title=None):
        self.reportPath = None
        self.verifyPath = None
        self.resultPath = None
        self.title = title
        self.test_type = None
        self.verifier = None

    def setup_paths_and_run(self, executor, testfile, verify_file):
        base_dir = '.'
        results_dir = 'testOutput'
        self.resultPath = os.path.join(base_dir, results_dir, executor, testfile)
        self.verifyPath = os.path.join(base_dir, 'testData', verify_file)
        self.reportPath = os.path.join(base_dir, 'testReports', executor, testfile)

        result = self.verifier.open_verify_files()

        self.print_result()

        return result

    def collation_exec(self, executor):
        # Set up paths and run verify
        self.title = executor.upper() + ' COLLATION_SHORT'
        self.test_type = 'collation_short'
        self.setup_paths_and_run(
            executor, 'coll_test_shift.json', 'collation_verify.json')

    def decimal_format_exec(self, executor):
        self.title = executor.upper() + ' DECIMAL_FMT'
        self.test_type = 'decimal_fmt'
        self.setup_paths_and_run(
            executor, 'dcml_fmt_test_file.json', 'dcml_fmt_verify.json')

    def display_names_exec(self, executor):
        self.title = executor.upper() + ' DISPLAY_NAMES'
        self.test_type = 'display_names'
        self.setup_paths_and_run(
            executor, 'display_names.json', 'display_names_verify.json')

    def print_result(self):
        logging.info('\n  Test Report for %s', self.title)
        test_report = self.verifier.report
        report_data = test_report.create_report()
        logging.info('  Report: %s', report_data)


# Test basic verifier functions
def run_verifier_tests():
    execs = ['node', 'rust']

    for executor in execs:
        tester_coll_node = Tester()
        tester_coll_node.collation_exec(executor)

        tester_decimal_fmt = Tester()
        tester_decimal_fmt.decimal_format_exec(executor)

        tester_display_names = Tester()
        tester_display_names.display_names_exec(executor)


# For testing
def main(args):
    verifier = Verifier()
    verifier.parseargs(args[1:])

    if verifier.options.test_verifier:
        # Simply run tests on the verifier. No real data
        run_verifier_tests()
        return

    if not verifier.options.summary_only:
        # Run the tests on the provided parameters.
        logging.info('Verifier starting on %d verify cases', len(verifier.verify_plans))
        verifier.verify_data_results()
        logging.info('Verifier completed %d data reports', len(verifier.verify_plans))

    # TODO: Should this be optional?
    verifier.create_summary_reports()
    logging.info('Verifier completed summary report')


if __name__ == '__main__':
    main(sys.argv)
