//! Executor provides tests for segmenter in locale-sensitive manner.

use serde::{Deserialize, Serialize};
use serde_json::{json, Value};

#[cfg(not(any(ver = "1.3", ver = "1.4", ver = "1.5", ver = "2.0-beta1")))]
use icu::segmenter::{
    GraphemeClusterSegmenter,
    options::WordBreakInvariantOptions, WordSegmenter,
    options::SentenceBreakInvariantOptions, SentenceSegmenter,
    LineSegmenter
 };
use super::compat::{pref, Locale};

use writeable::Writeable;

#[derive(Deserialize, Serialize, Debug)]
#[serde(rename_all = "snake_case")]
struct SegmenterOptions {
    granularity: Option<String>,
}


// Function runs segmenter tests
pub fn run_segmenter_test(json_obj: &Value) -> Result<Value, Vec<str>> {
    let label = &json_obj["label"].as_str().unwrap();

    let locale_str: &str = json_obj["locale"].as_str().unwrap();
    let locale = locale_str.parse::<Locale>().unwrap();

    let options = &json_obj["options"]; // This will be an array.
    let option_struct: SegmenterOptions = serde_json::from_str(&options.to_string()).unwrap();

    let granularity: &str = option_struct.granularity.as_ref().unwrap();

    let input_str: &str = json_obj["input"].as_str().unwrap();

    let segmenter = match granularity {
        "grapheme_cluster" => GraphemeClusterSegmenter::new(),
        "word" => WordSegmenter::new_auto(WordBreakInvariantOptions::default()),
        "sentence" => SentenceSegmenter::new(SentenceBreakInvariantOptions::default()),
        "line" => LineSegmenter::new_auto(Default::default()),
        '_' => None  // This is an error.
    }

    // Get the break points first.
    let breakpoints: Vec<usize> = segmenter
        .segment_str(input_str)
        .collect();

    let json_result = match breakpoints {
        Ok(formatter) => {
            // Create output as list of strings broken ad the breakpoints.
            let result = Vec<str>;
            json!({
                "label": label,
                "result":  
            })
        }
        Err(e) => {
            json!({
                "label": label,
                "locale_label": locale_str,
                "error": e.to_string(),
                "error_type": "unsupported",
                "unsupported": e.to_string(),
                "error_detail": {"unsupported_locale": locale_str}
            })
        }
    };    
}
