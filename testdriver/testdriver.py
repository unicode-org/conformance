# Read a Data Driven Test file
# 1. Parse into JSON structure
# 2. For each test, stringify and output as single line to stdout

from datetime import datetime
import json
import logging
import os
import subprocess
import sys
import time

import datasets as ddtData
import ddtargs

from testplan import TestPlan

# TODO: Separate TestPlan into another module.

class TestDriver():
  def __init__(self):
    # All test plans requested from command line arguments
    self.test_plans = []
    self.debug = False
    return

  def setArgs(self, argOptions):
    # Options come from parse of command line
    self.icuVersion = argOptions.icu_version
    self.cldrVersion = argOptions.cldr

    # Create "test plans" for each option
    for test_type in argOptions.test_type:

      if test_type not in ddtData.testDatasets:
        logging.warning('**** WARNING: test_type %s not in testDatasets',
                        test_type)
      else:
        # Create a test plan based on data and options
        testDataInfo = ddtData.testDatasets[test_type]
        if self.debug:
          logging.debug('$$$$$ test_type = %s testDataInfo = %s' % (
              test_type, testDataInfo.testDataFilename))

        testFilename = testDataInfo.testDataFilename
        for exec in argOptions.exec:
          exec_command = {}
          if not ddtData.allExecutors.has(exec):
            # Run a non-specified executor. Compatibility of versions
            # between test data and the executo should be done the text executor
            # program itself.
            if self.debug:
              print('!!! **** CUSTOM EXEC = %s' % exec)
            exec_command = {'path': exec}
          else:
            # Set details for execution from ExecutorInfo
            resolvedCldrVersion = ddtData.resolveCldr(self.cldrVersion)
            exec_command = ddtData.allExecutors.versionForCldr(
                exec, resolvedCldrVersion)
            # The command needs to be something else!
          newPlan = TestPlan(exec_command, test_type)
          newPlan.setOptions(argOptions)
          newPlan.test_lang = exec.split()[0]

          try:
            testData = ddtData.testDatasets[test_type]
            newPlan.setTestData(testData)
          except KeyError as err:
            print('!!! No test data filename for %s' % test_type)

          self.test_plans.append(newPlan)

  def parseArgs(self, args):
    # TODO: handle arguments for:
    #   executor language: NODE, RUST, CPP, JAVA, ETC.
    #   CLDR version
    #   test types: e.g., "collator", "decimal", "datetime", etc.
    #   Use these to get dataset info and call appropriate routines
    #     to execute tests and verify results.

    # Get all the arguments
    argparse = ddtargs.DdtArgs(args)
    if self.debug:
      print('TestDriver OPTIONS: %s' % argparse.getOptions())

    # Now use the argparse.options to set the values in the driver
    self.setArgs(argparse.getOptions())
    return

  def runPlans(self):
    # For each of the plans, run with the appropriate type of parallelism
    # Debugging output
    for plan in self.test_plans:
      plan.runPlan()


# Run the test with command line arguments
def main(args):

  driver = TestDriver()
  # print('ARGS = %s' % (args))
  driver.parseArgs(args[1:])

  driver.runPlans()

  #               if len(args)> 2:
      # Set limit on number to run
   #   numberToRun = int(args[2])
   #   driver.runLimit = numberToRun

   # driver.initExecutor()

if __name__ == "__main__":
    main(sys.argv)
