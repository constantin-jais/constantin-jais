use crate::{
    finding::{Finding, severity_rank},
    manifest::ManifestData,
    sql_facts::collect_schema_facts,
};

pub fn inspect(schema: &str, manifest: &ManifestData) -> Vec<Finding> {
    let facts = collect_schema_facts(schema);
    let schema_lc = schema.to_lowercase();
    let mut findings = waiver_invalid_findings(manifest);

    for table in &facts.tables {
        if !manifest.tables.iter().any(|t| eq_ident(&t.name, table)) {
            findings.push(Finding::new(
                "TABLE_CLASSIFICATION_REQUIRED",
                "manifest_coverage",
                "high",
                "table",
                table,
            ));
        }
    }

    findings.extend(
        facts
            .dangerous
            .iter()
            .cloned()
            .map(|f| with_waiver(f, manifest)),
    );

    findings.extend(security_definer_findings(schema));
    findings.extend(view_and_function_tenant_filter_findings(schema, manifest));

    for table in manifest
        .tables
        .iter()
        .filter(|t| t.classification == "tenant_scoped")
    {
        if tenant_column_nullable(schema, &table.name) {
            findings.push(with_waiver(
                Finding::new(
                    "TENANT_COLUMN_NOT_NULL_REQUIRED",
                    "rls_policy",
                    "medium",
                    "table",
                    &table.name,
                ),
                manifest,
            ));
        }

        if !facts.rls_enabled.iter().any(|t| eq_ident(t, &table.name)) {
            findings.push(with_waiver(
                Finding::new(
                    "RLS_REQUIRED_TENANT_TABLE",
                    "rls_policy",
                    "critical",
                    "table",
                    &table.name,
                ),
                manifest,
            ));
        } else if !facts.force_rls.iter().any(|t| eq_ident(t, &table.name)) {
            findings.push(with_waiver(
                Finding::new(
                    "FORCE_RLS_REQUIRED_TENANT_TABLE",
                    "rls_policy",
                    "high",
                    "table",
                    &table.name,
                ),
                manifest,
            ));
        }

        for role in &manifest.roles.app {
            if facts
                .grant_all
                .iter()
                .any(|(tbl, grantee)| eq_ident(tbl, &table.name) && eq_ident(grantee, role))
            {
                let mut f = Finding::new(
                    "GRANT_ALL_ON_TENANT_TABLE",
                    "grant_privilege",
                    "high",
                    "table",
                    &table.name,
                );
                f.role = Some(role.clone());
                findings.push(with_waiver(f, manifest));
            }
        }

        if table.contains_embeddings
            && vector_search_without_tenant_filter(&schema_lc, &table.name.to_lowercase())
        {
            findings.push(with_waiver(
                Finding::new(
                    "PGVECTOR_TENANT_FILTER_REQUIRED",
                    "pgvector_leakage",
                    "critical",
                    "function",
                    &extract_first_function_name(schema).unwrap_or_else(|| table.name.clone()),
                ),
                manifest,
            ));
        }
    }

    findings.sort_by_key(|f| (severity_rank(f.severity), f.rule_id, f.subject_name.clone()));
    findings
}

fn waiver_invalid_findings(manifest: &ManifestData) -> Vec<Finding> {
    let mut findings = Vec::new();
    for waiver in &manifest.waivers {
        let invalid = waiver.expires_at.is_none()
            || waiver
                .expires_at
                .as_deref()
                .is_some_and(|expires_at| expires_at <= "2026-06-30T00:00:00Z")
            || waiver.owner_actor_ref.as_ref().is_none_or(|v| v.is_empty())
            || waiver
                .reviewer_actor_ref
                .as_ref()
                .is_none_or(|v| v.is_empty());
        if invalid {
            findings.push(Finding::new(
                "WAIVER_INVALID",
                "manifest_coverage",
                "medium",
                "waiver",
                &waiver.id,
            ));
        }
    }
    findings
}

