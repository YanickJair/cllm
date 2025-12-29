<p align="center" style="margin: 0 0 10px">
  <img width="350" height="208" src="https://raw.githubusercontent.com/YanickJair/cllm/main/docs/img/cllm_logo_mythological.svg" alt='CLLM'>
</p>

<h1 align="center" style="font-size: 3rem; margin: -15px 0">
CLLM
</h1>

<h3 align="center">Compressed Language Models via Semantic Token Encoding</h3>

---

<div align="center">
<p>
<a href="https://github.com/YanickJar/cllm/actions">
    <img src="https://github.com/YanickJar/cllm/workflows/Test%20Suite/badge.svg" alt="Test Suite">
</a>
<a href="https://pypi.org/project/cllm/">
    <img src="https://badge.fury.io/py/cllm.svg" alt="Package version">
</a>
<a href="https://github.com/YanickJar/cllm/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
</a>
</p>

<em>Enterprise-grade compression for transcripts, structured data, and system prompts - achieving 60-95% token reduction.</em>
</div>

---

## 🚀 Overview

CLLM is a patent-pending compression technology that dramatically reduces LLM token consumption through semantic encoding. Unlike simple abbreviation or character-level compression, CLLM preserves the **meaning** of your content using structured token vocabularies.

### Three Core Compression Targets

**1. Transcripts** (Contact Centers)
- Customer service conversations
- Support call logs
- Agent-customer interactions
- 95.9% redundancy reduction (Shannon Entropy validated)

**2. Structured Data** (Enterprise)
- NBA (Next Best Action) catalogs
- Product configurations
- Business rule sets
- Metadata and taxonomies

**3. System Prompts** (Enterprise)
- Agent instructions
- Role definitions
- Operational guidelines
- Task specifications

### Benefits

- **60-95% token reduction** across all three targets
- **Equal or better LLM responses** with compressed inputs
- **Up to 73% faster processing** with reduced latency
- **Massive cost savings** for high-volume applications
- **No model training required** - works with existing LLMs

### The Problem

In high-volume LLM environments, verbose content creates significant challenges:
- Thousands of API calls per user per day
- Rapidly escalating token costs at scale
- Infrastructure bottlenecks under heavy load
- Deployment blocked by scalability concerns
- Conversation data consuming excessive context windows

### The Solution

**Transcript Compression:**
```text
Customer: Hi, I need help with my account balance.
Agent: I'd be happy to help. Can I have your account number?
Customer: It's 12345678.
Agent: Your current balance is $1,450.32.
```
↓
```text
[CTX:CUSTOMER_SERVICE][TOPIC:ACCOUNT_BALANCE][DATA:ACC=12345678,BAL=1450.32]
```

**System Prompt Compression:**
```text
You are a customer service quality analyst. Analyze transcripts for compliance 
violations and sentiment issues in agent responses.
```
↓
```text
[REQ:ANALYZE][TARGET:TRANSCRIPT:DOMAIN=SERVICE][EXTRACT:COMPLIANCE,SENTIMENT:SOURCE=AGENT]
```

**Result**: 85-92% token reduction, identical semantic meaning, faster processing.

---

## ✨ Key Features

- **Three Compression Targets**: Transcripts, Structured Data, System Prompts
- **Contact Center Focused**: Built for high-volume customer service operations
- **Semantic Compression**: Preserves meaning, not just characters
- **Hierarchical Token Vocabulary**: REQ, TARGET, EXTRACT, CTX, OUT, REF
- **Multilingual Support**: English, Portuguese, Spanish, French
- **High Accuracy**: 91.5% validation rate on 5,000+ dataset
- **Zero Training**: Works with GPT-4, Claude, and other modern LLMs out-of-the-box
- **Production Ready**: Battle-tested on real contact center transcripts and enterprise catalogs
---

## 📦 Installation

Install CLLM using pip:

```bash
pip install clm-core
```

### Required: Install spaCy Language Model

