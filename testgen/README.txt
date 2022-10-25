Unicode & CLDR Data Driven Test - Test Data Generation

This directory contains the scripts to generate the test data in JSON format
from ICU or CLDR test data files.

The current code is rather experimental in nature and lacks the refinement
of an object oriented design clearly defining generators of different types
of test data as objects, of error messages that provide clear and actionable
information, etc.

Currently the generator does not perform a validation of the output JSON data
against a JSON schema definition.

Also currently lacking is a mechanism that on demand downloads the testdata
files from the ICU/CLDR GitHub repository. For now the data files are expected
to be in the same directory as the script and remain checked-in into the
repository for the time being.


Execution of test date generator
================================

python3 testdata_gen.py


Output of test data generator
=============================

For each test data category NNNN two files are generated:

NNNN_test_file.json: contains the test data
NNNN_verify_file.json: contains the verification data, i.e. expected output.

Currently supported test data categories are: collation, language display
names, number formating.


