import json

import anthropic

SYSTEM_PROMPT = """
You are a Next Best Action recommendation system for customer service agents.
Analyze the call transcript and recommend the top 2 most relevant actions from
the NBA catalog. Consider customer intent, conversation context, and action
prerequisites. Return recommendations with confidence scores and reasoning
"""

def load_nbas() -> list[dict]:
    with open('./data/raw/nbas_dataset.json', 'r') as f:
        nbas: list = json.load(f)
    return nbas

class RunCLMBenchmark:
    def __int__(self, nbas: list[dict], transcripts: list) -> None:
        self.nbas = nbas
        self.transcripts = transcripts




client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1000,
    messages=[
        {
            "role": "user",
            "content": "What should I search for to find the latest developments in renewable energy?"
        }
    ]
)
print(message.content)

