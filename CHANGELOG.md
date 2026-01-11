# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- New `IntentDetectorV2` component (`clm_core/components/intent_detector_v2.py`) for enhanced intent detection capabilities
- CONSTRAINTS support in output schema formatting (`clm_core/components/sys_prompt/_schemas.py:240-241`)
  - Added CONSTRAINTS to ordered_keys in `OutputSchema.build_token()` method
  - CONSTRAINTS now properly included in output token generation alongside KEYS and ENUMS
- Test suite for `IntentDetectorV2` (`tests/components/test_intent_detector_v2.py`)

### Changed

- Updated `OutputSchema.build_token()` to handle CONSTRAINTS attribute in schema output format
- Modified `OutputField.required` field to be Optional[bool] for better flexibility
- Enhanced output format analyzer in `clm_core/components/sys_prompt/analyzers/output_format.py`
- Improved system prompt tokenizer with updated constraints handling
- Updated vocabulary definitions across multiple languages (EN, ES, FR, PT)
- Enhanced encoder and decoder with constraint-aware processing
- Updated documentation for system prompt encoder with constraint examples

### Fixed

- Fixed TARGET token formatting and enum output format generation
- Improved attribute ordering in output schema: SCHEMA → KEYS → ENUMS → CONSTRAINTS → others

### 0.1.0 - 2025-12-10

## Added

- Initial release of CLM (Compressed Language Model)
- Core compression engine with 60-95% token reduction
- Semantic token encoding system (REQ, TARGET, EXTRACT, CTX, OUT, REF)
- Multilingual support (English, Portuguese, Spanish, French)
- spaCy-based NLP pipeline for intent detection and target extraction
- Pattern matching and vocabulary system
- Comprehensive test suite with 5,194+ validation prompts
- 91.5% validation accuracy on large datasets
- Production-tested compression ratios of 75-82%

## Features

- `CLMEncoder` - Main compression engine
- `Vocabulary` - Hierarchical semantic tokens
- `IntentDetector` - Action detection (REQ tokens)
- `TargetExtractor` - Object identification (TARGET tokens)
- `AttributeParser` - Context and format extraction (CTX, OUT, EXTRACT)
- Batch processing support
- Detailed metadata and analytics
- Language-agnostic architecture

## Documentation

- Complete API reference
- Usage examples
- Installation guide
- Patent documentation (provisional)

### 0.0.1 - 2025-12-29

## Added

- Full README documentation
- v1 package