use pyo3::prelude::*;
pub mod encoder;
pub mod types;

mod py {
    pub mod config;
    pub mod encoder;
    pub mod enums;
    pub mod output;
}

use py::{
    config::PySDCompressionConfig, encoder::PySDEncoderV2, enums::PyFieldImportance,
    output::PyCLMOutput,
};

#[pymodule]
fn sd_encoder(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyFieldImportance>()?;
    m.add_class::<PyCLMOutput>()?;
    m.add_class::<PySDCompressionConfig>()?;
    m.add_class::<PySDEncoderV2>()?;

    Ok(())
}
