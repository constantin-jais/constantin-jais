use crate::{
    finding::{Finding, severity_rank},
    manifest::ManifestData,
    sql_facts::{SchemaFacts, collect_schema_facts},
};
use sqlparser::ast::{
    BinaryOperator, Expr, FunctionArg, FunctionArgExpr, FunctionArguments, JoinConstraint,
    JoinOperator, Query, Select, SetExpr, TableFactor, TableWithJoins, Value,
};
use std::collections::BTreeSet;

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

    findings.extend(
        unknown_grant_role_findings(&facts, manifest)
            .into_iter()
            .map(|f| with_waiver(f, manifest)),
    );

    findings.extend(security_definer_findings(schema));
    findings.extend(view_and_function_tenant_filter_findings(schema, manifest));

    for table in manifest
        .tables
        .iter()
        .filter(|t| t.classification == "tenant_scoped")
    {
        findings.extend(
            tenant_derivation_findings(&facts, &table.name, table.tenant_derivation.as_deref())
                .into_iter()
                .map(|f| with_waiver(f, manifest)),
        );

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

fn unknown_grant_role_findings(facts: &SchemaFacts, manifest: &ManifestData) -> Vec<Finding> {
    let known_roles = manifest
        .roles
        .app
        .iter()
        .chain(manifest.roles.readonly.iter())
        .chain(manifest.roles.migration.iter())
        .collect::<Vec<_>>();

    facts
        .grant_roles
        .iter()
        .filter(|role| !role.eq_ignore_ascii_case("PUBLIC"))
        .filter(|role| !known_roles.iter().any(|known| eq_ident(known, role)))
        .map(|role| {
            Finding::new(
                "GRANT_TO_UNKNOWN_ROLE",
                "grant_privilege",
                "high",
                "role",
                role,
            )
        })
        .collect()
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct TenantDerivationHop {
    child_table: String,
    child_col: String,
    parent_table: String,
    parent_exposed_col: String,
}

fn tenant_derivation_findings(
    facts: &SchemaFacts,
    table_name: &str,
    tenant_derivation: Option<&str>,
) -> Vec<Finding> {
    let Some(derivation) = tenant_derivation else {
        return Vec::new();
    };
    if derivation == "direct" || !derivation.contains("->") {
        return Vec::new();
    }

    let Some(path) = parse_tenant_derivation_path(table_name, derivation) else {
        return vec![Finding::new(
            "TENANT_DERIVATION_PATH_UNSUPPORTED",
            "tenant_isolation",
            "medium",
            "table",
            table_name,
        )];
    };

    let mut findings = Vec::new();
    let fk_path_present = path.iter().all(|hop| {
        facts.foreign_keys.iter().any(|fk| {
            eq_ident(&fk.table, &hop.child_table)
                && eq_ident(&fk.column, &hop.child_col)
                && eq_ident(&fk.referenced_table, &hop.parent_table)
                && eq_ident(&fk.referenced_column, "id")
        })
    });
    if !fk_path_present {
        findings.push(Finding::new(
            "TENANT_DERIVATION_FK_REQUIRED",
            "tenant_isolation",
            "medium",
            "table",
            table_name,
        ));
    }

    let policy_proves_derivation = facts.policies.iter().any(|policy| {
        if !eq_ident(&policy.table, table_name) {
            return false;
        }
        policy
            .using_expr
            .as_ref()
            .is_some_and(|expr| policy_expr_proves_path(expr, table_name, &path))
            || policy
                .with_check_expr
                .as_ref()
                .is_some_and(|expr| policy_expr_proves_path(expr, table_name, &path))
    });
    if !policy_proves_derivation {
        findings.push(Finding::new(
            "TENANT_DERIVATION_POLICY_REQUIRED",
            "tenant_isolation",
            "medium",
            "table",
            table_name,
        ));
    }

    findings
}

fn parse_tenant_derivation_path(
    table_name: &str,
    tenant_derivation: &str,
) -> Option<Vec<TenantDerivationHop>> {
    let parts = tenant_derivation
        .split("->")
        .map(|part| part.trim().to_lowercase())
        .filter(|part| !part.is_empty())
        .collect::<Vec<_>>();
    if parts.len() < 2 {
        return None;
    }

    let mut current_table = table_name.to_lowercase();
    let mut current_col = parts.first()?.clone();
    let mut hops = Vec::new();
    for parent_raw in parts.iter().skip(1) {
        let (parent_table, parent_exposed_col) = split_table_column(parent_raw)?;
        hops.push(TenantDerivationHop {
            child_table: current_table,
            child_col: current_col,
            parent_table: parent_table.clone(),
            parent_exposed_col: parent_exposed_col.clone(),
        });
        current_table = parent_table;
        current_col = parent_exposed_col;
    }
    Some(hops)
}

fn split_table_column(raw: &str) -> Option<(String, String)> {
    raw.rsplit_once('.')
        .map(|(table, column)| (table.trim().to_string(), column.trim().to_string()))
        .filter(|(table, column)| !table.is_empty() && !column.is_empty())
}

fn policy_expr_proves_path(expr: &Expr, policy_table: &str, path: &[TenantDerivationHop]) -> bool {
    match expr {
        Expr::Exists { subquery, negated } if !negated => {
            query_proves_path(subquery, policy_table, path)
        }
        Expr::Subquery(subquery) => query_proves_path(subquery, policy_table, path),
        Expr::Nested(inner)
        | Expr::IsFalse(inner)
        | Expr::IsNotFalse(inner)
        | Expr::IsTrue(inner)
        | Expr::IsNotTrue(inner)
        | Expr::IsNull(inner)
        | Expr::IsNotNull(inner)
        | Expr::IsUnknown(inner)
        | Expr::IsNotUnknown(inner)
        | Expr::UnaryOp { expr: inner, .. }
        | Expr::Cast { expr: inner, .. } => policy_expr_proves_path(inner, policy_table, path),
        Expr::BinaryOp { left, right, .. } => {
            policy_expr_proves_path(left, policy_table, path)
                || policy_expr_proves_path(right, policy_table, path)
        }
        Expr::InSubquery { subquery, .. } => query_proves_path(subquery, policy_table, path),
        _ => false,
    }
}

fn query_proves_path(query: &Query, policy_table: &str, path: &[TenantDerivationHop]) -> bool {
    set_expr_proves_path(&query.body, policy_table, path)
}

fn set_expr_proves_path(
    set_expr: &SetExpr,
    policy_table: &str,
    path: &[TenantDerivationHop],
) -> bool {
    match set_expr {
        SetExpr::Select(select) => select_proves_path(select, policy_table, path),
        SetExpr::Query(query) => query_proves_path(query, policy_table, path),
        SetExpr::SetOperation { left, right, .. } => {
            set_expr_proves_path(left, policy_table, path)
                || set_expr_proves_path(right, policy_table, path)
        }
        _ => false,
    }
}

fn select_proves_path(select: &Select, policy_table: &str, path: &[TenantDerivationHop]) -> bool {
    let Some(final_hop) = path.last() else {
        return false;
    };
    let conditions = select_conditions(select);
    if conditions.is_empty() {
        return false;
    }

    path.iter().all(|hop| {
        let child_refs = table_refs_for_policy_path(select, policy_table, &hop.child_table);
        let parent_refs = table_refs_for_policy_path(select, policy_table, &hop.parent_table);
        !parent_refs.is_empty()
            && conditions.iter().any(|expr| {
                expr_has_column_equality(
                    expr,
                    &parent_refs,
                    "id",
                    false,
                    &child_refs,
                    &hop.child_col,
                    eq_ident(&hop.child_table, policy_table),
                )
            })
    }) && {
        let final_parent_refs =
            table_refs_for_policy_path(select, policy_table, &final_hop.parent_table);
        !final_parent_refs.is_empty()
            && conditions.iter().any(|expr| {
                expr_has_tenant_setting_equality(
                    expr,
                    &final_parent_refs,
                    &final_hop.parent_exposed_col,
                )
            })
    }
}

fn select_conditions(select: &Select) -> Vec<&Expr> {
    let mut conditions = Vec::new();
    if let Some(selection) = &select.selection {
        conditions.push(selection);
    }
    for table in &select.from {
        collect_join_conditions(table, &mut conditions);
    }
    conditions
}

fn collect_join_conditions<'a>(table: &'a TableWithJoins, conditions: &mut Vec<&'a Expr>) {
    for join in &table.joins {
        match &join.join_operator {
            JoinOperator::Join(constraint)
            | JoinOperator::Inner(constraint)
            | JoinOperator::Left(constraint)
            | JoinOperator::LeftOuter(constraint)
            | JoinOperator::Right(constraint)
            | JoinOperator::RightOuter(constraint)
            | JoinOperator::FullOuter(constraint)
            | JoinOperator::CrossJoin(constraint)
            | JoinOperator::Semi(constraint)
            | JoinOperator::LeftSemi(constraint)
            | JoinOperator::RightSemi(constraint)
            | JoinOperator::Anti(constraint)
            | JoinOperator::LeftAnti(constraint)
            | JoinOperator::RightAnti(constraint)
            | JoinOperator::StraightJoin(constraint) => {
                if let JoinConstraint::On(expr) = constraint {
                    conditions.push(expr);
                }
            }
            _ => {}
        }
    }
}

fn table_refs_for_policy_path(
    select: &Select,
    policy_table: &str,
    table_name: &str,
) -> BTreeSet<String> {
    let mut refs = BTreeSet::new();
    if eq_ident(policy_table, table_name) {
        refs.insert(policy_table.to_lowercase());
        refs.insert(last_ident(policy_table).to_lowercase());
    }
    for table in &select.from {
        collect_table_refs(&table.relation, table_name, &mut refs);
        for join in &table.joins {
            collect_table_refs(&join.relation, table_name, &mut refs);
        }
    }
    refs
}

fn collect_table_refs(factor: &TableFactor, table_name: &str, refs: &mut BTreeSet<String>) {
    match factor {
        TableFactor::Table { name, alias, .. } if eq_ident(&name.to_string(), table_name) => {
            refs.insert(last_ident(&name.to_string()).to_lowercase());
            refs.insert(name.to_string().to_lowercase());
            if let Some(alias) = alias {
                refs.insert(alias.name.to_string().to_lowercase());
            }
        }
        TableFactor::Derived { subquery, .. } => {
            collect_query_table_refs(subquery, table_name, refs)
        }
        _ => {}
    }
}

fn collect_query_table_refs(query: &Query, table_name: &str, refs: &mut BTreeSet<String>) {
    if let SetExpr::Select(select) = &*query.body {
        for table in &select.from {
            collect_table_refs(&table.relation, table_name, refs);
            for join in &table.joins {
                collect_table_refs(&join.relation, table_name, refs);
            }
        }
    }
}

fn expr_has_column_equality(
    expr: &Expr,
    left_refs: &BTreeSet<String>,
    left_col: &str,
    left_allow_unqualified: bool,
    right_refs: &BTreeSet<String>,
    right_col: &str,
    right_allow_unqualified: bool,
) -> bool {
    match expr {
        Expr::BinaryOp {
            left,
            op: BinaryOperator::Eq,
            right,
        } => {
            (expr_is_column(left, left_refs, left_col, left_allow_unqualified)
                && expr_is_column(right, right_refs, right_col, right_allow_unqualified))
                || (expr_is_column(right, left_refs, left_col, left_allow_unqualified)
                    && expr_is_column(left, right_refs, right_col, right_allow_unqualified))
                || expr_has_column_equality(
                    left,
                    left_refs,
                    left_col,
                    left_allow_unqualified,
                    right_refs,
                    right_col,
                    right_allow_unqualified,
                )
                || expr_has_column_equality(
                    right,
                    left_refs,
                    left_col,
                    left_allow_unqualified,
                    right_refs,
                    right_col,
                    right_allow_unqualified,
                )
        }
        Expr::BinaryOp { left, right, .. } => {
            expr_has_column_equality(
                left,
                left_refs,
                left_col,
                left_allow_unqualified,
                right_refs,
                right_col,
                right_allow_unqualified,
            ) || expr_has_column_equality(
                right,
                left_refs,
                left_col,
                left_allow_unqualified,
                right_refs,
                right_col,
                right_allow_unqualified,
            )
        }
        Expr::Nested(inner)
        | Expr::UnaryOp { expr: inner, .. }
        | Expr::Cast { expr: inner, .. } => expr_has_column_equality(
            inner,
            left_refs,
            left_col,
            left_allow_unqualified,
            right_refs,
            right_col,
            right_allow_unqualified,
        ),
        _ => false,
    }
}

fn expr_has_tenant_setting_equality(
    expr: &Expr,
    tenant_table_refs: &BTreeSet<String>,
    tenant_col: &str,
) -> bool {
    match expr {
        Expr::BinaryOp {
            left,
            op: BinaryOperator::Eq,
            right,
        } => {
            (expr_is_column(left, tenant_table_refs, tenant_col, false)
                && expr_is_current_workspace_setting(right))
                || (expr_is_column(right, tenant_table_refs, tenant_col, false)
                    && expr_is_current_workspace_setting(left))
                || expr_has_tenant_setting_equality(left, tenant_table_refs, tenant_col)
                || expr_has_tenant_setting_equality(right, tenant_table_refs, tenant_col)
        }
        Expr::BinaryOp { left, right, .. } => {
            expr_has_tenant_setting_equality(left, tenant_table_refs, tenant_col)
                || expr_has_tenant_setting_equality(right, tenant_table_refs, tenant_col)
        }
        Expr::Nested(inner)
        | Expr::UnaryOp { expr: inner, .. }
        | Expr::Cast { expr: inner, .. } => {
            expr_has_tenant_setting_equality(inner, tenant_table_refs, tenant_col)
        }
        _ => false,
    }
}

fn expr_is_column(
    expr: &Expr,
    table_refs: &BTreeSet<String>,
    column: &str,
    allow_unqualified: bool,
) -> bool {
    expr_column_parts(expr).is_some_and(|parts| {
        parts.last().is_some_and(|last| eq_ident(last, column))
            && ((allow_unqualified && parts.len() == 1)
                || (parts.len() > 1
                    && table_refs.iter().any(|table_ref| {
                        eq_ident(&parts[..parts.len() - 1].join("."), table_ref)
                            || parts
                                .get(parts.len().saturating_sub(2))
                                .is_some_and(|qualifier| eq_ident(qualifier, table_ref))
                    })))
    })
}

fn expr_column_parts(expr: &Expr) -> Option<Vec<String>> {
    match expr {
        Expr::Identifier(ident) => Some(vec![ident.to_string().to_lowercase()]),
        Expr::CompoundIdentifier(idents) => Some(
            idents
                .iter()
                .map(|ident| ident.to_string().to_lowercase())
                .collect(),
        ),
        Expr::Nested(inner) | Expr::Cast { expr: inner, .. } => expr_column_parts(inner),
        _ => None,
    }
}

fn expr_is_current_workspace_setting(expr: &Expr) -> bool {
    match expr {
        Expr::Cast { expr: inner, .. } | Expr::Nested(inner) => {
            expr_is_current_workspace_setting(inner)
        }
        Expr::Function(function) if eq_ident(&function.name.to_string(), "current_setting") => {
            let FunctionArguments::List(args) = &function.args else {
                return false;
            };
            args.args.first().is_some_and(|arg| match arg {
                FunctionArg::Unnamed(FunctionArgExpr::Expr(Expr::Value(value))) => {
                    match &value.value {
                        Value::SingleQuotedString(v) | Value::EscapedStringLiteral(v) => {
                            v == "app.workspace_id"
                        }
                        _ => false,
                    }
                }
                _ => false,
            })
        }
        _ => false,
    }
}

fn last_ident(name: &str) -> &str {
    name.rsplit('.').next().unwrap_or(name)
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
