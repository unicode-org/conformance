/*
 * Provides tests for likely subtags to mimimize and maximize.
 */

use serde_json::{json, Value};

use icu::locid::Locale;
use icu::locid_transform::LocaleExpander;

use std::str::FromStr;

// https://docs.rs/icu_locid_transform/latest/icu_locid_transform/

// Function runs language names tests
pub fn run_likelysubtags_test(json_obj: &Value) -> Result<Value, String> {
    let lc = LocaleExpander::new();

    let label = &json_obj["label"].as_str().unwrap();

    let test_option = &json_obj["option"].as_str().unwrap();

    let locale_str: &str = json_obj["locale"].as_str().unwrap();

    let mut locale = Locale::from_str(locale_str).unwrap();

    if test_option == &"minimize" {
        lc.minimize(&mut locale);
    } else if test_option == &"maximize" {
        lc.maximize(&mut locale);
    }

    let json_result = json!({
        "label": label,
        "result": locale.to_string()
    });

    Ok(json_result)
}
