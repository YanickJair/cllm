# CLM Tokenization

## Overview

CLM Tokenization is the semantic token system that enables CLM's compression. Instead of character-level or word-level compression, CLM uses **hierarchical semantic tokens** that represent the meaning and structure of content.

**Core principle:** Compress meaning, not characters.

**Key characteristics:**
- Structured, predictable format
- Hierarchical organization
- Semantic preservation
- LLM-native understanding (no decompression needed)
- Consistent across all compression types

**Token reduction:** 60-95% depending on content type and configuration

---

## The Six Token Categories

CLM uses six fundamental token types that form a complete semantic representation:

| Token | Purpose | Required | Examples |
|-------|---------|----------|----------|
| **REQ** | Actions/Operations | ✅ Always | `[REQ:ANALYZE]`, `[REQ:EXTRACT,SUMMARIZE]` |
| **TARGET** | Objects/Data Sources | ✅ Always | `[TARGET:TRANSCRIPT]`, `[TARGET:DOCUMENT:TYPE=INVOICE]` |
| **EXTRACT** | Fields to Extract | ⚠️ When extracting | `[EXTRACT:SENTIMENT,COMPLIANCE]` |
| **CTX** | Contextual Information | ⚠️ When available | `[CTX:CUSTOMER_SERVICE]`, `[CTX:TONE=PROFESSIONAL]` |
| **OUT** | Output Formats | ⚠️ When specified | `[OUT:JSON]`, `[OUT_JSON:{field1,field2}]` |
| **REF** | References/IDs | ⚠️ When present | `[REF:CASE=12345]`, `[REF:KB=KB-001]` |

### Token Hierarchy

```
┌─────────────────────────────────────────┐
│  REQ (What to do)                       │  ← Primary action
│  [REQ:ANALYZE,EXTRACT]                  │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  TARGET (What to operate on)            │  ← Data source
│  [TARGET:TRANSCRIPT:DOMAIN=SUPPORT]     │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  EXTRACT (What data to get)             │  ← Specific fields
│  [EXTRACT:SENTIMENT,URGENCY,ACTIONS]    │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  CTX (Additional context)               │  ← Metadata
│  [CTX:LANGUAGE=EN]                      │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  OUT (How to format)                    │  ← Output spec
│  [OUT_JSON:{summary,score,issues}]      │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  REF (Identifiers)                      │  ← References
│  [REF:TICKET=TKT-123]                   │
└─────────────────────────────────────────┘
```

---

## Token Syntax

### Basic Structure

```
[CATEGORY:VALUE]
[CATEGORY:VALUE:ATTRIBUTE=VALUE]
[CATEGORY:VALUE1,VALUE2,VALUE3]
[CATEGORY:VALUE:ATTR1=VAL1,ATTR2=VAL2]
```

### Components

**1. Category** (Required)
- Always uppercase
- One of: REQ, TARGET, EXTRACT, CTX, OUT, REF

**2. Value** (Required)
- Primary semantic content
- Can be single or comma-separated list
- Uppercase with underscores

**3. Attributes** (Optional)
- Key-value pairs after colon
- Provide additional context
- Format: `KEY=VALUE` or `KEY=VALUE1,VALUE2`

### Examples

**Simple token:**
```
[REQ:ANALYZE]
```

**With single attribute:**
```
[TARGET:TRANSCRIPT:DOMAIN=SUPPORT]
```

**With multiple values:**
```
[REQ:ANALYZE,EXTRACT,SUMMARIZE]
```

**With multiple attributes:**
```
[EXTRACT:SENTIMENT,COMPLIANCE:TYPE=LIST,DOMAIN=LEGAL]
```

**Nested structure (JSON output):**
```
[OUT_JSON:{summary:STR,scores:{accuracy:FLOAT,compliance:FLOAT}}]
```

**Complex with enums:**
```
[OUT_JSON:{...}:ENUMS={"ranges":[{"min":0.0,"max":0.49,"label":"FAIL"}]}]
```

---

## REQ Token (Request/Action)

**Purpose:** Specifies what operation(s) to perform

**Format:** `[REQ:ACTION1,ACTION2,...]`

### Common REQ Values

