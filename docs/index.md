<p align="center" style="margin: 0 0 10px">
  <img width="350" height="208" src="https://raw.githubusercontent.com/YanickJair/cllm/main/docs/img/cllm_logo_mythological.svg" alt='CLM'>
</p>

<h1 align="center" style="font-size: 3rem; margin: -15px 0">
CLM
</h1>

<h3 align="center">Compressed Language Models via Semantic Token Encoding</h3>

---

<div align="center">
<p>
<a href="https://github.com/YanickJar/cllm/actions">
    <img src="https://github.com/YanickJar/cllm/workflows/Test%20Suite/badge.svg" alt="Test Suite">
</a>
<a href="https://pypi.org/project/cllm/">
    <img src="https://img.shields.io/pypi/v/cllm.svg" alt="Package version">
</a>
<a href="https://github.com/YanickJar/cllm/blob/main/LICENSE-AGPL">
    <img src="https://img.shields.io/badge/license-AGPL--3.0-blue.svg" alt="License">
</a>
</p>

<em>Semantic compression for transcripts, structured data, and system prompts - achieving 60-95% token reduction.</em>
</div>

---

## Overview

CLM is a patent-pending compression technology that reduces LLM token consumption through semantic encoding. Unlike simple abbreviation or character-level compression, CLM preserves the **meaning** of your content using structured token vocabularies.

### Three Core Compression Targets

1. **Transcripts** - Customer service conversations, support calls, chat interactions
2. **Structured Data** - Product catalogs, knowledge bases, business rules, configurations
3. **System Prompts** - Task instructions, role definitions, operational guidelines

**Key Benefits:**
- 60-95% token reduction
- Equal or better LLM responses
- Up to 73% faster processing
- No model training required

---

## Installation

Install CLM using pip:

```shell
pip install clm-core
```

### Install spaCy Language Model

