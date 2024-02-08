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
// TODO: NEEDED? #include "unicode/unumberoptions.h"
#include "unicode/uobject.h"

#include "unicode/unistr.h"
#include "unicode/locid.h"
#include "unicode/uclean.h"

#include "unicode/numfmt.h"
#include "unicode/numberrangeformatter.h"
#include "unicode/numsys.h"

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

using icu::NumberingSystem;

using icu::number::NumberFormatter;
using icu::number::NumberFormatterSettings;
using icu::number::Notation;
using icu::number::Precision;
using icu::number::IntegerWidth;
using icu::number::Scale;

using icu::CurrencyUnit;
using icu::MeasureUnit;

using number::impl::UFormattedNumberData;

using icu::number::LocalizedNumberFormatter;
using icu::number::FormattedNumber;
using icu::number::impl::UFormattedNumberData;
// using icu::number::SimpleNumberFormatter;

const string error_message = "error";

// Get the integer value of a settting
int16_t get_integer_setting(string key_value_string) {
  int16_t return_val = -1;
  size_t colon_pos = key_value_string.find(":");
  if (colon_pos >= 0) {
    string num_string = key_value_string.substr(colon_pos +1);
    return_val = std::stoi(num_string);
  }
  return return_val;
}

// Get the double value of a settting
double get_double_setting(string key_value_string) {
  double return_val = -1.0;
  size_t colon_pos = key_value_string.find(":");
  if (colon_pos >= 0) {
    string num_string = key_value_string.substr(colon_pos +1);
    return_val = std::stod(num_string);
  }
  return return_val;

}

// Get integer width settings
IntegerWidth set_integerWidth(json_object* options_obj) {
  IntegerWidth integerWidth_setting = IntegerWidth::zeroFillTo(1);
  if (!options_obj) {
    return integerWidth_setting;
  }
  string int_width_string;

  json_object* integer_obj_min = json_object_object_get(
      options_obj, "minimumIntegerDigits");
  json_object* integer_obj_max = json_object_object_get(
      options_obj, "maximumIntegerDigits");
  if (integer_obj_min && integer_obj_max) {
    int_width_string = json_object_get_string(integer_obj_min);
    int32_t val_min32 = get_integer_setting(int_width_string);
    int_width_string = json_object_get_string(integer_obj_max);
    int32_t val_max32 = get_integer_setting(int_width_string);
    integerWidth_setting = IntegerWidth::zeroFillTo(val_min32).truncateAt(val_max32);
  }
  else if (integer_obj_min && !integer_obj_max) {
    int_width_string = json_object_get_string(integer_obj_min);
    int32_t val_min32 = get_integer_setting(int_width_string);
    int_width_string = json_object_get_string(integer_obj_min);
    integerWidth_setting = IntegerWidth::zeroFillTo(val_min32);
  }
  else if (!integer_obj_min && integer_obj_max) {
    int_width_string = json_object_get_string(integer_obj_max);
    int32_t val_max32 = get_integer_setting(int_width_string);
    integerWidth_setting = IntegerWidth::zeroFillTo(1).truncateAt(val_max32);
  }
  return integerWidth_setting;
}

// Get fraction and siginfication digits settings
Precision set_precision_digits(json_object* options_obj, Precision previous_setting) {
  Precision precision_setting = previous_setting;
  if (!options_obj) {
    return precision_setting;
  }

  // First, consider fraction digits.
  json_object* precision_obj_max =
      json_object_object_get(options_obj, "maximumFractionDigits");
  json_object* precision_obj_min =
      json_object_object_get(options_obj, "minimumFractionDigits");

  string precision_string;

  int16_t val_max = 0;
  int16_t val_min = 0;
  if (precision_obj_max) {
    val_max = get_integer_setting(
        json_object_get_string(precision_obj_max));
  }
  if (precision_obj_min) {
    val_min = get_integer_setting(
        json_object_get_string(precision_obj_min));
  }
  if (precision_obj_max && precision_obj_min) {
    // Both are set
    precision_setting = Precision::minMaxFraction(val_min, val_max);
  }
  else if (!precision_obj_max && precision_obj_min) {
    precision_setting = Precision::minFraction(val_min);
  } else if (precision_obj_max && ! precision_obj_min) {
    precision_setting = Precision::maxFraction(val_max);
  }

  // Now handle significant digits
  precision_obj_max =
      json_object_object_get(options_obj, "maximumSignificantDigits");
  precision_obj_min =
      json_object_object_get(options_obj, "minimumSignificantDigits");

  if (precision_obj_max) {
    val_max = get_integer_setting(
        json_object_get_string(precision_obj_max));
  }
  if (precision_obj_min) {
    val_min = get_integer_setting(
        json_object_get_string(precision_obj_min));
  }
  if (precision_obj_max && precision_obj_min) {
    // Both are set
    precision_setting = Precision::minMaxSignificantDigits(val_min, val_max);
  }
  else if (!precision_obj_max && precision_obj_min) {
    precision_setting = Precision::minSignificantDigits(val_min);
  } else if (precision_obj_max && !precision_obj_min) {
    precision_setting = Precision::maxSignificantDigits(val_max);
  }

  return precision_setting;
}

