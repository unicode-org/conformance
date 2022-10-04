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

* testDriver.py: 

* datasets.py

* ddtargs.py

# testplan.py

* testreport.py
