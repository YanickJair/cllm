# CLM Tokenization

## Overview

CLM uses **three different compression systems**, each optimized for its specific content type. These systems are NOT interchangeable and do NOT share token vocabularies.

**Core principle:** Compress meaning, not characters.

### Automatic Intent Detection

CLM features **IntentDetectorV2**, an intelligent system that automatically determines the correct REQ (request/action) token from natural language input. The detector analyzes:
- **Signals** - Vocabulary-based phrase matching
- **Artifacts** - Structural patterns in the text
- **Epistemic grounding** - Context for prediction vs generation
- **SPEC detection** - Domain-specific output types

This means you can write natural language prompts and CLM will automatically compress them into the optimal token format.

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

The REQ token represents the **primary action or operation** to be performed. It is the most critical token in the system prompt hierarchy as it determines the fundamental task type.

#### REQ Categorization Taxonomy

REQ tokens are organized into **six fundamental categories** based on their purpose and what they produce:

##### A. ANALYSIS / EVALUATION
**Purpose:** Interpret, assess, or explain something.
**Produces:** Insight, judgment, reasoning.

**Examples:**
- Code review
- Risk assessment
- Performance evaluation
- Root cause analysis

**Canonical REQs:** `ANALYZE`, `EVALUATE`, `ASSESS`, `DIAGNOSE`

⚠️ **Use sparingly** — this is the most generic bucket.

##### B. GENERATION / CREATION
**Purpose:** Create a new artifact.
**Produces:** Text, data, structure, plans, content.

**Examples:**
- Write a report
- Generate a schema
- Produce odds
- Draft an email

**Canonical REQs:** `GENERATE_REPORT`, `GENERATE_SCHEMA`, `GENERATE_BETTING_ODDS`, `GENERATE_SUMMARY`

ℹ️ **This is where most business prompts land.**

##### C. PREDICTION / FORECASTING
**Purpose:** Estimate future outcomes or probabilities.
**Produces:** Probabilities, forecasts, predictions.

**Examples:**
- Match outcome probabilities
- Sales forecast
- Risk likelihood

**Canonical REQs:** `PREDICT_OUTCOME`, `FORECAST_METRIC`, `ESTIMATE_PROBABILITY`

⚠️ **Often overlaps with GENERATION** — choose the dominant intent.

**For betting:**
- Outcome = odds → GENERATION wins
- Time series forecast → PREDICTION wins

##### D. DECISION / RECOMMENDATION
**Purpose:** Choose or advise among options.
**Produces:** A decision, ranking, or recommendation.

**Examples:**
- Best investment option
- Recommended action
- Prioritized list

**Canonical REQs:** `RECOMMEND_ACTION`, `SELECT_OPTION`, `RANK_ALTERNATIVES`

##### E. EXTRACTION / TRANSFORMATION
**Purpose:** Convert or extract from existing input.
**Produces:** Structured data from unstructured input.

**Examples:**
- Extract entities
- Parse schema
- Normalize text

**Canonical REQs:** `EXTRACT_FIELDS`, `TRANSFORM_SCHEMA`, `NORMALIZE_TEXT`

ℹ️ **This is often machine-facing, not user-facing.**

##### F. VALIDATION / VERIFICATION
**Purpose:** Check correctness, compliance, or consistency.
**Produces:** Pass/fail, issues, validation results.

**Examples:**
- Policy compliance
- Schema validation
- Constraint checking

**Canonical REQs:** `VALIDATE_OUTPUT`, `VERIFY_COMPLIANCE`, `CHECK_CONSISTENCY`

---

#### REQ Token Values & Category Mapping

The following REQ tokens are available in CLM, organized by their category:

**Category A: ANALYSIS / EVALUATION**
- `ANALYZE` - Examine and evaluate content
- `CLASSIFY` - Categorize items (now mapped via ANALYZE)
- `DEBUG` - Find and fix issues

**Category B: GENERATION / CREATION**
- `GENERATE` - Create new content (reports, summaries, structured data)
- `SUMMARIZE` - Condense information (now mapped via GENERATE)

**Category C: PREDICTION / FORECASTING**
- `PREDICT` - Make future projections based on uncertainty and real-world grounding

**Category D: DECISION / RECOMMENDATION**
- `RECOMMEND` - Provide recommendations (deprecated, use RANK)
- `RANK` - Order items by priority or preference

**Category E: EXTRACTION / TRANSFORMATION**
- `EXTRACT` - Pull out specific data or entities
- `TRANSFORM` - Convert format or restructure data
- `FORMAT` - Reformat without changing meaning

