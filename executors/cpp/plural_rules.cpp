/********************************************************************
 * Comments and license as needed
 ************************************

/******
 * testing plural rules
 * Based on code of ICU4C testing:
 * https://github.com/unicode-org/icu/blob/maint/maint-75/icu4c/source/test/intltest/plurfmts.cpp
 */


#include "unicode/utypes.h"
#include "unicode/unistr.h"
#include "unicode/plurfmt.h"
#include "unicode/plurrule.h"

#include "unicode/locid.h"
#include "unicode/uclean.h"

#include "util.h"
#include <stdio.h>
#include <stdlib.h>
#include <vector>

#include <json-c/json.h>

#include <iostream>
#include <string>
#include <string_view>
#include <cstring>

using icu::PluralRules;

using std::cout;
using std::endl;
using std::string;


const string test_plural_rules (json_object* json_in) {
  UErrorCode status = U_ZERO_ERROR;

  json_object* label_obj = json_object_object_get(json_in, "label");
  string label_string = json_object_get_string(label_obj);

  // The locale in which the name is given.
  string locale_string = "und";
  string type_string = "";

  json_object* locale_label_obj = json_object_object_get(json_in, "locale");
  if (locale_label_obj) {
    locale_string = json_object_get_string(locale_label_obj);
  }
  Locale display_locale(locale_string.c_str());

  json_object* return_json = json_object_new_object();
  json_object_object_add(return_json, "label", label_obj);

  // The language's name to be displayed.
  json_object* sample_obj = json_object_object_get(json_in, "sample");

  bool input_is_double = false;
  bool input_is_integer = false;
  bool input_is_compact = false;

  double input_double_sample;
  int32_t input_int_sample;

  std::vector<UnicodeString> u_strings;
  int u_strings_size = 0;
  if (sample_obj) {
    // Get the number
    string sample_string = json_object_get_string(sample_obj);

    if (sample_string.find('.') != std::string::npos) {
      // Convert into an integer, decimal, or compact decimal
      input_double_sample = std::stod(sample_string);
      input_is_double = true;
      cout << "#    DOUBLE STRING " << input_double_sample << endl;
    } else
      if (sample_string.find('c') != std::string::npos) {
        input_is_compact = true;
      } else {
        input_int_sample = std::stoi(sample_string);
        input_is_integer = true;
        cout << "#    INT STRING " << input_int_sample << endl;
      }
  } else {
    // TODO: Report an error: no sample
  }

  // Get option fields
  json_object* type_obj = json_object_object_get(json_in, "type");
  if (type_obj) {
    type_string = json_object_get_string(type_obj);
  }
  UPluralType plural_type;
  if (type_string == "cardinal") {
    plural_type = UPLURAL_TYPE_CARDINAL;
  } else
    if (type_string == "ordinal") {
      plural_type = UPLURAL_TYPE_ORDINAL;
    } else {
      // TODO: Report and error.
    }

  cout << "# Plural type: " << type_string << " " << plural_type << endl;

  PluralRules* prules = icu::PluralRules::forLocale(
      display_locale,
      plural_type,
      status);

  if (U_FAILURE(status)) {
    json_object_object_add(return_json,
                           "error",
                           json_object_new_string("construct plural rules"));
  }

  // TODO: distinguish between ints, doubles, and compact values
  UnicodeString u_result;
  if (input_is_double) {
    cout << "Double select " << input_double_sample << endl;
    u_result = prules->select(input_double_sample);
  } else
  if (input_is_integer) {
    cout << "Double select " << input_double_sample << endl;
    u_result = prules->select(input_int_sample);
  } else {
    // TODO: Handle compact and other possible options
    cout << " # TODO: Handle compact, etc." << endl;
    u_result = "Not yet handled";
    json_object_object_add(
        return_json,
        "error",
        json_object_new_string("compact not yet supported"));
    json_object_object_add(
        return_json,
        "unsupported",
        json_object_new_string("compact not yet supported"));

    return  json_object_to_json_string(return_json);
  }

  char test_result_string[1000] = "";
  if (U_FAILURE(status)) {
    json_object_object_add(
        return_json,
        "error",
        json_object_new_string("calling plural rules select"));
  } else {
    int32_t chars_out =
        u_result.extract(test_result_string, 1000, nullptr, status);
  cout << " test_result_string " << test_result_string << endl;

  }

  if (U_FAILURE(status)) {
    json_object_object_add(
        return_json,
        "error",
        json_object_new_string("plural rules result extract error"));
  } else {
    // It all seems to work!
    json_object_object_add(return_json,
                           "result",
                           json_object_new_string(test_result_string));
  }

  // The JSON output.
  return  json_object_to_json_string(return_json);
}
