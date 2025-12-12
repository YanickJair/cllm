import json

from components.sys_prompt.analyzers.output_format import SysPromptOutputFormat


def demo():
    """Demonstrate the output format compression system"""

    compressor = SysPromptOutputFormat()

    print("=" * 80)
    print("CLLM OUTPUT FORMAT COMPRESSOR - DEMONSTRATION")
    print("=" * 80)

    # Example 1: Natural Language Output Spec (from diagram)
    print("\n1. NATURAL LANGUAGE OUTPUT SPECIFICATION")
    print("-" * 80)

    nl_spec = """Your response must be a list of dictionaries, where each dictionary represents an insight.
Every dictionary should contain the following keys:
• "insight" → a short description of the observation
• "evidence" → the exact quote or behavior from the transcript supporting it
• "impact" → a natural-language explanation of why it matters

Do not use JSON, code blocks, or headings in the output.
Just return the list of dictionaries directly as plain text."""

    print(f"Input:\n{nl_spec}\n")

    compressed, schema = compressor.compress_with_schema(nl_spec, return_schema=True)

    print(f"Extracted Schema:")
    print(f"  Format: {schema.format_type}")
    print(f"  Fields: {[f.name for f in schema.fields]}")
    print(f"  Attributes: {schema.attributes}")
    print(f"\nCompressed: {compressed}")

    # Example 2: Structured JSON Schema (from diagram)
    print("\n\n2. STRUCTURED JSON SCHEMA")
    print("-" * 80)

    structured_spec = {
        "top_themes": [
            {
                "theme": "name",
                "frequency": 0,
                "sentiment": "positive|neutral|negative"
            }
        ],
        "opportunities": ["list_of_suggestions"],
        "critical_issues": ["list"]
    }

    print(f"Input:\n{json.dumps(structured_spec, indent=2)}\n")

    compressed, schema = compressor.compress_with_schema(structured_spec, return_schema=True)

    print(f"Extracted Schema:")
    print(f"  Format: {schema.format_type}")
    print(f"  Top-level Keys: {list(structured_spec.keys())}")
    print(f"  Attributes: {schema.attributes}")
    print(f"\nCompressed: {compressed}")

    # Example 3: Product Feedback System (from diagram)
    print("\n\n3. PRODUCT FEEDBACK AGGREGATION & THEME DETECTION")
    print("-" * 80)

    feedback_system = {
        "task": "Analyze customer feedback and extract top themes and opportunities",
        "analysis_criteria": [
            "Repeated topics",
            "Sentiment polarity by theme",
            "Urgency/severity",
            "Product feature mapping",
            "Improvement or feature requests"
        ],
        "output_format": {
            "top_themes": [
                {"theme": "name", "frequency": 0, "sentiment": "positive|neutral|negative"}
            ],
            "opportunities": ["list_of_suggestions"],
            "critical_issues": ["list"]
        }
    }

    print(f"System Description:")
    print(f"  Task: {feedback_system['task']}")
    print(f"  Criteria: {len(feedback_system['analysis_criteria'])} analysis points")
    print(f"  Output Structure: {list(feedback_system['output_format'].keys())}")

    # Compress just the output format
    compressed = compressor.compress(feedback_system['output_format'])
    print(f"\nCompressed Output Spec: {compressed.build_token()}")

    # Example 4: Various Format Types
    print("\n\n4. DIFFERENT FORMAT TYPES")
    print("-" * 80)

    examples = [
        ("Return as markdown with sections", "MARKDOWN"),
        ("Provide a table with columns: name, age, city", "TABLE"),
        ("Give me a breakdown of the issues", "BREAKDOWN"),
        ("Return XML with tags for each field", "XML"),
        ("Show me the diff between versions", "DIFF"),
    ]

    for spec, expected_format in examples:
        compressed = compressor.compress(spec)
        print(f"  Input: {spec}")
        print(f"  Output: {compressed.build_token()}")
        print()

    print("=" * 80)
    print("✅ All examples compressed successfully!")
    print("=" * 80)

if __name__ == "__main__":
    demo()






