from datetime import datetime
import glob
import json
import logging
import logging.config
import os
import subprocess
import sys
import time


# Set up and execute a testing plan for DDT

class TestPlan:
    def __init__(self, exec_data, test_type, args=None):
        self.tests = None
        self.testScenario = None
        self.jsonData = None
        self.verifyFilePath = None
        self.verifyFilename = None
        self.outputFilePath = None
        self.icuVersion = None
        self.planId = None
        self.exec_data = exec_data
        self.exec_env = None
        self.exec_command = None
        self.exec_list = None
        if exec_data and 'path' in exec_data:
            self.exec_command = exec_data['path']
        if 'env' in exec_data:
            self.exec_env = exec_data['env']
        self.test_type = test_type
        self.runStyle = 'one_test'
        self.parallelMode = None
        self.options = None
        self.testData = None

        # Ignore this TestPlan. In other words, do not run
        self.ignore = None

        # Additional args to subprocess.run
        self.args = args

        self.run_error_message = None  # Set if execution
        self.test_lang = None
        self.inputFilePath = None
        self.resultsFile = None

        self.jsonOutput = {}  # Area for adding elements for the results file
        self.platformVersion = ''  # Records the executor version
        self.icu_version = None  # Requested by the test driver.
        self.run_limit = None  # Set to positive integer to activate
        self.debug = 1

        self.iteration = 0
        self.progress_interval = 1000

        self.verifier = None

        logging.config.fileConfig("../logging.conf")

    def set_options(self, options):
        self.options = options
        try:
            self.icu_version = options.icu_version
        except KeyError:
            logging.warning('NO ICU VERSION SET')

        if options.ignore and not options.ignore == "null":
            self.ignore = True

    def set_test_data(self, test_data):
        self.testData = test_data  # ???['tests']

    def set_verify_file(self, verify_filename):
        self.verifyFilename = verify_filename

    # Use the settings to run the plan, using stdout from this
    # routine as stdin for the test executor.
    # If possible, run the verifier too.
    def run_plan(self):
        # TODO: Handle list of custom test files
        if self.options.custom_testfile:
            pass

        # Check for option to set version of executor
        # TODO

        # If icu_version is "latest" or not set, get the highest numbered
        # version of the test data
        input_root = os.path.join(self.options.file_base,
                                  self.options.input_path)
        icu_test_dirs = glob.glob('icu*', root_dir=input_root)
        if not icu_test_dirs:
            raise Exception('No ICU test data found in directory %s' % input_root)

        if self.icu_version not in icu_test_dirs:
            # Test data versions are given as "icu" + primary number, e.g., "73"
            # TODO: Consider sorting with possible dotted versions, e.g., 73.1.3
            newest_version = sorted(icu_test_dirs, reverse=True)[0]
            logging.info('** Replacing proposed icu version of %s with version %s',
                         self.icu_version, newest_version)
            self.icu_version = newest_version

        if self.test_lang == 'node' and 'node_version' in self.options:
            # Set up for the version of node selected
            nvm_command = 'nvm use %s' % self.options.node_version
            # TODO: Figure out how to use nvm in a command
            # result = subprocess.run(['bash', '-c', nvm_command])

        self.inputFilePath = os.path.join(self.options.file_base,
                                          self.options.input_path,
                                          self.icu_version,
                                          self.testData.testDataFilename)

        # !!! TODO: create better lang-specific output
        output_dir = self.test_lang
        self.outputFilePath = os.path.join(self.options.file_base,
                                           self.options.output_path,
                                           self.options.icu_version,
                                           # self.platformVersion,
                                           output_dir,
                                           self.testData.testDataFilename)
        self.verifyFilePath = os.path.join(self.options.file_base,
                                           self.options.report_path,
                                           output_dir,
                                           self.testData.testDataFilename)
        if self.options.debug_level:
            self.debug = True

        if self.options.run_limit:
            self.run_limit = int(self.options.run_limit)
            if self.debug:
                logging.debug('!!! RUN LIMIT SET: %d', self.run_limit)

        if self.debug:
            logging.debug('Running plan %s on data %s',
                self.exec_command, self.inputFilePath)

        if self.options.exec_mode == 'one_test':
            self.run_one_test_mode()
        else:
            self.run_multitest_mode()
        return

    def request_executor_info(self):
        version_info = "#VERSION\n#EXIT\n"
        result = self.send_one_line(version_info)
        if result and result[0] == "#":
            # There's debug data. Take the 2nd line of this result
            result_lines = result.split('\n')
            result = result_lines[1]

        if not result:
            self.jsonOutput["platform error"] = self.run_error_message
            return None
        else:
            if self.debug:
                logging.debug('EXECUTOR INFO = %s', result)

            try:
                self.jsonOutput["platform"] = json.loads(result)
            except json.JSONDecodeError as error:
                logging.error("Encountered error in parsing executor result string as JSON: %s", error)
                logging.error("Result string received from executor: [%s]", result)
                return None

            try:
                self.platformVersion = self.jsonOutput["platform"]["platformVersion"]
                self.icuVersion = self.jsonOutput["platform"]["icuVersion"]
                try:
                    self.cldrVersion = self.jsonOutput["platform"]["cldrVersion"]
                except KeyError:
                    self.cldrVersion = 'CLDR version not specified'

                # TODO: Clean this up!
                # Get the test data area from the icu_version

                # Reset the output path based on the version.
                self.outputFilePath = os.path.join(self.options.file_base,
                                                   self.options.output_path,
                                                   self.test_lang,
                                                   self.options.icu_version,
                                                   # self.platformVersion,
                                                   self.testData.testDataFilename)
            except (KeyError, IndexError) as error:
                logging.error("Encountered error processing executor JSON values: %s", error)
                return None
        return True

    # Ask the executor to stop. May pass extra arguments in the message
    def request_executor_termination(self, terminate_args=None):
        terminate_msg = "#EXIT"
        result = None
        if terminate_args:
            terminate_msg += ' ' + terminate_args
            result = self.send_one_line(terminate_msg)

        if not result:
            self.jsonOutput["platform error"] = self.run_error_message
        else:
            if self.debug:
                logging.debug('TERMINATION INFO = %s', result)
                self.jsonOutput["platform"] = json.loads(result)

    def generate_header(self):
        # TODO: Create JSON versions of each of these rather than printing
        run_date_time = datetime.now()
        timestamp = time.time()
        test_environment = {
            "test_language": self.test_lang,
            "executor": self.exec_command,
            "test_type": self.test_type,
            "datetime": run_date_time.strftime('%m/%d/%Y, %H:%M:%S'),
            "timestamp": timestamp,
            "input_file": self.inputFilePath,

            # These should come from the Executor
            "icu_version": self.icuVersion,
            "cldr_version": self.cldrVersion,
            "test_count": len(self.tests)
        }
        self.jsonOutput['test_environment'] = test_environment
        return test_environment

    def complete_output_file(self, error_info):
        if self.resultsFile:
            # Generate final part of JSON output.
            # Adding terminators for JSON list and object

            self.jsonOutput['error_info'] = error_info

            # Create JSON output. Add indent= for pretty printing.
            self.resultsFile.write(json.dumps(self.jsonOutput))

            self.resultsFile.flush()
            self.resultsFile.close()

    def run_one_test_mode(self):
        if self.debug:
            logging.debug('  Running OneTestMode %s on data %s',
                  self.exec_command, self.inputFilePath)

        # Set up calls for version data --> results

        # Clear the JSON result for the new testing.
        self.jsonOutput = {}

        # Open the input file and get tests
        tests = self.open_json_test_data()
        if not tests:
            # The test data was not found. Skip this test.
            return None

        if self.debug:
            logging.info('@@@ %d tests found', len(tests))

        # Initialize JSON output headers --> results

        self.exec_list = self.exec_command.split()
        # TODO: get other things about the exec
        if self.debug:
            logging.info('EXEC info: exec_command %s, exec_list >%s<',
                         self.exec_command,
                         self.exec_list)

        # Start the JSON output
        # Set up calls for version data --> results
        if not self.request_executor_info():
            # TODO: Report problem with executor (somehow).
            return None

        # Use for directory of the output results
        # Check if report directory exists
        result_dir = None
        try:
            result_dir = os.path.dirname(self.outputFilePath)
            if not os.path.isdir(result_dir):
                os.makedirs(result_dir)
        except BaseException as error:
            sys.stderr.write('!!!%s:  Cannot create directory %sfor report file %s' %
                             (error, result_dir, self.outputFilePath))
            return None

        # Create results file
        try:
            if self.debug:
                logging.debug('++++++ Results file path = %s', self.outputFilePath)
                self.resultsFile = open(self.outputFilePath, encoding='utf-8', mode='w')
        except BaseException as error:
            logging.error('*** Cannot open results file at %s. Err = %s',
                  self.outputFilePath, error)
            self.resultsFile = open(self.outputFilePath, encoding='utf-8', mode='w')

        # Store information the test run
        # TODO: remove!??
        self.generate_header()

        # For each test
        #   send JSON data --> executor via stdout
        #      with subprocess
        #      handle any exceptions
        #   retrieve stdout result
        #   add format for JSON item
        #   output to result file
        #   output to result file

        # Work with the executor, running N tests each invocation
        try:
            per_execution = int(self.options.per_execution)
        except TypeError:
            per_execution = 1
        num_errors = self.run_all_single_tests(per_execution)

        env_dict = {}
        try:
            env_string = self.options.environment
            env_options = env_string.split(';')
            # Set the environment from the options, each separated with '='
            for option in env_options:
                parts = option.split('=')
                env_dict[parts[0]] = parts[1]
                # The environment variables for running the command line.
            self.exec_env = env_dict
        except (AttributeError, KeyError):
            env_dict = None
        # TODO: Use env_dict for environment information.

        # Complete outputFile
        self.complete_output_file(num_errors)
        return  # TODO: status

    def run_all_single_tests(self, tests_per_execution=1):
        # Print out each "test" item as a single line of text
        # Returns dictionary of all test results
        num_errors = 0

        # Save all results in single JSON output.
        all_test_results = []

        test_count = len(self.tests)
        test_num = 0
        lines_in_batch = 0

        # A group of tests separated by newlines
        test_lines = []

        # N tests may be given to send_one_line in a single batch.
        formatted_count = '{:,}'.format(test_count)
        for test in self.tests:
            test.update({"test_type": self.test_type})

            if self.progress_interval and test_num % self.progress_interval == 0:
                formatted_num = '{:,}'.format(test_num)
                logging.debug('Testing %s / %s. %s of %s', 
                    self.exec_list[0], self.testScenario, formatted_num, formatted_count)

            # Accumulate tests_per_execution items into a single outline
            if lines_in_batch < tests_per_execution:
                test_lines.append(json.dumps(test))
                lines_in_batch += 1
            else:  # lines_in_batch >= tests_per_execution
                # Time to send the batch
                result = self.process_batch_of_tests(test_lines)
                if result:
                    all_test_results.extend(result)
                else:
                    num_errors += 1
                    logging.error('!!!!!!  "platform error": "%s",\n', self.run_error_message)

                # Reset the batch
                lines_in_batch = 0
                test_lines = []

            test_num += 1
            if self.run_limit and test_num > self.run_limit:
                logging.info('** Stopped after %d tests', (test_num - 1))
                break

        # PROCESS THE LAST BATCH, if any
        all_test_results.extend(self.process_batch_of_tests(test_lines))

        self.jsonOutput['tests'] = all_test_results

        return num_errors

    def process_batch_of_tests(self, tests_to_send):
        # Handles a list of tests, appending "#EXIT" and sending
        # to the executor as a single line via stdin.
        num_errors = 0
        if not tests_to_send:
            return []

        if self.debug > 2:
            logging.debug('PROCESSING %d tests', len(tests_to_send))

        # Ask process to exit when finished.
        out_and_exit = '\n'.join(tests_to_send) + '\n#EXIT\n'

        if self.debug > 2:
            logging.info('+++ Test LINE TO EXECUTOR = %s', out_and_exit)

        result = self.send_one_line(out_and_exit)

        # TODO: If results indicate "unknown test type" for this executor,
        # don't sent more of that type.
        if not result:
            num_errors += 1
            logging.warning('!!!!!! process_batch_of_tests: "platform error": "%s"\n',
                            self.run_error_message)
            return None

        if self.debug > 2:
            logging.info('+++ Line from EXECUTOR = %s', result)

        index = 0
        batch_out = []
        for item in result.split('\n'):
            if self.debug > 1:
                logging.info(' RESULT %d = (%d)  >%s<', index, len(item), item)
            if not item or len(item) <= 0:
                # Check for special results returned from the executor,
                # indicated by '#' in the first column of the line returned.
                # An error is indicated by "#!!" in the first 3 columns.
                # TODO: Document these, perhaps in the project's JSON schema.
                continue
            if item[0] == "#":
                logging.debug('#### DEBUG OUTPUT = %s', item)

            # Process some types of errors
            if item[1:3] == "!!" and self.debug > 1:
                logging.warning(" !!!!!!!!!!!!!!!!! ERROR: %s", item)
                # Extract the message and check if we continue or not.
                json_start = item.index('{')
                json_text = item[json_start:]
                logging.debug('JSON TEXT = %s', json_text)
                json_out = json.loads(json_text)
                if 'error_retry' in json_out and json_out['error_retry']:
                    should_retry = json_out['error_retry']
                    logging.warning('!!! SHOULD RETRY = %s', should_retry)
            elif not(item is None) and item != "":
                try:
                    json_out = json.loads(item)
                    batch_out.append(json_out)
                except BaseException as error:
                    if self.debug > 1:
                        logging.warning('   && Item %s. Error in= %s. Received (%d): >%s<',
                                        index, error, len(item), item)
                    index += 1

        return batch_out

    def run_multitest_mode(self):
        # TODO Implement this
        logging.info('!!! Running MultiTestMode %s on data %s',
                     self.exec_command, self.inputFilePath)
        logging.warning('  ** UNIMPLEMENTED **')
        # Open the input file and get tests
        # Open results file

        # Initialize JSON output headers || results

        # Set up calls for version data || results

        # For each test
        #   send JSON data --> executor via stdout || stdout

        #   add format for JSON item
        #   pipe to result file

        # Complete outputFile via stdout

        # VERIFY?
        return  # TODO: status

    def open_json_test_data(self):
        # Read JSON file with results.
        try:
            input_file = open(self.inputFilePath,
                              encoding='utf-8', mode='r')
            file_raw = input_file.read()
            input_file.close()
            try:
                self.jsonData = json.loads(file_raw)
            except json.JSONDecodeError as error:
                logging.error('CANNOT parse JSON from file %s: %s', self.inputFilePath, error)
                return None
        except FileNotFoundError as err:
            logging.error('*** Cannot open file %s. Err = %s', self.inputFilePath, err)
            return None

        try:
            self.testScenario = self.jsonData['Test scenario']  # e.g., decimal_fmt
        except KeyError as error:
            logging.warning('*** Cannot get testScenario from  %s. Err = %s',
                            self.inputFilePath, error)
            self.testScenario = self.test_type

        self.tests = self.jsonData['tests']
        return self.tests

    # Send a single line of data or command to Stdout, capturing the output
    def send_one_line(self, input_line):
        self.run_error_message = None
        try:
            result = subprocess.run(self.exec_command,
                                    input=input_line,  # Usually a JSON string.
                                    encoding='utf-8',
                                    capture_output=True,
                                    env=self.exec_env,
                                    shell=True)
            if not result.returncode:
                return result.stdout
            else:
                logging.debug('$$$$$$$$$$$$$$$$ ---> return code: %s', result.returncode)
                logging.debug('    ----> INPUT LINE= >%s<', input_line)
                logging.debug('    ----> STDOUT= >%s<', result.stdout)
                self.run_error_message = '!!!! ERROR IN EXECUTION: %s. STDERR = %s' % (
                    result.returncode, result.stderr)
                logging.error(' !!!!!! exec_list = %s\n  input_line = %s' % (self.exec_list, input_line))
                logging.error(' !!!!!! %s' % self.run_error_message)

                # TODO!!!! Return an error for the offending line instead of failing for the whole batch

                return None
                input = json.loads(input_line.replace('#EXIT', ''))
                error_result = {'label': input['label'],
                                'input_data': input,
                                'error': self.run_error_message
                }
                return json.dumps(error_result)
        except BaseException as err:
            logging.error('!!! send_one_line fails: input => %s<. Err = %s', input_line, err)
            input = json.loads(input_line.replace('#EXIT', ''))
            error_result = {'label': input['label'],
                            'input_data': input,
                            'error': err
                            }
            return json.dumps(error_result)


        return None
