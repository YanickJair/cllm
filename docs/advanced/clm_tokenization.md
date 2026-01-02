# CLM Tokenization

## Overview

CLM uses **three different compression systems**, each optimized for its specific content type. These systems are NOT interchangeable and do NOT share token vocabularies.

**Core principle:** Compress meaning, not characters.

---

## Three Independent Systems

| Encoder | System | Structure | Compression |
|---------|--------|-----------|-------------|
| **System Prompt** | 6-Token Hierarchy | Hierarchical instruction flow | 65-90% |
| **Transcript** | Domain-Specific Tokens | Sequential conversation flow | 85-92% |
| **Structured Data** | Header + Row Format | Tabular schema + data | 70-85% |

### Why Three Different Systems?

Each content type has fundamentally different characteristics:

**System Prompts:**
- Complex, nested instructions
- Hierarchical relationships (action → target → fields → output)
- Requires logical flow preservation
- **Solution:** 6-token hierarchy (REQ, TARGET, EXTRACT, CTX, OUT, REF)

**Transcripts:**
- Sequential conversations
- Temporal flow (greeting → problem → actions → resolution)
- Emotional trajectories
- **Solution:** Domain-specific tokens (CALL, ISSUE, ACTION, SENTIMENT)

**Structured Data:**
- Tabular information
- Schema + records
- Repeated field structure
- **Solution:** Header + row format (not semantic tokens)

---

## Part 1: System Prompt Tokenization

### Purpose

Compress system instructions while preserving:
- What to do (actions/operations)
- What to operate on (data sources)
- What to extract (specific fields)
- How to format output (structure)

### The 6-Token Hierarchy

```
┌─────────────────────────────────────────┐
│  1. REQ - What to do                    │  ← Actions
│     [REQ:ANALYZE,EXTRACT]               │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  2. TARGET - What to operate on         │  ← Data source
│     [TARGET:TRANSCRIPT:DOMAIN=SUPPORT]  │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  3. EXTRACT - What fields to get        │  ← Specific data
│     [EXTRACT:SENTIMENT,URGENCY]         │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  4. CTX - Additional context            │  ← Metadata
│     [CTX:LANGUAGE=EN]                   │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  5. OUT - How to format                 │  ← Output spec
│     [OUT_JSON:{summary,score}]          │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  6. REF - Identifiers                   │  ← References
│     [REF:TICKET=TKT-123]                │
└─────────────────────────────────────────┘
```

### Token Categories

| Token | Purpose | Required | Examples |
|-------|---------|----------|----------|
| **REQ** | Actions/Operations | ✅ Always | `[REQ:ANALYZE]`, `[REQ:EXTRACT,SUMMARIZE]` |
| **TARGET** | Objects/Data Sources | ✅ Always | `[TARGET:TRANSCRIPT]`, `[TARGET:DOCUMENT:TYPE=INVOICE]` |
| **EXTRACT** | Fields to Extract | ⚠️ When extracting | `[EXTRACT:SENTIMENT,COMPLIANCE]` |
| **CTX** | Context/Conditions | ⚠️ When applicable | `[CTX:TONE=PROFESSIONAL]` |
| **OUT** | Output Format | ⚠️ When specified | `[OUT:JSON]`, `[OUT_JSON:{fields}]` |
| **REF** | References/IDs | ⚠️ When present | `[REF:CASE=12345]` |

### Syntax

**Basic structure:**
```
[CATEGORY:VALUE]
[CATEGORY:VALUE:ATTRIBUTE=VALUE]
[CATEGORY:VALUE1,VALUE2,VALUE3]
```

**Examples:**
```
Simple:     [REQ:ANALYZE]
Attribute:  [TARGET:TRANSCRIPT:DOMAIN=SUPPORT]
Multiple:   [REQ:ANALYZE,EXTRACT,SUMMARIZE]
Complex:    [EXTRACT:SENTIMENT,URGENCY:TYPE=LIST,DOMAIN=LEGAL]
```

### REQ Token (Request/Action)

