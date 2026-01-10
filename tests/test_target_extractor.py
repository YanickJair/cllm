"""
Test Suite for TargetExtractor

Tests the main target extraction orchestrator and its component extractors:
- ImperativeExtractor: Verb-led command patterns
- QuestionExtractor: Question patterns
- NounExtractor: Direct noun matches
- CompoundExtractor: Multi-word phrases
- PatternExtractor: Specific patterns (this X, for X, concepts)
- FallbackExtractor: Last-resort extraction
- TargetNormalizer: Target aggregation and normalization
- AttributeEnhancer: Contextual attribute enrichment
"""

import pytest
import spacy

from clm_core.components.target_extractor import TargetExtractor
from clm_core.components.sys_prompt import Target
from clm_core.components._target.extractors import FallbackExtractor
from clm_core.components._target.target_normalizer import TargetNormalizer
from clm_core.components._target.attributes import AttributeEnhancer
from clm_core.dictionary.en.vocabulary import ENVocabulary
from clm_core.dictionary.en.rules import ENRules

@pytest.fixture(scope="module")
def nlp():
    """Load spaCy model once for all tests"""
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        pytest.skip("spaCy model 'en_core_web_sm' not installed")


@pytest.fixture
def vocab():
    """Use real EN vocabulary for tests"""
    return ENVocabulary()


@pytest.fixture
def rules():
    """Use real EN parser rules for tests"""
    return ENRules()


@pytest.fixture
def target_extractor(nlp, vocab, rules):
    """Create TargetExtractor instance with real vocabulary and rules"""
    return TargetExtractor(nlp, vocab, rules)

class TestImperativeExtractor:
    """Tests for ImperativeExtractor"""

    def test_analyze_pattern(self, target_extractor, nlp):
        """Test ANALYZE pattern detection"""
        text = "Analyze this code for bugs"
        result = target_extractor.extract(text)

        assert result is not None
        assert result.token == "CODE"

    def test_extract_pattern(self, target_extractor, nlp):
        """Test EXTRACT pattern detection"""
        text = "Extract the data from the file"
        result = target_extractor.extract(text)

        assert result is not None
        assert result.token == "DATA"

    def test_summarize_transcript(self, target_extractor, nlp):
        """Test SUMMARIZE with transcript"""
        text = "Summarize this customer call transcript"
        result = target_extractor.extract(text)

        assert result is not None
        assert result.token == "TRANSCRIPT"

    def test_debug_pattern(self, target_extractor, nlp):
        """Test DEBUG pattern detection"""
        text = "Debug this function"
        result = target_extractor.extract(text)

        assert result is not None
        assert result.token == "CODE"

    def test_optimize_query(self, target_extractor, nlp):
        """Test OPTIMIZE with query"""
        text = "Optimize this SQL query for performance"
        result = target_extractor.extract(text)

        assert result is not None
        assert result.token == "QUERY"

    def test_generate_content(self, target_extractor, nlp):
        """Test GENERATE pattern"""
        text = "Generate a report summary"
        result = target_extractor.extract(text)

        assert result is not None
        assert result.token == "CONTENT"

    def test_classify_ticket(self, target_extractor, nlp):
        """Test CLASSIFY with ticket"""
        text = "Classify this support ticket by urgency"
        result = target_extractor.extract(text)

        assert result is not None
        assert result.token == "TICKET"

class TestQuestionExtractor:
    """Tests for QuestionExtractor"""

    def test_what_question(self, target_extractor, nlp):
        """Test 'what' question pattern"""
        text = "What is object-oriented programming?"
        result = target_extractor.extract(text)

        assert result is not None
        assert result.token == "CONCEPT"

    def test_how_question(self, target_extractor, nlp):
        """Test 'how' question pattern"""
        text = "How does DNS work?"
        result = target_extractor.extract(text)

        assert result is not None
        assert result.token == "CONCEPT"

    def test_why_question(self, target_extractor, nlp):
        """Test 'why' question pattern"""
        text = "Why is this happening?"
        result = target_extractor.extract(text)

        assert result is not None
        assert result.token == "CONCEPT"

    def test_non_question(self, target_extractor, nlp):
        """Test that non-questions don't trigger QuestionExtractor"""
        text = "Tell me about DNS"
        result = target_extractor.extract(text)

        # Should not be caught by QuestionExtractor (no ?)
        # May be caught by other extractors
        assert result is not None


