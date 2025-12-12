"""
CX-Focused CLLM Training Data Generator
Creates realistic customer support scenarios for training CLLM Model Core
"""

import json
import random
from typing import List, Dict
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core import CLMEncoder


class CXTrainingDataGenerator:
    """Generates CX-specific training data for CLLM"""

    def __init__(self):
        self.encoder = CLMEncoder("en_core_web_sm")

        # CX-specific instruction templates
        self.cx_instructions = {
            "sentiment_analysis": {
                "natural": [
                    "Analyze the customer sentiment in this conversation",
                    "Determine if the customer is satisfied, neutral, or frustrated",
                    "Assess the emotional tone of this customer interaction",
                ],
                "compressed": "[REQ:ANALYZE] [TARGET:TRANSCRIPT] [EXTRACT:SENTIMENT]",
            },
            "issue_extraction": {
                "natural": [
                    "Extract the main issue from this support ticket",
                    "Identify the customer's primary problem or concern",
                    "What is the customer trying to resolve?",
                ],
                "compressed": "[REQ:EXTRACT] [TARGET:TRANSCRIPT] [EXTRACT:ISSUE]",
            },
            "urgency_detection": {
                "natural": [
                    "Determine the urgency level of this customer issue",
                    "Is this a high-priority, medium-priority, or low-priority ticket?",
                    "Assess how quickly this issue needs to be addressed",
                ],
                "compressed": "[REQ:ANALYZE] [TARGET:TICKET] [EXTRACT:URGENCY]",
            },
            "routing": {
                "natural": [
                    "Route this ticket to the appropriate department",
                    "Which team should handle this customer issue?",
                    "Determine the best department to resolve this problem",
                ],
                "compressed": "[REQ:CLASSIFY] [TARGET:TICKET] [CTX:INTENT=ROUTING]",
            },
            "response_generation": {
                "natural": [
                    "Generate an appropriate response to this customer inquiry",
                    "Draft a professional reply addressing the customer's concern",
                    "Create a response that resolves the customer's issue",
                ],
                "compressed": "[REQ:GENERATE] [TARGET:RESPONSE] [CTX:TONE=PROFESSIONAL]",
            },
            "quality_check": {
                "natural": [
                    "Review this agent response for quality and compliance",
                    "Check if this response meets quality standards",
                    "Evaluate the appropriateness of this customer service response",
                ],
                "compressed": "[REQ:ANALYZE] [TARGET:RESPONSE] [EXTRACT:QUALITY]",
            },
            "escalation_check": {
                "natural": [
                    "Determine if this issue should be escalated to management",
                    "Does this ticket require supervisor intervention?",
                    "Assess if escalation is needed for this customer issue",
                ],
                "compressed": "[REQ:DETECT] [TARGET:TICKET] [EXTRACT:ESCALATION]",
            },
            "multi_extract": {
                "natural": [
                    "Extract the issue, sentiment, and recommended next steps from this ticket",
                    "Analyze this conversation and identify the problem, customer mood, and resolution path",
                    "Pull out the main issue, customer sentiment, urgency level, and suggested actions",
                ],
                "compressed": "[REQ:EXTRACT] [TARGET:TRANSCRIPT] [EXTRACT:ISSUE+SENTIMENT+URGENCY+NEXT_STEPS]",
            },
        }

        # Realistic customer issues by category
        self.customer_issues = {
            "technical": [
                "I can't log into my account. It keeps saying my password is wrong even though I know it's correct.",
                "The app crashes every time I try to upload a file. This has been happening for 3 days now.",
                "I'm getting an error code 500 when trying to checkout. Can you help?",
                "The website is extremely slow. Pages take forever to load.",
                "My account was working fine yesterday, but now I can't access any of my data.",
                "I keep getting logged out every few minutes. This is very frustrating.",
                "The mobile app won't sync with the web version. I'm losing data.",
                "I purchased the premium plan but the features aren't unlocked in my account.",
            ],
            "billing": [
                "I was charged twice for the same subscription. I need a refund immediately.",
                "Why did my bill increase this month? I didn't make any changes to my plan.",
                "I cancelled my subscription last week but was still charged today.",
                "I don't recognize a charge on my credit card from your company.",
                "My payment failed but I have sufficient funds. What's going on?",
                "I need to update my payment method but the system won't let me.",
                "Can I get a refund? The product doesn't work as advertised.",
                "I was promised a discount code but it's not working at checkout.",
            ],
            "account": [
                "I need to reset my password but I'm not receiving the reset email.",
                "How do I change my email address on file?",
                "I want to delete my account and all my personal data.",
                "Someone gained unauthorized access to my account. Please help!",
                "I can't update my profile information. The save button does nothing.",
                "My account was suspended without explanation. Why?",
                "I need to transfer my account to a different email address.",
                "How do I enable two-factor authentication?",
            ],
            "product": [
                "This product broke after just one week of use. I want a replacement.",
                "The item I received doesn't match the description on your website.",
                "The quality is much worse than I expected based on the reviews.",
                "This product is missing parts. The manual mentions components I didn't receive.",
                "How do I use this feature? The instructions aren't clear.",
                "Is this product compatible with [other product]?",
                "When will you restock this item? It's been out of stock for weeks.",
                "Can I return this if I'm not satisfied? What's your return policy?",
            ],
            "shipping": [
                "My order was supposed to arrive 3 days ago. Where is it?",
                "The tracking number you provided doesn't work.",
                "I received the wrong item. I ordered X but got Y instead.",
                "The package arrived damaged. The box was crushed.",
                "Can I change my shipping address? The order hasn't shipped yet.",
                "I need this urgently. Can you expedite the shipping?",
                "Part of my order is missing. I only received 2 of 3 items.",
                "I was charged for express shipping but it took the standard time.",
            ],
            "complaint": [
                "I've been on hold for 45 minutes. This is unacceptable customer service!",
                "Your agent was rude and unhelpful. I demand to speak with a manager.",
                "This is the third time I'm contacting you about the same issue. Nothing gets resolved!",
                "Your company keeps making mistakes with my orders. This is ridiculous.",
                "I'm extremely disappointed with your service. I'm considering switching to a competitor.",
                "You promised to call me back yesterday but nobody did. Very unprofessional.",
                "I've wasted hours trying to get help from your support team with no resolution.",
                "This has been the worst customer experience I've ever had.",
            ],
        }

        # Agent responses (realistic)
        self.agent_responses = {
            "empathy": [
                "I completely understand your frustration, and I apologize for the inconvenience.",
                "I'm sorry to hear about this experience. Let me help you resolve this right away.",
                "Thank you for bringing this to our attention. I can see why this is concerning.",
                "I appreciate your patience while we work through this issue together.",
            ],
            "investigation": [
                "Let me look into your account and see what's happening.",
                "I'm checking our system now to understand the root cause.",
                "Give me a moment to review your account history.",
                "I can see the issue in our system. Here's what happened...",
            ],
            "resolution": [
                "I've processed a full refund which should appear in 3-5 business days.",
                "I've escalated this to our technical team who will investigate within 24 hours.",
                "I've reset your account settings which should resolve the issue. Please try again.",
                "I've added a credit to your account as an apology for this inconvenience.",
            ],
        }

    def generate_transcript(self, issue_category: str) -> str:
        """Generate realistic customer support transcript"""

        issue = random.choice(self.customer_issues[issue_category])

        # Customer opening
        customer_start = random.choice(
            [
                f"Customer: Hi, I need help. {issue}",
                f"Customer: {issue}",
                f"Customer: Hello, I'm having a problem. {issue}",
                f"Customer: This is urgent! {issue}",
            ]
        )

        # Agent response
        agent_empathy = random.choice(self.agent_responses["empathy"])
        agent_investigation = random.choice(self.agent_responses["investigation"])

        # Customer follow-up (optional)
        customer_followup = random.choice(
            [
                "Customer: Okay, thank you for checking.",
                "Customer: How long will this take to resolve?",
                "Customer: This is really frustrating. I need this fixed ASAP.",
                "",  # Sometimes no follow-up
            ]
        )

        # Agent resolution
        agent_resolution = random.choice(self.agent_responses["resolution"])

        # Build transcript
        transcript = f"""{customer_start}
Agent: {agent_empathy} {agent_investigation}
{customer_followup}
Agent: {agent_resolution}"""

        return transcript.strip()

    def generate_sentiment_example(self) -> Dict:
        """Generate sentiment analysis training example"""

        issue_category = random.choice(list(self.customer_issues.keys()))
        transcript = self.generate_transcript(issue_category)

        # Determine sentiment based on category and content
        if (
            issue_category == "complaint"
            or "frustrated" in transcript.lower()
            or "ridiculous" in transcript.lower()
        ):
            sentiment = "negative"
            sentiment_desc = "frustrated and dissatisfied"
        elif "thank" in transcript.lower() or "appreciate" in transcript.lower():
            sentiment = "positive"
            sentiment_desc = "satisfied and appreciative"
        else:
            sentiment = "neutral"
            sentiment_desc = "neutral, seeking resolution"

        instruction = random.choice(
            self.cx_instructions["sentiment_analysis"]["natural"]
        )
        compressed = self.cx_instructions["sentiment_analysis"]["compressed"]

        output = f"""Sentiment Analysis:
- Overall sentiment: {sentiment.upper()}
- Customer appears: {sentiment_desc}
- Tone indicators: {"frustration, urgency" if sentiment == "negative" else "professional, calm" if sentiment == "neutral" else "satisfaction, gratitude"}
- Recommendation: {"Prioritize resolution, consider escalation" if sentiment == "negative" else "Standard follow-up" if sentiment == "neutral" else "Thank customer for patience"}"""

        return {
            "instruction_type": "sentiment_analysis",
            "instruction": compressed,
            "natural_instruction": instruction,
            "input": transcript,
            "output": output,
            "metadata": {"category": issue_category, "sentiment": sentiment},
        }

    def generate_issue_extraction_example(self) -> Dict:
        """Generate issue extraction training example"""

        issue_category = random.choice(list(self.customer_issues.keys()))
        transcript = self.generate_transcript(issue_category)

        # Extract the core issue
        issue = (
            [line for line in transcript.split("\n") if line.startswith("Customer:")][0]
            .replace("Customer:", "")
            .strip()
        )

        instruction = random.choice(self.cx_instructions["issue_extraction"]["natural"])
        compressed = self.cx_instructions["issue_extraction"]["compressed"]

        output = f"""Main Issue Extracted:

Primary Problem: {issue[:200]}...

Category: {issue_category.title()}
Type: {"Technical support" if issue_category == "technical" else "Billing inquiry" if issue_category == "billing" else "Account management" if issue_category == "account" else "Product question" if issue_category == "product" else "Shipping inquiry" if issue_category == "shipping" else "Complaint escalation"}

Customer Need: {"Immediate technical resolution" if issue_category == "technical" else "Billing correction/refund" if issue_category == "billing" else "Account access/security" if issue_category == "account" else "Product support/replacement" if issue_category == "product" else "Order status/delivery" if issue_category == "shipping" else "Escalation to management"}"""

        return {
            "instruction_type": "issue_extraction",
            "instruction": compressed,
            "natural_instruction": instruction,
            "input": transcript,
            "output": output,
            "metadata": {"category": issue_category},
        }

    def generate_routing_example(self) -> Dict:
        """Generate ticket routing training example"""

        issue_category = random.choice(list(self.customer_issues.keys()))
        transcript = self.generate_transcript(issue_category)

        # Determine routing
        routing_map = {
            "technical": ("Technical Support", "Tier 2 - Engineering"),
            "billing": ("Billing Department", "Payment Operations"),
            "account": ("Account Management", "Security Team"),
            "product": ("Product Support", "Product Specialists"),
            "shipping": ("Logistics", "Fulfillment Team"),
            "complaint": ("Customer Relations", "Escalation Team"),
        }

        department, team = routing_map[issue_category]

        instruction = random.choice(self.cx_instructions["routing"]["natural"])
        compressed = self.cx_instructions["routing"]["compressed"]

        output = f"""Routing Decision:

Recommended Department: {department}
Specific Team: {team}

Reasoning:
- Issue category: {issue_category.title()}
- Complexity: {"High" if issue_category in ["technical", "complaint"] else "Medium"}
- Requires: {"Specialized technical knowledge" if issue_category == "technical" else "Billing/payment authority" if issue_category == "billing" else "Account security expertise" if issue_category == "account" else "Product expertise" if issue_category == "product" else "Logistics coordination" if issue_category == "shipping" else "Management intervention"}

Priority: {"URGENT" if issue_category in ["complaint", "technical"] else "HIGH" if issue_category in ["billing", "account"] else "NORMAL"}"""

        return {
            "instruction_type": "routing",
            "instruction": compressed,
            "natural_instruction": instruction,
            "input": transcript,
            "output": output,
            "metadata": {"category": issue_category, "department": department},
        }

    def generate_response_generation_example(self) -> Dict:
        """Generate response generation training example"""

        issue_category = random.choice(list(self.customer_issues.keys()))
        issue = random.choice(self.customer_issues[issue_category])

        # Just the customer message (not full transcript)
        customer_message = f"Customer: {issue}"

        instruction = random.choice(
            self.cx_instructions["response_generation"]["natural"]
        )
        compressed = self.cx_instructions["response_generation"]["compressed"]

        # Generate appropriate response
        responses = {
            "technical": "Thank you for contacting us. I understand you're experiencing technical difficulties. I've reviewed your account and can see the issue. Our technical team is actively working on a fix. In the meantime, please try clearing your browser cache or using an incognito window. I'll also escalate this to our engineering team for permanent resolution within 24 hours. Is there anything else I can help you with?",
            "billing": "I sincerely apologize for the billing issue you've experienced. I've reviewed your account and can confirm the error. I've processed a full refund for the duplicate charge, which should appear in your account within 3-5 business days. I've also added a courtesy credit to your account. We've updated our systems to prevent this from happening again. Thank you for bringing this to our attention.",
            "account": "I understand your concern about account security, and I'm here to help. For your protection, I've temporarily secured your account. I'll send you a password reset link to your registered email address. Please also enable two-factor authentication for additional security. Our security team has been notified and will monitor for any suspicious activity. Is there anything else you need assistance with?",
            "product": "Thank you for reaching out about your product concern. I apologize that the item didn't meet your expectations. I'd be happy to process a replacement or full refund, whichever you prefer. I'm also adding a 20% discount code for your next purchase as an apology for this experience. Please let me know how you'd like to proceed, and I'll take care of it immediately.",
            "shipping": "I apologize for the delay in your shipment. I've tracked your order and can see it's currently in transit. According to our latest update, it should arrive within 2 business days. I've upgraded your shipping to priority at no additional cost and will send you tracking updates every 24 hours until delivery. If it doesn't arrive by then, please contact us immediately for a full refund or replacement.",
            "complaint": "I sincerely apologize for your frustrating experience. This doesn't reflect the level of service we strive to provide. I'm escalating this to my supervisor who will personally reach out to you within 2 hours. In the meantime, I've added a significant credit to your account and prioritized your case. We take all feedback seriously and will use this to improve our service. Thank you for giving us the opportunity to make this right.",
        }

        output = responses[issue_category]

        return {
            "instruction_type": "response_generation",
            "instruction": compressed,
            "natural_instruction": instruction,
            "input": customer_message,
            "output": output,
            "metadata": {"category": issue_category},
        }

    def generate_multi_extract_example(self) -> Dict:
        """Generate complex multi-field extraction example"""

        issue_category = random.choice(list(self.customer_issues.keys()))
        transcript = self.generate_transcript(issue_category)

        # Extract multiple fields
        issue = (
            [line for line in transcript.split("\n") if line.startswith("Customer:")][0]
            .replace("Customer:", "")
            .strip()
        )

        sentiment = (
            "negative" if issue_category in ["complaint", "technical"] else "neutral"
        )
        urgency = (
            "high"
            if issue_category in ["complaint", "technical"]
            else "medium"
            if issue_category in ["billing", "account"]
            else "low"
        )

        instruction = random.choice(self.cx_instructions["multi_extract"]["natural"])
        compressed = self.cx_instructions["multi_extract"]["compressed"]

        output = f"""Comprehensive Analysis:

ISSUE:
{issue[:150]}...

SENTIMENT:
- Level: {sentiment.upper()}
- Indicators: {"Frustration, anger" if sentiment == "negative" else "Professional, calm"}

URGENCY:
- Priority: {urgency.upper()}
- SLA: {"2 hours" if urgency == "high" else "24 hours" if urgency == "medium" else "3 days"}

NEXT STEPS:
1. {"Escalate to senior support immediately" if urgency == "high" else "Route to " + issue_category + " team"}
2. {"Offer immediate resolution or compensation" if sentiment == "negative" else "Provide standard resolution"}
3. {"Follow up within 2 hours" if urgency == "high" else "Follow up within 24 hours"}"""

        return {
            "instruction_type": "multi_extract",
            "instruction": compressed,
            "natural_instruction": instruction,
            "input": transcript,
            "output": output,
            "metadata": {
                "category": issue_category,
                "sentiment": sentiment,
                "urgency": urgency,
            },
        }

    def generate_cx_training_dataset(self, num_samples: int = 10000) -> List[Dict]:
        """Generate complete CX training dataset"""

        print("=" * 80)
        print("🎯 GENERATING CX-FOCUSED TRAINING DATA")
        print("=" * 80 + "\n")

        print(f"Target: {num_samples} training examples\n")

        # Distribution of example types
        distribution = {
            "sentiment_analysis": 0.25,  # 25%
            "issue_extraction": 0.20,  # 20%
            "routing": 0.15,  # 15%
            "response_generation": 0.20,  # 20%
            "multi_extract": 0.20,  # 20%
        }

        dataset = []

        for example_type, percentage in distribution.items():
            count = int(num_samples * percentage)
            print(f"Generating {count} {example_type} examples...")

            for i in range(count):
                if example_type == "sentiment_analysis":
                    example = self.generate_sentiment_example()
                elif example_type == "issue_extraction":
                    example = self.generate_issue_extraction_example()
                elif example_type == "routing":
                    example = self.generate_routing_example()
                elif example_type == "response_generation":
                    example = self.generate_response_generation_example()
                elif example_type == "multi_extract":
                    example = self.generate_multi_extract_example()

                example["id"] = f"cx_{example_type}_{i:05d}"
                dataset.append(example)

            print(f"  ✓ Completed {example_type}")

        # Shuffle dataset
        random.shuffle(dataset)

        print(f"\n✅ Generated {len(dataset)} total examples\n")

        return dataset

    def save_dataset(
        self, dataset: List[Dict], output_file: str = "cx_cllm_training_data.jsonl"
    ):
        """Save dataset in JSONL format"""

        with open(output_file, "w") as f:
            for example in dataset:
                f.write(json.dumps(example) + "\n")

        print(f"💾 Saved to {output_file}")

    def print_statistics(self, dataset: List[Dict]):
        """Print dataset statistics"""

        print("\n" + "=" * 80)
        print("📊 DATASET STATISTICS")
        print("=" * 80 + "\n")

        # Count by instruction type
        type_counts = {}
        for example in dataset:
            inst_type = example["instruction_type"]
            type_counts[inst_type] = type_counts.get(inst_type, 0) + 1

        print("Instruction Type Distribution:")
        for inst_type, count in sorted(
            type_counts.items(), key=lambda x: x[1], reverse=True
        ):
            pct = (count / len(dataset)) * 100
            print(f"  {inst_type:<25} {count:5d} ({pct:5.1f}%)")

        # Count by category
        category_counts = {}
        for example in dataset:
            if "category" in example["metadata"]:
                cat = example["metadata"]["category"]
                category_counts[cat] = category_counts.get(cat, 0) + 1

        print("\nIssue Category Distribution:")
        for category, count in sorted(
            category_counts.items(), key=lambda x: x[1], reverse=True
        ):
            pct = (count / len(dataset)) * 100
            print(f"  {category:<25} {count:5d} ({pct:5.1f}%)")

        # Average lengths
        avg_instruction = sum(len(e["instruction"]) for e in dataset) / len(dataset)
        avg_input = sum(len(e["input"]) for e in dataset) / len(dataset)
        avg_output = sum(len(e["output"]) for e in dataset) / len(dataset)

        print("\nAverage Character Lengths:")
        print(f"  Compressed Instruction:  {avg_instruction:.0f} chars")
        print(f"  Input (transcript):      {avg_input:.0f} chars")
        print(f"  Expected Output:         {avg_output:.0f} chars")

        # Compression stats
        avg_natural = sum(len(e["natural_instruction"]) for e in dataset) / len(dataset)
        compression_ratio = (1 - avg_instruction / avg_natural) * 100

        print("\nInstruction Compression:")
        print(f"  Natural language:        {avg_natural:.0f} chars")
        print(f"  CLLM compressed:         {avg_instruction:.0f} chars")
        print(f"  Compression ratio:       {compression_ratio:.1f}%")

        print()

    def show_examples(self, dataset: List[Dict], num_examples: int = 3):
        """Show sample examples from dataset"""

        print("\n" + "=" * 80)
        print("📋 SAMPLE TRAINING EXAMPLES")
        print("=" * 80 + "\n")

        samples = random.sample(dataset, min(num_examples, len(dataset)))

        for i, example in enumerate(samples, 1):
            print(
                f"Example {i}: {example['instruction_type'].replace('_', ' ').title()}"
            )
            print("-" * 80)
            print(f"Natural Instruction:\n  {example['natural_instruction']}\n")
            print(f"CLLM Compressed:\n  {example['instruction']}\n")
            print(f"Input:\n  {example['input'][:200]}...\n")
            print(f"Expected Output:\n  {example['output'][:200]}...\n")
            print("=" * 80 + "\n")


def main():
    """Generate CX-focused training data"""

    print("\n" + "=" * 80)
    print("🚀 CX-FOCUSED CLLM TRAINING DATA GENERATOR")
    print("=" * 80)
    print("\nBuilding enterprise-grade customer support training data...")
    print("Perfect for demonstrating real-world CX use cases!\n")

    # Initialize generator
    generator = CXTrainingDataGenerator()

    # Generate dataset
    dataset = generator.generate_cx_training_dataset(num_samples=10000)

    # Save dataset
    generator.save_dataset(dataset, "cx_cllm_training_data.jsonl")

    # Print statistics
    generator.print_statistics(dataset)

    # Show examples
    generator.show_examples(dataset, num_examples=3)

    print("=" * 80)
    print("✅ CX TRAINING DATA GENERATION COMPLETE!")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Review sample examples above")
    print("  2. Optionally: Enhance with GPT-4 for better responses")
    print("  3. Proceed to model training: python train_cllm_model.py")
    print("\nThis data is ready for demo to your CX company! 🎯\n")


if __name__ == "__main__":
    main()
