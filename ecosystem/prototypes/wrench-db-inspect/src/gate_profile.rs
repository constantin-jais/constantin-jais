use crate::finding::Finding;
use serde::Deserialize;
use std::{collections::BTreeMap, fs, path::PathBuf};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct GateDecision {
    pub blocks: bool,
    pub action: String,
    pub reason: String,
    pub profile: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct GateProfilesEnvelope {
    pub data: GateProfilesData,
}

#[derive(Debug, Clone, Deserialize)]
pub struct GateProfilesData {
    pub profiles: BTreeMap<String, GateProfile>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct GateProfile {
    pub default_actions: BTreeMap<String, String>,
    #[serde(default)]
    pub category_overrides: BTreeMap<String, String>,
    #[serde(default)]
    pub rule_overrides: BTreeMap<String, String>,
    #[serde(default)]
    pub waivers: WaiverPolicy,
}

#[derive(Debug, Clone, Deserialize)]
pub struct WaiverPolicy {
    #[serde(default = "default_true")]
    pub allow_active: bool,
    #[serde(default)]
    pub block_expired: bool,
    #[serde(default)]
    pub require_owner: bool,
    #[serde(default)]
    pub require_reviewer: bool,
    #[serde(default)]
    pub require_expiry: bool,
}

impl Default for WaiverPolicy {
    fn default() -> Self {
        Self {
            allow_active: true,
            block_expired: true,
            require_owner: true,
            require_reviewer: true,
            require_expiry: true,
        }
    }
}

fn default_true() -> bool {
    true
}

#[derive(Debug, Clone)]
pub struct GateProfiles {
    profiles: BTreeMap<String, GateProfile>,
}

impl GateProfiles {
    pub fn builtin() -> Self {
        let mut profiles = BTreeMap::new();
        profiles.insert(
            "local".to_string(),
            GateProfile::new([
                ("critical", "block"),
                ("high", "warn"),
                ("medium", "warn"),
                ("low", "warn"),
                ("info", "ignore"),
            ]),
        );
        profiles.insert(
            "pull_request".to_string(),
            GateProfile::new([
                ("critical", "block"),
                ("high", "block"),
                ("medium", "warn"),
                ("low", "warn"),
                ("info", "ignore"),
            ]),
        );
        let mut protected = GateProfile::new([
            ("critical", "block"),
            ("high", "block"),
            ("medium", "warn"),
            ("low", "warn"),
            ("info", "ignore"),
        ]);
        protected
            .category_overrides
            .insert("inspection_integrity".to_string(), "block".to_string());
        protected.rule_overrides.insert(
            "TABLE_CLASSIFICATION_REQUIRED".to_string(),
            "block".to_string(),
        );
        profiles.insert("protected_branch".to_string(), protected.clone());
        protected
            .category_overrides
            .insert("manifest_coverage".to_string(), "block".to_string());
        protected.rule_overrides.insert(
            "TENANT_DERIVATION_FK_REQUIRED".to_string(),
            "block".to_string(),
        );
        protected.rule_overrides.insert(
            "TENANT_DERIVATION_POLICY_REQUIRED".to_string(),
            "block".to_string(),
        );
        protected.rule_overrides.insert(
            "TENANT_DERIVATION_PATH_UNSUPPORTED".to_string(),
            "block".to_string(),
        );
        profiles.insert("release".to_string(), protected);
        Self { profiles }
    }

    pub fn from_optional_path(path: Option<&PathBuf>) -> Result<Self, String> {
        let Some(path) = path else {
            return Ok(Self::builtin());
        };
        let raw = fs::read_to_string(path)
            .map_err(|e| format!("cannot read gate profile config {}: {e}", path.display()))?;
        let envelope = serde_json::from_str::<GateProfilesEnvelope>(&raw)
            .map_err(|e| format!("invalid gate profile config JSON: {e}"))?;
        let profiles = Self {
            profiles: envelope.data.profiles,
        };
        profiles.validate()?;
        Ok(profiles)
    }

    pub fn decide(&self, profile_name: &str, finding: &Finding) -> GateDecision {
        let profile = self
            .profiles
            .get(profile_name)
            .or_else(|| self.profiles.get("protected_branch"));
        let effective_profile = if self.profiles.contains_key(profile_name) {
            profile_name
        } else {
            "protected_branch"
        };

        if finding.waiver_id.is_some() {
            let policy = profile.map(|p| &p.waivers).cloned().unwrap_or_default();
            if !policy.allow_active {
                return GateDecision {
                    blocks: true,
                    action: "block".to_string(),
                    reason: "waivers are not accepted by profile".to_string(),
                    profile: effective_profile.to_string(),
                };
            }
            if let Some(reason) = invalid_waiver_reason(finding, &policy) {
                return GateDecision {
                    blocks: true,
                    action: "block".to_string(),
                    reason,
                    profile: effective_profile.to_string(),
                };
            }
            return GateDecision {
                blocks: false,
                action: "waived".to_string(),
                reason: "active waiver accepted by profile".to_string(),
                profile: effective_profile.to_string(),
            };
        }

        let action = profile
            .and_then(|p| p.rule_overrides.get(finding.rule_id))
            .or_else(|| profile.and_then(|p| p.category_overrides.get(finding.category)))
            .or_else(|| profile.and_then(|p| p.default_actions.get(finding.severity)))
            .cloned()
            .unwrap_or_else(|| default_action_for_severity(finding.severity).to_string());

        GateDecision {
            blocks: action == "block",
            reason: format!(
                "{} {} action resolved to {} in {}",
                finding.severity, finding.rule_id, action, effective_profile
            ),
            action,
            profile: effective_profile.to_string(),
        }
    }

    pub fn gate_blocked(&self, profile_name: &str, findings: &[Finding]) -> bool {
        findings
            .iter()
            .any(|finding| self.decide(profile_name, finding).blocks)
    }

    fn validate(&self) -> Result<(), String> {
        if self.profiles.is_empty() {
            return Err("gate profile config must define at least one profile".to_string());
        }
        for (name, profile) in &self.profiles {
            for (severity, action) in &profile.default_actions {
                validate_action(action)
                    .map_err(|e| format!("profile {name} severity {severity}: {e}"))?;
            }
            for (category, action) in &profile.category_overrides {
                validate_action(action)
                    .map_err(|e| format!("profile {name} category {category}: {e}"))?;
            }
            for (rule, action) in &profile.rule_overrides {
                validate_action(action).map_err(|e| format!("profile {name} rule {rule}: {e}"))?;
            }
        }
        Ok(())
    }
}

impl GateProfile {
    fn new<const N: usize>(default_actions: [(&str, &str); N]) -> Self {
        Self {
            default_actions: default_actions
                .into_iter()
                .map(|(k, v)| (k.to_string(), v.to_string()))
                .collect(),
            category_overrides: BTreeMap::new(),
            rule_overrides: BTreeMap::new(),
            waivers: WaiverPolicy::default(),
        }
    }
}

fn invalid_waiver_reason(finding: &Finding, policy: &WaiverPolicy) -> Option<String> {
    if policy.require_expiry && finding.waiver_expires_at.is_none() {
        return Some("waiver missing expiry".to_string());
    }
    if policy.block_expired
        && finding
            .waiver_expires_at
            .as_deref()
            .is_some_and(|expires_at| expires_at <= "2026-06-30T00:00:00Z")
    {
        return Some("waiver expired".to_string());
    }
    if policy.require_owner && !finding.waiver_owner_present {
        return Some("waiver missing owner".to_string());
    }
    if policy.require_reviewer && !finding.waiver_reviewer_present {
        return Some("waiver missing reviewer".to_string());
    }
    None
}

fn validate_action(action: &str) -> Result<(), String> {
    match action {
        "block" | "warn" | "ignore" => Ok(()),
        other => Err(format!(
            "invalid action {other}; expected block|warn|ignore"
        )),
    }
}

fn default_action_for_severity(severity: &str) -> &'static str {
    match severity {
        "critical" | "high" => "block",
        "medium" | "low" => "warn",
        _ => "ignore",
    }
}
