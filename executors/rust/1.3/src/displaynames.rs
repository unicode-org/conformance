//! Executor provides tests for DisplayNames.

use serde_json::{json, Value};

use icu::displaynames::*;
use icu::locid::Locale;

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
        LocaleDisplayNamesFormatter::try_new(&langid.into(), Default::default()).unwrap();

    Ok(json!({
        "label": label,
        "result": displaynames.of(input)
    }))
}
