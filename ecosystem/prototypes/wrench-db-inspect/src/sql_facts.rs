use crate::finding::Finding;
use sqlparser::{
    ast::{AlterTableOperation, GrantObjects, Privileges, Statement},
    dialect::PostgreSqlDialect,
    parser::Parser,
};
use std::collections::BTreeSet;

#[derive(Debug, Default)]
pub struct SchemaFacts {
    pub tables: BTreeSet<String>,
    pub rls_enabled: BTreeSet<String>,
    pub force_rls: BTreeSet<String>,
    pub grant_all: BTreeSet<(String, String)>,
    pub dangerous: Vec<Finding>,
}

pub fn collect_schema_facts(schema: &str) -> SchemaFacts {
    let dialect = PostgreSqlDialect {};
    let mut facts = SchemaFacts::default();

    for stmt in parse_sql_lenient(schema, &dialect) {
        match stmt {
            Statement::CreateTable(create) => {
                facts.tables.insert(create.name.to_string());
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
                        _ => {}
                    }
                }
            }
            Statement::Grant(grant) => {
                if matches!(grant.privileges, Privileges::All { .. }) {
                    if let Some(GrantObjects::Tables(tables)) = grant.objects {
                        for table in tables {
                            for grantee in &grant.grantees {
                                facts
                                    .grant_all
                                    .insert((table.to_string(), grantee.to_string()));
                            }
                        }
                    }
                }
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
            Statement::Delete(delete) => {
                if delete.selection.is_none() {
                    facts.dangerous.push(Finding::new(
                        "UNQUALIFIED_DELETE_DANGEROUS",
                        "migration_safety",
                        "critical",
                        "table",
                        &delete.from.to_string(),
                    ));
                }
            }
            Statement::Update(update) => {
                if update.selection.is_none() {
                    facts.dangerous.push(Finding::new(
                        "UNQUALIFIED_UPDATE_DANGEROUS",
                        "migration_safety",
                        "critical",
                        "table",
                        &update.table.to_string(),
                    ));
                }
            }
            _ => {}
        }
    }

    facts
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
