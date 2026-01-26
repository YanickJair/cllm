# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.8] - 2026-01-26

### Added

- New `SDEncoderV2` class with improved nested schema handling
  - Header-first, row-based format with explicit nested schema scoping: `key:{nested}`
  - Nested schemas defined in header, values contain only data
  - Example: `{id,actions:{name,desc}}[1,[A,X][B,Y]]` instead of repeating schema in values
  - Config-driven with `drop_non_required_fields` option
- `drop_non_required_fields` parameter in `SDCompressionConfig`

### Changed

- `SDEncoderV2` is now the default encoder for structured data compression
- Improved compression ratio for nested objects and arrays of objects
- GitHub Workflow updated (.github/workflows/publish.yml):                                                                       
  - Added new test job that runs before build-and-publish                                                                        
  - Installs dependencies including spaCy model                                                                                  
  - Runs pytest tests/ -v --tb=short                                                                                             
  - Build job now has needs: test - won't publish if tests fail

### Documentation

- Updated `sd_encoder.md` to document `SDEncoderV2` and new nested schema format
- Updated examples to use new header-first format

## [0.0.7] - 2026-01-25

### Documentation

- Updated `sd_encoder.md` with new examples from `scripts/compress_structured_data.py`:
  - Added Example 1: Nested Data with Arrays (nested objects and user arrays)
  - Added Example 2: Product Catalog (demonstrates `excluded_fields` and `default_fields_importance`)
  - Added Example 3: KB Articles (shows `field_importance` and `max_description_length`)
- Added `default_fields_importance` parameter documentation to Configuration Reference
- Added "Nested Structure Handling" section documenting inline formatting for nested objects and arrays
- Updated imports to use simplified `from clm_core import SDCompressionConfig`
- Updated `index.md` structured data example:
  - Removed non-existent `dataset_name` parameter
  - Changed `max_field_length` to `max_description_length`
  - Fixed output format to match actual encoder behavior (`{fields}[values]`)
  - Added notes about comma escaping (`;`) and array separator (`+`)

## [0.0.4] - 2026-01-25

### Added

- `bind()` method on `CLMEncoder` for runtime placeholder binding in configuration prompts
- `suppress_role()` static method in `ConfigurationPromptMinimizer` for flexible role block removal
- `should_emit_out_json()` and `determine_text_output()` methods in `SysPromptOutputFormat` for improved output format detection
- `PLAIN_TEXT_ONLY_PATTERNS` in `SysPromptOutputFormat` for detecting plain text output requirements
- New default fields in `SDCompressionConfig`:
  - `uuid` and `priority` added to `simple_fields`
  - `uuid` and `priority` added to `default_fields_order`
  - `uuid` added to `default_fields_importance` as CRITICAL
- Test suite for `TranscriptEncoder` (`tests/components/test_transcript_encoder.py`)

### Changed

- Moved `bind()` method from `CLMOutput` to `ConfigurationPromptEncoder` - encoder now handles binding internally
- `ConfigurationPromptMinimizer` constructor now requires `config: SysPromptConfig` parameter
- `ROLE_BLOCK_PATTERN` in minimizer now supports multiple patterns including `<general_prompt>` blocks
- `OutputSchema.fields` and `OutputSchema.attributes` are now `Optional` for flexibility
- `OutputSchema.build_token()` now handles `TEXT` format type and `None` attributes gracefully
- Role pattern in `ConfigurationPromptEncoder` now matches `</role>` closing tag
- `SysPromptOutputFormat.compress()` returns `OutputSchema` with proper type hint

### Fixed

- Output format detection now correctly identifies plain text output requirements
- JSON block extraction in `extract_output_block()` no longer resets `in_json_block` flag prematurely
- `ConfigurationPromptMinimizer` now checks if `sentencizer` already exists before adding to spaCy pipeline
- Added missing `REQ` enum values used in vocabulary: `EXPLAIN`, `COMPARE`, `REVIEW`, `ASSESS`, `MONITOR`, `PARSE`, `MATCH`, `SELECT`, `OPTIMIZE`, `CALCULATE`, `AGGREGATE`, `DETERMINE`, `ROUTE`, `CODE`, `DETECT`, `LIST`
- Added `DETECTION` signal to `Signal` enum and `VOCAB_SIGNAL_MAP`
- Fixed test imports in `test_transcript_encoder.py` (`EnglishVocabulary` → `ENVocabulary`, `EnglishRules` → `ENRules`)
- Updated `test_types.py` tests for token-based compression ratio calculation and removed obsolete `bind` method tests
- Role extraction pattern now supports `&`, `-`, and numeric characters in role names
- Role suppression now removes "You are a..." sentences from NL when role is extracted (not just XML tags)
- SCORING sections with numeric ranges are now always removed from NL when output_format is present
- `<output_format>` XML tags are now properly removed by `extract_output_block()`
- `CLMOutput` validator now correctly falls back to original when compression ratio is negative (compressed larger than original)
- `CLMOutput.validate_compressed` normalizes all whitespace (tabs, newlines, multiple spaces) to single spaces
- Fixed `_trim_basic_rules` to not include indented content in replacement string
- `ConfigurationPromptEncoder.bind()` now returns original when combined CL+NL is larger than original