**Common values:**
- `ANALYZE` - Examine and evaluate
- `EXTRACT` - Pull out specific data
- `SUMMARIZE` - Condense information
- `GENERATE` - Create new content
- `CLASSIFY` - Categorize items
- `COMPARE` - Find differences/similarities
- `VALIDATE` - Check correctness
- `DEBUG` - Find and fix issues
- `OPTIMIZE` - Improve performance
- `TRANSFORM` - Convert format
- `EXPLAIN` - Describe concepts
- `RANK` - Order by priority

**Examples:**
```
[REQ:ANALYZE]
[REQ:EXTRACT]
[REQ:ANALYZE,EXTRACT,SUMMARIZE]
```

### TARGET Token (Object/Source)

**Common values:**
- `TRANSCRIPT` - Conversation record
- `DOCUMENT` - General document
- `TICKET` - Support ticket
- `CODE` - Source code
- `DATA` - Dataset
- `EMAIL` - Email message
- `INVOICE` - Invoice document
- `REPORT` - Analysis report

**Attributes:**
- `DOMAIN` - Subject area: `DOMAIN=SUPPORT`, `DOMAIN=FINANCE`
- `TYPE` - Specific subtype: `TYPE=INVOICE`, `TYPE=CONTRACT`
- `TOPIC` - Subject matter: `TOPIC=BILLING`, `TOPIC=TECHNICAL`

**Examples:**
```
[TARGET:TRANSCRIPT]
[TARGET:TRANSCRIPT:DOMAIN=SUPPORT]
[TARGET:DOCUMENT:TYPE=INVOICE:DOMAIN=FINANCE]
```

### EXTRACT Token (Fields to Extract)

**Common values:**

Customer Service:
- `SENTIMENT`, `URGENCY`, `ISSUE`, `RESOLUTION`, `COMPLIANCE`, `DISCLOSURES`

Entities:
- `NAMES`, `DATES`, `AMOUNTS`, `EMAILS`, `PHONES`, `ADDRESSES`

Technical:
- `BUGS`, `ERRORS`, `PERFORMANCE`, `SECURITY`

Business:
- `METRICS`, `DECISIONS`, `ACTIONS`, `NEXT_STEPS`, `OWNERS`

**Attributes:**
- `TYPE` - Data structure: `TYPE=LIST`, `TYPE=TABLE`
- `DOMAIN` - Context: `DOMAIN=LEGAL`, `DOMAIN=FINANCE`
- `SOURCE` - Origin: `SOURCE=AGENT`, `SOURCE=CUSTOMER`

**Examples:**
```
[EXTRACT:SENTIMENT,URGENCY,RESOLUTION]
[EXTRACT:COMPLIANCE:SOURCE=AGENT]
[EXTRACT:NAMES,EMAILS,PHONES:TYPE=LIST]
```

### CTX Token (Context)

**Common patterns:**
```
[CTX:CUSTOMER_SERVICE]
[CTX:LANGUAGE=EN]
[CTX:TONE=PROFESSIONAL]
[CTX:ESCALATE_IF=BASIC_FAILED:TARGET=TIER2]
```

### OUT Token (Output Format)

**Simple format:**
```
[OUT:JSON]
[OUT:MARKDOWN]
[OUT:TABLE]
[OUT:LIST]
```

**Structured JSON:**

Basic:
```
[OUT_JSON:{field1,field2,field3}]
```

With types (infer_types=True):
```
[OUT_JSON:{summary:STR,score:FLOAT,items:[STR]}]
```

Nested:
```
[OUT_JSON:{summary:STR,scores:{accuracy:FLOAT,compliance:FLOAT}}]
```

With enums (add_attrs=True):
```
[OUT_JSON:{score:FLOAT}:ENUMS={"ranges":[{"min":0.0,"max":0.49,"label":"FAIL"}]}]
```

### REF Token (References)

**Examples:**
```
[REF:CASE=12345]
[REF:TICKET=TKT-789]
[REF:KB=KB-001]
[REF:POLICY=POL-2024-05]
```

### Complete System Prompt Example

**Original:**
```
You are a Call QA & Compliance Scoring System for customer service operations.

TASK:
Analyze the transcript and score the agent's compliance across required QA categories.

ANALYSIS CRITERIA:
- Mandatory disclosures and verification steps
- Policy adherence
- Soft-skill behaviors (empathy, clarity, ownership)

OUTPUT FORMAT:
{
    "summary": "short_summary",
    "qa_scores": {
        "verification": 0.0,
        "policy_adherence": 0.0,
        "soft_skills": 0.0,
        "compliance": 0.0
    },
    "violations": ["list_any_detected"]
}
```

