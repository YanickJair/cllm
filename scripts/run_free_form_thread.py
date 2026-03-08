import json
from clm_core import CLMEncoder, CLMConfig, DataTypes, ThreadConfig


def load_threads():
    with open("./data/raw/thread_encoder_dataset.json", "r") as f:
        threads = json.load(f)
    return threads

if __name__ == "__main__":
    cfg=CLMConfig(
        lang="en",
        thread_config=ThreadConfig(
            include_summary=True,
            include_ctx_values=True
        )
    )
    encoder = CLMEncoder(
        cfg=cfg
    )
    threads = load_threads()

    results = []
    for thread in threads:
        metdata = {
            "id": thread.get("thread_id"),
            "channel": thread.get("channel"),
            "author": thread.get("author"),
        }
        message = ""
        for m in thread.get("messages", []):
            message += m.get("text")
        encoded = encoder.encode(
            input_=message,
            metadata=metdata,
            data_type=DataTypes.FREE_FORM
        )

        structured = encoded.to_dict()
        results.append({
            "original": message,
            "structured": structured,
            "compressed": encoded.compressed,
            "summary": encoded.summary(cfg.thread_config.default_summary_template)
        })

    with open("thread_free_form.json", "w") as f:
        json.dump(results, f)
