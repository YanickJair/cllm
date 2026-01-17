"""
Test script for system prompt compression corpus.

This script tests the CLMEncoder against a diverse corpus of system prompts
with different variations: tags/no-tags, placeholders, output formats, domains, etc.
"""
import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from clm_core import CLMEncoder, SysPromptConfig, CLMConfig


CORPUS_PATH = Path("./data/raw/system_prompts_corpus.json")
RESULTS_PATH = Path("./sys_prompt_corpus_results.json")


@dataclass
class TestResult:
    id: str
    category: str
    has_tags: bool
    has_placeholders: bool
    description: str
    success: bool
    cl: Optional[str] = None
    cl_nl: Optional[str] = None
    compression_ratio: Optional[float] = None
    metadata: Optional[dict] = None
    error: Optional[str] = None
    placeholders_detected: list[str] = field(default_factory=list)


def load_corpus() -> list[dict]:
    """Load the test corpus from JSON file."""
    with open(CORPUS_PATH, "r") as f:
        return json.load(f)


def run_single_test(encoder: CLMEncoder, item: dict, verbose: bool = False) -> TestResult:
    """Run compression test on a single corpus item."""
    result = TestResult(
        id=item.get("id", "unknown"),
        category=item.get("category", "unknown"),
        has_tags=item.get("has_tags", False),
        has_placeholders=item.get("has_placeholders", False),
        description=item.get("description", ""),
        success=False,
    )

    try:
        prompt = item.get("prompt", "")
        compressed = encoder.encode(prompt, verbose=verbose)

        if compressed:
            result.success = True
            result.cl = compressed.compressed
            runtime_values = item.get("runtime_values")
            result.cl_nl = compressed.bind(runtime_values) if runtime_values else compressed.bind()
            result.compression_ratio = compressed.compression_ratio
            result.metadata = compressed.metadata if hasattr(compressed, 'metadata') else {}
            result.placeholders_detected = compressed.placeholders if hasattr(compressed, 'placeholders') else []
        else:
            result.error = "Compression returned None"

    except Exception as e:
        result.error = str(e)

    return result


def run_corpus_tests(verbose: bool = False, filter_category: Optional[str] = None) -> list[TestResult]:
    """Run tests on the entire corpus or a filtered subset."""
    corpus = load_corpus()

    cfg = CLMConfig(
        lang="en",
        sys_prompt_config=SysPromptConfig(
            infer_types=True,
            add_attrs=True,
        )
    )
    encoder = CLMEncoder(cfg=cfg)
    results = []

    for item in corpus:
        if filter_category and item.get("category") != filter_category:
            continue

        result = run_single_test(encoder, item, verbose=verbose)
        results.append(result)

        status = "✓" if result.success else "✗"
        print(f"[{status}] {result.id}: {result.description}")
        if verbose and result.success and result.compression_ratio is not None:
            print(f"    Compression ratio: {result.compression_ratio:.2%}")
        if result.error:
            print(f"    Error: {result.error}")

    return results


def print_summary(results: list[TestResult]):
    """Print test summary statistics."""
    total = len(results)
    passed = sum(1 for r in results if r.success)
    failed = total - passed

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests: {total}")
    print(f"Passed: {passed} ({passed/total*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total*100:.1f}%)")

    if passed > 0:
        avg_ratio = sum(r.compression_ratio for r in results if r.success and r.compression_ratio) / passed
        print(f"Average compression ratio: {avg_ratio:.2%}")

    # Breakdown by category
    print("\nBy Category:")
    categories = set(r.category for r in results)
    for cat in sorted(categories):
        cat_results = [r for r in results if r.category == cat]
        cat_passed = sum(1 for r in cat_results if r.success)
        print(f"  {cat}: {cat_passed}/{len(cat_results)}")

    # Breakdown by tags
    print("\nBy Tags:")
    with_tags = [r for r in results if r.has_tags]
    without_tags = [r for r in results if not r.has_tags]
    print(f"  With tags: {sum(1 for r in with_tags if r.success)}/{len(with_tags)}")
    print(f"  Without tags: {sum(1 for r in without_tags if r.success)}/{len(without_tags)}")

    # Breakdown by placeholders
    print("\nBy Placeholders:")
    with_ph = [r for r in results if r.has_placeholders]
    without_ph = [r for r in results if not r.has_placeholders]
    print(f"  With placeholders: {sum(1 for r in with_ph if r.success)}/{len(with_ph)}")
    print(f"  Without placeholders: {sum(1 for r in without_ph if r.success)}/{len(without_ph)}")

    # Failed tests details
    if failed > 0:
        print("\nFailed Tests:")
        for r in results:
            if not r.success:
                print(f"  - {r.id}: {r.error}")


def save_results(results: list[TestResult]):
    """Save test results to JSON file."""
    output = []
    for r in results:
        output.append({
            "id": r.id,
            "category": r.category,
            "has_tags": r.has_tags,
            "cl_nl": r.cl_nl,
            "has_placeholders": r.has_placeholders,
            "description": r.description,
            "success": r.success,
            "compressed": r.cl,
            "compression_ratio": r.compression_ratio,
            "metadata": r.metadata,
            "error": r.error,
            "placeholders_detected": r.placeholders_detected,
        })

    with open(RESULTS_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {RESULTS_PATH}")


def test_single_by_id(prompt_id: str, verbose: bool = True):
    """Test a single prompt by its ID."""
    corpus = load_corpus()
    item = next((i for i in corpus if i.get("id") == prompt_id), None)

    if not item:
        print(f"Prompt with id '{prompt_id}' not found in corpus")
        return

    cfg = CLMConfig(
        lang="en",
        sys_prompt_config=SysPromptConfig(
            infer_types=True,
            add_attrs=True,
        )
    )
    encoder = CLMEncoder(cfg=cfg)
    result = run_single_test(encoder, item, verbose=verbose)

    print(f"\nTest: {result.id}")
    print(f"Description: {result.description}")
    print(f"Category: {result.category}")
    print(f"Has tags: {result.has_tags}")
    print(f"Has placeholders: {result.has_placeholders}")
    print(f"Success: {result.success}")

    if result.success:
        print(f"\nCompression ratio: {result.compression_ratio:.2%}")
        print(f"\nCompressed output:\n{result.compressed}")
        if result.placeholders_detected:
            print(f"\nPlaceholders detected: {result.placeholders_detected}")
    else:
        print(f"\nError: {result.error}")


def main():
    """Main entry point for corpus testing."""
    import argparse

    parser = argparse.ArgumentParser(description="Test system prompt compression corpus")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--category", "-c", type=str, help="Filter by category (task, configuration, mixed)")
    parser.add_argument("--single", "-s", type=str, help="Test a single prompt by ID")
    parser.add_argument("--save", action="store_true", help="Save results to JSON file")

    args = parser.parse_args()

    if args.single:
        test_single_by_id(args.single, verbose=args.verbose)
    else:
        results = run_corpus_tests(verbose=True, filter_category=args.category)
        print_summary(results)

        save_results(results)


if __name__ == "__main__":
    main()
