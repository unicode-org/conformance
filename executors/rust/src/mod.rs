mod compat;
mod try_or_return_error;

pub mod collator;
pub mod decimalfmt;
pub mod displaynames;
pub mod likelysubtags;
pub mod listfmt;
pub mod localenames;
pub mod numberfmt;
pub mod pluralrules;
pub mod relativedatetime_fmt;

#[cfg(any(conformance_ver = "1.3", conformance_ver = "1.4", conformance_ver = "1.5"))]
#[path = "datetime_1.rs"]
pub mod datetimefmt;

#[cfg(any(conformance_ver = "2.0-beta1"))]
#[path = "datetime_2.rs"]
pub mod datetimefmt;

use try_or_return_error::try_or_return_error;
