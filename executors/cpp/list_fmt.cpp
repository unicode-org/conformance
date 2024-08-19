/********************************************************************
 * testing list formatting in icu4c
 */
#include <json-c/json.h>

#include <unicode/utypes.h>

#include <unicode/listformatter.h>
#include <unicode/locid.h>
#include <unicode/unistr.h>

#include <stdio.h>
#include <stdlib.h>
#include <vector>

#include <cstring>
#include <iostream>
#include <string>
#include <string_view>

#include "util.h"

using icu::ListFormatter;
using icu::Locale;
using icu::UnicodeString;

using std::string;

/* Main test function */
const string TestListFmt (json_object* json_in) {
  UErrorCode status = U_ZERO_ERROR;

  json_object* label_obj = json_object_object_get(json_in, "label");
  string label_string = json_object_get_string(label_obj);

  // The locale in which the name is given.
  string locale_string = "und";
  json_object* locale_label_obj = json_object_object_get(json_in, "locale");
  if (locale_label_obj) {
    locale_string = json_object_get_string(locale_label_obj);
  }
  Locale displayLocale(locale_string.c_str());

  json_object* return_json = json_object_new_object();
  json_object_object_add(return_json, "label", label_obj);

  // The language's name to be displayed.
  json_object* input_list_obj = json_object_object_get(json_in, "input_list");

  std::vector<UnicodeString> u_strings;
  int u_strings_size = 0;
  if (input_list_obj) {
    int input_length = json_object_array_length(input_list_obj);

    // Construct the list of Unicode Strings
    for (int i = 0; i < input_length; i++) {
      // get the i-th object in the input list
      json_object* item = json_object_array_get_idx(input_list_obj, i);
      string item_string = json_object_get_string(item);
      u_strings.push_back(item_string.c_str());
    }
    u_strings_size = u_strings.size();
  } else {
    json_object_object_add(
        return_json,
        "error",
        json_object_new_string("no input list"));
    // TODO: return the JSON now.
  }

  // Get fields out of the options if present
  json_object* option_list_obj = json_object_object_get(json_in, "options");
  string style_string;
  string type_string;
  UListFormatterType format_type = ULISTFMT_TYPE_AND;
  UListFormatterWidth format_width = ULISTFMT_WIDTH_WIDE;

  if (option_list_obj) {
    json_object* style_obj = json_object_object_get(
        option_list_obj, "style");
    if (style_obj) {
      style_string = json_object_get_string(style_obj);
      if (style_string == "long") format_width = ULISTFMT_WIDTH_WIDE;
      if (style_string == "short") format_width = ULISTFMT_WIDTH_SHORT;
      if (style_string == "narrow") format_width = ULISTFMT_WIDTH_NARROW;
    }
    json_object* type_obj = json_object_object_get(
        option_list_obj, "type");
    if (type_obj) {
      type_string = json_object_get_string(type_obj);
      if (type_string == "conjunction") format_type = ULISTFMT_TYPE_AND;
      if (type_string == "disjunction") format_type = ULISTFMT_TYPE_OR;
      if (type_string == "unit") format_type = ULISTFMT_TYPE_UNITS;
    }
  }

  ListFormatter* list_formatter =
      ListFormatter::createInstance(displayLocale,
                                    format_type,
                                    format_width,
                                    status);
  if (check_icu_error(status,
                      return_json,"construct list formatter")) {
    return json_object_to_json_string(return_json);
  }

  UnicodeString *u_array = &u_strings[0];
  UnicodeString u_result_string;
  u_result_string = list_formatter->format(u_array,
                                           u_strings_size,
                                           u_result_string,
                                           status);

  if (check_icu_error(status, return_json, "calling format")) {
    return json_object_to_json_string(return_json);
  }

  string result_string;
  u_result_string.toUTF8String(result_string);

  // The JSON output.
  return  json_object_to_json_string(return_json);
}
