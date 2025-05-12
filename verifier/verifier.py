# Verifier class for checking actual test output vs. expectations

import datetime
import glob
import logging
import logging.config
import multiprocessing as mp
import os
import shutil
import sys

from testreport import SummaryReport
from testreport import CompareReport

from testreport import TestReport
from verify_plan import VerifyPlan

sys.path.append('../testdriver')
import datasets as ddt_data
from ddtargs import VerifyArgs

# Global constants
VERIFIER_REPORT_NAME = 'verifier_test_report.json'


class Verifier:
    def __init__(self):
        # Argument settings
        self.options = None

        # TODO: Clean up unused vars.
        self.test_type = None
        self.input_file_names = None
        self.file_base = None
        self.testdata_file = None
        self.report_file = None
        self.report_file_name = 'testReports'
        self.resultPath = None
        self.results = None

        self.verify_data_file = None
        self.verifyData = None
        self.verifyPath = None

        self.exec = None
        self.testdata_path = None
        self.debug = 0  # Different levels

        self.report = None
        self.reports = []

        self.run_in_parallel = True

        # Set of [result filepath, verify filepath, report path]
        self.result_timestamp = None

        # All the items that will be verified
        self.verify_plans = []

        # Filename used for the json version of verifier output
        self.report_filename = VERIFIER_REPORT_NAME

        logging.config.fileConfig("../logging.conf")

        logger = logging.Logger("VERIFIER LOGGER")
        logger.setLevel(logging.WARNING)

    def open_verify_files(self, vplan):
        # Get test data, verify data, and results for a case.
        try:
            vplan.result_file = open(vplan.result_path, encoding='utf-8', mode='r')
            file_time = os.path.getmtime(vplan.result_path)
            vplan.result_time_stamp = datetime.datetime.fromtimestamp(file_time).strftime('%Y-%m-%d %H:%M')
            vplan.report.timestamp = vplan.result_time_stamp
        except BaseException as err:
            logging.error('    *** CANNOT OPEN RESULTS FILE %s:\n        %s', vplan.result_path, err)
            return None

        try:
           vplan.verify_data_file = open(vplan.verify_path, encoding='utf-8', mode='r')
        except BaseException as err:
            logging.error('    **!!* %s: Cannot open verify file %s', err, vplan.verify_path)
            return None

        # Create report directory if needed
        report_dir = os.path.dirname(vplan.report_path)
        try:
            if not os.path.isdir(report_dir):
                os.makedirs(report_dir, exist_ok=True)
        except BaseException as err:
            logging.error('    !!! Cannot create directory %s for report file %s',
                             report_dir, vplan.report_path)
            logging.error('   !!! Error = %s', err)

            return None

        try:
            vplan.report_file = self.report_file = open(vplan.report_path, encoding='utf-8', mode='w')
        except BaseException as err:
            logging.error('*** Cannot open file %s: Error = %s', vplan.report_path, err)
            return None

        # Get the input file to explain test failures
        try:
            self.testdata_file = open(vplan.testdata_path, encoding='utf-8', mode='r')
        except BaseException as err:
            logging.error('*** Cannot open testdata file %s: Error = %s', vplan.testdata_path, err)
            return None

        # Initialize values for this case.
        self.results = None
        return True  # Indicates that data

    def set_verify_args(self, args):
        # Initialize commandline arguments
        self.options = VerifyArgs(args).getOptions()

        self.test_types = self.options.test_type

        # Create a set of verifications based on exec and test_type
        self.input_file_names = self.options.input_path

        self.file_base = self.options.file_base

    def setup_verify_plans(self):
        # Set of plans reading data and verifying result file vs. verify file
        if self.options.summary_only:
            return

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

        # Generate a plan for each executor, test_type, and icu_version
        for executor in executor_list:
            for test_type in test_list:

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
                                               self.report_filename)

                    # Make name for html detail file with standard name
                    report_html_path = os.path.join(
                        report_directory, self.report_filename.replace('.json', '.html'))

                    # Test report for verification
                    new_report = TestReport(report_path, report_html_path)
                    new_report.verifier_obj = self
                    new_report.set_title(executor, result_version, test_type)

                    # The verify plan for this
                    new_verify_plan = VerifyPlan(
                        testdata_path,
                        result_path,
                        verify_file_path,
                        report_path,
                        result_version
                    )
                    # Values needed by the plan
                    new_verify_plan.verifier_obj = self
                    new_verify_plan.set_test_type(test_type)
                    new_verify_plan.set_exec(executor)
                    new_verify_plan.set_report(new_report)

                    # Is this test needed?
                    if os.path.isfile(new_verify_plan.result_path):
                        self.verify_plans.append(new_verify_plan)
                    else:
                        logging.debug('** No results for %s, %s, %s',
                                      executor, test_type, result_version)

    # Verify plans in parallel
    def parallel_verify_data_results(self):
        if not self.options.run_serial:
            num_processors = mp.cpu_count()
            verify_plans = self.verify_plans
            logging.info('JSON validation: %s processors for %s plans',
                         num_processors, len(verify_plans))

            processor_pool = mp.Pool(num_processors)
            with processor_pool as p:
                result = p.map(self.verify_one_plan, verify_plans)
            return result
        else:
            logging.info('Running serially!')
            for vplan in self.verify_plans:
                self.verify_one_plan(vplan)

    # For one VerifyPlan, get data and run verification
    def verify_one_plan(self, vplan):
        result = {}

        # Read data
        if not vplan.read_verify_files():
            # Problems getting input data
            logging.warning('Cannot get data %s or %s',
                            vplan.result_path,
                            vplan.verify_path)
            return None

        # This fills in values of the report
        vplan.compare_test_to_expected()
        vplan.setup_report_data()

        result = {'compare_success': True}

        # Do more analysis on the failures and compute known issues
        vplan.report.summarize_failures()

        vplan.report.add_known_issues()
        # Save the results

        if not vplan.report.save_report():
            logging.error('!!! Could not save report for (%s, %s)',
                          vplan.test_type, vplan.exec)
        else:
            vplan.report.create_html_report()

        logging.debug('\nTEST RESULTS in %s for %s. %d tests found',
                          vplan.exec, vplan.test_type, len(vplan.test_results))

        return result

    def analyze_failures(self):
        # Analyze the test failures for types of mistakes, missing data, etc.?
        # !!! TODO: something
        return

    def setup_paths(self, executor, testfile, verify_file):
        base_dir = self.file_base
        if self.debug > 1:
            logging.debug('&&& FILE BASE = %s', base_dir)
            # Check on the path defined here
            test_output_dir = 'testOutput'
            self.resultPath = os.path.join(
                base_dir, test_output_dir, executor, testfile)
            self.verifyPath = os.path.join(
                base_dir, 'testData', verify_file)

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

        # Create compare html for each test type
        for test_type in self.test_types:
            logging.info('Creating compare for %s', test_type)
            compare_report = CompareReport(self.file_base, test_type)
            # TODO!!!! Finish

            json_files = compare_report.get_json_files()

            compare_report.create_report()

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
            validation_copy = os.path.join(self.file_base, self.report_file_name, test_output_validation_name)
            try:
                shutil.copyfile(test_output_validation, validation_copy)
            except BaseException as error:
                logging.warning('%s. Cannot copy schema validation file from %s to %s',
                                error, test_output_validation, validation_copy)

        return [schema_validation_name, generated_data_validation_name, test_output_validation_name]

    def copy_js_files(self):
        # Create a copy of locale .js files to the report area for including in reports
        files_to_copy = ['diff_match_patch.js']
        output_dir = os.path.join(self.file_base, self.report_file_name)

        for js_file in files_to_copy:
            destination = os.path.join(self.file_base, self.report_file_name, js_file)
            result = shutil.copy2(js_file, destination)


