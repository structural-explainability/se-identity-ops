use std::io::{self, BufRead};
fn main() {
    let stdin = io::stdin();
    for line in stdin.lock().lines() {
        let line = line.unwrap();
        match cep_core::common::localization::apply_localization_name(&line, "US-IL") {
            Ok(out) => println!("{}", out),
            Err(e) => println!("ERROR:{}", e),
        }
    }
}
