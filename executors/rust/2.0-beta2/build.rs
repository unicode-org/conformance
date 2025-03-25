#[path = "../common/print_icu4x_versions_1_5.rs"]
mod print_icu4x_versions_1_5;

#[path = "../common/print_modern_locales.rs"]
mod print_modern_locales;

pub fn main() {
    print_icu4x_versions_1_5::main();
    print_modern_locales::main();
}
