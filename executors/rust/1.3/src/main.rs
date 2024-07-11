// Read JSON test case from standard in.
// Parse to get test and parameters
// Run test
// Return results

// TODO:
// 3. Check compatibility of versions with data
// DONE 5. Move parameter extraction into function.
// 6. Fix NumberFormat with options
// 7. Clean up code
// 8. Decide on a repository structure
// DONE 9. Modularize into separate files for each type of test
// 10. Fix test_type and switch statement
// 11. Add language names

// References for ICU4X:
// https://unicode-org.github.io/icu4x-docs/doc/icu_collator/index.html

mod collator;
mod decimalfmt;
mod displaynames;
mod langnames;
mod likelysubtags;
mod listfmt;
mod numberfmt;
mod pluralrules;
mod relativedatetime_fmt;

use collator::run_collation_test;
use langnames::run_language_name_test;
use likelysubtags::run_likelysubtags_test;
use listfmt::run_list_fmt_test;
use numberfmt::run_numberformat_test;
use pluralrules::run_plural_rules_test;
use relativedatetime_fmt::run_relativedatetimeformat_test;

use serde_json::{json, Value};
use std::collections::HashMap;
use std::env;
use std::io;

// Read from stdin, call functions to get json, output the result.
fn main() -> io::Result<()> {
    env::set_var("RUST_BACKTRACE", "1");
    env_logger::init();
    log::info!("Welcome to the ICU4X Conformance Executor");

    // Supported tests names mapping to functions.
    // Use these strings to respond to test requests.
    let _supported_test_map = HashMap::from([
        ("collation_short".to_string(), run_collation_test), // TODO: ,("number_fmt".to_string(), run_numberformat_test)
    ]);

    // TODO: supported_test_map to call the functions.

    // TODO: Handle problem with
    // Error: Custom { kind: INvalidData, error: Error{"unexpected end of hex escape"
    // As in collation 000144, 0998, 0142
    let mut buffer = String::new();

    loop {
        let buffer_size = io::stdin().read_line(&mut buffer)?;
        if buffer_size == 0 {
            break;
        }
        if buffer.starts_with("#EXIT") {
            break;
        }
        if buffer.starts_with("#TESTS") {
            // Returns JSON list of supported tests.
            // TODO: let mut test_vec : Vec<&str> = supported_test_map.into_keys().collect();
            let json_result = json!(
                { "supported_tests": [
                    "collation_short",
                    "number_fmt",
                    "decimal_fmt",
                    "likelysubtags",
                    "list_fmt",
                    "plural_rules"
                ] }
            );
            println!("{}", json_result);
        }

        if buffer.starts_with("#VERSION") {
            let json_result = json!(
            {
                "platform": "ICU4X",
                "platformVersion": std::env!("CONFORMANCE_ICU4X_VERSION"),
                "icuVersion": std::env!("CONFORMANCE_ICU_VERSION"),
                "cldrVersion": std::env!("CONFORMANCE_CLDR_VERSION"),
            });
            println!("{}", json_result);
        } else {
            // Expecting test information as JSON data in a single line.

            //  https://stackoverflow.com/questions/30292752/how-do-i-parse-a-json-file
            let json_info: Value = serde_json::from_str(&buffer)?;

            let test_type: &str = json_info["test_type"].as_str().unwrap();
            let label: &str = json_info["label"].as_str().unwrap();

            // TODO!!! : supported_test_map to call the functions.
            let json_result = if test_type == "collation_short" {
                run_collation_test(&json_info)
            } else if (test_type == "decimal_fmt") || (test_type == "number_fmt") {
                run_numberformat_test(&json_info)
            } else if (test_type == "display_names")
                || (test_type == "language_display_name")
                || (test_type == "lang_names")
            {
                run_language_name_test(&json_info)
            } else if test_type == "likely_subtags" {
                run_likelysubtags_test(&json_info)
            } else if test_type == "list_fmt" {
                run_list_fmt_test(&json_info)
            } else if test_type == "plural_rules" {
                run_plural_rules_test(&json_info)
            } else if test_type == "rdt_fmt" {
                run_relativedatetimeformat_test(&json_info)
            } else {
                Err(test_type.to_string())
            };

            // Sends the result to stdout.
            match json_result {
                Ok(value) => println!("{}", value),
                Err(error_string) => println!(
                    "{}",
                    json!({"error": error_string,
                           "label": label,
                           "error_type": "unknown test type",
                           "error_detail": json_info})
                ),
            }
        }
        // Empty the input buffer
        buffer.clear();
    }

    Ok(())
}
