use crate::types::*;
use pyo3::prelude::*;

#[pyclass(from_py_object, name = "FieldImportance")]
#[derive(Clone)]
pub struct PyFieldImportance {
    pub inner: FieldImportance,
}

impl From<FieldImportance> for PyFieldImportance {
    fn from(inner: FieldImportance) -> Self {
        Self { inner }
    }
}

impl From<PyFieldImportance> for FieldImportance {
    fn from(py: PyFieldImportance) -> Self {
        py.inner
    }
}

#[pymethods]
#[allow(non_snake_case)]
impl PyFieldImportance {
    #[classattr]
    fn LOW() -> Self {
        FieldImportance::LOW.into()
    }
    #[classattr]
    fn MEDIUM() -> Self {
        FieldImportance::MEDIUM.into()
    }
    #[classattr]
    fn HIGH() -> Self {
        FieldImportance::HIGH.into()
    }
    #[classattr]
    fn CRITICAL() -> Self {
        FieldImportance::CRITICAL.into()
    }

    #[getter]
    fn value(&self) -> u8 {
        self.inner.clone() as u8
    }

    fn __eq__(&self, other: &Self) -> bool {
        self.inner == other.inner
    }

    fn __lt__(&self, other: &Self) -> bool {
        self.inner < other.inner
    }

    fn __le__(&self, other: &Self) -> bool {
        self.inner <= other.inner
    }

    fn __gt__(&self, other: &Self) -> bool {
        self.inner > other.inner
    }

    fn __ge__(&self, other: &Self) -> bool {
        self.inner >= other.inner
    }

    fn __repr__(&self) -> String {
        let name = match self.inner {
            FieldImportance::LOW => "LOW",
            FieldImportance::MEDIUM => "MEDIUM",
            FieldImportance::HIGH => "HIGH",
            FieldImportance::CRITICAL => "CRITICAL",
        };
        format!("FieldImportance.{name}")
    }

    fn __index__(&self) -> isize {
        self.inner.clone() as isize
    }

    fn __hash__(&self) -> isize {
        self.inner.clone() as isize
    }
}
