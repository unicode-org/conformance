/*
 * Executor provides tests for DisplayNames.
 */

use serde_json::{json, Value};
use std::io::{self, Write};

use core::cmp::Ordering;
use icu::displaynames::*;

use icu::locid::{locale, Locale};
use icu_provider::DataLocale;

// Function runs comparison using displaynames
pub fn run_coll_test(json_obj: &Value) {
    let label = &json_obj["label"].as_str().unwrap();
    let options = &json_obj["options"].as_str().unwrap();
    let input = &json_obj["input"].as_str().unwrap();

    // Default locale if not specified.
    let langid = if json_obj.get("locale") != None {
        let locale_name = &json_obj["locale"].as_str().unwrap();
        Locale::from_str(&locale_name).unwrap()
    } else {
        locale!("und")
    };
    let data_locale = DataLocale::from(langid);

    let data_provider = icu_testdata::unstable();

    let mut options = DisplayNamesOptions::new();

    let displaynames: DisplayNames =
        DisplayNames::try_new_unstable(&data_provider, data_locale, options).unwrap();

    let result = displaynames.of(input);

    let json_result = json!({
        "label": label,
        "result": result_string});
    println!("{}", json_result);
    io::stdout().flush().unwrap();
}