CLLM uses spaCy for natural language processing. Install the appropriate language model:

```bash
# English
python -m spacy download en_core_web_sm

# Portuguese
python -m spacy download pt_core_news_sm

# Spanish
python -m spacy download es_core_news_sm

# French
python -m spacy download fr_core_news_sm
```
---

## 🏗️ Architecture

### Semantic Token Categories

| Token | Purpose | Example |
|-------|---------|---------|
| `REQ` | Actions/operations | `[REQ:ANALYZE]`, `[REQ:EXTRACT]` |
| `TARGET` | Objects/data sources | `[TARGET:TRANSCRIPT]`, `[TARGET:DOCUMENT]` |
| `EXTRACT` | Fields to extract | `[EXTRACT:SENTIMENT,INTENT]` |
| `CTX` | Contextual information | `[CTX:CUSTOMER_SERVICE]` |
| `OUT` | Output formats | `[OUT:JSON]`, `[OUT:TABLE]` |
| `REF` | References/IDs | `[REF:CASE=12345]` |

### Compression Strategy

1. **Intent Detection**: Identifies the primary action (analyze, extract, summarize)
2. **Target Extraction**: Determines the data source and domain
3. **Pattern Recognition**: Maps verbose phrases to semantic tokens
4. **Redundancy Removal**: Eliminates 95.9% redundant information (Shannon Entropy validated)
5. **Structure Preservation**: Maintains relationships between concepts

---

## 📊 Performance Metrics

Based on production testing with 5,000+ samples across all three targets:

| Metric | Result |
|--------|--------|
| **Average Compression** | 75-92% |
| **Validation Accuracy** | 91.5% |
| **Test Pass Rate** | 88.2% |
| **Processing Speed Improvement** | Up to 73% |
| **Multilingual Coverage** | 4 languages |

### Compression by Target

| Target | Average Compression | Use Case |
|--------|-------------------|----------|
| **Transcripts** | 85-92% | Customer service calls |
| **Structured Data** | 70-85% | NBA catalogs, configs |
| **System Prompts** | 75-90% | Agent instructions |

### Real-World Example: Contact Center NBA

**Original**: System prompt (2,847 tokens) + NBA catalog (uncompressed)
```
Compressed: 966 tokens (66% reduction)
Latency: 1.88 seconds
Quality: Identical recommendations
Cost per 1000 calls: $2.40 → $0.82
```
---

## 🔧 API Reference

### CLLMConfig

```python
CLLMConfig(
    lang: str = "en",           # Language code: en, pt, es, fr
    ds_config: SDCompressionConfig = SDCompressionConfig(),  # Configuration for Structured Data compression
    sys_prompt_config: SysPromptConfig = SysPromptConfig(), # Configuration for System Prompt compression
)
```

### CLMEncoder (for Transcripts)

```python
encoder = CLMEncoder(cfg=CLLMConfig(...))

result = encoder.encode(
    input_: Any = "transcript",
    metadata: dict = {},
    verbose: bool = True
) -> CLMOutput
```

### CLLMEncoder (for System Prompts)

```python
encoder = CLLMEncoder(cfg=CLLMConfig(...))

result = encoder.encode(
    input_: Any = "system prompt",
    verbose: bool = False,
) -> CLMOutput
```

### StructuredDataEncoder (for Structured Data)

```python
encoder = CLLMEncoder(cfg=CLLMConfig(...))

result = encoder.encode(
    input_: Any = "system prompt",
    verbose: bool = False,
) -> CLMOutput
```

### Result Objects

```python
# All result types include:
result.compressed               # Compressed text string
result.original                 # Original token count
result.component                # Transcript, Structured Data, System Prompt
result.compression_ratio        # Ratio as decimal (0.0-1.0)
result.metadata                 # Optional: encoding details
```

---

## 🎓 Use Cases

### 1. Transcript Compression (Contact Centers)

Compress customer service conversations for analysis and AI processing:

