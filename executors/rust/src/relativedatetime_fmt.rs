// https://docs.rs/icu/1.3.2/icu/relativetime/struct.RelativeTimeFormatter.html
// https://docs.rs/icu_provider/1.3.0/icu_provider/struct.DataLocale.html#method.get_unicode_ext

use fixed_decimal::FixedDecimal;

use super::compat::{pref, unicode, unicode::key, Locale};

use std::str::FromStr;

#[cfg(any(ver = "1.3", ver = "1.4"))]
use icu::relativetime::{options::Numeric, *};

#[cfg(any(ver = "1.5", ver = "2.0-beta1"))]
use icu::experimental::relativetime::{options::Numeric, *};

#[cfg(any(ver = "1.3", ver = "1.4", ver = "1.5"))]
type Error = RelativeTimeError;

#[cfg(not(any(ver = "1.3", ver = "1.4", ver = "1.5")))]
type Error = icu_provider::DataError;

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
    locale: &Locale,
    unit: String,
    style: String,
    options: RelativeTimeFormatterOptions,
) -> Result<RelativeTimeFormatter, Error> {
    let prefs = pref!(locale);
    if unit == "year" {
        if style == "long" {
            RelativeTimeFormatter::try_new_long_year(prefs, options)
        } else if style == "short" {
            RelativeTimeFormatter::try_new_short_year(prefs, options)
        } else if style == "narrow" {
            RelativeTimeFormatter::try_new_narrow_year(prefs, options)
        } else {
            // Assume long
            RelativeTimeFormatter::try_new_long_year(prefs, options)
        }
    } else if unit == "quarter" {
        if style == "long" {
            RelativeTimeFormatter::try_new_long_quarter(prefs, options)
        } else if style == "short" {
            RelativeTimeFormatter::try_new_short_quarter(prefs, options)
        } else if style == "narrow" {
            RelativeTimeFormatter::try_new_narrow_quarter(prefs, options)
        } else {
            // Assume long
            RelativeTimeFormatter::try_new_long_quarter(prefs, options)
        }
    } else if unit == "month" {
        if style == "long" {
            RelativeTimeFormatter::try_new_long_month(prefs, options)
        } else if style == "short" {
            RelativeTimeFormatter::try_new_short_month(prefs, options)
        } else if style == "narrow" {
            RelativeTimeFormatter::try_new_narrow_month(prefs, options)
        } else {
            // Assume long
            RelativeTimeFormatter::try_new_long_month(prefs, options)
        }
    } else if unit == "week" {
        if style == "long" {
            RelativeTimeFormatter::try_new_long_week(prefs, options)
        } else if style == "short" {
            RelativeTimeFormatter::try_new_short_week(prefs, options)
        } else if style == "narrow" {
            RelativeTimeFormatter::try_new_narrow_week(prefs, options)
        } else {
            // Assume long
            RelativeTimeFormatter::try_new_long_week(prefs, options)
        }
    } else if unit == "day" {
        if style == "long" {
            RelativeTimeFormatter::try_new_long_day(prefs, options)
        } else if style == "short" {
            RelativeTimeFormatter::try_new_short_day(prefs, options)
        } else if style == "narrow" {
            RelativeTimeFormatter::try_new_narrow_day(prefs, options)
        } else {
            // Assume long
            RelativeTimeFormatter::try_new_long_day(prefs, options)
        }
    } else if unit == "hour" {
        if style == "long" {
            RelativeTimeFormatter::try_new_long_hour(prefs, options)
        } else if style == "short" {
            RelativeTimeFormatter::try_new_short_hour(prefs, options)
        } else if style == "narrow" {
            RelativeTimeFormatter::try_new_narrow_hour(prefs, options)
        } else {
            // Assume long
            RelativeTimeFormatter::try_new_long_hour(prefs, options)
        }
    } else if unit == "minute" {
        if style == "long" {
            RelativeTimeFormatter::try_new_long_minute(prefs, options)
        } else if style == "short" {
            RelativeTimeFormatter::try_new_short_minute(prefs, options)
        } else if style == "narrow" {
            RelativeTimeFormatter::try_new_narrow_minute(prefs, options)
        } else {
            // Assume long
            RelativeTimeFormatter::try_new_long_minute(prefs, options)
        }
    } else if unit == "second" {
        if style == "long" {
            RelativeTimeFormatter::try_new_long_second(prefs, options)
        } else if style == "short" {
            RelativeTimeFormatter::try_new_short_second(prefs, options)
        } else if style == "narrow" {
            RelativeTimeFormatter::try_new_narrow_second(prefs, options)
        } else {
            // Assume long
            RelativeTimeFormatter::try_new_long_second(prefs, options)
        }
    } else {
        // An unknown unit!
        RelativeTimeFormatter::try_new_narrow_second(prefs, options)
    }
}

pub fn run_relativedatetimeformat_test(json_obj: &Value) -> Result<Value, String> {
    let label = &json_obj["label"].as_str().unwrap();

    // If there are unsupported values, return
    // "unsupported" rather than an error.
    let options = &json_obj["options"]; // This will be an array.

    let option_struct: RelativeDateTimeFormatterOptions =
        serde_json::from_str(&options.to_string()).unwrap();

    let numbering_system_str: &Option<String> = &option_struct.numbering_system;

    // Set up the locale with its options.
    let locale_json_str: &str = json_obj["locale"].as_str().unwrap();
    let locale_str: String = locale_json_str.to_string();

    let locale_id = if let Ok(lc) = locale_str.parse::<Locale>() {
        lc
    } else {
        return Ok(json!({
            "label": label,
            "error_detail": {"locale": locale_str},
            "error_type": "locale problem",
        }));
    };

    let mut locale = Locale::from(locale_id);

    if numbering_system_str.is_some() {
        let numbering_system: &String = numbering_system_str.as_ref().unwrap();

        // Set up the numbering system in the locale.
        locale.extensions.unicode.keywords.set(
            key!("nu"),
            unicode::Value::from_str(numbering_system).unwrap(),
        );

        // TODO: update when ICU4X supports numbering systems.
        // Note that "actual_options" returns the expanded locale,
        // e.g., "actual_options":"DataLocale{en-US-u-nu-arab}"
        if numbering_system != "latn" {
            return Ok(json!({
                "error": "Number system not supported",
                "error_msg": numbering_system,
                "error_detail": {"locale": format!("{locale:?}")},                "label": label,
                "unsupported": "non-Latn numbering system",
            }));
        }
    }

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
        get_formatter_from_unit_style(&locale, unit.to_string(), style.to_string(), options);

    let formatter = match relative_time_formatter {
        Ok(formatter) => formatter,
        Err(error) => {
            return Ok(json!({
                "error": "Cannot create formatter",
                "error_msg": error.to_string(),
                "error_detail": {"locale": format!("{locale:?}")},
                "label": label,
            }));
        }
    };

    let formatted_result = formatter.format(count.clone());
    let result_string = formatted_result.to_string();
    Ok(json!({
        "label": label,
        "result": result_string,
        "actual_options": format!("{locale:?}"),
    }))
}
