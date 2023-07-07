/*
 * Executor provides tests for NumberFormat and DecimalFormat.
 */

use serde_json::{json, Value};
use writeable::Writeable;

use icu::decimal::options;
use icu::decimal::FixedDecimalFormatter;

use fixed_decimal::FixedDecimal;

use icu_compactdecimal::CompactDecimalFormatter;

use icu::locid::{locale, Locale};
use icu_provider::DataLocale;


use std::panic;
use std::str::FromStr;

// Support options - update when ICU4X adds support
static SUPPORTED_OPTIONS: [&str; 5] = [
    "minimumIntegerDigits",
    "maximumIntegerDigits",
    "minimumFractionDigits",
    "maximumFractionDigits",
    "RoundingMode",
];

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
    let options = &json_obj["options"]; // This will be an array.

    let mut unsupported_options: Vec<&str> = Vec::new();
    // If any option is not yet supported,
    let mut is_compact = false;
    let mut compact_type = "";
    for (option, setting) in options.as_object().unwrap() {
        let option_string = option.as_str();
        let setting_string = setting.as_str().unwrap();
        if option_string == "notation" && setting_string == "compact" {
            is_compact = true;
        } else if option_string == "compactDisplay" {
            compact_type = setting_string;
        }
        if !SUPPORTED_OPTIONS.contains(&option_string) {
            unsupported_options.push(&option);
        }
    }

    // Check if we can get anything to work!
    // if unsupported_options.len() > 0 {
    //     let json_result = json!({
    //         "label": label,
    //         "unsupported": label,
    //         "unsupported_options": unsupported_options
    //     });
    //     return Ok(json_result);
    // }

    let mut options: options::FixedDecimalFormatterOptions = Default::default();
    // TODO: Use options to call operations including pad and trunc with rounding.

    // Iterator over options, applying the

    // !! A test. More options to consider!
    options.grouping_strategy = options::GroupingStrategy::Min2;

    // Returns error if parsing the number string fails.
    let input_num = input.parse::<FixedDecimal>().map_err(|e| e.to_string())?;

    let mut result_string = if is_compact {
        let input_num = input.parse::<i64>().map_err(|e| e.to_string())?;
        // We saw compact!
        let cdf = if compact_type == "short" {
            CompactDecimalFormatter::try_new_short_unstable(
                &provider,
                &data_locale,
                Default::default(),
            ).unwrap()  // ??  options);
        } else {
            CompactDecimalFormatter::try_new_long_unstable(
                &provider,
                &data_locale,
                Default::default(),
            ).unwrap()  // ??  options);
        }
        cdf.format_i64(input_num)
    }
    else {
        let input_num = input.parse::<FixedDecimal>().map_err(|e| e.to_string())?;
        // Can this fail with invalid options?
        let fdf = FixedDecimalFormatter::try_new_unstable(&provider, &data_locale, options)
            .expect("Data should load successfully");
        fdf.format(&input_num)
    };

    // Result to stdout.
    let json_result = json!({
        "label": label,
        "result": result_string.write_to_string()});
    Ok(json_result)
}
