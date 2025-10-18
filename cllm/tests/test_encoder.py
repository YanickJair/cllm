"""
CLLM Encoder - Test Suite
Validates encoder performance on diverse prompts

Usage:
    python test_encoder.py
"""

import sys
import os
from typing import List, Dict
from dataclasses import dataclass

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the encoder (assuming it's in encoder.py)
# from encoder import CLLMEncoder, CompressionResult

# For demonstration, we'll simulate the encoder structure
@dataclass
class EncoderTestResult:
    prompt: str
    compressed: str
    expected: str
    matches: bool
    issues: List[str]
    compression_ratio: float
    has_req: bool
    has_target: bool
    metadata: Dict


class EncoderTester:
    """Test harness for CLLM encoder"""
    
    def __init__(self):
        self.test_cases = self._load_test_cases()
        self.results = []
    
    def _load_test_cases(self) -> List[Dict]:
        """
        Load test cases with expected outputs
        Each test case has:
        - prompt: The input prompt
        - expected: What we expect the compressed format to be
        - category: Type of prompt (general, customer_support, etc.)
        """
        return [
            # ============================================================
            # CUSTOMER SUPPORT PROMPTS
            # ============================================================
            {
                "prompt": "Analyze this customer support transcript and extract the main issue, sentiment, and action items. Format as JSON.",
                "expected": "[REQ:ANALYZE] [TARGET:TRANSCRIPT:DOMAIN=SUPPORT] [EXTRACT:ISSUE+SENTIMENT+ACTIONS] [OUT:JSON]",
                "category": "customer_support",
                "priority": "high"
            },
            {
                "prompt": "Review this customer complaint about delayed shipping and draft a professional response.",
                "expected": "[REQ:REVIEW] [REQ:GENERATE:TYPE=RESPONSE] [TARGET:COMPLAINT:ISSUE=SHIPPING_DELAY] [CTX:TONE=PROFESSIONAL]",
                "category": "customer_support",
                "priority": "high"
            },
            {
                "prompt": "Classify this support ticket by urgency and category.",
                "expected": "[REQ:CLASSIFY] [TARGET:TICKET] [EXTRACT:URGENCY+CATEGORY]",
                "category": "customer_support",
                "priority": "medium"
            },
            {
                "prompt": "Summarize this 30-minute customer call transcript briefly.",
                "expected": "[REQ:SUMMARIZE:BRIEF] [TARGET:TRANSCRIPT:TYPE=CALL:DURATION=30]",
                "category": "customer_support",
                "priority": "medium"
            },
            {
                "prompt": "Identify escalation triggers in this customer conversation.",
                "expected": "[REQ:IDENTIFY] [TARGET:CONVERSATION] [EXTRACT:ESCALATION_TRIGGERS]",
                "category": "customer_support",
                "priority": "high"
            },
            
            # ============================================================
            # CODE ANALYSIS PROMPTS
            # ============================================================
            {
                "prompt": "Analyze this Python code and identify bugs, security issues, and performance problems.",
                "expected": "[REQ:ANALYZE] [TARGET:CODE:LANG=PYTHON] [EXTRACT:BUGS+SECURITY+PERFORMANCE]",
                "category": "code",
                "priority": "high"
            },
            {
                "prompt": "Debug this JavaScript function that returns incorrect results.",
                "expected": "[REQ:DEBUG] [TARGET:CODE:LANG=JAVASCRIPT]",
                "category": "code",
                "priority": "high"
            },
            {
                "prompt": "Optimize this SQL query for better performance.",
                "expected": "[REQ:OPTIMIZE:PERFORMANCE] [TARGET:QUERY:LANG=SQL]",
                "category": "code",
                "priority": "medium"
            },
            {
                "prompt": "Review this code for style and readability issues.",
                "expected": "[REQ:REVIEW] [TARGET:CODE] [EXTRACT:STYLE+READABILITY]",
                "category": "code",
                "priority": "low"
            },
            
            # ============================================================
            # DATA ANALYSIS PROMPTS
            # ============================================================
            {
                "prompt": "Analyze this sales data CSV and identify trends and outliers.",
                "expected": "[REQ:ANALYZE] [TARGET:DATA:FORMAT=CSV:TYPE=SALES] [EXTRACT:TRENDS+OUTLIERS]",
                "category": "data",
                "priority": "high"
            },
            {
                "prompt": "Extract all dates and amounts from this financial report.",
                "expected": "[REQ:EXTRACT] [TARGET:REPORT:TYPE=FINANCIAL] [EXTRACT:DATES+AMOUNTS]",
                "category": "data",
                "priority": "medium"
            },
            
            # ============================================================
            # CONTENT GENERATION PROMPTS
            # ============================================================
            {
                "prompt": "Generate a professional email declining a job offer with gratitude.",
                "expected": "[REQ:GENERATE:TYPE=EMAIL] [CTX:TONE=PROFESSIONAL] [CTX:INCLUDE=GRATITUDE]",
                "category": "generation",
                "priority": "medium"
            },
            {
                "prompt": "Write a brief summary of this article in plain text.",
                "expected": "[REQ:SUMMARIZE:BRIEF] [TARGET:ARTICLE] [OUT:PLAIN]",
                "category": "generation",
                "priority": "low"
            },
            {
                "prompt": "Create a detailed technical specification for this API.",
                "expected": "[REQ:GENERATE] [TARGET:SPECIFICATION:TYPE=API] [CTX:STYLE=DETAILED+TECHNICAL]",
                "category": "generation",
                "priority": "high"
            },
            
            # ============================================================
            # EXPLANATION PROMPTS
            # ============================================================
            {
                "prompt": "Explain quantum computing to a 10-year-old using simple analogies.",
                "expected": "[REQ:EXPLAIN:SIMPLE] [TARGET:CONCEPT:TOPIC=QUANTUM_COMPUTING] [CTX:AUDIENCE=CHILD:AGE=10] [CTX:METHOD=ANALOGIES]",
                "category": "explanation",
                "priority": "medium"
            },
            {
                "prompt": "Describe how DNS works in technical detail.",
                "expected": "[REQ:EXPLAIN:TECHNICAL] [TARGET:CONCEPT:TOPIC=DNS]",
                "category": "explanation",
                "priority": "medium"
            },
            
            # ============================================================
            # COMPARISON PROMPTS
            # ============================================================
            {
                "prompt": "Compare React and Vue.js frameworks and highlight their differences.",
                "expected": "[REQ:COMPARE] [TARGET:FRAMEWORK:ITEMS=REACT,VUE] [EXTRACT:DIFFERENCES]",
                "category": "comparison",
                "priority": "low"
            },
            
            # ============================================================
            # TRANSFORMATION PROMPTS
            # ============================================================
            {
                "prompt": "Convert this meeting transcript into a structured action items list with owners.",
                "expected": "[REQ:TRANSFORM] [TARGET:TRANSCRIPT:TYPE=MEETING] [EXTRACT:ACTION_ITEMS+OWNERS] [OUT:LIST:STRUCTURED]",
                "category": "transformation",
                "priority": "high"
            },
            {
                "prompt": "Translate this business proposal from English to Spanish.",
                "expected": "[REQ:TRANSFORM:LANGUAGE] [TARGET:DOCUMENT:TYPE=PROPOSAL] [CTX:FROM=ENGLISH:TO=SPANISH]",
                "category": "transformation",
                "priority": "low"
            },
            {
                "prompt": "Rewrite this technical documentation in a user-friendly tone.",
                "expected": "[REQ:TRANSFORM:STYLE] [TARGET:DOCUMENT:TYPE=TECHNICAL] [CTX:TONE=FRIENDLY:AUDIENCE=USER]",
                "category": "transformation",
                "priority": "medium"
            }
        ]
    
    def run_tests(self, encoder) -> Dict:
        """
        Run all test cases through the encoder
        
        Args:
            encoder: Instance of CLLMEncoder
            
        Returns:
            Dictionary with test results and statistics
        """
        print("\n" + "="*80)
        print("CLLM ENCODER - TEST SUITE")
        print("="*80)
        print(f"\nRunning {len(self.test_cases)} test cases...\n")
        
        passed = 0
        failed = 0
        partial = 0
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n[Test {i}/{len(self.test_cases)}] {test_case['category'].upper()}")
            print("-" * 80)
            
            # Compress the prompt
            result = encoder.compress(test_case['prompt'], verbose=False)
            
            # Analyze result
            issues = []
            has_req = len(result.intents) > 0
            has_target = len(result.targets) > 0
            
            if not has_req:
                issues.append("Missing REQ token")
            if not has_target:
                issues.append("Missing TARGET token")
            
            # Compare with expected (simplified matching)
            expected = test_case['expected']
            compressed = result.compressed
            
            # Check if key tokens are present
            matches_expected = self._compare_compressed(compressed, expected)
            
            # Categorize result
            if has_req and has_target and not issues:
                if matches_expected:
                    status = "✓ PASS"
                    passed += 1
                else:
                    status = "⚠ PARTIAL"
                    issues.append("Output differs from expected")
                    partial += 1
            else:
                status = "✗ FAIL"
                failed += 1
            
            # Store result
            test_result = EncoderTestResult(
                prompt=test_case['prompt'],
                compressed=compressed,
                expected=expected,
                matches=matches_expected,
                issues=issues,
                compression_ratio=result.compression_ratio,
                has_req=has_req,
                has_target=has_target,
                metadata={'category': test_case['category'], 'priority': test_case['priority']}
            )
            self.results.append(test_result)
            
            # Print result
            print(f"Status: {status}")
            print(f"Original: {test_case['prompt']}")
            print(f"Expected: {expected}")
            print(f"Got:      {compressed}")
            print(f"Compression: {result.compression_ratio}%")
            
            if issues:
                print(f"Issues: {', '.join(issues)}")
        
        # Summary statistics
        total = len(self.test_cases)
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Total Tests:    {total}")
        print(f"Passed:         {passed} ({passed/total*100:.1f}%)")
        print(f"Partial:        {partial} ({partial/total*100:.1f}%)")
        print(f"Failed:         {failed} ({failed/total*100:.1f}%)")
        
        # Coverage by category
        print("\n" + "-"*80)
        print("COVERAGE BY CATEGORY")
        print("-"*80)
        categories = {}
        for i, test_case in enumerate(self.test_cases):
            cat = test_case['category']
            if cat not in categories:
                categories[cat] = {'total': 0, 'passed': 0}
            categories[cat]['total'] += 1
            if self.results[i].has_req and self.results[i].has_target:
                categories[cat]['passed'] += 1
        
        for cat, stats in sorted(categories.items()):
            coverage = stats['passed'] / stats['total'] * 100
            print(f"{cat:20s}: {stats['passed']}/{stats['total']} ({coverage:.1f}%)")
        
        # Common issues
        print("\n" + "-"*80)
        print("COMMON ISSUES")
        print("-"*80)
        all_issues = []
        for result in self.results:
            all_issues.extend(result.issues)
        
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        for issue, count in sorted(issue_counts.items(), key=lambda x: -x[1]):
            print(f"  • {issue}: {count} occurrences")
        
        # Average compression
        avg_compression = sum(r.compression_ratio for r in self.results) / len(self.results)
        print(f"\nAverage Compression Ratio: {avg_compression:.1f}%")
        
        return {
            'total': total,
            'passed': passed,
            'partial': partial,
            'failed': failed,
            'pass_rate': passed / total * 100,
            'avg_compression': avg_compression,
            'results': self.results
        }
    
    def _compare_compressed(self, actual: str, expected: str) -> bool:
        """
        Compare compressed outputs (simplified)
        In production, this would be more sophisticated
        """
        # Check if all expected tokens are present
        expected_tokens = expected.split()
        actual_lower = actual.lower()
        
        matches = 0
        for token in expected_tokens:
            # Extract token type (REQ, TARGET, etc.)
            if '[' in token:
                token_type = token.split(':')[0].replace('[', '')
                if token_type.lower() in actual_lower:
                    matches += 1
        
        # Return true if most tokens match
        return matches / len(expected_tokens) > 0.5 if expected_tokens else False
    
    def export_results(self, filename: str = "test_results.json"):
        """Export test results to JSON for analysis"""
        import json
        
        export_data = []
        for result in self.results:
            export_data.append({
                'prompt': result.prompt,
                'compressed': result.compressed,
                'expected': result.expected,
                'matches': result.matches,
                'issues': result.issues,
                'compression_ratio': result.compression_ratio,
                'has_req': result.has_req,
                'has_target': result.has_target,
                "metadata": result.metadata
            })
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"\n✓ Results exported to {filename}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run the test suite"""
    
    print("\n" + "="*80)
    print("CLLM ENCODER - VALIDATION TEST")
    print("="*80)
    print("\nThis test suite will:")
    print("  1. Run the encoder on 20 diverse test cases")
    print("  2. Compare outputs with expected results")
    print("  3. Identify gaps and issues")
    print("  4. Provide actionable insights for iteration")
    print("\nIMPORTANT: Make sure you have installed:")
    print("  pip install spacy")
    print("  python -m spacy download en_core_web_sm")
    print("\n" + "="*80 + "\n")
    
    try:
        # Import the encoder
        from src.core.encoder import CLLMEncoder
        
        # Initialize encoder
        print("Initializing encoder...")
        encoder = CLLMEncoder()
        
        # Create test harness
        tester = EncoderTester()
        
        # Run tests
        results = tester.run_tests(encoder)
        
        # Export results
        tester.export_results()
        
        # Final verdict
        print("\n" + "="*80)
        print("VERDICT")
        print("="*80)
        
        if results['pass_rate'] >= 80:
            print("✓ EXCELLENT: Encoder is working well!")
            print("  → Ready to test on full 100-prompt dataset")
            print("  → Minor tweaks may improve partial matches")
        elif results['pass_rate'] >= 60:
            print("⚠ GOOD: Encoder is functional but needs improvement")
            print("  → Review failed cases and add missing patterns")
            print("  → Iterate on vocabulary and detection rules")
        else:
            print("✗ NEEDS WORK: Encoder requires significant improvements")
            print("  → Review detection logic for REQ and TARGET tokens")
            print("  → Check vocabulary coverage")
            print("  → Consider adding more detection strategies")
        
        print("\nNext steps:")
        print("  1. Review test_results.json for detailed analysis")
        print("  2. Fix identified issues in encoder.py")
        print("  3. Re-run tests until pass rate > 80%")
        print("  4. Then test on full 100-prompt dataset")
        
    except ImportError as e:
        print(f"ERROR: Could not import encoder.py: {e}")
        print("Make sure encoder.py is in the same directory")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()