| Token | Meaning | Use Case |
|-------|---------|----------|
| `ANALYZE` | Examine and evaluate | Data analysis, review |
| `EXTRACT` | Pull out specific data | Field extraction |
| `SUMMARIZE` | Condense information | Content summarization |
| `GENERATE` | Create new content | Report generation |
| `CLASSIFY` | Categorize items | Classification tasks |
| `COMPARE` | Find differences/similarities | Comparison analysis |
| `VALIDATE` | Check correctness | Data validation |
| `DEBUG` | Find and fix issues | Troubleshooting |
| `OPTIMIZE` | Improve performance | Optimization |
| `TRANSFORM` | Convert format | Data transformation |
| `EXPLAIN` | Describe concepts | Explanations |
| `RANK` | Order by priority | Prioritization |
| `PREDICT` | Forecast outcomes | Predictions |

### Examples by Encoder

**Transcript Encoder:**
```
[REQ:ANALYZE]              # Analyze conversation
[REQ:EXTRACT]              # Extract specific fields
```

**System Prompt Encoder:**
```
[REQ:ANALYZE,SCORE]        # Analyze and score
[REQ:DIAGNOSE,TROUBLESHOOT] # Technical support
[REQ:EXTRACT]              # Data extraction
```

**Structured Data Encoder:**
```
[REQ:RANK]                 # Rank/sort data
[REQ:PREDICT]              # Predictive analysis
```

### Multiple Actions

Actions can be combined when multiple operations are needed:

```
[REQ:ANALYZE,EXTRACT,SUMMARIZE]
# 1. Analyze the content
# 2. Extract key fields
# 3. Summarize findings
```

---

## TARGET Token (Object/Source)

**Purpose:** Identifies what data source or object to operate on

**Format:** `[TARGET:OBJECT:DOMAIN=VALUE,TYPE=VALUE,...]`

### Common TARGET Values

| Token | Meaning | Use Case |
|-------|---------|----------|
| `TRANSCRIPT` | Conversation record | Customer service calls |
| `DOCUMENT` | General document | Reports, articles |
| `TICKET` | Support ticket | Customer issues |
| `CODE` | Source code | Programming |
| `DATA` | Dataset | Data analysis |
| `EMAIL` | Email message | Communication |
| `CALL` | Phone call | Voice interactions |
| `INVOICE` | Invoice document | Billing |
| `REPORT` | Analysis report | Business reporting |
| `NBA_CATALOG` | Next Best Action catalog | Recommendations |

### Attributes

**DOMAIN** - Subject area or context:
```
[TARGET:TRANSCRIPT:DOMAIN=SUPPORT]      # Customer support
[TARGET:TRANSCRIPT:DOMAIN=SALES]        # Sales call
[TARGET:TRANSCRIPT:DOMAIN=QA]           # Quality assurance
[TARGET:DOCUMENT:DOMAIN=FINANCE]        # Financial document
[TARGET:DOCUMENT:DOMAIN=LEGAL]          # Legal document
```

**TYPE** - Specific subtype:
```
[TARGET:DOCUMENT:TYPE=INVOICE]          # Invoice type
[TARGET:DOCUMENT:TYPE=CONTRACT]         # Contract type
[TARGET:CALL:TYPE=SUPPORT]              # Support call
[TARGET:CALL:TYPE=SALES]                # Sales call
```

**TOPIC** - Subject matter:
```
[TARGET:TRANSCRIPT:TOPIC=BILLING]       # About billing
[TARGET:TRANSCRIPT:TOPIC=TECHNICAL]     # Technical issue
```

### Examples by Encoder

**Transcript Encoder:**
```
[TARGET:TRANSCRIPT]
[TARGET:CALL:CHANNEL=phone]
[TARGET:TRANSCRIPT:DOMAIN=SUPPORT:TOPIC=BILLING]
```

**System Prompt Encoder:**
```
[TARGET:TRANSCRIPT:DOMAIN=QA]
[TARGET:DOCUMENT:TYPE=INVOICE]
[TARGET:NETWORK:DOMAIN=CONNECTIVITY]
```

**Structured Data Encoder:**
```
[TARGET:CATALOG:TYPE=NBA]
[TARGET:PRODUCT:CATEGORY=ELECTRONICS]
[TARGET:RULE:TYPE=VALIDATION]
```

---

## EXTRACT Token (Fields to Extract)

**Purpose:** Specifies which fields or data points to extract

**Format:** `[EXTRACT:FIELD1,FIELD2,...:TYPE=VALUE,DOMAIN=VALUE]`

