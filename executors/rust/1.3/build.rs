// Getting the version of ICU4X

fn main() {
    let metadata = cargo_metadata::MetadataCommand::new().exec().unwrap();
    for package in metadata.packages.iter() {
        if package.name == "icu" {
            println!(
                "cargo:rustc-env=CONFORMANCE_ICU4X_VERSION={}",
                package.version
            );
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
