from datetime import datetime
import json
import logging
import os
import subprocess
import re
import sys
import time

import datasets as ddtData
import ddtargs


# Set up and execute a testing plan for DDT

class TestPlan():
  def __init__(self, exec_data, test_type, args=None):
    self.planId = None
    self.exec_data = exec_data
    self.exec_env = None
    self.exec_command = None
    self.exec_list = None
    if exec_data:
      if 'path' in exec_data:
        self.exec_command = exec_data['path']
      if 'env' in exec_data:
        self.exec_env = exec_data['env']
    self.test_type = test_type
    self.runStyle = 'one_test'
    self.parallelMode = None
    self.options = None
    self.testData = None

    # Additional args to subprocess.run
    self.args = args

    self.run_error_messge = None  # Set if execution
    self.test_lang = None
    self.inputFilePath = None
    self.resultsFile = None

    self.jsonOutput = {}  # Area for adding elements for the results file
    self.platformVersion = ''  # Records the executor version
    self.icu_version = None
    self.run_limit = None  # Set to positive integer to activate
    self.debug = 1

    self.iteration = 0
    self.progress_interval = 1000

    self.verifier = None

  def setOptions(self, options):
    self.options = options
    try:
      self.icu_version = options.icu_version
    except:
      logging.warn('NO ICU VERSION SET')

  def setTestData(self, test_data):
    self.testData = test_data  # ???['tests']

  def setVerifyFile(self, verifyFilename):
    self.verifyFilename = verifyFilename

  # Use the settings to run the plan, using stdout from this
  # routine as stdin for the test executor.
  # If possible, run the verifier too.
  def runPlan(self):
    # TODO: Handle list of custom test files
    if self.options.custom_testfile:
      # For files in custom_testfile list, run the tests
      # for each specified executor.
      # !!!
      x = 1

    # Check for option to set version of executor
    # TODO

    if self.test_lang == 'node' and 'node_version' in self.options:
      # Set up for the version of node selected
      nvm_command = 'nvm use %s' % self.options.node_version
      result = subprocess.run(['bash', '-c', nvm_command])


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
        print('!!! RUN LIMIT SET: %d' % self.run_limit)

    if self.debug:
      print('Running plan %s on data %s' % (
          self.exec_command, self.inputFilePath))

    if self.options.exec_mode == 'one_test':
      self.runOneTestMode()
    else:
      self.runMultiTestMode()

    # TODO!!!: Run verify
    # self.runVerifyResult()
    return

  def requestExecutorInfo(self):
    versionInfo = "#VERSION"
    result = self.sendOneLine(versionInfo)
    if result and result[0] == "#":
      # There's debug data. Take the 2nd line of this result
      result_lines = result.split('\n')
      result = result_lines[1]

    if not result:
      self.jsonOutput["platform error"] = self.run_error_message
      return None
    else:
      if self.debug:
        print('EXECUTOR INFO = %s' % result)
      try:
        self.jsonOutput["platform"] = json.loads(result)
        self.platformVersion =  self.jsonOutput["platform"]["platformVersion"]
        self.icuVersion =  self.jsonOutput["platform"]["icuVersion"]

        # TODO: Clean this up!
        # Get the test data area from the icu_version

        # Reset the output path based on the version.
        self.outputFilePath = os.path.join(self.options.file_base,
                                           self.options.output_path,
                                           self.test_lang,
                                           self.options.icu_version,
                                           # self.platformVersion,
                                           self.testData.testDataFilename)
      except:
        return None
    return True

  # Ask the executor to stop. May pass extra arguments in the messsage
  def requestExecutorTermination(self, terminateArgs=None):
    terminateMsg = "#EXIT"
    if terminateArgs:
      terminateMsg += ' ' + terminateArgs
    result = self.sendOneLine(terminateMsg)

    if not result:
      self.jsonOutput["platform error"] = self.run_error_message
    else:
      if self.debug:
        print('TERMINATION INFO = %s' % result)
      self.jsonOutput["platform"] = json.loads(result)

  def generateHeader(self):
    # TODO: Create JSON versions of each of these rather than printing
    runDateTime = datetime.now()
    timestamp = time.time()
    test_environment = {
        "test_language": self.test_lang,
        "executor": self.exec_command,
        "test_type": self.test_type,

        "datetime": "%s" % runDateTime.strftime('%m/%d/%Y, %H:%M:%S'),
        "timestamp": "%s" % timestamp,

        "inputfile": self.inputFilePath,
        "resultfile": self.outputFilePath,

        "icu_version": '%s' % self.testData.icu_version,
        "cldr_version": '%s' % self.testData.cldr_version,
        "test_count": "%d" % len(self.tests)
    }
    self.jsonOutput['test_environment'] = test_environment
    return test_environment

  def completeOutputFile(self, errorInfo):
    if self.resultsFile:
      # Generate final part of JSON output.
      # Adding terminatiors for JSON list and object

      self.jsonOutput['errorInfo'] = errorInfo

      # Create JSON output
      self.resultsFile.write(json.dumps(self.jsonOutput, indent=2))

      self.resultsFile.flush()
      self.resultsFile.close()

  def runOneTestMode(self):
    if self.debug:
      print('  Running OneTestMode %s on data %s' %
            (self.exec_command, self.inputFilePath))

    # Set up calls for version data --> results

    # Clear the JSON result for the new testing.
    self.jsonOutput ={}

    # Open the input file and get tests
    tests = self.openJsonTestData()

    if not tests:
      # The test data was not found. Skip this test.
      return None

    if self.debug:
      print('@@@ %d tests found' % (len(tests)))

    # Initialize JSON output headers --> results

    self.exec_list = self.exec_command.split()
    # TODO: get other things about the exec
    if self.debug:
      print('EXEC info: exec_command %s, exec_list >%s<' % (self.exec_command,
      self.exec_list))

    # Start the JSON output

    # Set up calls for version data --> results
    is_executor_ok = self.requestExecutorInfo()
    if not is_executor_ok:
      return None

    # Use for directory of the output results
    # Check if report directory exists
    try:
      result_dir = os.path.dirname(self.outputFilePath)
      if not os.path.isdir(result_dir):
        os.makedirs(result_dir)
    except BaseException as err:
      sys.stderr.write('!!! Cannot create directory %sfor report file %s' %
                       (result_dir, self.outputFilePath))
      return None

    # Create results file

    try:
      if self.debug:
        print('++++++ Results file path = %s' % self.outputFilePath)
      self.resultsFile = open(self.outputFilePath, encoding='utf-8', mode='w')
    except BaseException as err:
      print('*** Cannot open results file at %s. Err = %s' %
            (self.outputFilePath, err))
      self.resultsFile = open(self.outputFilePath, encoding='utf-8', mode='w')

    # Store information the test run
    test_environment = self.generateHeader();

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
    except:
      per_execution = 1
    numErrors = self.runAllSingleTests(per_execution)

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
    except:
      env_string = ''

    # Complete outputFile
    self.completeOutputFile(numErrors)

    if self.verifier:
      self.runVerifyResult()

    return # TODO: status

  def runAllSingleTests(self, testsPerExecution=1):
    # Print out each "test" item as a single line of text
    # Returns dictionary of all test results
    numErrors = 0

    # Save all results in single JSON output.
    allTestResults = []

    testCount = len(self.tests)
    testNum = 0
    linesInBatch = 0

    # A group of tests separated by newlines
    testLines = []

    # N tests may be given to sendOneLine in a single batch.
    formattedCount = '{:,}'.format(testCount)
    for test in self.tests:
      test.update({"test_type": self.testScenario})

      if self.progress_interval and testNum % self.progress_interval == 0:
        formattedNum = '{:,}'.format(testNum)
        print('Testing %s / %s. %s of %s' % (
            self.exec_list[0], self.testScenario, formattedNum, formattedCount), end='\r')

      # Accumulate testsPerExecution items into a single outline
      if linesInBatch < testsPerExecution:
        outLine = json.dumps(test)
        testLines.append(outLine)
        linesInBatch += 1

      if linesInBatch >= testsPerExecution:
        # Time to send the batch
        result = self.processBatchOfTests(testLines)
        if result:
          allTestResults.extend(result)
        else:
          numErrors += 1
          print('!!!!!!  "platform error": "%s",\n' % self.run_error_message)

        # Reset the batch
        linesInBatch = 0
        testLines = []

      testNum += 1
      if self.run_limit and testNum > self.run_limit:
        print('** Stopped after %d tests' % (testNum - 1))
        break

    # PROCESS THE LAST BATCH, if any
    allTestResults.extend(self.processBatchOfTests(testLines))

    self.jsonOutput['tests'] = allTestResults

    return numErrors

  def processBatchOfTests(self, testsToSend):
    # Handles a list of tests, appending "#EXIT" and sending
    # to the executor as a single line via stdin.
    numErrors = 0
    if not testsToSend:
      return []

    if self.debug > 2:
      print('PROCESSING %d tests' % len(testsToSend))

    # Ask process to exit when finished.
    outAndExit = '\n'.join(testsToSend) + '\n#EXIT'

    if self.debug > 2:
      print('+++ Test LINE TO EXECUTOR = %s' % outAndExit)

    result = self.sendOneLine(outAndExit)

    # TODO: If results indicate "unknown test type" for this executor,
    # don't sent more of that type.
    if not result:
      numErrors += 1
      print('!!!!!! processBatchOfTests: "platform error": "%s"\n' % self.run_error_message)
      return None

    if self.debug > 2:
      print('+++ Line from EXECUTOR = %s' % result)

    index = 0
    batchOut = []
    should_retry = True
    for item in result.split('\n'):
      if self.debug > 1:
        print(' RESULT %d = (%d)  >%s<' % (index, len(item), item))
      if item and len(item) > 0:
        # Check for special results returned from the executor,
        # indicated by '#' in the first column of the line returned.
        # An error is indicated by "#!!" in the first 3 columns.
        # TODO: Document these, perhaps in the project's JSON schema.        #
        if item[0] == "#":
          print('#### DEBUG OUTPUT = %s' % item)

          # Process some types of errors
          if item[1:3] == "!!":
            print(" !!!!!!!!!!!!!!!!! ERROR: %s" % item)
            # Extract the message and check if we continue or not.
            json_start = item.index('{')
            json_text = item[json_start:]
            print('JSON TEXT = %s' % json_text)
            json_out = json.loads(json_text)
            if 'error_retry' in json_out and json_out['error_retry']:
              should_retry = json_out['error_retury']
              print('!!! SHOULD RETRY = %s' % should_retry)
        elif item != None and item != "":
            try:
              json_out = json.loads(item)
              batchOut.append(json_out)
            except BaseException as error:
              print('   && Item %s. Error in= %s. Received (%d): >%s<' %
                    (index, error, len(item), item))
        index += 1

    return batchOut

  def runMultiTestMode(self):
    # TODO Implement this
    print('!!! Running MultiTestMode %s on data %s' %
          (self.exec_command, self.inputFilePath))
    print('  ** UNIMPLEMENTED **')
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
    return # TODO: status

  def openJsonTestData(self):
    if self.debug:
      print('TESTPLAN 355 input file path = %s' %
            self.inputFilePath)
    try:
      inputFile = open(self.inputFilePath,
                       encoding='utf-8', mode='r')
    except BaseException as err:
      print('*** Cannot open file %s. Err = %s' %
            (self.inputFilePath, err))
      return None

    fileRaw = inputFile.read()
    inputFile.close()
    try:
      self.jsonData = json.loads(fileRaw)
    except BaseException as err:
      print('CANNOT parse JSON from file %s: %s' % (self.inputFilePath, err))

    try:
      self.testScenario = self.jsonData['Test scenario']  # e.g., decimal_fmt
    except:
      try:
        self.testScenario = self.jsonData['test scenario']  # e.g., decimal_fmt
      except BaseException as err:
        print('*** Cannot get testScenario from  %s. Err = %s' %
            (self.inputFilePath, err))

    self.tests = self.jsonData['tests']
    return self.tests

  # Send a single line of data or command to Stdout, capturing the output
  def sendOneLine(self, input_line):
    self.run_error_message = None
    try:
      result = subprocess.run(self.exec_list,
                              input=input_line, # Usually a JSON string.
                              encoding='utf-8',
                              capture_output=True,
                              env=self.exec_env)
      if not result.returncode:
        return result.stdout
      else:
        print('$$$$$$$$$$$$$$$$ ---> return code: %s' % result.returncode)
        print('    ----> INPUT LINE= >%s<' % input_line)
        print('    ----> STDOUT= >%s<' % result.stdout)
        self.run_error_message = '!!!! ERROR IN EXECUTION: %s. STDERR = %s' %(
            result.returncode, result.stderr)
        return None
    except BaseException as err:
      print('!!! sendOneLine fails: input => %s<. Err = %s' % (input_line, err))
      return None

  def runVerifyResult(self):
    # Check the actual test output against the expected values.
    self.verifier = Verifier(self.options.test_type,
                            self.options.output_path,
                            self.verifyFilePath,
                            self.options.report_path)

    results = self.verifier.compareTestToExpected()

    return "VERIFIER NOT IMPLEMENTED"
