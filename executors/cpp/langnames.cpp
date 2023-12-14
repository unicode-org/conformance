/********************************************************************
 * Comments and license as needed
 ************************************

/******
 * testing language display names
 */


#include "unicode/utypes.h"
#include "unicode/unistr.h"
#include "unicode/numfmt.h"
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


const string test_langnames (json_object *json_in) {
  UErrorCode status = U_ZERO_ERROR;

  json_object *label_obj = json_object_object_get(json_in, "label");
  string label_string = json_object_get_string(label_obj);


  // The locale in which the name is given.
  json_object *locale_label_obj = json_object_object_get(json_in, "locale_label");
  string locale_string = json_object_get_string(locale_label_obj);

  // The language's name to be displayed.
  json_object *language_label_obj = json_object_object_get(json_in, "language_label");
  string language_label_string = json_object_get_string(language_label_obj);

  Locale displayLocale(locale_string.c_str());

  Locale testLocale(language_label_string.c_str());

  UnicodeString testLang;

  testLocale.getDisplayName(displayLocale, testLang);
  // The following gives only the language name, without region information
  /// testLocale.getDisplayLanguage(displayLocale, testLang);

  json_object *return_json = json_object_new_object();
  json_object_object_add(return_json, "label", label_obj);

  char test_result_string[100] = "";

  int32_t chars_out = testLang.extract(test_result_string, 100, nullptr, status);
  if (U_FAILURE(status)) {
    json_object *error_msg = json_object_new_object();

    json_object_object_add(return_json,
                           "error", json_object_new_string("langnames extract error"));
  } else {
    json_object_object_add(return_json,
                           "result",
                           json_object_new_string(test_result_string));
  }

  string return_string = json_object_to_json_string(return_json);
  return return_string;
}
