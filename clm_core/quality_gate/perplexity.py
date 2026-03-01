import re
import time
from typing import Optional

from anthropic import Anthropic

from . import PerplexityResult


class PerplexityAnalyzer:
    """
    Tests LLM-native comprehension of CLM output by comparing responses
    to the same task delivered with original vs. compressed input.

    Method:
    1. Send both prompts to Claude (or any LLM) with a fixed evaluation task
    2. Compare responses for: structural match, key fact preservation, latency
    3. Score comprehension on a 0–1 composite

    This directly validates CLM's core claim: LLMs understand compressed
    tokens natively without fine-tuning.

    Note: Uses Anthropic API. Set ANTHROPIC_API_KEY in environment.
    Falls back to heuristic scoring if API is unavailable.
    """

    EVALUATION_TASK = """
    Given the above context, respond with a JSON object containing:
    {
      "primary_issue": "<what the customer needed>",
      "resolution": "<how it was resolved>",
      "sentiment": "<customer sentiment>",
      "follow_up_needed": <true|false>,
      "key_facts": ["<fact1>", "<fact2>", "<fact3>"]
    }
    Respond ONLY with the JSON object.
    """

    COMPREHENSION_THRESHOLD = 0.82
    MODEL = "claude-haiku-4-5-20251001"  # fast model for quality testing

    def __init__(self, api_key: Optional[str] = None):
        try:
            self.client = Anthropic(api_key=api_key)
            self._api_available = True
        except Exception:
            self._api_available = False

    def analyze(
        self,
        original: str,
        compressed: str,
        verbose: bool = False,
    ) -> PerplexityResult:
        if self._api_available:
            return self._analyze_via_api(original, compressed, verbose)
        else:
            return self._analyze_heuristic(original, compressed)

    def _call_llm(self, prompt: str) -> tuple[str, float, int]:
        """Returns (response_text, latency_ms, token_count)."""
        start = time.time()
        response = self.client.messages.create(
            model=self.MODEL,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        latency_ms = (time.time() - start) * 1000
        text = response.content[0].text
        token_count = response.usage.output_tokens
        return text, latency_ms, token_count

    def _analyze_via_api(
        self,
        original: str,
        compressed: str,
        verbose: bool,
    ) -> PerplexityResult:
        orig_prompt = f"{original}\n\n{self.EVALUATION_TASK}"
        CLM_prompt = f"{compressed}\n\n{self.EVALUATION_TASK}"

        if verbose:
            print("Calling LLM with original prompt...")
        orig_response, orig_latency, orig_tokens = self._call_llm(orig_prompt)

        if verbose:
            print("Calling LLM with compressed prompt...")
        CLM_response, CLM_latency, CLM_tokens = self._call_llm(CLM_prompt)

        orig_data = self._safe_parse_json(orig_response)
        CLM_data = self._safe_parse_json(CLM_response)

        orig_facts = set(f.lower() for f in orig_data.get("key_facts", []))
        CLM_facts = set(f.lower() for f in CLM_data.get("key_facts", []))

        facts_preserved = []
        facts_lost = []
        for of in orig_facts:
            of_words = set(of.split())
            matched = any(len(of_words & set(cf.split())) >= 2 for cf in CLM_facts)
            if matched:
                facts_preserved.append(of)
            else:
                facts_lost.append(of)

        expected_keys = {
            "primary_issue",
            "resolution",
            "sentiment",
            "follow_up_needed",
            "key_facts",
        }
        structure_preserved = expected_keys.issubset(set(CLM_data.keys()))

        field_similarities = []
        for key in ["primary_issue", "resolution", "sentiment"]:
            ov = orig_data.get(key, "").lower()
            cv = CLM_data.get(key, "").lower()
            if ov and cv:
                ov_words = set(ov.split())
                cv_words = set(cv.split())
                jaccard = (
                    len(ov_words & cv_words) / len(ov_words | cv_words)
                    if ov_words | cv_words
                    else 0
                )
                field_similarities.append(jaccard)
        response_similarity = (
            sum(field_similarities) / len(field_similarities)
            if field_similarities
            else 0.0
        )

        latency_improvement = ((orig_latency - CLM_latency) / orig_latency) * 100

        fact_score = len(facts_preserved) / len(orig_facts) if orig_facts else 1.0
        comprehension_score = (
            fact_score * 0.4
            + response_similarity * 0.4
            + (1.0 if structure_preserved else 0.0) * 0.2
        )

        return PerplexityResult(
            original_response_tokens=orig_tokens,
            compressed_response_tokens=CLM_tokens,
            original_latency_ms=round(orig_latency, 1),
            compressed_latency_ms=round(CLM_latency, 1),
            latency_improvement=round(latency_improvement, 1),
            response_similarity=round(response_similarity, 4),
            structure_preserved=structure_preserved,
            key_facts_preserved=facts_preserved,
            facts_lost=facts_lost,
            comprehension_score=round(comprehension_score, 4),
            passed=comprehension_score >= self.COMPREHENSION_THRESHOLD,
        )

    def _analyze_heuristic(self, original: str, compressed: str) -> PerplexityResult:
        """
        Offline fallback when API is unavailable.
        Uses token overlap between original and compressed as a proxy
        for how much context the LLM would receive.
        """
        # Normalize both to comparable token sets
        orig_tokens = set(re.findall(r"[A-Z_]{3,}", original.upper()))
        CLM_tokens = set(re.findall(r"[A-Z_]{3,}", compressed.upper()))

        overlap = orig_tokens & CLM_tokens
        coverage = len(overlap) / len(orig_tokens) if orig_tokens else 1.0

        return PerplexityResult(
            original_response_tokens=0,
            compressed_response_tokens=0,
            original_latency_ms=0.0,
            compressed_latency_ms=0.0,
            latency_improvement=0.0,
            response_similarity=round(coverage, 4),
            structure_preserved=True,
            key_facts_preserved=list(overlap),
            facts_lost=list(orig_tokens - CLM_tokens),
            comprehension_score=round(coverage, 4),
            passed=coverage >= self.COMPREHENSION_THRESHOLD,
        )

    @staticmethod
    def _safe_parse_json(text: str) -> dict:
        """Parse JSON response, tolerating markdown code fences."""
        import json

        clean = re.sub(r"```(?:json)?|```", "", text).strip()
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            return {}
