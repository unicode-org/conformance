// Read JSON test case from standard in.
// Parse to get test and parameters
// Run test
// Return results

use std::io;

mod icu {
    pub use ::icu::compactdecimal;
    pub use ::icu::displaynames;
    pub use ::icu::relativetime;
}

mod collator;
mod datetimefmt;
mod decimalfmt;
mod displaynames;
mod likelysubtags;
mod listfmt;
mod localenames;
mod numberfmt;
mod pluralrules;
mod relativedatetime_fmt;

#[path = "../../common/run_all_tests.rs"]
mod run_all_tests;

fn main() -> io::Result<()> {
    let executor_fns = run_all_tests::ExecutorFns {
        run_collation_test: collator::run_collation_test,
        run_datetimeformat_test: datetimefmt::run_datetimeformat_test,
        run_likelysubtags_test: likelysubtags::run_likelysubtags_test,
        run_list_fmt_test: listfmt::run_list_fmt_test,
        run_locale_name_test: localenames::run_locale_name_test,
        run_numberformat_test: numberfmt::run_numberformat_test,
        run_plural_rules_test: pluralrules::run_plural_rules_test,
        run_relativedatetimeformat_test: relativedatetime_fmt::run_relativedatetimeformat_test,
    };
    run_all_tests::main(executor_fns)
}
