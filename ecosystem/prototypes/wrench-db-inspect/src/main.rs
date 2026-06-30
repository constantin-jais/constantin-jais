mod finding;
mod gate_profile;
mod manifest;
mod redaction;
mod report;
mod rules;
mod sql_facts;

use crate::{
    gate_profile::GateProfiles,
    manifest::parse_manifest,
    report::{render_markdown_report, render_report},
    rules::inspect,
};
use std::{env, fs, path::PathBuf, process};

fn main() {
    match run_cli(&env::args().collect::<Vec<_>>()) {
        Ok(code) => process::exit(code),
        Err(err) => {
            eprintln!("wrench-db-inspect: {err}");
            process::exit(2);
        }
    }
}

fn run_cli(args: &[String]) -> Result<i32, String> {
    if args.len() == 1 || args.iter().any(|a| a == "--help" || a == "-h") {
        print_help();
        return Ok(0);
    }

    let mut manifest_path = None;
    let mut schema_path = None;
    let mut report_path = None;
    let mut report_md_path = None;
    let mut migrations_path = None;
    let mut gate_profile_config_path = None;
    let mut profile = "protected_branch".to_string();

    let mut i = usize::from(args.get(1).map(String::as_str) == Some("run"));
    while i + 1 < args.len() {
        i += 1;
        match args[i].as_str() {
            "--manifest" => manifest_path = take_path(args, &mut i),
            "--schema-dump" => schema_path = take_path(args, &mut i),
            "--report-json" => report_path = take_path(args, &mut i),
            "--report-md" => report_md_path = take_path(args, &mut i),
            "--profile" => profile = take_string(args, &mut i).unwrap_or(profile),
            "--gate-profile-config" => gate_profile_config_path = take_path(args, &mut i),
            "--migrations" => migrations_path = take_path(args, &mut i),
            other => return Err(format!("unknown argument: {other}")),
        }
    }

    let manifest_path = manifest_path.ok_or("--manifest is required")?;
    let schema_path = schema_path.ok_or("--schema-dump is required")?;
    let manifest_raw = fs::read_to_string(&manifest_path)
        .map_err(|e| format!("cannot read manifest {}: {e}", manifest_path.display()))?;
    let mut schema_raw = fs::read_to_string(&schema_path)
        .map_err(|e| format!("cannot read schema {}: {e}", schema_path.display()))?;
    if let Some(path) = migrations_path {
        schema_raw.push('\n');
        schema_raw.push_str(&read_migrations(&path)?);
    }

    let manifest = parse_manifest(&manifest_raw)?;
    let gate_profiles = GateProfiles::from_optional_path(gate_profile_config_path.as_ref())?;
    let findings = inspect(&schema_raw, &manifest);
    let report = render_report(
        &manifest,
        &findings,
        &profile,
        &gate_profiles,
        &manifest_path,
        &schema_path,
    )?;
    let markdown_report = render_markdown_report(&manifest, &findings, &profile, &gate_profiles);

    if let Some(path) = report_path {
        write_output(&path, report.json.clone(), "report")?;
    } else {
        println!("{}", report.json);
    }

    if let Some(path) = report_md_path {
        write_output(&path, markdown_report, "markdown report")?;
    }

    Ok(if report.blocks { 1 } else { 0 })
}

fn take_path(args: &[String], i: &mut usize) -> Option<PathBuf> {
    *i += 1;
    args.get(*i).map(PathBuf::from)
}

fn take_string(args: &[String], i: &mut usize) -> Option<String> {
    *i += 1;
    args.get(*i).cloned()
}

fn print_help() {
    println!(
        "wrench-db-inspect prototype\n\nUsage:\n  wrench-db-inspect run --manifest <manifest.json> --schema-dump <schema.sql> [--migrations <dir>] [--profile protected_branch] [--gate-profile-config <profiles.json>] [--report-json <report.json>] [--report-md <report.md>]\n"
    );
}

fn read_migrations(path: &PathBuf) -> Result<String, String> {
    if !path.exists() {
        return Ok(String::new());
    }
    let mut files = fs::read_dir(path)
        .map_err(|e| format!("cannot read migrations dir {}: {e}", path.display()))?
        .filter_map(Result::ok)
        .map(|entry| entry.path())
        .filter(|path| path.extension().is_some_and(|ext| ext == "sql"))
        .collect::<Vec<_>>();
    files.sort();
    let mut out = String::new();
    for file in files {
        out.push_str(
            &fs::read_to_string(&file)
                .map_err(|e| format!("cannot read migration {}: {e}", file.display()))?,
        );
        out.push('\n');
    }
    Ok(out)
}

