/*
 * Executor provides tests for LanguageNames, a special case of DisplayNames.
 */

use serde_json::{json, Value};

use icu_displaynames::{DisplayNamesOptions, LanguageDisplayNames};
use icu::locid::{locale, Locale, subtags_language as language};
use icu_provider::DataLocale;

use std::str::FromStr;

// Function runs language names tests
pub fn run_language_name_test(json_obj: &Value) -> Result<Value, String> {
    let provider = icu_testdata::unstable();

    let label = &json_obj["label"].as_str().unwrap();
    let options: DisplayNamesOptions = Default::default();

    let input_lang_str = &json_obj["language_label"].as_str().unwrap();
    let input_lang =language!("de");  // TODO!!! input_lang_str);
    
    let json_result1 = json!({
        "label": label,
        "result": input_lang});

    // Ok(json_result1)
    let langid = if json_obj.get("locale_label") != None {
        let locale_name = &json_obj["locale_label"].as_str().unwrap();
        Locale::from_str(locale_name).unwrap()
    } else {
        locale!("und")
    };
    let data_locale = DataLocale::from(langid);

    let json_result = json!({
        "label": label,
        "locale_name": langid.write_to_string,
        "result": "abc"
    });
    
    let display_name = LanguageDisplayNames::try_new_unstable(
         &provider,
         &data_locale.into(),
         options,
    ).expect("#Data should load correctly");

    // let json_result = json!({
    //     "label": label,
    //     "result":  display_name.of(input_lang)});

    Ok(json_result)
}
