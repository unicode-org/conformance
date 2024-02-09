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

using std::cout;
using std::endl;
using std::string;


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

  json_object *date_skeleton_obj = json_object_object_get(json_in, "datetime_skeleton");
  if (date_skeleton_obj) {
    // Data specifies a date time skeleton. Make a formatter based on this.
    string skeleton_string = json_object_get_string(date_skeleton_obj);

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
        icu::DateFormat::EStyle::kDefault,
        icu::DateFormat::EStyle::kDefault,
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

  // Get the input data as a date object.

  // Types of input:
  //   "input_millis" milliseconds since base date/time
  //   "input_string" parsable string such as "2020-03-02 10:15:17 -08:00"
  //   OTHER?

  UDate testDateTime;
  // The type of conversion requested
  json_object *input_millis = json_object_object_get(json_in, "input_millis");
  if (input_millis) {
    testDateTime = json_object_get_double(input_millis);
  }


  json_object *input_string_obj = json_object_object_get(json_in, "input_string");
  if (input_string_obj) {
    const string input_date_string = json_object_get_string(input_string_obj);
    cout << "# date from input_string: " << input_date_string << endl;

    UnicodeString date_ustring(input_date_string.c_str());

    cout << "# Calling parse" << endl;
    testDateTime = df->parse(date_ustring, status);
    if (U_FAILURE(status)) {
      // TODO: Return error.
      cout << "df->parse failure" << endl;
    }
    cout << "Called parse" << endl;
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
  }

  json_object_object_add(return_json,
                         "result",
                         json_object_new_string(test_result_string));

  string return_string = json_object_to_json_string(return_json);
  return return_string;
}
