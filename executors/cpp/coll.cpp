/*************************************************************************
 *
 *   © 2016 and later: Unicode, Inc. and others.
 *   License & terms of use: http://www.unicode.org/copyright.html
 *
 *************************************************************************
 *************************************************************************
 * COPYRIGHT:
 * Copyright (C) 2002-2006 IBM, Inc.   All Rights Reserved.
 *
 *************************************************************************/

/**
 * This calls collation on pairs of strings for ICU_conformance testing.
 */


#include <iostream>
#include <string>

#include <string.h>

#include <unicode/locid.h>
#include <unicode/utypes.h>
#include <unicode/coll.h>
#include <unicode/ucol.h>
#include <unicode/unistr.h>
#include <unicode/ustring.h>

#include <json-c/json.h>

using std::cout;
using std::endl;
using std::string;

using icu::Locale;
using icu::UnicodeString;
using icu::Collator;

/**
 * test_collator  --  process JSON inputs, run comparator, return result
 */
const string test_collator(json_object *json_in)  //
{
  UErrorCode status = U_ZERO_ERROR;

  json_object *label_obj = json_object_object_get(json_in, "label");
  string label_string = json_object_get_string(label_obj);

  json_object *str1 = json_object_object_get(json_in, "s1");
  json_object *str2 = json_object_object_get(json_in, "s2");

  string string1 = json_object_get_string(str1);
  string string2 = json_object_get_string(str2);
  // cout << "s1 = " << string1 << " s2 = " << string2 << endl;

  UnicodeString us1 = UnicodeString(string1.c_str()).unescape();
  UnicodeString us2 = UnicodeString(string2.c_str()).unescape();

  // Check unescaped versions.
  char char_out1[1000] = "";
  char char_out2[1000] = "";
  int32_t chars_out = us1.extract(char_out1, 1000, nullptr, status);
  chars_out = us2.extract(char_out2, 1000, nullptr, status);

  // cout << "us1 = " << char_out1 << " us2 = " << char_out2 << endl;

  json_object *locale_obj = json_object_object_get(json_in, "locale");
  const char *locale_string;
  if (locale_obj) {
    locale_string = json_object_get_string(locale_obj);
  } else {
    locale_string = nullptr;
  }


  // Allow for different levels or types of comparison.
  json_object *compare_type = json_object_object_get(json_in, "compare_type");
  if (compare_type) {
    const char *comparison_type = json_object_get_string(compare_type);
  }

  // Handle some options
  json_object *ignore_obj = json_object_object_get(json_in, "ignorePunctuation");

  const int32_t unspecified_length = -1;
  bool coll_result = true;

  // Create a C++ collator and try it.
  Collator *uni_coll = Collator::createInstance(Locale(locale_string), status);
  if (ignore_obj) {
    uni_coll->setAttribute(UCOL_ALTERNATE_HANDLING, UCOL_SHIFTED, status);
  }

  int uni_result = uni_coll->compare(us1, us2);
  // cout << "UNI_RESULT = " << uni_result << endl;

  // The json test output.
  json_object *return_json = json_object_new_object();
  json_object_object_add(return_json, "label", label_obj);

  int64_t numeric_result = int64_t(uni_result);
  if (uni_result == UCOL_GREATER) {
    coll_result = false;

    // Include data compared in the failing test
    json_object_object_add(
        return_json, "s1", json_object_new_string(string1.c_str()));
    json_object_object_add(
        return_json, "s2", json_object_new_string(string2.c_str()));

    // What was the actual returned value?
    json_object_object_add(
        return_json, "compare", json_object_new_int64(numeric_result));
  }

  json_object_object_add(
      return_json, "result", json_object_new_boolean(coll_result));

  return  json_object_to_json_string(return_json);
}