**Compressed (Level 1: No types, no attrs):**
```
[REQ:ANALYZE] [TARGET:TRANSCRIPT:DOMAIN=QA] 
[EXTRACT:COMPLIANCE,DISCLOSURES,VERIFICATION,POLICY,SOFT_SKILLS:TYPE=LIST,DOMAIN=LEGAL] 
[OUT_JSON:{summary,qa_scores:{verification,policy_adherence,soft_skills,compliance},violations}]
```
**Compression:** 70.7%

**Compressed (Level 4: Types + attrs):**
```
[REQ:ANALYZE] [TARGET:TRANSCRIPT:DOMAIN=QA] 
[EXTRACT:COMPLIANCE,DISCLOSURES,VERIFICATION,POLICY,SOFT_SKILLS:TYPE=LIST,DOMAIN=LEGAL] 
[OUT_JSON:{summary:STR,qa_scores:{verification:FLOAT,policy_adherence:FLOAT,soft_skills:FLOAT,compliance:FLOAT},violations:[STR]}:ENUMS={"ranges":[{"min":0.0,"max":0.49,"label":"FAIL"},{"min":0.5,"max":0.74,"label":"NEEDS_IMPROVEMENT"},{"min":0.75,"max":0.89,"label":"GOOD"},{"min":0.9,"max":1.0,"label":"EXCELLENT"}]}]
```
**Compression:** 26.6%

---

## Part 2: Transcript Tokenization

### Purpose

Compress customer service conversations while preserving:
- Call metadata (who, when, how long)
- Issue description
- Actions taken
- Resolution status
- Emotional trajectory

### The 7 Domain-Specific Tokens

```
┌─────────────────────────────────────────┐
│  1. CALL - Call metadata                │  ← Setup
│     [CALL:SUPPORT:AGENT=Raj:DURATION=9m]│
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  2. CUSTOMER - Customer info            │  ← Who
│     [CUSTOMER]                          │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  3. CONTACT - Contact details           │  ← How to reach
│     [CONTACT:EMAIL=user@example.com]    │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  4. ISSUE - Problem description         │  ← What's wrong
│     [ISSUE:BILLING_DISPUTE:SEVERITY=LOW]│
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  5. ACTION(S) - What was done          │  ← Troubleshooting
│     [ACTION:REFUND:RESULT=COMPLETED]    │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  6. RESOLUTION - Final outcome          │  ← How it ended
│     [RESOLUTION:RESOLVED:TIMELINE=TODAY]│
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  7. SENTIMENT - Emotional journey       │  ← Feeling
│     [SENTIMENT:NEUTRAL→SATISFIED→GRATEFUL]│
└─────────────────────────────────────────┘
```

### Token Definitions

| Token | Format | Purpose | Example |
|-------|--------|---------|---------|
| **CALL** | `[CALL:TYPE:AGENT=name:DURATION=time:CHANNEL=channel]` | Call metadata | `[CALL:SUPPORT:AGENT=Raj:DURATION=9m:CHANNEL=voice]` |
| **CUSTOMER** | `[CUSTOMER]` or `[CUSTOMER:NAME=name]` | Customer identifier | `[CUSTOMER]` |
| **CONTACT** | `[CONTACT:EMAIL=email]` or `[CONTACT:PHONE=number]` | Contact info | `[CONTACT:EMAIL=melissa.jordan@example.com]` |
| **ISSUE** | `[ISSUE:TYPE:SEVERITY=level]` | Problem description | `[ISSUE:BILLING_DISPUTE:SEVERITY=LOW]` |
| **ACTION** | `[ACTION:TYPE:RESULT=outcome:REFERENCE=ref]` | Action taken | `[ACTION:REFUND:RESULT=COMPLETED:REFERENCE=RFD-908712]` |
| **RESOLUTION** | `[RESOLUTION:STATUS:TIMELINE=when]` | Final outcome | `[RESOLUTION:RESOLVED:TIMELINE=TODAY]` |
| **SENTIMENT** | `[SENTIMENT:START→MIDDLE→END]` | Emotional trajectory | `[SENTIMENT:NEUTRAL→SATISFIED→GRATEFUL]` |

