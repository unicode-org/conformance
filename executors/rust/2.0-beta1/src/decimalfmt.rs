//! Executor provides tests for DecimalFormat and NumberFormat.

use serde_json::{json, Value};

use icu::decimal::options;
use icu::decimal::FixedDecimalFormatter;

use icu::locale::Locale;

// Runs decimal and number formatting given patterns or skeletons.
pub fn _todo(json_obj: &Value) -> Result<Value, String> {
    let label = &json_obj["label"].as_str().unwrap();

    // Default locale if not specified.
    let langid: Locale = json_obj
        .get("locale")
        .map(|locale_name| locale_name.as_str().unwrap().parse().unwrap())
        .unwrap_or_default();

    let input = &json_obj["input"].as_str().unwrap();

    let mut options: options::FixedDecimalFormatterOptions = Default::default();
    // TODO: populate option from input json_obj.
    // !! A test. More options to consider!
    options.grouping_strategy = options::GroupingStrategy::Min2;

    let fdf = FixedDecimalFormatter::try_new(langid.into(), options)
        .expect("Data should load successfully");

    // Check if the conversion from the string input is OK.
    let input_num = input.parse().expect("valid input format");
    let result_string = fdf.format_to_string(&input_num);

    Ok(json!({
        "label": label,
        "result": result_string
    }))
}
