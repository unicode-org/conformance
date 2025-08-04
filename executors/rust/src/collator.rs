//! Executor provides tests for Collator.

use serde_json::{json, Value};

use core::cmp::Ordering;
use icu::collator::*;

#[cfg(not(any(ver = "1.3", ver = "1.4", ver = "1.5", ver = "2.0-beta1")))]
use icu::collator::options::*;

#[cfg(not(any(ver = "1.3", ver = "1.4", ver = "1.5", ver = "2.0-beta1")))]
use icu::collator::preferences::{CollationCaseFirst as CaseFirst, CollationNumericOrdering};

use super::compat::{langid_und, pref};

// Function runs comparison using collator
pub fn run_collation_test(json_obj: &Value) -> Result<Value, String> {
    let label = &json_obj["label"].as_str().unwrap();
    let ignore_punctuation: Option<bool> = json_obj["ignorePunctuation"].as_bool();
    let str1: &str = json_obj["s1"].as_str().unwrap();
    let str2: &str = json_obj["s2"].as_str().unwrap();

    // These fields may be missing in tests
    let compare_option: Option<&str> = json_obj["compare_type"].as_str();
    let strength_option: Option<&str> = json_obj["strength"].as_str();
    let rules: Option<&str> = json_obj["rules"].as_str();

    let alternate_option: Option<&str> = json_obj["alternate"].as_str();
    let case_first_option: Option<&str> = json_obj["caseFirst"].as_str();
    let case_level_option: Option<&str> = json_obj["caseLevel"].as_str();
    let numeric_option: Option<&str> = json_obj["numeric"].as_str();
    let reorder_option: Option<&str> = json_obj["reorder"].as_str();
    let backwards_option: Option<&str> = json_obj["backwards"].as_str();
    let max_variable_option: Option<&str> = json_obj["maxVariable"].as_str();

    #[cfg(any(ver = "1.3", ver = "1.4", ver = "1.5"))]
    let mut options = CollatorOptions::new();
    #[cfg(not(any(ver = "1.3", ver = "1.4", ver = "1.5")))]
    let mut options = CollatorOptions::default();

    // Apply locale if given. Else use default locale.
    // Replace "root" with default locale
    let locale_name_opt = json_obj
        .get("locale")
        .map(|json_val| json_val.as_str().unwrap());
    let langid = match locale_name_opt {
        Some("root") | None => langid_und(),
        Some(other) => match other.parse() {
            Ok(l) => l,
            Err(_) => {
                return Ok(json!({
                    "label": label,
                    "error_detail": other,
                    "unsupported": "Unsupported locale",
                    "error_type": "unsupported",
                }))
            }
        },
    };

    #[cfg(any(ver = "1.3", ver = "1.4", ver = "1.5"))]
    let preferences: &icu_provider::DataLocale = pref!(&langid);
    #[cfg(not(any(ver = "1.3", ver = "1.4", ver = "1.5")))]
    #[cfg_attr(ver = "2.0-beta1", allow(unused_mut))]
    let mut preferences: CollatorPreferences = pref!(&langid);

    // Rules not yet supported.
    if rules.is_some() {
        return Ok(json!({
            "label": label,
            "error_detail": "Rules not supported",
            "unsupported": "Collator rules not available",
            "error_type": "unsupported",
        }));
    }

    if reorder_option.is_some() {
        // Reordering is only supported by the -kr option of a locale
        // See https://github.com/unicode-org/icu4x/issues/6033
        return Ok(json!({
            "label": label,
            "unsupported": "reorder scripts",
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

    if let Some(case_level) = case_level_option {
        options.case_level = match case_level {
            "off" => Some(CaseLevel::Off),
            "on" => Some(CaseLevel::On),
            _ => {
                return Ok(json!({
                    "label": label,
                    "error_detail": {"caseLevel": case_level},
                    "unsupported": "caseLevel",
                    "error_type": "unsupported",
                }));
            }
        }
    };

    if let Some(case_first) = case_first_option {
        #[cfg(not(any(ver = "1.3", ver = "1.4", ver = "1.5", ver = "2.0-beta1")))]
        {
            preferences.case_first = match case_first {
                "off" => Some(CaseFirst::False),
                "lower" => Some(CaseFirst::Lower),
                "upper" => Some(CaseFirst::Upper),
                _ => {
                    return Ok(json!({
                        "label": label,
                        "error_detail": {"caseFirst": case_first},
                        "unsupported": "caseFirst",
                        "error_type": "unsupported",
                    }));
                }
            }
        }
        #[cfg(any(ver = "1.3", ver = "1.4", ver = "1.5", ver = "2.0-beta1"))]
        {
            options.case_first = match case_first {
                "off" => Some(CaseFirst::Off),
                "lower" => Some(CaseFirst::LowerFirst),
                "upper" => Some(CaseFirst::UpperFirst),
                _ => {
                    return Ok(json!({
                        "label": label,
                        "error_detail": {"caseFirst": case_first},
                        "unsupported": "caseFirst",
                        "error_type": "unsupported",
                    }));
                }
            }
        }
    };

    // From 2.0, backward second level is available only via the fr-CA locale
    // <https://github.com/unicode-org/icu4x/pull/6291>
    if let Some(backwards) = backwards_option {
        #[cfg(not(any(ver = "1.3", ver = "1.4", ver = "1.5", ver = "2.0-beta1", ver = "2.0-beta2")))]
        {
            let _backwards = backwards;
            return Ok(json!({
                "label": label,
                "error_detail": {"backwards": backwards},
                "unsupported": "backwards",
                "error_type": "unsupported",
            }));
        }
        #[cfg(any(ver = "1.3", ver = "1.4", ver = "1.5", ver = "2.0-beta1", ver = "2.0-beta2"))]
        {
            options.backward_second_level = match backwards {
                "off" => Some(BackwardSecondLevel::Off),
                "on" => Some(BackwardSecondLevel::On),
                _ => {
                    return Ok(json!({
                        "label": label,
                        "error_detail": {"backwards": backwards},
                        "unsupported": "backwards",
                        "error_type": "unsupported",
                    }));
                }
            }
        }
    };

    // Numeric sort order.
    // CollatorPreferences in beta2 vs. Enum Numeric
    if let Some(numeric) = numeric_option {
        #[cfg(not(any(ver = "1.3", ver = "1.4", ver = "1.5", ver = "2.0-beta1")))]
        {
            preferences.numeric_ordering = match numeric {
                "off" => Some(CollationNumericOrdering::False),
                "on" => Some(CollationNumericOrdering::True),
                _ => {
                    return Ok(json!({
                        "label": label,
                        "error_detail": {"numeric": numeric},
                        "unsupported": "numeric",
                        "error_type": "unsupported",
                    }));
                }
            }
        };
        // !!! TODO: handle before 2.0beta2
    };

    if let Some(alternate) = alternate_option {
        options.alternate_handling = match alternate {
            "shifted" => Some(AlternateHandling::Shifted),
            "non-ignorable" => Some(AlternateHandling::NonIgnorable),
            _ => {
                return Ok(json!({
                    "label": label,
                    "error_detail": {"alternate": alternate},
                    "unsupported": "alternate",
                    "error_type": "unsupported",
                }));
            }
        }
    };

    if let Some(max_variable) = max_variable_option {
        options.max_variable = match max_variable {
            "space" => Some(MaxVariable::Space),
            "punctuation" => Some(MaxVariable::Punctuation),
            "symbol" => Some(MaxVariable::Symbol),
            "currency" => Some(MaxVariable::Currency),
            _ => {
                return Ok(json!({
                    "label": label,
                    "error_detail": {"maxVariable": max_variable},
                    "unsupported": "maxVariable",
                    "error_type": "unsupported",
                }));
            }
        }
    };

    // Ignore punctuation only if using shifted test.
    if let Some(ip) = ignore_punctuation {
        if ip {
            options.alternate_handling = Some(AlternateHandling::Shifted);
        }
    }

    // TODO !! Iterate to find actual level of comparison, then look
    // at compare type (1, 2, 3, 4, i, c) to see if it matches

    let collator = Collator::try_new(preferences, options).map_err(|e| e.to_string())?;
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

    let comparison_number: i16 = match comparison {
        Ordering::Less => -1,
        Ordering::Greater => 1,
        Ordering::Equal => 0,
    };

    let json_result = json!({
        "label": label,
        "result": result_string,
        "actual_options": {
            "options": format!("{options:?}, {preferences:?}"),
            "compared_result": comparison_number,
            "s1": str1,
            "s2": str2,
        }
    });
    Ok(json_result)
}
