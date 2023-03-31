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
  cout << "# LANGNAME: " << json_object_to_json_string(json_in);

  json_object *label_obj = json_object_object_get(json_in, "label");
  string label_string = json_object_get_string(label_obj);
  cout << "# LABEL: " << json_object_get_string(label_obj);

  json_object *return_json = json_object_new_object();
  json_object_object_add(return_json, "label", label_obj);
  json_object_object_add(return_json,
                         "result",
                         json_object_new_string(result.c_str()));

  json_object *locale_label_obj = json_object_object_get(json_in, "locale_label");
  string locale_string = json_object_get_string(locale_label_obj);
  cout << "# locale label: " << json_object_get_string(locale_label_obj);

  json_object *language_label_obj = json_object_object_get(json_in, "language_label");
  string language_label_string = json_object_get_string(language_label_obj);
  cout << "# language label: " << json_object_get_string(language_label_obj);

  Locale display_locale(locale_string);
  UnicodeString display_lang(lange_label_string);

  UnicodeString &name = getDisplayLanguage(const display_locale, UnicodeString &display_lang);

  json_object *return_json = json_object_new_object();
  json_object_object_add(return_json, "label", label_obj);
  json_object_object_add(return_json,
                         "result",
                         json_object_new_string(name.c_str()));
 string return_str = json_object_to_json_string(return_json);


  return result_string;
}
