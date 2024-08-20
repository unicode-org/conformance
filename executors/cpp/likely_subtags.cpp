/******
 * testing likely subtags for locales
 */

#include <json-c/json.h>

#include <unicode/bytestream.h>
#include <unicode/locid.h>
#include <unicode/uclean.h>
#include <unicode/unistr.h>
#include <unicode/utypes.h>

#include <stdio.h>
#include <stdlib.h>

#include <cstring>
#include <iostream>
#include <string>

#include "./util.h"

using std::string;

using icu::Locale;
using icu::StringByteSink;
using icu::UnicodeString;

const string TestLikelySubtags(json_object *json_in) {
  UErrorCode status = U_ZERO_ERROR;

  json_object *label_obj = json_object_object_get(json_in, "label");
  string label_string = json_object_get_string(label_obj);

  // The locale in which the name is given.
  json_object *locale_label_obj = json_object_object_get(json_in, "locale");
  string locale_string = json_object_get_string(locale_label_obj);

  // The type of conversion requested
  json_object *option_obj = json_object_object_get(json_in, "option");
  string option_string = json_object_get_string(option_obj);

  Locale displayLocale(locale_string.c_str());

  string test_result = "";

  json_object *return_json = json_object_new_object();
  json_object_object_add(return_json, "label", label_obj);

  // The default.
  string name_string;
  StringByteSink<string> byteSink(&name_string);

  if (option_string == "maximize") {
    // This makes the maximized form
    Locale maximized(displayLocale);
    maximized.addLikelySubtags(status);

    if (U_FAILURE(status)) {
      test_result = "error in maximize";
    } else {
      maximized.toLanguageTag(byteSink, status);

      if (U_FAILURE(status)) {
        json_object_object_add(
            return_json,
            "error",
            json_object_new_string("toLanguageTag"));
      }
      test_result = name_string;
    }
  } else if (option_string == "minimize" ||
             option_string == "minimizeFavorRegion") {
    // Minimize
    displayLocale.minimizeSubtags(status);
    if (U_FAILURE(status)) {
      const string error_message_min = "error in minimize";
      test_result = error_message_min;
    } else {
      displayLocale.toLanguageTag(byteSink, status);
      test_result = name_string;

      if (U_FAILURE(status)) {
        json_object_object_add(
            return_json,
            "error",
            json_object_new_string("toLanguageTag"));
      }
    }
  } else if (option_string == "minimizeFavorScript") {
    // Minimize with script preferred.
    bool favorScript = true;
    json_object_object_add(
        return_json,
        "error",
        json_object_new_string("unsupported option"));
    json_object_object_add(
        return_json,
        "error_type",
        json_object_new_string("unsupported"));
    json_object_object_add(
        return_json,
        "unsupported",
        json_object_new_string(option_string.c_str()));
    json_object_object_add(
        return_json,
        "error_detail",
        json_object_new_string("This ICU4C API is protected"));

    // This is a protected API in ICU4C.
    // displayLocale.minimizeSubtags(favorScript, status);
  } else {
    // An error in the call.
    json_object_object_add(
        return_json,
        "error",
        json_object_new_string("Unknown test option"));
    json_object_object_add(
        return_json,
        "error_detail",
        json_object_new_string(option_string.c_str()));
  }

  if (U_FAILURE(status)) {
    json_object_object_add(
        return_json,
        "error",
        json_object_new_string(test_result.c_str()));
  } else {
    // The output of the likely subtag operation.
    json_object_object_add(
        return_json,
        "result",
        json_object_new_string(test_result.c_str()));
  }

  return  json_object_to_json_string(return_json);
}