**Category F: VALIDATION / VERIFICATION**
- `VALIDATE` - Check correctness, compliance, or verification

**Utility / Other:**
- `SEARCH` - Search or find information
- `EXECUTE` - Execute operations or commands

**Examples:**
```
[REQ:ANALYZE]
[REQ:EXTRACT]
[REQ:GENERATE:SPECS:REPORT]
[REQ:VALIDATE]
[REQ:PREDICT:SPECS:FORECAST]
```

### How REQ Tokens are Automatically Detected

CLM uses **IntentDetectorV2** to automatically determine the correct REQ token from natural language input. The detection system analyzes three key dimensions:

#### 1. Signals (Vocabulary-Based Detection)

Signals are detected by matching phrases from the input text against a vocabulary dictionary:

| Signal | Trigger Words | Maps to REQ |
|--------|--------------|-------------|
| **ANALYSIS** | analyze, assess, review, evaluate | `ANALYZE` |
| **EXTRACTION** | extract, pull, get, retrieve | `EXTRACT` |
| **GENERATION** | generate, create, produce, summarize, list | `GENERATE` |
| **PREDICTION** | predict, forecast, calculate, project | `PREDICT` |
| **TRANSFORMATION** | transform, convert, restructure | `TRANSFORM` |
| **FORMATTING** | format, reformat, style | `FORMAT` |
| **VALIDATION** | validate, verify, check, ensure | `VALIDATE` |
| **RANKING** | rank, order, prioritize, best | `RANK` |
| **DEBUGGING** | debug, troubleshoot, fix | `DEBUG` |
| **SEARCH** | search, find, lookup | `SEARCH` |
| **EXECUTION** | execute, run, perform | `EXECUTE` |

#### 2. Artifacts (Pattern-Based Detection)

Artifacts are structural patterns detected in the text that indicate what type of output is expected:

| Artifact | Detection Pattern | Indicates |
|----------|------------------|-----------|
| **STRUCTURED** | JSON objects: `{...}` | Structured data output |
| **PROBABILITY** | Keywords: probability, odds, chance, likelihood | Probabilistic output |
| **LIST** | Markdown lists: `- item` or `* item` | List output |
| **VALIDATION** | Keywords: validate, verify, check compliance, ensure | Validation task |
| **DECISION** | Keywords: recommend, best option, choose, decision | Decision/ranking task |
| **TEXT** | Keywords: report, analysis | Text-based output |

#### 3. Epistemic Grounding (Context-Based Detection)

For probabilistic tasks, the system distinguishes between **GENERATE** and **PREDICT** based on epistemic grounding:

**PREDICT is chosen when:**
- **Uncertainty indicators** are present: "likely", "probably", "might", "could"
- **AND** either:
  - **Future indicators**: "will", "tomorrow", "next year", "forecast"
  - **OR Real-world indicators**: "weather", "market", "election", "outcome"

**GENERATE is chosen when:**
- Probability artifacts exist but without epistemic grounding
- Example: "Generate probability distribution" (synthetic data)

**Examples:**
```
"What's the likelihood it will rain tomorrow?"
→ PREDICT (uncertainty + future + real-world)

"Generate a probability distribution for dice rolls"
→ GENERATE (probability but synthetic, no real-world grounding)
```

#### 4. REQ Resolution Decision Tree

The system resolves the final REQ token using this priority order:

```
1. VALIDATE
   └─ If: (Artifact.VALIDATION OR Signal.VALIDATION)
      AND has_validation_target (STRUCTURED, TEXT, or DECISION artifacts)

2. EXTRACT
   └─ If: Signal.EXTRACTION
      AND NOT Artifact.PROBABILITY

3. TRANSFORM
   └─ If: Signal.TRANSFORMATION
      AND has_transform_target (STRUCTURED or TEXT artifacts)

4. FORMAT
   └─ If: Signal.FORMATTING

5. PREDICT
   └─ If: Artifact.PROBABILITY
      AND epistemic_grounding (uncertainty + future/real-world)

6. GENERATE
   └─ If: Artifact.PROBABILITY (without epistemic grounding)
      OR Artifact.STRUCTURED
      OR Artifact.TEXT
      OR Artifact.LIST

7. RANK
   └─ If: Signal.RANKING
      OR Artifact.DECISION

8. DEBUG
   └─ If: Signal.DEBUGGING

9. SEARCH
   └─ If: Signal.SEARCH

10. EXECUTE
    └─ If: Signal.EXECUTION

11. ANALYZE (default)
    └─ If: None of the above
```

