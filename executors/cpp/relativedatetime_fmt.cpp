/*
 * testing icu4c relative datetime format
 */

#include <unicode/utypes.h>

#include <json-c/json.h>

#include <unicode/locid.h>
#include <unicode/reldatefmt.h>
#include <unicode/udisplaycontext.h>
#include <unicode/unistr.h>

#include <cstdio>
#include <cstdlib>

#include <iostream>
#include <string>
#include <cstring>

#include "./util.h"

using icu::Locale;
using icu::NumberFormat;
using icu::RelativeDateTimeFormatter;
using icu::UnicodeString;

using std::string;

/*
 *  Check for ICU errors and add to output if needed.
 */
extern auto check_icu_error(UErrorCode error_code,
                                  json_object *return_json,
                                  string message_to_add_if_error) -> const bool;

auto StringToStyleEnum(string style_string) -> UDateRelativeDateTimeFormatterStyle {
  if (style_string == "long") { return UDAT_STYLE_LONG;
}
  if (style_string == "short") { return UDAT_STYLE_SHORT;
}
  if (style_string == "narrow") { return UDAT_STYLE_NARROW;
}
  return UDAT_STYLE_LONG;  // Default
}

auto StringToRelativeUnitEnum(string unit_string) -> URelativeDateTimeUnit {
  URelativeDateTimeUnit rel_unit;
  if (unit_string == "day") {
    return UDAT_REL_UNIT_DAY;
  } if (unit_string == "hour") {
    return UDAT_REL_UNIT_HOUR;
  } else if (unit_string == "minute") {
    return UDAT_REL_UNIT_MINUTE;
  } else if (unit_string == "month") {
    return UDAT_REL_UNIT_MONTH;
  } else if (unit_string == "second") {
    return UDAT_REL_UNIT_SECOND;
  } else if (unit_string == "week") {
    return UDAT_REL_UNIT_WEEK;
  } else if (unit_string == "quarter") {
    return UDAT_REL_UNIT_QUARTER;
  } else if (unit_string == "year") {
    return UDAT_REL_UNIT_YEAR;
  }
  // A default
  return UDAT_REL_UNIT_DAY;
}

string TestRelativeDateTimeFmt(json_object *json_in) {
  UErrorCode status = U_ZERO_ERROR;

  json_object *label_obj = json_object_object_get(json_in, "label");
  string label_string = json_object_get_string(label_obj);

  UDisplayContext cap_context = UDISPCTX_CAPITALIZATION_NONE;
  NumberFormat *nf = nullptr;

  // The locale for formatted output
  json_object *locale_label_obj = json_object_object_get(json_in, "locale");
  string locale_string;
  if (locale_label_obj != nullptr) {
    locale_string = json_object_get_string(locale_label_obj);
  } else {
    locale_string = "und";
  }

  json_object *unit_obj = json_object_object_get(json_in, "unit");
  string unit_string = json_object_get_string(unit_obj);

  json_object *count_obj = json_object_object_get(json_in, "count");
  string count_string = json_object_get_string(count_obj);
  double quantity = std::stod(count_string);

  json_object *return_json = json_object_new_object();
  json_object_object_add(return_json, "label", label_obj);

  // Get fields out of the options if present
  json_object* options_obj = json_object_object_get(json_in, "options");

  string style_string = "long";  // Default
  string numbering_system_string = "";  // Default
  string numeric_option = "";
  if (options_obj != nullptr) {
    json_object *style_obj = json_object_object_get(options_obj, "style");
    if (style_obj != nullptr) {
      style_string = json_object_get_string(style_obj);
    }
    json_object *ns_obj =
        json_object_object_get(options_obj, "numberingSystem");
    if (ns_obj != nullptr) {
      numbering_system_string = json_object_get_string(ns_obj);
    }
    json_object *numeric_obj = json_object_object_get(options_obj, "numeric");
    if (numeric_obj != nullptr) {
      numeric_option = json_object_get_string(numeric_obj);
    }
  }

  UDateRelativeDateTimeFormatterStyle
      rdtf_style = StringToStyleEnum(style_string);

  URelativeDateTimeUnit rel_unit;
  rel_unit = StringToRelativeUnitEnum(unit_string);

  // Add variants to the locale.
  string locale_selection_string = locale_string;
  if (numbering_system_string != "") {
    locale_selection_string =
        locale_string + "-u-nu-" + numbering_system_string;
  }

  Locale display_locale(locale_selection_string.c_str());

  // Construct a formatter
  RelativeDateTimeFormatter
      rdtf(display_locale, nf, rdtf_style, cap_context, status);

  if (check_icu_error(status, return_json, "Constructor")) {
    return json_object_to_json_string(return_json);
  }

  // The output of the formatting
  UnicodeString formatted_result;

  if (numeric_option == "auto") {
    rdtf.format(quantity, rel_unit, formatted_result, status);
  } else {
    // Default is "always"
    rdtf.formatNumeric(quantity, rel_unit, formatted_result, status);
  }

  if (check_icu_error(status, return_json, "In format or formatNumeric")) {
    return json_object_to_json_string(return_json);
  }

  // Get the resulting value as a string
  string test_result;
  formatted_result.toUTF8String(test_result);

  // Good calls all around. Send the result!
  json_object_object_add(return_json,
                         "result",
                         json_object_new_string(test_result.c_str()));

  return json_object_to_json_string(return_json);
}
