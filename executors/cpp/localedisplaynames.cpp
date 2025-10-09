/********************************************************************
 * testing icu4c for locale display names
 */

#include <json-c/json.h>

#include <unicode/utypes.h>

#include <unicode/locdspnm.h>
#include <unicode/uldnames.h>
#include <unicode/unistr.h>

#include <string>
#include <cstring>

#include "./util.h"

using icu::Locale;
using icu::UnicodeString;
using icu::LocaleDisplayNames;

auto TestLocaleDisplayNames (json_object *json_in) -> string {
  UErrorCode status = U_ZERO_ERROR;

  json_object *label_obj = json_object_object_get(json_in, "label");
  string label_string = json_object_get_string(label_obj);

  // The locale in which the name is given.
  json_object *locale_label_obj =
      json_object_object_get(json_in, "locale_label");
  string locale_string = json_object_get_string(locale_label_obj);

  // The locales's name to be displayed.
  json_object *displayed_locale_label_obj = json_object_object_get(
      json_in, "language_label");
  string displayed_locale_label_string =
      json_object_get_string(displayed_locale_label_obj);

  // Either standard or dialect names for the locale.
  string language_display_string = "standard";
  json_object *language_display_obj = json_object_object_get(
      json_in, "languageDisplay");
  if (language_display_obj != nullptr) {
    language_display_string = json_object_get_string(language_display_obj);
  }

  // In what language to show the locale name
  Locale displayLocale(locale_string.c_str());

  // The id of the locale to be formatted.
  Locale testLocale(displayed_locale_label_string.c_str());

  // Create display names object with the kind of locale name.
  // Default is "standard".
  UDialectHandling display_handling = ULDN_STANDARD_NAMES;
  if (language_display_string == "dialect") {
    display_handling = ULDN_DIALECT_NAMES;
  }

  LocaleDisplayNames* ldn =
      LocaleDisplayNames::createInstance(displayLocale, display_handling);

  // Get the resulting string for this testLocale
  UnicodeString locale_name_result;
  ldn->localeDisplayName(testLocale, locale_name_result);
  delete ldn;

  string result_string;
  locale_name_result.toUTF8String(result_string);

  // Create the output with label and resulting locale name.
  json_object *return_json = json_object_new_object();
  json_object_object_add(return_json, "label", label_obj);


  json_object_object_add(return_json,
                         "result",
                         json_object_new_string(result_string.c_str()));

  string return_string = json_object_to_json_string(return_json);
  return return_string;
}
