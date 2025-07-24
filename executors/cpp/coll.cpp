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

#include <cstring>
#include <iostream>
#include <string>

#include "./util.h"

using std::cout;
using std::endl;
using std::string;

using icu::Locale;
using icu::UnicodeString;
using icu::Collator;
using icu::RuleBasedCollator;

const char error_message[] = "error";

/**
 * TestCollator  --  process JSON inputs, run comparator, return result
 */
auto TestCollator(json_object *json_in) -> string {
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
