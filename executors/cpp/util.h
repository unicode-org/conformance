/*
 *  Check for ICU errors and add to output if needed.
 */

#include <json-c/json.h>

#include <string>

using std::string;

extern auto check_icu_error(UErrorCode error_code,
                                  json_object *return_json,
                                  string message_to_add_if_error) -> const bool;