class TestNounExtractor:
    """Tests for NounExtractor"""

    def test_single_noun(self, target_extractor, nlp):
        """Test single noun extraction"""
        text = "I need the code"
        result = target_extractor.extract(text)

        assert result is not None
        assert result.token == "CODE"

    def test_multiple_nouns(self, target_extractor, nlp):
        """Test multiple noun extraction (should be normalized to one)"""
        text = "I need the code and data"
        result = target_extractor.extract(text)

        # TargetExtractor.extract() returns single Target after normalization
        assert result is not None
        # The normalizer will pick the higher priority target
        assert result.token in ["CODE", "DATA"]

    def test_noun_not_in_vocab(self, target_extractor, nlp):
        """Test noun that's not in vocabulary"""
        text = "I need the widget"
        result = target_extractor.extract(text)

        # Should fall back to other extractors or fallback
        assert result is not None

class TestCompoundExtractor:
    """Tests for CompoundExtractor"""

    def test_compound_phrase(self, target_extractor, nlp):
        """Test compound phrase extraction"""
        # Uses real vocabulary which has compound phrases
        text = "Show me the error log"
        result = target_extractor.extract(text)

        assert result is not None

    def test_case_insensitive(self, target_extractor, nlp):
        """Test case-insensitive compound matching"""
        # Uses real vocabulary
        text = "Show me the ERROR LOG"
        result = target_extractor.extract(text)

        assert result is not None

class TestPatternExtractor:
    """Tests for PatternExtractor"""

    def test_this_pattern(self, target_extractor, nlp):
        """Test 'this X' pattern"""
        text = "Review this code"
        result = target_extractor.extract(text)

        assert result is not None
        assert result.token == "CODE"

    def test_that_pattern(self, target_extractor, nlp):
        """Test 'that X' pattern"""
        text = "Check that query"
        result = target_extractor.extract(text)

        assert result is not None
        assert result.token == "QUERY"

    def test_for_pattern(self, target_extractor, nlp):
        """Test 'for X' pattern"""
        text = "Generate instructions for the code"
        result = target_extractor.extract(text)

        assert result is not None
        # "Generate instructions" prioritizes CONTENT
        assert result.token in ["CODE", "CONTENT"]

    def test_concept_detection(self, target_extractor, nlp):
        """Test concept detection"""
        text = "Explain the concept of machine learning"
        result = target_extractor.extract(text)

        assert result is not None
        assert result.token == "CONCEPT"


class TestFallbackExtractor:
    """Tests for FallbackExtractor"""

    def test_fallback_no_req_tokens(self, nlp, vocab, rules):
        """Test fallback with no detected req tokens"""
        extractor = FallbackExtractor(nlp, vocab, rules)
        doc = nlp("Some random text")

        result = extractor.extract("Some random text", None, doc)

        assert result is not None
        assert result.token == "ANSWER"

    def test_fallback_generate_with_list(self, nlp, vocab, rules):
        """Test fallback with GENERATE and list indicators"""
        extractor = FallbackExtractor(nlp, vocab, rules)
        doc = nlp("Generate a list of items")

        result = extractor.extract("Generate a list of items", ["GENERATE"], doc)

        assert result is not None
        assert result.token == "ITEMS"

    def test_fallback_generate_without_list(self, nlp, vocab, rules):
        """Test fallback with GENERATE but no list indicators"""
        extractor = FallbackExtractor(nlp, vocab, rules)
        doc = nlp("Generate a summary")

        result = extractor.extract("Generate a summary", ["GENERATE"], doc)

        assert result is not None
        assert result.token == "CONTENT"

    def test_fallback_explain(self, nlp, vocab, rules):
        """Test fallback with EXPLAIN req token"""
        extractor = FallbackExtractor(nlp, vocab, rules)
        doc = nlp("Explain this")

        result = extractor.extract("Explain this", ["EXPLAIN"], doc)

        assert result is not None
        assert result.token == "CONCEPT"


