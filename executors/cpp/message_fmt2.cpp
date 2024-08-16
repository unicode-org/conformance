/********************************************************************
 * testing message format 2 in C++
 */

#include <json-c/json.h>

#include <unicode/locid.h>
#include <unicode/messageformat2.h>
#include <unicode/utypes.h>


#include <unicode/messageformat2_arguments.h>
#include <unicode/messageformat2_data_model.h>
#include <unicode/messageformat2_function_registry.h>
#include <unicode/messageformat2_formattable.h>
#include <unicode/messageformat2.h>
#include <unicode/msgfmt.h>
#include <unicode/unistr.h>

#include <stdio.h>
#include <stdlib.h>

#include <iostream>
#include <string>
#include <cstring>

using icu::Locale;
using icu::message2::MessageFormatter;
using icu::message2::MessageArguments;
using icu::message2::Formattable;

using icu::UnicodeString;


using std::cout;
using std::endl;
using std::string;

/* Based on this test file:
 * https://github.com/unicode-org/icu/blob/main/icu4c/source/test/intltest/messageformat2test.cpp
 */
const string TestMessageFormat2(json_object *json_in) {
  UErrorCode errorCode = U_ZERO_ERROR;

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
  json_object *test_description_obj = json_object_object_get(json_in, "test_description");
  if (test_description_obj) {
    test_description_string = json_object_get_string(test_description_obj);
  }

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
    // !!!
    int params_length = json_object_array_length(param_list_obj);
    // cout << "Params length = " << params_length << endl;

    // Construct the list of Unicode Strings
    for (int i = 0; i < params_length; i++) {
      json_object* param_obj = json_object_array_get_idx(param_list_obj, i);

      json_object *params_name_obj = json_object_object_get(param_obj, "name");
      if (params_name_obj) {
        params_name = json_object_get_string(params_name_obj);
        u_params_name = params_name.c_str();
      }
      json_object *params_value_obj = json_object_object_get(param_obj, "value");
      if (params_value_obj) {
        params_value = json_object_get_string(params_value_obj);
        u_params_value = params_value.c_str();
      }
      // cout << "  Name = " << params_name << ", value = " << params_value << endl;
      argsBuilder[u_params_name] = Formattable(u_params_value);
    }
  }

  // Start filling the return data.
  json_object *return_json = json_object_new_object();
  json_object_object_add(return_json, "label", label_obj);

  bool no_error = true;

  if (U_FAILURE(errorCode)) {
    const char* error_name = u_errorName(errorCode);
    json_object_object_add(
        return_json,
        "error", json_object_new_string("error in constructor"));
    json_object_object_add(
        return_json,
        "error_detail", json_object_new_string(error_name));
    no_error = false;
  }

  UParseError parseError;

  MessageFormatter::Builder builder(errorCode);
  MessageFormatter mf = builder.setPattern(u_src, parseError, errorCode)
                        .build(errorCode);

  MessageArguments args(argsBuilder, errorCode);

  UnicodeString result_ustring = mf.formatToString(args, errorCode);
  // Call the function and return the result.
  if (U_FAILURE(errorCode)) {
    const char* error_name = u_errorName(errorCode);
    json_object_object_add(
        return_json,
        "error", json_object_new_string("error in formatToString"));
    json_object_object_add(
        return_json,
        "error_detail", json_object_new_string(error_name));
    no_error = false;
  }


  int32_t chars_out;  // Results of extracting characters from Unicode string

  char test_result[1000] = "";

  // Get the resulting value as a string
  result_ustring.extract(test_result, 1000, nullptr, errorCode);  // ignore result

  // Call the function and return the result.
  if (U_FAILURE(errorCode)) {
  } else {
    // It worked!
    json_object_object_add(return_json,
                           "result",
                           json_object_new_string(test_result));
  }

  string return_string = json_object_to_json_string(return_json);
  return return_string;
}
