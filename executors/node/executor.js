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

let displaynames = require('./displaynames.js')

let langnames = require('./langnames.js')

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

// Test type support. Add new items as they are implemented
const testTypes = {
  TestCollShiftShort : Symbol("coll_shift_short"),
  TestDecimalFormat : Symbol("decimal_fmt"),
  TestNumberFormat : Symbol("number_fmt"),
  TestDateTimeFormat : Symbol("datetime_fmtl"),
  TestRelativeDateTimeFormat : Symbol("relative_datetime_fmt"),
  TestPluralRules : Symbol("plural_rules"),
  TestDisplayNames : Symbol("display_names"),
  TestLangNames : Symbol("language_display_name"),
}

const supported_test_types = [
  Symbol("coll_shift_short"),
  Symbol("decimal_fmt"),
  Symbol("number_fmt"),
  Symbol("display_names"),
  Symbol("language_display_name")
];
const supported_tests_json = {"supported_tests":
                              [
                                "coll_shift_short",
                                "decimal_fmt",
                                "number_fmt",
                                "display_names",
                                "language_display_name"
                              ]};

// Test line-by-line input, with output as string.
// Check on using Intl functions, e.g., DateTimeFormat()

let readline = require('readline');
let rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

/**
 * Given a JSON data structure, check for "test_type". If not present, then
 * infer the test ID from the label
 * !!! Not used now.
 */
function parseJsonForTestId(parsed) {
  let testId = parsed["test_type"];

  if (testId == "coll_shift_short") {
    return testTypes.TestCollShiftShort;
  }
  if (testId == "decimal_fmt" || testId == "number_fmt") {
    return testTypes.TestDecimalFormat;
  }
  if (testId == "display_names") {
    return testTypes.TestDisplayNames;
  }
  if (testId == "language_display_name") {
    return testTypes.TestLangNames;
  }
  console.log("#*********** Unknown test type = " + testId);
  return null;

  // No test found.
  return null;
}

// Read JSON tests, each on a single line.
// Process the test and output a line of JSON results.
let lineId = 0;
rl.on('line', function(line) {

  // if logging input.
  if (doLogInput > 0) {
    console.log("## NODE RECEIVED " + lineId + ' ' + line + ' !!!!!');
  }

  // Protocol:
  //  #VERSION to get version informatin
  // {....}   test line
  // EXIT
  // Check for commands starting with "#".
  if (line == "#VERSION") {
    // JSON output of the test enviroment.
    let versionJson = {'platform': 'NodeJS',
                       'platformVersion': process.version,
                       'icuVersion': process.versions.icu,
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
      outputLine = {'Cannot parse input line': error,
                    'input_line': line,
                    "testId": testId};

      // Send result to stdout for verification
      jsonOut = JSON.stringify(outputLine);
      process.stdout.write(jsonOut);
    }

    if (doLogInput > 0) {
      console.log("#----- PARSED JSON: " + JSON.stringify(parsedJson));
    }

    // testId = parseJsonForTestId(parsedJson);
    // Handle the string directly to  call the correct function.
    const test_type = parsedJson["test_type"];
    if (test_type == "coll_shift_short") {
      outputLine = collator.testCollationShort(parsedJson);
    } else
    if (test_type == "decimal_fmt" || test_type == "number_fmt") {
      outputLine = numberformatter.testDecimalFormat(parsedJson);
    } else
    if (test_type == "display_names") {
      outputLine = displaynames.testDisplayNames(parsedJson);
    } else
    if (test_type == "language_display_name") {
      outputLine = langnames.testLangNames(parsedJson);
    } else {
      outputLine = {'error': 'unknown test type', 'testId': testId,
                    'unsupported_test': testId};
    }

    // Send result to stdout for verification
    jsonOut = JSON.stringify(outputLine);
    process.stdout.write(jsonOut + '\n');

    lineId += 1;
  }
}
     )
