/*
 * Executor provides tests for LanguageNames, a special case of DisplayNames.
 */

use serde_json::{json, Value};

use icu_displaynames::{DisplayNamesOptions, LanguageDisplayNames};
use icu::locid::{locale, Locale, subtags_language as language};
use icu::locid::subtags::Language;

use icu_provider::DataLocale;

use std::str::FromStr;

// Function runs language names tests
pub fn run_language_name_test(json_obj: &Value) -> Result<Value, String> {
    let provider = icu_testdata::unstable();

    let label = &json_obj["label"].as_str().unwrap();
    let options: DisplayNamesOptions = Default::default();

    // let input_lang = language!("de");  // TODO!!! input_lang_str);

    let language_label = json_obj["language_label"].as_str().unwrap();
    println!("# {:?} LANGUAGE_LABEL", language_label);
    let input_lang = if json_obj.get("language_label") != None {
        let language_to_use = language_label; // language!("ru");  //
        Language::from_str(language_label)
    } else {
        // Need to handle language name plus region, e.g., "es-MX"
        println!("#{:?}", "DEFAULTING TO fr");
        Language::from_str("fr")
    };
    println!("#{:?}", input_lang);
    
    // The language whose name is returned as written in data_locale.
    let langid = if json_obj.get("locale_label") != None {
        let locale_name = &json_obj["locale_label"].as_str().unwrap();
        println!("LOCAL_NAME: {:?}", locale_name);
        Locale::from_str(locale_name).unwrap()
    } else {
        println!("No locale_label: Defaulting to und # {:?}", "DEFAULTING TO UND");
        Locale::from_str("es").unwrap()  //("und")
    };
    let data_locale = DataLocale::from(&langid);
    println!("DATA_LOCAL: {:?}", data_locale);
    
    let display_name_formatter = LanguageDisplayNames::try_new_unstable(
         &provider,
         &data_locale.into(),
         options,
    );

    let json_result =
        match display_name_formatter {
            Ok(formatter) => {
                json!({
                    "label": label,
                    "result":  formatter.of(input_lang)
                })
            },
            Err(e) => {
                json!({
                    "label": label,
                    "unsupported": "unsupported_options",
                    "error": e.to_string(),
                    "error_detail": {"unsupported_locale": langid.to_string()}
                })
            },
        };

    Ok(json_result)
}
