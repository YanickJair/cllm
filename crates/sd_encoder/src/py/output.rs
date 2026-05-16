use crate::types::CLMOutput;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pythonize::pythonize;

#[pyclass(skip_from_py_object, name = "CLMOutput")]
#[derive(Clone)]
pub struct PyCLMOutput {
    pub inner: CLMOutput,
}

impl From<CLMOutput> for PyCLMOutput {
    fn from(inner: CLMOutput) -> Self {
        Self { inner }
    }
}

#[pymethods]
impl PyCLMOutput {
    #[getter]
    fn compressed(&self) -> &str {
        self.inner.compressed()
    }

    #[getter]
    fn original<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        pythonize(py, self.inner.original()).map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }

    #[getter]
    fn component(&self) -> &str {
        self.inner.component()
    }

    #[getter]
    fn metadata<'py>(&self, py: Python<'py>) -> PyResult<Option<Bound<'py, PyDict>>> {
        self.inner
            .metadata()
            .map(|m| {
                let d = PyDict::new(py);
                for (k, v) in m {
                    d.set_item(k, v)?;
                }
                Ok(d)
            })
            .transpose()
    }

    fn n_tokens(&self) -> u32 {
        self.inner.n_tokens()
    }

    fn c_tokens(&self) -> u32 {
        self.inner.c_tokens()
    }

    fn compression_ratio(&self) -> f32 {
        self.inner.compression_ratio()
    }

    fn validate_compression_ratio(mut slf: PyRefMut<'_, Self>) -> PyRefMut<'_, Self> {
        slf.inner.validate_compression_ratio();
        slf
    }

    fn validate_compressed(mut slf: PyRefMut<'_, Self>) -> PyRefMut<'_, Self> {
        slf.inner.validate_compressed();
        slf
    }

    fn __repr__(&self) -> String {
        format!(
            "CLMOutput(component={:?}, c_tokens={}, n_tokens={}, ratio={:.1}%)",
            self.inner.component(),
            self.inner.c_tokens(),
            self.inner.n_tokens(),
            self.inner.compression_ratio()
        )
    }
}