### Common EXTRACT Fields

**Customer Service:**
```
SENTIMENT           # Emotional tone
URGENCY            # Priority level
ISSUE              # Problem description
RESOLUTION         # How it was resolved
COMPLIANCE         # Compliance markers
DISCLOSURES        # Required disclosures
VERIFICATION       # Verification steps
```

**Entities:**
```
NAMES              # Person names
DATES              # Temporal references
AMOUNTS            # Monetary values
EMAILS             # Email addresses
PHONES             # Phone numbers
ADDRESSES          # Physical addresses
```

**Technical:**
```
BUGS               # Software bugs
ERRORS             # Error messages
PERFORMANCE        # Performance metrics
SECURITY           # Security issues
```

**Business:**
```
METRICS            # KPIs and measurements
DECISIONS          # Decisions made
ACTIONS            # Actions taken
NEXT_STEPS         # Future actions
OWNERS             # Responsible parties
```

### Attributes

**TYPE** - Data structure:
```
[EXTRACT:ISSUES:TYPE=LIST]             # Return as list
[EXTRACT:METRICS:TYPE=TABLE]           # Return as table
[EXTRACT:DATA:TYPE=NESTED]             # Nested structure
```

**DOMAIN** - Context specification:
```
[EXTRACT:COMPLIANCE:DOMAIN=LEGAL]      # Legal compliance
[EXTRACT:METRICS:DOMAIN=FINANCE]       # Financial metrics
```

**SOURCE** - Origin of data:
```
[EXTRACT:SENTIMENT:SOURCE=AGENT]       # From agent
[EXTRACT:SENTIMENT:SOURCE=CUSTOMER]    # From customer
[EXTRACT:SENTIMENT:SOURCE=BOTH]        # From both parties
```

### Examples by Encoder

**Transcript Encoder:**
```
[EXTRACT:SENTIMENT,URGENCY,RESOLUTION]
[EXTRACT:COMPLIANCE:SOURCE=AGENT]
[EXTRACT:NAMES,EMAILS,PHONES:TYPE=LIST]
```

**System Prompt Encoder:**
```
[EXTRACT:COMPLIANCE,DISCLOSURES,VERIFICATION,POLICY:TYPE=LIST,DOMAIN=LEGAL]
[EXTRACT:VENDOR,INV_NUM,AMOUNT,DUE_DATE]
```

**Structured Data Encoder:**
```
# Not typically used in structured data
# (Fields are defined in schema)
```

---

## CTX Token (Context)

**Purpose:** Provides contextual information and metadata

**Format:** `[CTX:CONTEXT_TYPE:ATTRIBUTE=VALUE,...]`

### Common CTX Types

**Call Context:**
```
[CTX:CUSTOMER_SERVICE]                 # Customer service context
[CTX:TECHNICAL_SUPPORT]                # Technical support
[CTX:SALES]                            # Sales context
```

**Language/Tone:**
```
[CTX:LANGUAGE=EN]                      # English language
[CTX:TONE=PROFESSIONAL]                # Professional tone
[CTX:TONE=FRIENDLY,EMPATHETIC]         # Multiple tones
```

**Conditions:**
```
[CTX:ESCALATE_IF=BASIC_FAILED:TARGET=TIER2]
[CTX:CONFIDENCE_THRESHOLD=0.8]
```

### Examples by Encoder

**Transcript Encoder:**
```
[CTX:CUSTOMER_SERVICE]
[CTX:LANGUAGE=EN:TONE=PROFESSIONAL]
```

**System Prompt Encoder:**
```
[CTX:ESCALATE_IF=BASIC_FAILED:TARGET=TIER2]
[CTX:LANGUAGE=NON_TECHNICAL]
```

**Structured Data Encoder:**
```
# Context is typically in header:
[PRODUCT_CATALOG:50]{FIELDS...}
```

---

## OUT Token (Output Format)

**Purpose:** Specifies how to format the output

**Format:** `[OUT:FORMAT]` or `[OUT_FORMAT:STRUCTURE]`

### Simple Format Specification

```
[OUT:JSON]                             # Output as JSON
[OUT:MARKDOWN]                         # Output as Markdown
[OUT:TABLE]                            # Output as table
[OUT:LIST]                             # Output as list
[OUT:CSV]                              # Output as CSV
```