### CALL Token

**Format:** `[CALL:TYPE:AGENT=name:DURATION=time:CHANNEL=channel]`

**Attributes:**
- `TYPE` - Call category: `SUPPORT`, `SALES`, `TECHNICAL`
- `AGENT` - Agent name: `AGENT=Raj`, `AGENT=Sarah`
- `DURATION` - Call length: `DURATION=9m`, `DURATION=15m30s`
- `CHANNEL` - Communication method: `CHANNEL=voice`, `CHANNEL=chat`

**Examples:**
```
[CALL:SUPPORT:AGENT=Raj:DURATION=9m:CHANNEL=voice]
[CALL:SALES:AGENT=Sarah:DURATION=15m:CHANNEL=phone]
[CALL:TECHNICAL:DURATION=20m:CHANNEL=video]
```

### CUSTOMER Token

**Format:** `[CUSTOMER]` or `[CUSTOMER:NAME=name]`

**Purpose:** Identifies the customer (usually anonymous)

**Examples:**
```
[CUSTOMER]
[CUSTOMER:NAME=John_Smith]
```

### CONTACT Token

**Format:** `[CONTACT:TYPE=value]`

**Common types:**
- `EMAIL` - Email address
- `PHONE` - Phone number
- `ACCOUNT` - Account ID

**Examples:**
```
[CONTACT:EMAIL=melissa.jordan@example.com]
[CONTACT:PHONE=555-0123]
[CONTACT:ACCOUNT=ACC-789456]
```

### ISSUE Token

**Format:** `[ISSUE:TYPE:SEVERITY=level]`

**Common issue types:**
- `BILLING_DISPUTE` - Billing problems
- `TECHNICAL_ISSUE` - Technical problems
- `ACCOUNT_ACCESS` - Login/access issues
- `PRODUCT_INQUIRY` - Product questions
- `SERVICE_COMPLAINT` - Service complaints

**Severity levels:**
- `LOW` - Minor issue
- `MEDIUM` - Moderate issue
- `HIGH` - Major issue
- `CRITICAL` - Urgent issue

**Examples:**
```
[ISSUE:BILLING_DISPUTE:SEVERITY=LOW]
[ISSUE:TECHNICAL_ISSUE:SEVERITY=HIGH]
[ISSUE:ACCOUNT_ACCESS:SEVERITY=CRITICAL]
```

### ACTION Token

**Format:** `[ACTION:TYPE:RESULT=outcome:REFERENCE=ref:TIMELINE=when]`

**Common action types:**
- `TROUBLESHOOT` - Diagnostic steps
- `REFUND` - Process refund
- `RESET` - Reset account/password
- `ESCALATE` - Escalate to higher tier
- `VERIFY` - Verify information
- `UPDATE` - Update account/info

**Result values:**
- `COMPLETED` - Action finished successfully
- `PENDING` - Action in progress
- `FAILED` - Action unsuccessful
- `SCHEDULED` - Action scheduled for later

**Attributes:**
- `RESULT` - Outcome: `RESULT=COMPLETED`, `RESULT=PENDING`
- `REFERENCE` - Reference number: `REFERENCE=RFD-908712`
- `TIMELINE` - When completed/expected: `TIMELINE=3-5_DAYS`, `TIMELINE=TODAY`

**Examples:**
```
[ACTION:TROUBLESHOOT:RESULT=COMPLETED]
[ACTION:REFUND:REFERENCE=RFD-908712:TIMELINE=3-5_DAYS:RESULT=COMPLETED]
[ACTION:ESCALATE:TEAM=TIER2:RESULT=PENDING]
[ACTION:VERIFY:RESULT=COMPLETED]
```

**Multiple actions:**
```
[ACTION:VERIFY:RESULT=COMPLETED]
[ACTION:TROUBLESHOOT:RESULT=COMPLETED]
[ACTION:REFUND:REFERENCE=RFD-908712:TIMELINE=3-5_DAYS:RESULT=COMPLETED]
```

