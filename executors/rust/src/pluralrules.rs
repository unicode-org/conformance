#[cfg(not(any(ver = "1.3", ver = "1.4", ver = "1.5", ver = "2.0-beta1")))]
use fixed_decimal::Decimal;
#[cfg(any(ver = "1.3", ver = "1.4", ver = "1.5", ver = "2.0-beta1"))]
use fixed_decimal::FixedDecimal as Decimal;

use serde_json::{json, Value};
use std::str::FromStr;

use super::compat::{pref, Locale};

// https://docs.rs/icu/latest/icu/plurals/index.html
use icu::plurals::{PluralCategory, PluralRuleType, PluralRules};

// Function runs plural rules
pub fn run_plural_rules_test(json_obj: &Value) -> Result<Value, String> {
    let label = &json_obj["label"].as_str().unwrap();

    let locale_str: &str = json_obj["locale"].as_str().unwrap();

    let locale = if let Ok(lc) = locale_str.parse::<Locale>() {
        lc
    } else {
        return Ok(json!({
            "label": label,
            "error_detail": {"option": locale_str},
            "error_type": "locale problem",
        }));
    };

    // Get number string
    let input_number = &json_obj["sample"].as_str().unwrap();

    // Returns error if parsing the number string fails.
    let test_number = if let Ok(fd) = Decimal::from_str(input_number) {
        fd
    } else {
        // Report an unexpected result.
        return Ok(json!({
            "label": label,
            "error_detail": {"sample number": input_number},
            "error_type": "parsing sample",
            "unsupported": "input number"
        }));
    };

    // Get type string: either ordinal or cardinal
    let plural_type_string: &str = json_obj["type"].as_str().unwrap();

    // Get PluralRuleTypecardinal / ordinal
    let plural_type = if plural_type_string == "cardinal" {
        PluralRuleType::Cardinal
    } else {
        PluralRuleType::Ordinal
    };

    let pr =
        PluralRules::try_new(pref!(locale), plural_type.into()).expect("locale should be present");

    // Get the category and convert to a string.
    let category = pr.category_for(&test_number);

    let category_string = if category == PluralCategory::Zero {
        "zero"
    } else if category == PluralCategory::One {
        "one"
    } else if category == PluralCategory::Two {
        "two"
    } else if category == PluralCategory::Few {
        "few"
    } else if category == PluralCategory::Many {
        "many"
    } else if category == PluralCategory::Other {
        "other"
    } else {
        // Report an unexpected result.
        return Ok(json!({
            "label": label,
            "error_detail": {"option": "unknown category returned"},
            "error_type": "unsupported",
            "unsupported": "unknown plural result"
        }));
    };

    let json_result = json!({
        "label": label,
        "result": category_string
    });

    // Return the string
    Ok(json_result)
}