### Structured JSON Output

**Basic structure:**
```
[OUT_JSON:{field1,field2,field3}]
```

**With types (infer_types=True):**
```
[OUT_JSON:{summary:STR,score:FLOAT,items:[STR]}]
```

**Nested structure:**
```
[OUT_JSON:{summary:STR,scores:{accuracy:FLOAT,compliance:FLOAT}}]
```

**With enums (add_attrs=True):**
```
[OUT_JSON:{score:FLOAT}:ENUMS={"ranges":[{"min":0.0,"max":0.49,"label":"FAIL"}]}]
```

### Step-by-Step Output

```
[OUT_STEPS:NUMBERED,TIME_EST,SUCCESS_CRITERIA]
```

### Examples by Encoder

**Transcript Encoder:**
```
# Usually implicit (compressed format)
# Or specified in metadata
```

**System Prompt Encoder:**
```
[OUT_JSON:{summary,qa_scores:{verification,policy,accuracy},violations,recommendations}]

[OUT_JSON:{summary:STR,qa_scores:{verification:FLOAT,policy:FLOAT}}]

[OUT_STEPS:NUMBERED,SIMPLE_LANG,TIME_EST]
```

**Structured Data Encoder:**
```
# Output is the compressed structure itself:
[CATALOG:50]{FIELDS}
[row1_data]
[row2_data]
```

---

## REF Token (References/IDs)

**Purpose:** Captures identifiers and reference numbers

**Format:** `[REF:TYPE=VALUE,TYPE2=VALUE2]`

### Common REF Types

```
CASE                # Case number
TICKET              # Ticket ID
ORDER               # Order number
ACCOUNT             # Account ID
TRANSACTION         # Transaction ID
KB                  # Knowledge base article
REFERENCE           # Generic reference
```

### Examples by Encoder

**Transcript Encoder:**
```
[REF:CASE=12345]
[REF:TICKET=TKT-789]
[ACTION:REFUND:REFERENCE=RFD-908712]
```

**System Prompt Encoder:**
```
[REF:KB=KB-001]
[REF:POLICY=POL-2024-05]
```

**Structured Data Encoder:**
```
# IDs are in the data rows:
[KB-001,TITLE,CONTENT,...]
```

---

## Token Patterns by Encoder Type

### Transcript Encoder Tokens

**Core pattern:**
```
[CALL:TYPE:AGENT=name:DURATION=time:CHANNEL=channel]
[CUSTOMER] [CONTACT:EMAIL=email]
[ISSUE:TYPE:SEVERITY=level]
[ACTION:TYPE:RESULT=outcome]
[RESOLUTION:STATUS:TIMELINE=when]
[SENTIMENT:TRAJECTORY]
```

**Complete example:**
```
[CALL:SUPPORT:AGENT=Raj:DURATION=9m:CHANNEL=voice]
[CUSTOMER] [CONTACT:EMAIL=melissa.jordan@example.com]
[ISSUE:BILLING_DISPUTE:SEVERITY=LOW]
[ACTION:TROUBLESHOOT:RESULT=COMPLETED]
[ACTION:REFUND:REFERENCE=RFD-908712:TIMELINE=3-5_DAYS:RESULT=COMPLETED]
[RESOLUTION:RESOLVED:TIMELINE=TODAY]
[SENTIMENT:NEUTRAL→SATISFIED→GRATEFUL]
```

**Special tokens:**
- `CALL` - Call metadata (agent, duration, channel)
- `CUSTOMER` - Customer information
- `CONTACT` - Contact details
- `ISSUE` - Problem description with severity
- `ACTION` - Actions taken with results
- `RESOLUTION` - Final outcome
- `SENTIMENT` - Emotional trajectory (uses arrow: →)

---

### System Prompt Encoder Tokens

**Core pattern:**
```
[ROLE:TYPE:DOMAIN=domain]
[REQ:ACTION1,ACTION2]
[TARGET:OBJECT:DOMAIN=context]
[EXTRACT:FIELD1,FIELD2:ATTRIBUTES]
[OUT_JSON:{structure}]
[CTX:CONTEXT:CONDITIONS]
```

