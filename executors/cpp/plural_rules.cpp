/********************************************************************
 * testing plural rules in icu4c
 *
 * https://github.com/unicode-org/icu/blob/maint/maint-75/icu4c/source/test/intltest/plurfmts.cpp
 */

#include <json-c/json.h>

#include <unicode/locid.h>
#include <unicode/plurfmt.h>
#include <unicode/plurrule.h>
#include <unicode/unistr.h>

#include <string>
#include <vector>

#include "./util.h"

using icu::Locale;
using icu::PluralRules;
using icu::UnicodeString;

using std::string;

string TestPluralRules (json_object* json_in) {
  UErrorCode status = U_ZERO_ERROR;

  json_object* label_obj = json_object_object_get(json_in, "label");
  string label_string = json_object_get_string(label_obj);

  // The locale in which the name is given.
  string locale_string = "und";
  string type_string = "";

  json_object* locale_label_obj = json_object_object_get(json_in, "locale");
  if (locale_label_obj != nullptr) {
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
  if (sample_obj != nullptr) {
    // Get the number
    string sample_string = json_object_get_string(sample_obj);

    if (sample_string.find('c') != std::string::npos) {
      // TODO: Handle compact numbers
    }

    if (sample_string.find('.') != std::string::npos) {
      // Convert into an integer, decimal, or compact decimal
      input_double_sample = std::stod(sample_string);
      input_is_double = true;
    } else {
      input_int_sample = std::stoi(sample_string);
      input_is_integer = true;
    }
  } else {
    json_object_object_add(return_json,
                           "error",
                           json_object_new_string("no sample string"));
    return  json_object_to_json_string(return_json);
  }

  // Get option fields
  json_object* type_obj = json_object_object_get(json_in, "type");
  if (type_obj != nullptr) {
    type_string = json_object_get_string(type_obj);
  }
  UPluralType plural_type;
  if (type_string == "cardinal") {
    plural_type = UPLURAL_TYPE_CARDINAL;
  } else if (type_string == "ordinal") {
    plural_type = UPLURAL_TYPE_ORDINAL;
  } else {
    string error_message = "unknown plural type: " + type_string;
    json_object_object_add(
        return_json,
        "error",
        json_object_new_string(error_message.c_str()));
    return  json_object_to_json_string(return_json);
  }

  PluralRules* prules =
      icu::PluralRules::forLocale(display_locale, plural_type, status);

  if (check_icu_error(status, return_json, "contruct plural rules")) {
    return json_object_to_json_string(return_json);
  }

  // TODO: distinguish between ints, doubles, and compact values
  UnicodeString u_result;
  if (input_is_double) {
    u_result = prules->select(input_double_sample);
  } else if (input_is_integer) {
    u_result = prules->select(input_int_sample);
  } else if (input_is_compact) {
    // TODO: Handle compact and other possible options
    u_result = "Not yet handled";
    json_object_object_add(
        return_json,
        "error",
        json_object_new_string("compact not yet supported"));
    json_object_object_add(
        return_json,
        "unsupported",
        json_object_new_string("compact not yet supported"));

    return json_object_to_json_string(return_json);
  }

  string result_string;
  u_result.toUTF8String(result_string);

  // It all seems to work!
  json_object_object_add(
      return_json,
      "result",
      json_object_new_string(result_string.c_str()));

  // The JSON output.
  return  json_object_to_json_string(return_json);
}
