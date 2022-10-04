/*
 * Executor provides tests for Collator.
 */

use serde_json::{json, Value};
use std::io::{self,Write};

use core::cmp::Ordering;
use icu::collator::*;
use icu::locid::locale;

// Function runs comparison using collator
pub fn run_coll_test(json_obj: &Value) {
    let label = &json_obj["label"].as_str().unwrap();
    let str1: &str = &json_obj["string1"].as_str().unwrap();
    let str2: &str = &json_obj["string2"].as_str().unwrap();

    let data_provider = icu_testdata::unstable();

    let mut options = CollatorOptions::new();
    options.strength = Some(Strength::Tertiary);
    
    // Does this ignore punctuation?
    //coll_options.set_alternate_handling(Some(AlternateHandling::Shifted));

    let collator: Collator =
        Collator::try_new_unstable(
            &data_provider, &locale!("en").into(), options).unwrap();

    let comparison = collator.compare(&str1, &str2);

    let result = comparison == Ordering::Less;

    // TODO: How to do this easier?
    let mut result_string = "True";
    if !result {
        result_string = "False";
    }
    let json_result = json!({
        "label": label,
        "result": result_string});
    println!("{}", json_result);
    io::stdout().flush().unwrap();
}