**Complete example:**
```
[ROLE:QA_SYSTEM:DOMAIN=SERVICE]
[REQ:ANALYZE,SCORE]
[TARGET:TRANSCRIPT]
[EXTRACT:COMPLIANCE,DISCLOSURES,VERIFICATION:TYPE=LIST,DOMAIN=LEGAL]
[OUT_JSON:{summary:STR,qa_scores:{verification:FLOAT,policy:FLOAT,compliance:FLOAT},violations:[STR]}]
```

**Special tokens:**
- `ROLE` - Agent identity (unique to system prompts)
- Complex `OUT_JSON` with types and enums
- `CTX` with escalation rules

---

### Structured Data Encoder Tokens

**Core pattern:**
```
[DATASET_NAME:COUNT]{FIELD1,FIELD2,FIELD3,...}
[value1,value2,value3,...]
[value1,value2,value3,...]
```

**Complete example:**
```
[NBA_CATALOG:2]{NBA_ID,ACTION,DESCRIPTION,CONDITIONS,PRIORITY,CHANNEL}
[NBA-001,OFFER_PREMIUM_UPGRADE,RECOMMEND_PREMIUM_TIER,[TENURE>12M,NO_COMPLAINTS],HIGH,PHONE]
[NBA-002,CROSS_SELL_CREDIT_CARD,OFFER_COBRANDED_CARD,[GOOD_CREDIT,ACTIVE_CHECKING],MEDIUM,EMAIL]
```

**Special features:**
- Header format: `[NAME:COUNT]{FIELDS}`
- Row-based data structure
- Nested structures: `{KEY:VALUE}`
- Arrays: `[ITEM1,ITEM2]`
- Field name compression: `UPPERCASE_WITH_UNDERSCORES`

---

## Advanced Token Patterns

### Conditional Logic

**In CTX tokens:**
```
[CTX:ESCALATE_IF=BASIC_FAILED:TARGET=TIER2]
[CTX:RETRY_IF=ERROR:MAX_ATTEMPTS=3]
```

### Ranges and Thresholds

**In OUT_JSON enums:**
```
:ENUMS={"ranges":[
  {"min":0.0,"max":0.49,"label":"FAIL"},
  {"min":0.5,"max":0.74,"label":"NEEDS_IMPROVEMENT"},
  {"min":0.75,"max":0.89,"label":"GOOD"},
  {"min":0.9,"max":1.0,"label":"EXCELLENT"}
]}
```

### Sentiment Trajectories

**Special notation with arrows:**
```
[SENTIMENT:FRUSTRATED→NEUTRAL→SATISFIED]
[SENTIMENT:ANGRY→CALM→GRATEFUL]
[SENTIMENT:NEUTRAL→POSITIVE]
```

### Action Chains

**Sequential actions:**
```
[ACTION:VERIFY:RESULT=COMPLETED]
[ACTION:TROUBLESHOOT:RESULT=COMPLETED]
[ACTION:ESCALATE:TEAM=TIER2:RESULT=PENDING]
```

### Nested Structures

**JSON output with deep nesting:**
```
[OUT_JSON:{
  summary:STR,
  analysis:{
    scores:{
      technical:FLOAT,
      business:FLOAT
    },
    breakdown:[{
      category:STR,
      score:FLOAT
    }]
  }
}]
```

---

## Token Composition Examples

### Example 1: Simple Analysis

**Original:**
```
"Analyze the customer support transcript"
```

**Tokens:**
```
[REQ:ANALYZE]
[TARGET:TRANSCRIPT:DOMAIN=SUPPORT]
```

**Compression:** ~70%

---

### Example 2: Field Extraction

**Original:**
```
"Extract sentiment, urgency, and next steps from the support ticket"
```

**Tokens:**
```
[REQ:EXTRACT]
[TARGET:TICKET:DOMAIN=SUPPORT]
[EXTRACT:SENTIMENT,URGENCY,NEXT_STEPS]
```

**Compression:** ~75%

---

### Example 3: Complex QA System

**Original:**
```
You are a Call QA & Compliance Scoring System. Analyze the transcript
and score the agent's compliance. Extract compliance violations, policy
adherence, and soft skills. Return as JSON with scores from 0.0 to 1.0
where 0.0-0.49 is Fail, 0.5-0.74 is Needs Improvement, 0.75-0.89 is Good,
and 0.9-1.0 is Excellent.
```

