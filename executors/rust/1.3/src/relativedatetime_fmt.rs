// https://docs.rs/icu/1.3.2/icu/relativetime/struct.RelativeTimeFormatter.html

use fixed_decimal::FixedDecimal;
use icu::locid::Locale;
use icu_provider::DataLocale;

use icu::relativetime::{RelativeTimeFormatter, RelativeTimeFormatterOptions};

use serde_json::{json, Value};

use writeable::assert_writeable_eq;

struct RelativeDateTimeFormatterOptions {
    style: Option<String>,
    numbering_system: Option<String>,
}

pub fn run_relativedatetimeformat_test(json_obj: &Value) -> Result<Value, String> {
    let label = &json_obj["label"].as_str().unwrap();

    // If there are unsupported values, return
    // "unsupported" rather than an error.
    let options = &json_obj["options"]; // This will be an array.

    // let option_struct: RelativeDateTimeFormatterOptions = serde_json::from_str(&options.to_string()).unwrap();

    let locale_json_str: &str = json_obj["locale"].as_str().unwrap();

    let locale_str: String = locale_json_str.to_string();
    let lang_id = if let Ok(lc) = locale_str.parse::<Locale>() {
    } else {
        return Ok(json!({
            "label": label,
            "error_detail": {"locale": locale_str},
            "error_type": "locale problem",
        }));
    };
    let data_locale = DataLocale::from(lang_id);

    let count_str: &str = json_obj["count"].as_str().unwrap();
    let count = count_str
        .parse::<FixedDecimal>()
        .map_err(|e| e.to_string())?;

    let unit_str: &str = json_obj["unit"].as_str().unwrap();

    // !!! TODO: get the options to create the correct

    // TODO: use unit & length to select the correct constructor.

    let relative_time_formatter = RelativeTimeFormatter::try_new_long_second(
        &data_locale,
        RelativeTimeFormatterOptions::default(),
    )
    .expect("locale should be present");

    assert_writeable_eq!(
        relative_time_formatter.format(FixedDecimal::from(5i8)),
        "in 5 seconds"
    );
    assert_writeable_eq!(
        relative_time_formatter.format(FixedDecimal::from(-10i8)),
        "10 seconds ago"
    );

    let formatted_result = relative_time_formatter.format(count);
    // ??? .expect("should work");

    let result_string = formatted_result.to_string();

    Ok(json!({
            "label": label,
            "result": result_string,
            "actual_options": format!("{unit_str:?}, {count:?}"),
    //        format!("{option_struct:?}, {unit_str:?}, {count:?}"),
        }))
}
