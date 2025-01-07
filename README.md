# Unicode & CLDR Conformance Testing

This repository provides tools and procedures for verifying that an
implementation is working correctly according to the data-based
specifications. The tests are implemented on several platforms including NodeJS
(JavaScript), ICU4X (RUST), ICU4C, etc. Additional programming platforms may be
added to use the test driver framework.

One goal of this work is an easy-to-use framework for verifying that an
implementation of ICU functions agrees with the required behavior. When a test
passes in all implementations, it's a strong indication that results are
consistent across platforms.

A second goal is to find issues in particular implementations of ICU
functions. This is facilitated by generating data from CLDR (in most cases) or
other trusted sources. By highlighting different results than expected,
implementation errors can be highlighted in ways that unit testing in each
platform cannot easily detect.

**Conformance Testing** is also known as **Data Driven Test (DDT)**. It focuses
on functions that accept data input such as numbers, date/time data, and other
basic information. The specifications indicate the expected output from
implementations when given the data and argument settings for each of the many
individual data items.

Note that these tests are only one part of the testing required for
ICU-compliant libraries. Many additional tests are implemented in the
unit tests and other tests of the library implementations themselves.

* !!! TODO: reference to data specifications

#  The big pieces of Conformance Testing

## ICU versions for data and testing

Each ICU test program is built with a specific version of ICU & CLDR data. These
versions are updated periodically. For each ICU version, there is a specific
CLDR version, e.g., ICU73 uses data from CLDR 43, although multiple ICU releases
may depend on the same CLDR data.

For this reason, specifying a particular ICU version for test data or test
executor or both

Each part of Data Driven Testing is designed to handle a specific ICU version.

* Data generation uses specifications starting with ICU versions 70, 71,
  etc. For each ICU release, these data should be updated.

* Test execution allows setting the data version explicitly with a command line
  argument --icuversion that points to the indicated test data. The ICU version
  of the test executor platform is requested from each platform at the start of
  the test driver. Output directories are created under the platform for the
  test results running a particular ICU version, e.g., testOutput/node/icu73.

* Test verification uses ICU version information in the test output files for
  matching with the corresponding expected results. Verification output appears
  in the testResults subdirectory for each node, e.g. testOutput/rust/icu71.
  
* Schema checking uses explict descriptions of the data to be generated and used
in Conformance Testing. These include formats for test data, verification data,
and test output files.

### Terminology for Conformance Testing

* **Platform: a library or software that is executed to produce expected output
  such as formatted text. Examples include ICU4C, ICU4X, and NodeJS.

* **Component**: a type of test such as collation, list format, or plural
  rules. Each platform may implement tests for one or more components.

* **Version**: ICU and CLDR are released periodically with updated data and new
  capabilities. ICU versions are two digit numbers with optional minor revision number per semantic versioning,
  e.g., ICU76 or CLDR76. A platform usually is implemented in multiple ICU
  versions. Platforms should be updated to include each new ICU release.


## Architectural Overview

Conceptually, there are four main functional units of the DDT implementation:

![Conceptual model of Data Driven Testing](./ddt_concept_model.png)

# How to use Conformance Testing on your computer

## Installing Comformance Testing

The Conformance projectis publicly available. It can be installed and executed
on most computer systems. Using GitHub, developers can investigate how the
executors run each of the components. And developers can make changes and create
pull requests to suggest updates to the projectd.

### Get the source from GitHub

1. Create a directory on the computer for installing and running
   Conformance. Note that this may require more that 4 Gbytes when all the tests
   are executed.

