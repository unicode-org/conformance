// Get the list of modern locales for this ICU4X version

use std::path::PathBuf;
use icu_provider_source::{SourceDataProvider, CoverageLevel};

pub fn main() {
    let metadata = cargo_metadata::MetadataCommand::new().exec().unwrap();
    for package in metadata.packages.iter() {
        if package.name == "icu_provider_source" {
            let mut path = PathBuf::from(&package.manifest_path);
            path.pop();
            path.push("tests");
            path.push("data");
            path.push("cldr");
            let provider = SourceDataProvider::new_custom()
                .with_cldr(&path)
                .unwrap();
            let locales = provider.locales_for_coverage_levels([
                CoverageLevel::Modern
            ]).unwrap().into_iter().map(|l| l.to_string()).collect::<Vec<_>>();
            let locales_str = serde_json::to_string(&locales).unwrap();
            println!(
                "cargo:rustc-env=CONFORMANCE_ICU4X_LOCALES={}",
                locales_str
            );
        }
    }
}
