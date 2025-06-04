/******
 * testing segmenter / break iterator for locales
 */

#include <json-c/json.h>
#include <json-c/arraylist.h>

#include <unicode/brkiter.h>
#include <unicode/bytestream.h>
#include <unicode/locid.h>
#include <unicode/uclean.h>
#include <unicode/unistr.h>
#include <unicode/utypes.h>


#include <cstdio>
#include <cstdlib>

#include <cstring>
#include <iostream>
#include <string>

using std::string;

using icu::BreakIterator;
using icu::Locale;
using icu::StringByteSink;
using icu::UnicodeString;

void free_string(void* data) {
  if (data) {
    free(data);
  }
}

auto TestSegmenter(json_object *json_in) -> string {
  UErrorCode status = U_ZERO_ERROR;

  json_object *label_obj = json_object_object_get(json_in, "label");
  string label_string = json_object_get_string(label_obj);

  // The locale in which the name is given.
  json_object *locale_label_obj = json_object_object_get(json_in, "locale");
  string locale_string = json_object_get_string(locale_label_obj);
  Locale locale(locale_string.c_str());


  // What we are segmenting...
  json_object *input_obj = json_object_object_get(json_in, "input");
  string input = json_object_get_string(input_obj);

  UnicodeString u_input = UnicodeString::fromUTF8(input);

  // The type of conversion requested
  json_object *options_obj = json_object_object_get(json_in, "options");

  json_object *granularity_obj = json_object_object_get(options_obj, "granularity");
  string granularity_value = json_object_get_string(granularity_obj);

  // Create output array to store results
  struct json_object* test_result = json_object_new_array();

  json_object *return_json = json_object_new_object();
  json_object_object_add(return_json, "label", label_obj);

  // The default.
  BreakIterator* brk_iterator;

  if (granularity_value == "grapheme_cluster" ||
      granularity_value == "grapheme") {
    brk_iterator = BreakIterator::createCharacterInstance(locale, status);
  } else if (granularity_value == "word") {
    brk_iterator = BreakIterator::createWordInstance(locale, status);
  } else if (granularity_value == "sentence") {
    brk_iterator = BreakIterator::createSentenceInstance(locale, status);
  } else if (granularity_value == "line") {
    brk_iterator = BreakIterator::createLineInstance(locale, status);
  } else {
    // No such granularity
    json_object_object_add(
        return_json,
        "error",
        json_object_new_string("Unknown granularity"));
    json_object_object_add(
        return_json,
        "error_detail",
        json_object_new_string(granularity_value.c_str()));
    return  json_object_to_json_string(return_json);
  }

  // Check if there's an error in the creation of the iterator.
  if (U_FAILURE(status) != 0) {
    // An error in the call.
    json_object_object_add(
        return_json,
        "error",
        json_object_new_string("Failure to create break iterator "));
    json_object_object_add(
        return_json,
        "error_detail",
        json_object_new_string(granularity_value.c_str()));
    return  json_object_to_json_string(return_json);
  }

  // We must have an interator
  brk_iterator->setText(u_input);

  int32_t start_pos = brk_iterator->first();
  int32_t end_pos = brk_iterator->next();

  // Loop until we get DONE or an error.
  while (end_pos != BreakIterator::DONE) {
    // Extract the Unicode string, converting to a c string.
    UnicodeString u_target;
    u_input.extractBetween(start_pos, end_pos, u_target);
    string target;
    u_target.toUTF8String(target);
    json_object* j_target = json_object_new_string(target.c_str());
    json_object_array_add(test_result, j_target);
    start_pos = end_pos;
    end_pos = brk_iterator->next();
  }

  // For each, extract the current part of the input string, adding to the output
  json_object_object_add(return_json, "result", test_result);

  return  json_object_to_json_string(return_json);
}