#### 5. SPEC Detection (Output Specialization)

In addition to REQ detection, IntentDetectorV2 also detects **SPEC** (specification) which refines what type of output is being generated/predicted/extracted:

**SPEC detection uses three methods (scored):**

| Method | Score | Description |
|--------|-------|-------------|
| **Explicit patterns** | 3 points | Phrases like "generate a REPORT", "return a SUMMARY" |
| **Artifact mapping** | 2 points | Artifact.VALIDATION → VALIDATION_RESULT, Artifact.DECISION → RECOMMENDATION |
| **Keyword matching** | 1 point | Domain-specific keywords (see below) |

**SPEC Ontology (domain artifacts):**
- `SUPPORT_RESPONSE` - Customer support responses
- `TROUBLESHOOTING_GUIDE` - Step-by-step troubleshooting
- `BETTING_ODDS` - Betting or odds information
- `PROBABILITY_DISTRIBUTION` - Statistical distributions (excluded as non-domain)
- `FORECAST` - Future projections
- `REPORT` - Analysis reports
- `SUMMARY` - Condensed summaries
- `RECOMMENDATION` - Recommendations or decisions
- `RANKING` - Ordered lists
- `JSON_OBJECT` / `JSON_SCHEMA` - (excluded as format, not domain)
- `FIELDS` - Field extraction
- `ENTITIES` - Entity extraction
- `VALIDATION_RESULT` - Validation outcomes

**SPEC keyword mappings:**
```
BETTING_ODDS: ["odds", "betting", "bookmaker"]
FORECAST: ["forecast", "projection"]
SUMMARY: ["summary", "recap", "overview"]
REPORT: ["report", "analysis document"]
SUPPORT_RESPONSE: ["support", "ticket", "issue", "incident"]
TROUBLESHOOTING_GUIDE: ["troubleshoot", "troubleshooting", "steps"]
```

**How SPEC appears in tokens:**
```
[REQ:GENERATE:SPECS:REPORT]
[REQ:PREDICT:SPECS:FORECAST]
[REQ:VALIDATE:SPECS:VALIDATION_RESULT]
```

#### Complete Detection Example

**Input:**
```
"Analyze this customer support transcript and generate a detailed report
with sentiment analysis. Check if the agent followed compliance guidelines."
```

**Detection process:**

1. **Signals detected:**
   - "analyze" → Signal.ANALYSIS
   - "generate" → Signal.GENERATION

2. **Artifacts detected:**
   - "report" → Artifact.TEXT
   - "check" / "compliance" → Artifact.VALIDATION

3. **REQ resolution:**
   - Has validation signal + has validation target (TEXT)
   - **Result: REQ.VALIDATE** (validation takes priority)

4. **SPEC detection:**
   - "generate a...report" → explicit pattern (3 points) → "REPORT"
   - "compliance" keywords → "VALIDATION_RESULT"
   - Highest scorer: **REPORT**

**Final output:**
```
[REQ:VALIDATE:SPECS:REPORT]
```

#### More Real-World Examples

**Example 1: Weather Prediction**
```
Input: "What's the probability it will rain tomorrow in Seattle?"

Signals: PREDICTION (predict)
Artifacts: PROBABILITY (probability)
Epistemic: Yes (probability + will + real-world:weather)
REQ: PREDICT
SPEC: FORECAST (forecast implied)

Output: [REQ:PREDICT:SPECS:FORECAST]
```

**Example 2: Data Extraction**
```
Input: "Extract all email addresses and phone numbers from this document"

Signals: EXTRACTION (extract)
Artifacts: None (no JSON/list patterns in prompt)
REQ: EXTRACT
SPEC: ENTITIES (email addresses, phone numbers are entities)

Output: [REQ:EXTRACT:SPECS:ENTITIES]
```

**Example 3: Compliance Validation**
```
Input: "Verify that the agent followed all required disclosure steps and
validate compliance with company policies"

Signals: VALIDATION (verify, validate)
Artifacts: VALIDATION (verify, validate, compliance keywords)
Has validation target: Yes (implied TEXT)
REQ: VALIDATE
SPEC: VALIDATION_RESULT (validation context)

Output: [REQ:VALIDATE:SPECS:VALIDATION_RESULT]
```

