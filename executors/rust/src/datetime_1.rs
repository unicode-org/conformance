// https://docs.rs/icu/1.3.2/icu/datetime/struct.DateTimeFormatter.html
// https://docs.rs/icu/1.3.2/icu/datetime/input/trait.TimeZoneInput.html
// https://docs.rs/ixdtf/latest/ixdtf/

// IanaToBcp47Mapper deprecated in 1.5
#![cfg_attr(conformance_ver = "1.5", allow(deprecated))]

use icu::calendar::DateTime;
use icu::datetime::{
    options::components, options::length, options::DateTimeFormatterOptions, pattern::reference,
    pattern::runtime, ZonedDateTimeFormatter,
};

use icu::locid::Locale;

// https://docs.rs/icu/latest/icu/timezone/struct.CustomTimeZone.html#method.maybe_calculate_metazone
use icu::timezone::CustomTimeZone;
use icu::timezone::GmtOffset;
use icu::timezone::MetazoneCalculator;

use icu_provider::DataLocale;

use icu::timezone::IanaToBcp47Mapper;

use ixdtf::parsers::IxdtfParser;

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

    // Get calendar. If present, add to locale string
    // as "-u-ca-" + calendar name.
    let calendar_str = &option_struct.calendar;

    let locale_json_str: &str = json_obj["locale"].as_str().unwrap();
    let mut locale_str: String = locale_json_str.to_string();
    // ??? Is calendar necessary with the u-ca option in ISO string?
    if calendar_str.is_some() {
        locale_str = locale_json_str.to_string() + "-u-ca-" + &calendar_str.as_ref().unwrap();
    }

    let lang_id = if let Ok(lc) = locale_str.parse::<Locale>() {
        lc
    } else {
        return Ok(json!({
            "label": label,
            "error_detail": {"option": locale_str},
            "error_type": "locale problem",
        }));
    };
    let data_locale = DataLocale::from(lang_id);

    let mut _unsupported_options: Vec<&str> = Vec::new();

    let option_struct: DateTimeFormatOptions = serde_json::from_str(&options.to_string()).unwrap();

    let date_style_str = &option_struct.date_style;
    let date_style = match date_style_str.as_deref() {
        Some("full") => Some(length::Date::Full),
        Some("long") => Some(length::Date::Long),
        Some("medium") => Some(length::Date::Medium),
        Some("short") => Some(length::Date::Short),
        _ => None,
    };

    // TimeStyle long or full requires that you use ZonedDateTimeFormatter.
    // long known issue that is documented and has been filed several times.
    // Is fixed in 2.0
    let time_style_str = &option_struct.time_style;
    let time_style = match time_style_str.as_deref() {
        Some("full") => Some(length::Time::Full),
        Some("long") => Some(length::Time::Long),
        Some("medium") => Some(length::Time::Medium),
        Some("short") => Some(length::Time::Short),
        _ => None,
    };

    // Set up DT option if either is set
    let mut dt_length_options = length::Bag::empty();
    dt_length_options.date = date_style;
    dt_length_options.time = time_style;

    let dt_options = if dt_length_options != length::Bag::empty() {
        DateTimeFormatterOptions::Length(dt_length_options)
    } else {
        // For versions 1.X, but not in 2.X.
        // This is using an interal feature.
        let skeleton_str = &json_obj["skeleton"].as_str().unwrap();
        let parsed_skeleton = skeleton_str.parse::<reference::Pattern>().unwrap();
        let mut components_bag = components::Bag::from(&runtime::PatternPlurals::SinglePattern(
            runtime::Pattern::from(&parsed_skeleton),
        ));

        let option_struct: DateTimeFormatOptions =
            serde_json::from_str(&options.to_string()).unwrap();

        components_bag.hour = match option_struct.hour.as_deref() {
            Some("numeric") => Some(components::Numeric::Numeric),
            Some("2-digit") => Some(components::Numeric::TwoDigit),
            _ => None,
        };
        DateTimeFormatterOptions::Components(components_bag)
    };

    // Get ISO instant in UTC time zone
    let input_iso = &json_obj["input_string"].as_str().unwrap();

    let dt_iso = IxdtfParser::new(input_iso).parse().unwrap();
    let date = dt_iso.date.unwrap();
    let time = dt_iso.time.unwrap();

    // Compute the seconds for the timezone's offset
    let offset_seconds: i32 = json_obj["tz_offset_secs"]
        .as_i64()
        .unwrap()
        .try_into()
        .unwrap();

    let gmt_offset_seconds = GmtOffset::try_from_offset_seconds(offset_seconds).ok();

    let mut datetime_iso = DateTime::try_new_iso_datetime(
        date.year,
        date.month,
        date.day,
        time.hour,
        time.minute,
        0, // Seconds added below.
    )
    .expect("Failed to initialize ISO DateTime instance.");
    let mut dt_integer_minutes = datetime_iso.minutes_since_local_unix_epoch();
    dt_integer_minutes += offset_seconds / 60;

    datetime_iso = DateTime::from_minutes_since_local_unix_epoch(dt_integer_minutes);
    datetime_iso.time.second = time.second.try_into().unwrap();

    let any_datetime = datetime_iso.to_any();

    // Testing with a default timezone
    let timezone_str = &option_struct.time_zone;

    // https://docs.rs/icu/latest/icu/timezone/struct.IanaToBcp47Mapper.html
    let mapper = IanaToBcp47Mapper::new();
    let mapper_borrowed = mapper.as_borrowed();

    let mapped_tz = mapper_borrowed.get(timezone_str.as_ref().unwrap());
    let mzc = MetazoneCalculator::new();
    let my_metazone_id = mzc.compute_metazone_from_time_zone(mapped_tz.unwrap(), &datetime_iso);

    let time_zone = if timezone_str.is_some() {
        CustomTimeZone {
            gmt_offset: gmt_offset_seconds,
            time_zone_id: mapped_tz,
            metazone_id: my_metazone_id,
            zone_variant: None,
        }
    } else {
        // Defaults to UTC
        CustomTimeZone::utc()
    };

    // The constructor is called with the given options
    // The default parameter is time zone formatter options. Not used yet.
    let dtf_result = ZonedDateTimeFormatter::try_new_experimental(
        &data_locale,
        dt_options.clone(),
        Default::default(),
    );

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

    let formatted_dt = datetime_formatter
        .format(&any_datetime, &time_zone)
        .expect("should work");
    let result_string = formatted_dt.to_string();

    Ok(json!({
        "label": label,
        "result": result_string,
        "actual_options":
        format!("{dt_options:?}, {time_zone:?}"),
    }))
}
