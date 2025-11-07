"""
CLLM Encoder - Full Validation Suite
Tests encoder on 100 diverse prompts to validate production readiness

Usage:
    python validate_full.py
"""

import json
from typing import List, Dict
from collections import defaultdict
from src.core.encoder import CLLMEncoder


def load_all_prompts() -> List[Dict]:
    """Load all 100 test prompts with metadata"""
    prompts = []

    with open("data/raw/general_prompts.json", "r") as f:
        GENERAL_PROMPTS: dict = json.load(f)

    # Add general prompts
    for key, prompts_ in GENERAL_PROMPTS.items():
        for i, prompt in enumerate(prompts_):
            prompts.append(
                {
                    "id": f"general_{i + 1:03d}",
                    "prompt": prompt,
                    "category": "general",
                    "subcategory": key,
                }
            )

    # Add customer support prompts
    with open("data/raw/ctx_prompts.json", "r") as f:
        CUSTOMER_SUPPORT_PROMPTS: dict = json.load(f)

    for key, prompts_ in CUSTOMER_SUPPORT_PROMPTS.items():
        for i, prompt in enumerate(prompts_):
            prompts.append(
                {
                    "id": f"support_{i + 1:03d}",
                    "prompt": prompt,
                    "category": "customer_support",
                    "subcategory": key,
                }
            )

    return prompts


def load_alpaca_prompts() -> list[dict]:
    with open("data/raw/raw_set_of_instructions.json", "r") as f:
        alpaca_prompts: dict = json.load(f)

    p_size = int(len(alpaca_prompts) * 0.20)
    return alpaca_prompts[:p_size]


