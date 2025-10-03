from cllm.src.core.encoder import CLLMEncoder


def main():
    encoder = CLLMEncoder()

    test_prompts = [
        "Analyze this Python code and identify any potential bugs or security vulnerabilities.",
        "Extract all dates, names, and monetary amounts from this legal document and format as JSON.",
        "Summarize this customer support transcript briefly and identify the main issue.",
        "Generate a professional email declining a job offer while expressing gratitude.",
        "Explain quantum computing to a 10-year-old using simple analogies."
    ]
    
    print("\n" + "="*80)
    print("CLLM ENCODER - DEMO")
    print("="*80)
    
    # Compress each prompt
    for prompt in test_prompts:
        result = encoder.compress(prompt, verbose=True)

if __name__ == "__main__":
    main()
