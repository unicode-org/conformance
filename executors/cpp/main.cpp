/*************************************************************************
 *
 *   © 2016 and later: Unicode, Inc. and others.
 *   License & terms of use: http://www.unicode.org/copyright.html
 *
 *************************************************************************
 *************************************************************************
 * COPYRIGHT:
 * Copyright (C) 2002-2006 IBM, Inc.   All Rights Reserved.
 *
 *************************************************************************/

/**
 * This is the executor for C++ for ICU conformance testing.
 * This accepts instructions from the testDriver from STDIN,
 * handles the instruction including calling testing code,
 * and returns results via STDOUT.
 */

const char gHelpString[] =
    "usage: executor"
    "-help            Display this message.\n"
    "-debug n         Level of debug - default = -1\n";

#include <json-c/json.h>

#include <unicode/utypes.h>
#include <unicode/ucol.h>
#include <unicode/ustring.h>
#include <unicode/uvernum.h>

#include <iostream>
#include <string>
#include <vector>

using std::cin;
using std::cout;
using std::endl;
using std::string;

// Test functions
extern auto TestCollator(json_object *json_in) -> const string;
extern auto TestDatetimeFmt(json_object *json_in) -> const string;
extern auto TestLocaleDisplayNames(json_object *json_in) -> const string;
extern auto TestLikelySubtags(json_object *json_in) -> const string;
extern auto TestListFmt(json_object *json_in) -> const string;

// This API was added in ICU75.1
#if U_ICU_VERSION_MAJOR_NUM >= 75
extern const string TestMessageFormat2(json_object *json_in);
#endif

extern auto TestNumfmt(json_object *json_in) -> const string;
extern auto TestPluralRules(json_object *json_in) -> const string;
extern auto TestRelativeDateTimeFmt(json_object *json_in) -> const string;

/**
 * Main   --  process command line, call tests or return data
 *            input is STDIN, output is STDOUT.
 *            commands start with "#"
 *            test data is JSON format
 */
auto main(int argc, const char** argv) -> int {
  // All the currently supported test types.
  std::vector <string> supported_tests;
  supported_tests = {
    "collation_short",
    "datetime_fmt",
    "likely_subtags",
    "list_fmt",
    "lang_names",
    "number_fmt",
    "plural_rules",
    "rdt_fmt"
  };

  for (std::string line; std::getline(cin, line);) {
    if (line == "#EXIT") {
      return 0;
    }
    if (line == "#VERSION") {
      json_object *version = json_object_new_object();
      json_object_object_add(version, "platform",
                             json_object_new_string("ICU4C"));
      json_object_object_add(version, "icuVersion",
                             json_object_new_string(U_ICU_VERSION));
      json_object_object_add(version, "platformVersion",
                             json_object_new_string(U_ICU_VERSION));
      cout << json_object_to_json_string(version) << endl;
    } else if (line == "#TESTS") {
      // TODO: get from the array of supported tests
      json_object *tests_supported = json_object_new_object();
      json_object *test_array = json_object_new_array();

      for (const auto & supported_test : supported_tests) {
        json_object_array_add(
            test_array,
            json_object_new_string(supported_test.c_str()));
      }

      json_object_object_add(tests_supported, "supported_tests", test_array);
      std::cout << json_object_to_json_string(tests_supported) << endl;
    } else {
      // Parse the JSON data.
      // Get the test type and call the test function.

      std::string outputLine;

      struct json_object *json_input;
      json_input = json_tokener_parse(line.c_str());
      json_object *test_type_obj =
          json_object_object_get(json_input, "test_type");
      std::string test_type = json_object_get_string(test_type_obj);

      if (test_type == "collation_short") {
        outputLine = TestCollator(json_input);
      } else if (test_type == "datetime_fmt") {
         outputLine = TestDatetimeFmt(json_input);
#if U_ICU_VERSION_MAJOR_NUM >= 75
      } else if (test_type == "message_fmt2") {
        outputLine = TestMessageFormat2(json_input);
#endif
      } else if (test_type == "number_fmt") {
         outputLine = TestNumfmt(json_input);
      } else if (test_type == "likely_subtags") {
        outputLine = TestLikelySubtags(json_input);
      } else if (test_type == "list_fmt") {
        outputLine = TestListFmt(json_input);
      } else if (test_type == "lang_names") {
        outputLine = TestLocaleDisplayNames(json_input);
      } else if (test_type == "plural_rules") {
        outputLine = TestPluralRules(json_input);
      } else if (test_type == "rdt_fmt") {
        outputLine = TestRelativeDateTimeFmt(json_input);
      } else {
        outputLine =  "# BAD TEST " + test_type;
      }

      // Report back to the test driver.
      cout << outputLine << endl;
    }
  }
  return 0;
}
