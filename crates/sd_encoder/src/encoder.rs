use crate::types::{default_fields_importance, CLMOutput, FieldImportance, SDCompressionConfig};
use serde_json::{Map, Value};
use std::collections::HashSet;

pub trait SDEncoder {
    const ROW_OPEN: &'static str = "[";
    const ROW_CLOSE: &'static str = "]";
    const COMPONENT: &'static str = "ds_compression";
    fn encode(&self, data: &Value) -> CLMOutput;
}

pub struct SDEncoderV2 {
    config: SDCompressionConfig,
    delimiter: String,
    required_paths: HashSet<String>,
}

impl SDEncoderV2 {
    pub fn new(config: SDCompressionConfig, delimiter: impl Into<String>) -> Self {
        let required_paths = config
            .required_fields
            .clone()
            .unwrap_or_default()
            .into_iter()
            .collect();
        Self {
            config,
            delimiter: delimiter.into(),
            required_paths,
        }
    }

    pub fn delimiter(&self) -> &str {
        &self.delimiter
    }

    fn encode_object(&self, obj: &Map<String, Value>) -> String {
        let normalized = self.normalize_object(obj);
        let table_fields = self.find_table_fields(&normalized);
        let preserve = self.config.preserve_structure.unwrap_or(false);

        if preserve
            && table_fields.len() == 1
            && normalized.len() == 1
            && !self.has_identity_fields(&normalized)
        {
            return self.encode_table(&table_fields[0].1);
        }

        let row = self.filter_fields(&normalized, "");
        if row.is_empty() {
            return String::new();
        }

        format!("{{{}}}{}", self.format_header(&row), self.format_row(&row))
    }

    fn encode_list(&self, items: &[Value]) -> String {
        let dict_items: Vec<&Map<String, Value>> =
            items.iter().filter_map(|v| v.as_object()).collect();

        if !dict_items.is_empty()
            && dict_items.len() == items.len()
            && Self::same_schema(&dict_items)
        {
            let maps: Vec<Map<String, Value>> = dict_items.into_iter().cloned().collect();
            return self.encode_table(&maps);
        }

        items
            .iter()
            .map(|item| match item {
                Value::Object(obj) => self.encode_object(obj),
                _ => item.to_string(),
            })
            .filter(|s| !s.is_empty())
            .collect()
    }

    fn encode_table(&self, rows: &[Map<String, Value>]) -> String {
        let filtered: Vec<Map<String, Value>> = rows
            .iter()
            .map(|r| self.filter_fields(&self.normalize_object(r), ""))
            .filter(|r| !r.is_empty())
            .collect();

        if filtered.is_empty() {
            return String::new();
        }

        let body: String = filtered.iter().map(|r| self.format_row(r)).collect();
        format!("{{{}}}{}", self.format_header(&filtered[0]), body)
    }

    fn format_header(&self, row: &Map<String, Value>) -> String {
        self.ordered_items(row)
            .into_iter()
            .map(|(key, value)| {
                if let Some(obj) = value.as_object() {
                    format!("{}:{{{}}}", key, self.format_header(obj))
                } else if Self::is_nested_table(&value) {
                    let first = value.as_array().unwrap()[0].as_object().unwrap();
                    format!("{}:{{{}}}", key, self.format_header(first))
                } else {
                    key
                }
            })
            .collect::<Vec<_>>()
            .join(&self.delimiter)
    }

    fn format_row(&self, row: &Map<String, Value>) -> String {
        let values: Vec<String> = self
            .ordered_items(row)
            .into_iter()
            .map(|(_, v)| self.format_value(&v))
            .collect();
        format!("[{}]", values.join(&self.delimiter))
    }

    fn format_value(&self, value: &Value) -> String {
        match value {
            Value::Object(obj) => {
                if obj.len() == 1 {
                    self.format_value(obj.values().next().unwrap())
                } else {
                    self.format_row(obj)
                }
            }
            Value::Array(_) if Self::is_nested_table(value) => value
                .as_array()
                .unwrap()
                .iter()
                .filter_map(|v| v.as_object())
                .map(|obj| self.format_row(obj))
                .collect(),
            Value::Array(arr) => arr
                .iter()
                .map(|v| v.to_string())
                .collect::<Vec<_>>()
                .join("+"),
            Value::Bool(b) => if *b { "true" } else { "false" }.into(),
            Value::String(s) => s.replace(&self.delimiter, ";"),
            _ => value.to_string(),
        }
    }

