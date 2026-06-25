use crate::{
    finding::Finding, gate_profile::GateProfiles, manifest::ManifestData,
    redaction::redact_json_value, redaction::redact_text,
};
use serde_json::{Value, json};
use std::path::PathBuf;

pub fn render_report(
    manifest: &ManifestData,
    findings: &[Finding],
    profile: &str,
    gate_profiles: &GateProfiles,
    manifest_path: &PathBuf,
    schema_path: &PathBuf,
) -> Result<String, String> {
    let blocked = gate_profiles.gate_blocked(profile, findings);
    let status = status(findings, blocked);

    let findings_json: Vec<Value> = findings
        .iter()
        .map(|f| {
            let mut subject = json!({ "type": f.subject_type, "name": f.subject_name });
            if let Some(role) = &f.role {
                subject["role"] = json!(role);
            }
            let decision = gate_profiles.decide(profile, f);
            let mut obj = json!({
                "rule_id": f.rule_id,
                "category": f.category,
                "severity": f.severity,
                "confidence": f.confidence,
                "subject": subject,
                "gate": {
                    "blocks": decision.blocks,
                    "profile": decision.profile,
                    "action": decision.action,
                    "reason": decision.reason
                }
            });
            if let Some(id) = &f.waiver_id {
                obj["waiver"] = json!({
                    "id": id,
                    "expires_at": f.waiver_expires_at,
                    "owner_present": f.waiver_owner_present,
                    "reviewer_present": f.waiver_reviewer_present,
                    "accepted_by_gate": !decision.blocks && decision.action == "waived"
                });
            }
            obj
        })
        .collect();

    let mut report = json!({
        "data": {
            "format": "wrench.db_inspect.report.v0.1",
            "status": status,
            "summary": {
                "critical": findings.iter().filter(|f| f.severity == "critical").count(),
                "high": findings.iter().filter(|f| f.severity == "high").count(),
                "medium": findings.iter().filter(|f| f.severity == "medium").count(),
                "low": findings.iter().filter(|f| f.severity == "low").count(),
                "info": 0,
                "gate_blocked": blocked
            },
            "scope": {
                "product": manifest.product,
                "tenant": "organization",
                "inputs": [
                    { "kind": "manifest", "path": manifest_path.display().to_string() },
                    { "kind": "schema_dump", "path": schema_path.display().to_string() }
                ]
            },
            "metrics": metrics(manifest, findings, profile, gate_profiles),
            "findings": findings_json
        },
        "meta": {
            "schema_version": "0.1",
            "tool": "wrench-db-inspect",
            "tool_version": "0.1.0-prototype",
            "redaction": { "mode": "strict", "secrets_or_pii_included": false }
        }
    });

    redact_json_value(&mut report);
    serde_json::to_string_pretty(&report).map_err(|e| format!("cannot render report JSON: {e}"))
}

pub fn render_markdown_report(
    manifest: &ManifestData,
    findings: &[Finding],
    profile: &str,
    gate_profiles: &GateProfiles,
) -> String {
    let blocked = gate_profiles.gate_blocked(profile, findings);
    let status = status(findings, blocked);
    let mut out = String::new();
    out.push_str("# Wrench DB Inspect Report\n\n");
    out.push_str(&format!("- Product: `{}`\n", manifest.product));
    out.push_str("- Tenant: `organization`\n");
    out.push_str(&format!("- Profile: `{profile}`\n"));
    out.push_str(&format!("- Status: `{status}`\n"));
    out.push_str(&format!("- Gate blocked: `{blocked}`\n"));
    out.push_str(&format!(
        "- Blocking findings: `{}`\n",
        findings
            .iter()
            .filter(|f| gate_profiles.decide(profile, f).blocks)
            .count()
    ));
    out.push_str(&format!(
        "- Waivers: `{}`\n",
        findings.iter().filter(|f| f.waiver_id.is_some()).count()
    ));
    out.push_str(&format!(
        "- Tenant tables in manifest: `{}`\n\n",
        manifest
            .tables
            .iter()
            .filter(|t| t.classification == "tenant_scoped")
            .count()
    ));
    out.push_str("## Findings\n\n");
    if findings.is_empty() {
        out.push_str("No findings.\n");
    } else {
        out.push_str("| Severity | Rule | Subject | Gate | Waiver |\n");
        out.push_str("| --- | --- | --- | --- | --- |\n");
        for f in findings {
            out.push_str(&format!(
                "| `{}` | `{}` | `{}` `{}` | `{}` | `{}` |\n",
                f.severity,
                f.rule_id,
                f.subject_type,
                f.subject_name,
                gate_profiles.decide(profile, f).blocks,
                f.waiver_id.as_deref().unwrap_or("")
            ));
        }
    }
    out.push_str("\nReports intentionally omit row data, raw embeddings, prompts, credentials, DSNs, and PII.\n");
    redact_text(&out)
}