```python
from clm_core import CLMEncoder, CLMConfig

# Billing Issue - Mocking CX Transcript
transcript = "Customer: Hi Raj, I noticed an extra charge on my card for my plan this month. It looks like I was billed twice for the same subscription.\nAgent: I'm sorry to hear that, let’s take a look together. Can I have your account email or billing ID to verify your record?\nCustomer: Sure, it’s melissa.jordan@example.com.\nAgent: Thanks, Melissa. Give me just a moment... alright, I can see two transactions on your file — one processed on the 2nd and another on the 3rd. It seems the system retried payment even after the first one succeeded.\nCustomer: Oh wow, that explains it. So I’m not crazy then.\nAgent: Not at all. It’s a known issue we had earlier this week with duplicate processing. The good news is, you’re eligible for a full refund on the second charge.\nCustomer: Great. How long will it take to show up?\nAgent: Once I file the refund, it usually reflects within 3–5 business days depending on your bank. I’ll also send you a confirmation email with the reference number.\nCustomer: That works. Thank you for sorting it out so quickly.\nAgent: My pleasure. I’ve just submitted the refund request now — your reference number is RFD-908712. You should see that update later today.\nCustomer: Perfect. I appreciate your help, Raj.\nAgent: Anytime! Is there anything else I can check for you today?\nCustomer: No, that’s all. Thanks again!\nAgent: Thank you for calling us, Melissa. Have a great day ahead!"
cfg = CLMConfig(lang="en")
encoder = CLMEncoder(cfg=cfg)
compressed = encoder.encode(input_=transcript, metadata={'call_id': 'CX-0001', 'agent': 'Raj', 'duration': '9m', 'channel': 'voice', 'issue_type': 'Billing Dispute'})
# [CALL:SUPPORT:AGENT=Raj:DURATION=7m:CHANNEL=voice] [CUSTOMER] [CONTACT:EMAIL=MELISSA.JORDAN@EXAMPLE.COM] [ISSUE:BILLING_DISPUTE:SEVERITY=LOW] [ACTION:TROUBLESHOOT:RESULT=COMPLETED] [ACTION:REFUND:REFERENCE=RFD-908712:TIMELINE=TODAY:RESULT=COMPLETED] [RESOLUTION:RESOLVED:TIMELINE=TODAY] [SENTIMENT:NEUTRAL→SATISFIED→GRATEFUL]
```

### 2. Structured Data Compression (Enterprise)

Optimize NBA catalogs, product configs, and business rules:

```python
from clm_core import CLMEncoder, CLMConfig
from clm_core.types import SDCompressionConfig

# Knowledge Base structured data
kb_catalog = [
    {
        "article_id": "KB-001",
        "title": "How to Reset Password",
        "content": "To reset your password, go to the login page and click...",
        "category": "Account",
        "tags": ["password", "security", "account"],
        "views": 1523,
        "last_updated": "2024-10-15",
    }
]
config = CLMConfig(
    ds_config=SDCompressionConfig(
        dataset_name="ARTICLE",
        auto_detect=True,
        required_fields=["article_id", "title"],
        field_importance={"tags": 0.8, "content": 0.9},
        max_field_length=100,  # Longer for articles
    )
)

compressor = CLMEncoder(cfg=config)
compressed = compressor.encode(kb_catalog)
# '[KB_CATALOG:1]{ARTICLE_ID,TITLE,CONTENT,CATEGORY,VIEWS,LAST_UPDATED}\\n [KB-001,HOW_TO_RESET_PASSWORD,TO_RESET_YOUR_PASSWORD,_GO_TO_THE_LOGIN_PAGE_AND_CLICK...,ACCOUNT,1523,2024-10-15]'
```

### 3. System Prompt Compression (Enterprise)

Streamline agent instructions and role definitions:

