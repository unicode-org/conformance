 // https://docs.rs/icu/1.3.2/icu/datetime/struct.DateTimeFormatter.html

use icu::calendar::DateTime;
use icu::datetime::{options::length, DateTimeFormatter};
use icu::locid::Locale;

use serde_json::{json, Value};

use std::str::FromStr;
use writeable::assert_writeable_eq;

#[derive(Deserialize, Serialize, Debug)]
#[serde(rename_all = "camelCase")]
struct DateTimeFormatOptions {
    date_style: Option<String>,
    time_style: Option<String>,
    time_zone: Option<String>,
}

pub fn run_datetimeformat_test(json_obj: &Value) -> Result<Value, String> {
    let label = &json_obj["label"].as_str().unwrap();
    
    // Default locale if not specified.
    let mut langid: Locale = json_obj
        .get("locale")
        .map(|locale_name| locale_name.as_str().unwrap().parse().unwrap())
        .unwrap_or_default();

    // If there are unsupported values, return
    // "unsupported" rather than an error.
    let options = &json_obj["options"]; // This will be an array.

    let mut _unsupported_options: Vec<&str> = Vec::new();

    // TODO: handle options
    // TODO: handle calendar
    // TODO: dateStyle
    // TODO: timeStyle
    // TODO: timeZone
    // TODO: skeleton

    // Set up DT options

    let mut dt_options = length::Bag::from_date_time_style(
        length::Date::Medium,
        length::Time::Short
    );
    
    let option_struct: DateTimeFormatOptions =
        serde_json::from_string(@options.to_string()).unwrap();
    
    // time input in ISO format.
    let input_string = &json_obj["input_string"].unwrap();
    
    let dtf = DateTimeFormatter::try_new(
        langid,
        dt_options.into(),
    )
        .expect("Failed to create DateTimeFormatter instance.");

    let datetime = DateTime::try_new_iso_datetime(2020, 9, 1, 12, 34, 28)
        .expect("Failed to construct DateTime.");
    let any_datetime = datetime.to_any();
    
    // Result to stdout.
    // TODO: get the date/time info from a skeleton.
    let result_string = dtf.format(&any_datetime).expect("should work");

    
    Ok(json!({
        "label": label,
        "result": result_string,
        "actual_options": format!("{option_struct:?}, {options:?}"),
    }))
        
}
