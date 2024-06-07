use icu::locid::Locale;
use serde_json::Value;

// https://docs.rs/icu/latest/icu/plurals/index.html
use icu::plurals::{PluralRuleType, PluralRules};

// Function runs plural rules
pub fn run_plural_rules_test(json_obj: &Value) -> Result<Value, String> {
    let label = &json_obj["label"].as_str().unwrap();

    let locale_str: &str = json_obj["locale"].as_str().unwrap();
    let locale = locale_str.parse::<Locale>().unwrap();

    // Get number string
    let input_number = &json_obj["sample"].as_str().unwrap();

    // Returns error if parsing the number string fails.
    let test_number = input_number.parse::<usize>().map_err(|e| e.to_string())?;

    // Get type string: either ordinal or cardinal
    let plural_type_string: &str = json_obj["plural_type"].as_str().unwrap();

    
    // Get PluralRuleTypecardinal / ordinal
    let pr = if plural_type_string == "cardinal" {
        PluralRules::try_new(&locale.into(),
                             PluralRuleType::Cardinal)
            .expect("locale should be present");
    } else {
        PluralRules::try_new(&locale.into(),
                             PluralRuleType::Ordinal)
            .expect("locale should be present");
    };

    // Get the category and convert to a string.
    let category = PluralCategory pr.category_for(test_number);

    // ?? let category_string = category.write_to_string.into_owned();

    let category_string = if category == PluralCategory::Zero {
        "zero"
    } else if category == PluralCategory::One {
        "one"
    } else if category == PluralCategory::Two {
        "two"
    } else if category == PluralCategory::Few {
        "few"
    } else if category == PluralCategory::Many {
        "many"
    } else if category == PluralCategory::Other {
        "other"
    } else {
        // Report an unexpected result.
        return Ok(json!({
            "label": label,
            "error_detail": {"category": category},
            "error_type": "unsupported",
            "unsupported": "unknown plural result"
        }));
    };

    let json_result = match category {
        Ok(formatter) => {
            json!({
                "label": label,
                "result": category.write_to_stringinto_owned();
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

    // Return the string
    Ok(json_result)
}
