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
#include <map>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>

#include "./util.h"

using std::cout;
using std::endl;
using std::map;
using std::string;
using std::string_view;
using std::vector;

using icu::Locale;
using icu::UnicodeString;
using icu::Collator;
using icu::RuleBasedCollator;

const char error_message[] = "error";

// From icu/icu4c/source/text/intltest/collationtest.cpp
std::map<string, UColAttribute> attribute_map = {
    { "backwards", UCOL_FRENCH_COLLATION },
    { "alternate", UCOL_ALTERNATE_HANDLING },
    { "caseFirst", UCOL_CASE_FIRST },
    { "caseLevel", UCOL_CASE_LEVEL },
    // UCOL_NORMALIZATION_MODE is turned on and off automatically.
    { "strength", UCOL_STRENGTH },
    // UCOL_HIRAGANA_QUATERNARY_MODE is deprecated.
    { "numeric", UCOL_NUMERIC_COLLATION }
};

std::map<string, UColAttributeValue> values_map = {
    { "default", UCOL_DEFAULT },
    { "primary", UCOL_PRIMARY },
    { "secondary", UCOL_SECONDARY },
    { "tertiary", UCOL_TERTIARY },
    { "quaternary", UCOL_QUATERNARY },
    { "identical", UCOL_IDENTICAL },
    { "off", UCOL_OFF },
    { "on", UCOL_ON },
    { "shifted", UCOL_SHIFTED },
    { "non-ignorable", UCOL_NON_IGNORABLE },
    { "lower", UCOL_LOWER_FIRST },
    { "upper", UCOL_UPPER_FIRST }
};

