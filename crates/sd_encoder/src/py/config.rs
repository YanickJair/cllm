use crate::{
    py::enums::PyFieldImportance,
    types::{FieldImportance, SDCompressionConfig},
};
use pyo3::prelude::*;
use std::collections::HashMap;

#[pyclass(skip_from_py_object, name = "SDCompressionConfig")]
#[derive(Clone)]
pub struct PySDCompressionConfig {
    pub inner: SDCompressionConfig,
}

impl From<PySDCompressionConfig> for SDCompressionConfig {
    fn from(py: PySDCompressionConfig) -> Self {
        py.inner
    }
}

#[pymethods]
impl PySDCompressionConfig {
    #[new]
    #[pyo3(signature = (
        required_fields=None,
        auto_detect=None,
        drop_non_required_fields=None,
        importance_threshold=None,
        field_importance=None,
        excluded_fields=None,
        max_truncation_length=None,
        preserve_structure=None,
        max_truncation_mapping=None,
        default_fields_order=None,
    ))]
    fn new(
        required_fields: Option<Vec<String>>,
        auto_detect: Option<bool>,
        drop_non_required_fields: Option<bool>,
        importance_threshold: Option<PyFieldImportance>,
        field_importance: Option<HashMap<String, PyFieldImportance>>,
        excluded_fields: Option<Vec<String>>,
        max_truncation_length: Option<u16>,
        preserve_structure: Option<bool>,
        max_truncation_mapping: Option<HashMap<String, usize>>,
        default_fields_order: Option<Vec<String>>,
    ) -> Self {
        let inner = SDCompressionConfig::new(
            required_fields,
            auto_detect,
            drop_non_required_fields,
            importance_threshold.map(FieldImportance::from),
            field_importance.map(|m| {
                m.into_iter()
                    .map(|(k, v)| (k, FieldImportance::from(v)))
                    .collect()
            }),
            excluded_fields,
            max_truncation_length,
            preserve_structure,
            max_truncation_mapping,
            default_fields_order.unwrap_or_default(),
        );
        Self { inner }
    }

    #[getter]
    pub fn required_fields(&self) -> Option<Vec<String>> {
        self.inner.required_fields.clone()
    }

    #[getter]
    pub fn auto_detect(&self) -> Option<bool> {
        self.inner.auto_detect
    }

    #[getter]
    pub fn preserve_structure(&self) -> Option<bool> {
        self.inner.preserve_structure
    }

    #[getter]
    pub fn drop_non_required_fields(&self) -> Option<bool> {
        self.inner.drop_non_required_fields
    }

    #[getter]
    pub fn max_truncation_length(&self) -> Option<u16> {
        self.inner.max_truncation_length
    }

    #[getter]
    pub fn excluded_fields(&self) -> Option<Vec<String>> {
        self.inner.excluded_fields.clone()
    }

    #[getter]
    pub fn default_fields_order(&self) -> Vec<String> {
        self.inner.default_fields_order.clone()
    }

    #[getter]
    pub fn field_importance(&self) -> Option<HashMap<String, PyFieldImportance>> {
        self.inner.field_importance.clone().map(|m| {
            m.into_iter()
                .map(|(k, v)| (k, PyFieldImportance::from(v)))
                .collect()
        })
    }

    #[getter]
    pub fn max_truncation_mapping(&self) -> Option<HashMap<String, usize>> {
        self.inner.max_truncation_mapping.clone()
    }

    pub fn __repr__(&self) -> String {
        format!(
            "SDCompressionConfig(preserve_structure={:?}, auto_detect={:?}, \
            drop_non_required_fields={:?}, required_fields={:?})",
            self.inner.preserve_structure,
            self.inner.auto_detect,
            self.inner.drop_non_required_fields,
            self.inner.required_fields,
        )
    }
}
