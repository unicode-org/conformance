pub fn print(package: &cargo_metadata::Package) {
    println!(
        "cargo:rustc-env=CONFORMANCE_ICU4X_VERSION={}",
        package.version
    );
    println!("cargo::rustc-check-cfg=cfg(ver, values(\"1.3\", \"1.4\", \"1.5\", \"2.0-beta1\"))");
    if !package.version.pre.is_empty() {
        println!(
            "cargo:rustc-cfg=ver=\"{}.{}-{}\"",
            package.version.major, package.version.minor, package.version.pre,
        );
    } else {
        println!(
            "cargo:rustc-cfg=ver=\"{}.{}\"",
            package.version.major, package.version.minor,
        );
    }
}
