"""
GPT CLM Benchmark Script
========================

Tests CLM (Compressed Language Models) performance on OpenAI GPT models:
- GPT-4 Turbo
- GPT-4 Turbo Mini
- GPT-3.5 Turbo (nano)

Compares compressed vs natural language prompts for:
- Token usage
- Latency
- Cost
- Output quality
"""

import json
import time
import os
import sys
from typing import Optional

from components.ds_compression import CompressionConfig, DSEncoder

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: OpenAI package not installed!")
    print("Install with: pip install openai")
    sys.exit(1)

SYSTEM_PROMPT = """You are an NBA (Next Best Action) recommendation system for customer service agents.

TASK:
Analyze the customer service transcript and recommend the top 2 most relevant NBAs from the provided catalog.

ANALYSIS CRITERIA:
- Customer's primary issue and intent
- Current conversation context and history
- NBA prerequisites and applicability
- Expected resolution outcome
- Urgency and severity

OUTPUT FORMAT:
Return JSON with this exact structure:
{
  "primary_issue": "issue_category",
  "customer_intent": "what_customer_wants",
  "recommended_nbas": [
    {
      "nba_id": "NBA-XXX",
      "nba_title": "title",
      "confidence": 0.95,
      "reasoning": "why this NBA is most relevant"
    },
    {
      "nba_id": "NBA-YYY",
      "nba_title": "title",
      "confidence": 0.80,
      "reasoning": "why this is second choice"
    }
  ]
}

CONFIDENCE SCORING:
- 0.90-1.00: Perfect match, all prerequisites met
- 0.75-0.89: Strong match, minor considerations
- 0.60-0.74: Good match, some prerequisites unclear
- Below 0.60: Not recommended

PRIORITIZATION:
1. NBAs that directly resolve the customer's stated problem
2. NBAs matching conversation context and history
3. NBAs with satisfied prerequisites
4. Higher priority NBAs when multiple options exist"""


class RunGPTCLMBenchmark:
    """
    Benchmark CLM compression vs natural language on GPT models.

    Models tested:
    - gpt-4-turbo: Latest GPT-4 (highest quality)
    - gpt-4-turbo-preview: GPT-4 preview (mini version)
    - gpt-3.5-turbo: Fast and cheap (nano equivalent)
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize GPT CLM Benchmark.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.client = OpenAI(api_key=api_key)

        # GPT model names (update these if needed)
        self._gpt_models: tuple[str, str, str] = (
            "gpt-4-turbo",  # GPT-4.1 equivalent
            "gpt-4-turbo-preview",  # GPT-4.1-mini equivalent
            "gpt-3.5-turbo",  # GPT nano equivalent
        )

        # For display/results
        self._model_display_names = {
            "gpt-4-turbo": "gpt-4-turbo (4.1)",
            "gpt-4-turbo-preview": "gpt-4-turbo-mini (4.1-mini)",
            "gpt-3.5-turbo": "gpt-3.5-turbo (nano)",
        }

        # Pricing (per 1M tokens) - update as needed
        self._pricing = {
            "gpt-4-turbo": {"input": 10.00, "output": 30.00},
            "gpt-4-turbo-preview": {"input": 10.00, "output": 30.00},
            "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        }

    @staticmethod
    def dump_result(result: dict, filename: str = "gpt_clm_vs_nl.json") -> None:
        """Save benchmark results to JSON file."""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Results saved to: {filename}")

    @staticmethod
    def load_nbas() -> list[dict]:
        """Load NBA catalog from JSON file."""
        with open("./data/raw/nbas_dataset.json", "r") as f:
            nbas: list = json.load(f)
        return nbas

    @staticmethod
    def load_transcripts() -> list[dict]:
        """Load transcripts from JSON file."""
        with open("transcript_analysis.json", "r") as f:
            transcripts: list[dict[str, str]] = json.load(f)
        return transcripts

    @staticmethod
    def compress_nba_catalog(nbas: list) -> str:
        """
        Compress NBA catalog: ~1,100 tokens → ~300 tokens

        Reduces 12 NBAs from full JSON to compressed format:
        [NBA:001:TITLE:PRI=HIG:CAT=billing:PREREQ=x+y:ACT=a+b]

        Args:
            nbas: List of NBA dictionaries

        Returns:
            Compressed string representation
        """

        config = CompressionConfig(
            required_fields=["id", "title", "description", "category"],
            auto_detect=False,
        )
        compressor = DSEncoder(config=config, catalog_name="kb")
        return compressor.encode(nbas)

    def calculate_cost(
        self, model: str, input_tokens: int, output_tokens: int
    ) -> float:
        """
        Calculate cost for API call.

        Args:
            model: Model name
            input_tokens: Input token count
            output_tokens: Output token count

        Returns:
            Cost in USD
        """
        pricing = self._pricing.get(model, {"input": 0, "output": 0})
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    def run(
        self,
        max_transcripts: int = 10,
        specific_index: Optional[int] = None,
        models_to_test: Optional[list[str]] = None,
    ) -> None:
        """
        Run benchmark on GPT models.

        Args:
            max_transcripts: Maximum number of transcripts to test
            specific_index: Test only specific transcript index (for debugging)
            models_to_test: List of model names to test (None = test all)
        """
        print(f"\n{'=' * 70}")
        print("GPT CLM BENCHMARK")
        print("=" * 70)

        # Load data
        transcripts = self.load_transcripts()
        nbas = self.load_nbas()
        compressed_nbas = self.compress_nba_catalog(nbas)

        # CLM system prompt (compressed)
        clm_system_prompt = """You are an NBA recommendation system for customer service agents.