1. Next, get the code and data from the [Unicode Conformance GitHub
   site](https://github.com/unicode-org/conformance).

1. From the green Code button on Git button, select one of the options for cloning the
project, or download the project as a ZIP file.

1. Unzip if needed. Then make sure that the directory contains directories for testdriver, testgen, schema, executors, verifier.


### Set up tools and execution environments
Some setup is required to run Data Driven Testing code locally:

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

Note: Setting up Python modules or other software may be better done using a
virtual environment such as using `pip env` for installation.

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

### Running End-To-End on a local computer

Running conformance is easy. Simply execute the script that first generates
data, runs executors, checks data against schema, and then runs the verifier,
creating the dashboard.

The standard script runs all components on all platforms with all ICU
version. Note that this takes a few minutes.

```bash
bash generateDataAndRun.sh
```

Output will be created in the directory TEMP_DATA.

To run a quicker version that uses only 100 test cases for each instance, run this:

```bash
bash genData100.sh
```
which does the same thing much faster, resulting in the directory TEMP_DATA_100.

### Viewing conformance results in a browser
HTML output is found in the subdirectory testReports. To visualize this on your
computer, start a webserver. For example:

```bash
python3 -m http.server 9000 &
```

Then open the file testResults/index.html under the testReports folder in either
TEMP_DATA or TEMP_DATA_100 or in a custom folder.


### How this works

Two main pieces are used to create conformance output:
* run_config.json which describes the platforms and components to be executed

* execution scripts that run all the steps of conformance testing. This file
  extracts configurations from run_config
  
    *generateDataAndRun.sh* runs tests across all platforms, components, and ICU
    versions.

    *run_config.json* file is read by the execution scripts such as *generateDataAndRun.sh*

#### Execution script functions

The execution scripts perform several steps in sequence:

1. Special configuration to set up test environments for

    1. ICU4C versions

    1. NodeJS releases
    
    1. ICU4X using Rust

    1. Dart native and Dart web

1. Set the output directory as TEMP_DIR. Remove old data and create new output areas.

1. Generate all test data based on run_config's requirements
    1. This includes checking each generated test set and expected results against schema.

1. Check all the schema files for correct structure


1. Execute all specified tests using testdriver with the executors.

1. Evaluate all test output files against schema for test results.

1. Run the verifier on all testOutputs, creating testReports

### Running individual executors and debugging

Running  all  of  the  steps  above  may  not  be  needed  for  development  and
debugging. To facilitate quicker coding and testing, it may be useful to run using the 100 test case sample set.


The file run_config.json is simply a list of configuration information for
running selected versions of a platform with selected test types
(components). Here's an entry for ICU4C in version 76 that runs 7 components:

```json
[
  {
    "prereq": {
      "name": "Get ICU4C 76",
      "version": "76.1",
      "command": "bash ../executors/cpp/set_icu4c_binary.sh ../gh-cache/icu4c-76_1-Ubuntu22.04-x64.tgz"
    },
    "run": {
      "icu_version": "icu76",
      "exec": "cpp",
      "test_type": [
        "collation_short",
        "datetime_fmt",
        "lang_names",
        "likely_subtags",
        "message_fmt2",
        "number_fmt",
        "plural_rules"
      ],
      "per_execution": 10000
    }
  },
  ...
]
```

The section *prereq* is run before this particular executor `cpp` is run under
`testdriver`. The value of `per_execution` deteremines how many tests are passed
to a single instantiation of a test executor.

To use quicker development mode, do the following:

1. Clone run_config.json. Include only the executors and/or components that are
   being developed. Also consider selecting only the ICU version or versions
   needed.

1. Close one of the executions scripts to create a custom version. Change the
   reference from `run_config.json` to the modified version. Note
   that `export TEST_LIMIT=` may be changed to test a smaller set of cases. Note
   that this may also point to a custom directory for the output under the
   conformance directory.

To use this, simply execute the custom script using `bash` or equivalent in the
environment:

```bash
bash my_custom_script.sh
```

Then point the browser to `index.html` in the custom output folder in order to
view the summary and detail pages.

Also note: when customized testing is satisfactory, next run `genData100.sh` and
generateDataAndRun.sh` scripts to check if the full testing environment succeeds.

### Notes on finding errors

As each part of Conformance Test is executed, log files are created with the
output of each phase. Thes include output from python programs, executores, and scripts.

The files containing this logging infromation are called `debug.log, debug.log.1`,
etc.  These debug files are updated on each execution of the scripts in each of
these subdirectories:
* testgen
* testdriver
* schema
* verifier

It is useful to review the latest debug.log file for each phase in order to
identify errors in execution, warning messages, and possible failures.

Note that the log rotation automatically maintains recent history in several
versions of debug files in each subdirectory listed above.

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
    ```json
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
    ```json
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
  particular execution platform, i.e., programming languages.

* **Expected results** of running each test running with the specified ICU
  version. This does not depend on the platform.

* **Actual results** from executing each test in the input. This contains actual
  results from the execution of each test in a given platform. This data may
  include output from the executor including platform-specific parameters and
  settings derived from the input data. It may also include data on errors
  encountered during the run of the platform executor.

* **Schema files** describing the expected JSON format of each type of files for
  the components.

Schema validation is performed at these points in standard processing:

1. After test data generation, all generated test data and expected result data
   files are checked for correct structure.

2. Before test execution, the schema files themselves are checked for correct
   schema structure.

3. After test executors are run, all resulting test output files are checked
   for correct structure.

### Schema file directory structure
The top level directory `schema` contains the following:

* Python routines for checking these types of data.

* A Python routine for validating the structure of the .json schema files.

* One subdirectory for each component such as "collation". This contains schema
  .json files for generated tests, expected results, and test output structure.

```bash
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

Note also that schema validation creates a file
**schema/schema_validation_summary.json**
which is used in the summary presentation of Conformance results.

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

In the final phase of Conformance Testing, each individual test is matched with
the corresponding data from the required test results. A report of the test
results is generated. Several kinds of status values are possible for each test
item:

* **Success**: the actual result agrees with expected results

* **Failure**: a result is generated, but the result is not the same as the
expected value.

* **Error**: the test resulted in an exception or other behavior not anticipated
for the test case.

* **Known issue**: The test failure or error is known for the version of the
  platform and ICU. Note that each type of known issue should reference a
  publicly documented issue in ICU or CLDR.

* **Unsupported**: Some aspect of the requested test is not yet supported by the
  platform and ICU version.

* **No test run**: The test was not executed by the test implementation for the data.

### Open questions for the verifier
* What should be done if the test driver fails to complete? How can this be
  determined?

    * Proposal: each test execution shall output a completion message,
indicating that the test driver finished its execution normally, i.e., did not
crash.


# How to update Conformance Testing: ICU versions, platforms, components

Data Driven Testing is expected to remain current with ICU programs and data
updates. It is also designed to support new testing platforms in addition to the
current set of Dart, ICU4C, ICU4J, ICU4X, and NodeJS. And new types of tests,
i.e., "components", may be added to Conformance testing.

This section describes the process for keeping DDT up to date with needed test
types and required programming platforms

## Incorporating new ICU  / CLDR versions into DDT

ICU releases are usually made twice each calendar year, incorporating new data,
fixes, and new test files. ICU versions may also add new types of data
processing. A recent example is Message Format 2.

Because Data Driven Testing operations with multiple ICU and CLDR versions, this
system should be updated with each new ICU release. Here are several pull
requests for recent ICU updates:

* [ICU 76 for C++](https://github.com/unicode-org/conformance/pull/325/)

* [ICU 76 for Java](https://github.com/unicode-org/conformance/pull/344)

* [ICU76 for NodeJS](https://github.com/unicode-org/conformance/pull/348)

### ICU4C updates

These are usually the first changes to be made because ICU4C includes updates to code,
locale data, and test data for many components.

1. Test Driver:
* Add new ICU version data in several places in testdriver/datasets.py

2. testgen:
* Add a new directory for the icu version under testgen, e.g., icu76

* In this directory, copy test data from sources including icu4c/source. These
  files include collation tests, number format data, and others.

!!! TODO: Add details on the sources.

* Add new CLDR test data generated from CLDR sources (!!! details !!!)

3. schema: Add any new parameters in test data sources to test schema files.

4. Add a function in setup.sh to download the new ICU4C release.

5. Update run_config.json to reference new versions of executors and tests to run

### NodeJS and some data updates

NodeJS is usually updated several weeks after an ICU public release. Check on
the site [Node.js Releases](https://nodejs.org/en/about/previous-releases) for
the latest versions of NodeJS. Under each entry, the "changelog" will indicate
any updates to icu, e.g., [Version 23.3.0 on 2024-11-20]
(https://github.com/nodejs/node/blob/main/doc/changelogs/CHANGELOG_V23.md#23.3.0) which includes ICU76.1.

#### Add references in testdriver/datasets.py

In this file, add new Enum values to variables:
* NodeVersion

* IcuVersionToExecutorMap

* NodeICUVersionMap

#### Update run_config.json
Add the new NodeJS version to the run configurations. This includes the command
to install and use the latest NodeJS versions. Here's the new entry for ICU76.1
in NodeJS 23.3.0.

Be sure to add the new version number in both the `nvm install` and `nvm use`
parts of `command`.

Also, include all the tests to be run with this version of NodeJS.

```json
  {
    "prereq": {
      "name": "nvm 23.3.0, icu76.1",
      "version": "23.3.0",
      "command": "nvm install 23.3.0;nvm use 23.3.0 --silent"
    },
    "run": {
      "icu_version": "icu76",
      "exec": "node",
      "test_type": [
        "collation_short",
        "datetime_fmt",
        "list_fmt",
        "number_fmt",
        "lang_names",
        "likely_subtags",
        "rdt_fmt",
        "plural_rules"
      ],
      "per_execution": 10000
    }
  },
```

### Update ICU4J /Java to new ICU version

** TBD **
This requires referencing the new ICU4J versions in Maven Central (!!! REFERENCE NEEDED !!!)

#### run_config.json additions for Java

Updates to this file are straightforward.

### Update ICU4X / Rust to new ICU version

** TBD **

ICU4X is actively updating APIs in each new version. ICU4X releases are not
closely coordinated with ICU versions.

Adding a new ICU4X version after 1.4 may require significant changes to existing
#### run_config.json additions for ICU4X

Updates to this file are straightforward.

### Update Dart with new ICU versions

** TBD **


#### Test generator updates
Expected values for tests are obtained from several places:

* the preferred sources are generated directly from CLDR data, not mediated by
  ICU libraries. These test files are generated by programs run within the CLDR
  directories and are updated with each CLDR release.

* The second is test data used in ICU4C or ICU4J testing. For example, ICU4C
  includes 3 test files for collation that are then used by all platforms.

* Two types of test data are currently generated by NodeJS functions:
  * list format
  * relative date time format

Because of this, ICU version updated tests for these two components cannot be
run before adding a version of NodeJS that includes the new ICU version.

When the new NodeJS is incorporated into DDT, add the new NodeJS reference to
the list `icu_nvm_versions` in these files:

* testgen/generators/list_fmt.py
* testgen/generators/relativedatetime_fmt.py


## Adding New Test Types / Components
ICU supports a wide range of formatting and other functions. Many are candidates
for Conformance Testing. Although each has specific needs for testing, this
section presents an overview on adding new test types.

As an example, pull request
[PR#183](https://github.com/unicode-org/conformance/pull/183/files) added
datetime, list format, and relative date time format to test generation, test
executors, test driver, schema, verifier, and runtime configuration.

Also, see [ICU4J and relative date time format
PR#262](https://github.com/unicode-org/conformance/pull/262/files) for
details of adding a component to the ICU4J platform.

Note also that the above PR added an [executor file for the Rust /
ICU4X](https://github.com/unicode-org/conformance/pull/262/files#diff-f2bce2a303cd07f48c087c798a457ff78eeefbde853adb6a8c331f35b1b5571d)
version or relative date time format.

These are the main parts needed to add a component:

1. Add methods to create the test data in testgen/icu* and
   testgen/generators. Resulting .json files with test and verification data
   should be installed in testgen/icuXX directories as needed.

* Create python modules in testgen/generators/ to read raw test data, then
  create .json file with tests and expected resuls.

* Update testgen/tesdata_gen.py with:
* Import new test generator modules
* Add new Enum values
* Add code to execute* the new generator modules

2. Define new test types in these testdriver files:
* datasets.py
* ddtargs.py
* testdriver.py
* testplan.py

3. Executors: For each executor to run the new tests:
* Add a new code file to run the tests in the executor directory, e.g.,
  `executors/cpp`

* Update configuration information such as makefiles to include the new testing
  code

* Include calling the new test routines in the main program, e.g,. `main.cpp`

Hint: Run the executor as a standalone test version, giving sample tests on the
command line or in structured test code (i.e., ICU4J's framework.)

Once the executor is working with the new test type, incorporated it into
the full execution pipeline.

4. Update run_config.json with the new test_type in each executor supporting
   the component.

For reference,
[PR#183](https://github.com/unicode-org/conformance/pull/183/files) added these
components for datetime, list format, and relative date time format.

## Adding new test platforms, e.g., types of libraries

As additional test platforms and libraries support all or part of the ICU / CLDR
functions, including them in Conformance Testing will show the degree of
compatibility of actual execution.

See [Add Dart to executors
PR#65](https://github.com/unicode-org/conformance/pull/65) for an example.

See also the
[Rust executor for ICU4x 1.3 in PR#108](https://github.com/unicode-org/conformance/pull/108)

Adding a new platform involves several changes to the DDT system:
* Change the workflow to reference the new platform

* Create a new directory structure under executors/. Add .gitignore as needed.

* Add configuration specific to the platform in the new directory under executors/

* Set up a main program that will receive instructions on the STDIN command line

    * Parse the incoming JSON data to determine test type

    * Build separate files for running each type of test

    * Return results from each testing routine in JSON format

* Support the commands for information:
    * `#VERSION`
    * `#TEST`
    * etc.

* Update `testdriver/datasets.py` to include the new executor platform.


Note: it is very helpful to include sets of tests for the new platform for each
supported component. The ICU4J model with Intellij is a good example.

Make sure that your new executor can be run from a debugging environment or from
the command line. Tests can be tested easily here before adding them to the full execution scripts.

* Add the new platform to `run_config.json` including required setup and the implemented
  components for the DDT workflow.


See [Add Dart to executors
PR#65](https://github.com/unicode-org/conformance/pull/65) for am example.

See also the [Rust executor for ICU4x 1.3 in
PR#108](https://github.com/unicode-org/conformance/pull/108)


## Conformance Data models

### Directory `testData`:

Conformance Testing uses JSON formatted data files to describe tests and
parameters as well as to record test results and deliver information for the results dashboard. 

Test generation creates the test and verify data files for each version of ICU
in .json format:

  * A test data file for each type of test. Each contains a list of labeled
  tests with parameters, options, and input values for computing output
  strings.

  * Verify files for each test type. Each contains expected results for each
    test case.

For example, here is the structure for directory `toplevel`:

```bash
toplevel/testData/
├── icu67
│   └── ...
├── icu68
│   └── ...
...
├── icu76
│   ├── collation_test.json
│   ├── collation_verify.json
│   ├── datetime_fmt_test.json
│   ├── datetime_fmt_verify.json
│   ├── lang_name_test_file.json
│   ├── lang_name_verify_file.json
│   ├── likely_subtags_test.json
│   ├── likely_subtags_verify.json
│   ├── list_fmt_test.json
│   ├── list_fmt_verify.json
│   ├── message_fmt2_test.json
│   ├── message_fmt2_verify.json
│   ├── numberformattestspecification.txt
│   ├── numberpermutationtest.txt
│   ├── num_fmt_test_file.json
│   ├── num_fmt_verify_file.json
│   ├── plural_rules_test.json
│   ├── plural_rules_verify.json
│   ├── rdt_fmt_test.json
│   └── rdt_fmt_verify.json

```

### Directory `testOutput`

This contains a subdirectory for each executor. The output file from each test
is stored in the appropriate subdirectory. Each test result contains the label
of the test and the result of the test. This may be a boolean or a formatted
string.

The results file contains information identifying the test environment as well
as the result from each test. As an example, collation test results from the
`testOutput/node` file are shown here:

```json
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

And the overall structure:
```bash
toplevel/testOutput/
├── cpp
│   ├── icu71
│   ├── icu72
│   ├── icu73
│   ├── icu74
│   ├── icu75
│   └── icu76
├── dart_web
│   └── icu73
├── icu4j
│   ├── icu73
│   ├── icu74
│   ├── icu75
│   └── icu76
├── node
│   ├── icu69
│   ├── icu70
│   ├── icu71
│   ├── icu72
│   ├── icu73
│   ├── icu74
│   ├── icu75
│   └── icu76
├── rust
│   ├── icu73
│   └── icu74
└── test_output_validation_summary.json
```

And showing details for the icu76 output from ICU4J:

```bash
toplevel/testOutput/icu4j/icu76
├── collation_test.json
├── datetime_fmt_test.json
├── lang_name_test_file.json
├── likely_subtags_test.json
├── list_fmt_test.json
├── message_fmt2_test.json
├── num_fmt_test_file.json
├── plural_rules_test.json
└── rdt_fmt_test.json
```

### Directory `testReports`

This directory stores summary results from verifying the tests performed by each
executor. Included in the `testReports` directory are:

* `index.html`: shows all tests run and verified for all executors and
  versions. Requires a webserver to display this properly.

* `exec_summary.json`: contains summarized results for each pair (executor, icu
  version) in a graphical form. Contains links to details for each test pair.

* a subdirectory for each executor, each containing verification of the tested
  ICU versions, e.g., `node/`, `rust/`, etc.

Under each executor, one or more ICU version directories are created, such as
`icu76`. Each ICU version contains data for the detailed report:

* `verfier_test_report.html` - for showing results to a user via a web server

* `verfier_test_report.json` - containing verifier output for programmatic use

* `failing_tests.json` - a list of all failing tests with input values
* `pass.json` - list of test cases that match their expected results
* `test_errors.json` - list of test cases where the executor reported an error
* `unsupported.json` - list of test cases that are not expected to be supported
  in this version

The `verifier_test_report.json` file contains information on tests run and
comparison with the expected results. At a minimum, each report contains:

* The executor and test type
* Date and time of the test
* Execution information, from the testResults directory
* Total number of tests executed
* Total number of tests failing
* Total number of tests succeeding
* Number of exceptions identified in the test execution. This may include
  information on tests that could not be executed, along with the reasons for
  the problems.
* Analysis of test failures, if available. This may include summaries of string
  differences such as missing or extra characters or substitutions found in
  output data.

Example for details of ICU4C, version 76 of root directory **toplevel**:


```bash
toplevel/testReports/cpp/icu76/number_fmt/
├── error_characterized.json
├── fail_characterized.json
├── failing_tests.json
├── failure_parameters.json
├── known_issues_characterized.json
├── known_issues.json
├── pass_characterized.json
├── pass.json
├── test_errors.json
├── unsupported_characterized.json
├── unsupported.json
├── verifier_test_report.html
└── verifier_test_report.json
```

# History

Data Driven Test was initiated in 2022 at Google. The first release of the
package was delivered in October, 2022.

### Copyright & Licenses

Copyright © 2022-2024 Unicode, Inc. Unicode and the Unicode Logo are registered
trademarks of Unicode, Inc. in the United States and other countries.

A CLA is required to contribute to this project - please refer to the
[CONTRIBUTING.md](https://github.com/unicode-org/.github/blob/main/.github/CONTRIBUTING.md)
file (or start a Pull Request) for more information.

The contents of this repository are governed by the Unicode [Terms of
Use](https://www.unicode.org/copyright.html) and are released under [LICENSE](./LICENSE).
