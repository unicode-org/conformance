/*
 * Executor provides tests for NumberFormat and DecimalFormat.
 */

use serde_json::{json, Value};
use writeable::Writeable;

use icu::decimal::options;
use icu::decimal::FixedDecimalFormatter;

use fixed_decimal::FixedDecimal;

use icu::locid::{locale, Locale};
use icu_provider::DataLocale;

use std::panic;
use std::str::FromStr;

// Support options - update when ICU4X adds support
static SUPPORTED_OPTIONS: &[&str] =
    &["minimumIntegerDigits", "maximumIntegerDigits",
      "minimumFractionDigits", "maximumFractionDigits",
      "RoundingMode"];

// Runs decimal and number formatting given patterns or skeletons.
pub fn run_numberformat_test(json_obj: &Value) -> Result<Value, String> {
    let provider = icu_testdata::unstable();

    // TODO: Handle errors of missing JSON fields
    let label = &json_obj["label"].as_str().unwrap();

    // Default locale if not specified.
    let langid = if json_obj.get("locale") != None {
        let locale_name = &json_obj["locale"].as_str().unwrap();
        Locale::from_str(locale_name).unwrap()
    } else {
        locale!("und")
    };
    let data_locale = DataLocale::from(langid);

    let input = &json_obj["input"].as_str().unwrap();

    // TODO: Get the options from JSON. If there are unsupported values, return
    // "unsupported" rather than an error.
    let options = &json_obj["options"];  // This will be an array.

    let mut unsupported_options : Vec<&str>;
    // If any option is not yet supported, 
    for (option, setting) in options.as_object().unwrap()  {
        if ! SUPPORTED_OPTIONS.contains&(&option.to_string()) {
            unsupported_options.append(option.to_string());
        }
    }
    if unsupported_options.len() > 0 {
        let json_result = json!({
            "label": label,
            "unsupported": label,
            "unsupported_options": unsupported_options
        });
        return Ok(json_result);
    }

    let mut options: options::FixedDecimalFormatterOptions = Default::default();
    // TODO: Use options to call operations including pad and trunc with rounding.

    // Iterator over options, applying the 
    
    // !! A test. More options to consider!
    options.grouping_strategy = options::GroupingStrategy::Min2;

    // Can this fail with invalid options?
    let fdf = FixedDecimalFormatter::try_new_unstable(&provider, &data_locale, options)
        .expect("Data should load successfully");

    // Returns error if parsing the number string fails.
    let input_num = input.parse::<FixedDecimal>().map_err(|e| e.to_string())?;
    // TODO: Can this fail?
    let result_string = fdf.format(&input_num);

    // Result to stdout.
    let json_result = json!({
        "label": label,
        "result": result_string.write_to_string()});
    Ok(json_result)
}
