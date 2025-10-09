"""
Real-World Performance Evaluator
Tests CLLM on production use cases
"""

import json
import time
import re
from typing import Dict, List
from pathlib import Path

from src.core.encoder import CLLMEncoder


class RealWorldTestCase:
    """Represents a real-world use case"""

    def __init__(self, name: str, category: str, prompt: str,
                 expected_tokens: List[str], context: str = ""):
        self.name = name
        self.category = category
        self.prompt = prompt
        self.expected_tokens = expected_tokens  # Tokens we expect to see
        self.context = context


class RealWorldEvaluator:
    """Evaluates CLLM on real-world scenarios"""

    def __init__(self, encoder: CLLMEncoder):
        """
        Args:
            encoder: The CLLMEncoder instance
        """
        self.encoder = encoder
        self.test_cases = self.create_test_cases()
        self.results = []

    def create_test_cases(self) -> List[RealWorldTestCase]:
        """Create suite of real-world test cases"""

        cases = []

        # === CUSTOMER SUPPORT SCENARIOS ===
        cases.append(RealWorldTestCase(
            name="Support Ticket Analysis",
            category="customer_support",
            prompt="""Analyze this customer support ticket and extract the main issue, 
            sentiment, and urgency level. Customer: "I've been trying to log in for 2 hours 
            and keep getting error 403. This is blocking my work!""",
        expected_tokens = ["REQ:ANALYZE", "TARGET:TICKET", "EXTRACT:ISSUE", "EXTRACT:SENTIMENT"]
        ))

        cases.append(RealWorldTestCase(
            name="Support Response Generation",
            category="customer_support",
            prompt="""Generate a professional response to this customer complaint: 
            "Your product stopped working after the update." Include an apology and 
            troubleshooting steps.""",
            expected_tokens=["REQ:GENERATE", "TARGET:RESPONSE"]
        ))

        cases.append(RealWorldTestCase(
            name="Ticket Routing",
            category="customer_support",
            prompt="""Classify this support ticket and route it to the appropriate team: 
            "Cannot connect to database, getting timeout errors." Categories: Technical, 
            Billing, Account, General.""",
            expected_tokens=["REQ:CLASSIFY", "TARGET:TICKET"]
        ))

        # === CODE ANALYSIS SCENARIOS ===
        cases.append(RealWorldTestCase(
            name="Bug Detection",
            category="code_analysis",
            prompt="""Review this Python code for bugs and security issues:
            def process_user_input(data):
                return eval(data)""",
            expected_tokens=["REQ:ANALYZE", "TARGET:CODE", "EXTRACT:BUGS", "EXTRACT:SECURITY"]
        ))

        cases.append(RealWorldTestCase(
            name="Code Optimization",
            category="code_analysis",
            prompt="""Optimize this code for better performance:
            for i in range(len(arr)):
                for j in range(len(arr)):
                    if arr[i] > arr[j]:
                        temp = arr[i]
                        arr[i] = arr[j]
                        arr[j] = temp""",
            expected_tokens=["REQ:OPTIMIZE", "TARGET:CODE"]
        ))

        cases.append(RealWorldTestCase(
            name="Code Documentation",
            category="code_analysis",
            prompt="""Generate documentation for this function explaining what it does, 
            parameters, and return value.""",
            expected_tokens=["REQ:GENERATE", "TARGET:DOCUMENT"]
        ))

        # === DATA ANALYSIS SCENARIOS ===
        cases.append(RealWorldTestCase(
            name="Data Extraction",
            category="data_analysis",
            prompt="""Extract all email addresses, phone numbers, and dates from this text: 
            Contact John at john@example.com or 555-1234. Meeting scheduled for 2024-03-15.""",
            expected_tokens=["REQ:EXTRACT", "EXTRACT:EMAILS", "EXTRACT:PHONES", "EXTRACT:DATES"]
        ))

        cases.append(RealWorldTestCase(
            name="Data Transformation",
            category="data_analysis",
            prompt="""Convert this CSV data to JSON format: 
            Name,Age,City
            Alice,25,NYC
            Bob,30,LA""",
            expected_tokens=["REQ:TRANSFORM", "TARGET:DATA", "OUT:JSON"]
        ))

        cases.append(RealWorldTestCase(
            name="Data Aggregation",
            category="data_analysis",
            prompt="""Analyze this sales data and calculate total revenue by region, 
            average order value, and identify top 3 products.""",
            expected_tokens=["REQ:ANALYZE", "TARGET:DATA"]
        ))

        # === CONTENT GENERATION SCENARIOS ===
        cases.append(RealWorldTestCase(
            name="Email Generation",
            category="content_generation",
            prompt="""Write a professional email to a client explaining a project delay. 
            Keep tone apologetic but confident. Include next steps.""",
            expected_tokens=["REQ:GENERATE", "TARGET:EMAIL"]
        ))

        cases.append(RealWorldTestCase(
            name="Report Summary",
            category="content_generation",
            prompt="""Summarize this quarterly report into 3 key bullet points highlighting 
            main achievements and challenges.""",
            expected_tokens=["REQ:SUMMARIZE", "TARGET:REPORT", "OUT:LIST"]
        ))

        cases.append(RealWorldTestCase(
            name="Documentation Writing",
            category="content_generation",
            prompt="""Create API documentation for a REST endpoint that accepts POST requests 
            with user data and returns a success/error response.""",
            expected_tokens=["REQ:GENERATE", "TARGET:DOCUMENT"]
        ))

        return cases

    def evaluate_test_case(self, test_case: RealWorldTestCase) -> Dict:
        """Evaluate a single test case"""

        # Measure compression time
        start_time = time.time()
        compressed = self.encoder.compress(test_case.prompt).compressed
        compression_time = time.time() - start_time

        # Extract tokens from compressed output
        actual_tokens = re.findall(r'\[([^\]]+)\]', compressed)

        # Check if expected tokens are present
        token_matches = {}
        for expected in test_case.expected_tokens:
            # Check if token (or its base) is in actual tokens
            found = any(expected.split(':')[0] in token for token in actual_tokens)
            token_matches[expected] = found

        # Calculate metrics
        token_coverage = sum(token_matches.values()) / len(token_matches) if token_matches else 0

        original_length = len(test_case.prompt)
        compressed_length = len(compressed)
        compression_ratio = (1 - compressed_length / original_length) * 100

        result = {
            'test_case': test_case.name,
            'category': test_case.category,
            'original_prompt': test_case.prompt,
            'compressed': compressed,
            'original_length': original_length,
            'compressed_length': compressed_length,
            'compression_ratio': compression_ratio,
            'compression_time': compression_time,
            'expected_tokens': test_case.expected_tokens,
            'actual_tokens': actual_tokens,
            'token_matches': token_matches,
            'token_coverage': token_coverage,
            'success': token_coverage >= 0.75  # 75% token coverage = success
        }

        self.results.append(result)
        return result

    def evaluate_all(self) -> Dict:
        """Evaluate all test cases"""

        print("=" * 80)
        print("🌍 REAL-WORLD PERFORMANCE EVALUATION")
        print("=" * 80 + "\n")

        print(f"Running {len(self.test_cases)} real-world test cases...\n")

        # Evaluate each test case
        for test_case in self.test_cases:
            result = self.evaluate_test_case(test_case)

            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['category']:20s} | {result['test_case']}")
            print(f"   Compression: {result['compression_ratio']:.1f}% | "
                  f"Token Coverage: {result['token_coverage']:.0%} | "
                  f"Time: {result['compression_time'] * 1000:.2f}ms")

        return self.calculate_metrics()

    def calculate_metrics(self) -> Dict:
        """Calculate aggregate metrics"""

        total = len(self.results)

        # Overall metrics
        metrics = {
            'total_test_cases': total,
            'success_rate': sum(1 for r in self.results if r['success']) / total,
            'avg_compression_ratio': sum(r['compression_ratio'] for r in self.results) / total,
            'avg_token_coverage': sum(r['token_coverage'] for r in self.results) / total,
            'avg_compression_time': sum(r['compression_time'] for r in self.results) / total,
        }

        # Per-category metrics
        categories = set(r['category'] for r in self.results)
        metrics['category_performance'] = {}

        for category in categories:
            category_results = [r for r in self.results if r['category'] == category]
            metrics['category_performance'][category] = {
                'total': len(category_results),
                'success_rate': sum(1 for r in category_results if r['success']) / len(category_results),
                'avg_compression': sum(r['compression_ratio'] for r in category_results) / len(category_results),
                'avg_coverage': sum(r['token_coverage'] for r in category_results) / len(category_results),
            }

        # Find problem cases
        metrics['failed_cases'] = [
            {
                'name': r['test_case'],
                'category': r['category'],
                'token_coverage': r['token_coverage'],
                'compressed': r['compressed']
            }
            for r in self.results
            if not r['success']
        ]

        return metrics

    def print_report(self, metrics: Dict):
        """Print detailed evaluation report"""

        print("\n" + "=" * 80)
        print("📊 REAL-WORLD PERFORMANCE RESULTS")
        print("=" * 80 + "\n")

        print(f"Total Test Cases:        {metrics['total_test_cases']}")
        print(f"Success Rate:            {metrics['success_rate']:.1%}")
        print(f"Avg Compression Ratio:   {metrics['avg_compression_ratio']:.1f}%")
        print(f"Avg Token Coverage:      {metrics['avg_token_coverage']:.1%}")
        print(f"Avg Compression Time:    {metrics['avg_compression_time'] * 1000:.2f}ms")

        # Category breakdown
        print(f"\n📋 Performance by Category:")
        print("-" * 80)
        print(f"{'Category':<25} {'Success Rate':<15} {'Avg Compression':<18} {'Coverage'}")
        print("-" * 80)

        for category, stats in metrics['category_performance'].items():
            print(f"{category:<25} {stats['success_rate']:<14.1%} "
                  f"{stats['avg_compression']:<17.1f}% {stats['avg_coverage']:.1%}")

        # Show failed cases
        if metrics['failed_cases']:
            print(f"\n⚠️  Failed Cases ({len(metrics['failed_cases'])}):")
            for case in metrics['failed_cases']:
                print(f"\n  • {case['name']} ({case['category']})")
                print(f"    Token Coverage: {case['token_coverage']:.0%}")
                print(f"    Compressed: {case['compressed']}")

        # Overall verdict
        print("\n" + "=" * 80)
        success_rate = metrics['success_rate']
        if success_rate >= 0.95:
            print("✅ EXCELLENT: Ready for production use (≥95% success)")
        elif success_rate >= 0.85:
            print("✅ GOOD: Suitable for most use cases (≥85% success)")
        elif success_rate >= 0.75:
            print("⚠️  MODERATE: Works for many cases but needs improvement (75-85%)")
        else:
            print("❌ NEEDS WORK: Not production-ready (<75% success)")

        print("=" * 80 + "\n")

    def export_results(self, output_file: str = "real_world_results.json"):
        """Export detailed results"""
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"💾 Detailed results saved to {output_file}\n")


def main():
    """Run real-world performance evaluation"""

    # Import encoder
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))

    from src.core.encoder import CLLMEncoder
    import spacy

    # Initialize encoder
    print("Initializing CLLM Encoder...\n")
    encoder = CLLMEncoder("en_core_web_sm")

    # Create evaluator
    evaluator = RealWorldEvaluator(encoder)

    # Run evaluation
    metrics = evaluator.evaluate_all()

    # Print report
    evaluator.print_report(metrics)

    # Export results
    evaluator.export_results()

    print("\n✅ Real-world performance evaluation complete!\n")


if __name__ == "__main__":
    main()