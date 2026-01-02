# CLM Vocabulary

## Overview

The CLM Vocabulary system is the semantic foundation of CLLM compression. It defines mappings from natural language words and phrases to compressed semantic tokens, enabling intelligent compression that preserves meaning while dramatically reducing token count.

**Purpose:**
- Maps verbose phrases to concise tokens
- Identifies important vs. redundant words
- Provides language-specific semantic understanding
- Enables consistent token generation across compression types

**Structure:**
Each language has its own `Vocabulary` class (e.g., `ENVocabulary`, `PTVocabulary`) that inherits from `BaseVocabulary` and defines language-specific word lists, mappings, and patterns.

---

## Vocabulary Architecture

### Language-Specific Vocabularies

```python
# Available vocabularies
ENVocabulary()  # English - Complete
PTVocabulary()  # Portuguese - Complete
ESVocabulary()  # Spanish - Complete
FRVocabulary()  # French - Complete
# Others in development
```

**Access via CLMConfig:**
```python
from clm_core import CLMConfig, CLMEncoder

config = CLMConfig(lang="en")
vocab = config.vocab  # ENVocabulary instance

# Use vocabulary for compression
encoder = CLMEncoder(cfg=config)
```

---

## Core Vocabulary Categories

The vocabulary system is organized into 25+ categories, each serving a specific purpose in compression.

### 1. CODE_INDICATORS

**Purpose:** Identifies code and technical content

**Examples:**
```python
CODE_INDICATORS = (
    "code", "script", "function", "program", "algorithm",
    "api", "class", "method", "variable", "git", "commit",
    "unittest", "test case", "debug", "refactor"
)
```

**Use case:**
```
Input: "Review the code in the function and check for bugs"
Detection: "code", "function" → CODE domain
Output: [REQ:REVIEW] [TARGET:CODE:DOMAIN=CODE] [EXTRACT:BUGS]
```

---

### 2. ACTION_VERBS

**Purpose:** Comprehensive list of action verbs for intent detection

**Categories:**
- **Modification:** reduce, increase, improve, optimize, enhance, update, modify
- **Problem-solving:** fix, solve, resolve, debug, repair, troubleshoot, diagnose
- **Creation:** create, generate, build, make, produce, design, develop
- **Analysis:** analyze, examine, review, evaluate, assess, validate, verify
- **Explanation:** explain, describe, clarify, define, document
- **Processing:** calculate, compute, determine, find, process
- **Organization:** compare, contrast, classify, categorize, sort, organize
- **Data handling:** extract, transform, load, aggregate, filter
- **Operations:** deploy, release, rollback, scale, provision

**Examples (60+ verbs):**
```python
ACTION_VERBS = (
    "reduce", "increase", "improve", "optimize", "enhance",
    "fix", "solve", "resolve", "debug", "repair",
    "create", "generate", "build", "make", "produce",
    "analyze", "examine", "review", "evaluate", "assess",
    "explain", "describe", "clarify", "define", "document",
    # ... 40+ more
)
```

**Use case:**
```
Input: "Analyze the data and generate a report"
Verbs detected: "analyze" → ANALYZE, "generate" → GENERATE
Output: [REQ:ANALYZE,GENERATE] [TARGET:DATA] [OUT:REPORT]
```

---

### 3. STOPWORDS

**Purpose:** Words to remove during compression (no semantic value)

**Examples:**
```python
STOPWORDS = (
    "it", "this", "that", "these", "those",
    "a", "an", "the",
    "some", "any", "all", "none",
    "something", "anything", "everything", "nothing",
    "someone", "anyone", "everyone", "no one"
)
```

**Use case:**
```
Input: "Please analyze this data and provide the results"
Removal: "Please", "this", "the" → filtered out
Output: [REQ:ANALYZE] [TARGET:DATA] [OUT:RESULTS]
```

---

### 4. PRONOUNS

**Purpose:** Personal pronouns to filter or simplify

**Examples:**
```python
PRONOUNS = (
    "i", "we", "you", "they", "he", "she", "it",
    "me", "us", "them", "him", "her",
    "my", "our", "your", "their", "his", "her", "its"
)
```

**Use case:**
```
Input: "I need you to analyze my data"
Simplified: "I", "you", "my" → filtered
Output: [REQ:ANALYZE] [TARGET:DATA]
```

---

### 5. MODALS

**Purpose:** Modal verbs that add no semantic content

**Examples:**
```python
MODALS = (
    "can", "could", "should", "would", "will", "shall",
    "may", "might", "must",
    "do", "does", "did"
)
```

