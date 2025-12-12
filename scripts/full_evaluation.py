"""
Master Evaluation Runner
Runs all CLLM evaluations and produces comprehensive report
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def print_header(title: str):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def run_full_evaluation():
    """Run all evaluations"""

    print("\n" + "=" * 80)
    print("🎯 CLLM COMPREHENSIVE EVALUATION SUITE")
    print("=" * 80)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nThis will answer 3 critical questions:")
    print("  1. ❓ Semantic Preservation - Does compression retain full meaning?")
    print("  2. ❓ Reconstruction Quality - Can we decompress accurately?")
    print("  3. ❓ Real-World Performance - Does it work in production?")
    print("\n" + "=" * 80)

    results = {"evaluation_date": datetime.now().isoformat(), "evaluations": {}}

    # ============================================================
    # EVALUATION 1: Semantic Preservation
    # ============================================================
    print_header("1️⃣  SEMANTIC PRESERVATION EVALUATION")

    try:
        from evaluate_semantic_preservation import SemanticPreservationEvaluator

        eval1 = SemanticPreservationEvaluator()
        metrics1 = eval1.evaluate_corpus()
        eval1.print_report(metrics1)
        eval1.export_results("semantic_preservation_results.json")

        results["evaluations"]["semantic_preservation"] = {
            "status": "completed",
            "avg_score": metrics1["avg_preservation_score"],
            "verdict": "PASS" if metrics1["avg_preservation_score"] >= 0.80 else "FAIL",
        }

    except Exception as e:
        print(f"❌ Error in semantic preservation evaluation: {e}")
        results["evaluations"]["semantic_preservation"] = {
            "status": "failed",
            "error": str(e),
        }

    # ============================================================
    # EVALUATION 2: Reconstruction Quality
    # ============================================================
    print_header("2️⃣  RECONSTRUCTION QUALITY EVALUATION")

    try:
        from evaluate_reconstruction_quality import ReconstructionEvaluator

        eval2 = ReconstructionEvaluator()
        metrics2 = eval2.evaluate_corpus()
        eval2.print_report(metrics2)
        eval2.export_results("reconstruction_results.json")

        results["evaluations"]["reconstruction"] = {
            "status": "completed",
            "avg_score": metrics2["avg_reconstruction_score"],
            "verdict": "PASS"
            if metrics2["avg_reconstruction_score"] >= 0.70
            else "FAIL",
        }

    except Exception as e:
        print(f"❌ Error in reconstruction evaluation: {e}")
        results["evaluations"]["reconstruction"] = {"status": "failed", "error": str(e)}

    # ============================================================
    # EVALUATION 3: Real-World Performance
    # ============================================================
    print_header("3️⃣  REAL-WORLD PERFORMANCE EVALUATION")

    try:
        from evaluate_real_world_performance import RealWorldEvaluator
        from core import CLMEncoder
        import spacy

        print("Initializing encode...")
        nlp = spacy.load("en_core_web_sm")
        encoder = CLMEncoder(nlp)

        eval3 = RealWorldEvaluator(encoder)
        metrics3 = eval3.evaluate_all()
        eval3.print_report(metrics3)
        eval3.export_results("real_world_results.json")

        results["evaluations"]["real_world"] = {
            "status": "completed",
            "success_rate": metrics3["success_rate"],
            "avg_compression": metrics3["avg_compression_ratio"],
            "verdict": "PASS" if metrics3["success_rate"] >= 0.85 else "FAIL",
        }

    except Exception as e:
        print(f"❌ Error in real-world evaluation: {e}")
        results["evaluations"]["real_world"] = {"status": "failed", "error": str(e)}

    # ============================================================
    # FINAL SUMMARY
    # ============================================================
    print_header("📋 FINAL EVALUATION SUMMARY")

    print("Question 1: Semantic Preservation")
    if results["evaluations"]["semantic_preservation"]["status"] == "completed":
        score = results["evaluations"]["semantic_preservation"]["avg_score"]
        verdict = results["evaluations"]["semantic_preservation"]["verdict"]
        print(
            f"  Answer: {'✅' if verdict == 'PASS' else '❌'} {score:.1%} of semantic information preserved"
        )
        print(f"  Verdict: {verdict}")
    else:
        print("  Answer: ❌ Evaluation failed")

    print("\nQuestion 2: Reconstruction Quality")
    if results["evaluations"]["reconstruction"]["status"] == "completed":
        score = results["evaluations"]["reconstruction"]["avg_score"]
        verdict = results["evaluations"]["reconstruction"]["verdict"]
        print(
            f"  Answer: {'✅' if verdict == 'PASS' else '❌'} {score:.1%} reconstruction quality"
        )
        print(f"  Verdict: {verdict}")
        print("  Note: This uses simple rule-based decoder. An LLM would do better!")
    else:
        print("  Answer: ❌ Evaluation failed")

    print("\nQuestion 3: Real-World Performance")
    if results["evaluations"]["real_world"]["status"] == "completed":
        success = results["evaluations"]["real_world"]["success_rate"]
        compression = results["evaluations"]["real_world"]["avg_compression"]
        verdict = results["evaluations"]["real_world"]["verdict"]
        print(
            f"  Answer: {'✅' if verdict == 'PASS' else '❌'} {success:.1%} success rate on production scenarios"
        )
        print(f"  Compression: {compression:.1f}% average")
        print(f"  Verdict: {verdict}")
    else:
        print("  Answer: ❌ Evaluation failed")

    # Overall verdict
    print("\n" + "=" * 80)

    completed = [
        v for v in results["evaluations"].values() if v["status"] == "completed"
    ]
    passed = [v for v in completed if v["verdict"] == "PASS"]

    if len(passed) == 3:
        print("🎉 OVERALL: PRODUCTION READY")
        print("   All evaluations passed. CLLM is ready for real-world use!")
    elif len(passed) == 2:
        print("✅ OVERALL: NEARLY READY")
        print("   Most evaluations passed. Minor improvements needed.")
    elif len(passed) == 1:
        print("⚠️  OVERALL: NEEDS IMPROVEMENT")
        print("   Significant work needed before production use.")
    else:
        print("❌ OVERALL: NOT PRODUCTION READY")
        print("   Major improvements required.")

    print("=" * 80 + "\n")

    # Save summary
    with open("evaluation_summary.json", "w") as f:
        json.dump(results, f, indent=2)

    print("💾 Evaluation summary saved to evaluation_summary.json")
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    return results


if __name__ == "__main__":
    results = run_full_evaluation()
