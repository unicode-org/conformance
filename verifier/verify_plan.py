#
# Verifier class for checking actual test output vs. expectations

import datetime
import glob
import json
import logging
import logging.config
import multiprocessing as mp
import os
import shutil
import sys

class VerifyPlan:
    # Details of a verification plan.
    def __init__(self,
                 testdata_path, result_path, verify_path, report_path, report_version):
        self.testdata_path = testdata_path

        self.result_path = result_path
        self.result_time_stamp = None
        self.testdataDict = {}

        self.verify_path = verify_path
        self.verifyExpectedDict = {}

        self.report_path = report_path

        self.report = None
        self.report_file = None

        self.exec = None
        self.test_type = None

        # Is this actually useful?
        self.verifier_obj = None

        # The generated data
        self.report_json = None

        # Same as executor unless overridden
        self.library_name = None

    def read_verify_files(self):
        # Get test data, verify data, and results for this verify plan.

        # First, get the test output.
        try:
            with open(self.result_path,
                      encoding='utf-8', mode='r') as result_file:
                file_time = os.path.getmtime(self.result_path)
                self.result_time_stamp = datetime.datetime.fromtimestamp(
                    file_time).strftime('%Y-%m-%d %H:%M')
                self.report.timestamp = self.result_time_stamp
                self.resultData = json.loads(result_file.read())
                self.test_results = self.resultData['tests']
        except BaseException as err:
            logging.error('*** Cannot use results file %s:\n        %s',
                          self.result_path, err)
            return None

        # Next, get the verification data.
        try:
            with open(self.verify_path,
                      encoding='utf-8', mode='r') as verify_data_file:
                self.verifyData = json.loads(verify_data_file.read())
                self.verifyExpected = self.verifyData['verifications']
        except KeyError as err:
            logging.error('Cannot load %s verify data: %s',
                          self.verify_path, err)
            return None

        # Create report output directory path if needed
        report_dir = os.path.dirname(self.report_path)
        try:
            if not os.path.isdir(report_dir):
                os.makedirs(report_dir)
        except BaseException as err:
            logging.error('    !!! Cannot create directory %s for report file %s',
                          report_dir, self.report_path)
            logging.error('   !!! Error = %s', err)
            return None


        # Get the input file to explain test failures
        try:
            with open(self.testdata_path,
                      encoding='utf-8', mode='r') as testdata_file:
                self.testdata = json.loads(testdata_file.read())
        except BaseException as err:
            logging.error('*** Cannot open testdata file %s: Error = %s',
                          self.testdata_path, err)
            return None

        # Initialize values for this case.
        self.expected = None

        # TODO: !!! open report file in the report object
        try:
            self.report_file = open(self.report_path,
                                    encoding='utf-8', mode='w')
        except BaseException as err:
            logging.error('*** Cannot open file %s: Error = %s',
                          self.report_path, err)
            return None

        # Put data into dictionaries for quick access
        self.create_result_expected_dictionaries()

        return True  # Indicates that data reading was successful

    def create_result_expected_dictionaries(self):
        for item in self.testdata['tests']:
            self.testdataDict[item['label']] = item

        for item in self.verifyExpected:
            self.verifyExpectedDict[item['label']] = item

        return

    def set_exec(self, executor):
        self.exec = executor
        # Manual adjustment
        if self.exec == 'rust':
            self.library_name = 'ICU4X'
        else:
            self.library_name = self.exec


    def set_test_type(self, test_type):
        self.test_type = test_type

    def set_report(self, new_report):
        self.report = new_report
        # NEEDED???
        self.report_json = new_report

    def compare_test_to_expected(self):
        if not self.verifyExpected:
            sys.stderr.write('No expected data in %s' % self.verify_path)
            logging.error('No expected data in %s', self.verify_path)
            return None

        if not self.test_results:
            logging.error('*$*$*$*$* self.test_results = %s', self.test_results)
            return None

        if self.report:
            self.report.number_tests = len(self.test_results)

        # Loop over all test results, comparing with the expected value.
        index = 0
        total_results = len(self.test_results)
        for test in self.test_results:
            if not test:
                logging.debug('@@@@@ no test string: %s of %s', test, ltotal_results)

            if index % 10000 == 0:
                logging.debug('  progress = %d / %s', index, total_results)

            # The input to the test
            try:
                test_label = test['label']
            except:
                test_label = ''
                logging.warning('Unlabeled test: %s %s', self.report_path, test)

            test_data = self.find_testdata_with_label(test_label)

            # Get the result
            try:
                actual_result = test['result']

                verification_data = self.find_expected_with_label(test_label)

                if verification_data is None:
                    logging.warning('*** Cannot find verify data with label %s', test_label)
                    self.report.record_missing_verify_data(test)
                    # Bail on this test
                    continue

                # TODO: Verify data must always have 'verify' field - check with schema
                try:
                    expected_result = verification_data['verify']
                except BaseException:
                    expected_result = 'UNKNOWN'

                # Remember details about the test
                test['input_data'] = test_data
                test['expected'] = expected_result
                if actual_result == expected_result:
                    self.report.record_pass(test)
                else:
                    self.report.record_fail(test)

            except (AttributeError, KeyError):
                # Add input information to the test results
                test['input_data'] = test_data
                if test.get('unsupported'):
                    self.report.record_unsupported(test)
                else:
                    self.report.record_test_error(test)
                continue

            index += 1

        return

    def find_testdata_with_label(self, test_label):
        # Look for test_label in the expected data
        if not self.testdataDict:
            return None

        # Use Dictionary based on label
        try:
            return self.testdataDict[test_label]
        except BaseException as err:
            logging.error('----- findTestdataWithLabel %s', err)
            logging.error('  No test data item with test_label = %s', test_label)
            logging.error('  SUGGESTION: Check if test results are synced with test data!')

        return None

    def find_expected_with_label(self, test_label):
        # Look for test_label in the expected data
        # Very inefficient - use Binary Search on sorted labels.
        if not self.verifyExpectedDict:
            return None

        # Use Dictionary based on label
        try:
            return self.verifyExpectedDict[test_label]
        except BaseException as err:
            logging.error('----- find_expected_with_label %s', err)
            logging.error('  No expected item with test_label = %s', test_label)
        return None

    def setup_report_data(self):
        this_report = self.report

        this_report.number_tests = len(self.test_results)
        try:
            this_report.test_environment = self.resultData['test_environment']
        except KeyError:
            this_report.test_environment = {'test_language': self.exec}

        try:
            this_report.platform_info = self.resultData['platform']
        except KeyError:
            this_report.platform_info = self.report.test_environment['test_language']

        this_report.test_environment['platform'] = self.report.platform_info

        this_report.exec = self.report.test_environment['test_language']
        self.report.library_name = self.library_name

        this_report.test_type = self.test_type
        if not self.verifyExpected:
            sys.stderr.write('No expected data in %s' % self.verify_path)
            logging.error('No expected data in %s', self.verify_path)
            return None
