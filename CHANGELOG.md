# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2026-01-19

### Added

- Full dictionary implementations for Spanish (ES), French (FR), and Portuguese (PT) languages
  - `EPISTEMIC_KEYWORDS` with future, uncertainty, and real_world categories
  - `STOPWORDS` tuples for proper filtering
  - `CODE_INDICATORS` for code-related term detection
  - Expanded `patterns.py` with comprehensive regex patterns (~574+ lines each)
  - Enhanced `rules.py` with language-specific processing rules (~294+ lines each)
  - Extended `vocabulary.py` with full vocabulary definitions (~250+ lines each)

### Changed

- Refactored `ConfigurationPromptMinimizer` to use dependency injection
  - Now requires spaCy `Language` instance in constructor instead of lazy loading
  - Converted class methods to instance methods for cleaner API
  - Removed optional spaCy fallback - spaCy is now required
- Simplified minimizer initialization by removing `_get_nlp()` class method

### Fixed

- Removed regex-based fallback in minimizer (was unused code path)

## [0.3.0] - 2026-01-19

### Added

- New `IntentDetectorV2` component (`clm_core/components/intent_detector_v2.py`) for enhanced intent detection capabilities
- CONSTRAINTS support in output schema formatting (`clm_core/components/sys_prompt/_schemas.py:240-241`)
  - Added CONSTRAINTS to ordered_keys in `OutputSchema.build_token()` method
  - CONSTRAINTS now properly included in output token generation alongside KEYS and ENUMS
- Test suite for `IntentDetectorV2` (`tests/components/test_intent_detector_v2.py`)
- New Configuration Prompt encoding system (`clm_core/components/sys_prompt/`):
  - `ConfigurationPromptEncoder` (`_configuration_prompt_encoder.py`) for compressing configuration-style system prompts
    - Extracts ROLE, RULES (basic/custom), PRIORITY, and PLACEHOLDERS from prompts
    - Generates compressed tokens like `[PROMPT_MODE:CONFIGURATION][ROLE:ASSISTANT][RULES:BASIC,CUSTOM]`
  - `ConfigurationPromptMinimizer` (`_minimizer.py`) for intelligent NL prompt minimization
    - spaCy-based linguistic analysis for sentence-level filtering
    - CL-aware suppression removes redundant NL when CL tokens encode the same information
    - Meta-instruction detection and removal (priority explanations, rule-following instructions)
    - Falls back to regex-based minimization when spaCy unavailable
  - `PromptAssembler` (`prompt_assembler.py`) for binding runtime values into templates
  - `PromptTemplateValidator` and `BoundPromptValidator` (`_prompt_template_validator.py`) for validation
- New schema types in `_schemas.py`:
  - `PromptMode` enum (`TASK`, `CONFIGURATION`)
  - `PromptTemplate` model with `bind()` method for runtime value substitution
  - `ValidationLevel` enum and `ValidationIssue` model for structured validation feedback
- Output format integration with Configuration Prompt encoder
  - `use_structured_output_abstraction` config option in `SysPromptConfig`

### Changed

- Updated `OutputSchema.build_token()` to handle CONSTRAINTS attribute in schema output format
- Modified `OutputField.required` field to be Optional[bool] for better flexibility
- Enhanced output format analyzer in `clm_core/components/sys_prompt/analyzers/output_format.py`
- Improved system prompt tokenizer with updated constraints handling
- Updated vocabulary definitions across multiple languages (EN, ES, FR, PT)
- Enhanced encoder and decoder with constraint-aware processing
- Refactored sys_prompt module exports to include new Configuration Prompt components
- Intent token format simplified (removed outer brackets)

### Documentation

- Reorganized System Prompt Encoder documentation into dedicated section (`docs/sys_prompt/`)
  - `index.md` - Overview and architecture
  - `task_prompt.md` - Task Prompt encoding documentation
  - `configuration_prompt.md` - Configuration Prompt encoding documentation
- Added `SysPromptConfig` parameters reference table in Configuration docs
- Expanded tokenization documentation with new token examples and usage patterns
- Removed monolithic `sys_prompt_encoder.md` in favor of modular structure

### Fixed

- Fixed TARGET token formatting and enum output format generation
- Improved attribute ordering in output schema: SCHEMA → KEYS → ENUMS → CONSTRAINTS → others

## [0.1.0] - 2025-12-10

### Added

- Initial release of CLM (Compressed Language Model)
- Core compression engine with 60-95% token reduction
- Semantic token encoding system (REQ, TARGET, EXTRACT, CTX, OUT, REF)
- Multilingual support (English, Portuguese, Spanish, French)
- spaCy-based NLP pipeline for intent detection and target extraction
- Pattern matching and vocabulary system
- Comprehensive test suite with 5,194+ validation prompts
- 91.5% validation accuracy on large datasets
- Production-tested compression ratios of 75-82%

### Features

- `CLMEncoder` - Main compression engine
- `Vocabulary` - Hierarchical semantic tokens
- `IntentDetector` - Action detection (REQ tokens)
- `TargetExtractor` - Object identification (TARGET tokens)
- `AttributeParser` - Context and format extraction (CTX, OUT, EXTRACT)
- Batch processing support
- Detailed metadata and analytics
- Language-agnostic architecture

### Documentation

- Complete API reference
- Usage examples
- Installation guide
- Patent documentation (provisional)

## [0.0.1] - 2025-12-29

### Added

- Full README documentation
- Initial package structure