import re
from typing import Annotated

from annotated_doc import Doc
from spacy.language import Language

from clm_core.utils.parser_rules import BaseRules
from clm_core.utils.vocabulary import BaseVocabulary
from .analyzers.attribute_parser import AttributeParser
from clm_core.components.intent_detector_v2 import IntentDetectorV2 as IntentDetector
from clm_core.components.target_extractor import TargetExtractor
from .base_encoder import BasePromptEncoder
from .tokenizer import CLLMTokenizer
from clm_core.types import CLMOutput, SysPromptConfig

COMPONENT = "TASK_PROMPT"


class TaskPromptEncoder(BasePromptEncoder):
    def __init__(
        self,
        *,
        nlp: Annotated[
            Language,
            Doc(
                "spaCy language model to use (e.g. en_core_web_sm, en_core_web_md, en_core_web_lg)."
            ),
        ],
        config: Annotated[
            SysPromptConfig, Doc("Configuration for the task prompt encoder.")
        ] = SysPromptConfig(),
        vocab: Annotated[
            BaseVocabulary, Doc("Vocabulary instance for the target language.")
        ],
        rules: Annotated[BaseRules, Doc("Language-specific parsing rules.")],
    ):
        """Initialize the task prompt encoder."""

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

    def compress(
        self,
        prompt: Annotated[str, Doc("Natural language prompt to compress.")],
        verbose: Annotated[
            bool, Doc("When True, print detailed compression steps.")
        ] = False,
    ) -> CLMOutput:
        """Compress a natural language prompt into CLLM format."""
        if verbose:
            print(f"\n{'=' * 60}")
            print(f"Compressing: {prompt}")
            print(f"{'=' * 60}")

        intent = self.intent_detector.detect(text=prompt)
        if verbose:
            print(f"\n1. Intents detected: {intent.token}")

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
            intent=intent,
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
                "num_intents": 1 if intent.token else 0,
                "num_targets": 1 if target else 0,
                "verbs": verbs,
                "intents": intent.model_dump(),
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
                    for word in ["clm_core", "javascript", "function", "class"]
                ),
            },
        )

    def compress_batch(
        self,
        prompts: Annotated[
            list[str], Doc("List of natural language prompts to compress.")
        ],
        verbose: Annotated[
            bool, Doc("When True, print detailed compression steps for each prompt.")
        ] = False,
    ) -> list[CLMOutput]:
        """Compress multiple prompts."""
        results = []
        for i, prompt in enumerate(prompts, 1):
            if verbose:
                print(f"\n[{i}/{len(prompts)}]")
            result = self.compress(prompt, verbose=verbose)
            results.append(result)
        return results