### RESOLUTION Token

**Format:** `[RESOLUTION:STATUS:TIMELINE=when]`

**Status values:**
- `RESOLVED` - Issue fixed
- `PARTIAL` - Partially resolved
- `UNRESOLVED` - Issue not fixed
- `ESCALATED` - Sent to higher tier
- `PENDING` - Awaiting resolution

**Timeline values:**
- `TODAY` - Resolved same day
- `3-5_DAYS` - Expected timeframe
- `PENDING` - No specific timeline

**Examples:**
```
[RESOLUTION:RESOLVED:TIMELINE=TODAY]
[RESOLUTION:PARTIAL:TIMELINE=3-5_DAYS]
[RESOLUTION:ESCALATED:TIMELINE=PENDING]
```

### SENTIMENT Token

**Format:** `[SENTIMENT:START→MIDDLE→END]`

**Purpose:** Tracks emotional trajectory through conversation

**Common sentiment values:**
- `FRUSTRATED` - Upset, annoyed
- `ANGRY` - Very upset
- `CONCERNED` - Worried
- `NEUTRAL` - Calm, neutral
- `SATISFIED` - Content, pleased
- `GRATEFUL` - Thankful
- `POSITIVE` - Happy
- `CALM` - Peaceful

**Special notation:** Uses arrows (→) to show progression

**Examples:**
```
[SENTIMENT:FRUSTRATED→NEUTRAL→SATISFIED]
[SENTIMENT:ANGRY→CALM→GRATEFUL]
[SENTIMENT:NEUTRAL→SATISFIED→GRATEFUL]
[SENTIMENT:CONCERNED→NEUTRAL→POSITIVE]
```

### Complete Transcript Example

**Original conversation (9-minute billing dispute call):**
```
Agent Raj: Thank you for calling customer support. My name is Raj. How can I help you today?

Customer: Hi Raj, I have a billing issue. I was charged twice this month for my subscription - once on the 1st and again on the 15th. I should only be charged once.

Agent Raj: I'm sorry to hear about that double charge. That's definitely frustrating. Let me look into your account right away. Can I have your email address to pull up your account?

Customer: Sure, it's melissa.jordan@example.com

Agent Raj: Thank you. I see your account now. You're right - I can see two charges this month. Let me investigate what happened...

[... agent checks system ...]

Agent Raj: I found the issue. There was a system error during our billing cycle update that caused some accounts to be charged twice. I apologize for this inconvenience. I'm going to process a full refund for the duplicate charge right now.

Customer: Oh, thank you! How long will that take?

Agent Raj: The refund will be processed within 3 to 5 business days. You'll receive a confirmation email with reference number RFD-908712. Is there anything else I can help you with today?

Customer: No, that's perfect. Thank you so much for your help!

Agent Raj: You're very welcome! Thank you for being so patient with us. Have a great day!
```

**Compressed:**
```
[CALL:SUPPORT:AGENT=Raj:DURATION=9m:CHANNEL=voice]
[CUSTOMER] [CONTACT:EMAIL=melissa.jordan@example.com]
[ISSUE:BILLING_DISPUTE:SEVERITY=LOW]
[ACTION:TROUBLESHOOT:RESULT=COMPLETED]
[ACTION:REFUND:REFERENCE=RFD-908712:TIMELINE=3-5_DAYS:RESULT=COMPLETED]
[RESOLUTION:RESOLVED:TIMELINE=TODAY]
[SENTIMENT:NEUTRAL→SATISFIED→GRATEFUL]
```

**Original:** ~1,450 tokens  
**Compressed:** ~145 tokens  
**Reduction:** 90%

### Key Differences from System Prompts

| Aspect | System Prompts | Transcripts |
|--------|----------------|-------------|
| **Token Types** | REQ, TARGET, EXTRACT, CTX, OUT, REF | CALL, CUSTOMER, ISSUE, ACTION, RESOLUTION, SENTIMENT |
| **Structure** | Hierarchical (instruction flow) | Sequential (conversation flow) |
| **Purpose** | Instruction compression | Conversation compression |
| **Flow** | Logical (what→how→output) | Temporal (start→problem→actions→end) |
| **Special Features** | Nested JSON with types/enums | Sentiment trajectories with arrows (→) |
| **Multiple Items** | Comma-separated: `REQ:ACTION1,ACTION2` | Repeated tokens: multiple `[ACTION:...]` |

