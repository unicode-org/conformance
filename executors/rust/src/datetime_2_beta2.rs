// https://docs.rs/icu/1.3.2/icu/datetime/struct.DateTimeFormatter.html
// https://docs.rs/icu/1.3.2/icu/datetime/input/trait.TimeZoneInput.html
// https://docs.rs/ixdtf/latest/ixdtf/

use icu::calendar::cal::Iso;
use icu::datetime::fieldsets::builder::*;
use icu::datetime::input::ZonedDateTime;
use icu::datetime::options::*;
use icu::datetime::DateTimeFormatter;
use icu::datetime::DateTimeFormatterPreferences;

use icu::locale::extensions::unicode;
use icu::locale::preferences::extensions::unicode::keywords::CalendarAlgorithm;
use icu::locale::Locale;

use serde::{Deserialize, Serialize};
use serde_json::{json, Value};

#[derive(Deserialize, Serialize, Debug)]
#[serde(rename_all = "camelCase")]
struct DateTimeFormatOptions {
    calendar: Option<String>,
    date_style: Option<String>,
    numbering_system: Option<String>,
    time_style: Option<String>,
    time_zone: Option<String>,

    era: Option<String>,
    year: Option<String>,
    month: Option<String>,
    week: Option<String>,
    day: Option<String>,
    weekday: Option<String>,
    hour: Option<String>,
    minute: Option<String>,
    second: Option<String>,
    fractional_second: Option<String>,
}

pub fn run_datetimeformat_test(json_obj: &Value) -> Result<Value, String> {
    let label = &json_obj["label"].as_str().unwrap();

    // If there are unsupported values, return
    // "unsupported" rather than an error.
    let options = &json_obj["options"]; // This will be an array.

    let option_struct: DateTimeFormatOptions = serde_json::from_str(&options.to_string()).unwrap();

    let calendar_algorithm = option_struct.calendar.as_ref().map(|calendar_str| {
        CalendarAlgorithm::try_from(&unicode::Value::try_from_str(calendar_str).unwrap()).unwrap()
    });

    let locale = json_obj["locale"]
        .as_str()
        .unwrap()
        .parse::<Locale>()
        .unwrap();
    let mut preferences = DateTimeFormatterPreferences::from(&locale);
    preferences.calendar_algorithm = calendar_algorithm;

    let mut builder = FieldSetBuilder::default();
    builder.date_fields = match option_struct.date_style.as_deref() {
        Some("full") => Some(DateFields::YMDE),
        Some("long") => Some(DateFields::YMD),
        Some("medium") => Some(DateFields::YMD),
        Some("short") => Some(DateFields::YMD),
        Some(other) => panic!("unknown length: {other}"),
        None => None,
    };
    builder.time_precision = match option_struct.time_style.as_deref() {
        Some("full") => Some(TimePrecision::Second),
        Some("long") => Some(TimePrecision::Second),
        Some("medium") => Some(TimePrecision::Second),
        Some("short") => Some(TimePrecision::Minute),
        Some(other) => panic!("unknown length: {other}"),
        None => None,
    };
    builder.zone_style = match option_struct.time_style.as_deref() {
        Some("full") => Some(ZoneStyle::SpecificShort),
        Some("long") => Some(ZoneStyle::SpecificShort),
        Some("medium") => None,
        Some("short") => None,
        Some(other) => panic!("unknown length: {other}"),
        None => None,
    };
    let field_set = builder.build_composite().unwrap();

    // Get ISO instant in UTC time zone
    let input_iso = &json_obj["original_input"].as_str().unwrap();

    // Extract all the information we need from the string
    let input_zoned_date_time = super::try_or_return_error!(label, locale, {
        ZonedDateTime::try_from_str(&input_iso, Iso, Default::default(), &Default::default())
            .map_err(|e| format!("{e:?}"))
    });

    // The constructor is called with the given options
    // The default parameter is time zone formatter options. Not used yet.
    let dtf_result = DateTimeFormatter::try_new(preferences, field_set);

    let datetime_formatter = match dtf_result {
        Ok(dtf) => dtf,
        Err(e) => {
            return Ok(json!({
                "label": label,
                "error_detail": format!("{option_struct:?}"),
                "error_type": format!("Failed to create DateTimeFormatter instance: {e:?}"),
            }));
        }
    };

    let formatted_dt = datetime_formatter.format(&input_zoned_date_time);
    let result_string = formatted_dt.to_string();

    Ok(json!({
        "label": label,
        "result": result_string,
        "actual_options":
        format!("{field_set:?}, {input_zoned_date_time:?}"),
    }))
}
