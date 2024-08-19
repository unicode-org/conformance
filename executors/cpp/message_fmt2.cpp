/********************************************************************
 * testing message format 2 in C++
 */

#include <unicode/utypes.h>

#include <json-c/json.h>

// This API was added in ICU75.1
#if U_ICU_VERSION_MAJOR_NUM >= 75

#include <unicode/locid.h>
#include <unicode/messageformat2.h>
#include <unicode/messageformat2_arguments.h>
#include <unicode/messageformat2_data_model.h>
#include <unicode/messageformat2_function_registry.h>
#include <unicode/messageformat2_formattable.h>
#include <unicode/msgfmt.h>
#include <unicode/unistr.h>

#include <stdio.h>
#include <stdlib.h>

#include <iostream>
#include <string>
#include <cstring>

#include "util.h"

using icu::Locale;
using icu::message2::MessageFormatter;
using icu::message2::MessageArguments;
using icu::message2::Formattable;

using icu::UnicodeString;

using std::string;

/* Based on this test file:
 * https://github.com/unicode-org/icu/blob/main/icu4c/source/test/intltest/messageformat2test.cpp
 */
const string TestMessageFormat2(json_object *json_in) {
  // label information
  json_object *label_obj = json_object_object_get(json_in, "label");
  string label_string = json_object_get_string(label_obj);

  json_object *locale_label_obj = json_object_object_get(json_in, "locale");
  string locale_string = "und";
  if (locale_label_obj) {
    locale_string = json_object_get_string(locale_label_obj);
  }

  const Locale displayLocale(locale_string.c_str());

  string src_string;
  json_object *src_obj = json_object_object_get(json_in, "src");
  UnicodeString u_src;
  if (src_obj) {
    src_string = json_object_get_string(src_obj);
    u_src = src_string.c_str();
  }

  string test_description_string;
  json_object *test_description_obj =
      json_object_object_get(json_in, "test_description");
  if (test_description_obj) {
    test_description_string = json_object_get_string(test_description_obj);
  }

  // Start filling the return data.
  json_object *return_json = json_object_new_object();
  json_object_object_add(return_json, "label", label_obj);

  json_object* param_list_obj = json_object_object_get(json_in, "params");

  string params_name;
  UnicodeString u_params_name;
  string params_value;
  UnicodeString u_params_value;

  // Get all the argements from test params
  std::map<UnicodeString, Formattable> argsBuilder;

  if (param_list_obj) {
    array_list* param_list = json_object_get_array(param_list_obj);

    // For each item in the params list, get the name and value.
    // Add to the builder.
    int params_length = json_object_array_length(param_list_obj);

    // Construct the list of Unicode Strings
    for (int i = 0; i < params_length; i++) {
      json_object* param_obj = json_object_array_get_idx(param_list_obj, i);

      // Get the fields from this indexed element of the param_list
      json_object *params_name_obj = json_object_object_get(param_obj, "name");
      json_object *params_value_obj =
          json_object_object_get(param_obj, "value");

      if (params_name_obj && params_value_obj) {
        params_name = json_object_get_string(params_name_obj);
        u_params_name = params_name.c_str();

        params_value = json_object_get_string(params_value_obj);
        u_params_value = params_value.c_str();

        argsBuilder[u_params_name] = Formattable(u_params_value);
      } else {
        // Bail out due to incomplete parameter
        if (check_icu_error(
                U_MESSAGE_PARSE_ERROR,
                return_json, "incomplete param name / value")) {
          return json_object_to_json_string(return_json);
        }
      }
    }  // End of parameter loop
  }  // End parameter list processing

  UParseError parseError;
  UErrorCode errorCode = U_ZERO_ERROR;

  MessageFormatter::Builder builder(errorCode);
  if (check_icu_error(errorCode, return_json, "contructing builder")) {
    return json_object_to_json_string(return_json);
  }

  MessageFormatter mf = builder.setPattern(u_src, parseError, errorCode)
                        .setLocale(displayLocale)
                        .build(errorCode);
  if (parseError.line > 0) {
    // Information on position and preContext / postContext of parse error
    string precontext_string, postcontext_string;
    UnicodeString preContext = parseError.preContext;
    preContext.toUTF8String(precontext_string);
    UnicodeString postContext = parseError.postContext;
    postContext.toUTF8String(postcontext_string);

    // Build a message with all parsing info.
    string message = "Parse error on line: " +
                     std::to_string(parseError.line) +
                     " at offset: " +
                     std::to_string(parseError.offset) +
                     " precontext: " +
                     precontext_string +
                     " postcontext: " +
                     postcontext_string;

    if (check_icu_error(U_PARSE_ERROR, return_json, message.c_str())) {
      return json_object_to_json_string(return_json);
    }
  }

  if (check_icu_error(errorCode, return_json, "build.setPattern")) {
    return json_object_to_json_string(return_json);
  }

  MessageArguments args(argsBuilder, errorCode);
  if (check_icu_error(errorCode, return_json, "construction args")) {
    return json_object_to_json_string(return_json);
  }

  UnicodeString result_ustring = mf.formatToString(args, errorCode);
  if (check_icu_error(errorCode, return_json, "formatToString")) {
    return json_object_to_json_string(return_json);
  }

  // Get the resulting value and return JSON result.
  string result_string;
  result_ustring.toUTF8String(result_string);

  // It worked!
  json_object_object_add(return_json,
      "result", json_object_new_string(result_string.c_str()));

  return json_object_to_json_string(return_json);
}

#endif  // U_ICU_VERSION_MAJOR_NUM >= 75