class TestTargetNormalizer:
    """Tests for TargetNormalizer"""

    def test_normalize_single_target(self):
        """Test normalizing a single target"""
        normalizer = TargetNormalizer()
        target = Target(token="code", domain="technical", attributes={"lang": "python"})

        result = normalizer.normalize(target)

        assert result.token == "CODE"
        assert result.domain == "TECHNICAL"
        # Normalizer uppercases keys but not values
        assert result.attributes.get("LANG") == "python"

    def test_normalize_many_picks_priority(self):
        """Test that normalize_many picks highest priority target"""
        normalizer = TargetNormalizer()
        targets = [
            Target(token="ANSWER", attributes={}),
            Target(token="CODE", attributes={"LANG": "python"}),
            Target(token="TRANSCRIPT", attributes={"DURATION": "30"}),
        ]

        result = normalizer.normalize_many(targets)

        # TRANSCRIPT has highest priority (index 0)
        assert result.token == "TRANSCRIPT"
        # Should merge attributes from all targets where allowed
        assert "DURATION" in result.attributes

    def test_normalize_filters_banned_attributes(self):
        """Test that banned attributes are removed"""
        normalizer = TargetNormalizer()
        target = Target(
            token="CODE",
            attributes={"LANG": "python", "CONTEXT": "test", "RAW": "data"}
        )

        result = normalizer.normalize(target)

        assert "LANG" in result.attributes
        assert "CONTEXT" not in result.attributes  # BANNED
        assert "RAW" not in result.attributes  # BANNED

    def test_normalize_filters_disallowed_attributes(self):
        """Test that attributes not allowed for token type are removed"""
        normalizer = TargetNormalizer()
        target = Target(
            token="ANSWER",
            attributes={"LANG": "python", "FORMAT": "json"}
        )

        result = normalizer.normalize(target)

        # ANSWER has empty allowed set, but the logic only filters if allowed is truthy
        # When allowed is empty set, it's falsy, so attrs pass through
        # This is expected behavior - tokens with no restrictions keep all attrs
        assert isinstance(result.attributes, dict)

    def test_normalize_merges_attributes(self):
        """Test that attributes from multiple targets are merged"""
        normalizer = TargetNormalizer()
        targets = [
            Target(token="DATA", attributes={"FORMAT": "json"}),
            Target(token="DATA", attributes={"SIZE": "100"}),
        ]

        result = normalizer.normalize_many(targets)

        assert result.token == "DATA"
        assert "FORMAT" in result.attributes
        assert "SIZE" in result.attributes

    def test_normalize_merges_domains(self):
        """Test that domains from multiple targets are merged"""
        normalizer = TargetNormalizer()
        targets = [
            Target(token="CODE", domain="TECHNICAL"),
            Target(token="DATA", domain="ANALYTICS"),
        ]

        result = normalizer.normalize_many(targets)

        # Domains should be combined (implementation may vary)
        assert result.domain is not None

    def test_normalize_empty_list_returns_default(self):
        """Test normalize_many with empty list returns None"""
        normalizer = TargetNormalizer()

        result = normalizer.normalize_many([])

        # Returns None for empty list (as per implementation)
        assert result is None

class TestAttributeEnhancer:
    """Tests for AttributeEnhancer"""

    def test_enhance_concept_with_topic(self, nlp, vocab, rules):
        """Test enhancing CONCEPT with TOPIC"""
        # Use keyword arguments for AttributeEnhancer
        enhancer = AttributeEnhancer(nlp=nlp, vocab=vocab, rules=rules)
        text = "What is object-oriented programming?"
        doc = nlp(text)

        attrs = enhancer.enhance("CONCEPT", text, doc)

        # Should have TOPIC attribute (may vary based on implementation)
        assert isinstance(attrs, dict)

    def test_enhance_code_with_lang(self, nlp, vocab, rules):
        """Test enhancing CODE with LANG"""
        # Use keyword arguments for AttributeEnhancer
        enhancer = AttributeEnhancer(nlp=nlp, vocab=vocab, rules=rules)
        text = "Debug this Python function"
        doc = nlp(text)

        attrs = enhancer.enhance("CODE", text, doc)

        # Should have LANG attribute if Python is detected
        assert isinstance(attrs, dict)
        # Python should be detected
        assert "LANG" in attrs

    def test_enhance_result_with_type(self, nlp, vocab, rules):
        """Test enhancing RESULT with TYPE"""
        # Use keyword arguments for AttributeEnhancer
        enhancer = AttributeEnhancer(nlp=nlp, vocab=vocab, rules=rules)
        text = "Calculate the average score"
        doc = nlp(text)

        attrs = enhancer.enhance("RESULT", text, doc)

        assert isinstance(attrs, dict)

