/********************************************************************
 * testing message format 2 in C++
 */

#include <json-c/json.h>

#include <unicode/locid.h>
#include <unicode/messageformat2.h>
#include <unicode/utypes.h>

#include "unicode/messageformat2_arguments.h"
#include "unicode/messageformat2_data_model.h"
#include "unicode/messageformat2_function_registry.h"
#include "unicode/unistr.h"

#include <stdio.h>
#include <stdlib.h>

#include <iostream>
#include <string>
#include <cstring>

using icu::Locale;
using icu::MessageFormattermessage2;

using std::cout;
using std::endl;
using std::string;

const string TestMessageFormat2(json_object *json_in) {
  UErrorCode status = U_ZERO_ERROR;

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
  if (src_obj) {
    src_string = json_object_get_string(src_obj);
  }

  json_object *params_obj = json_object_object_get(json_in, "params");

  string params_name;
  string params_value;

  if (params_obj) {
    json_object *params_name_obj = json_object_object_get(params_obj, "name");
    if (params_name_obj) {
      params_name = json_object_get_string(params_name_obj);
    }

    json_object *params_value_obj = json_object_object_get(params_obj, "value");
    if (params_value_obj) {
      params_value = json_object_get_string(params_value_obj);
    }
  }

  // Start filling the return data.
  json_object *return_json = json_object_new_object();
  json_object_object_add(return_json, "label", label_obj);

  if (U_FAILURE(status)) {
    const char* error_name = u_errorName(status);
    json_object_object_add(
        return_json,
        "error", json_object_new_string("error in constructor"));
    json_object_object_add(
        return_json,
        "error_detail", json_object_new_string(error_name));
    no_error = false;
  }

  MessageFormatter::Builder builder(errorCode);
  MessageFormatter mf = builder.setPattern(u"Hello, {$userName}!", parseError, errorCode)
        .build(errorCode);

  UnicodeString result_ustring = formatter.formatToString(arguments, status);
  // Call the function and return the result.
  if (U_FAILURE(status)) {
    const char* error_name = u_errorName(status);
    json_object_object_add(
        return_json,
        "error", json_object_new_string("error in formatToString"));
    json_object_object_add(
        return_json,
        "error_detail", json_object_new_string(error_name));
    no_error = false;
    }


  int32_t chars_out;  // Results of extracting characters from Unicode string

  bool no_error = true;
  char test_result[1000] = "";

  // Get the resulting value as a string
  result_ustring.extract(test_result, 1000, nullptr, status);  // ignore result

  // Call the function and return the result.
  if (U_FAILURE(status)) {
      } else {
      // It worked!
      json_object_object_add(return_json,
                             "result",
                             json_object_new_string(test_result));
    }

  string return_string = json_object_to_json_string(return_json);
  return return_string;
}
