/********************************************************************
 * Comments and license as needed
 ************************************

/******
 * testing likely subtags for locales
 */

#include "unicode/utypes.h"
#include "unicode/unistr.h"
#include "unicode/locid.h"
#include "unicode/uclean.h"

#include "util.h"
#include <stdio.h>
#include <stdlib.h>

#include <json-c/json.h>

#include <iostream>
#include <string>
#include <cstring>

using std::cout;
using std::endl;
using std::string;

const string test_likely_subtags(json_object *json_in) {

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

  const char* test_result_string;
  const string error_message_max = "error in maximize";
  const string error_message_min = "error in minimize";
  const string protected_msg = "This ICU4C API is protected";
  const char* empty_result = "";

  json_object *return_json = json_object_new_object();
  json_object_object_add(return_json, "label", label_obj);

  // The default.
  test_result_string = empty_result;
  if (option_string == "maximize") {
    // This makes the maximized form
    Locale maximized(displayLocale);
    maximized.addLikelySubtags(status);
    if (U_FAILURE(status)) {
      test_result_string = error_message_max.c_str();
      cout << "ERROR MAXIMIZED:" << test_result_string << endl;
    } else {
      test_result_string = maximized.getName();
      cout << "MAXIMIZED:" << test_result_string << endl;
    }
  }
  else if (option_string == "minimize" || option_string == "minimizeFavorRegion") {
    // Minimize
    displayLocale.minimizeSubtags(status);
    if (U_FAILURE(status)) {
      test_result_string = error_message_min.c_str();
      cout << "ERROR MINIMIZED:" << test_result_string << endl;
    } else {
      const char* min_name = displayLocale.getName();
      cout << "MINIMIZED:" << min_name << endl;
      test_result_string = min_name;
    }
  }
  else if (option_string == "minimizeFavorScript") {
    // Minimize with script preferred.
    bool favorScript = true;
    json_object_object_add(return_json,
                         "unsupported",
                           json_object_new_string(option_string.c_str()));
    json_object_object_add(return_json,
                         "error_detail",
                           json_object_new_string(protected_msg.c_str()));
    // This is a protected API in ICU4C.
    // displayLocale.minimizeSubtags(favorScript, status);
  }
  else {
    // An error in the call.
    json_object *error_msg = json_object_new_object();

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
    cout << "REPORTING AN ERROR: " << test_result_string;
    json_object *error_msg = json_object_new_object();

    json_object_object_add(return_json,
                           "error",
                           json_object_new_string(test_result_string));
  } else {
    json_object_object_add(return_json,
                           "result",
                           json_object_new_string(test_result_string));
  }

  return  json_object_to_json_string(return_json);
}