# Test basic verifier functions
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
        self.title = executor.upper() + ' COLLATION'
        self.test_type = 'collation'
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


def run_verifier_tests():
    execs = ['node', 'rust']

    for executor in execs:
        tester_coll_node = Tester()
        tester_coll_node.collation_exec(executor)

        tester_decimal_fmt = Tester()
        tester_decimal_fmt.decimal_format_exec(executor)

        tester_display_names = Tester()
        tester_display_names.display_names_exec(executor)


# For running verifications of test output vs. expected values.
def main(args):
    # Initialize verifier using commandline args
    verifier = Verifier()

    verifier.set_verify_args(args[1:])

    if verifier.options.test_verifier:
        # Simply run tests on the verifier. No real data
        run_verifier_tests()
        return

    # Create verify plan for each verification
    verifier.setup_verify_plans()

    if not verifier.options.summary_only:
        # Run the tests on the provided parameters.
        logging.info('Verifier starting on %d verify cases',
                     len(verifier.verify_plans))

        # Use multiprocessing on verification
        verifier.parallel_verify_data_results()

        logging.info('Verifier completed %d data reports',
                     len(verifier.verify_plans))

    # TODO: Should this be optional?
    verifier.create_summary_reports()
    logging.info('Verifier completed summary report')

    # Copy any other files such as JavaScript to the report area
    verifier.copy_js_files()


if __name__ == '__main__':
    main(sys.argv)
