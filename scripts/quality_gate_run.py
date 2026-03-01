import json
from clm_core import CompressionQualityGate, CLMConfig, CLMEncoder

def load_threads():
    with open("./data/raw/transcripts_dataset.json", "r") as f:
        transcripts = json.load(f)
    return transcripts

if __name__ == "__main__":
    cfg = CLMConfig(lang="en", redaction_pattern="\[(.*?)\]")
    encoder = CLMEncoder(cfg=cfg)
    analyzer = CompressionQualityGate()

    transcripts = load_threads()
    results = []
    for transcript in transcripts:
        if transcript["metadata"]["channel"] == "voice":
            compressed = encoder.encode(input_=transcript.get("transcript"), metadata=transcript.get("metadata"))
            report = analyzer.analyze(
                original=compressed.original,
                compressed=compressed.compressed,
                structured=compressed.to_dict(),
                run_perplexity=True,
                verbose=True,
            )
            results.append(report.model_dump())

    with open("./data/raw/report.json", "w") as f:
        json.dump(results, f)

    print("\n" + "=" * 60)
    print(report.summary())

    # Per-field breakdown
    print("\n[Field-by-field Conditional Entropy]")
    print(f"{'Field':<22} {'Token':<22} {'Found':<8} {'Weight':<8} {'Null'}")
    print("-" * 70)
    for fr in report.conditional.field_results:
        status = "NULL" if fr.null_in_source else ("✓" if fr.found_in_compressed else "✗ LOST")
        print(f"{fr.field:<22} {fr.token_key:<22} {status:<8} {fr.weight:<8} {fr.null_in_source}")
