//! Executor provides tests for list formatting in locale-sensitive manner.

use serde::{Deserialize, Serialize};
use serde_json::{json, Value};

use icu::list::*;
use icu::locid::Locale;

use writeable::Writeable;

#[derive(Deserialize, Serialize, Debug)]
#[serde(rename_all = "snake_case")]
struct ListFormatOptions {
    style: Option<String>,
    list_type: Option<String>,
}

// Function runs list format tests
pub fn run_list_fmt_test(json_obj: &Value) -> Result<Value, String> {
    let label = &json_obj["label"].as_str().unwrap();

    let locale_str: &str = json_obj["locale"].as_str().unwrap();
    let locale = locale_str.parse::<Locale>().unwrap();

    let options = &json_obj["options"]; // This will be an array.
    let option_struct: ListFormatOptions = serde_json::from_str(&options.to_string()).unwrap();

    let style: &str = option_struct.style.as_ref().unwrap();
    let list_type: &str = option_struct.list_type.as_ref().unwrap();

    // get input list

    // Style
    let list_style: ListLength = if style == "long" {
        ListLength::Wide
    } else if style == "short" {
        ListLength::Short
    } else if style == "narrow" {
        ListLength::Narrow
    } else {
        // Report an unsupported option.
        return Ok(json!({
            "label": label,
            "error_detail": {"option": style},
            "unsupported": "unknown list style",
            "error_type": "unsupported",
        }));
    };

    let list_formatter_result: Result<ListFormatter, ListError> = if list_type == "conjunction" {
        // Reference: https://docs.rs/icu/latest/icu/list/index.html
        ListFormatter::try_new_and_with_length(&locale.into(), list_style)
    } else if list_type == "disjunction" {
        ListFormatter::try_new_or_with_length(&locale.into(), list_style)
    } else if list_type == "unit" {
        ListFormatter::try_new_unit_with_length(&locale.into(), list_style)
    } else {
        // This option is not  supported.
        return Ok(json!({
            "label": label,
            "error_detail": {"option": list_type},
            "unsupported": "unknown format type",
            "error_type": "unsupported",
        }));
    };

    // Data to be formatted.
    let input_list = json_obj["input_list"].as_array().unwrap();
    let input_list_str_iter = input_list
        .iter()
        .map(|json_value| json_value.as_str().unwrap());

    let json_result = match list_formatter_result {
        Ok(formatter) => {
            json!({
                "label": label,
                "result":  formatter.format(
                    input_list_str_iter).write_to_string().into_owned()
            })
        }
        Err(e) => {
            json!({
                "label": label,
                "locale_label": locale_str,
                "error": e.to_string(),
                "error_type": "unsupported",
                "unsupported": e.to_string(),
                "error_detail": {"unsupported_locale": locale_str}
            })
        }
    };

    Ok(json_result)
}
