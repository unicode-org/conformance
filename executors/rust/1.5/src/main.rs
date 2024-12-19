// Read JSON test case from standard in.
// Parse to get test and parameters
// Run test
// Return results

use std::io;

#[path = "../../1.3/src/collator.rs"]
mod collator;

#[path = "../../1.3/src/datetimefmt.rs"]
#[allow(deprecated)]
mod datetimefmt;

#[path = "../../1.3/src/decimalfmt.rs"]
mod decimalfmt;

#[path = "../../1.3/src/displaynames.rs"]
mod displaynames;

#[path = "../../1.3/src/likelysubtags.rs"]
mod likelysubtags;

#[path = "../../1.3/src/listfmt.rs"]
mod listfmt;

#[path = "../../1.3/src/localenames.rs"]
mod localenames;

#[path = "../../1.3/src/numberfmt.rs"]
mod numberfmt;

#[path = "../../1.3/src/pluralrules.rs"]
mod pluralrules;

#[path = "../../1.3/src/relativedatetime_fmt.rs"]
mod relativedatetime_fmt;

#[path = "../../common/run_all_tests.rs"]
mod run_all_tests;

mod icu {
    pub use ::icu::experimental::compactdecimal;
    pub use ::icu::experimental::displaynames;
    pub use ::icu::experimental::relativetime;
}

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