**Use case:**
```
Input: "You should analyze the code and you could check for bugs"
Removed: "should", "could" → no impact on meaning
Output: [REQ:ANALYZE] [TARGET:CODE] [EXTRACT:BUGS]
```

---

### 6. COMPOUND_PHRASES

**Purpose:** Multi-word phrases mapped to single tokens

**Examples:**
```python
COMPOUND_PHRASES = {
    "customer support": "TICKET",
    "customer service": "TICKET",
    "support ticket": "TICKET",
    "help desk": "TICKET",
    
    "chat transcript": "TRANSCRIPT",
    "conversation transcript": "TRANSCRIPT",
    
    "source code": "CODE",
    "code review": "CODE",
    "pull request": "CODE",
    
    "error message": "LOG",
    "stack trace": "LOG",
    "system log": "LOG",
    
    "api endpoint": "ENDPOINT",
    "rest api": "ENDPOINT",
    
    "unit test": "TEST",
    "test case": "TEST",
    
    "business plan": "PLAN",
    "project plan": "PLAN",
    
    "database query": "QUERY",
    "sql query": "QUERY"
}
```

**Use case:**
```
Input: "Analyze the customer support ticket and check the error message"
Mapping: "customer support" → TICKET, "error message" → LOG
Output: [REQ:ANALYZE] [TARGET:TICKET] [EXTRACT:LOG]
```

**Impact:** Reduces multi-word phrases to single tokens, significant compression

---

### 7. TYPE_MAP

**Purpose:** Document/content type identification

**Examples:**
```python
TYPE_MAP = {
    "call": "CALL",
    "phone call": "CALL",
    "meeting": "MEETING",
    "chat": "CHAT",
    "email": "EMAIL",
    "message": "EMAIL",
    "conversation": "CONVERSATION",
    "report": "REPORT",
    "document": "DOCUMENT",
    "article": "ARTICLE",
    "transcript": "TRANSCRIPT",
    "ticket": "TICKET",
    "case": "TICKET",
    "complaint": "COMPLAINT",
    "feedback": "FEEDBACK",
    "inquiry": "INQUIRY",
    "request": "REQUEST"
}
```

**Use case:**
```
Input: "Analyze the customer support call transcript"
Type detection: "call" → CALL, "transcript" → TRANSCRIPT
Output: [REQ:ANALYZE] [TARGET:CALL,TRANSCRIPT:DOMAIN=SUPPORT]
```

---

### 8. CONTEXT_MAP

**Purpose:** Domain/context identification

**Examples:**
```python
CONTEXT_MAP = {
    "customer": "CUSTOMER",
    "support": "SUPPORT",
    "sales": "SALES",
    "technical": "TECHNICAL",
    "engineering": "TECHNICAL",
    "product": "PRODUCT",
    "marketing": "MARKETING",
    "business": "BUSINESS",
    "finance": "FINANCE",
    "legal": "LEGAL",
    "hr": "HR",
    "operations": "OPERATIONS"
}
```

**Use case:**
```
Input: "Analyze the technical support ticket"
Context: "technical" → TECHNICAL, "support" → SUPPORT
Output: [REQ:ANALYZE] [TARGET:TICKET:DOMAIN=TECHNICAL,SUPPORT]
```

---

### 9. domain_candidates

**Purpose:** Keywords that indicate specific domains

**Domains (15 total):**

**CODE:**
```python
"bug", "error", "security", "performance", "code", "script",
"function", "algorithm", "debug", "compile", "library", "api"
```

**ENTITIES:**
```python
"names", "dates", "amounts", "addresses", "emails", "phones"
```

**QA:**
```python
"verification", "policy", "soft_skills", "accuracy", 
"compliance", "disclosures"
```

**SUPPORT:**
```python
"issue", "sentiment", "actions", "urgency", "priority",
"ticket", "customer", "agent", "troubleshoot"
```

**TECHNICAL:**
```python
"bug", "error", "stacktrace", "api", "server", "log",
"debug", "crash", "deployment", "backend"
```

**DOCUMENT:**
```python
"document", "article", "manual", "guide", "transcript",
"notes", "summary", "instructions"
```

**BUSINESS:**
```python
"report", "analysis", "executive", "management", "dashboard",
"kpi", "roi", "quarterly", "presentation"
```

**LEGAL:**
```python
"contract", "policy", "compliance", "gdpr", "clause",
"agreement", "terms", "privacy"
```

