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

    // TODO: Get and apply locale if given. Else use "und" or "en"
    
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
    let compare_symbol = compare_option.and_then(|c| c.get(0..1)).unwrap_or("<");

    if let Some(strength) = strength_option {
        options.strength = match strength {
            "primary" => Some(Strength::Primary),
            "secondary" => Some(Strength::Secondary),
            "tertiary" => Some(Strength::Tertiary),
            "quaternary" => Some(Strength::Quaternary),
            "identical" => Some(Strength::Identical),
            _ => {
                return Ok(json!({
                    "label": label,
                    "error_detail": {"strength": strength},
                    "unsupported": "strength",
                    "error_type": "unsupported",
                }));
            }
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

    let result_string = match compare_symbol {
        "<" => comparison.is_le(),
        "=" => comparison.is_eq(),
        _ => {
            return Ok(json!({
                "label": label,
                "error_detail": {
                    "compare_type": compare_symbol,
                },
                "unsupported": "compare_symbol",
                "error_type": "unsupported",
            }));
        }
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
