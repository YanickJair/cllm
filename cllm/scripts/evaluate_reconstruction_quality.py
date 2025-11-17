"""
Reconstruction Quality Evaluator
Tests if compressed tokens can be decompressed back to natural language
"""

import json
import re
from typing import Dict
from difflib import SequenceMatcher
import spacy


class SimpleDecoder:
    """Simple rule-based decoder to reconstruct natural language from CLLM tokens"""

    def __init__(self):
        # Token to natural language mappings
        self.req_to_text = {
            "ANALYZE": "Analyze",
            "EXTRACT": "Extract",
            "GENERATE": "Generate",
            "SUMMARIZE": "Summarize",
            "TRANSFORM": "Transform",
            "EXPLAIN": "Explain",
            "COMPARE": "Compare",
            "CLASSIFY": "Classify",
            "DEBUG": "Debug",
            "OPTIMIZE": "Optimize",
            "VALIDATE": "Validate",
            "SEARCH": "Search",
            "RANK": "Rank",
            "PREDICT": "Predict",
            "FORMAT": "Format",
            "DETECT": "Detect",
            "CALCULATE": "Calculate",
        }

        self.target_to_text = {
            "CODE": "this code",
            "TRANSCRIPT": "this transcript",
            "EMAIL": "this email",
            "DOCUMENT": "this document",
            "DATA": "this data",
            "TICKET": "this ticket",
            "QUERY": "this query",
            "REPORT": "this report",
            "CONVERSATION": "this conversation",
            "CONCEPT": "this concept",
            "PATTERN": "the pattern",
            "ANSWER": "an answer",
        }

    def decode(self, compressed: str) -> str:
        """Decode compressed tokens to natural language"""

        if not compressed or len(compressed) == 0:
            return ""

        # Extract tokens
        tokens = re.findall(r"\[([^\]]+)\]", compressed)

        # Parse token structure
        req_tokens = []
        target_tokens = []
        extract_tokens = []
        ctx_tokens = []
        out_tokens = []

        for token in tokens:
            if token.startswith("REQ:"):
                req = token.split(":")[1].split(":")[0]  # Get action without modifiers
                req_tokens.append(req)
            elif token.startswith("TARGET:"):
                target = token.split(":")[1].split(":")[0]
                target_tokens.append(target)
            elif token.startswith("EXTRACT:"):
                extract_tokens.append(token)
            elif token.startswith("CTX:"):
                ctx_tokens.append(token)
            elif token.startswith("OUT:"):
                out_tokens.append(token)

        # Reconstruct natural language
        parts = []

        # Add action
        if req_tokens:
            action = self.req_to_text.get(req_tokens[0], req_tokens[0].lower())
            parts.append(action)

        # Add target
        if target_tokens:
            target = self.target_to_text.get(target_tokens[0], target_tokens[0].lower())
            parts.append(target)

        # Add extract fields
        if extract_tokens:
            extract_text = extract_tokens[0].replace("EXTRACT:", "").replace("+", ", ")
            parts.append(f"and extract {extract_text.lower()}")

        # Add output format
        if out_tokens:
            format_text = out_tokens[0].replace("OUT:", "").split(":")[0]
            parts.append(f"in {format_text.lower()} format")

        # Construct sentence
        if len(parts) == 0:
            return compressed  # Can't decode, return as-is

        reconstructed = " ".join(parts) + "."

        # Capitalize first letter
        reconstructed = reconstructed[0].upper() + reconstructed[1:]

        return reconstructed


