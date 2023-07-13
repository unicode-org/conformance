/*
 * Executor provides tests for LanguageNames, a special case of DisplayNames.
 */

use serde_json::{json, Value};

use icu_displaynames::{DisplayNamesOptions, LanguageDisplayNames};
use icu::locid::{locale, Locale};
use icu_provider::DataLocale;

// Function runs language names tests
pub fn run_lang_test(json_obj: &Value) -> Result<String, String> {
    let label = &json_obj["label"].as_str().unwrap();
    let options: DisplayNamesOptions = Default::default();

    let input = &json_obj["input"].as_str().unwrap();

    // Default locale if not specified.
    let langid = if json_obj.get("locale") != None {
        let locale_name = &json_obj["locale"].as_str().unwrap();
        Locale::from_str(locale_name).unwrap()
    } else {
        locale!("und");
    };
    let data_locale = DataLocale::from(langid);

    let display_name = LanguageDisplayNames::try_new_unstable(
        icu_testdata::unstable(),
        &data_locale.into(),
        options,
    );

    let result = display_name.of(input);

    let json_result = json!({
        "label": label,
        "result": result});
    Ok(json_result);
}