---

## Part 3: Structured Data Format

### Purpose

Compress tabular data (catalogs, products, rules) while preserving:
- Field schema
- Record structure
- Relationships
- Data types

### Format Structure

**NOT token-based** - uses header + row format:

```
[DATASET_NAME:COUNT]{FIELD1,FIELD2,FIELD3,...}
[value1,value2,value3,...]
[value1,value2,value3,...]
```

### Components

**1. Header:**
```
[DATASET_NAME:COUNT]{FIELD_NAMES}
```
- `DATASET_NAME`: Data type (e.g., NBA_CATALOG, PRODUCT, RULE)
- `COUNT`: Number of records
- `{FIELD_NAMES}`: Comma-separated field list

**2. Rows:**
```
[value1,value2,value3,...]
```
- One row per record
- Values in same order as header
- Nested objects: `{KEY:VALUE}`
- Arrays: `[ITEM1,ITEM2]`

### Data Type Handling

| Type | Original | Compressed |
|------|----------|------------|
| String | `"Hello World"` | `HELLO_WORLD` |
| Number | `1299.99` | `1299.99` |
| Boolean | `true` | `TRUE` |
| Array | `["a", "b", "c"]` | `[A,B,C]` |
| Null | `null` | `NULL` |
| Date | `"2024-10-15"` | `2024-10-15` |
| Object | `{"key": "value"}` | `{KEY:VALUE}` |

### Complete Example: NBA Catalog

**Original:**
```json
[
  {
    "nba_id": "NBA-001",
    "action": "Offer Premium Upgrade",
    "description": "Recommend premium tier to qualified customers",
    "conditions": ["tenure > 12 months", "no recent complaints"],
    "priority": "high",
    "channel": "phone",
    "expected_value": 450
  },
  {
    "nba_id": "NBA-002",
    "action": "Cross-sell Credit Card",
    "description": "Offer co-branded credit card to active users",
    "conditions": ["good credit score", "active checking"],
    "priority": "medium",
    "channel": "email",
    "expected_value": 300
  }
]
```

**Compressed:**
```
[NBA_CATALOG:2]{NBA_ID,ACTION,DESCRIPTION,CONDITIONS,PRIORITY,CHANNEL,EXPECTED_VALUE}
[NBA-001,OFFER_PREMIUM_UPGRADE,RECOMMEND_PREMIUM_TIER,[TENURE>12M,NO_COMPLAINTS],HIGH,PHONE,450]
[NBA-002,CROSS_SELL_CREDIT_CARD,OFFER_COBRANDED_CARD,[GOOD_CREDIT,ACTIVE_CHECKING],MEDIUM,EMAIL,300]
```

**Compression:** ~82%

### Nested Structures

**Original:**
```json
{
  "sku": "LAPTOP-001",
  "name": "Professional Laptop",
  "specifications": {
    "processor": "Intel i7",
    "ram": "16GB DDR5",
    "storage": "512GB SSD"
  },
  "features": ["Backlit keyboard", "Fingerprint reader"]
}
```

**Compressed:**
```
[PRODUCT:1]{SKU,NAME,SPECIFICATIONS,FEATURES}
[LAPTOP-001,PROFESSIONAL_LAPTOP,{PROCESSOR:I7,RAM:16GB_DDR5,STORAGE:512GB_SSD},[BACKLIT_KB,FINGERPRINT]]
```

### Key Differences from Token Systems

| Aspect | System Prompt / Transcript | Structured Data |
|--------|----------------------------|-----------------|
| **Format** | Semantic tokens | Header + rows |
| **Categories** | 6 or 7 token types | No token categories |
| **Purpose** | Meaning compression | Schema + data compression |
| **Structure** | Token hierarchy/flow | Tabular (spreadsheet-like) |
| **Nesting** | Via token attributes | Via {}, [] notation |
| **Semantic** | High (preserves meaning) | Medium (preserves structure) |

---

## Common Principles

Despite using different systems, all three encoders share core principles:

### 1. Semantic Preservation