**FINANCE:**
```python
"invoice", "billing", "payment", "transaction", "refund",
"expense", "balance", "statement"
```

**SECURITY:**
```python
"breach", "risk", "threat", "alert", "malware", "phishing",
"permissions", "access control", "audit"
```

**MEDICAL:**
```python
"patient", "diagnosis", "prescription", "clinical", "symptoms",
"treatment", "doctor"
```

**SALES:**
```python
"lead", "crm", "opportunity", "pipeline", "prospect", "deal", "quote"
```

**EDUCATION:**
```python
"lesson", "curriculum", "teacher", "student", "training", "course"
```

**Use case:**
```
Input: "Analyze the invoice for compliance with GDPR policy"
Keywords: "invoice" → FINANCE, "compliance", "gdpr", "policy" → LEGAL
Output: [REQ:ANALYZE] [TARGET:INVOICE:DOMAIN=FINANCE,LEGAL]
```

---

### 10. REQ_TOKENS

**Purpose:** Maps action phrases to standardized request tokens

**Main categories (23 total):**

**ANALYZE:**
```python
"analyze", "review", "examine", "evaluate", "assess",
"inspect", "check out", "audit", "investigate"
```

**EXTRACT:**
```python
"extract", "pull out", "identify", "find", "locate",
"get", "retrieve", "return", "include", "select"
```

**GENERATE:**
```python
"generate", "create", "write", "draft", "compose",
"produce", "build", "develop", "suggest", "formulate"
```

**SUMMARIZE:**
```python
"summarize", "condense", "brief", "synopsis", "sum up",
"digest", "recap"
```

**TRANSFORM:**
```python
"convert", "transform", "change", "rewrite", "translate",
"modify", "adapt", "rephrase", "edit", "add", "remove"
```

**EXPLAIN:**
```python
"explain", "describe", "clarify", "elaborate", "tell me about",
"detail", "illustrate", "discuss", "define"
```

**COMPARE:**
```python
"compare", "contrast", "versus", "vs", "difference between",
"differentiate", "distinguish"
```

**CLASSIFY:**
```python
"classify", "categorize", "sort", "group", "label",
"organize", "arrange", "segment"
```

**DEBUG:**
```python
"debug", "troubleshoot", "diagnose", "fix bug", "investigate bug",
"find bug", "track down", "identify issue"
```

**OPTIMIZE:**
```python
"optimize", "improve", "enhance", "refactor", "speed up",
"streamline", "maximize", "minimize", "reduce", "increase"
```

**VALIDATE:**
```python
"validate", "verify", "check", "confirm", "test",
"ensure", "certify", "authenticate"
```

**And 12 more categories:** SEARCH, RANK, PREDICT, FORMAT, DETECT, CALCULATE, AGGREGATE, DETERMINE, ROUTE, EXECUTE, LIST, MATCH, SELECT

**Use case:**
```
Input: "Please summarize the document and extract key entities"
Mapping: "summarize" → SUMMARIZE, "extract" → EXTRACT
Output: [REQ:SUMMARIZE,EXTRACT] [TARGET:DOCUMENT] [EXTRACT:ENTITIES]
```

---

### 11. TARGET_TOKENS

**Purpose:** Maps object descriptions to standardized target tokens

**Categories (40+ targets):**

**Code & Technical:**
```python
"CODE": ["code", "script", "program", "function"],
"QUERY": ["query", "sql", "database query"],
"ENDPOINT": ["endpoint", "api", "rest endpoint"],
"COMPONENT": ["component", "module", "package"],
"SYSTEM": ["system", "application", "software"],
"TEST": ["test", "unit test", "test case"],
"LOG": ["log", "logs", "error log"]
```

**Documents:**
```python
"DOCUMENT": ["document", "doc", "file", "report"],
"EMAIL": ["email", "message", "correspondence"],
"REPORT": ["report", "analysis", "findings"],
"TRANSCRIPT": ["transcript", "conversation", "chat log"]
```

**Customer Service:**
```python
"TICKET": ["ticket", "support ticket", "issue", "case"],
"COMPLAINT": ["complaint", "issue", "problem"],
"REQUEST": ["request", "service request"],
"INQUIRY": ["inquiry", "question", "query"],
"CALL": ["call", "phone call", "support call"]
```

**Business:**
```python
"PLAN": ["plan", "business plan", "project plan"],
"POST": ["post", "linkedin post", "blog post"],
"SUMMARY": ["summary", "executive summary"],
"METRICS": ["revenue", "metrics", "statistics"]
```

