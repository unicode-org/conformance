//! Executor provides tests for segmenter in locale-sensitive manner.

use serde::{Deserialize, Serialize};
use serde_json::{json, Value};

#[cfg(not(any(ver = "2.0-beta1")))]
use icu::segmenter::{options::*, *};

use super::compat::Locale;

#[derive(Deserialize, Serialize, Debug)]
#[serde(rename_all = "snake_case")]
struct SegmenterOptions {
    granularity: Option<String>,
}

// Function runs segmenter tests
pub fn run_segmenter_test(json_obj: &Value) -> Result<Value, String> {
    // To use the locale
    let label = &json_obj["label"].as_str().unwrap();

    let locale_str: &str = json_obj["locale"].as_str().unwrap();
    let locale = locale_str.parse::<Locale>().unwrap();
    let lang_identifier = locale.id;

    let options = &json_obj["options"]; // This will be an array.
    let option_struct: SegmenterOptions = serde_json::from_str(&options.to_string()).unwrap();

    let granularity: &str = option_struct.granularity.as_ref().unwrap();

    let input_string: &str = json_obj["input"].as_str().unwrap();

    // Get desired segmenter, then comput the break points from the input.
    let breakpoints: Vec<usize> = match granularity {
        "grapheme_cluster" => {
            let segmenter = GraphemeClusterSegmenter::new();
            segmenter.segment_str(input_string).collect()
        }
        "word" => {
            // Get options
            let mut options = WordBreakOptions::default();
            options.content_locale = Some(&lang_identifier);

            let segmenter = WordSegmenter::try_new_auto(options).unwrap();
            segmenter.segment_str(input_string).collect()
        }
        "sentence" => {
            // Get options
            let mut options = SentenceBreakOptions::default();
            options.content_locale = Some(&lang_identifier);
            let segmenter = SentenceSegmenter::try_new(options).unwrap();
            segmenter.segment_str(input_string).collect()
        }
        "line" => {
            // Get options
            let mut options = LineBreakOptions::default();
            options.strictness = Some(LineBreakStrictness::Strict);
            options.content_locale = Some(&lang_identifier);
            let segmenter = LineSegmenter::new_auto(options);
            segmenter.segment_str(input_string).collect()
        }
        _ => {
            // This is an error
            return Ok(json!({
                "label": label,
                "locale_label": locale_str,
                "error": "Unknown segmenter option",
                "error_type": "unsupported",
                "unsupported": granularity.to_string(),
                "error_detail": {"unsupported_locale": locale_str}
            }));
        }
    };

    // Create output as list of strings broken ad the breakpoints.
    // For breakpoints, extract each part and push to result;
    let mut segments: Vec<String> = vec![];
    let mut start: usize = 0;
    for index in breakpoints.iter() {
        if *index > 0 {
            segments.push(input_string[start..*index].to_string());
        }
        start = *index;
    }
    Ok(json!({
        "label": label,
        "result": segments
    }))
}