## [0.0.3.3] - 2026-01-24

### Added

- `n_tokens` and `c_tokens` as computed properties on `CLMOutput` model
  - Token estimation (~4 chars per token) now handled centrally in `CLMOutput._estimate_tokens()`
  - Encoders no longer need to calculate tokens manually
- Comprehensive test suite for `DSEncoder` (`tests/components/test_ds_encoder.py`) with 55 tests:
  - `TestDSEncoderInit`: Initialization and configuration tests
  - `TestDSEncoderDelimiterProperty`: Delimiter getter/setter tests
  - `TestDSEncoderEstimateTokens`: Token estimation tests
  - `TestDSEncoderEncode`: Main encode method tests
  - `TestDSEncoderEncodeItem`: Item encoding tests
  - `TestDSEncoderGetOrderedFields`: Field ordering tests
  - `TestDSEncoderFormatItemToken`: Token formatting tests
  - `TestDSEncoderFormatHeaderKeys`: Header formatting tests
  - `TestDSEncoderFormatValue`: Value formatting tests
  - `TestDSEncoderShouldIncludeField`: Field inclusion logic tests
  - `TestDSEncoderDetectFieldImportance`: Field importance detection tests
  - `TestDSEncoderIntegration`: End-to-end integration tests

### Changed

- `CLMOutput.compression_ratio` now calculated from token counts (`n_tokens`/`c_tokens`) instead of raw length
- DS compression output format optimized for better compression:
  - Removed unnecessary uppercasing of values
  - Removed space-to-underscore replacement (keeps original text)
  - Single-line format for items (no newlines between records)
  - Simplified header format (removed `CATALOG_CATALOG:N` prefix)
- Long text fields now truncated using `max_description_length` config (default: 200 chars)

### Fixed

- DS compression header/value alignment issue - header keys now match value order
  - Extracted ordering logic into `_get_ordered_fields()` method
  - Both `_format_header_keys()` and `_format_item_token()` use same ordering
- `compression_ratio` returning incorrect values for structured data (was using `len()` on list/dict)
- Syntax errors in `_minimizer.py` (incomplete function stubs)

### Documentation

- Updated `sd_encoder.md` with new compression format and `CLMOutput` fields
- Removed domain-specific references (NBA, CX) from documentation - now uses generic terminology
- Updated `docs/index.md` with generic use case descriptions
- Updated `docs/sys_prompt/index.md` with generic terminology
- Renamed script functions in `compress_structured_data.py` to be more generic

## [0.0.3.2] - 2026-01-22

### Added

- Comprehensive test suite for core types (`tests/test_types.py`)
  - `TestFieldImportance`: Enum value and comparison tests
  - `TestCLMOutput`: Creation, compression ratio, and bind method tests
  - `TestSDCompressionConfig`: Default values and custom configuration tests
  - `TestSDCompressionConfigFieldImportanceValidator`: Float-to-enum conversion tests
  - `TestSDCompressionConfigFieldImportanceSerializer`: Serialization tests

### Changed

- Enhanced `SDCompressionConfig.default_fields_importance` field handling:
  - Added `field_validator` to convert float/int values (e.g., `1.0`, `0.8`) to `FieldImportance` enum members
  - Added `field_serializer` to serialize enum values back to floats in `model_dump()`
  - Changed `model_config` from `use_enum_values=True` to `use_enum_values=False` for proper enum handling
  - Marked field as `frozen=True` for immutability
- Updated example script (`scripts/compress_structured_data.py`) to demonstrate float-based importance values

### Fixed

- CI/CD workflow file formatting (trailing newline in `publish.yml`)

## [0.0.3.1] - 2026-01-19

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

## [0.0.3] - 2026-01-19

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

## [0.0.2] - 2025-12-10

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