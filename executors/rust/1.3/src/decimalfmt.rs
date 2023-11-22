//! Executor provides tests for DecimalFormat and NumberFormat.

use serde_json::{json, Value};

use icu::decimal::options;
use icu::decimal::FixedDecimalFormatter;

use fixed_decimal::FixedDecimal;

use icu::locid::locale;

// Runs decimal and number formatting given patterns or skeletons.
pub fn run_numberformat_test(json_obj: &Value) {
    let provider = icu_testdata::get_provider();

    let label = &json_obj["label"].as_str().unwrap();

    // Default locale if not specified.
    let mut langid = locale!("und");
    if json_obj.get("locale") != None {
        let locale_name = &json_obj["locale"].as_str().unwrap();
        langid = icu::locid:Locale::from_str(&locale_name);
    }

    let input = &json_obj["input"].as_str().unwrap();

    let mut options: options::FixedDecimalFormatterOptions = Default::default();
    // TODO: populate option from input json_obj.
    // !! A test. More options to consider!
    options.grouping_strategy = options::GroupingStrategy::Min2;

    let fdf = FixedDecimalFormatter::try_new_with_buffer_provider(
        &provider, &langid.into(), options)
        .expect("Data should load successfully");

    // Check if the conversion from the string input is OK.
    let input_num: FixedDecimal = input.parse().expect("valid input format");
    let result_string = fdf.format_to_string(&input_num);

    // Result to stdout.
    let json_result = json!({
        "label": label,
        "result": result_string});
    print!("{}", json_result);
}


