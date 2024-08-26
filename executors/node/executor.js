/* Main execution program for Data Driven Test of ICU / Unicode / CLDR
   functions and data.

   This accepts test statements via StdIn in JSON format.

   The type of test determines the corresponding test function that then
   receives the test case. This includes the type of operation, e.g.,
   collation, number format, locale matching, likely subtags, etc.

   The data includes parameters needed to specify the function called as well
   as the test data passed to the function.

   Expected results are not read by this program.

   Output includes test ID and actual results from the test, written to StdOut.
*/


let collator = require('./collator.js');

let numberformatter = require('./numberformat.js');

let displaynames = require('./displaynames.js');

let localedisplaynames = require('./localedisplaynames.js')

let likely_subtags = require('./likely_subtags.js');

let datetime_fmt = require('./datetime_fmt.js');

let list_fmt = require('./list_fmt.js');

let plural_rules = require('./plural_rules.js');

let rdt_fmt = require('./relativedatetime_fmt.js');

/**
 * TODOs:
 * 1. Handle other types of test cases.
 */

/**
 * 21-Mar-2024: Adding datetime and list formatting.
 * 16-Sep-2022: Modularize this, moving functions to other files.
 * 29-Aug-2022: Adding basic decimal test
 * 16-Aug-2022: Collation tests all working now.
 * 09-Aug-2022: Using updated Collation test data, about 10% of the tests fail
 *
 * Started 28-July-2022, ccornelius@google.com
 */

let doLogInput = 0;  // TODO: How to turn this on from command line?
let doLogOutput = 0;

// Test type support. Add new items as they are implemented
const testTypes = {
  TestCollationShort : Symbol("collation_short"),
  TestCollShiftShort : Symbol("coll_shift_short"),
  TestCollNonignorableShort : Symbol("coll_nonignorable_short"),
  TestDecimalFormat : Symbol("decimal_fmt"),
  TestNumberFormat : Symbol("number_fmt"),
  TestDateTimeFormat : Symbol("datetime_fmt"),
  TestPluralRules : Symbol("plural_rules"),
  TestDisplayNames : Symbol("display_names"),
  TestListFmt : Symbol("list_fmt"),
  TestLocaleDisplayNames : Symbol("language_display_name"),
  TestRelativeDateTimeFormat : Symbol("rdt_fmt")
};

const supported_test_types = [
  Symbol("collation_short"),
  Symbol("coll_shift_short"),
  Symbol("coll_nonignorable_short"),
  Symbol("decimal_fmt"),
  Symbol("number_fmt"),
  Symbol("display_names"),
  Symbol("lang_names"),
  Symbol("language_display_name"),
  Symbol("local_info"),
  Symbol("datetime_fmt"),
  Symbol("list_fmt"),
  Symbol("rdt_fmt"),
  Symbol("plural_rules")
];

const supported_tests_json = {
  "supported_tests": [
    "collation_short",
    "coll_shift_short",
    "decimal_fmt",
    "number_fmt",
    "display_names",
    "lang_names",
    "language_display_name",
    "list_fmt",
    "rdt_fmt",
    "plural_rules"
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

  if (testId == "coll_shift_short" || testId == "collation_short") {
    return testTypes.TestCollationShort;
  }
  if (testId == "collation_short") {
    return testTypes.TestCollationShort;
  }
  if (testId == "coll_shift_short") {
    return testTypes.TestCollShiftShort;
  }

  if (testId == "coll_nonignorable_short"){
    return testTypes.TestCollNonignorableShort;
  }

  if (testId == "decimal_fmt" || testId == "number_fmt") {
    return testTypes.TestDecimalFormat;
  }

  if (testId == "display_names") {
    return testTypes.TestDisplayNames;
  }

  if (testId == "language_display_name" || testId == "lang_names") {
    return testTypes.TestLocaleDisplayNames;
  }

  if (testId == "datetime_fmt") {
    return testTypes.TestDateTimeFormat;
  }

  if (testId == "list_fmt") {
    return testTypes.TestListFmt;
  }

  if (testId == "rdt_fmt") {
    return testTypes.TestRelativeDateTimeFmt;
  }

  if (testId == "plural_rules") {
    return testTypes.TestPluralRules;
  }

  console.log("#*********** NODE Unknown test type = " + testId);
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
  //  #VERSION to get version information
  // {....}   test line
  // EXIT
  // Check for commands starting with "#".
  if (line == "#VERSION") {
    // JSON output of the test enviroment.
    const versionJson = {'platform': 'NodeJS',
                         'platformVersion': process.version,
                         'icuVersion': process.versions.icu,
                         'cldrVersion': process.versions.cldr
                        };

    // TODO: Make this more specific for JSON info.
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
      outputLine = {'error': error,
                    'message': 'Cannot parse input line',
                    'input_line': line,
                    "testId": testId};

      // Send result to stdout for verification
      const jsonOut = JSON.stringify(outputLine);
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
    if (test_type == "coll_shift_short" || test_type == "collation_short") {
      outputLine = collator.testCollationShort(parsedJson);
    } else
    if (test_type == "decimal_fmt" || test_type == "number_fmt") {
      outputLine = numberformatter.testDecimalFormat(parsedJson, doLogInput);
    } else
    if (test_type == "display_names") {
      outputLine = displaynames.testDisplayNames(parsedJson);
    } else
    if (test_type == "language_display_name" || test_type == "lang_names") {
      outputLine = localedisplaynames.testLocaleDisplayNames(parsedJson);
    } else
    if (test_type == "likely_subtags") {
      outputLine = likely_subtags.testLikelySubtags(parsedJson);
    } else
    if (test_type == "datetime_fmt") {
      outputLine = datetime_fmt.testDateTimeFmt(parsedJson);
    } else
    if (test_type == "list_fmt") {
      outputLine = list_fmt.testListFmt(parsedJson);
    } else
    if (test_type == "rdt_fmt") {
      outputLine = rdt_fmt.testRelativeDateTimeFmt(parsedJson);
    } else
    if (test_type == "plural_rules") {
      outputLine = plural_rules.testPluralRules(parsedJson);
    } else {
      outputLine = {'error': 'unknown test type',
                    'test_type': test_type,
                    'unsupported_test': test_type};
    }

    const jsonOut = JSON.stringify(outputLine);

    if ('error' in outputLine && !('unsupported' in outputLine)) {
      // To get the attention of the driver
      console.log("#!! ERROR in NODE call: test_type: " + test_type + ", " + JSON.stringify(outputLine));
    }

    // Send result to stdout for verification
    process.stdout.write(jsonOut + '\n');
    if (doLogOutput > 0) {
      console.log("##### NODE RETURNS " + lineId + ' ' + jsonOut + ' !!!!!');
    }

  }
  lineId += 1;
}

     )
