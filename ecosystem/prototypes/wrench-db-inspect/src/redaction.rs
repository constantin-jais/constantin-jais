use regex::Regex;
use serde_json::Value;

const REDACTED_DSN: &str = "[REDACTED_DSN]";
const REDACTED_SECRET: &str = "[REDACTED_SECRET]";
const REDACTED_ASSIGNMENT: &str = "[REDACTED_SECRET_ASSIGNMENT]";

pub fn redact_text(input: &str) -> String {
    let mut out = input.to_string();
    for (pattern, replacement) in [
        (r#"(?i)postgres(?:ql)?://[^\s\"'`<>]+"#, REDACTED_DSN),
        (
            r#"(?i)\b(?:password|passwd|pwd|secret|token|api[_-]?key)\s*=\s*[^\s\"'`,;]+"#,
            REDACTED_ASSIGNMENT,
        ),
        (
            r"\bsk_(?:test|live|proj)_[A-Za-z0-9_\-]{8,}\b",
            REDACTED_SECRET,
        ),
        (
            r"\b(?:Bearer|Basic)\s+[A-Za-z0-9._~+\-/]+=*",
            REDACTED_SECRET,
        ),
    ] {
        let regex = Regex::new(pattern).expect("redaction regex must compile");
        out = regex.replace_all(&out, replacement).to_string();
    }
    out
}

pub fn redact_json_value(value: &mut Value) {
    match value {
        Value::String(s) => *s = redact_text(s),
        Value::Array(items) => {
            for item in items {
                redact_json_value(item);
            }
        }
        Value::Object(map) => {
            for item in map.values_mut() {
                redact_json_value(item);
            }
        }
        Value::Null | Value::Bool(_) | Value::Number(_) => {}
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn redacts_common_secret_like_patterns() {
        let input = "postgres://user:pass@example/db token=abc123 sk_test_fixture_redaction_123456 Bearer abc.def";
        let redacted = redact_text(input);
        assert!(!redacted.contains("postgres://user"));
        assert!(!redacted.contains("abc123"));
        assert!(!redacted.contains("sk_test_fixture_redaction_123456"));
        assert!(!redacted.contains("Bearer abc.def"));
        assert!(redacted.contains(REDACTED_DSN));
        assert!(redacted.contains(REDACTED_SECRET));
    }
}
