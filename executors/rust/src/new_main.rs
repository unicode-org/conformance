// Read JSON test case from standard in.
// Parse to get test and parameters
// Run test
// Return results

// TODO:
// 1. Create results as JSON line
// 2. Get the version of ICU & CLDR data
// 3. Check compatibility
// 4. Evaluate speed - should this be an optimized output
// 5. Move parameter extraction into function.
// 6. Add NumberFormat test

use serde_json::{Value};
use std::io::{self};
use substring::Substring;

use core::cmp::Ordering;
use icu::collator::*;
use icu::locid::locale;

// Function runs comparison using collator
fn run_coll_test (
    string1: &str, string2: &str) -> bool {

    let data_provider = icu_testdata::get_provider();

    let coll_options = CollatorOptions::new();

    let collator: Collator =
        Collator::try_new_unstable(
            &data_provider,
            &locale!("en").into(),
            coll_options).unwrap();
    
    let result = collator.compare(&string1, &string2);
    return result == Ordering::Less;
}


// Prints to stdout with result of comparing two strings
fn run_coll_test2(coll_json: serde_json) -> &str {
    let str1 : &str= &coll_json["string1"].to_string();
    let str2 : &str= &coll_json["string2"].to_string();
    
    let result : bool = run_coll_test(str1, str2);
    if result == true {
        print!("{}\"label\": {}, \"result\": \"{}\"{}",
               "{", label, result, "}");
        // println!(" \{\"label\": \"{}\", \"result": \"{}\"", label, result);
    } else {
        print!(
            "{}\"label\": {}, \"result\": \"{}\", \"string1\": {}, \"string2\":{}{}",
            "{", label, result, str1, str2, "}");
    }
}

// Runs number formatting given patterns or skeletons
fn run_numberformat_test() {
}

// Trying to read from stdin, outputting the number of chars to stdout.
fn main() -> io::Result<()> {
    let mut buffer = String::new();
    io::stdin().read_line(&mut buffer)?;

    // println!("RUST: {}", buffer);

    if &buffer.substring(0, 1) == &"#" {
        println!("INFO: {}", buffer);

        // !!! PackageMetadata
        // let pkg_meta_data : icu_testdata::metadata::PackageMetadata =
        let info = icu_testdata::metadata::load().unwrap();
        let cldr_version =
            &info.package_metadata.cldr_json_gitref;
        println!("CLDR INFO: {}", cldr_version);
        
    } else {
        //  https://stackoverflow.com/questions/30292752/how-do-i-parse-a-json-file
        let parsed : Value = serde_json::from_str(&buffer)?;
        
        let label = &parsed["label"].to_string();
        
        let test_pos = label.find(&"coll_shift_short_");
        let is_collation_test : bool = test_pos != None;
        // Extract id
        // let v: Vec<&str> = label.rsplit(&"_").collect();
        
        let str1 : &str= &parsed["string1"].to_string();
        let str2 : &str= &parsed["string2"].to_string();
        if is_collation_test {
            let result : bool = run_coll_test(str1, str2);
            if result == true {
                print!("{}\"label\": {}, \"result\": \"{}\"{}",
                         "{", label, result, "}");
                // println!(" \{\"label\": \"{}\", \"result": \"{}\"", label, result);
            } else {
                print!(
                    "{}\"label\": {}, \"result\": \"{}\", \"string1\": {}, \"string2\":{}{}",
                         "{", label, result, str1, str2, "}");
            }
        }
    }

    // Try adding new field
    // TODO!! parsed.insert("result", is_collation_test);

    Ok(())
}
