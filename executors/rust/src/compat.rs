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

#[cfg(any(ver = "1.3", ver = "1.4", ver = "1.5"))]
pub(crate) fn is_locale_supported(_: &Locale) -> bool {
    // Unconditionally return true so that tests will run
    true
}

#[cfg(not(any(ver = "1.3", ver = "1.4", ver = "1.5")))]
pub(crate) fn is_locale_supported(locale: &Locale) -> bool {
    let json_str = std::env!("CONFORMANCE_ICU4X_LOCALES");
    let locales: Vec<String> = serde_json::from_str(json_str).unwrap();
    let language = locale.id.language;
    let mut language_script = langid_und();
    language_script.language = language;
    language_script.script = locale.id.script;
    for candidate in locales.iter() {
        if writeable::cmp_str(&language, candidate).is_eq() {
            return true;
        }
        if writeable::cmp_str(&language_script, candidate).is_eq() {
            return true;
        }
    }
    false
}

pub(crate) fn langid_und() -> LanguageIdentifier {
    locale!("und").id
}

#[cfg(not(any(
    ver = "1.3",
    ver = "1.4",
    ver = "1.5",
    ver = "2.0-beta1",
    ver = "2.0-beta2"
)))]
macro_rules! as_borrowed_2_0 {
    ($expr:expr) => {
        $expr.as_borrowed()
    };
}

#[cfg(any(
    ver = "1.3",
    ver = "1.4",
    ver = "1.5",
    ver = "2.0-beta1",
    ver = "2.0-beta2"
))]
macro_rules! as_borrowed_2_0 {
    ($expr:expr) => {
        $expr
    };
}

pub(crate) use as_borrowed_2_0;