class ValidationRunner:
    """Runs comprehensive validation on 100+ prompts"""

    def __init__(self, encoder: CLLMEncoder):
        self.encoder = encoder
        self.results = []
        self.stats = defaultdict(int)

    def run_validation(self, prompts: List[Dict]) -> Dict:
        """
        Run validation on all prompts

        Returns comprehensive analysis
        """
        print("\n" + "=" * 80)
        print("CLLM ENCODER - FULL VALIDATION")
        print("=" * 80)
        print(f"\nValidating {len(prompts)} prompts...")
        print("This may take 1-2 minutes...\n")

        # Track progress
        total = len(prompts)
        failed_cases = []
        partial_cases = []
        category_stats = defaultdict(lambda: {"total": 0, "passed": 0, "failed": 0})

        # Process each prompt
        for i, prompt_data in enumerate(prompts, 1):
            if i % 10 == 0:
                print(f"Progress: {i}/{total} ({i / total * 100:.0f}%)")

            prompt = prompt_data["prompt"]
            category = prompt_data["category"]
            subcategory = prompt_data["subcategory"]

            # Compress
            result = self.encoder.compress(prompt, verbose=False)

            # Analyze
            has_req = len(result.intents) > 0
            has_target = len(result.targets) > 0
            is_complete = has_req and has_target

            # Categorize result
            if is_complete:
                status = "PASS"
                category_stats[category]["passed"] += 1
            elif has_req or has_target:
                status = "PARTIAL"
                partial_cases.append(
                    {
                        "id": prompt_data["id"],
                        "prompt": prompt,
                        "compressed": result.compressed,
                        "has_req": has_req,
                        "has_target": has_target,
                        "category": category,
                        "subcategory": subcategory,
                    }
                )
            else:
                status = "FAIL"
                failed_cases.append(
                    {
                        "id": prompt_data["id"],
                        "prompt": prompt,
                        "compressed": result.compressed,
                        "category": category,
                        "subcategory": subcategory,
                    }
                )
                category_stats[category]["failed"] += 1

            category_stats[category]["total"] += 1

            # Store result
            self.results.append(
                {
                    "id": prompt_data["id"],
                    "prompt": prompt,
                    "compressed": result.compressed,
                    "compression_ratio": result.compression_ratio,
                    "has_req": has_req,
                    "has_target": has_target,
                    "status": status,
                    "category": category,
                    "subcategory": subcategory,
                    "metadata": result.metadata,
                }
            )

        print("\n✓ Validation complete!\n")

        # Calculate statistics
        total_prompts = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        partial = sum(1 for r in self.results if r["status"] == "PARTIAL")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")

        avg_compression = (
            sum(r["compression_ratio"] for r in self.results) / total_prompts
        )

        # Print summary
        self._print_summary(total_prompts, passed, partial, failed, avg_compression)
        self._print_category_breakdown(category_stats)
        self._print_subcategory_breakdown()

        # Print failures
        if failed_cases:
            self._print_failures(failed_cases)

        if partial_cases:
            self._print_partial_cases(partial_cases)

        # Export results
        self._export_results()

        return {
            "total": total_prompts,
            "passed": passed,
            "partial": partial,
            "failed": failed,
            "pass_rate": (passed / total_prompts) * 100,
            "coverage_rate": ((passed + partial) / total_prompts) * 100,
            "avg_compression": avg_compression,
            "failed_cases": failed_cases,
            "partial_cases": partial_cases,
        }

    def _print_summary(self, total, passed, partial, failed, avg_compression):
        """Print summary statistics"""
        print("=" * 80)
        print("SUMMARY STATISTICS")
        print("=" * 80)
        print(f"Total Prompts:       {total}")
        print(f"Passed (Full):       {passed} ({passed / total * 100:.1f}%)")
        print(f"Partial Coverage:    {partial} ({partial / total * 100:.1f}%)")
        print(f"Failed:              {failed} ({failed / total * 100:.1f}%)")
        print(f"\nOverall Coverage:    {(passed + partial) / total * 100:.1f}%")
        print(f"Avg Compression:     {avg_compression:.1f}%")

        # Verdict
        print("\n" + "=" * 80)
        print("VERDICT")
        print("=" * 80)

        pass_rate = (passed / total) * 100
        if pass_rate >= 90:
            print("✓ EXCELLENT: Encoder is production-ready!")
            print("  → Deploy with confidence")
            print("  → Minor edge case handling recommended")
        elif pass_rate >= 80:
            print("✓ GOOD: Encoder is highly functional")
            print("  → Address failed cases before production")
            print("  → Consider as beta release")
        elif pass_rate >= 70:
            print("⚠ ACCEPTABLE: Encoder works but needs improvement")
            print("  → Iterate on failed patterns")
            print("  → Test again after fixes")
        else:
            print("✗ NEEDS WORK: Significant improvements required")
            print("  → Analyze failure patterns")
            print("  → Expand vocabulary or detection logic")

    def _print_category_breakdown(self, category_stats):
        """Print breakdown by category"""
        print("\n" + "-" * 80)
        print("COVERAGE BY CATEGORY")
        print("-" * 80)

        for category in sorted(category_stats.keys()):
            stats = category_stats[category]
            coverage = (
                (stats["passed"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            )
            print(
                f"{category:20s}: {stats['passed']:2d}/{stats['total']:2d} ({coverage:5.1f}%)"
            )

    def _print_subcategory_breakdown(self):
        """Print breakdown by subcategory"""
        print("\n" + "-" * 80)
        print("COVERAGE BY SUBCATEGORY")
        print("-" * 80)

        subcategory_stats = defaultdict(lambda: {"total": 0, "passed": 0})

        for result in self.results:
            subcat = result["subcategory"]
            subcategory_stats[subcat]["total"] += 1
            if result["status"] == "PASS":
                subcategory_stats[subcat]["passed"] += 1

        for subcat in sorted(subcategory_stats.keys()):
            stats = subcategory_stats[subcat]
            coverage = (
                (stats["passed"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            )
            print(
                f"{subcat:25s}: {stats['passed']:2d}/{stats['total']:2d} ({coverage:5.1f}%)"
            )

    def _print_failures(self, failed_cases):
        """Print detailed failure analysis"""
        print("\n" + "=" * 80)
        print(f"FAILED CASES ({len(failed_cases)} total)")
        print("=" * 80)

        for i, case in enumerate(failed_cases, 1):
            print(f"\n[Failure {i}] {case['id']} - {case['subcategory']}")
            print(f"Prompt:     {case['prompt'][:70]}...")
            print(f"Compressed: {case['compressed']}")
            print("Issue:      Missing both REQ and TARGET tokens")

    def _print_partial_cases(self, partial_cases):
        """Print partial coverage cases"""
        print("\n" + "=" * 80)
        print(f"PARTIAL COVERAGE ({len(partial_cases)} total)")
        print("=" * 80)

        for i, case in enumerate(partial_cases[:10], 1):  # Show first 10
            print(f"\n[Partial {i}] {case['id']} - {case['subcategory']}")
            print(f"Prompt:     {case['prompt'][:70]}...")
            print(f"Compressed: {case['compressed']}")
            issue = "Missing TARGET" if case["has_req"] else "Missing REQ"
            print(f"Issue:      {issue}")

        if len(partial_cases) > 10:
            print(f"\n... and {len(partial_cases) - 10} more partial cases")

    def _export_results(self):
        """Export results to JSON"""
        filename = "validation_results_5K.json"
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✓ Full results exported to {filename}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def main():
    """Run full validation"""
    print("\n" + "=" * 80)
    print("CLLM ENCODER - 100 PROMPT VALIDATION")
    print("=" * 80)
    print("\nThis will test the encoder on 100 diverse prompts:")
    print("  • 50 General-purpose prompts")
    print("  • 50 Customer Support prompts")
    print("  • Comprehensive coverage analysis")
    print("  • Detailed failure reporting")
    print("\n" + "=" * 80)

    # Initialize encoder
    print("\nInitializing encoder...")
    encoder = CLLMEncoder()

    # Load prompts
    print("Loading 100 test prompts...")
    prompts = load_alpaca_prompts()
    print(f"✓ Loaded {len(prompts)} prompts")

    # Run validation
    validator = ValidationRunner(encoder)
    results = validator.run_validation(prompts)

    # Final recommendations
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)

    if results["pass_rate"] >= 90:
        print("1. Review validation_results_100.json for any edge cases")
        print("2. Build production pipeline (CLI, API, packaging)")
        print("3. Generate training data for CLLM model")
        print("4. Consider publishing results (arXiv paper)")
    elif results["pass_rate"] >= 80:
        print("1. Analyze failed cases in validation_results_100.json")
        print("2. Add missing patterns to vocabulary")
        print("3. Re-run validation to verify improvements")
        print("4. Aim for 90%+ before production deployment")
    else:
        print("1. Deep dive into failure patterns")
        print("2. Consider expanding vocabulary coverage")
        print("3. May need additional detection strategies")
        print("4. Re-test after significant changes")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