**Example 4: Report Generation**
```
Input: "Create a summary report of customer feedback trends from Q4"

Signals: GENERATION (create, summary)
Artifacts: TEXT (report)
REQ: GENERATE (has TEXT artifact)
SPEC: REPORT (report explicitly mentioned)

Output: [REQ:GENERATE:SPECS:REPORT]
```

**Example 5: Probability Distribution (Synthetic)**
```
Input: "Generate a probability distribution for rolling two dice"

Signals: GENERATION (generate)
Artifacts: PROBABILITY (probability)
Epistemic: No (synthetic scenario, not real-world prediction)
REQ: GENERATE (probability without epistemic grounding)
SPEC: None (PROBABILITY_DISTRIBUTION excluded as non-domain)

Output: [REQ:GENERATE]
```

**Example 6: Data Transformation**
```
Input: "Convert this CSV data to JSON format {csv_data}"

Signals: TRANSFORMATION (convert)
Artifacts: STRUCTURED (JSON mentioned, {csv_data} pattern)
Has transform target: Yes (STRUCTURED)
REQ: TRANSFORM
SPEC: None

Output: [REQ:TRANSFORM]
```

**Example 7: Recommendation/Ranking**
```
Input: "Rank these candidates by best fit for the senior engineer position"

Signals: RANKING (rank)
Artifacts: DECISION (best)
REQ: RANK
SPEC: RANKING

Output: [REQ:RANK:SPECS:RANKING]
```

**Example 8: Troubleshooting Guide**
```
Input: "Generate troubleshooting steps for network connectivity issues"

Signals: GENERATION (generate)
Artifacts: TEXT (guide implied), LIST (steps)
REQ: GENERATE
SPEC: TROUBLESHOOTING_GUIDE (troubleshooting keyword)

Output: [REQ:GENERATE:SPECS:TROUBLESHOOTING_GUIDE]
```

#### Key Takeaways

1. **REQ detection is hierarchical** - certain REQs take priority (VALIDATE > EXTRACT > TRANSFORM > PREDICT > GENERATE)
2. **Signals + Artifacts + Context** all contribute to the final decision
3. **SPEC adds domain specificity** to the output type (REPORT, FORECAST, VALIDATION_RESULT, etc.)
4. **Epistemic grounding distinguishes PREDICT from GENERATE** for probabilistic tasks
5. **Default is ANALYZE** when no clear signals are detected

#### Complete Vocabulary Reference

The complete trigger phrase vocabularies are defined in language-specific vocabulary files:

**Location:** `clm_core/dictionary/{lang}/vocabulary.py`

**Available languages:**
- `en` - English (ENVocabulary)
- `es` - Spanish (ESVocabulary)
- `pt` - Portuguese (PTVocabulary)
- `fr` - French (FRVocabulary)

**Key vocabulary properties:**

1. **REQ_TOKENS** - Maps REQ types to trigger phrases:
   ```python
   "ANALYZE": ["analyze", "review", "examine", "evaluate", "assess", ...]
   "EXTRACT": ["extract", "pull out", "identify", "find", "retrieve", ...]
   "GENERATE": ["generate", "create", "write", "draft", "compose", ...]
   "VALIDATE": ["validate", "verify", "check", "confirm", "ensure", ...]
   "TRANSFORM": ["convert", "transform", "change", "rewrite", ...]
   "FORMAT": ["format", "structure", "organize", "layout", ...]
   "DEBUG": ["debug", "troubleshoot", "diagnose", "fix bug", ...]
   "SEARCH": ["search", "query", "lookup", "find", "look for", ...]
   "RANK": ["prioritize", "order", "sort by", "rate", "rank", ...]
   "PREDICT": ["predict", "forecast", "project", "estimate future", ...]
   "CALCULATE": ["calculate", "compute", "figure out", "quantify", ...]
   "EXECUTE": ["use", "apply", "implement", "run", "perform", ...]
   ```

2. **EPISTEMIC_KEYWORDS** - Keywords for epistemic grounding:
   ```python
   "future": ["next", "upcoming", "future", "will", "expected", "forecast", ...]
   "uncertainty": ["chance", "likelihood", "probability", "odds", "risk", ...]
   "real_world": ["match", "season", "weather", "election", "market", ...]
   ```

3. **Other useful vocabularies:**
   - `ACTION_VERBS` - General action verbs
   - `COMPOUND_PHRASES` - Multi-word phrases (e.g., "customer support" → "TICKET")
   - `TYPE_MAP` - Document type mappings
   - `CONTEXT_MAP` - Domain context mappings

