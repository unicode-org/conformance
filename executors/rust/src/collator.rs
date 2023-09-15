/*
 * Executor provides tests for Collator.
 */

use serde_json::{json, Value};

use core::cmp::Ordering;
use icu::collator::*;
use icu::locid::locale;

// Function runs comparison using collator
pub fn run_collation_test(json_obj: &Value) -> Result<Value, String> {
    // TODO: Handle errors of missing values and failures.
    let label = &json_obj["label"].as_str().unwrap();
    let ignore_punctuation: &Option<bool> = &json_obj["ignorePunctuation"].as_bool();
    let str1: &str = json_obj["s1"].as_str().unwrap();
    let str2: &str = json_obj["s2"].as_str().unwrap();

    let data_provider = icu_testdata::unstable();

    let mut options = CollatorOptions::new();
    options.strength = Some(Strength::Tertiary);

    // Ignore punctuation only if using shifted test.
    if let Some(ip) = ignore_punctuation {
        if *ip {
            options.alternate_handling = Some(AlternateHandling::Shifted);
        }
    }

    let collator: Collator =
        Collator::try_new_unstable(&data_provider, &locale!("en").into(), options).unwrap();

    let comparison = collator.compare(str1, str2);

    let result = comparison == Ordering::Less;

    // TODO: How to do this easier?
    let mut result_string = true;
    if !result {
        result_string = false;
    }

    let mut comparison_number : i16 = 0;
    if comparison == Ordering::Less {
        comparison_number = -1;
    } else if comparison == Ordering::Greater {
        comparison_number = 1;
    }
    // TODO: Convert comparison to "<", "=", or ">"
    let json_result = json!({
        "label": label,
        "result": result_string,
        "compare_result": comparison_number
    });
    Ok(json_result)
}
