# Unicode & CLDR Data Driven Test

This repository provides tools and procedures for verifying that an
implementation is working correctly according to the data-based
specifications. The tests are implemented on several platforms including NodeJS
(JavaScript), ICU4X (RUST), ICU4C, etc. Additional programming platforms may be
added to use the test driver framework.

The goal of this work is an easy-to-use framework for verifying that an
implementation of ICU functions agrees with the required behavior. When a DDT
tet passes, it a strong indication that output is consistent across platforms.

Data Driven Test (DDT) focuses on functions that accept data input such as
numbers, date/time data, and other basic information. The specifications
indicate the expected output from implementations when given the data and
argument settings for each of the many individual data items.

Note that these tests are only part of the testing required for ICU-compliant
libraries. Many additional tests are implemented in the

* !!! TODO: reference to data specifications

# Components of Data Driven Test

## ICU versions for data and testing

Each ICU test program is built with a specific version of ICU & CLDR data. These
versions are updated periodically. For each ICU version, there is a specific
CLDR version, e.g., ICU73 uses data from CLDR 43, although multiple ICU releases
may depend on the same CLDR data.

For this reason, specifying a particular ICU version for test data or test
executor or both

Each part of Data Driven Testing is designed to handle a specific ICU version.

* Data generation uses specifications starting with ICU versions 70, 71, etc. For each ICU release, these data should be updated.

* Test execution allows setting the data version explicitly with a command line
  argument --icuversion that points to the indicated test data. The ICU version
  of the test executor platform is requested from each platform at the start of
  the test driver. Output directories are created under the platform for the
  test results running a particular ICU version, e.g., testOutput/node/icu73.

* Test verification uses ICU version information in the test output files for
  matching with the corresponding expected results. Verification output appears
  in the testResults subdirectory for each node, e.g. testOutput/rust/icu71.

## Architectural Overview

Conceptually, there are four main functional units of the DDT implementation:

![Conceptual model of Data Driven Testing](./ddt_concept_model.png)

## Data generation

Utilizes Unicode (UTS-35) specifications, CLDR data, and existing ICU test
data. Existing ICU test data has the advantage of being already structured
towards data driven testing, is in many cases formatted in a way to simplify
adding new tests, and contains edge and error cases.

Data generation creates two files:
* Test data instance: a JSON file containing the type of test and additional
  information on the environment and version of data.

The test type is indicated with the "Test scenario" field.

Individual data tests are stored as an array of items, each with a label and
parameters to be set for computing a result.

  Example line for collation_short:
  ```
  {
  "description": "UCA conformance test. Compare the first data\n   string with the second and with strength = identical level\n   (using S3.10). If the second string is greater than the first\n   string, then stop with an error.",
  "Test scenario": "collation_short",
  "tests": [
    {
      "label": "0000000",
      "string1": "\u0009!",
      "string2": "\u0009?"
    },
  ```
* A required test result file (JSON) containing the expected results from each
  of the inputs. This could be called the “golden data”.

  Sample verify data:
  ```
  {"Test scenario": "collation_short",
  "verifications": [
    {
      "label": "0000000",
      "verify": "True"
    },
  ```

## Checking data using schemas

Several types of JSON formatted data are created and used by Conformance
processing, and the integity of this information must be maintained.

