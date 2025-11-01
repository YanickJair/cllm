import json
import time
import os
import sys

from src.core.encoder import CLLMEncoder

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import anthropic

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



class RunCLMBenchmark:
    def __init__(self) -> None:
        self.client = anthropic.Anthropic()
        self.encoder = CLLMEncoder()
        self._claude_models: tuple[str, str, str] = ("claude-sonnet-4-5", "claude-haiku-3.5", "claude-opus-4.1")

    @staticmethod
    def dump_result(result: dict) -> None:
        with open("clm_vs_nl.json", "w") as f:
            json.dump(result, f)

    @staticmethod
    def load_nbas() -> list[dict]:
        with open('./data/raw/nbas_dataset.json', 'r') as f:
            nbas: list = json.load(f)
        return nbas

    @staticmethod
    def load_transcripts() -> list[dict]:
        with open('transcript_analysis.json', 'r') as f:
            transcripts: list[dict[str, str]] = json.load(f)
        return transcripts

    def run(self) -> None:
        transcripts = self.load_transcripts()
        nbas = self.load_nbas()

        result: dict = {
            "claude-sonnet-4-5": {"clm": [], "nl": []},
            "claude-haiku-3.5": {"clm": [], "nl": []},
            "claude-opus-4.1": {"clm": [], "nl": []},
        }
        clm_system_prompt = self.encoder.compress(SYSTEM_PROMPT)
        print(clm_system_prompt.compressed)
        for model in self._claude_models:
            for transcript in transcripts[:10]:
                tc = transcript.get("compressed")
                to = transcript.get("original")

                print(f"\nOriginal length: {len(to)} chars")
                print(f"Compressed length: {len(tc)} chars")
                print(f"NBAs length: {len(nbas)}")
                print(f"Compression ratio: {(1 - len(tc) / len(to)) * 100:.1f}%")

                start_time = time.time()
                tc_message = self.client.messages.create(
                    model=model,
                    max_tokens=1000,
                    system=clm_system_prompt.compressed,
                    messages=[{
                        "role": "user",
                        "content": f"""Analyze the following call transcript:
                        TRANSCRIPT:
                        {tc}

                        NBA CATALOG:
                        {json.dumps(nbas[:5])}

                        Recommend the top 2 most relevant NBAs."""
                    }]
                )
                tc_latency = time.time() - start_time
                tc_tokens = tc_message.usage.input_tokens + tc_message.usage.output_tokens
                tc_output = tc_message.content[0].text  # type: ignore

                result[model]["clm"].append({
                    "llm_output": tc_output,
                    "original": to,  # Store original for comparison
                    "compressed": tc,
                    "n_tokens": tc_tokens,
                    "latency": tc_latency,
                    "input_tokens": tc_message.usage.input_tokens,
                    "output_tokens": tc_message.usage.output_tokens,
                    "model": model
                })
                print(f"  CLM: {tc_tokens} tokens, {tc_latency:.2f}s = {result}")
                break


                start_time = time.time()
                to_message = self.client.messages.create(
                    model=model,
                    max_tokens=1000,
                    system=SYSTEM_PROMPT,
                    messages=[{
                        "role": "user",
                        "content": f"""Analyze the following call transcript:
                        TRANSCRIPT:
                        {to}

                        NBA CATALOG:
                        {json.dumps(nbas)}

                        Recommend the top 2 most relevant NBAs."""
                    }]
                )
                to_latency = time.time() - start_time
                to_tokens = to_message.usage.input_tokens + to_message.usage.output_tokens
                to_output = to_message.content[0].text  # type: ignore

                result[model]["nl"].append({
                    "llm_output": to_output,
                    "original": to,
                    "n_tokens": to_tokens,
                    "latency": to_latency,
                    "input_tokens": to_message.usage.input_tokens,
                    "output_tokens": to_message.usage.output_tokens,
                    "model": model
                })

                print(f"  Natural: {to_tokens} tokens, {to_latency:.2f}s")
                print(
                    f"  Savings: {(1 - tc_tokens / to_tokens) * 100:.1f}% tokens, {(1 - tc_latency / to_latency) * 100:.1f}% latency")
                print()
            break
        self.dump_result(result)

if __name__ == "__main__":
    benchmark = RunCLMBenchmark()
    benchmark.run()