    fn normalize_object(&self, obj: &Map<String, Value>) -> Map<String, Value> {
        let mut out = Map::new();
        for (key, value) in obj {
            let normalized = self.normalize_value(value, key);
            let is_empty_arr = normalized.as_array().map(|a| a.is_empty()).unwrap_or(false);
            if is_empty_arr && !self.is_required_path(key) {
                continue;
            }
            out.insert(key.clone(), normalized);
        }
        out
    }

    fn normalize_value(&self, value: &Value, key: &str) -> Value {
        match value {
            Value::Object(obj) => Value::Object(self.normalize_object(obj)),
            Value::Array(arr) if !arr.is_empty() && arr.iter().all(|v| v.is_object()) => {
                Value::Array(
                    arr.iter()
                        .filter_map(|v| v.as_object())
                        .map(|obj| Value::Object(self.normalize_object(obj)))
                        .collect(),
                )
            }
            Value::String(s) => {
                if let Some(limit) = self
                    .config
                    .max_truncation_mapping
                    .as_ref()
                    .and_then(|m| m.get(key))
                {
                    if s.len() > *limit {
                        return Value::String(format!("{}...", &s[..*limit]));
                    }
                }
                if let Some(max) = self.config.max_truncation_length {
                    let max = max as usize;
                    if s.len() > max {
                        return Value::String(format!("{}...", &s[..max]));
                    }
                }
                value.clone()
            }
            _ => value.clone(),
        }
    }

    fn filter_fields(&self, obj: &Map<String, Value>, path: &str) -> Map<String, Value> {
        let mut out = Map::new();
        let preserve = self.config.preserve_structure.unwrap_or(false);

        for (key, value) in obj {
            let full_path = if path.is_empty() {
                key.clone()
            } else {
                format!("{path}.{key}")
            };

            if !self.should_include_path(&full_path, value) {
                continue;
            }

            if value.is_object() && preserve {
                let nested = self.filter_fields(value.as_object().unwrap(), &full_path);
                if !nested.is_empty() {
                    out.insert(key.clone(), Value::Object(nested));
                }
            } else if Self::is_nested_table(value) && preserve {
                let arr = value.as_array().unwrap();
                let first = self.filter_fields(arr[0].as_object().unwrap(), &full_path);
                let cl_first = first.clone();
                if !first.is_empty() {
                    let kept: HashSet<&String> = first.keys().collect();
                    let mut filtered = vec![Value::Object(cl_first)];
                    for item in &arr[1..] {
                        if let Some(obj) = item.as_object() {
                            let row: Map<_, _> = obj
                                .iter()
                                .filter(|(k, _)| kept.contains(k))
                                .map(|(k, v)| (k.clone(), v.clone()))
                                .collect();
                            filtered.push(Value::Object(row));
                        }
                    }
                    out.insert(key.clone(), Value::Array(filtered));
                }
            } else {
                out.insert(key.clone(), value.clone());
            }
        }
        out
    }

    fn should_include_path(&self, path: &str, value: &Value) -> bool {
        if self.config.drop_non_required_fields.unwrap_or(false) && !self.required_paths.is_empty()
        {
            if self.required_paths.contains(path) {
                return true;
            }
            return self
                .required_paths
                .iter()
                .any(|r| r.starts_with(&format!("{path}.")));
        }

        let key = path.split('.').last().unwrap_or(path);

        if let Some(excluded) = &self.config.excluded_fields {
            if excluded.iter().any(|e| e == key) {
                return false;
            }
        }

        if let Some(required) = &self.config.required_fields {
            if required.iter().any(|r| r == key) {
                return true;
            }
        }

        let threshold = self
            .config
            .importance_threshold
            .clone()
            .unwrap_or(FieldImportance::LOW);

        if let Some(fi) = &self.config.field_importance {
            if let Some(importance) = fi.get(key) {
                return importance >= &threshold;
            }
        }

        if self.config.auto_detect.unwrap_or(false) {
            return self.detect_field_importance(key, value) >= threshold;
        }

        true
    }