fn write_output(path: &PathBuf, content: String, label: &str) -> Result<(), String> {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).map_err(|e| format!("cannot create {label} dir: {e}"))?;
    }
    fs::write(path, content).map_err(|e| format!("cannot write {label} {}: {e}", path.display()))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::manifest::ManifestData;

    fn fixture(case: &str) -> (String, ManifestData) {
        let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("../../specs/wrench-db-inspect/fixtures")
            .join(case);
        let schema = fs::read_to_string(root.join("schema.sql")).unwrap();
        let manifest =
            parse_manifest(&fs::read_to_string(root.join("manifest.json")).unwrap()).unwrap();
        (schema, manifest)
    }

    #[test]
    fn pass_rls_tenant_policy_ok() {
        let (schema, manifest) = fixture("pass/rls_tenant_policy_ok");
        assert!(inspect(&schema, &manifest).is_empty());
    }

    #[test]
    fn fail_missing_rls() {
        let (schema, manifest) = fixture("fail/rls_missing_on_tenant_table");
        let findings = inspect(&schema, &manifest);
        assert!(
            findings
                .iter()
                .any(|f| f.rule_id == "RLS_REQUIRED_TENANT_TABLE")
        );
        assert!(GateProfiles::builtin().gate_blocked("protected_branch", &findings));
    }

    #[test]
    fn fail_grant_all() {
        let (schema, manifest) = fixture("fail/grant_all_to_app_role");
        let findings = inspect(&schema, &manifest);
        assert!(findings.iter().any(|f| {
            f.rule_id == "GRANT_ALL_ON_TENANT_TABLE" && f.role.as_deref() == Some("rumble_app")
        }));
    }

    #[test]
    fn fail_pgvector_leak() {
        let (schema, manifest) = fixture("fail/pgvector_global_embedding_leak");
        let findings = inspect(&schema, &manifest);
        assert!(findings.iter().any(|f| {
            f.rule_id == "PGVECTOR_TENANT_FILTER_REQUIRED"
                && f.subject_name == "public.match_sources"
        }));
    }

    #[test]
    fn unknown_unclassified_table() {
        let (schema, manifest) = fixture("unknown/unclassified_table");
        let findings = inspect(&schema, &manifest);
        assert!(
            findings
                .iter()
                .any(|f| f.rule_id == "TABLE_CLASSIFICATION_REQUIRED")
        );
    }

    #[test]
    fn fail_force_rls_required() {
        let (schema, manifest) = fixture("fail/rls_not_forced_on_tenant_table");
        let findings = inspect(&schema, &manifest);
        assert!(
            findings
                .iter()
                .any(|f| f.rule_id == "FORCE_RLS_REQUIRED_TENANT_TABLE")
        );
    }

    #[test]
    fn fail_disable_rls_forbidden() {
        let (schema, manifest) = fixture("fail/disable_rls_migration");
        let findings = inspect(&schema, &manifest);
        assert!(
            findings
                .iter()
                .any(|f| f.rule_id == "DISABLE_RLS_FORBIDDEN")
        );
    }

    #[test]
    fn fail_dangerous_drop_table() {
        let (schema, manifest) = fixture("fail/dangerous_drop_table");
        let findings = inspect(&schema, &manifest);
        assert!(findings.iter().any(|f| f.rule_id == "DROP_TABLE_DANGEROUS"));
    }

    #[test]
    fn fail_dangerous_drop_column() {
        let (schema, manifest) = fixture("fail/dangerous_drop_column");
        let findings = inspect(&schema, &manifest);
        assert!(
            findings
                .iter()
                .any(|f| f.rule_id == "DROP_COLUMN_DANGEROUS")
        );
    }

    #[test]
    fn fail_truncate_dangerous() {
        let (schema, manifest) = fixture("fail/truncate_dangerous");
        let findings = inspect(&schema, &manifest);
        assert!(findings.iter().any(|f| f.rule_id == "TRUNCATE_DANGEROUS"));
    }

    #[test]
    fn fail_unqualified_delete_or_update() {
        let (delete_schema, delete_manifest) = fixture("fail/unqualified_delete");
        let delete_findings = inspect(&delete_schema, &delete_manifest);
        assert!(
            delete_findings
                .iter()
                .any(|f| f.rule_id == "UNQUALIFIED_DELETE_DANGEROUS")
        );

        let (update_schema, update_manifest) = fixture("fail/unqualified_update");
        let update_findings = inspect(&update_schema, &update_manifest);
        assert!(
            update_findings
                .iter()
                .any(|f| f.rule_id == "UNQUALIFIED_UPDATE_DANGEROUS")
        );
    }

    #[test]
    fn warn_security_definer_missing_search_path() {
        let (schema, manifest) = fixture("warn/security_definer_missing_search_path");
        let findings = inspect(&schema, &manifest);
        assert!(findings.iter().any(|f| {
            f.rule_id == "SECURITY_DEFINER_SEARCH_PATH_REQUIRED" && f.severity == "medium"
        }));
        assert!(!GateProfiles::builtin().gate_blocked("protected_branch", &findings));
    }

    #[test]
    fn warn_tenant_column_nullable() {
        let (schema, manifest) = fixture("warn/tenant_column_nullable");
        let findings = inspect(&schema, &manifest);
        assert!(
            findings.iter().any(|f| {
                f.rule_id == "TENANT_COLUMN_NOT_NULL_REQUIRED" && f.severity == "medium"
            })
        );
        assert!(!GateProfiles::builtin().gate_blocked("protected_branch", &findings));
    }

    #[test]
    fn warn_view_without_tenant_filter() {
        let (schema, manifest) = fixture("warn/view_without_tenant_filter");
        let findings = inspect(&schema, &manifest);
        assert!(
            findings
                .iter()
                .any(|f| { f.rule_id == "VIEW_TENANT_FILTER_REQUIRED" && f.severity == "medium" })
        );
        assert!(!GateProfiles::builtin().gate_blocked("protected_branch", &findings));
    }

    #[test]
    fn warn_function_without_tenant_filter() {
        let (schema, manifest) = fixture("warn/function_without_tenant_filter");
        let findings = inspect(&schema, &manifest);
        assert!(
            findings.iter().any(|f| {
                f.rule_id == "FUNCTION_TENANT_FILTER_REQUIRED" && f.severity == "medium"
            })
        );
        assert!(!GateProfiles::builtin().gate_blocked("protected_branch", &findings));
    }

    #[test]
    fn gate_profile_local_does_not_block_high() {
        let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("../../specs/wrench-db-inspect/fixtures");
        let report = std::env::temp_dir().join("wdi-local-profile-report.json");
        let code = run_cli(&[
            "wrench-db-inspect".to_string(),
            "run".to_string(),
            "--manifest".to_string(),
            root.join("fail/grant_all_to_app_role/manifest.json")
                .display()
                .to_string(),
            "--schema-dump".to_string(),
            root.join("fail/grant_all_to_app_role/schema.sql")
                .display()
                .to_string(),
            "--profile".to_string(),
            "local".to_string(),
            "--gate-profile-config".to_string(),
            root.join("gate-profiles/default.json")
                .display()
                .to_string(),
            "--report-json".to_string(),
            report.display().to_string(),
        ])
        .unwrap();
        assert_eq!(code, 0);
        let json: serde_json::Value =
            serde_json::from_str(&fs::read_to_string(report).unwrap()).unwrap();
        assert_eq!(json["data"]["findings"][0]["gate"]["action"], "warn");
    }

    #[test]
    fn gate_profile_config_can_block_medium_rule() {
        let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("../../specs/wrench-db-inspect/fixtures");
        let config = std::env::temp_dir().join("wdi-strict-medium-profile.json");
        fs::write(&config, r#"{
          "data": {
            "format": "wrench.db_inspect.gate_profiles.v0.1",
            "profiles": {
              "strict": {
                "default_actions": { "critical": "block", "high": "block", "medium": "warn", "low": "warn", "info": "ignore" },
                "category_overrides": {},
                "rule_overrides": { "TENANT_COLUMN_NOT_NULL_REQUIRED": "block" },
                "waivers": { "allow_active": true }
              }
            }
          },
          "meta": { "schema_version": "0.1" }
        }"#).unwrap();
        let report = std::env::temp_dir().join("wdi-strict-medium-report.json");
        let code = run_cli(&[
            "wrench-db-inspect".to_string(),
            "run".to_string(),
            "--manifest".to_string(),
            root.join("warn/tenant_column_nullable/manifest.json")
                .display()
                .to_string(),
            "--schema-dump".to_string(),
            root.join("warn/tenant_column_nullable/schema.sql")
                .display()
                .to_string(),
            "--profile".to_string(),
            "strict".to_string(),
            "--gate-profile-config".to_string(),
            config.display().to_string(),
            "--report-json".to_string(),
            report.display().to_string(),
        ])
        .unwrap();
        assert_eq!(code, 1);
        let json: serde_json::Value =
            serde_json::from_str(&fs::read_to_string(report).unwrap()).unwrap();
        assert_eq!(json["data"]["findings"][0]["gate"]["action"], "block");
    }

    #[test]
    fn report_renderer_redacts_future_secret_like_finding_fields() {
        use crate::{
            finding::Finding,
            report::{render_markdown_report, render_report},
        };
        let (_, manifest) = fixture("pass/rls_tenant_policy_ok");
        let gate_profiles = GateProfiles::builtin();
        let finding = Finding::new(
            "REDACTION_TEST",
            "inspection_integrity",
            "high",
            "sql_snippet",
            "postgres://fixture_user:fixture_password@localhost/db sk_test_fixture_redaction_123456",
        );
        let manifest_path = PathBuf::from("manifest.json");
        let schema_path = PathBuf::from("schema.sql");
        let rendered = render_report(
            &manifest,
            &[finding],
            "protected_branch",
            &gate_profiles,
            &manifest_path,
            &schema_path,
        )
        .unwrap();
        let json_report = rendered.json;
        let md_report = render_markdown_report(
            &manifest,
            &[Finding::new(
                "REDACTION_TEST",
                "inspection_integrity",
                "high",
                "sql_snippet",
                "postgres://fixture_user:fixture_password@localhost/db sk_test_fixture_redaction_123456",
            )],
            "protected_branch",
            &gate_profiles,
        );
        for forbidden in [
            "fixture_password",
            "postgres://fixture_user",
            "sk_test_fixture_redaction_123456",
        ] {
            assert!(
                !json_report.contains(forbidden),
                "JSON report leaked {forbidden}"
            );
            assert!(
                !md_report.contains(forbidden),
                "Markdown report leaked {forbidden}"
            );
        }
        assert!(json_report.contains("[REDACTED_DSN]"));
        assert!(json_report.contains("[REDACTED_SECRET]"));
        let json: serde_json::Value = serde_json::from_str(&json_report).unwrap();
        assert_eq!(json["data"]["metrics"]["redactions_applied_count"], 2);
        assert_eq!(json["meta"]["redaction"]["applied"], true);
    }

    #[test]
    fn release_blocks_when_report_redaction_was_applied() {
        use crate::{finding::Finding, report::render_report};
        let (_, manifest) = fixture("pass/rls_tenant_policy_ok");
        let gate_profiles = GateProfiles::builtin();
        let finding = Finding::new(
            "REDACTION_TEST",
            "inspection_integrity",
            "high",
            "sql_snippet",
            "postgres://fixture_user:fixture_password@localhost/db",
        );
        let rendered = render_report(
            &manifest,
            &[finding],
            "release",
            &gate_profiles,
            &PathBuf::from("manifest.json"),
            &PathBuf::from("schema.sql"),
        )
        .unwrap();
        assert!(rendered.blocks);
        let json: serde_json::Value = serde_json::from_str(&rendered.json).unwrap();
        assert_eq!(json["meta"]["redaction"]["applied"], true);
        assert_eq!(json["data"]["summary"]["gate_blocked"], true);
        assert_eq!(
            json["data"]["report_gate"]["reason"],
            "redaction applied in release requires review"
        );
    }

    #[test]
    fn redaction_fixture_does_not_leak_secret_like_sql_comments() {
        let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("../../specs/wrench-db-inspect/fixtures");
        let report = std::env::temp_dir().join("wdi-redaction-report.json");
        let report_md = std::env::temp_dir().join("wdi-redaction-report.md");
        let code = run_cli(&[
            "wrench-db-inspect".to_string(),
            "run".to_string(),
            "--manifest".to_string(),
            root.join("redaction/secret_like_sql_comments/manifest.json")
                .display()
                .to_string(),
            "--schema-dump".to_string(),
            root.join("redaction/secret_like_sql_comments/schema.sql")
                .display()
                .to_string(),
            "--profile".to_string(),
            "protected_branch".to_string(),
            "--gate-profile-config".to_string(),
            root.join("gate-profiles/default.json")
                .display()
                .to_string(),
            "--report-json".to_string(),
            report.display().to_string(),
            "--report-md".to_string(),
            report_md.display().to_string(),
        ])
        .unwrap();
        assert_eq!(code, 0);
        let json_report = fs::read_to_string(report).unwrap();
        let md_report = fs::read_to_string(report_md).unwrap();
        let json: serde_json::Value = serde_json::from_str(&json_report).unwrap();
        assert_eq!(json["meta"]["redaction"]["applied"], false);
        for forbidden in [
            "sk_test_fixture_redaction_123456",
            "fixture_password",
            "postgres://fixture_user",
        ] {
            assert!(
                !json_report.contains(forbidden),
                "JSON report leaked {forbidden}"
            );
            assert!(
                !md_report.contains(forbidden),
                "Markdown report leaked {forbidden}"
            );
        }
    }

    #[test]
    fn release_blocks_expired_waiver() {
        let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("../../specs/wrench-db-inspect/fixtures");
        let report = std::env::temp_dir().join("wdi-expired-waiver-report.json");
        let code = run_cli(&[
            "wrench-db-inspect".to_string(),
            "run".to_string(),
            "--manifest".to_string(),
            root.join("waiver/critical_with_expired_waiver/manifest.json")
                .display()
                .to_string(),
            "--schema-dump".to_string(),
            root.join("waiver/critical_with_expired_waiver/schema.sql")
                .display()
                .to_string(),
            "--profile".to_string(),
            "release".to_string(),
            "--gate-profile-config".to_string(),
            root.join("gate-profiles/default.json")
                .display()
                .to_string(),
            "--report-json".to_string(),
            report.display().to_string(),
        ])
        .unwrap();
        assert_eq!(code, 1);
        let json: serde_json::Value =
            serde_json::from_str(&fs::read_to_string(report).unwrap()).unwrap();
        assert!(
            json["data"]["findings"]
                .as_array()
                .unwrap()
                .iter()
                .any(|f| {
                    f["rule_id"] == "WAIVER_INVALID"
                        && f["subject"]["name"] == "wv_fixture_critical_with_expired_waiver"
                })
        );
        assert!(
            json["data"]["findings"]
                .as_array()
                .unwrap()
                .iter()
                .any(|f| { f["gate"]["reason"] == "waiver expired" })
        );
    }

    #[test]
    fn release_blocks_incomplete_waiver() {
        let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("../../specs/wrench-db-inspect/fixtures");
        let report = std::env::temp_dir().join("wdi-incomplete-waiver-report.json");
        let code = run_cli(&[
            "wrench-db-inspect".to_string(),
            "run".to_string(),
            "--manifest".to_string(),
            root.join("waiver/critical_with_incomplete_waiver/manifest.json")
                .display()
                .to_string(),
            "--schema-dump".to_string(),
            root.join("waiver/critical_with_incomplete_waiver/schema.sql")
                .display()
                .to_string(),
            "--profile".to_string(),
            "release".to_string(),
            "--gate-profile-config".to_string(),
            root.join("gate-profiles/default.json")
                .display()
                .to_string(),
            "--report-json".to_string(),
            report.display().to_string(),
        ])
        .unwrap();
        assert_eq!(code, 1);
        let json: serde_json::Value =
            serde_json::from_str(&fs::read_to_string(report).unwrap()).unwrap();
        assert!(
            json["data"]["findings"]
                .as_array()
                .unwrap()
                .iter()
                .any(|f| {
                    f["rule_id"] == "WAIVER_INVALID"
                        && f["subject"]["name"] == "wv_fixture_critical_with_incomplete_waiver"
                })
        );
        assert!(
            json["data"]["findings"]
                .as_array()
                .unwrap()
                .iter()
                .any(|f| { f["gate"]["reason"] == "waiver missing reviewer" })
        );
    }

    #[test]
    fn valid_waiver_unblocks_gate_but_keeps_finding() {
        let (schema, manifest) = fixture("waiver/critical_with_valid_expiring_waiver");
        let findings = inspect(&schema, &manifest);
        let finding = findings
            .iter()
            .find(|f| f.rule_id == "RLS_REQUIRED_TENANT_TABLE")
            .unwrap();
        assert_eq!(finding.waiver_id.as_deref(), Some("wv_fixture_rls_001"));
        assert!(!GateProfiles::builtin().gate_blocked("protected_branch", &findings));
    }
}
