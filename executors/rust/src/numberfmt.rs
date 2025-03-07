//! Executor provides tests for NumberFormat and DecimalFormat.

use fixed_decimal::FixedDecimal;
use fixed_decimal::SignDisplay;
// TODO: use fixed_decimal::ScientificDecimal;

use super::compat::{pref, unicode, Locale};
use icu::decimal::options;
use icu::decimal::FixedDecimalFormatter;

use serde::{Deserialize, Serialize};
use serde_json::{json, Value};

use writeable::Writeable;

#[cfg(any(ver = "1.3", ver = "1.4"))]
use icu::compactdecimal::CompactDecimalFormatter;

#[cfg(any(ver = "1.5", ver = "2.0-beta1"))]
use icu::experimental::compactdecimal::CompactDecimalFormatter;

// Support options - update when ICU4X adds support
static _SUPPORTED_OPTIONS: [&str; 6] = [
    "compactDisplay",
    "minimumIntegerDigits",
    "maximumIntegerDigits",
    "minimumFractionDigits",
    "maximumFractionDigits",
    "roundingMode",
];

#[derive(Deserialize, Serialize, Debug)]
#[serde(rename_all = "camelCase")]
struct NumberFormatOptions {
    compact_display: Option<String>,
    currency_display: Option<String>,
    currency_sign: Option<String>,
    maximum_fraction_digits: Option<u8>,
    maximum_integer_digits: Option<u8>,
    maximum_significant_digits: Option<u8>,
    minimum_fraction_digits: Option<u8>,
    minimum_integer_digits: Option<u8>,
    minimum_significant_digits: Option<u8>,
    notation: Option<String>,
    numbering_system: Option<String>,
    rounding_mode: Option<String>,
    sign_display: Option<String>,
    style: Option<String>,
    unit: Option<String>,
    unit_display: Option<String>,
    use_grouping: Option<bool>,
    // unsupported options with special labels for conformance
    conformance_scale: Option<String>,
    conformance_decimal_always: Option<bool>,
}

