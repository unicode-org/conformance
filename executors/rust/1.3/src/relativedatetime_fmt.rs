// https://docs.rs/icu/1.3.2/icu/relativetime/struct.RelativeTimeFormatter.html

use fixed_decimal::FixedDecimal;
use icu::locid::Locale;
use icu_provider::DataLocale;

use icu::relativetime::options::Numeric;
use icu::relativetime::{RelativeTimeError, RelativeTimeFormatter, RelativeTimeFormatterOptions};

use serde::{Deserialize, Serialize};
use serde_json::{json, Value};

#[derive(Deserialize, Serialize, Debug)]
#[serde(rename_all = "camelCase")]
struct RelativeDateTimeFormatterOptions {
    style: Option<String>,
    numbering_system: Option<String>,
    numeric: Option<String>,
}

fn get_formatter_from_unit_style(
    locale: &DataLocale,
    unit: String,
    style: String,
    options: RelativeTimeFormatterOptions,
) -> Result<RelativeTimeFormatter, RelativeTimeError> {
    if unit == "year" {
        if style == "long" {
            RelativeTimeFormatter::try_new_long_year(locale, options)
        } else if style == "short" {
            RelativeTimeFormatter::try_new_short_year(locale, options)
        } else if style == "narrow" {
            RelativeTimeFormatter::try_new_narrow_year(locale, options)
        } else {
            // Assume long
            RelativeTimeFormatter::try_new_long_year(locale, options)
        }
    } else if unit == "quarter" {
        if style == "long" {
            RelativeTimeFormatter::try_new_long_quarter(locale, options)
        } else if style == "short" {
            RelativeTimeFormatter::try_new_short_quarter(locale, options)
        } else if style == "narrow" {
            RelativeTimeFormatter::try_new_narrow_quarter(locale, options)
        } else {
            // Assume long
            RelativeTimeFormatter::try_new_long_quarter(locale, options)
        }
    } else if unit == "month" {
        if style == "long" {
            RelativeTimeFormatter::try_new_long_month(locale, options)
        } else if style == "short" {
            RelativeTimeFormatter::try_new_short_month(locale, options)
        } else if style == "narrow" {
            RelativeTimeFormatter::try_new_narrow_month(locale, options)
        } else {
            // Assume long
            RelativeTimeFormatter::try_new_long_month(locale, options)
        }
    } else if unit == "week" {
        if style == "long" {
            RelativeTimeFormatter::try_new_long_week(locale, options)
        } else if style == "short" {
            RelativeTimeFormatter::try_new_short_week(locale, options)
        } else if style == "narrow" {
            RelativeTimeFormatter::try_new_narrow_week(locale, options)
        } else {
            // Assume long
            RelativeTimeFormatter::try_new_long_week(locale, options)
        }
    } else if unit == "day" {
        if style == "long" {
            RelativeTimeFormatter::try_new_long_day(locale, options)
        } else if style == "short" {
            RelativeTimeFormatter::try_new_short_day(locale, options)
        } else if style == "narrow" {
            RelativeTimeFormatter::try_new_narrow_day(locale, options)
        } else {
            // Assume long
            RelativeTimeFormatter::try_new_long_day(locale, options)
        }
    } else if unit == "hour" {
        if style == "long" {
            RelativeTimeFormatter::try_new_long_hour(locale, options)
        } else if style == "short" {
            RelativeTimeFormatter::try_new_short_hour(locale, options)
        } else if style == "narrow" {
            RelativeTimeFormatter::try_new_narrow_hour(locale, options)
        } else {
            // Assume long
            RelativeTimeFormatter::try_new_long_hour(locale, options)
        }
    } else if unit == "minute" {
        if style == "long" {
            RelativeTimeFormatter::try_new_long_minute(locale, options)
        } else if style == "short" {
            RelativeTimeFormatter::try_new_short_minute(locale, options)
        } else if style == "narrow" {
            RelativeTimeFormatter::try_new_narrow_minute(locale, options)
        } else {
            // Assume long
            RelativeTimeFormatter::try_new_long_minute(locale, options)
        }
    } else if unit == "second" {
        if style == "long" {
            RelativeTimeFormatter::try_new_long_second(locale, options)
        } else if style == "short" {
            RelativeTimeFormatter::try_new_short_second(locale, options)
        } else if style == "narrow" {
            RelativeTimeFormatter::try_new_narrow_second(locale, options)
        } else {
            // Assume long
            RelativeTimeFormatter::try_new_long_second(locale, options)
        }
    } else {
        // An unknown unit!
        RelativeTimeFormatter::try_new_narrow_second(locale, options)
    }
}

pub fn run_relativedatetimeformat_test(json_obj: &Value) -> Result<Value, String> {
    let label = &json_obj["label"].as_str().unwrap();

    // If there are unsupported values, return
    // "unsupported" rather than an error.
    let options = &json_obj["options"]; // This will be an array.

    let option_struct: RelativeDateTimeFormatterOptions =
        serde_json::from_str(&options.to_string()).unwrap();

    let numbering_system_str = &option_struct.numbering_system;

    let locale_json_str: &str = json_obj["locale"].as_str().unwrap();
    let mut locale_str: String = locale_json_str.to_string();

    if numbering_system_str.is_some() {
       let numbering_system = numbering_system_str.as_ref().unwrap();
       locale_str =
            locale_json_str.to_string() + "-u-nu-" + numbering_system;

        // TODO: update when ICU4X supports numbering systems.
        if numbering_system != "latn" {
            return Ok(json!({
                "error": "Number system not supported",
                "error_msg": numbering_system,
                "label": label,
                "unsupported": "non-Latn numbering system",
            }));
        }
    }

    let lang_id = if let Ok(lc) = locale_str.parse::<Locale>() {
        lc
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

    let unit: &str = json_obj["unit"].as_str().unwrap();

    let mut style = "";
    if option_struct.style.is_some() {
        style = option_struct.style.as_ref().unwrap();
    }

    // Get numeric option
    let options = if option_struct.numeric == Some(String::from("auto")) {
        RelativeTimeFormatterOptions {
            numeric: Numeric::Auto,
        }
    } else {
        // The default
        RelativeTimeFormatterOptions {
            numeric: Numeric::Always,
        }
    };

    // Use unit & style to select the correct constructor.
    let relative_time_formatter =
        get_formatter_from_unit_style(&data_locale, unit.to_string(), style.to_string(), options);

    let formatter = match relative_time_formatter {
        Ok(formatter) => formatter,
        Err(error) => {
            return Ok(json!({
                "error": "Cannot create formatter",
                "error_msg": error.to_string(),
                "label": label,
            }));
        }
    };

    let formatted_result = formatter.format(count.clone());
    let result_string = formatted_result.to_string();
    Ok(json!({
        "label": label,
        "result": result_string,
        "actual_options": format!("{data_locale:?}"),
    }))
}
