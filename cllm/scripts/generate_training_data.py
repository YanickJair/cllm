"""
CLLM Training Data Generator
Generates paired examples of (CLLM compressed + data) → (expected output)
"""

import json
import random
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from src.core.encoder import CLLMEncoder


class TrainingDataGenerator:
    """Generates training data for CLLM Model Core"""

    def __init__(self):
        self.encoder = CLLMEncoder("en_core_web_sm")
        self.examples = []

    def generate_instruction_response_pairs(
        self, num_samples: int = 10000
    ) -> list[dict]:
        """
        Generate training pairs showing how to interpret CLLM tokens

        Format:
        {
            "compressed_instruction": "[REQ:ANALYZE] [TARGET:CODE]",
            "natural_instruction": "Analyze this code",
            "data": "def foo(): return 42",
            "expected_output": "This function returns 42..."
        }
        """

        print(f"Generating {num_samples} training examples...")

        training_data = []

        # Load your existing validation data
        with open("validation_results_5K.json") as f:
            validation_data = json.load(f)

        # Use first 1000 as base
        base_examples = validation_data[:1000]

        # Generate variations
        for i in range(num_samples):
            base = random.choice(base_examples)

            # Get compressed version
            compressed = base.get("compressed", "")
            if not compressed:
                continue

            # Create training example
            example = {
                "id": f"train_{i:05d}",
                "compressed_instruction": compressed,
                "natural_instruction": base["prompt"],
                "data": self._generate_synthetic_data(compressed),
                "expected_behavior": self._describe_expected_behavior(compressed),
            }

            training_data.append(example)

            if (i + 1) % 1000 == 0:
                print(f"  Generated {i + 1}/{num_samples}...")

        return training_data

    def _generate_synthetic_data(self, compressed: str) -> str:
        """Generate appropriate data based on compressed instruction"""

        if "TARGET:CODE" in compressed:
            return self._generate_code_sample()
        elif "TARGET:TRANSCRIPT" in compressed:
            return self._generate_transcript_sample()
        elif "TARGET:EMAIL" in compressed:
            return self._generate_email_sample()
        elif "TARGET:DATA" in compressed:
            return self._generate_data_sample()
        else:
            return self._generate_generic_text()

    def _generate_code_sample(self) -> str:
        samples = [
            "def calculate_sum(numbers):\n    return sum(numbers)",
            "class User:\n    def __init__(self, name):\n        self.name = name",
            "function processData(data) {\n    return data.filter(x => x > 0);\n}",
            "SELECT * FROM users WHERE age > 18 ORDER BY created_at DESC;",
        ]
        return random.choice(samples)

    def _generate_transcript_sample(self) -> str:
        samples = [
            "Customer: I'm having trouble logging in.\nAgent: I can help with that. What error are you seeing?",
            "User: The app keeps crashing when I click submit.\nSupport: Let me check the logs...",
            "Client: Need to upgrade my plan.\nRep: Certainly! Which features are you interested in?",
        ]
        return random.choice(samples)

    def _generate_email_sample(self) -> str:
        samples = [
            "Subject: Project Update\n\nHi team, here's our progress this week...",
            "Subject: Meeting Request\n\nCould we schedule time to discuss the proposal?",
            "Subject: Issue Report\n\nI noticed a bug in the latest release...",
        ]
        return random.choice(samples)

    def _generate_data_sample(self) -> str:
        samples = [
            "Name,Age,City\nAlice,25,NYC\nBob,30,LA\nCarol,28,SF",
            '{"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}',
            "Q1: $100K, Q2: $150K, Q3: $200K, Q4: $175K",
        ]
        return random.choice(samples)

    def _generate_generic_text(self) -> str:
        samples = [
            "The quick brown fox jumps over the lazy dog. This is a test sentence.",
            "Machine learning is transforming industries. AI adoption continues to grow.",
            "Climate change requires urgent action. Renewable energy is key.",
        ]
        return random.choice(samples)

    def _describe_expected_behavior(self, compressed: str) -> str:
        """Describe what the model should do with this compressed instruction"""

        behaviors = []

        if "REQ:ANALYZE" in compressed:
            behaviors.append("Perform thorough analysis")
        if "REQ:EXTRACT" in compressed:
            behaviors.append("Extract specified information")
        if "REQ:GENERATE" in compressed:
            behaviors.append("Generate requested content")
        if "REQ:SUMMARIZE" in compressed:
            behaviors.append("Create concise summary")

        if "EXTRACT:" in compressed:
            fields = compressed.split("EXTRACT:")[1].split("]")[0]
            behaviors.append(f"Focus on extracting: {fields}")

        if "OUT:" in compressed:
            format_type = compressed.split("OUT:")[1].split("]")[0]
            behaviors.append(f"Format output as: {format_type}")

        return " | ".join(behaviors) if behaviors else "Process as instructed"

    def create_instruction_tuning_dataset(
        self, output_file: str = "cllm_training_data.jsonl"
    ):
        """
        Create dataset in instruction-tuning format

        Format for fine-tuning (e.g., LLaMA, Mistral):
        {
            "instruction": "[REQ:ANALYZE] [TARGET:CODE]",
            "input": "def foo(): return 42",
            "output": "This function named 'foo' returns the integer 42..."
        }
        """

        print("\n" + "=" * 80)
        print("CREATING INSTRUCTION-TUNING DATASET")
        print("=" * 80 + "\n")

        # Generate base training data
        training_data = self.generate_instruction_response_pairs(num_samples=10000)

        # Convert to instruction-tuning format
        instruction_dataset = []

        for example in training_data:
            # Create instruction-following example
            entry = {
                "instruction": example["compressed_instruction"],
                "input": example["data"],
                "output": self._generate_appropriate_response(
                    example["compressed_instruction"], example["data"]
                ),
                "natural_equivalent": example["natural_instruction"],
            }

            instruction_dataset.append(entry)

        # Save as JSONL
        with open(output_file, "w") as f:
            for entry in instruction_dataset:
                f.write(json.dumps(entry) + "\n")

        print(f"✅ Created {len(instruction_dataset)} training examples")
        print(f"💾 Saved to {output_file}")

        # Show statistics
        self._print_dataset_stats(instruction_dataset)

        return instruction_dataset

    def _generate_appropriate_response(self, compressed: str, data: str) -> str:
        """Generate what the model should output for this instruction+data pair"""

        # This is a simplified version - in practice, you'd want to use an LLM
        # to generate high-quality responses based on the CLLM instruction

        if "REQ:ANALYZE" in compressed:
            if "TARGET:CODE" in compressed:
                return f"Analysis of the code:\n{data}\n\nThis code defines functionality that..."
            else:
                return f"Analysis:\n{data}\n\nKey observations: ..."

        elif "REQ:EXTRACT" in compressed:
            return "Extracted information:\n- Field 1: ...\n- Field 2: ..."

        elif "REQ:SUMMARIZE" in compressed:
            return f"Summary: {data[:100]}... Key points include..."

        elif "REQ:GENERATE" in compressed:
            return "Generated content based on input..."

        else:
            return f"Processed according to instruction: {compressed}"

    def _print_dataset_stats(self, dataset: list[dict]):
        """Print statistics about the generated dataset"""

        print("\n" + "-" * 80)
        print("DATASET STATISTICS")
        print("-" * 80)

        # Count by REQ type
        req_types = {}
        for entry in dataset:
            compressed = entry["instruction"]
            for req in ["ANALYZE", "EXTRACT", "GENERATE", "SUMMARIZE", "TRANSFORM"]:
                if f"REQ:{req}" in compressed:
                    req_types[req] = req_types.get(req, 0) + 1

        print("\nInstruction Types:")
        for req, count in sorted(req_types.items(), key=lambda x: x[1], reverse=True):
            pct = (count / len(dataset)) * 100
            print(f"  REQ:{req:<12} {count:5d} ({pct:5.1f}%)")

        # Count by TARGET type
        target_types = {}
        for entry in dataset:
            compressed = entry["instruction"]
            for target in ["CODE", "TRANSCRIPT", "EMAIL", "DATA", "DOCUMENT"]:
                if f"TARGET:{target}" in compressed:
                    target_types[target] = target_types.get(target, 0) + 1

        print("\nTarget Types:")
        for target, count in sorted(
            target_types.items(), key=lambda x: x[1], reverse=True
        ):
            pct = (count / len(dataset)) * 100
            print(f"  TARGET:{target:<12} {count:5d} ({pct:5.1f}%)")

        # Token statistics
        avg_instruction_length = sum(len(e["instruction"]) for e in dataset) / len(
            dataset
        )
        avg_input_length = sum(len(e["input"]) for e in dataset) / len(dataset)
        avg_output_length = sum(len(e["output"]) for e in dataset) / len(dataset)

        print("\nAverage Lengths:")
        print(f"  Instruction: {avg_instruction_length:.1f} chars")
        print(f"  Input:       {avg_input_length:.1f} chars")
        print(f"  Output:      {avg_output_length:.1f} chars")
        print()

    def create_token_vocabulary(self, output_file: str = "cllm_token_vocab.json"):
        """Create vocabulary of all CLLM tokens for embedding layer"""

        print("\n" + "=" * 80)
        print("CREATING CLLM TOKEN VOCABULARY")
        print("=" * 80 + "\n")

        vocab = {
            "special_tokens": ["[PAD]", "[UNK]", "[CLS]", "[SEP]"],
            "req_tokens": [],
            "target_tokens": [],
            "extract_tokens": [],
            "ctx_tokens": [],
            "out_tokens": [],
        }

        # Load vocabulary from your encoder
        from src.utils.vocabulary import Vocabulary

        v = Vocabulary()

        # Add all token types
        vocab["req_tokens"] = list(v.REQ_TOKENS.keys())
        vocab["target_tokens"] = list(v.TARGET_TOKENS.keys())
        vocab["extract_tokens"] = v.EXTRACT_FIELDS

        # Calculate total
        total_tokens = (
            len(vocab["special_tokens"])
            + len(vocab["req_tokens"])
            + len(vocab["target_tokens"])
            + len(vocab["extract_tokens"])
        )

        vocab["vocab_size"] = total_tokens

        # Save
        with open(output_file, "w") as f:
            json.dump(vocab, f, indent=2)

        print(f"✅ Created vocabulary with {total_tokens} tokens")
        print(f"💾 Saved to {output_file}\n")

        return vocab


def main():
    """Generate all training artifacts"""

    print("\n" + "=" * 80)
    print("🚀 CLLM MODEL CORE - TRAINING DATA GENERATION")
    print("=" * 80 + "\n")

    generator = TrainingDataGenerator()

    # 1. Create instruction-tuning dataset
    print("Step 1: Generating instruction-tuning dataset...")
    generator.create_instruction_tuning_dataset()

    # 2. Create token vocabulary
    print("\nStep 2: Creating token vocabulary...")
    generator.create_token_vocabulary()

    print("\n" + "=" * 80)
    print("✅ TRAINING DATA GENERATION COMPLETE")
    print("=" * 80)
    print("\nGenerated files:")
    print("  1. cllm_training_data.jsonl    - Training dataset")
    print("  2. cllm_token_vocab.json       - Token vocabulary")
    print("\nNext steps:")
    print("  1. Review generated data quality")
    print("  2. Optionally: Use GPT-4 to generate better responses")
    print("  3. Proceed to Phase 2: Model Architecture")
    print()


if __name__ == "__main__":
    main()
