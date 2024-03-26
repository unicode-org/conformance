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
#include "unicode/uclean.h"

#include "util.h"
#include <stdio.h>
#include <stdlib.h>

#include <json-c/json.h>

#include <iostream>
#include <string>
#include <cstring>

using icu::DateFormat;

using std::cout;
using std::endl;
using std::string;

icu::DateFormat::EStyle stringToEStyle(string style_string) {
  if (style_string == "full") return icu::DateFormat::kFull;
  if (style_string == "long") return icu::DateFormat::kLong;
  if (style_string == "medium") return icu::DateFormat::kMedium;
  if (style_string == "short") return icu::DateFormat::kShort;
  return icu::DateFormat::kDefault;
}


const string test_datetime_fmt(json_object *json_in) {
  UErrorCode status = U_ZERO_ERROR;

  json_object *label_obj = json_object_object_get(json_in, "label");
  string label_string = json_object_get_string(label_obj);

  // The locale for formatted output
  json_object *locale_label_obj = json_object_object_get(json_in, "locale");
  string locale_string;
  if (locale_label_obj) {
    locale_string = json_object_get_string(locale_label_obj);
  } else {
    locale_string = "und";
  }

  Locale displayLocale(locale_string.c_str());

  DateFormat* df;

  // Get the input data as a date object.

  // Types of input:
  //   "input_millis" milliseconds since base date/time
  //   "input_string" parsable string such as "2020-03-02 10:15:17 -08:00"
  //   OTHER?

  string dateStyle_str;
  string timeStyle_str;
  string calendar_str;
  string timezone_str;

  string era_str;
  string year_str;
  string month_str;
  string weekday_str;
  string day_str;
  string hour_str;
  string minute_str;
  string second_str;
  int fractional_seconds_digits = 0;

  // Get fields out of the options if present
  json_object* options_obj = json_object_object_get(json_in, "options");

  icu::DateFormat::EStyle date_style = icu::DateFormat::EStyle::kNone;
  icu::DateFormat::EStyle time_style = icu::DateFormat::EStyle::kNone;

  if (options_obj) {
    json_object* option_item = json_object_object_get(options_obj, "dateStyle");
    if (option_item) {
      dateStyle_str = json_object_get_string(option_item);
      date_style = stringToEStyle(dateStyle_str);
      cout << "# dateStyle: " << dateStyle_str << " " << date_style << endl;
    }

    option_item = json_object_object_get(options_obj, "timeStyle");
    if (option_item) {
      timeStyle_str = json_object_get_string(option_item);
      time_style = stringToEStyle(timeStyle_str);
      cout << "# timeStyle: " << timeStyle_str << " " << time_style << endl;
    }

    option_item = json_object_object_get(options_obj, "calendar");
    if (option_item) {
      dateStyle_str = json_object_get_string(option_item);
      cout << "# calendar: " << calendar_str << endl;
    }

    option_item = json_object_object_get(options_obj, "timezone");
    if (option_item) {
      timezone_str = json_object_get_string(option_item);
      cout << "# timezone: " << timezone_str << endl;
    }

    option_item = json_object_object_get(options_obj, "era");
    if (option_item) {
      era_str = json_object_get_string(option_item);
      cout << "# era: " << era_str << endl;
    }

    option_item = json_object_object_get(options_obj, "year");
    if (option_item) {
      year_str = json_object_get_string(option_item);
      cout << "# year: " << year_str << endl;
    }

    option_item = json_object_object_get(options_obj, "month");
    if (option_item) {
      month_str = json_object_get_string(option_item);
      cout << "# month: " << month_str << endl;
    }

    option_item = json_object_object_get(options_obj, "weekday");
    if (option_item) {
      weekday_str = json_object_get_string(option_item);
      cout << "# weekdat: " << weekday_str << endl;
    }

    option_item = json_object_object_get(options_obj, "day");
    if (option_item) {
      day_str = json_object_get_string(option_item);
      cout << "# day: " << day_str << endl;
    }

    option_item = json_object_object_get(options_obj, "hour");
    if (option_item) {
      hour_str = json_object_get_string(option_item);
      cout << "# hour: " << hour_str << endl;
    }

    option_item = json_object_object_get(options_obj, "minute");
    if (option_item) {
      minute_str = json_object_get_string(option_item);
      cout << "# minute: " << minute_str << endl;
    }

    option_item = json_object_object_get(options_obj, "second");
    if (option_item) {
      second_str = json_object_get_string(option_item);
      cout << "# second: " << second_str << endl;
    }

    option_item = json_object_object_get(options_obj, "fractional_seconds_digits");
    if (option_item) {
      fractional_seconds_digits = json_object_get_int(option_item);
      cout << "# fractional seconds digits: " << fractional_seconds_digits << endl;
    }

  }

  json_object *date_skeleton_obj = json_object_object_get(json_in, "datetime_skeleton");
  if (date_skeleton_obj) {
    // Data specifies a date time skeleton. Make a formatter based on this.
    string skeleton_string = json_object_get_string(date_skeleton_obj);

    cout << "# Skelecton = " << skeleton_string << endl;

    UnicodeString u_skeleton = skeleton_string.c_str();
    df = DateFormat::createInstanceForSkeleton(u_skeleton,
                                               displayLocale,
                                               status);
    if (U_FAILURE(status)) {
      // TODO: Return error.
      cout << "# ERROR in createInstanceForSkeleton" << endl;
    }
  } else {
    // Create default formatter
    df = DateFormat::createDateTimeInstance(
        date_style,
        time_style,
        displayLocale);
  }

  if (df == nullptr) {
    cout << "# DATE TIME FORMATTER == nullptr == " << df << endl;
    // Post an error in the return
    return "";
  }

  // JSON data returned.
  json_object *return_json = json_object_new_object();
  json_object_object_add(return_json, "label", label_obj);

  UDate testDateTime;
  // The type of conversion requested

  // Prefer milliseconds as input.
  json_object *input_millis = json_object_object_get(json_in, "input_millis");
  if (input_millis) {
    testDateTime = json_object_get_double(input_millis);
  } else {
    json_object *input_string_obj = json_object_object_get(json_in, "input_string");
    if (input_string_obj) {
      const string input_date_string = json_object_get_string(input_string_obj);
      cout << "# date from input_string: " << input_date_string << endl;

      UnicodeString date_ustring(input_date_string.c_str());

      UnicodeString parse_skeleton = "YYYY-MM-DD HH:mm:ss";

      DateFormat* dparser = DateFormat::createInstanceForSkeleton(parse_skeleton,
                                                                  displayLocale,
                                                                  status);
      testDateTime = dparser->parse(date_ustring, status);
      if (U_FAILURE(status)) {
        cout << "df->parse failure: " << u_errorName(status) << endl;
        // TODO: Return error in the json.
      }
    }
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
    json_object_object_add(return_json,
                           "error",
                           json_object_new_string("Failure in extracting test result"));
  } else {
    json_object_object_add(return_json,
                           "result",
                           json_object_new_string(test_result_string));
  }
  string return_string = json_object_to_json_string(return_json);
  return return_string;
}
