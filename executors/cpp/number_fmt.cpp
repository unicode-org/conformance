/********************************************************************
 * Comments and license as needed
 ************************************

/******
 * testing number format
 */


#include "unicode/dcfmtsym.h"

#include "unicode/utypes.h"
//#include "unicode/appendable.h"
#include "unicode/bytestream.h"
#include "unicode/compactdecimalformat.h"
#include "unicode/currunit.h"
#include "unicode/dcfmtsym.h"
#include "unicode/fieldpos.h"
#include "unicode/fpositer.h"
#include "unicode/measunit.h"
#include "unicode/nounit.h"
#include "unicode/numberformatter.h"
//#include "unicode/parseerr.h"
#include "unicode/plurrule.h"
#include "unicode/ucurr.h"
#include "unicode/stringpiece.h"
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
using icu::number::Notation;
using icu::number::Precision;

using icu::CurrencyUnit;
using icu::MeasureUnit;

using number::impl::UFormattedNumberData;

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

  // Other parts of the input.
  json_object *options_obj = json_object_object_get(json_in, "options");
  json_object *skeleton_obj = json_object_object_get(json_in, "skeleton");
  json_object *pattern_obj = json_object_object_get(json_in, "pattern");

  // The locale for numbers
  json_object *locale_label_obj = json_object_object_get(json_in, "locale");
  string locale_string = "und";
  if (locale_label_obj) {
    locale_string = json_object_get_string(locale_label_obj);
  }
  const Locale displayLocale(locale_string.c_str());

  // Get options
  json_object *notation_obj;
  json_object *unit_obj;
  json_object *unitDisplay_obj;
  json_object *style_obj;
  json_object *currencyDisplay_obj;
  json_object *roundingMode_obj;
  json_object *compactDisplay_obj;
  json_object *currency_obj;

  string notation_string = "";
  string unit_string = "";
  string unitDisplay_string = "";
  string style_string = "";
  string currency_string = "";
  string roundingMode_string = "";
  string compactDisplay_string = "";
  string currencyDisplay_string = "";

  // Defaults for settings.
  MeasureUnit unit_setting= NoUnit::base();
  UNumberUnitWidth unit_width_setting= UNumberUnitWidth::UNUM_UNIT_WIDTH_NARROW;
  Notation notation_setting= Notation::simple();

  char16_t uCurrency[4];
  if (options_obj) {
    notation_obj = json_object_object_get(options_obj, "notation");
    if (notation_obj) {
      notation_string = json_object_get_string(notation_obj);
    }

    // TODO: Initialize notation_setting based on this string.
    unit_obj = json_object_object_get(options_obj, "unit");
    if (unit_obj) {
      unit_string = json_object_get_string(unit_obj);
      if (unit_string == "percent") {
        unit_setting= NoUnit::percent();
      }
    }

    unitDisplay_obj = json_object_object_get(options_obj, "unitDisplay");
    if (unitDisplay_obj) {
      unitDisplay_string = json_object_get_string(unitDisplay_obj);
      if (unitDisplay_string == "narrow") {
        unit_width_setting = UNumberUnitWidth::UNUM_UNIT_WIDTH_NARROW;
      }
      else if (unitDisplay_string == "long") {
        unit_width_setting = UNumberUnitWidth::UNUM_UNIT_WIDTH_FULL_NAME;
      }
    }

    style_obj = json_object_object_get(options_obj, "style");
    if (style_obj) {
      style_string = json_object_get_string(style_obj);
    }

    compactDisplay_obj = json_object_object_get(options_obj, "compactDisplay");
    if (compactDisplay_obj) {
      compactDisplay_string = json_object_get_string(compactDisplay_obj);
      if (compactDisplay_string == "short") {
        notation_setting = Notation::compactShort();
      } else {
        notation_setting = Notation::compactLong();
      }
    }

    currencyDisplay_obj = json_object_object_get(options_obj, "currencyDisplay");
    if (currencyDisplay_obj) {
      currencyDisplay_string = json_object_get_string(currencyDisplay_obj);
      if (currencyDisplay_string == "narrowSymbol") {
        UNumberUnitWidth::UNUM_UNIT_WIDTH_NARROW;
      }
      else if (currencyDisplay_string == "symbol") {
        UNumberUnitWidth::UNUM_UNIT_WIDTH_SHORT;
      }
      else if (currencyDisplay_string == "name") {
        UNumberUnitWidth::UNUM_UNIT_WIDTH_FULL_NAME;
      }
    }

    currency_obj = json_object_object_get(options_obj, "currency");
    if (currency_obj) {
      currency_string = json_object_get_string(currency_obj);
      // Set the unit to a currency value
      unit_setting = CurrencyUnit(icu::StringPiece(currency_string), status);
    }

    roundingMode_obj = json_object_object_get(options_obj, "roundingMode");
    if (roundingMode_obj) {
      roundingMode_string = json_object_get_string(roundingMode_obj);
    }
  }

  // Additional parameters and values
  json_object *input_obj = json_object_object_get(json_in, "input");
  string input_string = json_object_get_string(input_obj);

  // Start using these things

  // JSON for the results
  json_object *return_json = json_object_new_object();
  json_object_object_add(return_json, "label", label_obj);

  string test_result;

  // Get the numeric value
  double input_double = std::stod(input_string);

  LocalizedNumberFormatter nf;
  if (notation_string == "scientific") {
    nf = NumberFormatter::withLocale(displayLocale)
         .notation(Notation::scientific())
         .unit(unit_setting)
         .unitWidth(unit_width_setting);
 }
  else  if (notation_string == "compact") {
    // TODO !!! GENERALIZE
    // Check for style
      nf = NumberFormatter::withLocale(displayLocale)
           .notation(notation_setting)
           .unit(unit_setting)
           .unitWidth(unit_width_setting);
  }
  else if (style_string == "currency") {
    nf = NumberFormatter::withLocale(displayLocale)
         .unit(CurrencyUnit(currency_string, status))
         .unit(unit_setting)
         .unitWidth(unit_width_setting);
  }
  else {
    // Use settings to initialize the formatter
    nf = NumberFormatter::withLocale(displayLocale)
         .notation(notation_setting)
         .unit(unit_setting)
         .unitWidth(unit_width_setting);
  }

  if (U_FAILURE(status)) {
      test_result = error_message.c_str();
      // TODO: report the error in creating the instance
  }

  UnicodeString number_result;
  FormattedNumber fmt_number = nf.formatDouble(input_double, status);
  number_result = fmt_number.toString(status);
  if (U_FAILURE(status)) {
      test_result = error_message.c_str();
      // TODO: report the error
  }

  // Get the resulting value as a string
  char test_result_string[1000] = "";
  int32_t chars_out = number_result.extract(test_result_string, 1000, nullptr, status);
  test_result = test_result_string;

  if (U_FAILURE(status)) {
    // Report a failure
    test_result = error_message.c_str();
    json_object_object_add(return_json,
                           "error", json_object_new_string("langnames extract error"));
  } else {
    // It worked!
    json_object_object_add(return_json,
                           "result",
                           json_object_new_string(test_result.c_str()));
  }


  string return_string = json_object_to_json_string(return_json);
  return return_string;
}
