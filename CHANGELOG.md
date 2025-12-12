# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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