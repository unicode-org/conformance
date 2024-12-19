// Read JSON test case from standard in.
// Parse to get test and parameters
// Run test
// Return results

use std::io;

mod collator;
// mod datetimefmt;
mod decimalfmt;
mod displaynames;
mod likelysubtags;
mod listfmt;
mod localenames;
mod numberfmt;
mod pluralrules;
mod relativedatetime_fmt;

#[path = "../../common/try_or_return_error.rs"]
#[macro_use]
mod try_or_return_error;

pub fn return_error(json_obj: &serde_json::Value) -> Result<serde_json::Value, String> {
    let label = &json_obj["label"].as_str().unwrap();
    return Ok(serde_json::json!({
        "label": label,
        "error_type": "datetime ignored",
        "error": "datetime ignored"
    }));
}

#[path = "../../common/run_all_tests.rs"]
mod run_all_tests;

fn main() -> io::Result<()> {
    let executor_fns = run_all_tests::ExecutorFns {
        run_collation_test: collator::run_collation_test,
        run_datetimeformat_test: return_error,
        // run_datetimeformat_test: datetimefmt::run_datetimeformat_test,
        run_likelysubtags_test: likelysubtags::run_likelysubtags_test,
        run_list_fmt_test: listfmt::run_list_fmt_test,
        run_locale_name_test: localenames::run_locale_name_test,
        run_numberformat_test: numberfmt::run_numberformat_test,
        run_plural_rules_test: pluralrules::run_plural_rules_test,
        run_relativedatetimeformat_test: relativedatetime_fmt::run_relativedatetimeformat_test,
    };
    run_all_tests::main(executor_fns)
}