**Example usage:**
```python
from clm_core.dictionary.en.vocabulary import ENVocabulary

vocab = ENVocabulary()

# Get all trigger phrases for EXTRACT
extract_phrases = vocab.REQ_TOKENS["EXTRACT"]
# ["extract", "pull out", "identify", "find", ...]

# Get epistemic keywords
future_keywords = vocab.EPISTEMIC_KEYWORDS["future"]
# ["next", "upcoming", "future", "will", ...]
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

### Intent Detection in the Encoding Pipeline

The IntentDetectorV2 is the **first step** in the system prompt encoding pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│  1. INTENT DETECTION (IntentDetectorV2)                     │
│     Input: Natural language prompt                          │
│     Output: Intent (REQ + SPEC)                             │
│                                                              │
│     Process:                                                 │
│     • Detect signals from vocabulary                        │
│     • Detect artifacts from patterns                        │
│     • Check epistemic grounding                             │
│     • Resolve REQ token (priority-based)                    │
│     • Extract SPEC (scoring-based)                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  2. TARGET DETECTION                                         │
│     Extract what the operation targets (TRANSCRIPT, etc.)   │
│     Output: [TARGET:TRANSCRIPT:DOMAIN=SUPPORT]              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  3. EXTRACTION FIELD DETECTION                               │
│     Identify fields to extract (SENTIMENT, URGENCY, etc.)   │
│     Output: [EXTRACT:SENTIMENT,URGENCY,RESOLUTION]          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  4. CONTEXT DETECTION                                        │
│     Extract context and conditions                          │
│     Output: [CTX:LANGUAGE=EN]                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  5. OUTPUT FORMAT DETECTION                                  │
│     Parse output schema and format requirements             │
│     Output: [OUT_JSON:{field:TYPE,...}:ENUMS={...}]         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  6. REFERENCE DETECTION                                      │
│     Extract IDs and references                              │
│     Output: [REF:TICKET=TKT-123]                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  FINAL COMPRESSED OUTPUT:                                    │
│  [REQ:VALIDATE:SPECS:REPORT]                                │
│  [TARGET:TRANSCRIPT:DOMAIN=SUPPORT]                         │
│  [EXTRACT:SENTIMENT,URGENCY,RESOLUTION]                     │
│  [CTX:LANGUAGE=EN]                                           │
│  [OUT_JSON:{summary:STR,scores:{...}}:ENUMS={...}]          │
│  [REF:TICKET=TKT-123]                                        │
└─────────────────────────────────────────────────────────────┘
```

**Key points:**
- Intent detection happens **first** and determines the REQ token
- REQ token guides the rest of the encoding process
- SPEC provides additional domain context for the output
- All components work together to form the complete compressed prompt

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

## Part 1b: Configuration Prompt Tokenization

### Purpose

Configuration prompts are **template-based system instructions** that define an agent's persistent behavior. Unlike task prompts that focus on a specific action, configuration prompts establish identity, rules, and behavioral patterns.

**Key differences from Task Prompts:**
- Define agent role and persona (not actions)
- Contain behavioral rules (basic and custom)
- Support runtime placeholders for dynamic values
- Include priority definitions for rule conflicts

### Configuration Prompt Token Types

```
+-----------------------------------------+
|  1. PROMPT_MODE - Prompt type           |  <- Identifier
|     [PROMPT_MODE:CONFIGURATION]         |
+-----------------------------------------+
           |
           v
+-----------------------------------------+
|  2. ROLE - Agent identity               |  <- Who
|     [ROLE:CUSTOMER_SUPPORT_AGENT]       |
+-----------------------------------------+
           |
           v
+-----------------------------------------+
|  3. RULES - Active rule sets            |  <- Behavior
|     [RULES:BASIC,CUSTOM]                |
+-----------------------------------------+
           |
           v
+-----------------------------------------+
|  4. PRIORITY - Conflict resolution      |  <- Precedence
|     [PRIORITY:CUSTOM_OVER_BASIC]        |
+-----------------------------------------+
           |
           v
+-----------------------------------------+
|  5. OUT - Output format (optional)      |  <- Output spec
|     [OUT_JSON:{field:TYPE}]             |
+-----------------------------------------+
```

### Token Definitions

