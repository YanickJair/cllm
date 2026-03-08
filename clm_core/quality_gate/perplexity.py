import os
import re
import time
from typing import Literal, Annotated

from annotated_doc import Doc

from . import PerplexityResult, PerplexityConfig


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

    Set ANTHROPIC_API_KEY or OPENAI_CLIENT_KEY in environment depending on
    the chosen client. Falls back to heuristic scoring if the client cannot
    be initialized.
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
    ANTHROPIC_DEFAULT_MODEL = "claude-haiku-4-5-20251001"
    OPENAI_DEFAULT_MODEL = "gpt-5-nano-2025-08-07"

    def __init__(
        self,
        llm_client: Annotated[
            Literal["anthropic", "openai"] | None,
            Doc("""
            Which LLM client to use? Right now there are only two options:
                - Anthropic
                - OpenAI
            If no client is set, the perplexity analysis will fallback to Heuristics analysis.
            If a client is set, the PerplexityConfig must be set as well in order to create the connection.
            """),
        ] = None,
        cfg: Annotated[
            PerplexityConfig | None,
            Doc("""
            PerplexityConfig refers to LLM configuration.
            
            **Example**

            ```python
            from clm_core import PerplexityConfig. We recommend using small models for the task.

            pp_cfg = PerplexityConfig(
                llm_model=...,
                api_key=...,
                host_url=...,
                temperature=...,
            )
            encoded = encoder.encode(original)
            structured = encoder.to_dict(encoded)
            ```
            """),
        ] = None,
    ) -> None:
        if not llm_client or llm_client not in ("anthropic", "openai"):
            raise NotImplementedError(f"Unrecognized LLM client {llm_client}")
        self.llm_client = llm_client
        try:
            if llm_client == "anthropic":
                from anthropic import Anthropic

                self.client = Anthropic(
                    api_key=os.getenv("ANTHROPIC_API_KEY"), base_url=self.BASE_URL
                )
            else:
                from openai import OpenAI

                self.client = OpenAI(
                    api_key=os.getenv("OPENAI_CLIENT_KEY"), base_url=self.BASE_URL
                )
            self._api_available = True
        except Exception:
            print(
                f"{llm_client} model not available or key not provided. Make sure you have installed {llm_client} and set the key."
            )
            self._api_available = False

    def analyze(
        self,
        original: Annotated[
            str,
            Doc("""
            The original transcript (transcript, prompt, etc.) used in the CLM.

            This input is going to be used against compressed to perform the perplexity analysis.
            """),
        ],
        compressed: Annotated[
            str,
            Doc("""
            The compressed transcript (transcript, prompt, etc.) used in the CLM.

            This input is going to be used against original to perform the conditional entropy analysis.
            """),
        ],
        task: Annotated[
            str | None,
            Doc("""
            The task to perform the perplexity analysis. You can define the task according to your
            dataset and your need. The task will be performed on both original and compressed data.
            
            If no task is defined, and perplexity was set to run, the default task will be performed:
                Given the above context, respond with a JSON object containing:
                {
                  "primary_issue": "<what the customer needed>",
                  "resolution": "<how it was resolved>",
                  "sentiment": "<customer sentiment>",
                  "follow_up_needed": <true|false>,
                  "key_facts": ["<fact1>", "<fact2>", "<fact3>"]
                }
                Respond ONLY with the JSON object.
            """),
        ] = None,
        verbose: Annotated[
            bool,
            Doc("""
            A flag that enables verbose output.
            
            Defaults to False.
            """),
        ] = False,
    ) -> PerplexityResult:
        if self._api_available:
            return self._analyze_via_api(original, compressed, verbose, task)
        else:
            return self._analyze_heuristic(original, compressed)

    def _call_llm(
        self,
        prompt: Annotated[
            str, Doc("Full prompt string to send to the configured LLM.")
        ],
    ) -> tuple[str, float, int]:
        """Returns (response_text, latency_ms, token_count)."""
        start = time.time()
        if self.llm_client == "anthropic":
            response = self.client.messages.create(
                model=self.ANTHROPIC_MODEL,
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text
            token_count = response.usage.output_tokens
        else:
            response = self.client.chat.completions.create(
                model=self.OPENAI_MODEL,
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.choices[0].message.content
            token_count = response.usage.completion_tokens
        latency_ms = (time.time() - start) * 1000
        return text, latency_ms, token_count

    def _analyze_via_api(
        self,
        original: str,
        compressed: str,
        verbose: bool,
        task: str = None,
    ) -> PerplexityResult:
        orig_prompt = f"{original}\n\n{self.EVALUATION_TASK if not task else task}"
        clm_prompt = f"{compressed}\n\n{self.EVALUATION_TASK if not task else task}"

        if verbose:
            print("Calling LLM with original prompt...")
        orig_response, orig_latency, orig_tokens = self._call_llm(orig_prompt)

        if verbose:
            print("Calling LLM with compressed prompt...")
        clm_response, clm_latency, clm_tokens = self._call_llm(clm_prompt)

        orig_data = self._safe_parse_json(orig_response)
        clm_data = self._safe_parse_json(clm_response)

        orig_facts = {f.lower() for f in orig_data.get("key_facts", [])}
        clm_facts = {f.lower() for f in clm_data.get("key_facts", [])}

        facts_preserved = []
        facts_lost = []
        for of in orig_facts:
            of_words = set(of.split())
            matched = any(len(of_words & set(cf.split())) >= 2 for cf in clm_facts)
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
        structure_preserved = expected_keys.issubset(set(clm_data.keys()))

        field_similarities = []
        for key in ["primary_issue", "resolution", "sentiment"]:
            ov = orig_data.get(key, "").lower()
            cv = clm_data.get(key, "").lower()
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

        latency_improvement = ((orig_latency - clm_latency) / orig_latency) * 100

        fact_score = len(facts_preserved) / len(orig_facts) if orig_facts else 1.0
        comprehension_score = (
            fact_score * 0.4
            + response_similarity * 0.4
            + (1.0 if structure_preserved else 0.0) * 0.2
        )

        return PerplexityResult(
            original_response_tokens=orig_tokens,
            compressed_response_tokens=clm_tokens,
            original_latency_ms=round(orig_latency, 1),
            compressed_latency_ms=round(clm_latency, 1),
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
        clm_tokens = set(re.findall(r"[A-Z_]{3,}", compressed.upper()))

        overlap = orig_tokens & clm_tokens
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
            facts_lost=list(orig_tokens - clm_tokens),
            comprehension_score=round(coverage, 4),
            passed=coverage >= self.COMPREHENSION_THRESHOLD,
        )

    @staticmethod
    def _safe_parse_json(text: str) -> dict:
        """Parse JSON response, tolerating Markdown code fences."""
        import json

        clean = re.sub(r"```(?:json)?|```", "", text).strip()
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            return {}
