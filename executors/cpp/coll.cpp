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

#include <iostream>
#include <string>

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
const string TestCollator(json_object *json_in) {
  UErrorCode status = U_ZERO_ERROR;

  json_object *label_obj = json_object_object_get(json_in, "label");
  string label_string = json_object_get_string(label_obj);

  json_object *str1 = json_object_object_get(json_in, "s1");
  json_object *str2 = json_object_object_get(json_in, "s2");

  string string1 = json_object_get_string(str1);
  string string2 = json_object_get_string(str2);

  // Does this conversion preserve the data?
  UnicodeString us1 = UnicodeString::fromUTF8(string1);
  UnicodeString us2 = UnicodeString::fromUTF8(string2);

  string test_result;
  int uni_result_utf8;

  json_object *locale_obj = json_object_object_get(json_in, "locale");
  const char *locale_string;
  if (locale_obj) {
    locale_string = json_object_get_string(locale_obj);
  } else {
    locale_string = "und";
  }

  // Comparison type
  json_object *compare_type_obj =
      json_object_object_get(json_in, "compare_type");
  string compare_type_string = "";
  if (compare_type_obj) {
    compare_type_string = json_object_get_string(compare_type_obj);
  }

  // Strength of comparison
  Collator::ECollationStrength strength_type =  Collator::PRIMARY;
  string strength_string = "";

  json_object *strength_obj = json_object_object_get(json_in, "strength");
  if (strength_obj) {
    strength_string = json_object_get_string(strength_obj);
    if (strength_string == "primary") {
      strength_type = Collator::PRIMARY;
    } else if (strength_string == "secondary") {
      strength_type = Collator:: SECONDARY;
    } else if (strength_string == "tertiary") {
      strength_type = Collator::TERTIARY;
    } else if (strength_string == "quaternary") {
      strength_type = Collator::QUATERNARY;
    } else if (strength_string == "IDENTICAL") {
      strength_type = Collator::IDENTICAL;
    }
  }

  // Check for rule-based collation
  json_object *rules_obj = json_object_object_get(json_in, "rules");
  string rules_string = "";
  if (rules_obj) {
    rules_string = json_object_get_string(rules_obj);
  }
  UnicodeString uni_rules = UnicodeString::fromUTF8(rules_string);

  // Allow for different levels or types of comparison.
  json_object *compare_type = json_object_object_get(json_in, "compare_type");
  if (compare_type) {
    // TODO: Apply this in tests.
    const char *comparison_type = json_object_get_string(compare_type);
  }

  // Handle some options
  json_object *ignore_obj =
      json_object_object_get(json_in, "ignorePunctuation");

  const int32_t unspecified_length = -1;
  bool coll_result = true;

  // The json test output.
  json_object *return_json = json_object_new_object();
  json_object_object_add(return_json, "label", label_obj);

  bool no_error = true;
  int uni_result;
  // Create a C++ collator and try it.

  Collator *uni_coll = nullptr;
  RuleBasedCollator *rb_coll = nullptr;

  if (rules_string != "") {
    char uni_rules_out[1000] = "";
    int32_t rule_chars_out =
        uni_rules.extract(uni_rules_out, 1000, nullptr, status);

    // Make sure normalization is consistent
    rb_coll = new RuleBasedCollator(uni_rules, UCOL_ON, status);
    if (U_FAILURE(status)) {
      test_result = error_message;
      // TODO: report the error in creating the instance
      cout << "# Error in making RuleBasedCollator: " <<
          label_string << " : " << test_result << endl;

      json_object_object_add(
          return_json,
          "error", json_object_new_string("creat rule based collator"));
      no_error = false;
    }

    uni_result = rb_coll->compare(us1, us2, status);
    if (U_FAILURE(status)) {
      test_result = error_message;

      json_object_object_add(
          return_json,
          "error", json_object_new_string("error in rb_coll->compare"));
      no_error = false;
      cout << "# Error in rb_coll->compare: " <<
          label_string << " : " <<
          test_result << endl;
    }
    // Don't need this anymore.
    delete rb_coll;
  } else {
    // Not a rule-based collator.
    if (locale_string == "") {
      uni_coll = Collator::createInstance(status);
    } else {
      cout << "# Locale set to " << locale_string <<  endl;
      uni_coll = Collator::createInstance(Locale(locale_string), status);
    }

    if (U_FAILURE(status)) {
      test_result = error_message;
      json_object_object_add(
          return_json,
          "error", json_object_new_string("error creating collator instance"));
      no_error = false;
      cout << "# Error in createInstance: " <<
          label_string << " : " <<
          test_result << endl;
    }

    // Make sure normalization is consistent
    uni_coll->setAttribute(UCOL_NORMALIZATION_MODE, UCOL_ON, status);
    if (U_FAILURE(status)) {
      test_result = error_message;
      json_object_object_add(
          return_json,
          "error",
          json_object_new_string("error setting normalization to UCOL_ON"));
      no_error = false;
      cout << "# Error in setAttribute: " <<
          label_string << " : " <<
          test_result << endl;
    }

    if (strength_obj) {
      uni_coll->setStrength(strength_type);
    }

    if (ignore_obj) {
      const bool ignore_punctuation_bool = json_object_get_boolean(ignore_obj);
      if (ignore_punctuation_bool) {
        uni_coll->setAttribute(UCOL_ALTERNATE_HANDLING, UCOL_SHIFTED, status);
        if (U_FAILURE(status)) {
          test_result = error_message;
          json_object_object_add(
              return_json,
              "error", json_object_new_string("error setAttribute"));
          no_error = false;
          cout << "# Error in setAttribute: " <<
              label_string << " : " <<
              test_result << endl;
        }
      }
    }

    // Just to check the result.
    UColAttributeValue alternate_value =
        uni_coll->getAttribute(UCOL_ALTERNATE_HANDLING, status);

    // Try two differen APIs
    uni_result_utf8 = uni_coll->compareUTF8(string1, string2, status);
    // This one seems to work better.
    uni_result = uni_coll->compare(us1, us2, status);

    if (uni_result != uni_result_utf8) {
      cout << "# UNI_COLL COMPARE Unicode String " << uni_result << " ";
      cout << "# UNI_COLL COMPARE UTF8 String " << uni_result_utf8 << endl;
      cout << "# ******* results different in " << label_string << endl;
    }

    if (U_FAILURE(status)) {
        json_object_object_add(
            return_json,
            "error", json_object_new_string("error in uni_coll_compare"));
      no_error = false;
      cout << "## Error in uni_coll->compare: " <<
          label_string << " : " <<
          error_message << endl;
    }
    if (uni_coll) {
      UColAttributeValue alternate_value =
          uni_coll->getAttribute(UCOL_ALTERNATE_HANDLING, status);
    }
    delete uni_coll;
  }

  if (no_error) {
    if (uni_result == UCOL_GREATER) {
      coll_result = false;

      cout << "# UNI_RESULT: " << label_string << " " << uni_result <<
          "  s1: " << string1 << " s2: " << string2 << endl;

      // Check unescaped versions.
      char char_out1[1000] = "";
      char char_out2[1000] = "";
      int32_t chars_out = us1.extract(char_out1, 1000, nullptr, status);
      if (U_FAILURE(status)) {
        test_result = error_message;
        json_object_object_add(
            return_json,
            "error", json_object_new_string("error extracting us1"));
        cout << "# Error in us1.extract: " <<
            label_string << " : " <<
            test_result << endl;
      }

      int32_t chars_out2 = us2.extract(char_out2, 1000, nullptr, status);
      if (U_FAILURE(status)) {
        test_result = error_message;
        // TODO: report the error in creating the instance
        test_result = error_message;
        json_object_object_add(
            return_json,
            "error", json_object_new_string("error extracting us2"));
        cout << "# Error in us2.extract: " <<
            label_string << " : " <<
            test_result << endl;
      }

      // Include data compared in the failing test
      json_object_object_add(
          return_json, "s1", json_object_new_string(string1.c_str()));
      json_object_object_add(
          return_json, "s2", json_object_new_string(string2.c_str()));

      // What was the actual returned value?
      json_object_object_add(
          return_json, "compare", json_object_new_int64(uni_result));
    } else {
      coll_result = true;
    }

    json_object_object_add(
        return_json, "result", json_object_new_boolean(coll_result));
  }

  return  json_object_to_json_string(return_json);
}
