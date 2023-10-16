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

#include <unicode/utypes.h>
#include <unicode/ucol.h>
#include <unicode/ustring.h>

#include <json-c/json.h>

using std::cout;
using std::endl;
using std::string;

// TODO: Replace this with JSON output
const string ret_value = "{\"label\": \"0\", \"result\": \"True\"}";

/**
 * test_collator  --  process JSON inputs, run comparator, return result
 */
const string test_collator(json_object *json_in)  //
{
  json_object *label_obj = json_object_object_get(json_in, "label");
  string label_string = json_object_get_string(label_obj);

  json_object *str1 = json_object_object_get(json_in, "string1");
  json_object *str2 = json_object_object_get(json_in, "string2");

  string string1 = json_object_get_string(str1);
  string string2 = json_object_get_string(str2);

  // In the default locale
  UErrorCode status = U_ZERO_ERROR;
  UCollator *coll = ucol_open(NULL, &status);

  char16_t source[100];
  char16_t target[100];
  char opt_source[100];
  char opt_target[100];
  strcpy(opt_source,string1.c_str());
  strcpy(opt_target, string2.c_str());
  u_unescape(opt_source, source, 100);
  u_unescape(opt_target, target, 100);

  string coll_result = "True";
  UCollationResult result = ucol_strcoll(coll,
                                         source, -1,
                                         target, -1);

  // The json result.
  json_object *return_json = json_object_new_object();
  json_object_object_add(return_json, "label", label_obj);

  if (result != UCOL_LESS) {
    coll_result = "False";
    // Include date for the failing test
    json_object_object_add(return_json,
                           "s1",
                           json_object_new_string(string1.c_str()));
    json_object_object_add(return_json,
                           "s2",
                           json_object_new_string(string2.c_str()));
    if (result == UCOL_EQUAL) {
      json_object_object_add(return_json,
                             "compare",
                             json_object_new_string("UCOLL_EQUAL"));
    } else {
      json_object_object_add(return_json,
                             "compare",
                             json_object_new_string("UCOLL_GREATER"));
    }
  }
  ucol_close(coll);

  json_object_object_add(return_json,
                         "result",
                         json_object_new_string(coll_result.c_str()));

  string return_str = json_object_to_json_string(return_json);

  // cout << "# COLL OUT: " << return_str << endl;
  return return_str;
}