Analyze the transcript and recommend the top 2 most relevant NBAs.

Consider these factors:
- Primary issue and customer intent
- Conversation context and history
- NBA prerequisites and applicability
- Expected resolution and urgency

Return JSON:
{
  "primary_issue": "category",
  "customer_intent": "what_they_want",
  "recommended_nbas": [
    {"nba_id": "NBA-XXX", "nba_title": "title", "confidence": 0.95, "reasoning": "why relevant"},
    {"nba_id": "NBA-YYY", "nba_title": "title", "confidence": 0.80, "reasoning": "why second"}
  ]
}

Confidence scores:
0.90-1.00 = Perfect match, all prerequisites met
0.75-0.89 = Strong match with minor considerations
0.60-0.74 = Good match, some prerequisites unclear
Below 0.60 = Not recommended

Prioritize:
1. NBAs that directly resolve the stated problem
2. NBAs matching conversation context
3. NBAs with satisfied prerequisites
4. Higher priority NBAs when multiple options exist"""

        # Initialize results
        models = models_to_test or list(self._gpt_models)
        result: dict = {model: {"clm": [], "nl": []} for model in models}

        # Show compression stats
        print(f"\n{'=' * 70}")
        print("NBA CATALOG COMPRESSION")
        print("=" * 70)
        print(f"Original: ~{len(json.dumps(nbas)) // 4} tokens")
        print(f"Compressed: ~{len(compressed_nbas) // 4} tokens")
        print(
            f"Savings: {(1 - len(compressed_nbas) / len(json.dumps(nbas))) * 100:.1f}%"
        )
        print(f"Compressed NBAs (first 150 chars): {compressed_nbas[:150]}...")
        print("=" * 70 + "\n")

        # Determine which transcripts to test
        if specific_index is not None:
            transcript_indices = [specific_index]
        else:
            transcript_indices = range(min(max_transcripts, len(transcripts)))

        # Run benchmark
        try:
            for model in models:
                display_name = self._model_display_names.get(model, model)
                print(f"\n{'=' * 70}")
                print(f"TESTING MODEL: {display_name}")
                print("=" * 70)

                for idx in transcript_indices:
                    transcript = transcripts[idx]
                    tc = transcript.get("compressed")
                    to = transcript.get("original")

                    print(f"\n--- Transcript {idx + 1}/{len(transcripts)} ---")
                    print(f"Original length: {len(to)} chars")
                    print(f"Compressed length: {len(tc)} chars")
                    print(f"Compression ratio: {(1 - len(tc) / len(to)) * 100:.1f}%")

                    # Test CLM (compressed)
                    print("\n  🔵 Testing CLM (compressed)...")
                    start_time = time.time()
                    try:
                        tc_response = self.client.chat.completions.create(
                            model=model,
                            max_tokens=500,
                            temperature=0.0,
                            messages=[
                                {"role": "system", "content": clm_system_prompt},
                                {
                                    "role": "user",
                                    "content": f"""Analyze the following call transcript:

                                    TRANSCRIPT:
                                    {tc}
                                    
                                    NBA CATALOG:
                                    {compressed_nbas}
                                    
                                    Recommend the top 2 most relevant NBAs.""",
                                },
                            ],
                        )
                        tc_latency = time.time() - start_time
                        tc_input_tokens = tc_response.usage.prompt_tokens  # type: ignore
                        tc_output_tokens = tc_response.usage.completion_tokens  # type: ignore
                        tc_total_tokens = tc_response.usage.total_tokens  # type: ignore
                        tc_output = tc_response.choices[0].message.content  # type: ignore
                        tc_cost = self.calculate_cost(
                            model, tc_input_tokens, tc_output_tokens
                        )

                        result[model]["clm"].append(
                            {
                                "transcript_index": idx,
                                "llm_output": tc_output,
                                "original": to,
                                "compressed": tc,
                                "total_tokens": tc_total_tokens,
                                "input_tokens": tc_input_tokens,
                                "output_tokens": tc_output_tokens,
                                "latency": tc_latency,
                                "cost_usd": tc_cost,
                                "model": model,
                            }
                        )

                        print(
                            f"     Tokens: {tc_total_tokens} (in: {tc_input_tokens}, out: {tc_output_tokens})"
                        )
                        print(f"     Latency: {tc_latency:.2f}s")
                        print(f"     Cost: ${tc_cost:.6f}")

                    except Exception as e:
                        print(f"     ❌ Error: {e}")
                        result[model]["clm"].append(
                            {"error": str(e), "transcript_index": idx}
                        )

                    # Test Natural Language (uncompressed)
                    print("\n  🟢 Testing Natural Language (uncompressed)...")
                    start_time = time.time()
                    try:
                        to_response = self.client.chat.completions.create(
                            model=model,
                            max_tokens=500,
                            temperature=0.0,
                            messages=[
                                {"role": "system", "content": SYSTEM_PROMPT},
                                {
                                    "role": "user",
                                    "content": f"""Analyze the following call transcript:

                                    TRANSCRIPT:
                                    {to}
                                    
                                    NBA CATALOG:
                                    {json.dumps(nbas)}
                                    
                                    Recommend the top 2 most relevant NBAs.""",
                                },
                            ],
                        )
                        to_latency = time.time() - start_time
                        to_input_tokens = to_response.usage.prompt_tokens  # type: ignore
                        to_output_tokens = to_response.usage.completion_tokens  # type: ignore
                        to_total_tokens = to_response.usage.total_tokens  # type: ignore
                        to_output = to_response.choices[0].message.content  # type: ignore
                        to_cost = self.calculate_cost(
                            model, to_input_tokens, to_output_tokens
                        )

                        result[model]["nl"].append(
                            {
                                "transcript_index": idx,
                                "llm_output": to_output,
                                "original": to,
                                "total_tokens": to_total_tokens,
                                "input_tokens": to_input_tokens,
                                "output_tokens": to_output_tokens,
                                "latency": to_latency,
                                "cost_usd": to_cost,
                                "model": model,
                            }
                        )

                        print(
                            f"     Tokens: {to_total_tokens} (in: {to_input_tokens}, out: {to_output_tokens})"
                        )
                        print(f"     Latency: {to_latency:.2f}s")
                        print(f"     Cost: ${to_cost:.6f}")

                    except Exception as e:
                        print(f"     ❌ Error: {e}")
                        result[model]["nl"].append(
                            {"error": str(e), "transcript_index": idx}
                        )

                    # Show comparison
                    if (
                        "error" not in result[model]["clm"][-1]
                        and "error" not in result[model]["nl"][-1]
                    ):
                        token_savings = (1 - tc_total_tokens / to_total_tokens) * 100
                        latency_savings = (1 - tc_latency / to_latency) * 100
                        cost_savings = (1 - tc_cost / to_cost) * 100

                        print("\n  💰 SAVINGS:")
                        print(f"     Tokens: {token_savings:.1f}%")
                        print(f"     Latency: {latency_savings:.1f}%")
                        print(f"     Cost: {cost_savings:.1f}%")

                    print()

        except KeyboardInterrupt:
            print("\n\n⚠️  Benchmark interrupted by user")
        except Exception as e:
            print(f"\n\n❌ ERROR: {e}")
            import traceback

            traceback.print_exc()
        finally:
            # Always save results
            self.dump_result(result)
            self.print_summary(result)

    def print_summary(self, result: dict) -> None:
        """Print benchmark summary statistics."""
        print(f"\n{'=' * 70}")
        print("BENCHMARK SUMMARY")
        print("=" * 70)

        for model, data in result.items():
            display_name = self._model_display_names.get(model, model)
            print(f"\n{display_name}:")

            clm_data = [r for r in data["clm"] if "error" not in r]
            nl_data = [r for r in data["nl"] if "error" not in r]

            if not clm_data or not nl_data:
                print("  ⚠️  Insufficient data for comparison")
                continue

            # Calculate averages
            avg_clm_tokens = sum(r["total_tokens"] for r in clm_data) / len(clm_data)
            avg_nl_tokens = sum(r["total_tokens"] for r in nl_data) / len(nl_data)
            avg_clm_latency = sum(r["latency"] for r in clm_data) / len(clm_data)
            avg_nl_latency = sum(r["latency"] for r in nl_data) / len(nl_data)
            avg_clm_cost = sum(r["cost_usd"] for r in clm_data) / len(clm_data)
            avg_nl_cost = sum(r["cost_usd"] for r in nl_data) / len(nl_data)

            token_savings = (1 - avg_clm_tokens / avg_nl_tokens) * 100
            latency_savings = (1 - avg_clm_latency / avg_nl_latency) * 100
            cost_savings = (1 - avg_clm_cost / avg_nl_cost) * 100

            print(
                f"  Avg Tokens:  CLM {avg_clm_tokens:.0f} | NL {avg_nl_tokens:.0f} | Savings: {token_savings:.1f}%"
            )
            print(
                f"  Avg Latency: CLM {avg_clm_latency:.2f}s | NL {avg_nl_latency:.2f}s | Savings: {latency_savings:.1f}%"
            )
            print(
                f"  Avg Cost:    CLM ${avg_clm_cost:.6f} | NL ${avg_nl_cost:.6f} | Savings: {cost_savings:.1f}%"
            )

        print("=" * 70)


def main():
    """Main entry point with command-line argument support."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Benchmark CLM compression on GPT models"
    )
    parser.add_argument(
        "--max-transcripts",
        type=int,
        default=10,
        help="Maximum number of transcripts to test (default: 10)",
    )
    parser.add_argument(
        "--index",
        type=int,
        default=None,
        help="Test only specific transcript index (for debugging)",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=None,
        help="Specific models to test (default: all)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="gpt_clm_vs_nl.json",
        help="Output filename (default: gpt_clm_vs_nl.json)",
    )

    args = parser.parse_args()

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY environment variable not set!")
        print("   Set it with: export OPENAI_API_KEY='your-api-key'")
        sys.exit(1)

    # Run benchmark
    benchmark = RunGPTCLMBenchmark()
    benchmark.run(
        max_transcripts=args.max_transcripts,
        specific_index=args.index,
        models_to_test=args.models,
    )


if __name__ == "__main__":
    main()
