# Conformance schema

This directory contains JSON schema for communications between parts of Data
Drive Test (DDT). This defines the form of the .json files that store
information using the JSON schema approach.

References:

* https://json-schema.org/

* https://json-schema.org/draft/2020-12/json-schema-core

In this directory, there is a subdirectory for each test type,
e.g. `collation_short`. In each, there are files describing legal JSON forms for:

1. generated test data. The file is named test_schema.json.
1. output from test execution. This file is always called `result_schema.json`
1. output from the verifier. This describes the output of the verificatino
step. It will be added in the future.

Definition of test data requires that no specified properties exist in the
testing schema. To check this, use this specification for each set of
properties:

```
"additionalProperties": false
```

When a new type of test is added, do these steps:

1. Define the format of the test data .json produced by `testgen/testdata_gen.py`
   as `test_schema.json`. Make sure that all properties are specified, including
   defining the possible type(s) of each. Add explicit enumerations for limitied
   sets of values.

1. Add the directory to this folder with the test type as the folder name. E.g.,
   for new test "test_feature", create the test_feature directory here.

1. Include the file describing the generated test data as `test_schema.json` in
   that directory.

1. Add the new test type to `schema_files.py`.

1. Run `check_schema.py` in this folder to verify that the schema is syntactically
   correct. Don't proceed until this run is clean for all schemas.

1. After generating the test data, run the script `check_generated_data.py` in
   this folder for all the icu versions. Make sure that all data files pass with
   the test schema.

1. When a text executor is implemented for the new type of test, add a file
   `result_schema.json` under the test_type file in this schema folder. It should
   describe all possible outputs from running tests on the various platforms.

1. When new tests have been executed, run `check_test_output.py` in this
   folder. Fix any unexpected or undefined fields. Resolve any reports of
   unexepected data types.

