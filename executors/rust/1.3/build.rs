// Getting the version of ICU4X

fn main() {
    let metadata = cargo_metadata::MetadataCommand::new().exec().unwrap();
    for package in metadata.packages.iter() {
        if package.name == "icu" {
            println!(
                "cargo:rustc-env=CONFORMANCE_ICU4X_VERSION={}",
                package.version
            );
            return;
        }
    }
}
