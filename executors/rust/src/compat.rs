#![allow(unused_imports)] // not all versions use all imports

#[cfg(any(conformance_ver = "1.3", conformance_ver = "1.4", conformance_ver = "1.5"))]
pub use icu::locid::{locale, Locale, LanguageIdentifier, extensions::unicode};

#[cfg(not(any(conformance_ver = "1.3", conformance_ver = "1.4", conformance_ver = "1.5")))]
pub use icu::locale::{locale, Locale, LanguageIdentifier, extensions::unicode};


#[cfg(any(conformance_ver = "1.3", conformance_ver = "1.4", conformance_ver = "1.5"))]
macro_rules! pref {
	($arg:expr) => {
		&($arg).into()
	}
}

#[cfg(not(any(conformance_ver = "1.3", conformance_ver = "1.4", conformance_ver = "1.5")))]
macro_rules! pref {
	($arg:expr) => {
		($arg).into()
	}
}

pub(crate) use pref;
