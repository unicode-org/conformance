//! Provides tests for likely subtags to mimimize and maximize.

use serde_json::{json, Value};

#[cfg(any(ver = "1.3", ver = "1.4", ver = "1.5"))]
pub use icu::locid_transform::LocaleExpander;

#[cfg(not(any(ver = "1.3", ver = "1.4", ver = "1.5")))]
pub use icu::locale::LocaleExpander;

#[cfg(any(ver = "1.3", ver = "1.4", ver = "1.5"))]
type LocaleType = super::compat::Locale;

#[cfg(not(any(ver = "1.3", ver = "1.4", ver = "1.5")))]
type LocaleType = super::compat::LanguageIdentifier;

// https://docs.rs/icu/latest/icu/locid_transform/

// Function runs language names tests
pub fn run_likelysubtags_test(json_obj: &Value) -> Result<Value, String> {
    let lc = LocaleExpander::new_extended();

    let label = &json_obj["label"].as_str().unwrap();

    let test_option = &json_obj["option"].as_str().unwrap();

    let locale_str: &str = json_obj["locale"].as_str().unwrap();

    let mut locale = locale_str.parse::<LocaleType>().unwrap();

    if test_option == &"minimizeFavorScript" {
        #[cfg(any(ver = "1.3", ver = "1.4"))]
        {
            // This option is not yet supported.
            return Ok(json!({
                "label": label,
                "error_detail": {"option": test_option},
                "unsupported": test_option,
                "error_type": "unsupported",
            }));
        }
        #[cfg(not(any(ver = "1.3", ver = "1.4")))]
        {
            lc.minimize_favor_script(&mut locale);
        }
    } else if test_option == &"minimize" || test_option == &"minimizeFavorRegion" {
        lc.minimize(&mut locale);
    } else if test_option == &"maximize" {
        lc.maximize(&mut locale);
    } else {
        // This option is not yet supported.
        return Ok(json!({
            "label": label,
            "error_detail": {"option": test_option},
            "unsupported": test_option,
            "error_type": "unsupported",
        }));
    }

    let json_result = json!({
        "label": label,
        "result": locale.to_string()
    });

    Ok(json_result)
}