class ReconstructionEvaluator:
    """Evaluates reconstruction quality"""

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.decoder = SimpleDecoder()
        self.results = []

    def calculate_text_similarity(self, original: str, reconstructed: str) -> float:
        """Calculate character-level similarity"""
        return SequenceMatcher(None, original.lower(), reconstructed.lower()).ratio()

    def calculate_semantic_similarity(self, original: str, reconstructed: str) -> float:
        """Calculate semantic similarity using spaCy"""
        doc1 = self.nlp(original)
        doc2 = self.nlp(reconstructed)

        # Use spaCy's similarity (based on word vectors)
        return doc1.similarity(doc2)

    def extract_key_concepts(self, text: str) -> set:
        """Extract key concepts from text"""
        doc = self.nlp(text)

        concepts = set()

        # Extract verbs
        concepts.update(token.lemma_ for token in doc if token.pos_ == "VERB")

        # Extract nouns
        concepts.update(
            token.lemma_ for token in doc if token.pos_ in ["NOUN", "PROPN"]
        )

        # Extract entities
        concepts.update(ent.text.lower() for ent in doc.ents)

        return concepts

    def calculate_concept_coverage(self, original: str, reconstructed: str) -> float:
        """Calculate what % of original concepts are in reconstructed text"""
        original_concepts = self.extract_key_concepts(original)
        reconstructed_concepts = self.extract_key_concepts(reconstructed)

        if len(original_concepts) == 0:
            return 1.0

        # How many original concepts appear in reconstruction?
        overlap = original_concepts.intersection(reconstructed_concepts)
        return len(overlap) / len(original_concepts)

    def evaluate_sample(
        self, prompt: str, compressed: str, prompt_id: str = None
    ) -> Dict:
        """Evaluate reconstruction for a single sample"""

        # Decode
        reconstructed = self.decoder.decode(compressed)

        # Calculate metrics
        text_similarity = self.calculate_text_similarity(prompt, reconstructed)
        semantic_similarity = self.calculate_semantic_similarity(prompt, reconstructed)
        concept_coverage = self.calculate_concept_coverage(prompt, reconstructed)

        # Overall reconstruction score (weighted average)
        reconstruction_score = (
            text_similarity * 0.2  # 20% weight on exact text match
            + semantic_similarity * 0.4  # 40% weight on semantic similarity
            + concept_coverage * 0.4  # 40% weight on concept preservation
        )

        result = {
            "prompt_id": prompt_id,
            "original": prompt,
            "compressed": compressed,
            "reconstructed": reconstructed,
            "text_similarity": text_similarity,
            "semantic_similarity": semantic_similarity,
            "concept_coverage": concept_coverage,
            "reconstruction_score": reconstruction_score,
        }

        self.results.append(result)
        return result

    def evaluate_corpus(
        self, validation_file: str = "validation_results_100.json"
    ) -> Dict:
        """Evaluate reconstruction quality on entire corpus"""

        print("=" * 80)
        print("🔄 RECONSTRUCTION QUALITY EVALUATION")
        print("=" * 80 + "\n")

        # Load validation results
        with open(validation_file) as f:
            data = json.load(f)

        print(f"Evaluating {len(data)} prompts...\n")

        # Evaluate each sample
        for item in data:
            if item.get("compressed") and len(item["compressed"]) > 0:
                self.evaluate_sample(
                    prompt=item["prompt"],
                    compressed=item["compressed"],
                    prompt_id=item.get("id"),
                )

        return self.calculate_metrics()

    def calculate_metrics(self) -> Dict:
        """Calculate aggregate metrics"""

        total = len(self.results)

        metrics = {
            "total_samples": total,
            "avg_text_similarity": sum(r["text_similarity"] for r in self.results)
            / total,
            "avg_semantic_similarity": sum(
                r["semantic_similarity"] for r in self.results
            )
            / total,
            "avg_concept_coverage": sum(r["concept_coverage"] for r in self.results)
            / total,
            "avg_reconstruction_score": sum(
                r["reconstruction_score"] for r in self.results
            )
            / total,
        }

        # Find good and bad examples
        sorted_results = sorted(
            self.results, key=lambda x: x["reconstruction_score"], reverse=True
        )

        metrics["best_reconstructions"] = [
            {
                "original": r["original"][:80],
                "reconstructed": r["reconstructed"][:80],
                "score": r["reconstruction_score"],
            }
            for r in sorted_results[:5]
        ]

        metrics["worst_reconstructions"] = [
            {
                "original": r["original"][:80],
                "compressed": r["compressed"],
                "reconstructed": r["reconstructed"][:80],
                "score": r["reconstruction_score"],
            }
            for r in sorted_results[-5:]
        ]

        return metrics

    def print_report(self, metrics: Dict):
        """Print evaluation report"""

        print("=" * 80)
        print("📊 RECONSTRUCTION QUALITY RESULTS")
        print("=" * 80 + "\n")

        print(f"Total Samples:               {metrics['total_samples']}")
        print("\nReconstruction Metrics:")
        print(f"  Text Similarity:           {metrics['avg_text_similarity']:.2%}")
        print(f"  Semantic Similarity:       {metrics['avg_semantic_similarity']:.2%}")
        print(f"  Concept Coverage:          {metrics['avg_concept_coverage']:.2%}")
        print(f"  Overall Score:             {metrics['avg_reconstruction_score']:.2%}")

        # Show examples
        print("\n✅ Best Reconstructions:")
        for i, ex in enumerate(metrics["best_reconstructions"][:3], 1):
            print(f"\n  {i}. Score: {ex['score']:.0%}")
            print(f"     Original:      {ex['original']}...")
            print(f"     Reconstructed: {ex['reconstructed']}...")

        print("\n⚠️  Worst Reconstructions:")
        for i, ex in enumerate(metrics["worst_reconstructions"][:3], 1):
            print(f"\n  {i}. Score: {ex['score']:.0%}")
            print(f"     Original:      {ex['original']}...")
            print(f"     Compressed:    {ex['compressed']}")
            print(f"     Reconstructed: {ex['reconstructed']}...")

        # Overall verdict
        print("\n" + "=" * 80)
        score = metrics["avg_reconstruction_score"]
        if score >= 0.80:
            print("✅ EXCELLENT: High-quality reconstruction (≥80%)")
        elif score >= 0.70:
            print("✅ GOOD: Acceptable reconstruction quality (≥70%)")
        elif score >= 0.60:
            print("⚠️  MODERATE: Reconstruction could be improved (60-70%)")
        else:
            print("❌ POOR: Reconstruction quality needs work (<60%)")

        print("\nNote: This uses a simple rule-based decoder.")
        print("An LLM trained on CLLM tokens would reconstruct much better!")
        print("=" * 80 + "\n")

    def export_results(self, output_file: str = "reconstruction_results.json"):
        """Export detailed results"""
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"💾 Detailed results saved to {output_file}\n")


def main():
    """Run reconstruction quality evaluation"""

    evaluator = ReconstructionEvaluator()

    # Evaluate corpus
    metrics = evaluator.evaluate_corpus()

    # Print report
    evaluator.print_report(metrics)

    # Export results
    evaluator.export_results()

    print("\n✅ Reconstruction evaluation complete!\n")


if __name__ == "__main__":
    main()
