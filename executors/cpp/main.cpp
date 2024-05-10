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

#include <iostream>
#include <string>

#include "unicode/utypes.h"
#include "unicode/ucol.h"
#include "unicode/ustring.h"
#include "unicode/uvernum.h"

using std::cin;
using std::cout;
using std::endl;
using std::string;

// Test functions
extern const string test_collator(json_object *json_in);
extern const string test_datetime_fmt(json_object *json_in);
extern const string test_langnames(json_object *json_in);
extern const string test_likely_subtags(json_object *json_in);
extern const string test_list_fmt(json_object *json_in);
extern const string TestPluralRules(json_object *json_in);
extern const string test_numfmt(json_object *json_in);

string supported_tests[7] = {
  "collation_short",
  "datetime_fmt",
  "likely_subtags",
  "list_fmt",
  "lang_names",
  "plural_rules",
  "number_fmt"
};


string cppVersion = "1.0";

/**
 * Main   --  process command line, call tests or return data
 *            input is STDIN, output is STDOUT.
 *            commands start with "#"
 *            test data is JSON format
 */
int main(int argc, const char** argv)
{
  for (string line; std::getline(cin, line);) {
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
      for (int index = 0; index < 4; index ++) {
        json_object_array_add(
            test_array,
            json_object_new_string(supported_tests[index].c_str()));
      }

      json_object_object_add(tests_supported, "supported_tests", test_array);
      std::cout << json_object_to_json_string(tests_supported) << endl;
    } else {
      // Parse the JSON data.
      // Get the test type and call the test function.

      string outputLine;

      struct json_object *json_input;
      json_input = json_tokener_parse(line.c_str());
      json_object *test_type_obj =
          json_object_object_get(json_input, "test_type");
      string test_type = json_object_get_string(test_type_obj);

      // Handle each type of test.
      if (test_type == "collation_short") {
        outputLine = test_collator(json_input);
      } else if (test_type == "datetime_fmt") {
        outputLine = test_datetime_fmt(json_input);
      } else if (test_type == "number_fmt") {
        outputLine = test_numfmt(json_input);
      } else if (test_type == "likely_subtags") {
        outputLine = test_likely_subtags(json_input);
      } else if (test_type == "list_fmt") {
        outputLine = test_list_fmt(json_input);
      } else if (test_type == "lang_names") {
        outputLine = test_langnames(json_input);
      } else if (test_type == "plural_rules") {
        outputLine = TestPluralRules(json_input);
      } else {
        outputLine =  "# BAD TEST " + test_type;
        //       "{\"error\": \"unknown test type\"," +
        //       "\"test_type\":" +  test_type + "," +
        //       "\"unsupported_test:\"" + test_type + "}";
      }
      cout << outputLine << endl;
    }
  }
  return 0;
}