CLM uses [spaCy](https://spacy.io) for natural language processing tasks such as NER and rule-based information extraction. We support four languages: **English**, **Portuguese**, **French**, and **Spanish**.

Download your language model from [spaCy](https://spacy.io/usage):

```shell
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

## Quick Start

### Import CLM

```python
from clm_core import CLMConfig, CLMEncoder
```

### Create Configuration

```python
config = CLMConfig(lang="en")
```

By choosing English as your language, CLM automatically loads the `en_core_web_sm` spaCy model and uses the internal English [dictionary and vocabulary](advanced/clm_dictionary.md) for compression.

---

## Compression Examples

### 1. System Prompt Compression

Perfect for compressing task instructions, role definitions, and specifications:

```python
encoder = CLMEncoder(cfg=config)

sys_prompt = """
You are a Call QA & Compliance Scoring System for customer service operations.

TASK:
Analyze the transcript and score the agent's compliance across required QA categories.

ANALYSIS CRITERIA:
- Mandatory disclosures and verification steps
- Policy adherence
- Soft-skill behaviors (empathy, clarity, ownership)
- Process accuracy
- Compliance violations or risks
- Customer sentiment trajectory

OUTPUT FORMAT:
{
    "summary": "short_summary",
    "qa_scores": {
        "verification": 0.0,
        "policy_adherence": 0.0,
        "soft_skills": 0.0,
        "accuracy": 0.0,
        "compliance": 0.0
    },
    "violations": ["list_any_detected"],
    "recommendations": ["improvement_suggestions"]
}

SCORING:
0.00–0.49: Fail
0.50–0.74: Needs Improvement
0.75–0.89: Good
0.90–1.00: Excellent
"""

result = encoder.encode(sys_prompt)
print(result.compressed)
```

**Output:**
```text
[REQ:ANALYZE] [TARGET:TRANSCRIPT:DOMAIN=QA] 
[EXTRACT:COMPLIANCE,DISCLOSURES,VERIFICATION,POLICY,SOFT_SKILLS,ACCURACY,SENTIMENT:TYPE=LIST,DOMAIN=LEGAL] 
[OUT_JSON:{summary,qa_scores:{verification,policy_adherence,soft_skills,accuracy,compliance},violations,recommendations}:ENUMS={"ranges": [{"min": 0.0, "max": 0.49, "label": "FAIL"}, {"min": 0.5, "max": 0.74, "label": "NEEDS_IMPROVEMENT"}, {"min": 0.75, "max": 0.89, "label": "GOOD"}, {"min": 0.9, "max": 1.0, "label": "EXCELLENT"}]}]
```

**📊 Compression: 62.7% token reduction**

The compressed result preserves the semantic meaning while dramatically reducing token count through [Hierarchical Token](advanced/clm_tokenization.md) representation.

---

### 2. Structured Data Compression

Compress knowledge bases, product catalogs, and structured datasets:

```python
from clm_core import SDCompressionConfig

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
    lang="en",
    ds_config=SDCompressionConfig(
        auto_detect=True,
        required_fields=["article_id", "title"],
        field_importance={"tags": 0.8, "content": 0.9},
        max_description_length=100,
    )
)

encoder = CLMEncoder(cfg=config)
result = encoder.encode(kb_catalog)
print(result.compressed)
```

**Output:**
```text
{article_id,title,content,category,tags,views}[KB-001,How to Reset Password,To reset your password; go to the login page and click...,Account,password+security+account,1523]
```

**Note:** Commas in text values are escaped with semicolons. Arrays use `+` as separator.

**Key Features:**
- Supports both single objects and arrays of objects
- Configure field importance and thresholds
- Specify required/excluded fields
- Auto-detect important fields based on patterns
- Nested structures preserved with inline formatting

Learn more about [Structured Data Compression](sd_encoder.md).

---

### 3. Transcript Compression

Compress customer service conversations while preserving context and sentiment:

```python
# Billing Issue - Customer Support Transcript
transcript = """Customer: Hi Raj, I noticed an extra charge on my card for my plan this month. It looks like I was billed twice for the same subscription.
Agent: I'm sorry to hear that, let's take a look together. Can I have your account email or billing ID to verify your record?
Customer: Sure, it's melissa.jordan@example.com.
Agent: Thanks, Melissa. Give me just a moment... alright, I can see two transactions on your file — one processed on the 2nd and another on the 3rd. It seems the system retried payment even after the first one succeeded.
Customer: Oh wow, that explains it. So I'm not crazy then.
Agent: Not at all. It's a known issue we had earlier this week with duplicate processing. The good news is, you're eligible for a full refund on the second charge.
Customer: Great. How long will it take to show up?
Agent: Once I file the refund, it usually reflects within 3–5 business days depending on your bank. I'll also send you a confirmation email with the reference number.
Customer: That works. Thank you for sorting it out so quickly.
Agent: My pleasure. I've just submitted the refund request now — your reference number is RFD-908712. You should see that update later today.
Customer: Perfect. I appreciate your help, Raj.
Agent: Anytime! Is there anything else I can check for you today?
Customer: No, that's all. Thanks again!
Agent: Thank you for calling us, Melissa. Have a great day ahead!"""

cfg = CLMConfig(lang="en")
encoder = CLMEncoder(cfg=cfg)

result = encoder.encode(
    input_=transcript,
    metadata={
        'call_id': 'CALL-0001',
        'representative': 'Raj',
        'duration': '9m',
        'channel': 'voice',
        'issue_type': 'Billing Dispute'
    }
)
print(result.compressed)
```

**Output:**
```text
[CALL:SUPPORT:AGENT=Raj:DURATION=9m:CHANNEL=voice] 
[CUSTOMER] [CONTACT:EMAIL=melissa.jordan@example.com] 
[ISSUE:BILLING_DISPUTE:SEVERITY=LOW] 
[ACTION:TROUBLESHOOT:RESULT=COMPLETED] 
[ACTION:REFUND:REFERENCE=RFD-908712:TIMELINE=3-5_DAYS:RESULT=COMPLETED] 
[RESOLUTION:RESOLVED:TIMELINE=TODAY] 
[SENTIMENT:NEUTRAL→SATISFIED→GRATEFUL]
```

**What's Preserved:**
- ✅ Representative's name (key information)
- ✅ Customer contact details (key information)
- ✅ Issue type and severity (important context)
- ✅ Actions taken with attributes (TIMELINE, RESULT, REFERENCE)
- ✅ Resolution outcome
- ✅ Sentiment trajectory throughout conversation

**Typical Compression: 85-92% for customer service transcripts**

Learn more about [Transcript Compression](transcript_encoder.md) and [token hierarchy](advanced/clm_tokenization.md).

---

## Hierarchical Token Vocabulary

CLM uses six semantic token categories:

| Token | Purpose | Example |
|-------|---------|---------|
| `REQ` | Actions/operations | `[REQ:ANALYZE]`, `[REQ:EXTRACT]` |
| `TARGET` | Objects/data sources | `[TARGET:TRANSCRIPT]`, `[TARGET:DOCUMENT]` |
| `EXTRACT` | Fields to extract | `[EXTRACT:SENTIMENT,INTENT]` |
| `CTX` | Contextual information | `[CTX:CUSTOMER_SERVICE]` |
| `OUT` | Output formats | `[OUT:JSON]`, `[OUT:TABLE]` |
| `REF` | References/IDs | `[REF:CASE=12345]` |

This structured approach preserves semantic relationships while achieving massive token reduction.

---

## Performance Metrics

Based on production testing with 5,000+ samples:

| Target Type | Average Compression | Use Case |
|-------------|-------------------|----------|
| **System Prompts** | 75-90% | Task instructions, role definitions |
| **Transcripts** | 85-92% | Customer service calls |
| **Structured Data** | 40-85% | Catalogs, configurations |

**Validation Accuracy:** 91.5%  
**Test Pass Rate:** 88.2%  
**Processing Speed Improvement:** Up to 73%  
**Multilingual Coverage:** 4 languages  

---

## Next Steps

- **[System Prompt Encoding](sys_prompt/index.md)** - Overview of system prompt compression
  - [Task Prompts](sys_prompt/task_prompt.md) - Action-oriented instruction compression
  - [Configuration Prompts](sys_prompt/configuration_prompt.md) - Template-based agent configuration
- **[Structured Data Encoding](sd_encoder.md)** - Configuration options and best practices
- **[Transcript Encoding](transcript_encoder.md)** - Customer service conversation compression
- **[Advanced: CLM Dictionary](advanced/clm_dictionary.md)** - Understanding the vocabulary
- **[Advanced: Tokenization](advanced/clm_tokenization.md)** - Token hierarchy and structure

---

## License

CLM is dual-licensed:

- **AGPL-3.0** for open source projects ([details](https://github.com/YanickJar/cllm/blob/main/LICENSE-AGPL))
- **Commercial License** for proprietary use ([contact us](mailto:yanick.jair.ta@gmail.com))

See our [Licensing Guide](https://github.com/YanickJar/cllm/blob/main/LICENSING.md) for details.

---

## Support

- 📖 **Documentation**: [docs.cllm.io](https://docs.cllm.io)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/YanickJar/cllm/discussions)
- 🐛 **Issues**: [GitHub Issues](https://github.com/YanickJar/cllm/issues)
- 📧 **Email**: yanick.jair.ta@gmail.com

---

<div align="center">
<p>Made with ❤️ for the LLM community</p>
</div>