**Specialized:**
```python
"NBA_CATALOG": ["nba", "next best action", "predefined actions"],
"CUSTOMER_INTENT": ["customer intent", "customer need"],
"CORRELATION": ["correlation", "relationship"],
"TRADEOFF": ["trade-off", "tradeoffs"],
"PATTERN": ["pattern", "patterns", "trend"],
"CHURN": ["churn", "customer churn", "attrition"]
```

**Use case:**
```
Input: "Analyze the NBA catalog and identify patterns in customer churn"
Mapping: "nba catalog" → NBA_CATALOG, "patterns" → PATTERN, "customer churn" → CHURN
Output: [REQ:ANALYZE] [TARGET:NBA_CATALOG] [EXTRACT:PATTERN,CHURN]
```

---

### 12. EXTRACT_FIELDS

**Purpose:** Standardized field names for extraction

**Categories (50+ fields):**

**Customer Service:**
```python
"ISSUE", "SENTIMENT", "ACTIONS", "NEXT_STEPS",
"URGENCY", "PRIORITY", "CUSTOMER_INTENT"
```

**Entities:**
```python
"NAMES", "DATES", "AMOUNTS", "EMAILS", "PHONES", "ADDRESSES"
```

**Technical:**
```python
"BUGS", "SECURITY", "PERFORMANCE", "ERRORS", "WARNINGS"
```

**Analysis:**
```python
"KEYWORDS", "TOPICS", "ENTITIES", "FACTS", "DECISIONS",
"REQUIREMENTS", "FEATURES", "PROBLEMS", "SOLUTIONS", "RISKS"
```

**Metrics:**
```python
"METRICS", "KPI", "SCORES", "RATINGS", "RELEVANCE_SCORE",
"MATCH_CONFIDENCE", "SEMANTIC_SIMILARITY"
```

**Metadata:**
```python
"OWNERS", "ASSIGNEES", "STAKEHOLDERS", "PARTICIPANTS",
"TIMESTAMPS", "DURATIONS", "FREQUENCIES", "QUANTITIES",
"CATEGORIES", "TAGS", "LABELS", "STATUS", "TYPE"
```

**Use case:**
```
Input: "Extract sentiment, urgency, and next steps from the ticket"
Fields: "sentiment" → SENTIMENT, "urgency" → URGENCY, "next steps" → NEXT_STEPS
Output: [REQ:EXTRACT] [TARGET:TICKET] [EXTRACT:SENTIMENT,URGENCY,NEXT_STEPS]
```

---

### 13. OUTPUT_FORMATS

**Purpose:** Specifies desired output format

**Examples:**
```python
OUTPUT_FORMATS = {
    "JSON": ["json", "json format"],
    "MARKDOWN": ["markdown", "md"],
    "TABLE": ["table", "tabular"],
    "LIST": ["list", "bullet points", "bullets"],
    "PLAIN": ["plain text", "text only"],
    "CSV": ["csv", "comma-separated"]
}
```

**Use case:**
```
Input: "Analyze the data and return results as JSON"
Format: "json" → JSON
Output: [REQ:ANALYZE] [TARGET:DATA] [OUT:JSON]
```

---

### 14. rank_triggers

**Purpose:** Identifies ranking/sorting requests

**Examples:**
```python
rank_triggers = {
    "rank", "ranking", "sort", "sort by", "order", "order by",
    "prioritize", "priority", "most important", "least important",
    "top", "bottom", "first", "last", "highest", "lowest",
    "best", "worst", "greatest", "least", "maximum", "minimum",
    "arrange"
}
```

**Use case:**
```
Input: "Rank the tickets by priority and sort by urgency"
Triggers: "rank", "sort" → REQ:RANK
Output: [REQ:RANK] [TARGET:TICKETS] [BY:PRIORITY,URGENCY]
```

---

### 15. NOISE_VERBS

**Purpose:** Common verbs with little semantic value to filter

**Examples:**
```python
NOISE_VERBS = {
    "be", "have", "do", "can", "could", "should", "would",
    "may", "might", "must", "will", "shall",
    "go", "come", "take", "get", "make", "work", "live",
    "know", "think", "feel", "say", "call"
}
```

**Use case:**
```
Input: "I would like you to have the system analyze the data"
Filter: "would", "have" → removed
Output: [REQ:ANALYZE] [TARGET:DATA]
```

---

### 16. IMPERATIVE_PATTERNS

**Purpose:** Command patterns that map to actions

