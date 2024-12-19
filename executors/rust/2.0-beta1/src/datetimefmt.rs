// https://docs.rs/icu/1.3.2/icu/datetime/struct.DateTimeFormatter.html
// https://docs.rs/icu/1.3.2/icu/datetime/input/trait.TimeZoneInput.html
// https://docs.rs/ixdtf/latest/ixdtf/

use icu::datetime::fieldsets;
use icu::datetime::fieldsets::enums::*;
use icu::datetime::DateTimeFormatter;
use icu::datetime::DateTimeFormatterPreferences;

use icu::locale::extensions::unicode;
use icu::locale::preferences::extensions::unicode::keywords::CalendarAlgorithm;
use icu::locale::Locale;

use icu::timezone::IxdtfParser;

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

    let field_set = match (
        option_struct.date_style.as_deref(),
        option_struct.time_style.as_deref(),
    ) {
        (Some(date_style), Some(time_style)) => {
            use fieldsets::*;
            use CompositeFieldSet::DateTime;
            use CompositeFieldSet::DateTimeZone;
            use DateAndTimeFieldSet as Enum;
            match (date_style, time_style) {
                ("full", "full") => DateTimeZone(Enum::YMDET(YMDET::long()), ZoneStyle::Z),
                ("full", "long") => DateTimeZone(Enum::YMDET(YMDET::long()), ZoneStyle::Z),
                ("full", "medium") => DateTime(Enum::YMDET(YMDET::long())),
                ("full", "short") => DateTime(Enum::YMDET(YMDET::long().hm())),
                ("long", "full") => DateTimeZone(Enum::YMDT(YMDT::long()), ZoneStyle::Z),
                ("long", "long") => DateTimeZone(Enum::YMDT(YMDT::long()), ZoneStyle::Z),
                ("long", "medium") => DateTime(Enum::YMDT(YMDT::long())),
                ("long", "short") => DateTime(Enum::YMDT(YMDT::long().hm())),
                ("medium", "full") => DateTimeZone(Enum::YMDT(YMDT::medium()), ZoneStyle::Z),
                ("medium", "long") => DateTimeZone(Enum::YMDT(YMDT::medium()), ZoneStyle::Z),
                ("medium", "medium") => DateTime(Enum::YMDT(YMDT::medium())),
                ("medium", "short") => DateTime(Enum::YMDT(YMDT::medium().hm())),
                ("short", "full") => DateTimeZone(Enum::YMDT(YMDT::short()), ZoneStyle::Z),
                ("short", "long") => DateTimeZone(Enum::YMDT(YMDT::short()), ZoneStyle::Z),
                ("short", "medium") => DateTime(Enum::YMDT(YMDT::short())),
                ("short", "short") => DateTime(Enum::YMDT(YMDT::short().hm())),
                (date_style, time_style) => {
                    panic!("unknown date/time style: {date_style}, {time_style}")
                }
            }
        }
        (Some(date_style), None) => {
            use CompositeFieldSet as Comp;
            use DateFieldSet as Enum;
            match date_style {
                "full" => Comp::Date(Enum::YMDE(fieldsets::YMDE::long())),
                "long" => Comp::Date(Enum::YMD(fieldsets::YMD::long())),
                "medium" => Comp::Date(Enum::YMD(fieldsets::YMD::medium())),
                "short" => Comp::Date(Enum::YMD(fieldsets::YMD::short())),
                time_style => panic!("unknown time style: {time_style}"),
            }
        }
        (None, Some(time_style)) => {
            use CompositeFieldSet as Comp;
            use TimeFieldSet as Enum;
            match time_style {
                "full" => Comp::TimeZone(Enum::T(fieldsets::T::long()), ZoneStyle::Z),
                "long" => Comp::TimeZone(Enum::T(fieldsets::T::long()), ZoneStyle::Z),
                "medium" => Comp::Time(Enum::T(fieldsets::T::medium())),
                "short" => Comp::Time(Enum::T(fieldsets::T::short())),
                date_style => panic!("unknown date style: {date_style}"),
            }
        }
        (None, None) => {
            // Components bag.
            // The test cases only use semantic skeletons, so we can match on them here.
            match json_obj["skeleton"].as_str().unwrap() {
                other => panic!("unknown skeleton: {other}"),
            }
        }
    };

    // Get ISO instant in UTC time zone
    let input_iso = &json_obj["original_input"].as_str().unwrap();

    // Extract all the information we need from the string
    let input_zoned_date_time = crate::try_or_return_error!(label, locale, {
        IxdtfParser::new()
            .try_from_str(&input_iso)
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

    let formatted_dt = datetime_formatter.format_any_calendar(&input_zoned_date_time);
    let result_string = formatted_dt.to_string();

    Ok(json!({
        "label": label,
        "result": result_string,
        "actual_options":
        format!("{field_set:?}, {input_zoned_date_time:?}"),
    }))
}
