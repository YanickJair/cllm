import json
from clm_core import CLMEncoder, CLMConfig, ThreadConfig, DataTypes


def load_data() -> dict:
    with open("./data/raw/thread_data.json", "r") as f:
        threads = json.load(f)
    return threads

def normalize_free_form(messages: list[dict[str, str]]) -> str:
    m_ = ""
    for m in messages:
        m_ = m_ + " " + m.get("text", "")
    return m_

if __name__ == "__main__":
    threads = load_data()
    encoder = CLMEncoder(
        cfg=CLMConfig(
            lang="en",
            thread_config=ThreadConfig(
                include_ctx_values=True,
            )
        )
    )

    results = []
    for k, ths in threads.items():
        if k == "threads":
            for t in ths:
                msg = normalize_free_form(t.get("messages", []))
                r = encoder.encode(
                    input_=msg,
                    metadata={
                        "id": t.get("id", ""),
                        "channel": t.get("channel", ""),
                    },
                    data_type=DataTypes.FREE_FORM
                )
                results.append({
                    "structured": r.to_dict(),
                    "compressed": r.compressed,
                    "original": r.original,
                    "c_ratio": r.compression_ratio,
                    "n_tokens": r.n_tokens,
                    "c_tokens": r.c_tokens,
                    "type": "FREE_FORM",
                })
        else:
            for t in ths:
                r = encoder.encode(
                    input_=t.get("text"),
                    metadata={"id": t.get("id", ""), "channel": "EMAIL"},
                    data_type=DataTypes.TRANSCRIPT
                )
                results.append({
                    "structured": r.to_dict(),
                    "compressed": r.compressed,
                    "original": r.original,
                    "c_ratio": r.compression_ratio,
                    "n_tokens": r.n_tokens,
                    "c_tokens": r.c_tokens,
                    "type": "TRANSCRIPT",
                })

    with open("./data/processed/thread_data.json", "w") as f:
        json.dump(results, f)