| Token | Purpose | Required | Examples |
|-------|---------|----------|----------|
| **PROMPT_MODE** | Identifies prompt type | Yes | `[PROMPT_MODE:CONFIGURATION]` |
| **ROLE** | Agent identity/persona | When detected | `[ROLE:ASSISTANT]`, `[ROLE:CUSTOMER_SUPPORT_AGENT]` |
| **RULES** | Active rule sets | When detected | `[RULES:BASIC]`, `[RULES:BASIC,CUSTOM]` |
| **PRIORITY** | Rule conflict resolution | When detected | `[PRIORITY:CUSTOM_OVER_BASIC]` |
| **OUT** | Output format | When specified | `[OUT_JSON:{response:STR}]` |

### PROMPT_MODE Token

**Purpose:** Identifies this as a configuration prompt (vs task prompt)

**Values:**
- `CONFIGURATION` - Template-based agent configuration
- `TASK` - Action-oriented task prompt (default)

**Example:**
```
[PROMPT_MODE:CONFIGURATION]
```

### ROLE Token

**Purpose:** Captures the agent's identity and persona

**Detection patterns:**
- `<role>You are a...</role>` tags
- "You are a..." or "Your role is..." phrases

**Examples:**
```
[ROLE:HELPFUL_ASSISTANT]
[ROLE:CUSTOMER_SUPPORT_AGENT]
[ROLE:CONTENT_MODERATOR]
[ROLE:PROFESSIONAL_TRANSLATOR]
```

**Normalization:**
- Spaces replaced with underscores
- Converted to uppercase
- Articles (a, an, the) removed

### RULES Token

**Purpose:** Indicates which rule sets are active

**Values:**
- `BASIC` - Standard/default rules detected
- `CUSTOM` - User-specific rules detected

**Detection patterns:**
- `<basic_rules>` tags or "basic rules" phrase
- `<custom_rules>` tags or "custom instructions" phrase

**Examples:**
```
[RULES:BASIC]
[RULES:CUSTOM]
[RULES:BASIC,CUSTOM]
```

### PRIORITY Token

**Purpose:** Defines how rule conflicts should be resolved

**Values:**
- `CUSTOM_OVER_BASIC` - Custom rules take precedence

**Detection patterns:**
- "custom instructions are paramount"
- "prioritize custom instructions"
- "custom instructions override"

**Example:**
```
[PRIORITY:CUSTOM_OVER_BASIC]
```

### Configuration Prompt Example

**Original:**
```
<role>You are a helpful customer support agent</role>

<basic_rules>
- Be polite and professional
- Verify customer identity
- Document all interactions
</basic_rules>

<custom_rules>
- Address customer as: {{customer_name}}
- Account tier: {{account_tier}}
</custom_rules>

Follow the basic rules as your foundation. If there are conflicts
between basic rules and custom instructions, prioritize custom
instructions. Custom instructions are paramount.

OUTPUT:
{
    "response": "message",
    "escalate": true/false
}
```

**Compressed CL Token:**
```
[PROMPT_MODE:CONFIGURATION][ROLE:CUSTOMER_SUPPORT_AGENT][RULES:BASIC,CUSTOM][PRIORITY:CUSTOM_OVER_BASIC][OUT_JSON:{response:STR,escalate:BOOL}]
```

**Metadata extracted:**
- `role`: "CUSTOMER_SUPPORT_AGENT"
- `rules`: {"basic": true, "custom": true}
- `priority`: "CUSTOM_OVER_BASIC"
- `placeholders`: ["customer_name", "account_tier"]
- `output_format`: "{response:STR,escalate:BOOL}"

### Two-Phase Compression

Configuration prompts use a **two-phase compression** approach:

**Phase 1: CL Token Generation**
- Extract semantic elements (role, rules, priority)
- Generate compressed CL tokens
- Detect and encode output format

**Phase 2: NL Minimization**
- Remove redundant meta-instructions
- Suppress priority explanations (encoded in CL)
- Trim verbose rule descriptions
- Remove content already encoded in CL tokens

**Result:** CL tokens + minimized NL prompt

See [Configuration Prompt Encoding](../sys_prompt/configuration_prompt.md) for complete documentation.

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

- **[System Prompt Encoder](../sys_prompt/index.md)** - Overview of system prompt compression
  - [Task Prompts](../sys_prompt/task_prompt.md) - Using the 6-token hierarchy
  - [Configuration Prompts](../sys_prompt/configuration_prompt.md) - Template-based agent configuration
- **[Structured Data Encoder](../sd_encoder.md)** - Using header + row format
- **[CLM Vocabulary](clm_vocabulary.md)** - Understanding vocabulary mappings
- **[CLM Configuration](clm_configuration.md)** - Configuring the encoders

---