fn view_and_function_tenant_filter_findings(schema: &str, manifest: &ManifestData) -> Vec<Finding> {
    let tenant_tables = manifest
        .tables
        .iter()
        .filter(|t| t.classification == "tenant_scoped")
        .map(|t| t.name.to_lowercase())
        .collect::<Vec<_>>();
    let mut findings = Vec::new();

    for block in schema.split(';') {
        let block_lc = block.to_lowercase();
        let references_tenant_table = tenant_tables.iter().any(|table| {
            block_lc.contains(&format!("from {table}"))
                || block_lc.contains(&format!("join {table}"))
        });
        if !references_tenant_table || has_tenant_filter(&block_lc) {
            continue;
        }

        if block_lc.contains("create view") {
            findings.push(Finding::new(
                "VIEW_TENANT_FILTER_REQUIRED",
                "rls_policy",
                "medium",
                "view",
                &extract_named_object(block, "create view")
                    .unwrap_or_else(|| "unknown".to_string()),
            ));
        } else if block_lc.contains("create function") {
            findings.push(Finding::new(
                "FUNCTION_TENANT_FILTER_REQUIRED",
                "rls_policy",
                "medium",
                "function",
                &extract_first_function_name(block).unwrap_or_else(|| "unknown".to_string()),
            ));
        }
    }

    findings
}

fn security_definer_findings(schema: &str) -> Vec<Finding> {
    let mut findings = Vec::new();
    for block in schema.split(';') {
        let block_lc = block.to_lowercase();
        if block_lc.contains("create function")
            && block_lc.contains("security definer")
            && !block_lc.contains("search_path")
        {
            let name = extract_first_function_name(block).unwrap_or_else(|| "unknown".to_string());
            findings.push(Finding::new(
                "SECURITY_DEFINER_SEARCH_PATH_REQUIRED",
                "grant_privilege",
                "medium",
                "function",
                &name,
            ));
        }
    }
    findings
}

fn tenant_column_nullable(schema: &str, table_name: &str) -> bool {
    let schema_lc = schema.to_lowercase();
    let table_lc = table_name.to_lowercase();
    let Some(start) = schema_lc.find(&format!("create table {table_lc}")) else {
        return false;
    };
    let tail = &schema_lc[start..];
    let Some(open) = tail.find('(') else {
        return false;
    };
    let Some(close) = tail[open + 1..].find(");") else {
        return false;
    };
    let columns = &tail[open + 1..open + 1 + close];
    columns
        .lines()
        .map(str::trim)
        .any(|line| line.starts_with("organization_id") && !line.contains("not null"))
}

fn with_waiver(mut finding: Finding, manifest: &ManifestData) -> Finding {
    if let Some(w) = manifest
        .waivers
        .iter()
        .find(|w| w.rule_id == finding.rule_id && eq_ident(&w.subject.name, &finding.subject_name))
    {
        finding.waiver_id = Some(w.id.clone());
        finding.waiver_expires_at = w.expires_at.clone();
        finding.waiver_owner_present = w.owner_actor_ref.as_ref().is_some_and(|v| !v.is_empty());
        finding.waiver_reviewer_present =
            w.reviewer_actor_ref.as_ref().is_some_and(|v| !v.is_empty());
    }
    finding
}

fn vector_search_without_tenant_filter(schema_lc: &str, table_lc: &str) -> bool {
    schema_lc.contains("<->")
        && schema_lc.contains(&format!("from {table_lc}"))
        && !has_tenant_filter(schema_lc)
}

fn has_tenant_filter(sql_lc: &str) -> bool {
    sql_lc.contains("organization_id") && sql_lc.contains("current_setting('app.organization_id'")
}

fn extract_named_object(sql: &str, prefix: &str) -> Option<String> {
    let sql_lc = sql.to_lowercase();
    let start = sql_lc.find(prefix)? + prefix.len();
    let rest = sql[start..].trim();
    rest.split_whitespace()
        .next()
        .map(|s| s.trim_matches('(').to_string())
}

fn extract_first_function_name(schema: &str) -> Option<String> {
    for line in schema.lines() {
        let trimmed = line.trim();
        if trimmed.to_lowercase().starts_with("create function ") {
            return trimmed["CREATE FUNCTION ".len()..]
                .split('(')
                .next()
                .map(|s| s.trim().to_string());
        }
    }
    None
}

fn eq_ident(a: &str, b: &str) -> bool {
    a.eq_ignore_ascii_case(b)
}
