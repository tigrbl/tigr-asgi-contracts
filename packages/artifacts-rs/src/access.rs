use std::fs;
use std::path::{Path, PathBuf};

pub fn contract_root() -> PathBuf {
    let crate_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let vendored = crate_root.join("contract");
    if vendored.exists() {
        return vendored;
    }
    crate_root.join("../../contract")
}

pub fn load_json(rel: &str) -> serde_json::Value {
    let path = contract_root().join(rel);
    let data = fs::read_to_string(path).expect("read json");
    serde_json::from_str(&data).expect("parse json")
}

pub fn load_yaml(rel: &str) -> serde_yaml::Value {
    let path = contract_root().join(rel);
    let data = fs::read_to_string(path).expect("read yaml");
    serde_yaml::from_str(&data).expect("parse yaml")
}

pub fn manifest() -> serde_json::Value {
    load_json("manifest.json")
}

pub fn checksums() -> String {
    fs::read_to_string(contract_root().join("checksums.txt")).expect("read checksums")
}
