use crate::finding::Finding;
use sqlparser::{
    ast::{
        AlterColumnOperation, AlterTableOperation, ColumnOption, Expr, GrantObjects, Privileges,
        Statement, TableConstraint,
    },
    dialect::PostgreSqlDialect,
    parser::Parser,
};
use std::collections::BTreeSet;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ForeignKeyFact {
    pub table: String,
    pub column: String,
    pub referenced_table: String,
    pub referenced_column: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PolicyFact {
    pub table: String,
    pub name: String,
    pub using_expr: Option<Expr>,
    pub with_check_expr: Option<Expr>,
}

#[derive(Debug, Default)]
pub struct SchemaFacts {
    pub tables: BTreeSet<String>,
    pub rls_enabled: BTreeSet<String>,
    pub force_rls: BTreeSet<String>,
    pub grant_all: BTreeSet<(String, String)>,
    pub grant_roles: BTreeSet<String>,
    pub foreign_keys: Vec<ForeignKeyFact>,
    pub policies: Vec<PolicyFact>,
    pub dangerous: Vec<Finding>,
}

pub fn collect_schema_facts(schema: &str) -> SchemaFacts {
    let dialect = PostgreSqlDialect {};
    let mut facts = SchemaFacts::default();

    for stmt in parse_sql_lenient(schema, &dialect) {
        match stmt {
            Statement::CreateTable(create) => {
                let table_name = create.name.to_string();
                facts.tables.insert(table_name.clone());
                for column in &create.columns {
                    for opt in &column.options {
                        if let ColumnOption::ForeignKey(fk) = &opt.option {
                            facts.foreign_keys.push(ForeignKeyFact {
                                table: table_name.clone(),
                                column: column.name.to_string(),
                                referenced_table: fk.foreign_table.to_string(),
                                referenced_column: fk
                                    .referred_columns
                                    .first()
                                    .map(ToString::to_string)
                                    .unwrap_or_else(|| "id".to_string()),
                            });
                        }
                    }
                }
                for constraint in &create.constraints {
                    if let TableConstraint::ForeignKey(fk) = constraint {
                        for (idx, column) in fk.columns.iter().enumerate() {
                            facts.foreign_keys.push(ForeignKeyFact {
                                table: table_name.clone(),
                                column: column.to_string(),
                                referenced_table: fk.foreign_table.to_string(),
                                referenced_column: fk
                                    .referred_columns
                                    .get(idx)
                                    .or_else(|| fk.referred_columns.first())
                                    .map(ToString::to_string)
                                    .unwrap_or_else(|| "id".to_string()),
                            });
                        }
                    }
                }
            }
            Statement::CreatePolicy(policy) => {
                facts.policies.push(PolicyFact {
                    table: policy.table_name.to_string(),
                    name: policy.name.to_string(),
                    using_expr: policy.using.clone(),
                    with_check_expr: policy.with_check.clone(),
                });
            }
            Statement::AlterTable(alter) => {
                if alter
                    .operations
                    .iter()
                    .any(|op| matches!(op, AlterTableOperation::EnableRowLevelSecurity))
                {
                    facts.rls_enabled.insert(alter.name.to_string());
                }
                if alter
                    .operations
                    .iter()
                    .any(|op| matches!(op, AlterTableOperation::ForceRowLevelSecurity))
                {
                    facts.force_rls.insert(alter.name.to_string());
                }
                for op in &alter.operations {
                    match op {
                        AlterTableOperation::DisableRowLevelSecurity => {
                            facts.dangerous.push(Finding::new(
                                "DISABLE_RLS_FORBIDDEN",
                                "migration_safety",
                                "critical",
                                "table",
                                &alter.name.to_string(),
                            ))
                        }
                        AlterTableOperation::DropColumn { .. } => {
                            facts.dangerous.push(Finding::new(
                                "DROP_COLUMN_DANGEROUS",
                                "migration_safety",
                                "high",
                                "table",
                                &alter.name.to_string(),
                            ))
                        }
                        AlterTableOperation::DropConstraint { .. } => {
                            facts.dangerous.push(Finding::new(
                                "DROP_CONSTRAINT_DANGEROUS",
                                "migration_safety",
                                "high",
                                "table",
                                &alter.name.to_string(),
                            ))
                        }
                        AlterTableOperation::DropForeignKey { .. } => {
                            facts.dangerous.push(Finding::new(
                                "DROP_FOREIGN_KEY_DANGEROUS",
                                "migration_safety",
                                "high",
                                "table",
                                &alter.name.to_string(),
                            ))
                        }
                        AlterTableOperation::NoForceRowLevelSecurity => {
                            facts.dangerous.push(Finding::new(
                                "NO_FORCE_RLS_FORBIDDEN",
                                "migration_safety",
                                "critical",
                                "table",
                                &alter.name.to_string(),
                            ))
                        }
                        AlterTableOperation::AlterColumn {
                            column_name,
                            op: AlterColumnOperation::DropNotNull,
                        } => facts.dangerous.push(Finding::new(
                            "ALTER_COLUMN_DROP_NOT_NULL_DANGEROUS",
                            "migration_safety",
                            "high",
                            "column",
                            &format!("{}.{}", alter.name, column_name),
                        )),
                        _ => {}
                    }
                }
            }
            Statement::Grant(grant) => {
                for grantee in &grant.grantees {
                    facts.grant_roles.insert(grantee.to_string());
                }
                if matches!(grant.privileges, Privileges::All { .. }) {
                    if grant
                        .grantees
                        .iter()
                        .any(|g| g.to_string().eq_ignore_ascii_case("PUBLIC"))
                    {
                        facts.dangerous.push(Finding::new(
                            "GRANT_ALL_TO_PUBLIC_DANGEROUS",
                            "grant_privilege",
                            "critical",
                            "grant",
                            "PUBLIC",
                        ));
                    }
                    if let Some(objects) = grant.objects {
                        match objects {
                            GrantObjects::Tables(tables) => {
                                for table in tables {
                                    for grantee in &grant.grantees {
                                        facts
                                            .grant_all
                                            .insert((table.to_string(), grantee.to_string()));
                                    }
                                }
                            }
                            GrantObjects::Schemas(schemas) => {
                                for schema in schemas {
                                    facts.dangerous.push(Finding::new(
                                        "GRANT_ALL_ON_SCHEMA_DANGEROUS",
                                        "grant_privilege",
                                        "high",
                                        "schema",
                                        &schema.to_string(),
                                    ));
                                }
                            }
                            GrantObjects::AllTablesInSchema { schemas } => {
                                for schema in schemas {
                                    facts.dangerous.push(Finding::new(
                                        "GRANT_ALL_TABLES_IN_SCHEMA_DANGEROUS",
                                        "grant_privilege",
                                        "high",
                                        "schema",
                                        &schema.to_string(),
                                    ));
                                }
                            }
                            _ => {}
                        }
                    }
                }
            }
            Statement::DropPolicy(policy) => {
                facts.dangerous.push(Finding::new(
                    "DROP_POLICY_DANGEROUS",
                    "migration_safety",
                    "critical",
                    "table",
                    &policy.table_name.to_string(),
                ));
            }
            Statement::Drop { names, .. } => {
                for name in names {
                    facts.dangerous.push(Finding::new(
                        "DROP_TABLE_DANGEROUS",
                        "migration_safety",
                        "critical",
                        "table",
                        &name.to_string(),
                    ));
                }
            }
            Statement::Truncate(truncate) => {
                facts.dangerous.push(Finding::new(
                    "TRUNCATE_DANGEROUS",
                    "migration_safety",
                    "critical",
                    "table",
                    &truncate
                        .table_names
                        .first()
                        .map(ToString::to_string)
                        .unwrap_or_else(|| "unknown".to_string()),
                ));
            }
            Statement::Delete(delete) if delete.selection.is_none() => {
                facts.dangerous.push(Finding::new(
                    "UNQUALIFIED_DELETE_DANGEROUS",
                    "migration_safety",
                    "critical",
                    "table",
                    &delete.from.to_string(),
                ));
            }
            Statement::Update(update) if update.selection.is_none() => {
                facts.dangerous.push(Finding::new(
                    "UNQUALIFIED_UPDATE_DANGEROUS",
                    "migration_safety",
                    "critical",
                    "table",
                    &update.table.to_string(),
                ));
            }
            _ => {}
        }
    }

    add_text_fallback_facts(schema, &mut facts);

    facts
}

fn add_text_fallback_facts(schema: &str, facts: &mut SchemaFacts) {
    let schema_lc = schema.to_lowercase();
    // Some PostgreSQL GRANT forms involving PUBLIC may be rejected by the parser depending on
    // exact grammar support. Keep this fallback narrow: any GRANT ALL to PUBLIC is unsafe enough
    // to block, and reports contain only the synthetic subject `PUBLIC`, not SQL text.
    if schema_lc.contains("grant all")
        && schema_lc.contains(" to public")
        && !facts
            .dangerous
            .iter()
            .any(|f| f.rule_id == "GRANT_ALL_TO_PUBLIC_DANGEROUS")
    {
        facts.dangerous.push(Finding::new(
            "GRANT_ALL_TO_PUBLIC_DANGEROUS",
            "grant_privilege",
            "critical",
            "grant",
            "PUBLIC",
        ));
    }

    if schema_lc.contains("set row_security = off") || schema_lc.contains("set row_security to off")
    {
        facts.dangerous.push(Finding::new(
            "SET_ROW_SECURITY_OFF_FORBIDDEN",
            "migration_safety",
            "critical",
            "session_setting",
            "row_security",
        ));
    }

    if schema_lc.contains("alter default privileges") && schema_lc.contains("grant all") {
        facts.dangerous.push(Finding::new(
            "DEFAULT_PRIVILEGES_GRANT_ALL_DANGEROUS",
            "grant_privilege",
            "high",
            "default_privileges",
            "future_objects",
        ));
    }
}

fn parse_sql_lenient(schema: &str, dialect: &PostgreSqlDialect) -> Vec<Statement> {
    if let Ok(stmts) = Parser::parse_sql(dialect, schema) {
        return stmts;
    }

    // PostgreSQL extensions/functions can be ahead of parser support. Parse each statement
    // independently so one unsupported construct does not hide table/grant/RLS facts.
    schema
        .split(';')
        .filter_map(|chunk| {
            let sql = chunk.trim();
            if sql.is_empty() {
                None
            } else {
                Parser::parse_sql(dialect, &format!("{sql};")).ok()
            }
        })
        .flatten()
        .collect()
}
