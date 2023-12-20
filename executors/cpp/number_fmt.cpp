/********************************************************************
 * Comments and license as needed
 ************************************

/******
 * testing number format
 */


#include "unicode/dcfmtsym.h"

#include "unicode/utypes.h"
#include "unicode/appendable.h"
#include "unicode/bytestream.h"
#include "unicode/currunit.h"
#include "unicode/dcfmtsym.h"
#include "unicode/displayoptions.h"
#include "unicode/fieldpos.h"
#include "unicode/fpositer.h"
#include "unicode/measunit.h"
#include "unicode/nounit.h"
#include "unicode/numberformatter.h"
#include "unicode/parseerr.h"
#include "unicode/plurrule.h"
#include "unicode/ucurr.h"
#include "unicode/unum.h"
#include "unicode/unumberformatter.h"
#include "unicode/uobject.h"

#include "unicode/unistr.h"
#include "unicode/locid.h"
#include "unicode/uclean.h"

#include "unicode/numfmt.h"
#include "unicode/numberrangeformatter.h"

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

using icu::number::NumberFormatter;
using icu::number::LocalizedNumberFormatter;
using icu::number::FormattedNumber;
using icu::number::impl::UFormattedNumberData;
// using icu::number::SimpleNumberFormatter;

const string error_message = "error";

const string test_numfmt(json_object *json_in) {
  UErrorCode status = U_ZERO_ERROR;

  // Locale information
  json_object *label_obj = json_object_object_get(json_in, "label");
  string label_string = json_object_get_string(label_obj);


  // The locale for numbers
  json_object *locale_label_obj = json_object_object_get(json_in, "locale");
  string locale_string = "und";
  if (locale_label_obj) {
    locale_string = json_object_get_string(locale_label_obj);
  }
  Locale displayLocale(locale_string.c_str());

  std:: cout<< "Locale = " << locale_string << std::endl;

  // Additional parameters and values
  json_object *input_obj = json_object_object_get(json_in, "input");
  string input_string = json_object_get_string(input_obj);
  json_object *options_obj = json_object_object_get(json_in, "options");
  json_object *rounding_mode_obj = json_object_object_get(json_in, "roundingMode");
  json_object *skeleton_obj = json_object_object_get(json_in, "skeleton");
  json_object *pattern_obj = json_object_object_get(json_in, "pattern");

  // Start using these things

  // JSON for the results
  json_object *return_json = json_object_new_object();
  json_object_object_add(return_json, "label", label_obj);

  string test_result;

  // Get the numeric value
  double input_double = std::stod(input_string);
  std:: cout<< "num_double = " << input_double << std::endl;

  // TEMPORARY - just return the input.
  test_result = input_string;

  // TODO!!!
  //  SimpleNumberFormatter snf = SimpleNumberFormatter::forLocale(displayLocale, status);

  LocalizedNumberFormatter nf = LocalizedNumberFormatter();  // (displayLocale);

  FormattedNumber fnum = nf.formatDouble(input_double, status);
  if (U_FAILURE(status)) {
      test_result = error_message.c_str();
  }

  // Get the resulting value as a string
  UnicodeString number_result =  fnum.toString(status);
  char test_result_string[1000] = "";
  int32_t chars_out = number_result.extract(test_result_string, 1000, nullptr, status);
  test_result = test_result_string;

  if (U_FAILURE(status)) {
      test_result = error_message.c_str();
  }

  if (U_FAILURE(status)) {
    json_object_object_add(return_json,
                           "error", json_object_new_string("langnames extract error"));
  } else {
    json_object_object_add(return_json,
                           "result",
                           json_object_new_string(test_result.c_str()));
  }


  string return_string = json_object_to_json_string(return_json);
  return return_string;
}
