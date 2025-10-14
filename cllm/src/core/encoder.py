# Main encoder class
import re
import spacy

from src.core.vocabulary import Vocabulary
from src.analyzers.attribute_parser import AttributeParser
from src.analyzers.intent_detector import IntentDetector
from src.analyzers.target_extractor import TargetExtractor
from src.core.tokenizer import CLLMTokenizer

from src.core._schemas import CompressionResult


class CLLMEncoder:
    """Main CLLM encoder - orchestrates compression pipeline"""
    
    def __init__(self, model: str = "en_core_web_sm"):
        """
        Initialize encoder
        
        Args:
            model: spaCy model to use (en_core_web_sm, en_core_web_md, en_core_web_lg)
        """
        print(f"Loading spaCy model: {model}...")
        self.nlp: spacy.Language = spacy.load(model)

        # Initialize components
        self.intent_detector = IntentDetector(self.nlp)
        self.target_extractor = TargetExtractor(self.nlp)
        self.attribute_parser = AttributeParser(self.nlp)
        self.tokenizer = CLLMTokenizer()

        print("✓ CLLM Encoder initialized successfully")

    def compress(self, prompt: str, verbose: bool = False) -> CompressionResult:
        """
        Compress a natural language prompt into CLLM format
        
        Args:
            prompt: Natural language prompt to compress
            verbose: Print detailed compression steps
            
        Returns:
            CompressionResult with compressed format and metadata
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"Compressing: {prompt}")
            print(f"{'='*60}")

        # Step 1: Detect intents
        intents = self.intent_detector.detect(text=prompt)
        if verbose:
            print(f"\n1. Intents detected: {[i.token for i in intents]}")
        
        # Step 2: Extract targets
        targets = self.target_extractor.extract(prompt)
        if verbose:
            print(f"2. Targets detected: {[t.token for t in targets]}")

        # Step 3: Parse extraction fields
        extractions = self.attribute_parser.parse_extraction_fields(prompt)
        if verbose and extractions:
            print(f"3. Extraction fields: {extractions.fields}")

        # Step 4: Parse contexts
        contexts = self.attribute_parser.parse_contexts(prompt)
        if verbose and contexts:
            print(f"4. Contexts: {[(c.aspect, c.value) for c in contexts]}")
        
        # Step 5: Parse output format
        output_format = self.attribute_parser.parse_output_format(prompt)
        if verbose and output_format:
            print(f"5. Output format: {output_format.format_type}")
        
        # Step 6: Build compressed sequence
        compressed = self.tokenizer.build_sequence(
            intents=intents,
            contexts=contexts,
            targets=targets,
            output_format=output_format,
            extractions=extractions,
        )

        # Calculate compression ratio
        compression_ratio = round((1 - len(compressed) / len(prompt)) * 100, 1)
        doc = self.nlp(prompt)
        verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]

        if verbose:
            print(f"\n{'='*60}")
            print(f"Compressed: {compressed}")
            print(f"Compression: {compression_ratio}%")
            print(f"{'='*60}\n")

        return CompressionResult(
            original=prompt,
            compressed=compressed,
            intents=intents,
            targets=targets,
            extractions=extractions,
            contexts=contexts,
            output_format=output_format,
            compression_ratio=compression_ratio,
            metadata={
                "original_length": len(prompt),
                "compressed_length": len(compressed),
                "num_intents": len(intents),
                "num_targets": len(targets),
                "input_tokens": len(prompt.split()),
                "output_tokens": len(compressed.split()),
                "verbs": verbs,
                "noun_chunks": [chunk.text for chunk in doc.noun_chunks],
                "language": "en",
                "has_numbers": bool(re.search(r'\d', prompt)),
                "has_urls": bool(re.search(r'https?://', prompt)),
                "has_code_indicators": any(
                    word in prompt.lower() 
                    for word in ['python', 'javascript', 'function', 'class']
                ),
                "unmatched_verbs": [v for v in verbs if not any(v in Vocabulary.REQ_TOKENS[i.token] for i in intents if i.token in Vocabulary.REQ_TOKENS)]
            }
        )
    
    def compress_batch(self, prompts: list[str], verbose: bool = False) -> list[CompressionResult]:
        """Compress multiple prompts"""
        results = []
        for i, prompt in enumerate(prompts, 1):
            if verbose:
                print(f"\n[{i}/{len(prompts)}]")
            result = self.compress(prompt, verbose=verbose)
            results.append(result)
        return results