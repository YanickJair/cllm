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
        self._claude_models: tuple[str, str] = ("claude-haiku-4-5-20251001", "claude-opus-4-1-20250805")

    @staticmethod
    def dump_result(result: dict) -> None:
        with open("clm_vs_nl.json", "w", encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False)

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

    @staticmethod
    def compress_nba_catalog(nbas: list) -> str:
        """
        Compress NBA catalog: ~1,100 tokens → ~300 tokens

        Reduces 12 NBAs from full JSON to compressed format:
        [NBA:001:TITLE:PRI=HIG:CAT=billing:PREREQ=x+y:ACT=a+b]
        """

        def compress_single_nba(nba: dict) -> str:
            nba_id = nba.get('id', '').replace('NBA-', '')
            title = nba.get('title', '').upper().replace(' ', '_')[:25]
            priority = nba.get('priority', 'MEDIUM').upper()[:3]
            category = nba.get('category', '').lower()[:10]

            prereqs = nba.get('prerequisites', [])
            prereq_str = '+'.join([p.replace(' ', '_').lower() for p in prereqs]) if prereqs else ''

            actions = nba.get('actions', [])
            action_names = []
            for action in actions:
                if isinstance(action, dict):
                    name = action.get('name', '').lower().replace(' ', '_')
                    if name:
                        action_names.append(name)
            action_str = '+'.join(action_names) if action_names else ''

            parts = [f"NBA:{nba_id}:{title}"]
            if priority and priority != 'MED':
                parts.append(f"PRI={priority}")
            if category:
                parts.append(f"CAT={category}")
            if prereq_str:
                parts.append(f"PREREQ={prereq_str}")
            if action_str:
                parts.append(f"ACT={action_str}")

            return f"[{':'.join(parts)}]"

        return ' '.join([compress_single_nba(nba) for nba in nbas])

    def run(self) -> None:
        transcripts = self.load_transcripts()
        nbas = self.load_nbas()
        compressed_nbas = self.compress_nba_catalog(nbas)

        result: dict = {
            "claude-sonnet-4-5": {"clm": [], "nl": []},
            "claude-haiku-4-5-20251001": {"clm": [], "nl": []},
            "claude-opus-4-1-20250805": {"clm": [], "nl": []},
        }
        clm_system_prompt = """[SYS:ROLE=NBA_RECOMMENDER] [SYS:TASK=ANALYZE_TRANSCRIPT+RECOMMEND_TOP_2_NBAS] [SYS:OUTPUT=JSON] [SYS:CONFIDENCE=0.90-1.00:PERFECT|0.75-0.89:STRONG|0.60-0.74:GOOD] [SYS:PRIORITY=RESOLVE_PROBLEM>MATCH_CONTEXT>MEET_PREREQS]"""

        print(f"\n{'=' * 70}")
        print("NBA CATALOG COMPRESSION")
        print('=' * 70)
        print(f"Original: ~{len(json.dumps(nbas)) // 4} tokens")
        print(f"Compressed: ~{len(compressed_nbas) // 4} tokens")
        print(f"Savings: {(1 - len(compressed_nbas) / len(json.dumps(nbas))) * 100:.1f}%")
        print(f"Compressed NBAs (first 150 chars): {compressed_nbas[:150]}...")

        print('=' * 70 + '\n')
        try:
            for model in self._claude_models:
                if model != "claude-opus-4-1-20250805":
                    continue
                for idx, transcript in enumerate(transcripts[:10]):
                    if idx != 7:
                        continue

                    tc = transcript.get("compressed")
                    to = transcript.get("original")
                    print(f"Running Index: {idx} on {model} - {tc}")


                    print(f"\nOriginal length: {len(to)} chars")
                    print(f"Compressed length: {len(tc)} chars")
                    print(f"NBAs: {len(nbas)} NBAs")
                    print(f"Compression ratio: {(1 - len(tc) / len(to)) * 100:.1f}%")

                    start_time = time.time()
                    tc_message = self.client.messages.create(
                        model=model,
                        max_tokens=200,
                        system=clm_system_prompt,
                        messages=[{
                            "role": "user",
                            "content": f"""Analyze the following call transcript:
                            TRANSCRIPT:
                            {tc}
    
                            NBA CATALOG:
                            {compressed_nbas}
                            
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
                    print(f"  INPUT TOKENS: {tc_tokens} tokens, {tc_latency:.2f}s")

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
        except Exception as e:
            print(f"Something went wrong: {e}")
            pass
        self.dump_result(result)

if __name__ == "__main__":
    benchmark = RunCLMBenchmark()
    benchmark.run()