```python
# Agent Role Definition
compressed = encoder.encode(
    "You are a technical support specialist. Analyze customer issues, "
    "identify root causes, and provide step-by-step solutions."
)
# [ROLE:TECH_SUPPORT][REQ:ANALYZE,DIAGNOSE,SOLVE][OUT:STEPS]

# Quality Analysis Instructions
compressed = encoder.encode(
    "Review the transcript for compliance with data privacy regulations, "
    "professional tone, and correct problem resolution."
)
# [REQ:REVIEW][TARGET:TRANSCRIPT][EXTRACT:COMPLIANCE:TYPE=PRIVACY,TONE,RESOLUTION]
```

---

## 🧪 Testing

Run the test suite:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=cllm --cov-report=html

# Run specific test category
pytest tests/test_encoder.py -v
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/YanickJar/cllm.git
cd cllm

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

---

## 📄 License

CLLM is dual-licensed to give you flexibility:

### 1️⃣ AGPL-3.0 (Open Source)

For open source projects, research, and evaluation, CLLM is available under the [GNU Affero General Public License v3.0](LICENSE-AGPL).

**You can freely use CLLM if you:**
- ✅ Keep your project open source (AGPL-compatible)
- ✅ Share all modifications and derivative works
- ✅ Open source any SaaS/web service that uses CLLM

**Important**: If you offer CLLM functionality over a network (SaaS, API, web service), the AGPL requires you to make your complete application source code available to users.

### 2️⃣ Commercial License

For commercial use without AGPL restrictions, we offer commercial licenses:

**Commercial license includes:**
- ❌ No requirement to open source your application
- ✅ Use in proprietary/closed-source products
- ✅ SaaS and API services without source disclosure
- ✅ Full patent grants for CLLM technology
- ✅ Priority support and consulting
- ✅ Custom integrations and features

**Pricing:**
- 💡 **Startup**: <$1M revenue - Contact for pricing
- 🏢 **Enterprise**: Custom pricing based on scale
- 🤝 **OEM/Integration**: Volume licensing available

📧 **Get a commercial license**: license@cllm.io

### Patent Notice

CLLM includes patent-pending technology:
- **Application Number**: [Pending]
- **Technology**: Semantic Token Encoding for LLM Compression

**Patent Grant**: 
- AGPL-3.0 users receive a royalty-free patent license for AGPL-compliant use
- Commercial licensees receive full patent rights per license agreement

For questions about patents or licensing: legal@cllm.io

---

### Which License Should I Choose?

| Use Case | Recommended License |
|----------|-------------------|
| Open source project | AGPL-3.0 (Free) |
| Research/Academic | AGPL-3.0 (Free) |
| Internal tools (not distributed) | AGPL-3.0 (Free) |
| Closed-source product | Commercial |
| SaaS/API service | Commercial |
| Enterprise deployment | Commercial |

**Not sure?** Contact us at license@cllm.io - we're happy to help!

---

## 🔗 Links

- **Documentation**: [docs.cllm.io](https://docs.cllm.io) (coming soon)
- **PyPI**: [pypi.org/project/cllm](https://pypi.org/project/cllm)
- **Issues**: [GitHub Issues](https://github.com/YanickJar/cllm/issues)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

---

## 💡 Citation

If you use CLLM in your research or production systems, please cite:

```bibtex
@software{cllm2025,
  title = {CLLM: Compressed Language Models via Semantic Token Encoding},
  author = {Jarry, Yanick},
  year = {2025},
  url = {https://github.com/YanickJar/cllm}
}
```

---

## 🙏 Acknowledgments

CLLM was developed to solve real-world scalability challenges in enterprise contact center operations, where high-volume LLM usage creates significant cost and infrastructure barriers.

**Built with**: Python, spaCy, Pydantic

---

<div align="center">
<p>Made with ❤️ for the LLM community</p>
<p>
<a href="https://github.com/YanickJar/cllm">⭐ Star us on GitHub</a> • 
<a href="https://github.com/YanickJar/cllm/issues/new">🐛 Report Bug</a> • 
<a href="https://github.com/YanickJar/cllm/discussions">💬 Discussions</a>
</p>
</div>
