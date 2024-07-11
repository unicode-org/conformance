// Getting the version of ICU4X

fn main() {
    let metadata = cargo_metadata::MetadataCommand::new().exec().unwrap();
    for package in metadata.packages.iter() {
        if package.name == "icu" {
            println!(
                "cargo:rustc-env=CONFORMANCE_ICU4X_VERSION={}",
                package.version
            );
        } else if package.name == "icu_calendar_data" {
            println!(
                "cargo:rustc-env=CONFORMANCE_ICU_VERSION={}",
                &package.metadata["sources"]["icuexport"]["tagged"]
                    .as_str()
                    .unwrap()
            );
            println!(
                "cargo:rustc-env=CONFORMANCE_CLDR_VERSION={}",
                &package.metadata["sources"]["cldr"]["tagged"]
                    .as_str()
                    .unwrap()
            );
        }
    }
}
