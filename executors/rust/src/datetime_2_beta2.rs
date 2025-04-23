// https://docs.rs/icu/1.3.2/icu/datetime/struct.DateTimeFormatter.html
// https://docs.rs/icu/1.3.2/icu/datetime/input/trait.TimeZoneInput.html
// https://docs.rs/ixdtf/latest/ixdtf/

use icu::calendar::cal::Iso;
use icu::datetime::fieldsets::builder::*;
use icu::datetime::input::ZonedDateTime;
use icu::datetime::options::*;
use icu::datetime::DateTimeFormatter;
use icu::datetime::DateTimeFormatterPreferences;
use icu::time::zone::UtcOffsetCalculator;

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

    semantic_skeleton: Option<String>,
    semantic_skeleton_length: Option<String>,
}

pub fn run_datetimeformat_test(json_obj: &Value) -> Result<Value, String> {
    let label = &json_obj["label"].as_str().unwrap();

    // If there are unsupported values, return
    // "unsupported" rather than an error.
    let options = &json_obj["options"]; // This will be an array.

    let option_struct: DateTimeFormatOptions = serde_json::from_str(&options.to_string()).unwrap();

    let skeleton_str = json_obj["semanticSkeleton"].as_str();

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
        None => match skeleton_str {
            Some("D" | "DT" | "DTZ") => Some(DateFields::D),
            Some("MD" | "MDT" | "MDTZ") => Some(DateFields::MD),
            Some("YMD" | "YMDT" | "YMDTZ") => Some(DateFields::YMD),
            Some("DE" | "DET" | "DETZ") => Some(DateFields::DE),
            Some("MDE" | "MDET" | "MDETZ") => Some(DateFields::MDE),
            Some("YMDE" | "YMDET" | "YMDETZ") => Some(DateFields::YMDE),
            Some("E" | "ET" | "ETZ") => Some(DateFields::E),
            Some("M") => Some(DateFields::M),
            Some("YM") => Some(DateFields::YM),
            Some("Y") => Some(DateFields::Y),
            Some("T" | "Z" | "TZ") => None,
            Some(other) => return Ok(json!({
                "label": label,
                "error_detail": format!("Unknown skeleton: {other}"),
                "error_type": format!("Unknown skeleton"),
            })),
            None => None,
        },
    };
    builder.time_precision = match option_struct.time_style.as_deref() {
        Some("full") => Some(TimePrecision::Second),
        Some("long") => Some(TimePrecision::Second),
        Some("medium") => Some(TimePrecision::Second),
        Some("short") => Some(TimePrecision::Minute),
        Some(other) => return Ok(json!({
            "label": label,
            "error_detail": format!("Unknown time style: {other}"),
            "error_type": format!("Unknown time style"),
        })),
        None => {
            if let Some(skeleton_str) = skeleton_str {
                if skeleton_str.contains("T") {
                    // TODO: The input should contain TimePrecision but it doesn't
                    Some(TimePrecision::Second)
                } else {
                    None
                }
            } else {
                None
            }
        },
    };
    builder.zone_style = match option_struct.time_style.as_deref() {
        Some("full") => Some(ZoneStyle::SpecificShort),
        Some("long") => Some(ZoneStyle::SpecificShort),
        Some("medium") => None,
        Some("short") => None,
        Some(other) => return Ok(json!({
            "label": label,
            "error_detail": format!("Unknown time style: {other}"),
            "error_type": format!("Unknown time style"),
        })),
        None => {
            if let Some(skeleton_str) = skeleton_str {
                if skeleton_str.contains("Z") {
                    // TODO: The input should contain ZoneStyle but it doesn't
                    Some(ZoneStyle::SpecificShort)
                } else {
                    None
                }
            } else {
                None
            }
        },
    };
    let field_set = match builder.build_composite() {
        Ok(field_set) => field_set,
        Err(e) => return Ok(json!({
            "label": label,
            "error_detail": format!("Couldn't build field set: {e}"),
            "error_type": format!("Invalid datetime fields or options"),
        }))
    };

    // Get ISO instant in UTC time zone
    let input_iso = &json_obj["original_input"].as_str().unwrap();

    // Workaround for https://github.com/unicode-org/icu4x/issues/6489
    let input_iso = input_iso.replace("Z[", "+00:00[");

    // Extract all the information we need from the string
    let parsed_zdt = super::try_or_return_error!(label, locale, {
        ZonedDateTime::try_loose_from_str(&input_iso, Iso, Default::default())
            .map_err(|e| format!("{e:?}"))
    });

    let input_zoned_date_time = ZonedDateTime {
        date: parsed_zdt.date,
        time: parsed_zdt.time,
        zone: parsed_zdt.zone.infer_zone_variant(&UtcOffsetCalculator::new()),
    };

    // The constructor is called with the given options
    // The default parameter is time zone formatter options. Not used yet.
    let dtf_result = DateTimeFormatter::try_new(preferences, field_set);

    let datetime_formatter = match dtf_result {
        Ok(dtf) => dtf,
        Err(e) => {
            return Ok(json!({
                "label": label,
                "error_detail": format!("{e:?}: {option_struct:?}"),
                "error_type": format!("Failed to create DateTimeFormatter instance"),
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