UNumberSignDisplay set_sign_display(json_object* options_obj) {
  UNumberSignDisplay signDisplay_setting = UNUM_SIGN_AUTO;

  if (!options_obj) {
    return signDisplay_setting;
  }

  json_object* signDisplay_obj =
      json_object_object_get(options_obj, "signDisplay");
  if (signDisplay_obj) {
    string signDisplay_string = json_object_get_string(signDisplay_obj);

    if (signDisplay_string == "exceptZero") {
      signDisplay_setting = UNUM_SIGN_EXCEPT_ZERO;
    }
    else if (signDisplay_string == "always") {
      signDisplay_setting = UNUM_SIGN_ALWAYS;
    }
    else if (signDisplay_string == "never") {
      signDisplay_setting = UNUM_SIGN_NEVER;
    }
    else if (signDisplay_string == "negative") {
      signDisplay_setting = UNUM_SIGN_NEGATIVE;
    }
    else if (signDisplay_string == "accounting") {
      signDisplay_setting = UNUM_SIGN_ACCOUNTING;
    }
    else if (signDisplay_string == "accounting_exceptZero") {
      signDisplay_setting = UNUM_SIGN_ACCOUNTING_EXCEPT_ZERO;
    }
    else if (signDisplay_string == "accounting_negative") {
      signDisplay_setting = UNUM_SIGN_ACCOUNTING_NEGATIVE;
    }
  }
  return signDisplay_setting;
}

