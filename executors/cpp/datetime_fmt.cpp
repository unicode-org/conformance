/********************************************************************
 * testing icu4c datetime format
 */

#include <json-c/json.h>

#include <cstdio>
#include <cstdlib>

#include <iostream>
#include <string>
#include <cstring>

#include "unicode/utypes.h"
#include "unicode/unistr.h"
#include "unicode/datefmt.h"
#include "unicode/locid.h"
#include "unicode/smpdtfmt.h"
#include "unicode/timezone.h"

#include "unicode/uclean.h"

#include "./util.h"

using icu::Calendar;
using icu::DateFormat;
using icu::Locale;
using icu::SimpleDateFormat;
using icu::TimeZone;
using icu::UnicodeString;

using std::cout;
using std::endl;
using std::string;

auto StringToEStyle(string style_string) -> icu::DateFormat::EStyle {
  if (style_string == "full") { return icu::DateFormat::kFull;
}
  if (style_string == "long") { return icu::DateFormat::kLong;
}
  if (style_string == "medium") { return icu::DateFormat::kMedium;
}
  if (style_string == "short") { return icu::DateFormat::kShort;
}
  return icu::DateFormat::kNone;
}

auto TestDatetimeFmt(json_object *json_in) -> string {
  UErrorCode status = U_ZERO_ERROR;

  json_object *label_obj = json_object_object_get(json_in, "label");
  string label_string = json_object_get_string(label_obj);

  Calendar *cal = nullptr;

  UnicodeString u_tz_utc("UTC");
  TimeZone *tz = nullptr;  // TimeZone::createTimeZone(u_tz_utc);

  // The locale for formatted output
  json_object *locale_label_obj = json_object_object_get(json_in, "locale");
  string locale_string;
  if (locale_label_obj != nullptr) {
    locale_string = json_object_get_string(locale_label_obj);
  } else {
    locale_string = "und";
  }

  Locale display_locale(locale_string.c_str());

  // JSON data returned.
  json_object *return_json = json_object_new_object();
  json_object_object_add(return_json, "label", label_obj);

  string calendar_str = "gregory";

  // Get fields out of the options if present
  json_object* options_obj = json_object_object_get(json_in, "options");

  if (options_obj != nullptr) {
    // Check for timezone and calendar
    json_object* option_item =
        json_object_object_get(options_obj, "timeZone");
    if (option_item != nullptr) {
      string timezone_str = json_object_get_string(option_item);
      UnicodeString u_tz(timezone_str.c_str());
      tz = TimeZone::createTimeZone(u_tz);
    }

    json_object* cal_item =
        json_object_object_get(options_obj, "calendar");
    if (cal_item != nullptr) {
      calendar_str = json_object_get_string(cal_item);
    }
  }

  // Add '@calendar=' + calendar_string to locale
  locale_string = locale_string + "@calendar=" + calendar_str;
  display_locale = locale_string.c_str();

  if (tz != nullptr) {
    cal = Calendar::createInstance(tz, display_locale, status);
  } else {
    cal = Calendar::createInstance(display_locale, status);
  }
  if (U_FAILURE(status) != 0) {
    json_object_object_add(
        return_json,
        "error",
        json_object_new_string("Error in createInstance for calendar"));
    return json_object_to_json_string(return_json);
  }

  DateFormat* df;


  // Get the input data as a date object.
  // Types of input:
  //   "input_string" parsable ISO formatted string of an instant
  //       "2020-03-02 10:15:17Z

  string dateStyle_str;
  string timeStyle_str;

  // Expected values if neither dateStyle nor timeStyle is given explicitly.
  icu::DateFormat::EStyle date_style = icu::DateFormat::EStyle::kNone;
  icu::DateFormat::EStyle time_style = icu::DateFormat::EStyle::kNone;

  // Set this as default unless there's an explicit setting of
  // skeleton or date_style.
  string default_skeleton_string = "M/d/yyyy";

  // Indicates if the library outputs date and time with the "at", as in "July 1 at 10:00"
  bool supports_atTime = true;

  string dateTimeFormatType_str = "";

  if (options_obj != nullptr) {
    json_object* option_item = json_object_object_get(options_obj, "dateStyle");
    if (option_item != nullptr) {
      dateStyle_str = json_object_get_string(option_item);
      date_style = StringToEStyle(dateStyle_str);
    }

    option_item = json_object_object_get(options_obj, "timeStyle");
    if (option_item != nullptr) {
      timeStyle_str = json_object_get_string(option_item);
      time_style = StringToEStyle(timeStyle_str);
    }

    option_item = json_object_object_get(options_obj, "dateTimeFormatType");
    if (option_item != nullptr) {
      // What this data item expects.
      dateTimeFormatType_str = json_object_get_string(option_item);
      // Check if this is not supported?
      if ((dateTimeFormatType_str == "atTime" && !supports_atTime) ||
          (dateTimeFormatType_str != "atTime" && supports_atTime)) {
        const char* error_name = u_errorName(status);
        // Inexact result is unsupported.
        json_object_object_add(
            return_json,
            "error_type",
            json_object_new_string("unsupported"));
        json_object_object_add(
            return_json,
            "unsupported",
            json_object_new_string("format type"));
        string detail_str = "formatType: " + dateTimeFormatType_str;
        json_object_object_add(
            return_json,
            "error_detail",
            json_object_new_string(detail_str.c_str()));
        return json_object_to_json_string(return_json);
      }
    }
  }

  json_object *date_skeleton_item =
      json_object_object_get(options_obj, "skeleton");
  string skeleton_string;
  if (date_style == icu::DateFormat::EStyle::kNone &&
      time_style == icu::DateFormat::EStyle::kNone) {
    skeleton_string = default_skeleton_string;
  }
  if (date_skeleton_item != nullptr) {
    // Data specifies a date time skeleton. Make a formatter based on this.
    skeleton_string = json_object_get_string(date_skeleton_item);
  }
  if (!skeleton_string.empty()) {
    UnicodeString u_skeleton(skeleton_string.c_str());
    if (cal != nullptr) {
      df = DateFormat::createInstanceForSkeleton(cal,
                                                 u_skeleton,
                                                 display_locale,
                                                 status);
    } else {
      df = DateFormat::createInstanceForSkeleton(u_skeleton,
                                                 display_locale,
                                                 status);
    }
    if (check_icu_error(status, return_json, "createInstanceForSkeleton")) {
      return json_object_to_json_string(return_json);
    }
  } else {
    // Create default formatter
    df = DateFormat::createDateTimeInstance(
        date_style,
        time_style,
        display_locale);
  }

  if (df == nullptr) {
    // Post an error in the return
    json_object_object_add(
        return_json,
        "error",
        json_object_new_string("Cannot construct datetime formatter"));
    return json_object_to_json_string(return_json);
  }

  // !!! IS OFFSET ALREADY CONSIDERED?
  if (tz != nullptr) {
    df->setTimeZone(*tz);
  }

  // Use ISO string form of the date/time.
  json_object *input_string_obj =
      json_object_object_get(json_in, "input_string");
  // Prefer ISO input as input.
  json_object *input_millis = json_object_object_get(json_in, "input_millis");

  UDate test_date_time;
  if (input_string_obj != nullptr) {
    Locale und_locale("und");

    string input_date_string = json_object_get_string(input_string_obj);

    // SimpleDateFormat can't parse options or timezone offset
    // First, remove options starting with "["
    std::size_t pos = input_date_string.find("[");
    if (pos >= 0) {
      input_date_string = input_date_string.substr(0, pos);
    }
    // Now remove the explicit offset
    pos = input_date_string.find("+");
    if (pos >= 0) {
      input_date_string = input_date_string.substr(0, pos);
    }
    pos = input_date_string.rfind("-");
    if (pos >= 10) {
      // DOn't clip in the date fields
      input_date_string = input_date_string.substr(0, pos);
    }
    UnicodeString date_ustring(input_date_string.c_str());

    // TODO:  handles the offset +/-
    SimpleDateFormat iso_date_fmt(u"y-M-d'T'h:m:sZ", und_locale, status);
    if (U_FAILURE(status) != 0) {
      string error_name = u_errorName(status);
      string error_message =
          "# iso_date_fmt constructor failure: " +
          error_name;

      json_object_object_add(
          return_json,
          "error",
          json_object_new_string("No date/time data provided"));

      return json_object_to_json_string(return_json);
    }

    // Get date from the parser if possible.
    test_date_time = iso_date_fmt.parse(date_ustring, status);
    if (check_icu_error(status,
                        return_json,
                        "# iso_date_fmt parse failure" + input_date_string)) {
      return json_object_to_json_string(return_json);
    }
  } else if (input_millis != nullptr) {
    test_date_time = json_object_get_double(input_millis);
  } else {
    json_object_object_add(
        return_json,
        "error",
        json_object_new_string("No date/time data provided"));

    string return_string = json_object_to_json_string(return_json);
    return json_object_to_json_string(return_json);
  }

  // The output of the formatting step
  UnicodeString formatted_result;
  df->format(test_date_time, formatted_result);

  // Get the resulting value as a string
  string result_string;
  formatted_result.toUTF8String(result_string);

  // Good calls all around. Send the result!
  json_object_object_add(return_json,
                         "result",
                         json_object_new_string(result_string.c_str()));

  return json_object_to_json_string(return_json);
}
