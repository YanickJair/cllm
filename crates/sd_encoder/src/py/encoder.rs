use crate::{
    encoder::{SDEncoder, SDEncoderV2},
    py::{config::PySDCompressionConfig, output::PyCLMOutput},
};
use pyo3::prelude::*;
use pythonize::depythonize;

#[pyclass(name = "SDEncoderV2")]
pub struct PySDEncoderV2 {
    pub inner: SDEncoderV2,
    pub delimiter: String,
}

impl PySDEncoderV2 {
    fn convert_error(e: impl std::fmt::Display) -> PyErr {
        pyo3::exceptions::PyValueError::new_err(e.to_string())
    }
}

#[pymethods]
impl PySDEncoderV2 {
    #[new]
    #[pyo3(signature = (config, delimiter = ","))]
    fn new(config: PyRef<'_, PySDCompressionConfig>, delimiter: &str) -> Self {
        Self {
            inner: SDEncoderV2::new(config.inner.clone(), delimiter),
            delimiter: delimiter.to_uppercase(),
        }
    }

    pub fn encode(&self, data: &Bound<'_, PyAny>) -> PyResult<PyCLMOutput> {
        let value = depythonize(data).map_err(Self::convert_error)?;
        Ok(PyCLMOutput::from(self.inner.encode(&value)))
    }

    pub fn encode_validated(&self, data: &Bound<'_, PyAny>) -> PyResult<PyCLMOutput> {
        // Encode data and validate it before returning it.
        // If compression failed to produce better number
        // the original input is returned
        let value = depythonize(data).map_err(Self::convert_error)?;
        let mut output = PyCLMOutput::from(self.inner.encode(&value));
        output.inner.validate_compressed();
        output.inner.validate_compression_ratio();
        Ok(output)
    }

    #[getter]
    pub fn delimiter(&self) -> &str {
        &self.delimiter
    }

    pub fn __repr__(&self) -> String {
        format!("SDEncoderV2(delimiter={:?})", self.delimiter)
    }
}
