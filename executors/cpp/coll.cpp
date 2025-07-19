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


#include <json-c/json.h>

#include <unicode/coll.h>
#include <unicode/locid.h>
#include <unicode/tblcoll.h>
#include <unicode/ucol.h>
#include <unicode/unistr.h>
#include <unicode/ustring.h>
#include <unicode/utypes.h>

#include <bits/stdc++.h>
#include <cstring>
#include <iostream>
#include <map>
#include <string>
#include <vector>

#include "./util.h"

using std::cout;
using std::endl;
using std::map;
using std::string;
using std::vector;

using icu::Locale;
using icu::UnicodeString;
using icu::Collator;
using icu::RuleBasedCollator;

using namespace std;

const char error_message[] = "error";

UnicodeString get_char_from_hex_list(json_object* str_codes_obj,
                                     int debug_level) {
    // Get the hex codes and assemble into a string with \u
    int input_length = json_object_array_length(str_codes_obj);

    // Construct the list of Unicode Strings
    string hex_list = "";
    for (int i = 0; i < input_length; i++) {
      // get the i-th object in the input list
      json_object* item = json_object_array_get_idx(str_codes_obj, i);
      string hex_string = json_object_get_string(item);
      string escape_prefix;
      switch (hex_string.size()) {
        case 5:
          escape_prefix = "\\U000";
          break;
        case 6:
          escape_prefix = "\\U00";
          break;
        case 7:
          escape_prefix = "\\U0";
          break;
        case 4:
        default:
          escape_prefix = "\\u";
          break;
        case 3:
          escape_prefix = "\\u0";
          break;
        case 2:
          escape_prefix = "\\u00";
          break;
        case 1:
          escape_prefix = "\\u000";
          break;
      }
      hex_list += escape_prefix + hex_string;
    }
    // Finally, unescape this list.
    UnicodeString u_hex = UnicodeString::fromUTF8(hex_list);
    UnicodeString s_new = u_hex.unescape();
    if (debug_level > 0) {
      string target;
      s_new.toUTF8String(target);
    }

    return s_new;
}

  std::map<string, int> reorder_map = {
    // Note that this is a subset of the script codes
    {"digit", UCOL_REORDER_CODE_DIGIT},
    {"space", UCOL_REORDER_CODE_SPACE},
    {"symbol", UCOL_REORDER_CODE_SYMBOL},
    {"punct", UCOL_REORDER_CODE_PUNCTUATION},
    {"Latn", USCRIPT_LATIN},
    {"Grek", USCRIPT_GREEK},
    {"Goth", USCRIPT_GOTHIC},
    {"Hani", USCRIPT_HAN},
    {"Hang", USCRIPT_HANGUL},
    {"Hebr", USCRIPT_HEBREW},
    {"Hira", USCRIPT_HIRAGANA},
    {"Zyyy", USCRIPT_COMMON},
    {"Zzzz", USCRIPT_UNKNOWN}
  };

/*
 * BuildReorderList -- Convert string containing reorder specs to integers
 */
auto BuildReorderList(string reorder_string, int debug_level) -> vector<int32_t> {
  // https://unicode-org.github.io/icu-docs/apidoc/dev/icu4c/uscript_8h_source.html
  UErrorCode status = U_ZERO_ERROR;

  if (debug_level > 0) {
    cout << "# BuildReorderList: " << reorder_string << endl;
  }

  // Split reorder_string into strings.
  vector<string> reorder_strings;
  size_t start = 0;
  size_t end = reorder_string.find_first_of(' ');
  while (end != std::string::npos) {
    string this_one = reorder_string.substr(start, end-start);
    reorder_strings.emplace_back(this_one);
    start = end + 1;
    end = reorder_string.find(' ', start);
  }

  // Create an array of codes based on number of strings
  vector<int32_t> return_codes;
  // For each, set the UCOL value in return_codes
  std::vector<string>::iterator it;
  std::map<string,int>::iterator map_it;
  int index = 0;
  for (vector<string>::iterator it = reorder_strings.begin();
       it != reorder_strings.end(); ++it) {
    string script_tag = *it;
    map_it = reorder_map.find(script_tag);
    if (map_it != reorder_map.end()) {
      if (debug_level > 0) {
        return_codes.push_back(map_it->second);
      }
      cout << "# RECOGNIZED SCRIPT CODE: " << script_tag << " --> " << map_it->second << endl;
    } else {
      cout << "# UNRECOGNIZED SCRIPT CODE: " << script_tag << endl;
    }
  }
  if (debug_level > 0) {
    cout << "# SCRIPT CODES: " << return_codes.size() << endl;
  }
  return return_codes;
}

