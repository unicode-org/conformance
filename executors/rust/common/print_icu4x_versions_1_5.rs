// Get the version of ICU4X and data

#[path = "./print_icu4x_version.rs"]
mod print_icu4x_version;

pub fn main() {
    println!("cargo::rustc-check-cfg=cfg(conformance_ver, values(\"1.3\", \"1.4\", \"1.5\", \"2.0-beta1\"))");

    let metadata = cargo_metadata::MetadataCommand::new().exec().unwrap();
    for package in metadata.packages.iter() {
        if package.name == "icu" {
            print_icu4x_version::print(&package);
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