**Tokens:**
```
[ROLE:QA_SYSTEM:DOMAIN=SERVICE]
[REQ:ANALYZE,SCORE]
[TARGET:TRANSCRIPT]
[EXTRACT:COMPLIANCE,POLICY,SOFT_SKILLS:TYPE=LIST,DOMAIN=LEGAL]
[OUT_JSON:{qa_scores:{compliance:FLOAT,policy:FLOAT,soft_skills:FLOAT}}:ENUMS={"ranges":[{"min":0.0,"max":0.49,"label":"FAIL"},{"min":0.5,"max":0.74,"label":"NEEDS_IMPROVEMENT"},{"min":0.75,"max":0.89,"label":"GOOD"},{"min":0.9,"max":1.0,"label":"EXCELLENT"}]}]
```

**Compression:** ~65%

---

### Example 4: Complete Transcript

**Original:**
```
Customer: Hi Raj, I have a billing issue. I was charged twice.
Agent: I'm sorry to hear that. Let me check your account.
[... 15 more exchanges ...]
Agent: I've submitted a refund. Reference RFD-908712.
Customer: Thank you so much!
```

**Tokens:**
```
[CALL:SUPPORT:AGENT=Raj:DURATION=9m:CHANNEL=voice]
[CUSTOMER] [CONTACT:EMAIL=melissa.jordan@example.com]
[ISSUE:BILLING_DISPUTE:SEVERITY=LOW]
[ACTION:TROUBLESHOOT:RESULT=COMPLETED]
[ACTION:REFUND:REFERENCE=RFD-908712:TIMELINE=3-5_DAYS:RESULT=COMPLETED]
[RESOLUTION:RESOLVED:TIMELINE=TODAY]
[SENTIMENT:NEUTRAL→SATISFIED→GRATEFUL]
```

**Compression:** ~90%

---

### Example 5: Structured Data

**Original:**
```json
[
  {
    "nba_id": "NBA-001",
    "action": "Offer Premium Upgrade",
    "description": "Recommend premium tier to qualified customers",
    "conditions": ["tenure > 12 months", "no recent complaints"],
    "priority": "high",
    "channel": "phone"
  }
]
```

**Tokens:**
```
[NBA_CATALOG:1]{NBA_ID,ACTION,DESCRIPTION,CONDITIONS,PRIORITY,CHANNEL}
[NBA-001,OFFER_PREMIUM_UPGRADE,RECOMMEND_PREMIUM_TIER,[TENURE>12M,NO_COMPLAINTS],HIGH,PHONE]
```

**Compression:** ~82%

---

## Token Design Principles

### 1. Semantic Preservation

**Goal:** Maintain complete meaning in compressed form

**Approach:**
- Use semantic tokens, not abbreviations
- Preserve relationships between concepts
- Maintain hierarchical structure

**Example:**
```
Bad:  "Anlz trnscrpt get sent urgncy"
Good: [REQ:ANALYZE] [TARGET:TRANSCRIPT] [EXTRACT:SENTIMENT,URGENCY]
```

### 2. Predictable Structure

**Goal:** Consistent, parseable format

**Approach:**
- Fixed token categories
- Standard syntax
- Clear hierarchy

**Example:**
```
Always: [CATEGORY:VALUE:ATTRIBUTES]
Never:  (Category-Value-Attributes) or {category, value, attributes}
```

### 3. LLM-Native Format

**Goal:** LLMs understand without decompression

**Approach:**
- Readable structure
- Semantic clarity
- Contextual information

**Example:**
LLMs can process:
```
[REQ:ANALYZE] [TARGET:TRANSCRIPT:DOMAIN=SUPPORT] [EXTRACT:SENTIMENT]
```

Without needing to decompress to:
```
"Analyze the customer support transcript and extract sentiment"
```

### 4. Hierarchical Organization

**Goal:** Express complex relationships

**Approach:**
- Primary tokens (REQ, TARGET)
- Secondary tokens (EXTRACT, CTX)
- Tertiary tokens (OUT, REF)

**Example:**
```
[REQ:ANALYZE]                          # What to do
  [TARGET:TRANSCRIPT:DOMAIN=SUPPORT]   # What to analyze
    [EXTRACT:SENTIMENT,URGENCY]        # What to get
      [OUT:JSON]                       # How to return it
```

### 5. Attribute Flexibility

**Goal:** Rich metadata without complexity

**Approach:**
- Optional attributes
- Key-value pairs
- Extensible structure