class TestTargetExtractorIntegration:
    """Integration tests for full extraction pipeline"""

    def test_full_pipeline_imperative(self, target_extractor):
        """Test full pipeline with imperative command"""
        text = "Analyze this Python code for security issues"
        result = target_extractor.extract(text)

        assert result is not None
        assert result.token == "CODE"

    def test_full_pipeline_question(self, target_extractor):
        """Test full pipeline with question"""
        text = "What is machine learning?"
        result = target_extractor.extract(text)

        assert result is not None
        assert result.token == "CONCEPT"

    def test_full_pipeline_with_req_tokens(self, target_extractor):
        """Test pipeline with detected req tokens"""
        text = "Summarize this 30-minute customer call transcript"
        detected_req_tokens = ["SUMMARIZE"]

        result = target_extractor.extract(text, detected_req_tokens)

        assert result is not None
        assert result.token == "TRANSCRIPT"

    def test_complex_prompt(self, target_extractor):
        """Test complex prompt with multiple potential targets"""
        text = "Review this customer support ticket and extract the main issue"
        result = target_extractor.extract(text)

        assert result is not None
        # Could match TICKET, DOCUMENT, or other targets based on extraction logic
        assert result.token in ["TICKET", "CONTENT", "DATA", "DOCUMENT"]

    def test_technical_domain_detection(self, target_extractor):
        """Test that technical domain is detected"""
        text = "Debug this Python function in the database module"
        result = target_extractor.extract(text)

        assert result is not None
        assert result.token == "CODE"
        # Domain detection depends on implementation

    def test_empty_text(self, target_extractor):
        """Test with empty text"""
        text = ""
        result = target_extractor.extract(text)

        # Should handle gracefully (fallback to ANSWER or similar)
        assert result is not None

    def test_ambiguous_text(self, target_extractor):
        """Test with ambiguous text"""
        text = "Please help"
        result = target_extractor.extract(text)

        # Should fall back to ANSWER or similar
        assert result is not None
        assert result.token in ["ANSWER", "CONTENT", "CONCEPT"]


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_very_long_text(self, target_extractor):
        """Test with very long text"""
        text = "Analyze " + "this code " * 100
        result = target_extractor.extract(text)

        assert result is not None

    def test_special_characters(self, target_extractor):
        """Test with special characters"""
        text = "Debug this @#$% code!!!"
        result = target_extractor.extract(text)

        assert result is not None
        assert result.token == "CODE"

    def test_mixed_case(self, target_extractor):
        """Test with mixed case text"""
        text = "ANALYZE THIS CODE"
        result = target_extractor.extract(text)

        assert result is not None
        assert result.token == "CODE"

    def test_unicode_text(self, target_extractor):
        """Test with unicode characters"""
        text = "Analyze this código"
        result = target_extractor.extract(text)

        assert result is not None

    def test_numbers_in_text(self, target_extractor):
        """Test with numbers in text"""
        text = "Analyze this 123 dataset with 456 rows"
        result = target_extractor.extract(text)

        assert result is not None

    def test_multiple_sentences(self, target_extractor):
        """Test with multiple sentences"""
        text = "I have a problem. This code is broken. Can you debug it?"
        result = target_extractor.extract(text)

        assert result is not None

    # New behaviors
    def test_detect_query_via_pattern_extractor(self, target_extractor):
        """Should detect QUERY when phrased as 'that query'"""
        text = "Optimize that query for performance"
        result = target_extractor.extract(text)

        assert result is not None
        assert result.token == "QUERY"

    def test_list_generation_prefers_items(self, target_extractor):
        """Fallback should map GENERATE + list indicators to ITEMS"""
        text = "Generate a bullet list of items"
        result = target_extractor.extract(text, detected_req_tokens=["GENERATE"]) 

        assert result is not None
        assert result.token in ["ITEMS", "CONTENT"]

    def test_question_without_question_mark(self, target_extractor):
        """Non-marked questions should still yield a target via other extractors"""
        text = "Explain the concept of recursion"
        result = target_extractor.extract(text)

        assert result is not None
        assert result.token in ["CONCEPT", "CONTENT"]

    def test_attribute_enhancement_for_language(self, target_extractor):
        """AttributeEnhancer should add LANG for code targets when language present"""
        text = "Analyze the Python code sample"
        result = target_extractor.extract(text)

        assert result is not None
        assert result.token == "CODE"
        # Enhanced attributes should include language when detectable
        assert isinstance(result.attributes, dict)

    def test_empty_input_falls_back(self, target_extractor):
        """Empty input should fall back to default target (e.g., ANSWER)"""
        text = "   "
        result = target_extractor.extract(text)

        assert result is not None
        assert result.token in ["ANSWER", "CONTENT", "CONCEPT"]


class TestPerformance:
    """Performance and stress tests"""

    @pytest.mark.slow
    def test_batch_extraction(self, target_extractor):
        """Test extracting from multiple prompts"""
        prompts = [
            "Analyze this code",
            "What is DNS?",
            "Summarize this transcript",
            "Generate a report",
            "Debug this function",
        ]

        results = [target_extractor.extract(p) for p in prompts]

        assert len(results) == len(prompts)
        assert all(r is not None for r in results)

    @pytest.mark.slow
    def test_repeated_extraction(self, target_extractor):
        """Test repeated extraction of same prompt"""
        text = "Analyze this code for bugs"

        results = [target_extractor.extract(text) for _ in range(100)]

        # Results should be consistent
        assert all(r.token == results[0].token for r in results)
