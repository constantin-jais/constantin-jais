use serde::Deserialize;

#[derive(Debug, Deserialize)]
struct ManifestEnvelope {
    data: ManifestData,
}

#[derive(Debug, Deserialize)]
pub struct ManifestData {
    pub product: String,
    pub roles: ManifestRoles,
    pub tables: Vec<TableSpec>,
    #[serde(default)]
    pub waivers: Vec<WaiverSpec>,
}

#[derive(Debug, Deserialize)]
pub struct ManifestRoles {
    #[serde(default)]
    pub app: Vec<String>,
}

#[derive(Debug, Clone, Deserialize, PartialEq, Eq)]
pub struct TableSpec {
    pub name: String,
    pub classification: String,
    #[serde(default)]
    pub contains_embeddings: bool,
}

#[derive(Debug, Clone, Deserialize, PartialEq, Eq)]
pub struct WaiverSpec {
    pub id: String,
    pub rule_id: String,
    pub subject: WaiverSubject,
    pub expires_at: Option<String>,
    pub owner_actor_ref: Option<String>,
    pub reviewer_actor_ref: Option<String>,
}

#[derive(Debug, Clone, Deserialize, PartialEq, Eq)]
pub struct WaiverSubject {
    pub name: String,
}

pub fn parse_manifest(raw: &str) -> Result<ManifestData, String> {
    serde_json::from_str::<ManifestEnvelope>(raw)
        .map(|env| env.data)
        .map_err(|e| format!("invalid manifest JSON: {e}"))
}
