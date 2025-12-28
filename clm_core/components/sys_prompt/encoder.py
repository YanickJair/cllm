import re

from spacy.language import Language

from clm_core.utils.parser_rules import BaseRules
from clm_core.utils.vocabulary import BaseVocabulary

from ._schemas import CompressionResult, SysPromptConfig
from .analyzers.attribute_parser import AttributeParser
from clm_core.components.intent_detector import IntentDetector
from clm_core.components.target_extractor import TargetExtractor
from .tokenizer import CLLMTokenizer
from clm_core.types import CLMOutput

COMPONENT = "SYSTEM_PROMPT"

class SysPromptEncoder:
    def __init__(
        self,
        *,
        nlp: Language,
        config: SysPromptConfig = SysPromptConfig(),
        vocab: BaseVocabulary,
        rules: BaseRules,
    ) -> None:
        """
        Initialize encode

        Args:
            nlp: spaCy model to use (en_core_web_sm, en_core_web_md, en_core_web_lg)
        """

        self.nlp: Language = nlp
        self._config = config
        self._vocab = vocab
        self._rules = rules

        self.intent_detector = IntentDetector(self.nlp, vocab=self._vocab)
        self.target_extractor = TargetExtractor(
            self.nlp, vocab=self._vocab, rules=self._rules
        )
        self.attribute_parser = AttributeParser(
            nlp=self.nlp, config=config, vocab=self._vocab, rules=rules
        )
        self.tokenizer = CLLMTokenizer()

    def compress(self, prompt: str, verbose: bool = False) -> CLMOutput:
        """
        Compress a natural language prompt into CLLM format

        Args:
            prompt: Natural language prompt to compress
            verbose: Print detailed compression steps

        Returns:
            CompressionResult with compressed format and metadata
        """
        if verbose:
            print(f"\n{'=' * 60}")
            print(f"Compressing: {prompt}")
            print(f"{'=' * 60}")

        intents = self.intent_detector.detect(text=prompt)
        if verbose:
            print(f"\n1. Intents detected: {[i.token for i in intents]}")

        target = self.target_extractor.extract(prompt)
        if verbose:
            print(f"2. Targets detected: {target.token}")

        extractions = self.attribute_parser.parse_extraction_fields(prompt)
        quantifiers = self.attribute_parser.extract_quantifier(prompt)
        specifications = self.attribute_parser.extract_specifications(prompt)
        if verbose and extractions:
            print(f"3. Extraction fields: {extractions.fields}")
            print(f"3.1 Quantifiers field: {quantifiers}")

        contexts = self.attribute_parser.parse_contexts(prompt)
        if verbose and contexts:
            print(f"4. Contexts: {[(c.aspect, c.value) for c in contexts]}")

        output_format = self.attribute_parser.parse_output_format(prompt)
        if verbose and output_format:
            print(f"5. Output format: {output_format.format_type}")

        compressed = self.tokenizer.build_sequence(
            intents=intents,
            contexts=contexts,
            target=target,
            output_format=output_format,
            extractions=extractions,
            quantifier=quantifiers,
            specifications=specifications,
        )

        doc = self.nlp(prompt)
        verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]

        if verbose:
            print(f"\n{'=' * 60}")
            print(f"Compressed: {compressed}")
            print(f"{'=' * 60}\n")

        return CLMOutput(
            original=prompt,
            compressed=compressed,
            component=COMPONENT,
            metadata={
                "original_length": len(prompt),
                "compressed_length": len(compressed),
                "num_intents": len(intents),
                "num_targets": 1 if target else 0,
                "input_tokens": len(prompt.split()),
                "output_tokens": len(compressed.split()),
                "verbs": verbs,
                "intents": intents,
                "target": target,
                "extractions": extractions,
                "contexts": contexts,
                "output_format": output_format,
                "noun_chunks": [chunk.text for chunk in doc.noun_chunks],
                "language": "en",
                "has_numbers": bool(re.search(r"\d", prompt)),
                "has_urls": bool(re.search(r"https?://", prompt)),
                "has_code_indicators": any(
                    word in prompt.lower()
                    for word in ["python", "javascript", "function", "class"]
                ),
                "unmatched_verbs": [
                    v
                    for v in verbs
                    if not any(
                        v in self._vocab.REQ_TOKENS[i.token]
                        for i in intents
                        if i.token in self._vocab.REQ_TOKENS
                    )
                ],
            },
        )

    def compress_batch(
        self, prompts: list[str], verbose: bool = False
    ) -> list[CompressionResult]:
        """Compress multiple prompts"""
        results = []
        for i, prompt in enumerate(prompts, 1):
            if verbose:
                print(f"\n[{i}/{len(prompts)}]")
            result = self.compress(prompt, verbose=verbose)
            results.append(result)
        return results
