use serde::Serialize;

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct Finding {
    pub rule_id: &'static str,
    pub category: &'static str,
    pub severity: &'static str,
    pub confidence: &'static str,
    pub subject_type: &'static str,
    pub subject_name: String,
    pub role: Option<String>,
    pub waiver_id: Option<String>,
    pub waiver_expires_at: Option<String>,
    pub waiver_owner_present: bool,
    pub waiver_reviewer_present: bool,
}

impl Finding {
    pub fn new(
        rule_id: &'static str,
        category: &'static str,
        severity: &'static str,
        subject_type: &'static str,
        subject_name: &str,
    ) -> Self {
        Self {
            rule_id,
            category,
            severity,
            confidence: "high",
            subject_type,
            subject_name: subject_name.to_string(),
            role: None,
            waiver_id: None,
            waiver_expires_at: None,
            waiver_owner_present: false,
            waiver_reviewer_present: false,
        }
    }
}

pub fn severity_rank(sev: &str) -> u8 {
    match sev {
        "critical" => 0,
        "high" => 1,
        "medium" => 2,
        "low" => 3,
        _ => 4,
    }
}