**Goal:** Maintain complete meaning in compressed form

All three systems preserve the essential meaning of the original content, just using different methods:
- System Prompts: Hierarchical semantic tokens
- Transcripts: Sequential domain tokens
- Structured Data: Schema-based compression

### 2. LLM-Native Format

**Goal:** LLMs understand without decompression

All three formats are designed to be understood by modern LLMs (GPT-4, Claude, etc.) without requiring decompression:

```
System Prompt:  [REQ:ANALYZE] [TARGET:TRANSCRIPT] [EXTRACT:SENTIMENT]
Transcript:     [ISSUE:BILLING_DISPUTE] [ACTION:REFUND:RESULT=COMPLETED]
Structured:     [NBA_CATALOG:2]{ID,ACTION} [NBA-001,UPGRADE] [NBA-002,CROSS_SELL]
```

LLMs can process all three formats directly.

### 3. Predictable Structure

**Goal:** Consistent, parseable format

Each system has clear syntax rules:
- System Prompts: `[CATEGORY:VALUE:ATTR=VAL]`
- Transcripts: `[TOKEN:TYPE:ATTR=VAL]`
- Structured Data: `[HEADER]{FIELDS}` + `[values]`

### 4. Compression Without Loss

**Goal:** Dramatic size reduction while preserving information

All three achieve 60-95% token reduction while maintaining semantic completeness.

---

## Best Practices

### 1. Use the Right System for Your Content

```
Instructions/Prompts → System Prompt Encoder
Conversations → Transcript Encoder  
Tabular Data → Structured Data Encoder
```

### 2. Understand System-Specific Features

**System Prompts:**
- Use hierarchical flow (REQ → TARGET → EXTRACT → OUT)
- Leverage OUT_JSON for structured output
- Use CTX for conditions and escalation rules

**Transcripts:**
- Follow conversation flow (CALL → ISSUE → ACTION → RESOLUTION)
- Use multiple ACTION tokens for sequential steps
- Capture sentiment trajectories with arrows (→)

**Structured Data:**
- Define clear field schema in header
- Use nested notation for complex structures
- Maintain consistent field order across rows

### 3. Test Compression Quality

```python
# Verify compression preserves meaning
result = encoder.encode(content)

# Check compression ratio
print(f"Reduction: {result.compression_ratio:.1%}")

# Test LLM understanding
llm_response = llm.complete(
    system=result.compressed,
    user="Test query"
)
# Verify LLM understood the compressed content
```

---

## Troubleshooting

### Issue: Wrong Encoder Used

**Symptom:** Poor compression or unexpected output

**Solution:** Use the correct encoder for your content type
```python
# For instructions:
sys_encoder = CLMEncoder(cfg=CLMConfig(lang="en"))

# For conversations:
transcript_encoder = CLMEncoder(cfg=CLMConfig(lang="en"))

# For tabular data:
sd_encoder = CLMEncoder(cfg=CLMConfig(
    lang="en",
    ds_config=SDCompressionConfig(...)
))
```

### Issue: LLM Doesn't Understand Compressed Format

**Symptom:** LLM response quality degraded

**Cause:** Modern LLMs understand structured tokens

**Solution:**
- Verify syntax is correct for the encoder type
- Ensure tokens are well-formed
- Test with different LLM models

### Issue: Information Loss

**Symptom:** Important details missing from compressed output

**Solution for System Prompts:**
```python
# Use less aggressive compression
config = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(
        infer_types=True,   # Add type information
        add_attrs=True      # Include enums/ranges
    )
)
```

**Solution for Structured Data:**
```python
# Lower importance threshold
config = CLMConfig(
    lang="en",
    ds_config=SDCompressionConfig(
        importance_threshold=0.4,  # Include more fields
        max_field_length=300       # Preserve more content
    )
)
```

---

## Next Steps

- **[System Prompt Encoder](sys_prompt_encoder.md)** - Using the 6-token hierarchy
- **[Structured Data Encoder](sd_encoder.md)** - Using header + row format
- **[CLM Vocabulary](advanced/clm_vocabulary.md)** - Understanding vocabulary mappings
- **[CLM Configuration](advanced/clm_configuration)** - Configuring the encoders

---
