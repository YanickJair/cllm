import json
from clm_core import CLMEncoder, CLMConfig


def load_threads():
    with open("./data/raw/thread_encoder_dataset.json", "r") as f:
        threads = json.load(f)
    return threads

if __name__ == "__main__":
    encoder = CLMEncoder(cfg=CLMConfig(lang="en"))