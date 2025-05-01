//! Executor provides tests for DisplayNames.

use serde_json::{json, Value};

#[cfg(any(ver = "1.3", ver = "1.4"))]
use icu::displaynames::*;

#[cfg(not(any(ver = "1.3", ver = "1.4")))]
use icu::experimental::displaynames::*;

use super::compat::{pref, Locale};

// Function runs comparison using displaynames
pub fn _todo(json_obj: &Value) -> Result<Value, String> {
    let label = &json_obj["label"].as_str().unwrap();
    let _options = &json_obj["options"].as_str().unwrap();
    let input = &json_obj["input"].as_str().unwrap().parse().unwrap();

    // Default locale if not specified.
    let langid: Locale = json_obj
        .get("locale")
        .map(|locale_name| locale_name.as_str().unwrap().parse().unwrap())
        .unwrap_or_default();

    let displaynames =
        LocaleDisplayNamesFormatter::try_new(pref!(langid), Default::default()).unwrap();

    Ok(json!({
        "label": label,
        "result": displaynames.of(input)
    }))
}
