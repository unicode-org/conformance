// https://docs.rs/icu/1.3.2/icu/datetime/struct.DateTimeFormatter.html
// https://docs.rs/icu/1.3.2/icu/datetime/input/trait.TimeZoneInput.html
// https://docs.rs/ixdtf/latest/ixdtf/


use icu::calendar::DateTime;
use icu::datetime::{options::length, ZonedDateTimeFormatter};
use icu::locid::Locale;

// https://docs.rs/icu/latest/icu/timezone/struct.CustomTimeZone.html#method.maybe_calculate_metazone
use icu::timezone::{CustomTimeZone};
use icu::timezone::provider::{TimeZoneBcp47Id};
use tinystr::tinystr;
use icu::timezone::MetazoneCalculator;

use icu_provider::DataLocale;

use icu::timezone::IanaToBcp47Mapper;

use ixdtf::parsers::IxdtfParser;

use serde::{Deserialize, Serialize};
use serde_json::{json, Value};

#[derive(Deserialize, Serialize, Debug)]
#[serde(rename_all = "camelCase")]
struct DateTimeFormatOptions {
    date_style: Option<String>,
    time_style: Option<String>,
    time_zone: Option<String>,
    era: Option<String>,
    calendar: Option<String>,
    numbering_system: Option<String>,
}

pub fn run_datetimeformat_test(json_obj: &Value) -> Result<Value, String> {
    let label = &json_obj["label"].as_str().unwrap();

    // If there are unsupported values, return
    // "unsupported" rather than an error.
    let options = &json_obj["options"]; // This will be an array.

    let option_struct: DateTimeFormatOptions =
        serde_json::from_str(&options.to_string()).unwrap();

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

    // TODO: Get and use timeZone

    let option_struct: DateTimeFormatOptions = serde_json::from_str(&options.to_string()).unwrap();

    let date_style_str = &option_struct.date_style;
    let date_style = if date_style_str == &Some("full".to_string()) {
        length::Date::Full
    } else if date_style_str == &Some("long".to_string()) {
        length::Date::Long
    } else if date_style_str == &Some("short".to_string()) {
        length::Date::Short
    } else if date_style_str == &Some("medium".to_string()) {
        length::Date::Medium
    } else {
        length::Date::Full
    };

    // TimeStyle long or full requires that you use ZonedDateTimeFormatter.
    // long known issue that is documented and has been filed several times.
    // Is fixed in 2.0
    let time_style_str = &option_struct.time_style;
    let time_style = if time_style_str == &Some("full".to_string()) {
        length::Time::Full
    } else if time_style_str == &Some("long".to_string()) {
        length::Time::Long
    } else if time_style_str == &Some("short".to_string()) {
        length::Time::Short
    } else if time_style_str == &Some("medium".to_string()) {
        length::Time::Medium
    } else {
        // !!! SET TO UNDEFINED
       length::Time::Full
    };

    // Set up DT option if either is set
    let dt_options = if date_style_str.is_some() && time_style_str.is_some() {
        length::Bag::from_date_time_style(date_style, time_style)
    } else if date_style_str.is_none() && time_style_str.is_some() {
        length::Bag::from_time_style(time_style)
    } else if date_style_str.is_some() && time_style_str.is_none() {
        length::Bag::from_date_style(date_style)
    } else {
        length::Bag::default()
    };

    // Get ISO input string including offset and time zone
    let input_iso = &json_obj["input_string"].as_str().unwrap();
//    let input_iso: String = input_time_string.to_string() + "[-00:00]";

    let dt_iso = IxdtfParser::new(&input_iso).parse().unwrap();
    let date = dt_iso.date.unwrap();
    let time = dt_iso.time.unwrap();
    let _tz_offset = dt_iso.offset.unwrap();
    let _tz_annotation = dt_iso.tz.unwrap();

    let datetime_iso = DateTime::try_new_iso_datetime(
        date.year,
        date.month,
        date.day,
        time.hour,
        time.minute,
        time.second,
    )
    .expect("Failed to initialize ISO DateTime instance.");
    let any_datetime = datetime_iso.to_any();

    // Testing with a default timezone
    let timezone_str = &option_struct.time_zone;

    // https://docs.rs/icu/latest/icu/timezone/struct.IanaToBcp47Mapper.html
    let mapper = IanaToBcp47Mapper::new();
    let mapper_borrowed = mapper.as_borrowed();

    let mapped_tz = mapper_borrowed.get(timezone_str.as_ref().unwrap());
    let mzc = MetazoneCalculator::new();
    let my_metazone_id = mzc.compute_metazone_from_time_zone(mapped_tz.unwrap(), &datetime_iso);
    
    // Compute the seconds for the 
    let offset_seconds = GmtOffset::try_from_offset_seconds(
        tz_offset.hour * 360 + _tz_offset.minute * 60);
    
    let time_zone = if timezone_str.is_some() {
        CustomTimeZone {
            gmt_offset: offset_seconds,   // ??? tz_offset,
            time_zone_id: None,  // !! ?? Some(TimeZoneBcp47Id(tinystr!(4, my_metazone_id))),
            metazone_id: my_metazone_id,
            zone_variant: None,
        }
    } else {
        // Defaults to UTC
        CustomTimeZone::utc()
    };

    // The constructor is called with the given options
    // The default parameter is time zone formatter options. Not used yet.
    let dtf_result =
        ZonedDateTimeFormatter::try_new(&data_locale, dt_options.into(), Default::default());

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

    // Note: A "classical" skeleton is used in most cases, but this version
    // of the executor does not use it.

    let formatted_dt = datetime_formatter
        .format(&any_datetime, &time_zone)
        .expect("should work");
    let result_string = formatted_dt.toy_string();

    Ok(json!({
        "label": label,
        "result": result_string,
        "actual_options":
        format!("{_tz_offset:?}, {dt_options:?}, {timezone:?}"),  // , {dt_iso:?}"),
    }))
}

