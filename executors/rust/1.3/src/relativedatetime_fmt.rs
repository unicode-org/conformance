 // https://docs.rs/icu/1.3.2/icu/datetime/struct.DateTimeFormatter.html

use icu::calendar::DateTime;
use icu::calendar::{buddhist::Buddhist,
                    chinese::Chinese,
                    coptic::Coptic,
                    dangi::Dangi,
                    ethiopian::Ethiopian,
                    gregory::Gregorian,
                    hebrew::Hebrew,
                    indian::Indian,
                    iso::Iso,
                    japanese::Japanese,
                    julian::Julian,
                    persian::Persian,
                    roc::Roc,
                    Date};

use icu::datetime::{options::length, DateTimeFormatter};
// use icu::datetime::input::DateTimeInput;
use icu_provider::DataLocale;

use icu::locid::Locale;

use serde_json::{json, Value};
use serde::{Deserialize,Serialize};

#[derive(Deserialize, Serialize, Debug)]
#[serde(rename_all = "camelCase")]
struct RDTFormatOptions {
    calendar: Option<String>,
    numbering_system: Option<String>
}

pub fn run_relativedatetimeformat_test(json_obj: &Value) -> Result<Value, String> {
    let label = &json_obj["label"].as_str().unwrap();
    
    // If there are unsupported values, return
    // "unsupported" rather than an error.
    let options = &json_obj["options"]; // This will be an array.

    let option_struct: RDTFormatOptions = serde_json::from_str(&options.to_string()).unwrap();
    let numbering_system_str = &option_struct.numbering_system;

    let locale_json_str: &str = json_obj["locale"].as_str().unwrap();
    let mut locale_str: String = locale_json_str.to_string();
    if numbering_system_str.is_some() {
        locale_str = locale_json_str.to_string() + "-u-nu-" +
            &numbering_system_str.as_ref().unwrap();
    }

    let langid: Locale = json_obj
        .get("locale")
        .map(|locale_name| local_str)
        .unwrap_or_default();

    let data_locale = DataLocale::from(langid);

    // 
    let mut _unsupported_options: Vec<&str> = Vec::new();

    // handle options - maybe done?
    
    // Set up DT options
    let dt_options = length::Bag::from_date_time_style(
        length::Date::Medium,
        length::Time::Short
    );
    
    let option_struct: DateTimeFormatOptions =
        serde_json::from_str(&options.to_string()).unwrap();
    
    // TODO: !!! time input in ISO format.
    // let input_string = &json_obj["input_string"].as_str().unwrap();

    // let iso_input = DateTime::try_new_iso_datetime(input_string);

    let dtf = DateTimeFormatter::try_new(
        &data_locale,
        dt_options.into(),
    )
        .expect("Failed to create DateTimeFormatter instance.");

    // !!! TEMPORARY !
    let date_iso = DateTime::try_new_iso_datetime(2020, 9, 1, 12, 34, 28)
        .expect("Failed to construct DateTime.");
    let any_datetime = date_iso.to_any();

    // !!! Calendar.
    let calendar_type = gregorian;
    let calendar_date = date_iso.to_calendar(calendar_type);

    // Result to stdout.
    // TODO: get the date/time info from a skeleton.
    let formatted_dt = dtf.format(&any_datetime).expect("should work");
    let result_string = formatted_dt.to_string();
    
    Ok(json!({
        "label": label,
        "result": result_string,
        "actual_options": format!("{option_struct:?}, {options:?}, {locale_str:?}"),
    }))
        
}