**Example:**
```
Basic:    [TARGET:TRANSCRIPT]
Enhanced: [TARGET:TRANSCRIPT:DOMAIN=SUPPORT:TOPIC=BILLING:LANGUAGE=EN]
```

---

## Token Validation

### Well-Formed Tokens

**Valid:**
```
[REQ:ANALYZE]
[TARGET:TRANSCRIPT:DOMAIN=SUPPORT]
[EXTRACT:SENTIMENT,URGENCY,ACTIONS]
[OUT_JSON:{summary:STR,score:FLOAT}]
```

**Invalid:**
```
REQ:ANALYZE                           # Missing brackets
[REQ ANALYZE]                         # Missing colon
[REQ:analyze]                         # Lowercase value
[TARGET:TRANSCRIPT DOMAIN=SUPPORT]    # Missing colon before attribute
```

### Token Completeness

**Minimal valid compression:**
```
[REQ:ANALYZE] [TARGET:TRANSCRIPT]
```

**Enhanced compression:**
```
[REQ:ANALYZE] [TARGET:TRANSCRIPT:DOMAIN=SUPPORT] [EXTRACT:SENTIMENT]
```

**Full compression:**
```
[REQ:ANALYZE,EXTRACT] [TARGET:TRANSCRIPT:DOMAIN=SUPPORT:TOPIC=BILLING]
[EXTRACT:SENTIMENT,URGENCY,ACTIONS:TYPE=LIST] [OUT:JSON]
[REF:TICKET=TKT-12345]
```

---

## Best Practices

### 1. Include Minimum Required Tokens

Always include REQ and TARGET:
```
✅ [REQ:ANALYZE] [TARGET:TRANSCRIPT]
❌ [EXTRACT:SENTIMENT]  # Missing REQ and TARGET
```

### 2. Use Specific Values When Available

Be specific with attributes:
```
Better:  [TARGET:TRANSCRIPT:DOMAIN=SUPPORT:TOPIC=BILLING]
Worse:   [TARGET:TRANSCRIPT]
```

### 3. Combine Related Actions

Group related operations:
```
Better:  [REQ:ANALYZE,EXTRACT,SUMMARIZE]
Worse:   [REQ:ANALYZE] [REQ:EXTRACT] [REQ:SUMMARIZE]
```

### 4. Maintain Token Order

Follow the hierarchical order:
```
✅ [REQ:...] [TARGET:...] [EXTRACT:...] [CTX:...] [OUT:...] [REF:...]
❌ [OUT:...] [REQ:...] [TARGET:...]  # Out of order
```

### 5. Use Appropriate Specificity

Match detail level to use case:
```
Simple task:    [REQ:ANALYZE] [TARGET:DATA]
Complex task:   [REQ:ANALYZE,CLASSIFY,RANK] [TARGET:DATA:DOMAIN=FINANCE:TYPE=TRANSACTIONS] [EXTRACT:AMOUNT,DATE,CATEGORY:TYPE=TABLE] [OUT:CSV]
```

---

## Troubleshooting

### Issue: Tokens Too Verbose

**Symptom:** Compressed output longer than expected

**Solution:**
```python
# Check configuration
config = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(
        infer_types=False,  # Remove types to reduce size
        add_attrs=False     # Remove enums to reduce size
    )
)
```

### Issue: Missing Information

**Symptom:** Critical details lost in compression

**Solution:**
```python
# Use conservative compression
config = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(
        infer_types=True,   # Add types for clarity
        add_attrs=True      # Add enums for detail
    )
)
```

### Issue: LLM Doesn't Understand Tokens

**Symptom:** LLM response quality degraded

**Cause:** Modern LLMs (GPT-4, Claude) understand structured tokens natively

**Solution:**
- Verify token syntax is correct
- Ensure tokens are well-formed
- Test with different LLM models

---

## Next Steps

- **[CLM Configuration](clm_configuration.md)** - Configuring the tokenization system
- **[CLM Vocabulary](clm_vocabulary.md)** - Understanding the vocabulary mappings
- **[System Prompt Encoder](../sys_prompt_encoder.md)** - Applying tokens to system prompts
- **[Transcript Encoder](../transcript_encoder.md)** - Applying tokens to transcripts
- **[Structured Data Encoder](../sd_encoder.md)** - Applying tokens to structured data

---
