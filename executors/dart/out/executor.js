/* Main execution program for Data Driven Test of ICU / Unicode / CLDR
   functions and data.

   This accepts test statements via StdIn in JSON format.

   The type of test determines the corresponding test function that then
   receives the test case. This includes the type of operation, e.g.,
   collation, number format, locale matching, etc.

   The data includes parameters needed to specify the function called as well
   as the test data passed to the function.

   Expected results are not read by this program.

   Output includes test ID and actual results from the test, written to StdOut.
*/


let collator = require('./collator.js')

let numberformatter = require('./numberformat.js')

let likely_subtags = require('./likely_subtags.js')

let lang_names = require('./lang_names.js');

const { dartVersion } = require('./version.js')

/**
 * TODOs:
 * 1. Handle other types of test cases.
 */

/**
 * 16-Sep-2022: Modularize this, moving functions to other files.
  * 29-Aug-2022: Adding basic decimal test
  * 16-Aug-2022: Collation tests all working now.
  * 09-Aug-2022: Using updated Collation test data, about 10% of the tests fail
  *
  * Started 28-July-2022, ccornelius@google.com
 */

let doLogInput = 0;
let doLogOutput = 0;

const supported_tests_json = {
  "supported_tests":
    [
      "coll_shift_short",
      "collation_short",
      "decimal_fmt",
      "number_fmt",
      "display_names",
      "language_display_name"
    ]
};

// Test line-by-line input, with output as string.
// Check on using Intl functions, e.g., DateTimeFormat()

let readline = require('readline');
let rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

// Read JSON tests, each on a single line.
// Process the test and output a line of JSON results.
let lineId = 0;
rl.on('line', function (line) {

  // if logging input.
  if (doLogInput > 0) {
    console.log("## NODE RECEIVED " + lineId + ' ' + line + ' !!!!!');
  }

  // Protocol:
  //  #VERSION to get version information
  // {....}   test line
  // EXIT
  // Check for commands starting with "#".
  if (line == "#VERSION") {
    // JSON output of the test enviroment.
    let versionJson = {
      'platform': 'Dart Web',
      'platformVersion': process.version,
      'icuVersion': process.versions.icu,
      'intlVersion': dartVersion,
    };

    // TODO: Make this more specific JSON info.
    lineOut = JSON.stringify(versionJson);
    process.stdout.write(lineOut);
  } else
    if (line == "#EXIT") {
      process.exit();
    } else
      if (line == "#TESTS") {
        lineOut = JSON.stringify(supported_tests_json);
        process.stdout.write(lineOut);
      }
      else {
        // Handle test cases.
        let testId;
        let parsedJson;
        try {
          parsedJson = JSON.parse(line);
        } catch (error) {
          outputLine = {
            'Cannot parse input line': error,
            'input_line': line,
            "testId": testId
          };

          // Send result to stdout for verification
          jsonOut = JSON.stringify(outputLine);
          if (doLogOutput > 0) {
            console.log("## ERROR " + lineId + ' ' + outputLine + ' !!!!!');
          }
          process.stdout.write(jsonOut);
        }

        if (doLogInput > 0) {
          console.log("#----- PARSED JSON: " + JSON.stringify(parsedJson));
        }

        // Handle the string directly to  call the correct function.
        const test_type = parsedJson["test_type"];
        if (test_type == "collation_short") {
          outputLine = collator.testCollationShort(parsedJson);
        } else if (test_type == "decimal_fmt" || test_type == "number_fmt") {
          outputLine = numberformatter.testDecimalFormat(parsedJson, doLogInput > 0, process.version);
        } else if (test_type == "likely_subtags") {
          outputLine = likely_subtags.testLikelySubtags(parsedJson);
        } else if (test_type == "language_display_name" || test_type == "lang_names") {
          outputLine = lang_names.testLangNames(parsedJson);
        } else {
          outputLine = {
            'error': 'unknown test type', 'testId': testId,
            'unsupported_test': testId
          };
        }

        if ('error' in outputLine) {
          // To get the attention of the driver
          console.log("#!! ERROR in DART_WEB: " + test_type + ": " + JSON.stringify(outputLine));
        }

        // Send result to stdout for verification
        jsonOut = JSON.stringify(outputLine);
        process.stdout.write(jsonOut + '\n');
        if (doLogOutput > 0) {
          console.log("##### NODE RETURNS " + lineId + ' ' + jsonOut + ' !!!!!');
        }

      }
  lineId += 1;
}
)
