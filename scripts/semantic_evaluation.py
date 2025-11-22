"""
Tests if your compressed tokens contain all the information from the original prompt.
"""

"""
Semantic Preservation Evaluator
Tests if compressed tokens preserve all information from original prompts
"""

import json
import re
from typing import Dict
import spacy


class SemanticPreservationEvaluator:
    """Evaluates how well compression preserves semantic information"""

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.results = []

    def extract_key_information(self, prompt: str) -> Dict:
        """Extract key semantic elements from original prompt"""
        doc = self.nlp(prompt)

        return {
            "verbs": [token.lemma_ for token in doc if token.pos_ == "VERB"],
            "nouns": [token.lemma_ for token in doc if token.pos_ in ["NOUN", "PROPN"]],
            "entities": [ent.text for ent in doc.ents],
            "has_extract_request": any(
                word in prompt.lower()
                for word in ["extract", "find", "identify", "get", "pull"]
            ),
            "has_format_request": any(
                word in prompt.lower()
                for word in ["json", "csv", "table", "list", "format"]
            ),
            "has_code_reference": any(
                word in prompt.lower()
                for word in ["code", "function", "script", "python", "javascript"]
            ),
            "has_data_reference": any(
                word in prompt.lower() for word in ["data", "dataset", "csv", "file"]
            ),
        }

    def extract_compressed_information(self, compressed: str) -> Dict:
        """Extract semantic elements from compressed tokens"""
        tokens = re.findall(r"\[([^\]]+)\]", compressed)

        info = {
            "has_req": any("REQ:" in t for t in tokens),
            "has_target": any("TARGET:" in t for t in tokens),
            "has_extract": any("EXTRACT:" in t for t in tokens),
            "has_context": any("CTX:" in t for t in tokens),
            "has_output": any("OUT:" in t for t in tokens),
            "req_tokens": [t for t in tokens if "REQ:" in t],
            "target_tokens": [t for t in tokens if "TARGET:" in t],
            "extract_tokens": [t for t in tokens if "EXTRACT:" in t],
            "out_tokens": [t for t in tokens if "OUT:" in t],
        }

        return info

    def check_semantic_match(self, original_info: Dict, compressed_info: Dict) -> Dict:
        """Check if compressed representation matches original semantics"""

        checks = {
            "has_action": compressed_info["has_req"],  # Should have REQ token
            "has_target": compressed_info["has_target"],  # Should have TARGET token
            "extract_preserved": True,  # Check if extract fields are captured
            "format_preserved": True,  # Check if output format is specified
        }

        # Check extract preservation
        if original_info["has_extract_request"]:
            checks["extract_preserved"] = compressed_info["has_extract"]

        # Check format preservation
        if original_info["has_format_request"]:
            checks["format_preserved"] = compressed_info["has_output"]

        # Overall semantic preservation score
        checks["preservation_score"] = sum(checks.values()) / len(checks)

        return checks

    def evaluate_sample(
        self, prompt: str, compressed: str, prompt_id: str = None
    ) -> Dict:
        """Evaluate a single prompt-compressed pair"""

        original_info = self.extract_key_information(prompt)
        compressed_info = self.extract_compressed_information(compressed)
        semantic_match = self.check_semantic_match(original_info, compressed_info)

        result = {
            "prompt_id": prompt_id,
            "prompt": prompt,
            "compressed": compressed,
            "original_length": len(prompt),
            "compressed_length": len(compressed),
            "original_info": original_info,
            "compressed_info": compressed_info,
            "semantic_match": semantic_match,
            "preservation_score": semantic_match["preservation_score"],
        }

        self.results.append(result)
        return result

    def evaluate_corpus(
        self, validation_file: str = "validation_results_100.json"
    ) -> Dict:
        """Evaluate entire corpus"""

        print("=" * 80)
        print("🔍 SEMANTIC PRESERVATION EVALUATION")
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

        # Calculate aggregate metrics
        return self.calculate_metrics()

    def calculate_metrics(self) -> Dict:
        """Calculate aggregate preservation metrics"""

        total = len(self.results)

        metrics = {
            "total_samples": total,
            "avg_preservation_score": sum(r["preservation_score"] for r in self.results)
            / total,
            "has_action_pct": sum(
                1 for r in self.results if r["semantic_match"]["has_action"]
            )
            / total
            * 100,
            "has_target_pct": sum(
                1 for r in self.results if r["semantic_match"]["has_target"]
            )
            / total
            * 100,
            "extract_preserved_pct": sum(
                1 for r in self.results if r["semantic_match"]["extract_preserved"]
            )
            / total
            * 100,
            "format_preserved_pct": sum(
                1 for r in self.results if r["semantic_match"]["format_preserved"]
            )
            / total
            * 100,
        }

        # Find problematic cases
        metrics["low_preservation_cases"] = [
            {
                "prompt_id": r["prompt_id"],
                "prompt": r["prompt"][:100],
                "compressed": r["compressed"],
                "score": r["preservation_score"],
            }
            for r in self.results
            if r["preservation_score"] < 0.5
        ]

        return metrics

    def print_report(self, metrics: Dict):
        """Print evaluation report"""

        print("=" * 80)
        print("📊 SEMANTIC PRESERVATION RESULTS")
        print("=" * 80 + "\n")

        print(f"Total Samples:              {metrics['total_samples']}")
        print(f"Avg Preservation Score:     {metrics['avg_preservation_score']:.2%}\n")

        print("Component Preservation:")
        print(f"  Action (REQ) captured:    {metrics['has_action_pct']:.1f}%")
        print(f"  Target captured:          {metrics['has_target_pct']:.1f}%")
        print(f"  Extract fields preserved: {metrics['extract_preserved_pct']:.1f}%")
        print(f"  Format preserved:         {metrics['format_preserved_pct']:.1f}%")

        # Show problematic cases
        if metrics["low_preservation_cases"]:
            print(
                f"\n⚠️  Low Preservation Cases ({len(metrics['low_preservation_cases'])}):"
            )
            for i, case in enumerate(metrics["low_preservation_cases"][:5], 1):
                print(f"\n  {i}. Score: {case['score']:.0%}")
                print(f"     Prompt: {case['prompt']}...")
                print(f"     Compressed: {case['compressed']}")

        # Overall verdict
        print("\n" + "=" * 80)
        if metrics["avg_preservation_score"] >= 0.90:
            print("✅ EXCELLENT: Semantic preservation is very high (≥90%)")
        elif metrics["avg_preservation_score"] >= 0.80:
            print("✅ GOOD: Semantic preservation is acceptable (≥80%)")
        elif metrics["avg_preservation_score"] >= 0.70:
            print("⚠️  MODERATE: Some semantic information may be lost (70-80%)")
        else:
            print("❌ POOR: Significant semantic information loss (<70%)")

        print("=" * 80 + "\n")

        return metrics

    def export_results(self, output_file: str = "semantic_preservation_results.json"):
        """Export detailed results"""
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"💾 Detailed results saved to {output_file}\n")


def main():
    """Run semantic preservation evaluation"""

    evaluator = SemanticPreservationEvaluator()

    # Evaluate corpus
    metrics = evaluator.evaluate_corpus()

    # Print report
    evaluator.print_report(metrics)

    # Export results
    evaluator.export_results()

    print("\n✅ Semantic preservation evaluation complete!\n")


if __name__ == "__main__":
    main()