    fn is_required_path(&self, key: &str) -> bool {
        self.required_paths
            .iter()
            .any(|rp| rp == key || rp.starts_with(&format!("{key}.")))
    }

    fn find_table_fields<'a>(
        &self,
        obj: &'a Map<String, Value>,
    ) -> Vec<(&'a String, Vec<Map<String, Value>>)> {
        obj.iter()
            .filter_map(|(k, v)| {
                v.as_array().and_then(|arr| {
                    if !arr.is_empty() && arr.iter().all(|x| x.is_object()) {
                        Some((
                            k,
                            arr.iter().filter_map(|x| x.as_object().cloned()).collect(),
                        ))
                    } else {
                        None
                    }
                })
            })
            .collect()
    }

    fn has_identity_fields(&self, obj: &Map<String, Value>) -> bool {
        let simple: HashSet<&str> = SDCompressionConfig::simple_fields()
            .iter()
            .copied()
            .collect();
        obj.keys()
            .any(|k| simple.contains(k.to_lowercase().as_str()))
    }

    fn is_nested_table(value: &Value) -> bool {
        value.as_array().map_or(false, |arr| {
            !arr.is_empty()
                && arr.iter().all(|x| x.is_object())
                && Self::same_schema(&arr.iter().filter_map(|x| x.as_object()).collect::<Vec<_>>())
        })
    }

    fn same_schema(rows: &[&Map<String, Value>]) -> bool {
        if rows.is_empty() {
            return true;
        }
        let keys: HashSet<&String> = rows[0].keys().collect();
        rows.iter()
            .all(|r| r.keys().collect::<HashSet<_>>() == keys)
    }

    fn ordered_items(&self, obj: &Map<String, Value>) -> Vec<(String, Value)> {
        let simple_set: HashSet<&str> = SDCompressionConfig::simple_fields()
            .iter()
            .copied()
            .collect();
        let mut simple: Vec<(String, Value)> = Vec::new();
        let mut complex: Vec<(String, Value)> = Vec::new();

        for (k, v) in obj {
            if simple_set.contains(k.to_lowercase().as_str()) {
                simple.push((k.clone(), v.clone()));
            } else {
                complex.push((k.clone(), v.clone()));
            }
        }

        simple.sort_by_key(|(k, _)| {
            self.config
                .default_fields_order
                .iter()
                .position(|f| f == k)
                .unwrap_or(999)
        });

        simple.into_iter().chain(complex).collect()
    }

    fn detect_field_importance(&self, key: &str, value: &Value) -> FieldImportance {
        let key_lower = key.to_lowercase();
        let defaults = default_fields_importance();

        for (pattern, importance) in &defaults {
            if key_lower.contains(pattern) {
                return importance.clone();
            }
        }

        if key_lower.starts_with('_') {
            return FieldImportance::LOW;
        }
        if key_lower.ends_with("_at") || key_lower.ends_with("_date") {
            return FieldImportance::LOW;
        }

        let is_empty = value.is_null() || value.as_str().map(|s| s.is_empty()).unwrap_or(false);
        if is_empty {
            return FieldImportance::LOW;
        }

        if let Some(s) = value.as_str() {
            if s.len() > 500 {
                return FieldImportance::MEDIUM;
            }
            if s.len() < 3 {
                return FieldImportance::LOW;
            }
        }

        FieldImportance::MEDIUM
    }
}

impl SDEncoder for SDEncoderV2 {
    fn encode(&self, data: &Value) -> CLMOutput {
        let compressed = match data {
            Value::Object(obj) => self.encode_object(obj),
            Value::Array(arr) => self.encode_list(arr),
            _ => data.to_string(),
        };

        CLMOutput::new(data.clone(), Self::COMPONENT.to_string(), compressed)
    }
}
