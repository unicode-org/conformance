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
static _SUPPORTED_OPTIONS: [&str; 6] = [
    "compactDisplay",
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
    let langid = if json_obj.get("locale").is_some() {
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
    for (option, _setting) in options.as_object().unwrap() {
        if !SUPPORTED_OPTIONS.contains(&option.as_str()) {
            unsupported_options.push(&option);
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
    let result_string = if is_compact {
        // We saw compact!
        let cdf = if compact_type == "short" {
            CompactDecimalFormatter::try_new_short_unstable(
                &provider,
                &data_locale,
                Default::default(),
            )
            .unwrap()
        } else {
            println!("#{:?}", "   LONG");
            CompactDecimalFormatter::try_new_long_unstable(
                &provider,
                &data_locale,
                Default::default(),
            )
            .unwrap()
        };
        // input.parse().map_err(|e| e.to_string())?;
        let input_num = CompactDecimal::from_str(input).map_err(|e| e.to_string())?;
        let formatted_cdf = cdf.format_compact_decimal(&input_num);
        formatted_cdf
            .map_err(|e| e.to_string())?
            .write_to_string()
            .into_owned()
    // }
    // else if is_scientific {
    //     let mut sci_decimal = input.parse::<ScientificDecimal>().map_err(|e| e.to_string());
    //     // TEMPORARY
    } else {
        // FixedDecimal
        // Can this fail with invalid options?
        let fdf = FixedDecimalFormatter::try_new_unstable(&provider, &data_locale, options.clone())
            .expect("Data should load successfully");

        let mut input_num = input.parse::<FixedDecimal>().map_err(|e| e.to_string())?;
        // Apply relevant options for digits.
        if let Some(x) = option_struct.minimum_fraction_digits {
            input_num.pad_end(-(x as i16));
        }
        if let Some(x) = option_struct.maximum_fraction_digits {
            input_num.half_even(-(x as i16));
        }
        if let Some(x) = option_struct.maximum_integer_digits {
            input_num.set_max_position(x as i16);
            input_num.trim_start();
        }
        if let Some(x) = option_struct.minimum_integer_digits {
            input_num.pad_start(x as i16);
        }

        // Apply the options and get formatted string.
        fdf.format(&input_num).write_to_string().into_owned()
    };

    // Result to stdout.
    let json_result = json!({
        "label": label,
        "result": result_string.write_to_string()});
    Ok(json_result)
}
