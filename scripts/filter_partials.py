import json

# Load your results
with open("validation_results_100.json") as f:
    results = json.load(f)

# Filter PARTIAL prompts
partial_prompts = [r for r in results if r["status"] == "PARTIAL"]

with open("validation_results_900_partials.json", "w") as f:
    json.dump(partial_prompts, f)
print(f"Total PARTIAL: {len(partial_prompts)}\n")
