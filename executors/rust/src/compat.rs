#![allow(unused_imports)] // not all versions use all imports

#[cfg(any(ver = "1.3", ver = "1.4", ver = "1.5"))]
pub use icu::locid::{extensions::unicode, locale, LanguageIdentifier, Locale};

#[cfg(not(any(ver = "1.3", ver = "1.4", ver = "1.5")))]
pub use icu::locale::{extensions::unicode, locale, LanguageIdentifier, Locale};

#[cfg(any(ver = "1.3", ver = "1.4", ver = "1.5"))]
macro_rules! pref {
    ($arg:expr) => {
        &($arg).into()
    };
}

#[cfg(not(any(ver = "1.3", ver = "1.4", ver = "1.5")))]
macro_rules! pref {
    ($arg:expr) => {
        ($arg).into()
    };
}

pub(crate) use pref;
