//! Executor provides tests for Collator.

use serde_json::{json, Value};

use core::cmp::Ordering;
use icu::collator::*;

#[cfg(not(any(ver = "1.3", ver = "1.4", ver = "1.5", ver = "2.0-beta1")))]
use icu::collator::options::*;

use super::compat::{locale, pref};

// Function runs comparison using collator
pub fn run_collation_test(json_obj: &Value) -> Result<Value, String> {
    // TODO: Handle errors of missing values and failures.
    let label = &json_obj["label"].as_str().unwrap();
    let ignore_punctuation: &Option<bool> = &json_obj["ignorePunctuation"].as_bool();
    let str1: &str = json_obj["s1"].as_str().unwrap();
    let str2: &str = json_obj["s2"].as_str().unwrap();

    // This may be missing
    let compare_option: Option<&str> = json_obj["compare_type"].as_str();

    let strength_option: Option<&str> = json_obj["strength"].as_str();

    let rules: Option<&str> = json_obj["rules"].as_str();

    #[cfg(any(ver = "1.3", ver = "1.4", ver = "1.5"))]
    let mut options = CollatorOptions::new();
    #[cfg(not(any(ver = "1.3", ver = "1.4", ver = "1.5")))]
    let mut options = CollatorOptions::default();

    // Handle the given options

    // Rules not yet supported.
    if rules.is_some() {
        return Ok(json!({
            "label": label,
            "error_detail": "Rules not supported",
            "unsupported": "Collator rules not available",
            "error_type": "unsupported",
        }));
    }

    // Use compare_type to get < or =.
    let mut compare_symbol = "<"; // Default
    if let Some(comparison) = compare_option {
        compare_symbol = &comparison[0..1];
    }

    if let Some(strength) = strength_option {
        options.strength = if strength == "primary" {
            Some(Strength::Tertiary)
        } else if strength == "secondary" {
            Some(Strength::Secondary)
        } else if strength == "tertiary" {
            Some(Strength::Tertiary)
        } else if strength == "quaternary" {
            Some(Strength::Quaternary)
        } else if strength == "identical" {
            Some(Strength::Identical)
        } else {
            return Ok(json!({
                "label": label,
                "error_detail": {"strength": strength},
                "unsupported": "strength",
                "error_type": "unsupported",
            }));
        };
    };

    // Ignore punctuation only if using shifted test.
    if let Some(ip) = ignore_punctuation {
        if *ip {
            options.alternate_handling = Some(AlternateHandling::Shifted);
        }
    }

    // TODO !! Iterate to find actual level of comparison, then look
    // at compare type (1, 2, 3, 4, i, c) to see if it matches

    let collator = Collator::try_new(pref!(locale!("en")), options).unwrap();

    let comparison = collator.compare(str1, str2);

    let result_string = if compare_symbol == "<" {
        comparison.is_le()
    } else if compare_symbol == "=" {
        comparison.is_eq()
    } else {
        return Ok(json!({
            "label": label,
            "error_detail": {
                "compare_type": compare_symbol,
            },
            "unsupported": "compare_symbol",
            "error_type": "unsupported",
        }));
    };

    let mut comparison_number: i16 = 0;
    if comparison == Ordering::Less {
        comparison_number = -1;
    } else if comparison == Ordering::Greater {
        comparison_number = 1;
    }

    // TODO: Convert comparison to "<", "=", or ">"
    let json_result = json!({
        "label": label,
        "result": result_string,
        "compare_result": comparison_number,
        "actual_options": format!("{options:?}")
    });
    Ok(json_result)
}
