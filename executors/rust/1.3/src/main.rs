// Read JSON test case from standard in.
// Parse to get test and parameters
// Run test
// Return results

mod icu {
    pub use ::icu::compactdecimal;
    pub use ::icu::displaynames;
    pub use ::icu::relativetime;
}

#[path = "../../src/mod.rs"]
mod executors;

#[path = "../../common/run_all_tests.rs"]
mod run_all_tests;

fn main() -> std::io::Result<()> {
    let executor_fns = run_all_tests::ExecutorFns {
        run_collation_test: executors::collator::run_collation_test,
        run_datetimeformat_test: executors::datetimefmt::run_datetimeformat_test,
        run_likelysubtags_test: executors::likelysubtags::run_likelysubtags_test,
        run_list_fmt_test: executors::listfmt::run_list_fmt_test,
        run_locale_name_test: executors::localenames::run_locale_name_test,
        run_numberformat_test: executors::numberfmt::run_numberformat_test,
        run_plural_rules_test: executors::pluralrules::run_plural_rules_test,
        run_relativedatetimeformat_test: executors::relativedatetime_fmt::run_relativedatetimeformat_test,
    };
    run_all_tests::main(executor_fns)
}
