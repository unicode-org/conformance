//! Executor provides tests for LanguageNames, a special case of DisplayNames.

use serde_json::{json, Value};

use super::compat::{pref, Locale};

#[cfg(any(ver = "1.3", ver = "1.4"))]
use icu::displaynames::*;

#[cfg(any(ver = "1.5", ver = "2.0-beta1"))]
use icu::experimental::displaynames::*;

// Function runs locale names tests
pub fn run_locale_name_test(json_obj: &Value) -> Result<Value, String> {
    let label = &json_obj["label"].as_str().unwrap();
    let mut options: DisplayNamesOptions = Default::default();

    let language_label = json_obj["language_label"]
        .as_str()
        .unwrap()
        .replace('_', "-");
    let input_locale_result = language_label.parse::<Locale>();
    let input_locale = match input_locale_result {
        Ok(l) => l,
        Err(_e) => {
            return Ok(json!({
                "error": format!("bad language label: {}", language_label),
                // ?? Get the string associated?
                // "error_msg": e.as_str(),
                "label": label,
                "language_label": language_label,
                "test_type": "display_names",
                "unsupported": "language_label",
                "error_type": "unsupported",
            }));
        }
    };

    let locale_name_result = &json_obj["locale_label"].as_str();
    let locale_name = match locale_name_result {
        Some(s) => s,
        None => {
            return Ok(json!({
                "error": "locale label",
                "label": label,
                "language_label": language_label,
                "test_type": "display_names",
                "unsupported": "locale name",
                "error_type": "unsupported",
                "error_detail": {"cannot parse locale": &locale_name_result}
            }))
        }
    };

    // Get either standard or dialect form of locale name.
    let language_display_result = json_obj["languageDisplay"].as_str();
    let language_display: LanguageDisplay = match language_display_result {
        Some(s) => match s {
            "standard" => LanguageDisplay::Standard,
            "dialect" => LanguageDisplay::Dialect,
            &_ => LanguageDisplay::Standard,
        },
        None => LanguageDisplay::Standard, // The default
    };

    options.language_display = language_display;

    let langid_result = locale_name.parse::<Locale>();

    let langid = match langid_result {
        Ok(lid) => lid,
        Err(e) => {
            return Ok(json!({
                "error": e.to_string(),
                "label": label,
                "locale_label": locale_name,
                "language_label": language_label,
                "test_type": "display_names",
                "unsupported": "locale name",
                "error_type": "unsupported",
                "error_detail": {"unsupported_locale": locale_name},
            }))
        }
    };

    let display_name_formatter = LocaleDisplayNamesFormatter::try_new(pref!(langid), options);

    let json_result = match display_name_formatter {
        Ok(formatter) => {
            json!({
                "label": label,
                "result":  formatter.of(&input_locale)
            })
        }
        Err(e) => {
            json!({
                "label": label,
                "locale_label": locale_name,
                "error": e.to_string(),
                "error_type": "unsupported",
                "unsupported": e.to_string(),
                "error_detail": {"formatting fails for": locale_name}
            })
        }
    };

    Ok(json_result)
}