**Examples:**
```python
IMPERATIVE_PATTERNS = [
    (["list", "enumerate", "itemize"], "LIST", "ITEMS"),
    (["name", "identify"], "GENERATE", "ITEMS"),
    (["give", "provide", "suggest"], "GENERATE", "ITEMS"),
    (["tell", "explain", "describe"], "EXPLAIN", "CONCEPT")
]
```

**Use case:**
```
Input: "List the top 5 issues"
Pattern: "list" → LIST + ITEMS
Output: [REQ:LIST] [TARGET:ITEMS] [LIMIT:5]
```

---

### 17. QUESTION_WORDS

**Purpose:** Question word detection for query analysis

**Examples:**
```python
QUESTION_WORDS = ["what", "who", "where", "when", "why", "how", "which"]
```

**Use case:**
```
Input: "What are the main issues?"
Detection: "what" → question pattern
Output: [REQ:EXTRACT] [TARGET:ISSUES:TYPE=MAIN]
```

---

## Vocabulary Usage in Compression

### Flow: Natural Language → Compressed Tokens

**Step 1: Text Input**
```
"Please analyze the customer support transcript and extract 
sentiment, urgency, and next steps"
```

**Step 2: Vocabulary Matching**
```
"analyze" → REQ_TOKENS["ANALYZE"]
"customer support transcript" → COMPOUND_PHRASES["customer support"] + TYPE_MAP["transcript"]
"extract" → REQ_TOKENS["EXTRACT"]
"sentiment" → EXTRACT_FIELDS["SENTIMENT"]
"urgency" → EXTRACT_FIELDS["URGENCY"]
"next steps" → EXTRACT_FIELDS["NEXT_STEPS"]
```

**Step 3: Token Generation**
```
[REQ:ANALYZE,EXTRACT] 
[TARGET:TRANSCRIPT:DOMAIN=SUPPORT] 
[EXTRACT:SENTIMENT,URGENCY,NEXT_STEPS]
```

**Step 4: Compression**
```
Original: 87 tokens
Compressed: 23 tokens
Reduction: 73.6%
```

---

## Language-Specific Vocabularies

### English (ENVocabulary)

**Status:** ✅ Complete  
**Coverage:** All 25+ categories fully populated  
**Quality:** Production-ready  
**Size:** 1,000+ mappings

**Strengths:**
- Comprehensive technical vocabulary
- Extensive business terminology
- Rich customer service terms
- Complete domain coverage

---

### Portuguese (PTVocabulary)

**Status:** ✅ Complete  
**Coverage:** All categories with Portuguese translations  
**Quality:** Production-ready

**Example mappings:**
```python
REQ_TOKENS = {
    "ANALYZE": ["analisar", "revisar", "examinar", "avaliar"],
    "EXTRACT": ["extrair", "obter", "identificar", "localizar"],
    "GENERATE": ["gerar", "criar", "escrever", "produzir"]
}

TARGET_TOKENS = {
    "DOCUMENTO": ["documento", "doc", "arquivo"],
    "TRANSCRIPT": ["transcrição", "conversa", "diálogo"]
}
```

---

### Spanish (ESVocabulary)

**Status:** ✅ Complete  
**Coverage:** All categories with Spanish translations  
**Quality:** Production-ready

**Example mappings:**
```python
REQ_TOKENS = {
    "ANALYZE": ["analizar", "revisar", "examinar", "evaluar"],
    "EXTRACT": ["extraer", "obtener", "identificar", "localizar"],
    "GENERATE": ["generar", "crear", "escribir", "producir"]
}
```

---

### French (FRVocabulary)

**Status:** ✅ Complete  
**Coverage:** All categories with French translations  
**Quality:** Production-ready

**Example mappings:**
```python
REQ_TOKENS = {
    "ANALYZE": ["analyser", "examiner", "évaluer", "inspecter"],
    "EXTRACT": ["extraire", "obtenir", "identifier", "localiser"],
    "GENERATE": ["générer", "créer", "écrire", "produire"]
}
```

---

## Extending Vocabulary

### Understanding Vocabulary Categories

Each category serves a specific purpose:

| Category | Purpose | Impact |
|----------|---------|--------|
| **REQ_TOKENS** | Action detection | High - Determines primary operation |
| **TARGET_TOKENS** | Object identification | High - What to operate on |
| **EXTRACT_FIELDS** | Field names | High - What data to extract |
| **COMPOUND_PHRASES** | Multi-word compression | Very High - 5-10x compression |
| **domain_candidates** | Domain detection | Medium - Context setting |
| **STOPWORDS** | Noise removal | Medium - Cleanup |
| **CODE_INDICATORS** | Technical detection | Low - Domain hint |
| **rank_triggers** | Sorting detection | Low - Specialized use |

