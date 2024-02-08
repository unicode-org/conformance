# Executors for Data Driven Test

## What is an "executor"?

Data Driven Test uses executors to run tests in specific platforms, returning
the results as JSON-formatted strings to the testDriver. Each executor
implements a specific language or system such as NodeJS (Javascript), Rust
(ICU4X), Java (ICU4J), etc.

Some prebuilt executors are provided in this repository, but a user may develop
and use custom executors with the testDriver framework. Users are encouraged to
propose new additions to this repository for frameworks of general interest.


## Requirements
An executor must run as a command line program, accepting data from the standard
input stream (stdin). The protocol expected is described below.

Each executor should accept JSON data describing the test to be performed from
stdin. The executor may run a single test on each execution or may perform
multiple tests until it receives a command to stop its operation.

Tests should be stateless, i.e., each test should create a test environment that
does not depend on the results of previous tests or stored states.

## Protocol for communication with testDriver

The testDriver program initiates an executor with a command line such as `nodejs
executor.js`. TestDriver then sends information to the stdin of the running
executor program. These instructions are defined below.

A text executor accepts three kinds of input via the standard input (stdin):
* `#VERSION` - a command that requesting information about the executor’s
  configuration and version. This should be in JSON format. For example:
  `{"cldrVersion":"41.0.0","icuVersion":"icu4x/2022-08-17/71.x","platform":"rust","platformVersion":"1.62.1"}'
* JSON-formatted information on each test to be performed
* `#EXIT` - a command to stop the execution and terminate the instance

Empty lines should be ignored by the executor.

Output from an executor is strictly given through its STDOUT, not via
files. 

Returned values should be in JSON format.

### Errors and exceptions
Exceptions and errors may sometimes occur in the execution. An executor may return errors in two ways:

1. The executor should return JSON data indicating all relevant parameters such
  as "label".

    * When an error occurs, the executor will include a JSON key "error" with the
    value describing the error condition.

2. An executor may also return a line beginning with `#` or `!`, followed by a
  warning or error message that should can be logged to stderr in the output of
  testDriver.

## Examples

Executors are provided for NodeJS and Rust that actually call I18N functions in
the respective platforms. In addition, a simple Python program example is an
example of how a user may create and run additional executors in the DDT
framework under the testDriver.

Executors accept and parse data from stdin, implementing the protocol described
above.

* NodeJS: The file `executor.js` creates objects from classes of the [ECMAScript
  Intl
  object]https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl). Routines
  implement the following types of tests
  * collation: Pairs of strings are compared using the default locale. A numeric
    result of -1, 0, or 1 is returned in the JSON item "result".
  * number formatting: The "options" key indicates the parameters applied to
  * display names: Accepts locale of output
    * Includes "calendar", "currency", "dateTimeField", "language", "region",
      and "script.
    * An input value. The input depends on the type and may be the code for a
      language or locale, e.g., "fr-CA", the code for a region or country, e.g.,
      "NO", etc.
  * language names: tests for the locale-specific name of languages, e.g.,
    "Allemand" for the name of "de" in locale "fr".

* Rust, using ICU4X.
  * [collation](https://icu4x.unicode.org/doc/icu_collator/index.html): Pairs of
    strings are compared using the default locale. A numeric result of -1, 0, or
    1 is returned in the JSON item "result".
  * [fixed decimal](https://icu4x.unicode.org/doc/icu_decimal/index.html):
    supports options available in
    [FixedDecimal](https://icu4x.unicode.org/doc/fixed_decimal/struct.FixedDecimal.html)
