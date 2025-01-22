/*
 * Common functions for dealing with JSON data in conformance testing
 */


#include <json-c/json.h>

#include <unicode/utypes.h>

#include <string>
#include <cstring>

#include "./util.h"

using std::string;

/* Checks if the result is an error. If not, return false.
   If there's an error, add an error field and the given message
   to the return_json object and return true.
*/
auto check_icu_error(UErrorCode error_code,
                           json_object *return_json,
                           string message_to_add_if_error) -> const bool {
  bool is_error = false;

  if (U_FAILURE(error_code) == 0) {
    return is_error;
  }

  is_error = true;

  const char* error_name = u_errorName(error_code);
  json_object_object_add(
      return_json,
      "error", json_object_new_string(message_to_add_if_error.c_str()));
  json_object_object_add(
      return_json,
      "error_detail", json_object_new_string(error_name));

  return is_error;
}