---

## Best Practices

### 1. Leverage Compound Phrases

**Impact:** Highest compression ratio

```python
# Without compound phrase
"customer support ticket" → 3 tokens

# With COMPOUND_PHRASES mapping
"customer support" → TICKET → 1 token
Total: "customer support ticket" → TICKET → 1 token (66% reduction)
```

### 2. Use Domain-Specific Vocabularies

```python
# Generic
config = CLMConfig(lang="en")

# Add domain context helps
# (domain is inferred from vocabulary matches)
```

### 3. Understand Token Priority

**Priority order:**
1. **Required tokens** (REQ, TARGET) - Always present
2. **Extract fields** - When extraction requested
3. **Context** - When domain detected
4. **Output** - When format specified
5. **Metadata** - When available

### 4. Test Vocabulary Coverage

```python
# Check if vocabulary handles your domain
test_phrases = [
    "analyze customer support ticket",
    "extract sentiment from transcript",
    "generate next best action"
]

for phrase in test_phrases:
    result = encoder.encode(phrase)
    print(f"{phrase} → {result.compressed}")
    print(f"Compression: {result.compression_ratio:.1%}")
```

---

## Advanced: Vocabulary Statistics

### English Vocabulary Size

| Category | Count |
|----------|-------|
| **ACTION_VERBS** | 60+ |
| **REQ_TOKENS** | 23 categories × 5-10 synonyms = 150+ |
| **TARGET_TOKENS** | 40+ categories × 3-7 variants = 200+ |
| **EXTRACT_FIELDS** | 50+ |
| **COMPOUND_PHRASES** | 45+ |
| **domain_candidates** | 15 domains × 10-20 keywords = 200+ |
| **STOPWORDS** | 25+ |
| **Total mappings** | ~1,000+ |

### Coverage by Domain

Based on `domain_candidates`:

| Domain | Keywords | Use Cases |
|--------|----------|-----------|
| **SUPPORT** | 18 | Customer service, tickets, complaints |
| **CODE** | 19 | Software development, debugging |
| **TECHNICAL** | 12 | IT operations, system issues |
| **BUSINESS** | 11 | Reports, analytics, presentations |
| **FINANCE** | 9 | Invoices, billing, transactions |
| **LEGAL** | 9 | Contracts, compliance, policies |
| **SECURITY** | 9 | Threats, breaches, access control |
| **MEDICAL** | 8 | Patient care, diagnoses |
| **SALES** | 8 | CRM, leads, deals |
| **EDUCATION** | 7 | Training, courses, students |
| **QA** | 6 | Quality assurance, compliance |
| **ENTITIES** | 6 | Names, dates, amounts |
| **DOCUMENT** | 10 | General documents |

---

## Troubleshooting

### Issue: Low Compression in Specific Domain

**Symptom:** Compression ratio lower than expected for your content type

**Solution:** Check if vocabulary has coverage for your domain

```python
# Check domain candidates
config = CLMConfig(lang="en")
vocab = config.vocab

# Does your domain exist?
domains = vocab.domain_candidates.keys()
print(f"Available domains: {domains}")

# If missing: content may not compress well
# Consider contributing to vocabulary or using web feedback
```

### Issue: Important Terms Not Recognized

**Symptom:** Specific jargon or terminology not mapping correctly

**Solution:** Use explicit field names that match EXTRACT_FIELDS

```python
# Instead of domain jargon
"Get the customer NPS score"

# Use vocabulary terms
"Extract the satisfaction rating"  # Maps to RATINGS
```

### Issue: Over-Compression Losing Meaning

**Symptom:** Compressed output lacks necessary detail

**Solution:** Vocabulary prioritizes semantic preservation

```python
# The vocabulary is designed to preserve meaning
# If compression seems too aggressive, it may be working correctly
# Test with LLM to verify understanding
```

---

## Next Steps

- **[CLM Configuration](clm_configuration.md)** - Using vocabularies via config
- **[Token Hierarchy](clm_tokenization.md)** - Understanding token structure
- **[Pattern Matching Rules](clm_configuration.md#pattern-matching-rules)** - Regex-based patterns
- **[System Prompt Encoder](../sys_prompt_encoder.md)** - Vocabulary in system prompts
- **[Transcript Encoder](../transcript_encoder.md)** - Vocabulary in transcripts

---