import json

from clm_core import CLMEncoder, SysPromptConfig
from clm_core import CLMConfig

def load_prompts() -> list[dict[str, str]]:
    data: list[dict[str, str]] = []
    with open("./data/raw/system_prompts.json", "r") as f:
        data = json.load(f)
    return data

def single_prompt():
    nl_spec = """
    You are a Betting Analysis agent. Your task is to analyze soccer matches by 
    evaluating each team's performance throughout the season and provide accurate 
    betting odds.
    
    ANALYSIS CRITERIA:
    - Review recent match results (last 10 games)
    - Analyze home vs. away performance
    - Consider head-to-head history
    - Factor in injuries and suspensions
    - Evaluate current league position
    - Assess offensive and defensive statistics
    
    EXAMPLE:
    Analyze Chelsea FC's season performance by reviewing statistics from each game. 
    Based on win rate, goals scored/conceded, clean sheets, and recent form, 
    calculate the probability of win, draw, or loss for their next match.
    
    OUTPUT FORMAT:
    Return your analysis as a dictionary object with odds as decimal probabilities:
    {
        "win": 0.45,
        "draw": 0.30,
        "lose": 0.25
    }
    
    Note: Odds must sum to 1.0. Consider all factors before providing final odds.
    """
    cfg = CLMConfig(
        lang="en",
        sys_prompt_config=SysPromptConfig(
            infer_types=True,
            add_attrs=True,
        )
    )
    encoder = CLMEncoder(cfg=cfg)
    compressed = encoder.encode(nl_spec, verbose=False)
    print(compressed.compressed, compressed.compression_ratio)

def main(prompts):
    cfg = CLMConfig(
        lang="en",
    )
    encoder = CLMEncoder(cfg=cfg)
    results = []

    for prompt in prompts:
        compressed = encoder.encode(prompt.get("prompt"), verbose=False)  # type: ignore
        results.append(compressed.model_dump())
        break

    with open("sys_prompt_compression-v2.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    # main(load_prompts())
    single_prompt()
