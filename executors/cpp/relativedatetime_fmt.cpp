/********************************************************************
 * testing icu4c relative datetime format
 */

#include <json-c/json.h>

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#include <cstring>
#include <iostream>
#include <string>

#include "unicode/utypes.h"
#include "unicode/unistr.h"
#include "unicode/locid.h"
#include "unicode/numfmt.h"
#include "unicode/reldatefmt.h"
#include "unicode/udisplaycontext.h"

using icu::Locale;
using icu::NumberFormat;
using icu::RelativeDateTimeFormatter;
using icu::UnicodeString;

using std::cout;
using std::endl;
using std::string;

UDateRelativeDateTimeFormatterStyle StringToRelative(string style_string) {
  if (style_string == "long") return UDAT_STYLE_LONG;
  if (style_string == "short") return UDAT_STYLE_SHORT;
  if (style_string == "narrow") return UDAT_STYLE_NARROW;
  return UDAT_STYLE_LONG;  // Default
}

const string TestRelativeDateTimeFmt(json_object *json_in) {
  UErrorCode status = U_ZERO_ERROR;

  json_object *label_obj = json_object_object_get(json_in, "label");
  string label_string = json_object_get_string(label_obj);

  UDisplayContext cap_context = UDISPCTX_CAPITALIZATION_NONE;
  NumberFormat *nf = nullptr;

  // The locale for formatted output
  json_object *locale_label_obj = json_object_object_get(json_in, "locale");
  string locale_string;
  if (locale_label_obj) {
    locale_string = json_object_get_string(locale_label_obj);
  } else {
    locale_string = "und";
  }

  Locale display_locale(locale_string.c_str());

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
  if (options_obj) {
    json_object *style_obj = json_object_object_get(options_obj, "style");
    if (style_obj) {
      style_string = json_object_get_string(style_obj);
    }
  }

  UDateRelativeDateTimeFormatterStyle
      rdtf_style = StringToRelative(style_string);

  UDateRelativeUnit rel_unit;
  if (unit_string == "day") {
    rel_unit = UDAT_RELATIVE_DAYS;
  } else if (unit_string == "hour") {
    rel_unit = UDAT_RELATIVE_HOURS;
  } else if (unit_string == "minute") {
    rel_unit = UDAT_RELATIVE_MINUTES;
  } else if (unit_string == "month") {
    rel_unit = UDAT_RELATIVE_MONTHS;
  } else if (unit_string == "second") {
    rel_unit = UDAT_RELATIVE_SECONDS;
  } else if (unit_string == "week") {
    rel_unit = UDAT_RELATIVE_WEEKS;
  } else if (unit_string == "year") {
    rel_unit = UDAT_RELATIVE_YEARS;
  } else if (unit_string == "quarter") {
    // This is not supported.
    json_object_object_add(
        return_json,
        "error",
        json_object_new_string("unsupported unit"));
    json_object_object_add(
        return_json,
        "error_type",
        json_object_new_string("unsupported"));
    json_object_object_add(
        return_json,
        "unsupported",
        json_object_new_string("Bad relative date time unit"));
    json_object_object_add(
        return_json,
        "error_detail",
        json_object_new_string(unit_string.c_str()));

    // This can't be processed so return now.
    return json_object_to_json_string(return_json);
  }

  // Construct a formatter
  RelativeDateTimeFormatter
      rdtf(display_locale, nf, rdtf_style, cap_context, status);

  if (U_FAILURE(status)) {
    json_object_object_add(
        return_json,
        "error",
        json_object_new_string("Error creating RelativeDateTimeFormatter"));
    json_object_object_add(
        return_json,
        "error_detail",
        json_object_new_string("no detail available"));
    return json_object_to_json_string(return_json);
  }

  UDateDirection direction = UDAT_DIRECTION_NEXT;
  if (quantity < 0.0) {
    direction = UDAT_DIRECTION_LAST;
  } else if (quantity > 0.0) {
    direction = UDAT_DIRECTION_NEXT;
  }
  cout << "** direction for " << quantity << ", ENUM = " << direction << endl;

  // The output of the formatting
  UnicodeString formatted_result;

  rdtf.format(fabs(quantity), direction, rel_unit, formatted_result, status);

  if (U_FAILURE(status)) {
    json_object_object_add(
        return_json,
        "error",
        json_object_new_string("Error calling rdtf.format"));
    return json_object_to_json_string(return_json);
  }

  // Get the resulting value as a string
  char test_result_string[1000] = "";
  formatted_result.extract(
      test_result_string, 1000, nullptr, status);  // ignore return value

  if (U_FAILURE(status)) {
    json_object_object_add(
        return_json,
        "error",
        json_object_new_string("Failed extracting test result"));
    json_object_object_add(
        return_json,
        "error_detail",
        json_object_new_string("no detail available"));
  } else {
    // Good calls all around. Send the result!
    json_object_object_add(return_json,
                           "result",
                           json_object_new_string(test_result_string));
  }

  return json_object_to_json_string(return_json);
}
