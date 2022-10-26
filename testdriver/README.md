# Test Driver

The test driver program consists of several Python routines to

* read test data in JSON format, generated from Unicode specification files,

* identify appropriate test executors associated with test data,
* execute tests in the specified execution platforms
* store results in designated test result areas
* call the test verifier on the results of the test, if desired.

The test driver program is run by specifying commanand line parameters that define the input data, test platforms to be run, area for the test results, etc.

## Test driver modules

These are the Python3 modules that implement the test driver functions:

### testDriver.py: 

The main routine running tests. It accepts a command line that contains
information on the tests to be run, locations of files, and parameters for
running the tests. See *ddtargs.py* for command line arguments.

testDriver uses command line values to locate standard test data locations and
execution parameters. It uses information in *datasets.py* if test names and
executors are pre-defined.

The sample scripts runColl_node.sh and runColl_rust.sh illustrate the use of
expected *exec* programs and standard tests.

testDriver can also accept data inputs and executor program information that is
not built in. The script *runColl_python.sh* illustrates calling a program in a
location that is not pre-defined in datasets.py.

### ddtargs.py

This module defines parameters needed for locating and running test executors
and the test data associated.

```
python3 testdriver.py --help
usage: testdriver.py [-h] [--debug_level DEBUG_LEVEL]
                     [--test_type [{coll_shift_short,decimal_fmt,display_names,number_fmt,lang_names,ALL} ...]] [--exec [EXEC ...]]
                     [--file_base FILE_BASE] [--input_path INPUT_PATH] [--output_path OUTPUT_PATH] [--report_path REPORT_PATH] [--icu ICU]
                     [--cldr CLDR] [--exec_mode EXEC_MODE] [--parallel_mode PARALLEL_MODE] [--run_limit RUN_LIMIT]
                     [--start_test START_TEST] [--progress_interval PROGRESS_INTERVAL] [--per_execution PER_EXECUTION]
                     [--custom_testfile [CUSTOM_TESTFILE ...]] [--verifyonly VERIFYONLY] [--noverify NOVERIFY]
                     [--custom_verifier CUSTOM_VERIFIER]

Process DDT Test Driver arguments

options:
  -h, --help            show this help message and exit
  --debug_level DEBUG_LEVEL
  --test_type [{coll_shift_short,decimal_fmt,display_names,number_fmt,lang_names,ALL} ...], --type [{coll_shift_short,decimal_fmt,display_names,number_fmt,lang_names,ALL} ...], -t [{coll_shift_short,decimal_fmt,display_names,number_fmt,lang_names,ALL} ...]
  --exec [EXEC ...]     Execution platforms
  --file_base FILE_BASE
                        Base directory for input, output, and report paths
  --input_path INPUT_PATH
  --output_path OUTPUT_PATH
  --report_path REPORT_PATH
  --icu ICU
  --cldr CLDR
  --exec_mode EXEC_MODE
  --parallel_mode PARALLEL_MODE
  --run_limit RUN_LIMIT
  --start_test START_TEST
                        number of tests to skip at start of the test data
  --progress_interval PROGRESS_INTERVAL
                        Interval between progress output printouts
  --per_execution PER_EXECUTION
                        How many tests are run in each invocation of an executor
  --custom_testfile [CUSTOM_TESTFILE ...]
                        full path to test data file in JSON format
  --verifyonly VERIFYONLY
  --noverify NOVERIFY
  --custom_verifier CUSTOM_VERIFIER
```

### datasets.py

This file has structures that expand command line values *test_type* and *exec*
to test files and known executors, if they are recognized. This makes it easy to
create compact command lines for *testdriver.py*.

### testplan.py

The values assembled by testdriver for data sets and executors are turned into
test plans that are implemented by *testplan.py*. For example, the command line
may include:

```
  --test_type coll_shift_short displaynames number_fmt
  
  --exec rust node
```
This will be expanded into 6 testplans, 3 for each executor:

* node with coll_shift_short
* node with displaynames
* node with number_fmt
* rust with coll_shift_short
* rust with displaynames
* rust with number_fmt

These 6 test plans will be executed individually, producing output in the
respective testResults directories for node and rust.

They may be executed serially or in parallel (to be implemented.)