std::map<string, UColReorderCode> val_attribute_map = {
  // For maxVariable setting
  {"space", UCOL_REORDER_CODE_SPACE},
  {"punct", UCOL_REORDER_CODE_PUNCTUATION},
  {"symbol", UCOL_REORDER_CODE_SYMBOL},
  {"currency", UCOL_REORDER_CODE_CURRENCY}
};

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
  char delimiter = ' ';
  std::stringstream ss(reorder_string);

  vector<string> reorder_strings;
  string segment;
  while (std::getline(ss, segment, delimiter)) {
    reorder_strings.push_back(segment);
  }
  if (debug_level > 0) {
    cout << "REORDER count: " << reorder_strings.size() << endl;
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
      return_codes.push_back(map_it->second);
      if (debug_level > 0) {
        cout << "# RECOGNIZED SCRIPT CODE: " <<
            script_tag << " --> " << map_it->second << endl;
      }
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
auto TestCollator(json_object *json_in) -> string {
  int debug_level = 0;

  UErrorCode status = U_ZERO_ERROR;

  json_object *label_obj = json_object_object_get(json_in, "label");
  string label_string = json_object_get_string(label_obj);

  json_object *str1 = json_object_object_get(json_in, "s1");
  json_object *str2 = json_object_object_get(json_in, "s2");

  // We need to handle null characters, so get the length and the bytes.
  int str1_len = json_object_get_string_len(str1);
  string_view string1(json_object_get_string(str1), str1_len);
  int str2_len = json_object_get_string_len(str2);
  string_view string2(json_object_get_string(str2), str2_len);

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

  // Apply reordering if present
  json_object *reorder_obj = json_object_object_get(json_in, "reorder");
  string reorder_string;
  vector<int32_t> reorder_codes_v;
  if (reorder_obj) {
    reorder_string = json_object_get_string(reorder_obj);
    reorder_codes_v = BuildReorderList(reorder_string, debug_level);
  }

  json_object *alternate_obj = json_object_object_get(json_in, "alternate");
  UColAttributeValue alternate_value;
  if (alternate_obj) {
    string alternate = json_object_get_string(alternate_obj);
    if (alternate == "shifted") {
      alternate_value = UCOL_SHIFTED;
    } else
      if (alternate == "non-ignorable") {
        alternate_value = UCOL_NON_IGNORABLE;
      }
  }

  // Check for rule-based collation
  json_object *rules_obj = json_object_object_get(json_in, "rules");
  int rules_len = json_object_get_string_len(rules_obj);

  string_view rules_string(json_object_get_string(rules_obj), rules_len);
  UnicodeString uni_rules = UnicodeString::fromUTF8(rules_string).unescape();
  string actual_rules = "";

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

  if (rules_len > 0) {
    // Make sure normalization is consistent
    rb_coll = new RuleBasedCollator(uni_rules, UCOL_ON, status);
    if (check_icu_error(status, return_json, "create RuleBasedCollator")) {
      // Put json_in as the actual input received.
      json_object_object_add(
          return_json, "actual_options",
          json_object_new_string(json_object_get_string(json_in)));

      return json_object_to_json_string(return_json);
    }

    // Get the rules as seen by the collator.
    UnicodeString gotten_rules = rb_coll->getRules();
    gotten_rules.toUTF8String(actual_rules);

    // Make sure that attributes and optionsare set for rule based collator, too.
    if (reorder_obj) {
      rb_coll->setReorderCodes(reorder_codes_v.data(), reorder_codes_v.size(), status);
      if (check_icu_error(status, return_json, "rb_coll with reorder")) {
        return json_object_to_json_string(return_json);
      }
    }

    if (alternate_obj) {
      rb_coll->setAttribute(UCOL_ALTERNATE_HANDLING, alternate_value, status);
      if (check_icu_error(status, return_json, "alternate")) {
        json_object_object_add(
            return_json, "actual_options",
            json_object_new_string(json_object_get_string(json_in)));

        return json_object_to_json_string(return_json);
      }
    }

    json_object *case_first_obj = json_object_object_get(json_in, "caseFirst");
    if (case_first_obj) {
      // TODO: Check status
      string case_first = json_object_get_string(case_first_obj);
      if (case_first == "lower") {
        rb_coll->setAttribute(UCOL_CASE_FIRST, UCOL_LOWER_FIRST, status);
      } else
        if (case_first == "upper") {
          rb_coll->setAttribute(UCOL_CASE_FIRST, UCOL_UPPER_FIRST, status);
        }
    }

    json_object *case_level_obj = json_object_object_get(json_in, "caseLevel");
    if (case_level_obj) {
      // TODO: Check status
      string case_level = json_object_get_string(case_level_obj);
      if (case_level == "off") {
        rb_coll->setAttribute(UCOL_CASE_LEVEL, UCOL_OFF, status);
      } else
        if (case_level == "on") {
          rb_coll->setAttribute(UCOL_CASE_LEVEL, UCOL_ON, status);
        }
    }

    if (strength_obj != nullptr) {
      rb_coll->setStrength(strength_type);
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
      if (check_icu_error(status, return_json,
                          "Collator:createInstance")) {
        json_object_object_add(
            return_json, "actual_options",
            json_object_new_string(json_object_get_string(json_in)));

        return json_object_to_json_string(return_json);
      }
    }

    if (alternate_obj) {
      uni_coll->setAttribute(UCOL_ALTERNATE_HANDLING, alternate_value, status);
      if (check_icu_error(status, return_json, "alternate")) {
        json_object_object_add(
            return_json, "actual_options",
            json_object_new_string(json_object_get_string(json_in)));

        return json_object_to_json_string(return_json);
      }
    }

    if (reorder_obj) {
      uni_coll->setReorderCodes(reorder_codes_v.data(), reorder_codes_v.size(), status);
      if (check_icu_error(status, return_json, "uni_coll->setReorderCodes")) {
        return json_object_to_json_string(return_json);
      }
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

    // Check the other attributes and set values as needed.
    for (auto const& [key, ucol_attribute] : attribute_map) {
      // Is this key in the json data.
      json_object *attribute_obj = json_object_object_get(json_in, key.c_str());
      if (attribute_obj != nullptr) {
        // Get the test value and the corresponding attribute value
        string test_value = json_object_get_string(attribute_obj);

        std::map<string,UColAttributeValue>::iterator values_it;
        values_it = values_map.find(test_value);
        if (values_it != values_map.end()) {
          // This is the value that we can set
          uni_coll->setAttribute(ucol_attribute, values_it->second, status);
          if (check_icu_error(
                  status, return_json,
                  "getet UCOL_ALTERNATE_HANDLING")) {
            return json_object_to_json_string(return_json);
          }
        }
      }
    }

    // Set maxVariable, too!
    json_object *attribute_obj = json_object_object_get(json_in, "maxVariable");
    if (attribute_obj != nullptr) {
      string test_value = json_object_get_string(attribute_obj);
      std::map<string, UColReorderCode>::iterator values_it;
      values_it = val_attribute_map.find(test_value);
      if (values_it != val_attribute_map.end()) {
        uni_coll->setMaxVariable(values_it->second, status);
      }
    }

    // Perform the string comparison
    uni_result = uni_coll->compare(us1, us2, status);
    if (check_icu_error( status, return_json, "uni_coll->compare")) {
      return json_object_to_json_string(return_json);
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
    // Include the data compared in the failing test
    json_object* actual_values = json_object_new_object();

    json_object_object_add(
        actual_values, "s1_actual", json_object_new_string_len(string1.data(), string1.size()));
    json_object_object_add(
        actual_values, "s2_actual", json_object_new_string_len(string2.data(), string2.size()));

    json_object_object_add(
        actual_values, "input",
        json_object_new_string(json_object_get_string(json_in)));

    json_object_object_add(
        return_json, "actual_options",
        actual_values);

    if (rules_len > 0) {
      // Show the rules that were actually found.
      json_object_object_add(
          actual_values,
          "rules_actual",
          json_object_new_string(actual_rules.c_str())
                             );
    }

    // Record the actual returned value
    json_object_object_add(
        return_json, "compare", json_object_new_int64(uni_result));
  }

  // The output
  json_object_object_add(
      return_json, "result", json_object_new_boolean(static_cast<json_bool>(coll_result)));

  return  json_object_to_json_string(return_json);
}