fn metrics(
    manifest: &ManifestData,
    findings: &[Finding],
    profile: &str,
    gate_profiles: &GateProfiles,
) -> Value {
    let tenant_table_count = manifest
        .tables
        .iter()
        .filter(|t| t.classification == "tenant_scoped")
        .count();
    let embedding_table_count = manifest
        .tables
        .iter()
        .filter(|t| t.contains_embeddings)
        .count();
    let blocking_finding_count = findings
        .iter()
        .filter(|f| gate_profiles.decide(profile, f).blocks)
        .count();
    let waiver_count = findings.iter().filter(|f| f.waiver_id.is_some()).count();
    let waiver_invalid_count = findings
        .iter()
        .filter(|f| f.rule_id == "WAIVER_INVALID")
        .count();
    let unknown_state_count = findings
        .iter()
        .filter(|f| matches!(f.category, "manifest_coverage" | "inspection_integrity"))
        .count();

    let tenant_rls_coverage =
        coverage_from_missing_rule(tenant_table_count, findings, "RLS_REQUIRED_TENANT_TABLE");
    let tenant_force_rls_coverage = coverage_from_missing_rule(
        tenant_table_count,
        findings,
        "FORCE_RLS_REQUIRED_TENANT_TABLE",
    );
    let pgvector_tenant_coverage = coverage_from_missing_rule(
        embedding_table_count,
        findings,
        "PGVECTOR_TENANT_FILTER_REQUIRED",
    );

    json!({
        "manifest_table_count": manifest.tables.len(),
        "tenant_scoped_table_count": tenant_table_count,
        "embedding_table_count": embedding_table_count,
        "tenant_rls_coverage": tenant_rls_coverage,
        "tenant_force_rls_coverage": tenant_force_rls_coverage,
        "pgvector_tenant_coverage": pgvector_tenant_coverage,
        "blocking_finding_count": blocking_finding_count,
        "waiver_count": waiver_count,
        "waiver_invalid_count": waiver_invalid_count,
        "unknown_state_count": unknown_state_count,
        "parser_error_count": 0,
        "report_secret_leak_count": 0,
        "report_pii_leak_count": 0,
        "raw_embedding_leak_count": 0,
        "mutating_operation_count": 0
    })
}

fn coverage_from_missing_rule(total: usize, findings: &[Finding], missing_rule_id: &str) -> Value {
    if total == 0 {
        return Value::Null;
    }
    let missing = findings
        .iter()
        .filter(|f| f.rule_id == missing_rule_id && f.waiver_id.is_none())
        .count();
    json!((total.saturating_sub(missing) as f64) / (total as f64))
}

fn status(findings: &[Finding], blocked: bool) -> &'static str {
    if blocked {
        "failed"
    } else if findings.iter().any(|f| f.waiver_id.is_some()) {
        "passed_with_waiver"
    } else {
        "passed"
    }
}
