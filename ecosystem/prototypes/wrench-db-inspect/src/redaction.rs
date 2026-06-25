use regex::Regex;
use serde_json::Value;

const REDACTED_DSN: &str = "[REDACTED_DSN]";
const REDACTED_SECRET: &str = "[REDACTED_SECRET]";
const REDACTED_ASSIGNMENT: &str = "[REDACTED_SECRET_ASSIGNMENT]";

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RedactionResult {
    pub text: String,
    pub count: usize,
}

pub fn redact_text(input: &str) -> String {
    redact_text_with_count(input).text
}

pub fn redact_text_with_count(input: &str) -> RedactionResult {
    let mut out = input.to_string();
    let mut count = 0;
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
        count += regex.find_iter(&out).count();
        out = regex.replace_all(&out, replacement).to_string();
    }
    RedactionResult { text: out, count }
}

pub fn redact_json_value(value: &mut Value) -> usize {
    match value {
        Value::String(s) => {
            let result = redact_text_with_count(s);
            *s = result.text;
            result.count
        }
        Value::Array(items) => items.iter_mut().map(redact_json_value).sum(),
        Value::Object(map) => map.values_mut().map(redact_json_value).sum(),
        Value::Null | Value::Bool(_) | Value::Number(_) => 0,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn redacts_common_secret_like_patterns() {
        let input = "postgres://user:pass@example/db token=abc123 sk_test_fixture_redaction_123456 Bearer abc.def";
        let result = redact_text_with_count(input);
        assert!(!result.text.contains("postgres://user"));
        assert!(!result.text.contains("abc123"));
        assert!(!result.text.contains("sk_test_fixture_redaction_123456"));
        assert!(!result.text.contains("Bearer abc.def"));
        assert!(result.text.contains(REDACTED_DSN));
        assert!(result.text.contains(REDACTED_SECRET));
        assert_eq!(result.count, 4);
    }
}
