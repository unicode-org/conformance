/********************************************************************
 * Comments and license as needed
 ************************************

/******
 * testing datetime format
 */


#include "unicode/utypes.h"
#include "unicode/unistr.h"
#include "unicode/datefmt.h"
#include "unicode/locid.h"
#include "unicode/smpdtfmt.h"
#include "unicode/timezone.h"

#include "unicode/uclean.h"

#include "util.h"
#include <stdio.h>
#include <stdlib.h>

#include <json-c/json.h>

#include <iostream>
#include <string>
#include <cstring>

using icu::Calendar;
using icu::DateFormat;
using icu::SimpleDateFormat;
using icu::TimeZone;

using std::cout;
using std::endl;
using std::string;

icu::DateFormat::EStyle stringToEStyle(string style_string) {
  if (style_string == "full") return icu::DateFormat::kFull;
  if (style_string == "long") return icu::DateFormat::kLong;
  if (style_string == "medium") return icu::DateFormat::kMedium;
  if (style_string == "short") return icu::DateFormat::kShort;
  return icu::DateFormat::kNone;
}

const string test_datetime_fmt(json_object *json_in) {
  UErrorCode status = U_ZERO_ERROR;

  json_object *label_obj = json_object_object_get(json_in, "label");
  string label_string = json_object_get_string(label_obj);

  Calendar *cal = nullptr;
  TimeZone *tz = nullptr;

  // The locale for formatted output
  json_object *locale_label_obj = json_object_object_get(json_in, "locale");
  string locale_string;
  if (locale_label_obj) {
    locale_string = json_object_get_string(locale_label_obj);
  } else {
    locale_string = "und";
  }

  Locale displayLocale(locale_string.c_str());
  Locale und_locale("und");

  // JSON data returned.
  json_object *return_json = json_object_new_object();
  json_object_object_add(return_json, "label", label_obj);

  string calendar_str;

  // Get fields out of the options if present
  json_object* options_obj = json_object_object_get(json_in, "options");

  if (options_obj) {
    json_object* cal_item = json_object_object_get(options_obj, "calendar");
    if (cal_item) {
      calendar_str = json_object_get_string(cal_item);

      // Add '@calendar=' + calendar_string to locale
      locale_string = locale_string + "@calendar=" + calendar_str;

      cout << "# Calendar locale: " << locale_string << endl;
      if (tz) {
        cal = Calendar::createInstance(*tz, displayLocale, status);
      } else {
        cal = Calendar::createInstance(displayLocale, status);
      }
      if (U_FAILURE(status)) {
        cout << "# ERROR in createInstance for Calendar" << endl;
        json_object_object_add(
            return_json,
            "error",
            json_object_new_string("Error in createInstance for calendar"));
        return json_object_to_json_string(return_json);
      }
    }
  }

  DateFormat* df;


  // Get the input data as a date object.
  // Types of input:
  //   "input_string" parsable ISO formatted string such as
  //       "2020-03-02 10:15:17 -08:00"

  string dateStyle_str;
  string timeStyle_str;
  string timezone_str;

  // Expected values if neither dateStyle nor timeStyle is given explicitly.
  icu::DateFormat::EStyle date_style = icu::DateFormat::EStyle::kNone;
  icu::DateFormat::EStyle time_style = icu::DateFormat::EStyle::kNone;

  if (options_obj) {
    json_object* option_item = json_object_object_get(options_obj, "dateStyle");
    if (option_item) {
      dateStyle_str = json_object_get_string(option_item);
      date_style = stringToEStyle(dateStyle_str);
    }

    option_item = json_object_object_get(options_obj, "timeStyle");
    if (option_item) {
      timeStyle_str = json_object_get_string(option_item);
      time_style = stringToEStyle(timeStyle_str);
    }

    option_item = json_object_object_get(options_obj, "timeZone");
    if (option_item) {
      timezone_str = json_object_get_string(option_item);
      UnicodeString u_tz(timezone_str.c_str());
      tz = TimeZone::createTimeZone(u_tz);
      cout << "# Created timezone " << tz << " for " << timezone_str << endl;
    }
  }

  json_object *date_skeleton_obj =
      json_object_object_get(json_in, "skeleton");
  if (date_skeleton_obj) {
    // Data specifies a date time skeleton. Make a formatter based on this.
    string skeleton_string = json_object_get_string(date_skeleton_obj);

    cout << "# Skeleton = " << skeleton_string << endl;
    UnicodeString u_skeleton(skeleton_string.c_str());
    if (cal) {
      cout << "  Cal defined " << endl;
      df = DateFormat::createInstanceForSkeleton(cal,
                                                 u_skeleton,
                                                 displayLocale,
                                                 status);
    } else {
      cout << "  NO CAL DEFINED " << endl;
      df = DateFormat::createInstanceForSkeleton(u_skeleton,
                                                 displayLocale,
                                                 status);
    }
    if (U_FAILURE(status)) {
      cout << "# ERROR in createInstanceForSkeleton" << endl;
      json_object_object_add(
          return_json,
          "error",
          json_object_new_string("Error in createInstanceForSkeleton"));
      return json_object_to_json_string(return_json);
    }
  } else {
    // Create default formatter
    cout << "# createDateTimeInstance: dstyle " <<
        date_style << ", tstyle " <<
        time_style << " locale " <<
        locale_string <<
        endl;

    df = DateFormat::createDateTimeInstance(
        date_style,
        time_style,
        displayLocale);
  }

  if (df == nullptr) {
    cout << "# DATE TIME FORMATTER == nullptr == " << df << endl;
    // Post an error in the return
    json_object_object_add(
        return_json,
        "error",
        json_object_new_string("Cannot construct datetime formatter"));
    return json_object_to_json_string(return_json);
  }

  if (tz) {
    cout <<
        "# Setting TZ " <<
        tz <<
        endl;
    df->setTimeZone(*tz);
  }


  // Use ISO string form of the date/time.
  json_object *input_string_obj = json_object_object_get(json_in, "input_string");
  // Prefer ISO input as input.
  json_object *input_millis = json_object_object_get(json_in, "input_millis");

  UDate testDateTime;
  if (input_string_obj) {
    string input_date_string = json_object_get_string(input_string_obj);

    UnicodeString date_ustring(input_date_string.c_str());

    SimpleDateFormat iso_date_fmt(u"y-M-d'T'h:m:s.SSSZ", und_locale, status);
    if (U_FAILURE(status)) {
      string error_name = u_errorName(status);
      string error_message =
          "# iso_date_fmt constructor failure: " +
          error_name;

      cout << error_message << endl;

      json_object_object_add(
          return_json,
          "error",
          json_object_new_string("No date/time data provided"));

      return json_object_to_json_string(return_json);
    }

    // Get date from the parser if possible.
    testDateTime = iso_date_fmt.parse(date_ustring, status);

    if (U_FAILURE(status)) {
      string error_message = "# iso_date_fmt parse failure: " +
                             input_date_string + " " +
                             u_errorName(status);
      cout << error_message << endl;

      json_object_object_add(
          return_json,
          "error",
          json_object_new_string(error_message.c_str()));

      return json_object_to_json_string(return_json);
    }
  } else
    if (input_millis) {
      testDateTime = json_object_get_double(input_millis);
    } else {
      // TODO: Post an error due to missing date/time data.
      json_object_object_add(
          return_json,
          "error",
          json_object_new_string("No date/time data provided"));

      string return_string = json_object_to_json_string(return_json);
      return json_object_to_json_string(return_json);
    }

  // The output of the formatting
  UnicodeString formatted_result;

  df->format(testDateTime, formatted_result);

  // Get the resulting value as a string
  string test_result;
  int32_t chars_out;  // Results of extracting characters from Unicode string
  char test_result_string[1000] = "";
  chars_out = formatted_result.extract(test_result_string, 1000, nullptr, status);

  if (U_FAILURE(status)) {
    // TODO: Return error.
    cout << "# formatted result: extract error. " << chars_out << endl;
    json_object_object_add(
        return_json,
        "error",
        json_object_new_string("Failed extracting test result"));
    return json_object_to_json_string(return_json);
  }

  // Good calls all around. Send the result!
  json_object_object_add(return_json,
                         "result",
                         json_object_new_string(test_result_string));

  return json_object_to_json_string(return_json);
}
