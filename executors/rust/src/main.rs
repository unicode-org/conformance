// Read JSON test case from standard in.
// Parse to get test and parameters
// Run test
// Return results

// TODO:
// 3. Check compatibility of versions with data
// DONE 5. Move parameter extraction into function.
// 6. Add NumberFormat test
// 7. Clean up code
// 8. Decide on a repository structure
// 9. Modularize into separate files for each type of test
// 10. Fix test_type and switch statement

// References for ICU4X:
// https://unicode-org.github.io/icu4x-docs/doc/icu_collator/index.html

mod collator;
mod numberfmt;

use serde_json::{json, Value};

use std::env;
use std::io::{self};
use std::panic;

use substring::Substring;

// Test modules for each type
use collator::run_coll_test;

use numberfmt::run_numberformat_test;

// Read from stdin, call functions to get json, output the result.
fn main() -> io::Result<()> {
    env::set_var("RUST_BACKTRACE", "1");
    env_logger::init();
    log::info!("Welcome to the ICU4X Conformance Executor");

    let mut buffer = String::new();

    loop {
        let buffer_size = io::stdin().read_line(&mut buffer)?;
        if buffer_size == 0 {
            break;
        }
        if buffer.substring(0, 5) == "#EXIT" {
            break;
        }
        if buffer.substring(0, 8) == "#VERSION" {
            // Get data version information from PackageMetadata
            // https://crates.io/crates/rustc_version_runtime
            // https://github.com/serde-rs/json

            // These fail when executed by testDriver.py
            // https://doc.rust-lang.org/std/panic/fn.catch_unwind.html
            let check_icu_info = panic::catch_unwind(|| {
                icu_testdata::versions::icu_tag();
            });

            if check_icu_info.is_ok() {
                let icu_version = &icu_testdata::versions::icu_tag();
                let cldr_version = &icu_testdata::versions::cldr_tag();

                let json_result = json!(
                {
                    "platform": "rust",
                    "platformVersion": rustc_version_runtime::version().to_string(),
                    "icuVersion": icu_version,
                    "cldrVersion": cldr_version,
                });
                println!("{}", json_result);
            } else {
                let json_result = json!(
                    {
                        "platform": "rust",
                        "platformVersion":
                        rustc_version_runtime::version().to_string(),
                        "icuVersion": "unknown",
                        "cldrVersion": "unknown",
                    }
                );
                log::debug!("# RESULT returned = {}", json_result.to_string());
                println!("{}", json_result);
            }
        } else {
            // Expecting test information as JSON data in a single line.

            //  https://stackoverflow.com/questions/30292752/how-do-i-parse-a-json-file
            let json_info: Value = serde_json::from_str(&buffer)?;

            let test_type: &str = json_info["test_type"].as_str().unwrap();
            let label: &str = json_info["label"].as_str().unwrap();

            let json_result = if test_type == "coll_shift_short" {
                // TODO: Get the json result and print here
                run_coll_test(&json_info)
            } else if (test_type == "decimal_fmt") || (test_type == "number_fmt") {
                // TODO: Get the json result and print here
                run_numberformat_test(&json_info)
            } else {
                Err(test_type.to_string())
            };
            match json_result {
                Ok(value) => println!("{}", value),
                Err(s) => println!(
                    "{}",
                    json!({"error": s, "label": label,
                           "type": "unknown test type",
                           "received_info": json_info})
                ),
            }
        }
        // Empty the input buffer
        buffer.clear();
    }

    Ok(())
}
