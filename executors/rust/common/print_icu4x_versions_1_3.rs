// Get the version of ICU4X and data

#[path = "./print_icu4x_version.rs"]
mod print_icu4x_version;

pub fn main() {
    let metadata = cargo_metadata::MetadataCommand::new().exec().unwrap();
    for package in metadata.packages.iter() {
        if package.name == "icu" {
            print_icu4x_version::print(&package);
        }
    }

    // Get data version information from PackageMetadata
    // https://crates.io/crates/rustc_version_runtime
    // https://github.com/serde-rs/json

    println!(
        "cargo:rustc-env=CONFORMANCE_ICU_VERSION={}",
        icu_datagen::DatagenProvider::LATEST_TESTED_ICUEXPORT_TAG
    );
    println!(
        "cargo:rustc-env=CONFORMANCE_CLDR_VERSION={}",
        icu_datagen::DatagenProvider::LATEST_TESTED_CLDR_TAG
    );
}