/**
 * TestCollator  --  process JSON inputs, run comparator, return result
 */
auto TestCollator(json_object *json_in, int debug_level) -> string {
  UErrorCode status = U_ZERO_ERROR;

  json_object *label_obj = json_object_object_get(json_in, "label");
  string label_string = json_object_get_string(label_obj);

  json_object *str1 = json_object_object_get(json_in, "s1");
  json_object *str2 = json_object_object_get(json_in, "s2");

  // Unescape the input strings?
  string string1 = json_object_get_string(str1) ;
  string string2 = json_object_get_string(str2);

  // Does this conversion preserve the data?
  UnicodeString us1 = UnicodeString::fromUTF8(string1);
  UnicodeString us2 = UnicodeString::fromUTF8(string2);

  json_object *str1_codes_obj = json_object_object_get(json_in, "s1_codes");
  json_object *str2_codes_obj = json_object_object_get(json_in, "s2_codes");

  // Use the hex codes if they are provided rather than s1 and s2.
  if (str1_codes_obj) {
    us1 = get_char_from_hex_list(str1_codes_obj, debug_level);
  }
  if (str2_codes_obj) {
    us2 = get_char_from_hex_list(str2_codes_obj, debug_level);
  }

  string test_result;
  int uni_result_utf8;

  json_object *locale_obj = json_object_object_get(json_in, "locale");
  const char *locale_string;
  if (locale_obj != nullptr) {
    locale_string = json_object_get_string(locale_obj);
  } else {
    locale_string = "und";
  }

  // Comparison type
  json_object *compare_type_obj =
      json_object_object_get(json_in, "compare_type");
  string compare_type_string;
  if (compare_type_obj != nullptr) {
    compare_type_string = json_object_get_string(compare_type_obj);
    if (compare_type_string.substr(0,4) == "&lt;") {
      compare_type_string = "<" + compare_type_string.substr(4,1);
    }
  }

  // Strength of comparison
  Collator::ECollationStrength strength_type =  Collator::PRIMARY;
  string strength_string;

  json_object *strength_obj = json_object_object_get(json_in, "strength");
  if (strength_obj != nullptr) {
    strength_string = json_object_get_string(strength_obj);
    if (strength_string == "primary") {
      strength_type = Collator::PRIMARY;
    } else if (strength_string == "secondary") {
      strength_type = Collator:: SECONDARY;
    } else if (strength_string == "tertiary") {
      strength_type = Collator::TERTIARY;
    } else if (strength_string == "quaternary") {
      strength_type = Collator::QUATERNARY;
    } else if (strength_string == "identical") {
      strength_type = Collator::IDENTICAL;
    }
  }

  // Apply reordering if present
  json_object *reorder_obj = json_object_object_get(json_in, "reorder");
  string reorder_string;
  vector<int32_t> reorder_codes_v;
  if (reorder_obj) {
    reorder_string = json_object_get_string(reorder_obj);
    reorder_codes_v = BuildReorderList(reorder_string, debug_level);
  }

  // Check for rule-based collation
  json_object *rules_obj = json_object_object_get(json_in, "rules");
  string rules_string;
  if (rules_obj != nullptr) {
    rules_string = json_object_get_string(rules_obj);
  }
  UnicodeString uni_rules = UnicodeString::fromUTF8(rules_string);

  // Handle some options
  json_object *ignore_obj =
      json_object_object_get(json_in, "ignorePunctuation");

  const int32_t unspecified_length = -1;
  bool coll_result = true;

  // The json test output.
  json_object *return_json = json_object_new_object();
  json_object_object_add(return_json, "label", label_obj);

  int uni_result;
  // Create a C++ collator and try it.

  Collator *uni_coll = nullptr;
  RuleBasedCollator *rb_coll = nullptr;

  if (!rules_string.empty()) {
    string uni_rules_string;
    // TODO: Check if this is needed.
    uni_rules.toUTF8String(uni_rules_string);

    // Make sure normalization is consistent
    rb_coll = new RuleBasedCollator(uni_rules, UCOL_ON, status);
    if (check_icu_error(status, return_json, "create RuleBasedCollator")) {
      // Put json_in as the actual input received.
      json_object_object_add(
          return_json, "actual_options",
          json_object_new_string(json_object_get_string(json_in)));

      return json_object_to_json_string(return_json);
    }
    if (reorder_obj) {
      if (debug_level > 0) {
        cout << "# RB_COLL: reorder codes: " << reorder_string << "(" << reorder_codes_v.size() << ")" << endl;
      }
      rb_coll->setReorderCodes(reorder_codes_v.data(), reorder_codes_v.size(), status);
      if (check_icu_error(status, return_json, "rb_coll with reorder")) {
        return json_object_to_json_string(return_json);
      }
    }

    uni_result = rb_coll->compare(us1, us2, status);
    if (check_icu_error(status, return_json, "rb_coll->compare")) {
      return json_object_to_json_string(return_json);
    }

    // Don't need this anymore.
    delete rb_coll;
  } else {
    // Not a rule-based collator.
    if (strlen(locale_string) <= 0) {
      // Uses the default Locale.
      uni_coll = Collator::createInstance(status);
    } else {
      Locale this_locale;
      if (locale_string == "root") {
        this_locale = Locale::getRoot();
      } else {
        this_locale = Locale(locale_string);
      }
      uni_coll = Collator::createInstance(this_locale, status);
    }

    if (check_icu_error(
            status, return_json, "create collator instance")) {
      return json_object_to_json_string(return_json);
    }

    if (reorder_obj) {
      if (debug_level > 0) {
        cout << "# UNI_COLL: reorder codes: " << reorder_string << "(" << reorder_codes_v.size() << ")" << endl;
      }
      uni_coll->setReorderCodes(reorder_codes_v.data(), reorder_codes_v.size(), status);
      if (check_icu_error(status, return_json, "uni_coll->setReorderCodes")) {
        return json_object_to_json_string(return_json);
      }
    }

    // Make sure normalization is consistent
    uni_coll->setAttribute(UCOL_NORMALIZATION_MODE, UCOL_ON, status);
    if (check_icu_error(
            status, return_json, "error setting normalization to UCOL_ON")) {
      return json_object_to_json_string(return_json);
    }

    if (strength_obj != nullptr) {
      uni_coll->setStrength(strength_type);
    }

    if (ignore_obj != nullptr) {
      const bool ignore_punctuation_bool = json_object_get_boolean(ignore_obj) != 0;
      if (ignore_punctuation_bool) {
        uni_coll->setAttribute(UCOL_ALTERNATE_HANDLING, UCOL_SHIFTED, status);
        if (check_icu_error(
                status, return_json,
                "set UCOL_ALTERNATE_HANDLING to UCOL_SHIFTED")) {
          return json_object_to_json_string(return_json);
        }
      }
    }

    // Just to check the result.
    uni_coll->getAttribute(UCOL_ALTERNATE_HANDLING, status);  // ignore return
    if (check_icu_error(
            status, return_json,
            "getet UCOL_ALTERNATE_HANDLING")) {
      return json_object_to_json_string(return_json);
    }

    // Perform the string comparison
    uni_result = uni_coll->compare(us1, us2, status);
    if (check_icu_error( status, return_json, "uni_coll_compare")) {
      return json_object_to_json_string(return_json);
    }

    if (uni_coll != nullptr) {
      uni_coll->getAttribute(UCOL_ALTERNATE_HANDLING, status);  // ignore result
    }
    delete uni_coll;
    if (check_icu_error( status, return_json, "uni_coll->getATTRIBUTE")) {
      return json_object_to_json_string(return_json);
    }
  }

  // Use the compare_type to see if "<" or "=" should be applied.
  if (compare_type_string == "" || compare_type_string.substr(0, 1) == "<") {
    // Default checking for <= 0.
    coll_result = (uni_result != UCOL_GREATER);
  } else
    if (compare_type_string == "=") {
      coll_result = (uni_result == UCOL_EQUAL);
    } else {
      //
      coll_result = (uni_result == UCOL_EQUAL);
    }

  if (!coll_result) {
    // Test did not succeed!
    // Include data compared in the failing test
    json_object* actual_values = json_object_new_object();

    json_object_object_add(
        actual_values, "s1_actual", json_object_new_string(string1.c_str()));
    json_object_object_add(
        actual_values, "s2_actual", json_object_new_string(string2.c_str()));
    json_object_object_add(
        actual_values, "input",
        json_object_new_string(json_object_get_string(json_in)));

    json_object_object_add(
        return_json, "actual_options",
        actual_values);

    // Record the actual returned value
    json_object_object_add(
        return_json, "compare", json_object_new_int64(uni_result));
  }

  json_object_object_add(
      return_json, "result", json_object_new_boolean(static_cast<json_bool>(coll_result)));

  return  json_object_to_json_string(return_json);
}
