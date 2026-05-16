use regex::Regex;
use serde_json::Value;
use std::collections::HashMap;

#[derive(Debug, Clone)]
pub struct CLMOutput {
    pub original: Value,
    pub component: String,
    pub compressed: String,
    pub metadata: Option<HashMap<String, String>>,
}

#[derive(Debug, Clone)]
pub struct SDCompressionConfig {
    pub required_fields: Option<Vec<String>>,
    pub auto_detect: Option<bool>,
    pub drop_non_required_fields: Option<bool>,
    pub field_importance: Option<HashMap<String, FieldImportance>>,
    pub importance_threshold: Option<FieldImportance>,
    pub excluded_fields: Option<Vec<String>>,
    pub max_truncation_length: Option<u16>,
    pub preserve_structure: Option<bool>,
    pub max_truncation_mapping: Option<HashMap<String, usize>>, // per-field truncation
    pub default_fields_order: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, PartialOrd)]
#[repr(u8)]
pub enum FieldImportance {
    LOW = 1,
    MEDIUM = 2,
    HIGH = 3,
    CRITICAL = 4,
}

impl CLMOutput {
    pub fn new(original: Value, component: String, compressed: String) -> Self {
        Self {
            original,
            component,
            compressed,
            metadata: None,
        }
    }

    pub fn original(&self) -> &Value {
        &self.original
    }
    pub fn component(&self) -> &str {
        &self.component
    }
    pub fn compressed(&self) -> &str {
        &self.compressed
    }
    pub fn metadata(&self) -> Option<&HashMap<String, String>> {
        self.metadata.as_ref()
    }

    pub fn validate_compression_ratio(&mut self) {
        if Self::c_tokens(&self) > Self::n_tokens(&self) {
            self.compressed = self.original.to_string();
        }
    }

    pub fn validate_compressed(&mut self) {
        let rgx = Regex::new(r"\s+").unwrap();
        self.compressed = rgx.replace(&self.compressed, " ").trim().to_string();
    }

    fn estimate_tokens(data: &str) -> u32 {
        (data.len() as u32 / 4).max(1)
    }

    pub fn n_tokens(&self) -> u32 {
        Self::estimate_tokens(&self.original.to_string())
    }

    pub fn c_tokens(&self) -> u32 {
        Self::estimate_tokens(&self.compressed)
    }

    pub fn compression_ratio(&self) -> f32 {
        (1.0 - (self.c_tokens() as f32 / self.n_tokens() as f32)) * 100.0
    }
}

pub fn default_fields_importance<'a>() -> HashMap<&'static str, FieldImportance> {
    let mut hm = HashMap::new();
    hm.insert("id", FieldImportance::CRITICAL);
    hm.insert("uuid", FieldImportance::CRITICAL);
    hm.insert("external_id", FieldImportance::CRITICAL);
    hm.insert("name", FieldImportance::CRITICAL);
    hm.insert("title", FieldImportance::CRITICAL);
    hm.insert("type", FieldImportance::MEDIUM);
    hm.insert("category", FieldImportance::HIGH);
    hm.insert("subcategory", FieldImportance::LOW);
    hm.insert("description", FieldImportance::MEDIUM);
    hm.insert("details", FieldImportance::HIGH);
    hm.insert("notes", FieldImportance::HIGH);
    hm.insert("status", FieldImportance::HIGH);
    hm.insert("priority", FieldImportance::HIGH);
    hm.insert("severity", FieldImportance::HIGH);
    hm.insert("resolution", FieldImportance::MEDIUM);
    hm.insert("owner", FieldImportance::MEDIUM);
    hm.insert("assignee", FieldImportance::MEDIUM);
    hm.insert("department", FieldImportance::MEDIUM);
    hm.insert("channel", FieldImportance::MEDIUM);
    hm.insert("language", FieldImportance::MEDIUM);
    hm.insert("source", FieldImportance::LOW);
    hm.insert("metadata", FieldImportance::LOW);
    hm.insert("created_at", FieldImportance::LOW);
    hm.insert("updated_at", FieldImportance::LOW);
    hm.insert("version", FieldImportance::LOW);

    hm
}

#[allow(dead_code)]
impl SDCompressionConfig {
    pub fn new(
        required_fields: Option<Vec<String>>,
        auto_detect: Option<bool>,
        drop_non_required_fields: Option<bool>,
        importance_threshold: Option<FieldImportance>,
        field_importance: Option<HashMap<String, FieldImportance>>,
        excluded_fields: Option<Vec<String>>,
        max_truncation_length: Option<u16>,
        preserve_structure: Option<bool>,
        max_truncation_mapping: Option<HashMap<String, usize>>, // per-field truncation
        default_fields_order: Vec<String>,
    ) -> Self {
        Self {
            required_fields: required_fields,
            auto_detect: auto_detect,
            drop_non_required_fields: drop_non_required_fields,
            importance_threshold: importance_threshold,
            field_importance: field_importance,
            excluded_fields: excluded_fields,
            max_truncation_length: max_truncation_length,
            preserve_structure: preserve_structure,
            max_truncation_mapping: max_truncation_mapping,
            default_fields_order: default_fields_order,
        }
    }

    pub fn simple_fields() -> &'static [&'static str] {
        &[
            "id",
            "uuid",
            "title",
            "name",
            "type",
            "priority",
            "email",
            "article_id",
            "product_id",
        ]
    }
}
