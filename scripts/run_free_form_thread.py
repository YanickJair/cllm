import json
from clm_core import CLMEncoder, CLMConfig, DataTypes, ThreadConfig


def load_threads():
    with open("./data/raw/thread_encoder_dataset.json", "r") as f:
        threads = json.load(f)
    return threads

if __name__ == "__main__":
    input_ = """Hi support team, I noticed my account was charged twice this month — one on the 2nd and another on the 3rd. Can you please look into this? My account email is melissa.jordan@example.com. Thanks, Melissa --- Hi Melissa, Thanks for reaching out. I can confirm the duplicate charge — it was caused by a payment retry that fired after the first transaction already succeeded. I've initiated a full refund on the second charge. You'll see it within 3–5 business days. Your reference number is RFD-908712. Best, Raj – Support Team▋"""
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
    encoded = encoder.encode(input_=input_, data_type=DataTypes.FREE_FORM, metadata={"channel": "email"})
    print(encoded.n_tokens, encoded.c_tokens, encoded.compressed, encoded.to_dict(), encoded.compression_ratio)