const string test_numfmt(json_object *json_in) {
  UErrorCode status = U_ZERO_ERROR;

  // label information
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

  // Try using the skeleton to create the formatter
  json_object *skelecton_obj = json_object_object_get(json_in, "skeleton");
  UnicodeString unicode_skeleton_string;
  string skeleton_string;
  if (skeleton_obj) {
    skeleton_string = json_object_get_string(skeleton_obj);
    unicode_skeleton_string = skeleton_string.c_str();
  }

  // Get options
  json_object *notation_obj;
  json_object *unit_obj;
  json_object *unitDisplay_obj;
  json_object *style_obj;
  json_object *currencyDisplay_obj;
  json_object *group_obj;
  json_object *precision_obj_min;
  json_object *precision_obj_max;
  json_object *min_integer_digits_obj;
  json_object *max_integer_digits_obj;
  json_object *roundingMode_obj;
  json_object *compactDisplay_obj;
  json_object *currency_obj;
  json_object *signDisplay_obj;

  string notation_string = "";
  string precision_string = "";
  string unit_string = "";
  string unitDisplay_string = "";
  string style_string = "";
  string compactDisplay_string = "";

  // Defaults for settings.
  CurrencyUnit currency_unit_setting = CurrencyUnit();
  IntegerWidth integerWidth_setting = IntegerWidth::zeroFillTo(1);
  MeasureUnit unit_setting = NoUnit::base();
  Notation notation_setting = Notation::simple();
  Precision precision_setting = Precision::integer();  // TODO?  = Precision::unlimited();
  Scale scale_setting = Scale::none();
  UNumberSignDisplay signDisplay_setting = UNUM_SIGN_AUTO;
  UNumberFormatRoundingMode rounding_setting = UNUM_ROUND_HALFEVEN;
  UNumberDecimalSeparatorDisplay separator_setting = UNUM_DECIMAL_SEPARATOR_AUTO;
  UNumberGroupingStrategy grouping_setting = UNUM_GROUPING_AUTO;
  UNumberUnitWidth unit_width_setting =
      UNumberUnitWidth::UNUM_UNIT_WIDTH_NARROW;

  NumberingSystem* numbering_system =
      NumberingSystem::createInstance(displayLocale, status);

  // Check all the options
  if (options_obj) {
    signDisplay_setting = set_sign_display(options_obj);

    notation_obj = json_object_object_get(options_obj, "notation");
    if (notation_obj) {
      notation_string = json_object_get_string(notation_obj);
    }

    // TODO: Initialize setting based on this string.
    unit_obj = json_object_object_get(options_obj, "unit");
    if (unit_obj) {
      unit_string = json_object_get_string(unit_obj);
      if (unit_string == "percent") {
        unit_setting= NoUnit::percent();
      }
      else if (unit_string == "permille") {
        unit_setting= NoUnit::permille();
      }
      else if (unit_string == "furlong") {
        unit_setting= MeasureUnit::getFurlong();
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

    currency_obj = json_object_object_get(options_obj, "currency");
    if (currency_obj) {
      string currency_string = json_object_get_string(currency_obj);
      // Set the unit to a currency value
      unit_setting = CurrencyUnit(icu::StringPiece(currency_string), status);
    }

    // TODO: make a function
    currencyDisplay_obj = json_object_object_get(options_obj, "currencyDisplay");
    if (currencyDisplay_obj) {
      string currencyDisplay_string = json_object_get_string(currencyDisplay_obj);
      unit_width_setting = UNumberUnitWidth::UNUM_UNIT_WIDTH_NARROW;
     if (currencyDisplay_string == "narrowSymbol") {
        unit_width_setting = UNumberUnitWidth::UNUM_UNIT_WIDTH_NARROW;
      }
      else if (currencyDisplay_string == "symbol") {
        unit_width_setting = UNumberUnitWidth::UNUM_UNIT_WIDTH_SHORT;
      }
      else if (currencyDisplay_string == "name") {
        unit_width_setting = UNumberUnitWidth::UNUM_UNIT_WIDTH_FULL_NAME;
      }
    }

    // TODO: Make this a function rather than inline.
    roundingMode_obj = json_object_object_get(options_obj, "roundingMode");
    if (roundingMode_obj) {
      string roundingMode_string = json_object_get_string(roundingMode_obj);
      if (roundingMode_string == "floor") {
        rounding_setting = UNUM_ROUND_FLOOR;
      } else if (roundingMode_string == "ceil") {
        rounding_setting = UNUM_ROUND_CEILING;
      } else if (roundingMode_string == "halfEven") {
        rounding_setting = UNUM_ROUND_HALFEVEN;
      } else if (roundingMode_string == "halfTrunc") {
        rounding_setting = UNUM_ROUND_HALFDOWN;
      } else if (roundingMode_string == "halfExpand") {
        rounding_setting = UNUM_ROUND_HALFUP;
      } else if (roundingMode_string == "trunc") {
        rounding_setting = UNUM_ROUND_DOWN;
      } else if (roundingMode_string == "expand") {
        rounding_setting = UNUM_ROUND_UP;
      }
      // TODO: Finish this
      //  UNUM_ROUND_HALFEVEN , UNUM_FOUND_HALFEVEN = UNUM_ROUND_HALFEVEN , UNUM_ROUND_HALFDOWN = UNUM_ROUND_HALFEVEN + 1 , UNUM_ROUND_HALFUP ,
      //  UNUM_ROUND_UNNECESSARY , UNUM_ROUND_HALF_ODD , UNUM_ROUND_HALF_CEILING , UNUM_ROUND_HALF_FLOOR
    }

    // TODO: make a function
    group_obj = json_object_object_get(options_obj, "useGrouping");
    if (group_obj) {
      string group_string = json_object_get_string(group_obj);
      if (group_string == "false") {
        grouping_setting = UNUM_GROUPING_OFF;
      }
      else if (group_string == "true") {
        grouping_setting = UNUM_GROUPING_AUTO;
      }
      else if (group_string == "on_aligned") {
        grouping_setting = UNUM_GROUPING_ON_ALIGNED;
      }
      // TODO: FINISH - could be OFF, MIN2, AUTO, ON_ALIGNED, THOUSANDS
    }

    // Need to avoid resetting when not options are specifierd.
    precision_setting = set_precision_digits(options_obj, precision_setting);

    // Minimum integer digits
    integerWidth_setting = set_integerWidth(options_obj);

    // Check on scaling the value
    json_object* scale_obj = json_object_object_get(options_obj, "conformanceScale");
    if (scale_obj) {
      string scale_string = json_object_get_string(scale_obj);
      double scale_val = get_double_setting(scale_string);
      scale_setting = Scale::byDouble(scale_val);
    }

    // Other settings...
    // NumberFormatter::with().symbols(DecimalFormatSymbols(Locale("de_CH"), status))

    json_object* numbering_system_obj = json_object_object_get(options_obj,
                                                               "numberingSystem");
    if (numbering_system_obj) {
      string numbering_system_string = json_object_get_string(numbering_system_obj);
      numbering_system = NumberingSystem::createInstanceByName(
          numbering_system_string.c_str(), status);
    }

    // Handling decimal point
    json_object* decimal_always_obj =
        json_object_object_get(options_obj, "conformanceDecimalAlways");
    if (decimal_always_obj) {
      string separator_string = json_object_get_string(
          decimal_always_obj);
      if (separator_string == "true") {
        separator_setting = UNUM_DECIMAL_SEPARATOR_ALWAYS;
      }
    }
  }


  // Additional parameters and values
  json_object *input_obj = json_object_object_get(json_in, "input");
  string input_string = json_object_get_string(input_obj);

  // Start using these things

  // JSON for the results
  json_object *return_json = json_object_new_object();
  json_object_object_add(return_json, "label", label_obj);

  int32_t chars_out;  // Results of extracting characters from Unicode string
  bool no_error = true;
  char test_result_string[1000] = "";

  string test_result;

  // Get the numeric value
  double input_double = std::stod(input_string);

  LocalizedNumberFormatter nf;
  if (notation_string == "scientific") {
    notation_setting = Notation::scientific();
    if (options_obj) {
      json_object* conformanceExponent_obj =
          json_object_object_get(options_obj, "conformanceExponent");
      if (conformanceExponent_obj) {
        // Check for the number of digits and sign
        string confExp_string = json_object_get_string(conformanceExponent_obj);
        // https://unicode-org.github.io/icu-docs/apidoc/released/icu4c/unumberformatter_8h.html#a18092ae1533c9c260f01c9dbf25589c9
        // TODO: Parse to find the number of values and the sign setting
        if (confExp_string == "+ee") {
          notation_setting = Notation::scientific().withMinExponentDigits(2)
                             .withExponentSignDisplay(UNUM_SIGN_ALWAYS);
        }
      }
    }
  }

  if (skeleton_obj) {
    // If present, use the skeleton
    nf = NumberFormatter::forSkeleton(
        unicode_skeleton_string, status).locale(displayLocale);
  }
  else {
  // Use settings to initialize the formatter
  nf = NumberFormatter::withLocale(displayLocale)
       .notation(notation_setting)
       .decimal(separator_setting)
       .precision(precision_setting)
       .integerWidth(integerWidth_setting)
       .grouping(grouping_setting)
       .adoptSymbols(numbering_system)
       .roundingMode(rounding_setting)
       .scale(scale_setting)
       .sign(signDisplay_setting)
       .unit(unit_setting)
       .unitWidth(unit_width_setting);
  }

  if (U_FAILURE(status)) {
      test_result = error_message.c_str();
      const char* error_name = u_errorName(status);
      json_object_object_add(return_json,
                           "error", json_object_new_string("error in constructor"));
      json_object_object_add(return_json,
                             "error_detail", json_object_new_string(error_name));
      no_error = false;
  }

  if (no_error) {
    UnicodeString number_result;
    // Use formatDecimal, passing the string instead of a double.
    FormattedNumber fmt_number = nf.formatDecimal(input_string, status);
    number_result = fmt_number.toString(status);
    if (U_FAILURE(status)) {
      const char* error_name = u_errorName(status);
      json_object_object_add(return_json,
                           "error", json_object_new_string("error in toString"));
      json_object_object_add(return_json,
                             "error_detail", json_object_new_string(error_name));
      no_error = false;
    }

    // Get the resulting value as a string
    chars_out = number_result.extract(test_result_string, 1000, nullptr, status);
    test_result = test_result_string;

    if (U_FAILURE(status)) {
      // Report a failure
      const char* error_name = u_errorName(status);
      json_object_object_add(
          return_json, "error", json_object_new_string("error in string extract"));
      json_object_object_add(
          return_json, "error_detail", json_object_new_string(error_name));
      no_error = false;
    } else {
      // It worked!
      json_object_object_add(return_json,
                             "result",
                             json_object_new_string(test_result.c_str()));
    }
  }
  // To see what was actually used.
  UnicodeString u_skeleton_out = nf.toSkeleton(status);
  chars_out = u_skeleton_out.extract(test_result_string, 1000, nullptr, status);
  json_object_object_add(return_json,
                         "actual_skeleton",
                         json_object_new_string(test_result_string));

  string return_string = json_object_to_json_string(return_json);
  return return_string;
}