Data Driven Testing uses [JSON Schema
Validation](https://python-jsonschema.readthedocs.io/en/latest/validate/) to
insure the structure of data files. JSON schema make sure that needed parameters
and other information are present as required and that the type of each data
item is as specified.

In addition, schema specification can restrict the range of data fields to those
expected, allowing only those data that are expected in JSON output files. This
gives a measure of confidence in the data exchanged between the phases of
Conformance Testing.

The types of data include:

* **Generated test data** including all parameters and settings as well as
  ancilliary descriptive information for each test. This data depends only on
  the type of test (component) and the ICU version. It does not depend on the
  particular execution platorm, i.e., programming languages.

* **Expected results** of running each test running with the specified ICU
  version. This does not depend on the platform.

* **Actual results** from executing each test in the input. This contains actual
  results from the execution of each test in a given platform. This data may
  include output from the executor including platform-specific parameters and
  settings derived from the input data. It may also include data on errors
  encountered during the run of the platform executor.

* **Schema files** describing the expected JSON format of each type of files for
  the components.

Schema validation is performed at these times in standard processing:

1. After test data generation, all generated test data and expected result data
   files are checked for correct structure.

2. Before test execution, the schema files themselves are checked for correct
   schema structure..

3. After test executors are run, all resuulting test output files are checked
   for correct structure.


Top level directory `schema` contains the following:

* One subdirectory for each component such as "collation". This contains schema.json files for generated tests, expected results, and test output structure.

* Python routines for checking these types of data.

* A Python routine for validating the structure of the .json schema files.

```
$ ls schema/*.py
schema/check_generated_data.py  schema/check_test_output.py  schema/__init__.py      schema/schema_validator.py
schema/check_schemas.py         schema/check_verify_data.py  schema/schema_files.py

$ tree schema/*

schema/collation_short
├── result_schema.json
├── test_schema.json
└── verify_schema.json
schema/datetime_fmt
├── result_schema.json
├── test_schema.json
└── verify_schema.json
schema/lang_names
├── #result_schema.json#
├── result_schema.json
├── test_schema.json
└── verify_schema.json
schema/likely_subtags
├── result_schema.json
├── test_schema.json
└── verify_schema.json
schema/list_fmt
├── #result_schema.json#
├── result_schema.json
├── test_schema.json
└── verify_schema.json
schema/message_fmt2
├── README.md
├── result_schema.json
├── testgen_schema.json
├── test_schema.json
└── verify_schema.json
schema/number_format
├── result_schema.json
├── test_schema.json
└── verify_schema.json
schema/plural_rules
├── result_schema.json
├── test_schema.json
└── verify_schema.json
schema/rdt_fmt
├── result_schema.json
├── test_schema.json
└── verify_schema.json
```

Note also that the schema validation creates a file
**schema/schema_validation_summary.json**
which is used in the summary presentation of the Conformance results.

## Text Execution

Test execution consists of a Test Driver script and implementation-specific
executables.  The test driver executes each of the configured test
implementation executables, specifying the input test data and the location for
storing results.  STDIN and STDOUT are the defaults.

### Test executors

Each test executor platform contains a main routine that accepts a test request
from the test driver, calling the tests based on the request data.

Each executor parses the data line sent by the test driver, extracting elements
to set up the function call the the particular test.

For each test, the needed functions and other objects are created and the test
is executed. Results are saved to a JSON output file.

See [executors/README](./executors/README.md) for more details

## Verification

Each test is matched with the corresponding data from the required test
results. A report of the test results is generated. Several kinds of status
values are possible for each test item:

* **Success**: the actual result agrees with expected results
* **Failure**: a result is generated, but the result is not the same as the expected
value.
* **No test run**: The test was not executed by the test implementation for the data
item
* **Error**: the test resulted in an exception or other behavior not anticipated for
the test case

### Open questions for the verifier
* What should be done if the test driver fails to complete? How can this be
  determined?

    * Proposal: each test execution shall output a completion message,
indicating that the test driver finished its execution normally, i.e., did not
crash.

# How to use DDT

In its first implementation, Data Driven Test uses data files formatted with
JSON structures describing tests and parameters. The data directory string is
set up as follows:

## A directory `testData` containing
  * Test data files for each type of test, e.g., collation, numberformat,
  displaynames, etc. Each file contains tests with a label, input, and
  parameters.
  * Verify files for each test type. Each contains a list of test labels and
  expected results from the corresponding tests.

## Directory `testOutput`

This contains a subdirectory for each executor. The output file from each test
is stored in the appropriate subdirectory. Each test result contains the label
of the test and the result of the test. This may be a boolean or a formatted
string.

The results file contains information identifying the test environment as well
as the result from each test. As an example, collation test results from the
`testOutput/node` file are shown here:

```
{
  "platform": {
    "platform": "NodeJS",
    "platformVersion": "v18.7.0",
    "icuVersion": "71.1"
  },
  "test_environment": {
    "test_language": "nodejs",
    "executor": "/usr/bin/nodejs ../executors/nodejs/executor.js",
    "test_type": "collation_short",
    "datetime": "10/07/2022, 16:19:00",
    "timestamp": "1665184740.2130146",
    "inputfile": "/usr/local/google/home/ccornelius/DDT_DATA/testData/icu73/collation_testt.json",
    "resultfile": "/usr/local/google/home/ccornelius/DDT_DATA/testOutputs/node/icu73/collation_test.json",
    "icu_version": "ICUVersion.ICU71",
    "cldr_version": "CLDRVersion.CLDR41",
    "test_count": "192707"
  },
  "tests": [
    {
      "label": "0000000",
      "result": "True"
    },
    {
      "label": "0000001",
      "result": "True"
    },
    ...
  ]
}
```

## Directory `testReports`
This directory stores summary results from verifying the tests performed by each executor. Included in the `testReports` directory are:

* `index.html`: shows all tests run and verified for all executors and versions. Requires a webserver to display this properly.

* `exec_summary.json`: contains summarized results for each pair (executor, icu version) in a graphical form. Contains links to details for each test pair.

* subdirectory for each executor, each containing verification of the tested icu versions, e.g., `node/`, `rust/`, etc.

Under each executor, one or more ICU version files are created, each containing:

* `verfier_test_report.html` - for showing results to a user via a web server

* `verfier_test_report.json` - containing verifier output for programmatic use

* `failing_tests.json` - a list of all failing tests with input values
* `pass.json` - list of test cases that match their expected results
* `test_errors.json` - list of test cases where the executor reported an error
* `unsupported.json` - list of test cases that are not expected to be supported in this version

The `verifier_test_report.json` file contains information on tests run and comparison with the expected results. At a minimum, each report contains:

* The executor and test type
* Date and time of the test
* Execution information, from the testResults directory
* Total number of tests executed
* Total number of tests failing
* Total number of tests succeeding
* Number of exceptions identified in the test execution. This may include
  information on tests that could not be executed, along with the reasons
  for the problems.
* Analysis of test failures, if available. This may include summaries of string
  differences such as missing or extra characters or substitutions found in
  output data.

## Contributor setup

Requirements to run Data Driven Testing code locally:

- Install the Python package `jsonschema`
    * In a standard Python environment, you can run
        ```
        pip install jsonschema
        ```
    * Some operating systems (ex: Debian) might prefer that you install
    the OS package that encapsulates the Python package
        ```
        sudo apt-get install python-jsonschema
        ```
- Install the minimum version supported by ICU4X
    * The latest minimum supported supported Rust version ("MSRV") can be found in the
    [`rust-toolchain.toml` file](https://github.com/unicode-org/icu4x/blob/main/rust-toolchain.toml)
    * To view your current default Rust version (and other locally installed Rust versions):
        ```
        rustup show
        ```
    * To update to the latest Rust version:
        ```
        rustup update
        ```
  - Install `logrotate`
      ```
      sudo apt-get install logrotate
      ```

# History

Data Driven Test was initiated in 2022 at Google. The first release of the
package was delivered in October, 2022.

### Copyright & Licenses

Copyright © 2022-2024 Unicode, Inc. Unicode and the Unicode Logo are registered trademarks of Unicode, Inc. in the United States and other countries.

A CLA is required to contribute to this project - please refer to the [CONTRIBUTING.md](https://github.com/unicode-org/.github/blob/main/.github/CONTRIBUTING.md) file (or start a Pull Request) for more information.

The contents of this repository are governed by the Unicode [Terms of Use](https://www.unicode.org/copyright.html) and are released under [LICENSE](./LICENSE).
