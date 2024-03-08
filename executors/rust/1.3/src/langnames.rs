//! Executor provides tests for LanguageNames, a special case of DisplayNames.

use serde_json::{json, Value};

use icu::displaynames::{DisplayNamesOptions, LanguageDisplayNames};

use icu::locid::subtags::Language;
use icu::locid::Locale;

// Function runs language names tests
pub fn run_language_name_test(json_obj: &Value) -> Result<Value, String> {
    let label = &json_obj["label"].as_str().unwrap();
    let options: DisplayNamesOptions = Default::default();

    let language_label = json_obj["language_label"]
        .as_str()
        .unwrap()
        .replace('_', "-");
    let input_lang_result = language_label.parse::<Language>();
    let input_lang = match input_lang_result {
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
                "error_detail": {"unsupported_locale": &locale_name_result}
            }))
        }
    };

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

    let display_name_formatter = LanguageDisplayNames::try_new(&langid.into(), options);

    let json_result = match display_name_formatter {
        Ok(formatter) => {
            json!({
                "label": label,
                "result":  formatter.of(input_lang)
            })
        }
        Err(e) => {
            json!({
                "label": label,
                "locale_label": locale_name,
                "error": e.to_string(),
                "error_type": "unsupported",
                "unsupported": e.to_string(),
                "error_detail": {"unsupported_locale": locale_name}
            })
        }
    };

    Ok(json_result)
}
