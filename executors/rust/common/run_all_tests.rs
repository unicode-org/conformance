// Read JSON test case from standard in.
// Parse to get test and parameters
// Run test
// Return results

// TODO:
// 3. Check compatibility of versions with data
// DONE 5. Move parameter extraction into function.
// 6. Fix NumberFormat with options
// 7. Clean up code
// 8. DONE Decide on a repository structure
// 9. DONE Modularize into separate files for each type of test
// 10. Fix test_type and switch statement
// 11. DONE Add language names --> locale names

// References for ICU4X:
// https://unicode-org.github.io/icu4x-docs/doc/icu_collator/index.html

use serde_json::{json, Value};
use std::env;
use std::io;

#[path = "../src/mod.rs"]
mod executors;

pub type ExecutorFn = fn(&Value) -> Result<Value, String>;

pub struct ExecutorFns {
    pub run_collation_test: ExecutorFn,
    pub run_datetimeformat_test: ExecutorFn,
    pub run_likelysubtags_test: ExecutorFn,
    pub run_list_fmt_test: ExecutorFn,
    pub run_locale_name_test: ExecutorFn,
    pub run_numberformat_test: ExecutorFn,
    pub run_plural_rules_test: ExecutorFn,
    pub run_relativedatetimeformat_test: ExecutorFn,
}

pub fn main() -> io::Result<()> {
    let executor_fns = ExecutorFns {
        run_collation_test: executors::collator::run_collation_test,
        run_datetimeformat_test: executors::datetimefmt::run_datetimeformat_test,
        run_likelysubtags_test: executors::likelysubtags::run_likelysubtags_test,
        run_list_fmt_test: executors::listfmt::run_list_fmt_test,
        run_locale_name_test: executors::localenames::run_locale_name_test,
        run_numberformat_test: executors::numberfmt::run_numberformat_test,
        run_plural_rules_test: executors::pluralrules::run_plural_rules_test,
        run_relativedatetimeformat_test: executors::relativedatetime_fmt::run_relativedatetimeformat_test,
    };
    run_all_tests(executor_fns)
}

// Read from stdin, call functions to get json, output the result.
pub fn run_all_tests(fns: ExecutorFns) -> io::Result<()> {
    env::set_var("RUST_BACKTRACE", "1");
    env_logger::init();
    log::info!("Welcome to the ICU4X Conformance Executor");

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
                (fns.run_collation_test)(&json_info)
            } else if (test_type == "decimal_fmt") || (test_type == "number_fmt") {
                (fns.run_numberformat_test)(&json_info)
            } else if (test_type == "display_names")
                || (test_type == "language_display_name")
                || (test_type == "lang_names")
            {
                (fns.run_locale_name_test)(&json_info)
            } else if test_type == "likely_subtags" {
                (fns.run_likelysubtags_test)(&json_info)
            } else if test_type == "list_fmt" {
                (fns.run_list_fmt_test)(&json_info)
            } else if test_type == "datetime_fmt" {
                (fns.run_datetimeformat_test)(&json_info)
            } else if test_type == "plural_rules" {
                (fns.run_plural_rules_test)(&json_info)
            } else if test_type == "rdt_fmt" {
                (fns.run_relativedatetimeformat_test)(&json_info)
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