// Runs decimal and number formatting given patterns or skeletons.
pub fn run_numberformat_test(json_obj: &Value) -> Result<Value, String> {
    let label = &json_obj["label"].as_str().unwrap();

    // Default locale if not specified.
    let mut langid: Locale = json_obj
        .get("locale")
        .map(|locale_name| locale_name.as_str().unwrap().parse().unwrap())
        .unwrap_or_default();

    let input = &json_obj["input"].as_str().unwrap();

    // If there are unsupported values, return
    // "unsupported" rather than an error.
    let options = &json_obj["options"]; // This will be an array.

    let mut _unsupported_options: Vec<&str> = Vec::new();

    // If any option is not yet supported, should we report as UNSUPPORTED?
    let option_struct: NumberFormatOptions = serde_json::from_str(&options.to_string()).unwrap();
    let mut is_compact = false;
    let mut compact_type = "";
    let mut is_scientific = false;
    let mut _rounding_mode = "";
    let mut style = "";
    let mut unit = "";
    if option_struct.notation == Some(String::from("compact")) {
        is_compact = true;
    }
    if option_struct.compact_display.is_some() {
        compact_type = option_struct.compact_display.as_ref().unwrap();
    }
    if option_struct.notation == Some(String::from("scientific")) {
        is_scientific = true;
    }
    if option_struct.style.is_some() {
        style = option_struct.style.as_ref().unwrap();
    }
    if option_struct.unit.is_some() {
        unit = option_struct.unit.as_ref().unwrap();
    }
    if option_struct.rounding_mode.is_some() {
        _rounding_mode = option_struct.rounding_mode.as_ref().unwrap();
    }
    let mut options: options::FixedDecimalFormatterOptions = Default::default();
    // TODO: Use options to call operations including pad and trunc with rounding.

    // !! A test. More options to consider!
    match option_struct.use_grouping {
        Some(true) => options.grouping_strategy = options::GroupingStrategy::Always,
        Some(false) => options.grouping_strategy = options::GroupingStrategy::Never,
        _ => options.grouping_strategy = options::GroupingStrategy::Auto,
    }

    // --------------------------------------------------------------------------------

    // UNSUPPORTED THINGS.
    // This will change with new additions to ICU4X.
    if style == "unit"
        || style == "currency"
        || unit == "percent"
        || is_scientific
        || option_struct.minimum_significant_digits.is_some()
        || option_struct.maximum_significant_digits.is_some()
        || option_struct.conformance_scale.is_some()
        || option_struct.conformance_decimal_always.is_some()
        || (is_compact
            && (option_struct.minimum_fraction_digits.is_some()
                || option_struct.maximum_fraction_digits.is_some()
                || option_struct.minimum_integer_digits.is_some()
                || option_struct.maximum_integer_digits.is_some()
                || option_struct.rounding_mode.is_some()
                || option_struct.sign_display.is_some()))
    {
        return Ok(json!({
            "label": label,
            "error_detail": {"style": style,
                             "unit": unit,
                             "scientific": is_scientific},
            "unsupported": "unit or style not implemented",
            "error_type": "unsupported",
        }));
    }
    // --------------------------------------------------------------------------------

    if let Some(numsys) = option_struct.numbering_system.as_ref() {
        langid
            .extensions
            .unicode
            .keywords
            .set(unicode::key!("nu"), numsys.parse().unwrap());
    }

    // Returns error if parsing the number string fails.
    let mut input_num = input.parse::<FixedDecimal>().map_err(|e| e.to_string())?;

    let result_string = if is_compact {
        // We saw compact!
        let cdf = super::try_or_return_error!(label, langid, {
            if compact_type == "short" {
                CompactDecimalFormatter::try_new_short(pref!(&langid), Default::default())
            } else {
                println!("#{:?}", "   LONG");
                CompactDecimalFormatter::try_new_long(pref!(&langid), Default::default())
            }
        });
        // input.parse().map_err(|e| e.to_string())?;

        let input_num = input.parse::<FixedDecimal>().map_err(|e| e.to_string())?;
        let formatted_cdf = cdf.format_fixed_decimal(input_num);
        formatted_cdf.write_to_string().into_owned()
    // }
    // else if is_scientific {
    //     let mut sci_decimal = input.parse::<ScientificDecimal>().map_err(|e| e.to_string());
    //     // TEMPORARY
    } else {
        // FixedDecimal
        let fdf = super::try_or_return_error!(label, langid, {
            FixedDecimalFormatter::try_new(pref!(&langid), options.clone())
        });

        // Apply relevant options for digits.
        if let Some(x) = option_struct.maximum_fraction_digits {
            #[cfg(any(ver = "1.3", ver = "1.4", ver = "1.5"))]
            match option_struct.rounding_mode.as_deref() {
                Some("ceil") => input_num.ceil(-(x as i16)),
                Some("floor") => input_num.floor(-(x as i16)),
                Some("expand") => input_num.expand(-(x as i16)),
                Some("trunc") => input_num.trunc(-(x as i16)),
                Some("halfCeil") => input_num.half_ceil(-(x as i16)),
                Some("halfFloor") => input_num.half_floor(-(x as i16)),
                Some("halfExpand") => input_num.half_expand(-(x as i16)),
                Some("halfTrunc") => input_num.half_trunc(-(x as i16)),
                Some("halfEven") => input_num.half_even(-(x as i16)),
                _ => input_num.half_even(-(x as i16)),
            };
            #[cfg(not(any(ver = "1.3", ver = "1.4", ver = "1.5")))]
            input_num.round_with_mode(
                -(x as i16),
                match option_struct.rounding_mode.as_deref() {
                    Some("ceil") => fixed_decimal::RoundingMode::Ceil,
                    Some("floor") => fixed_decimal::RoundingMode::Floor,
                    Some("expand") => fixed_decimal::RoundingMode::Expand,
                    Some("trunc") => fixed_decimal::RoundingMode::Trunc,
                    Some("halfCeil") => fixed_decimal::RoundingMode::HalfCeil,
                    Some("halfFloor") => fixed_decimal::RoundingMode::HalfFloor,
                    Some("halfExpand") => fixed_decimal::RoundingMode::HalfExpand,
                    Some("halfTrunc") => fixed_decimal::RoundingMode::HalfTrunc,
                    Some("halfEven") => fixed_decimal::RoundingMode::HalfEven,
                    _ => fixed_decimal::RoundingMode::HalfEven,
                },
            );
            input_num.trim_end();
        }
        if let Some(x) = option_struct.minimum_fraction_digits {
            input_num.pad_end(-(x as i16));
        }
        if let Some(x) = option_struct.maximum_integer_digits {
            input_num.set_max_position(x as i16);
            input_num.trim_start();
        }
        if let Some(x) = option_struct.minimum_integer_digits {
            input_num.pad_start(x as i16);
        }

        let sign_display = match option_struct.sign_display.as_deref() {
            Some("auto") => Some(SignDisplay::Auto),
            Some("never") => Some(SignDisplay::Never),
            Some("always") => Some(SignDisplay::Always),
            Some("exceptZero") => Some(SignDisplay::ExceptZero),
            Some("negative") => Some(SignDisplay::Negative),
            _ => None,
        };
        if let Some(sign_display) = sign_display {
            input_num.apply_sign_display(sign_display);
        }

        // Apply the options and get formatted string.
        fdf.format_to_string(&input_num)
    };

    // Result to stdout.
    Ok(json!({
        "label": label,
        "result": result_string,
        "actual_options": format!("{option_struct:?}, {options:?}"),
    }))
}
