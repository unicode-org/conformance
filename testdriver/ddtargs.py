# Process command line arguments for running DDT

# Args expected with examples
#  test_type: coll_shift, decimal_fmt, etc.
#  exec: nodejs, rust, cpp, java, custom
#  cldr_version: 41
#  icu_version: 71.1
#  args: additional arguments for custom

#  Options for multiprocessing / threading
#  parallel: exec, cpus, none
#  infolder:
#  outfolder:
#  noverify

#  Option for running tests with executor instance:
#  exec_mode:
#    one_test: each test item launches an exector (slow, safe)
#    multi_test: run a single executor instance taking multiple tests
#      faster but not hermetically isolated

import argparse
import sys

class DdtOptions():
  def __init__(self):
    self.test_data_path = 'testData'
    self.test_output_path = 'testResults'
    self.test_report_path = 'testReports'

    self.parallel_mode = None  # For each exec or using N CPUs?
    self.exec_mode = 'one_test'  # Default. 'multi_test

type_options = ['coll_shift_short', 'decimal_fmt', 'display_names',
                'number_fmt', 'lang_names', 'ALL']

class DdtArgs():
  def __init__(self, args):
    self.options = None  # A simple namespace with each field

    self.parser = argparse.ArgumentParser(
        description='Process DDT Test Driver arguments')

    setCommonArgs(self.parser)

    self.parser.add_argument(
        '--start_test', default=0,
        help='number of tests to skip at start of the test data')

    self.parser.add_argument(
        '--per_execution', default=1,
        help='How many tests are run in each invocation of an executor')

    # For handling verification
    self.parser.add_argument('--verifyonly', default=None)
    self.parser.add_argument('--noverify', default=None)  #
    self.parser.add_argument('--custom_verifier', default=None)  #
    self.options = self.parser.parse_args(args)

  def parse(self):
    return self.options

  def getOptions(self):
    return self.options


class VerifyArgs():
  def __init__(self, args):
    self.parser = argparse.ArgumentParser(
        description='Process DDT Verifier arguments')

    setCommonArgs(self.parser)
    self.parser.add_argument('--verify_file_name', action='extend', nargs='*',
                             help='Files with expected results for verifying', default=None)

    self.parser.add_argument('--test_verifier',
                             help='Flag to run in test mode', default=None)

    self.options = self.parser.parse_args(args)
    return

  def getOptions(self):
    return self.options


# Set up arguments common to both testDriver and verifier
def setCommonArgs(parser):

  # What data and executor(s) to verify
  parser.add_argument('--test_type', '--type', '-t', '--test',
                      action='extend', nargs='*',
                      choices=type_options)
  # All more than one item in exec list
  parser.add_argument('--exec', action='extend', nargs='*',
                      help='Execution platforms') #, default='ALL')

  # TODO: are these being used? How?
  parser.add_argument('--icu', default='LATEST')
  parser.add_argument('--cldr', default='LATEST')

  # Location of the data files
  parser.add_argument(
      '--file_base', default="",
      help='Base directory for input, output, and report paths')
  parser.add_argument('--input_path', default='testData')
  parser.add_argument('--output_path', default='testResults')
  parser.add_argument('--report_path', default='testReports')

  parser.add_argument('--exec_mode', default='one_test')
  parser.add_argument('--parallel_mode', default=None)
  parser.add_argument('--run_limit', default=None)

  parser.add_argument(
      '--custom_testfile', default=None, action='extend', nargs='*',
      help='full path to test data file in JSON format')

  parser.add_argument(
      '--progress_interval',
      help="Interval between progress output printouts", default=None)

  parser.add_argument('--debug_level', default=None)


def argsTestData():
  tests = [
      ['--test_type', 'coll_shift_short'],
      ['--test_type', 'coll_shift_short', '-t', 'decimal_fmt'],
      ['--test_type', 'coll_shift_short', '--test_type', 'decimal_fmt', 'number_fmt', 'display_names',
       'lang_names'],

      ['--test', 'coll_shift_short', 'ALL', 'decimal_fmt'],

      ['--test_type', 'ALL'],
      '--type ALL decimal_fmt --exec a b c d'.split(),

      ['--exec', 'nodejs'],
      ['--exec nodejs rust /bin/mytest'],
      '--exec nodejs --test_type decimal_fmt --icu 71 --cldr 40'.split(),
      ['--exec', 'python py/exec.py'],
      '--test_random 1234'.split(),
      ['--exec', '--custom_testfile', 'testData/customtest1.json',
       'testData/customtest2.json',
       'testData/customtest3.json'],
  ]
  return tests

def main(args):

  argparse = DdtArgs()

  tests = argsTestData()
  for test in tests:
    try:
      print('Args = %s' % test)

      result = argparse.parse(test)
      print('  OPTIONS = %s' % argparse.options)
    except BaseException as err:
      print(' ERROR: %s ' % err)

if __name__ == "__main__":
    main(sys.argv)
