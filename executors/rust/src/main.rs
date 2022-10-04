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
// !!! use std::io::{self, Write};
use substring::Substring;

// Test modules for each type
use collator::run_coll_test;

use numberfmt::run_numberformat_test;

// Ead from stdin, call function, output the result.
fn main() -> io::Result<()> {
    env::set_var("RUST_BACKTRACE", "1");

    let mut buffer = String::new();

    loop {
        io::stdin().read_line(&mut buffer).unwrap(); // ?

        // DEBUG: println!("# BUFFER received = {}", buffer);
        if buffer.len() <= 0 {
            continue;
        }
        if &buffer.substring(0, 5) == &"#EXIT" {
            break;
        }
        if &buffer.substring(0, 8) == &"#VERSION" {
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
                // !!io::stdout().write_all(&json_result.to_string());
                println!("{}", json_result.to_string());
            } else {
                let json_result = json!(
                    {
                        "platform": "rust",
                        "platformVersion": rustc_version_runtime::version().to_string(),
                        "icuVersion": "unknown",
                        "cldrVersion": "unknown",
                    }
                );
                // io::stdout().write_all(&json_result.to_string());
                println!("RESULT{}", json_result.to_string());
            }
        } else {
            // Test data expected in form of JSON data in a single line.

            //  https://stackoverflow.com/questions/30292752/how-do-i-parse-a-json-file
            let json_info: Value = serde_json::from_str(&buffer)?;

            let test_type: &str = &json_info["test_type"].as_str().unwrap();

            if test_type == "coll_shift_short" {
                run_coll_test(&json_info);
            } else if (test_type == "decimal_fmt") ||
                (test_type == "number_fmt") {
                run_numberformat_test(&json_info);
            } else {
                println!("# NO CASE FOR test_type: {}", test_type);
            }
            // TODO: The output should be done from the main routine, not
            // individual routines.
        }

        // Empty the input buffer
        buffer.clear();
    }
    println!("");

    Ok(())
}
