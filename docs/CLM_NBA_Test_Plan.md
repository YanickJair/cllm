# CLM vs Natural Language - NBA Test Plan

## 🎯 Objective

Prove that CLM-compressed transcripts can:
1. Maintain or improve accuracy vs natural language
2. Work on cheaper models with same quality
3. Reduce latency and cost significantly

**Success Criteria:**
- CLM on Sonnet 4.5 ≥ Natural Language on Opus 4.1 (accuracy)
- CLM shows lower latency + cost
- LLM judge scores CLM ≥ 90% quality vs natural language

---

## 📊 Test Matrix

| Test ID | Input Format | Model | Metrics*#YJKL0ud#

|---------|-------------|-------|---------|
| T1 | Natural Language | Claude Opus 4.1 | Baseline |
| T2 | Natural Language | Claude Sonnet 4.5 | Compare |
| T3 | Natural Language | Claude Haiku 4 | Compare |
| T4 | **CLM Compressed** | Claude Opus 4.1 | Compare |
| T5 | **CLM Compressed** | Claude Sonnet 4.5 | **Target Winner** |
| T6 | **CLM Compressed** | Claude Haiku 4 | Compare |

**Key Comparison:**
- **T1 vs T5**: Can CLM on Sonnet match Natural Language on Opus?
- If T5 accuracy ≥ T1 AND T5 cost < T1 → **CLM WINS**

---

## 🧪 Test Dataset

### 1. Real Customer Transcripts (10-20 samples)

**Requirements:**
- Actual Foundever customer service calls
- Diverse issue types:
  - Billing disputes
  - Technical support
  - Product inquiries
  - Account changes
  - Escalations
- Length: 500-2000 tokens each
- Include metadata: call_id, agent, duration, channel

**Example transcript structure:**
```
Call ID: CS-12345
Agent: Sarah
Duration: 8m
Channel: Voice

Agent: Hi, thank you for calling. How can I help?
Customer: Hi, I'm having trouble with my bill...
[... full conversation ...]
```

### 2. Real NBA Catalog

**Your existing NBA catalog from Salesforce Einstein:**
```json
{
  "nbas": [
    {
      "id": "NBA-001",
      "title": "Billing Issue Resolution",
      "description": "Handle billing problems including disputed charges...",
      "category": "billing",
      "priority": "high",
      "prerequisites": ["account_verified", "billing_access"],
      "actions": [
        {
          "name": "Verify Charges",
          "description": "Review recent charges with customer",
          "steps": ["Pull billing history", "Identify disputed charges", "Explain each charge"]
        },
        {
          "name": "Process Refund",
          "description": "Issue refund for valid disputes",
          "steps": ["Verify refund eligibility", "Process credit", "Confirm with customer"]
        }
      ],
      "expected_outcome": "Resolved billing dispute, customer satisfied"
    },
    // ... 20-30 more NBAs
  ]
}
```

**Compress NBA catalog using your existing CLLM NBA encoder:**
```
[NBA:001:BILLING_ISSUE:PRIORITY=HIGH:ACTIONS=VERIFY_CHARGES+PROCESS_REFUND]
[NBA:002:TECH_SUPPORT:PRIORITY=MEDIUM:ACTIONS=TROUBLESHOOT+ESCALATE]
...
```

### 3. Expected Ground Truth

**For each transcript, have human expert annotate:**
```json
{
  "transcript_id": "CS-12345",
  "ground_truth": {
    "primary_issue": "BILLING_DISPUTE",
    "recommended_nbas": [
      {
        "nba_id": "NBA-001",
        "confidence": 0.95,
        "reasoning": "Customer disputed charges, matches billing resolution flow"
      },
      {
        "nba_id": "NBA-018",
        "confidence": 0.75,
        "reasoning": "Backup option if refund not approved"
      }
    ],
    "next_best_action": "Verify Charges",
    "expected_resolution": "Process refund"
  }
}
```

---

## 🔧 Test Implementation

### Step 1: Prepare Input Variants

For each transcript, create TWO versions:

#### A. Natural Language Version
```
System Prompt (400 tokens):
You are a Next Best Action recommendation system for customer service agents.
Analyze the call transcript and recommend the top 2 most relevant actions from
the NBA catalog. Consider customer intent, conversation context, and action
prerequisites. Return recommendations with confidence scores and reasoning...

User Prompt:
Analyze the following call transcript and recommend the top 2 NBAs:

TRANSCRIPT:
Agent: Hi, thank you for calling. How can I help?
Customer: Hi, I'm having trouble with my bill. I was charged twice...
[... full 1,500 token transcript ...]

NBA CATALOG:
1. Billing Issue Resolution
   Description: Handle billing problems including disputed charges...
   Actions: Verify Charges, Process Refund
   [... full 2,200 token catalog ...]

Recommend the top 2 NBAs with confidence scores and reasoning.
```

**Total tokens: ~4,100 tokens**

#### B. CLM Compressed Version
```
System Prompt (1 token):
[REF:SYS_NBA_RECOMMEND:v1]

User Prompt:
[REQ:RECOMMEND:TOP=2] [TARGET:NBA:DOMAIN=SUPPORT]

[TRANSCRIPT:
 [CALL:SUPPORT:AGENT=Sarah:DURATION=8m]
 [CUSTOMER:ACCOUNT=12345:TIER=PREMIUM]
 [CONTACT:EMAIL=user@example.com]
 [ISSUE:BILLING_DISPUTE:DISPUTED_AMOUNTS=$14.99+$16.99:CAUSE=DOUBLE_CHARGE]
 [ACTION:VERIFY:RESULT=CONFIRMED]
 [RESOLUTION:PENDING]
 [SENTIMENT:FRUSTRATED→NEUTRAL]
]

[NBA_CATALOG:
 [NBA:001:BILLING_ISSUE:PRIORITY=HIGH:ACTIONS=VERIFY_CHARGES+PROCESS_REFUND]
 [NBA:002:ACCOUNT_UPDATE:PRIORITY=MEDIUM:ACTIONS=UPDATE_INFO+VERIFY_IDENTITY]
 ...
]

[OUT:JSON:FIELDS=nba_id+confidence+reasoning]
```

**Total tokens: ~225 tokens**

**Token Reduction: 94.5%** (4,100 → 225)

---

### Step 2: Execute Tests

For each of the 6 test configurations (T1-T6):

```python
def run_test(test_id: str, transcript: str, nba_catalog: dict, 
             input_format: str, model: str):
    """
    Run single test case
    """
    # Prepare input
    if input_format == "natural":
        prompt = create_natural_language_prompt(transcript, nba_catalog)
    else:  # CLM
        compressed_transcript = compress_transcript(transcript)
        compressed_catalog = compress_nba_catalog(nba_catalog)
        prompt = create_clm_prompt(compressed_transcript, compressed_catalog)
    
    # Call API
    start_time = time.time()
    response = call_anthropic_api(
        model=model,
        prompt=prompt
    )
    latency = time.time() - start_time
    
    # Calculate cost
    input_tokens = count_tokens(prompt)
    output_tokens = count_tokens(response)
    cost = calculate_cost(model, input_tokens, output_tokens)
    
    # Parse response
    recommendations = parse_nba_recommendations(response)
    
    return {
        'test_id': test_id,
        'input_format': input_format,
        'model': model,
        'latency_ms': latency * 1000,
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'cost_dollars': cost,
        'recommendations': recommendations,
        'raw_response': response
    }
```

---

### Step 3: LLM Judge Evaluation

Use Claude Opus 4.1 as the judge (most capable model):

```python
JUDGE_PROMPT = """
You are evaluating NBA recommendations from a customer service AI system.

GROUND TRUTH:
{ground_truth}

RECOMMENDATION A:
{recommendation_a}

RECOMMENDATION B:
{recommendation_b}

Evaluate both recommendations on:
1. Accuracy (0-10): How well do they match ground truth?
2. Relevance (0-10): Are the NBAs appropriate for this situation?
3. Reasoning Quality (0-10): Is the explanation clear and logical?
4. Actionability (0-10): Can an agent immediately use this?

Return your evaluation as JSON:
{
  "recommendation_a": {
    "accuracy": 9,
    "relevance": 8,
    "reasoning_quality": 9,
    "actionability": 8,
    "total_score": 34,
    "strengths": "...",
    "weaknesses": "..."
  },
  "recommendation_b": {
    "accuracy": 7,
    "relevance": 8,
    "reasoning_quality": 6,
    "actionability": 7,
    "total_score": 28,
    "strengths": "...",
    "weaknesses": "..."
  },
  "winner": "A",
  "confidence": "high",
  "reasoning": "Recommendation A is more accurate and provides clearer reasoning..."
}
"""

def judge_recommendations(ground_truth, rec_a, rec_b):
    """
    Use LLM to judge which recommendation is better
    """
    prompt = JUDGE_PROMPT.format(
        ground_truth=json.dumps(ground_truth, indent=2),
        recommendation_a=json.dumps(rec_a, indent=2),
        recommendation_b=json.dumps(rec_b, indent=2)
    )
    
    response = call_anthropic_api(
        model="claude-opus-4.1",
        prompt=prompt
    )
    
    return json.loads(response)
```

---

## 📊 Metrics to Track

### 1. Cost Metrics

```python
# Anthropic Pricing (as of Oct 2024)
PRICING = {
    "claude-opus-4.1": {
        "input": 15.00 / 1_000_000,   # $15 per 1M tokens
        "output": 75.00 / 1_000_000   # $75 per 1M tokens
    },
    "claude-sonnet-4.5": {
        "input": 3.00 / 1_000_000,    # $3 per 1M tokens
        "output": 15.00 / 1_000_000   # $15 per 1M tokens
    },
    "claude-haiku-4": {
        "input": 0.25 / 1_000_000,    # $0.25 per 1M tokens
        "output": 1.25 / 1_000_000    # $1.25 per 1M tokens
    }
}

def calculate_cost(model: str, input_tokens: int, output_tokens: int):
    pricing = PRICING[model]
    return (input_tokens * pricing['input']) + (output_tokens * pricing['output'])
```

### 2. Latency Metrics

- **Time to first token** (TTFT)
- **Total completion time**
- Measured in milliseconds

### 3. Accuracy Metrics

From LLM judge:
- **Accuracy score** (0-10)
- **Relevance score** (0-10)
- **Reasoning quality** (0-10)
- **Actionability** (0-10)
- **Total score** (0-40)

### 4. Business Metrics

```python
# At scale (50,000 NBAs/day)
def calculate_annual_savings(test_results):
    baseline = test_results['T1']  # Natural Language + Opus
    winner = test_results['T5']     # CLM + Sonnet
    
    requests_per_day = 50_000
    requests_per_year = requests_per_day * 365
    
    baseline_cost_per_request = baseline['cost_dollars']
    winner_cost_per_request = winner['cost_dollars']
    
    annual_baseline_cost = baseline_cost_per_request * requests_per_year
    annual_winner_cost = winner_cost_per_request * requests_per_year
    
    annual_savings = annual_baseline_cost - annual_winner_cost
    
    return {
        'annual_baseline_cost': annual_baseline_cost,
        'annual_winner_cost': annual_winner_cost,
        'annual_savings': annual_savings,
        'savings_percentage': (annual_savings / annual_baseline_cost) * 100
    }
```

---

## 📈 Expected Results

### Hypothesis

| Test | Input | Model | Est. Cost/Req | Est. Latency | Est. Accuracy |
|------|-------|-------|---------------|--------------|---------------|
| T1 | Natural | Opus 4.1 | $0.0615 | 2.5s | 95% |
| T2 | Natural | Sonnet 4.5 | $0.0123 | 1.8s | 90% |
| T3 | Natural | Haiku 4 | $0.0010 | 0.8s | 75% |
| T4 | **CLM** | Opus 4.1 | **$0.0034** | 0.6s | 97% |
| T5 | **CLM** | Sonnet 4.5 | **$0.0007** | 0.4s | 95% |
| T6 | **CLM** | Haiku 4 | **$0.0001** | 0.2s | 85% |

### Key Insights

**If T5 (CLM + Sonnet) ≥ T1 (Natural + Opus):**
- ✅ Same or better accuracy
- ✅ 94.5% cost reduction ($0.0615 → $0.0007)
- ✅ 84% latency reduction (2.5s → 0.4s)
- ✅ Annual savings: **$1.1M+** (at 50K requests/day)

**Winner Scenario:**
> "CLM-compressed transcripts on Sonnet 4.5 deliver the same accuracy as natural language on Opus 4.1, at 1/88th the cost and 6x faster."

---

## 🚀 Implementation Timeline

### Week 1: Setup (Days 1-5)

**Day 1-2: Data Collection**
- [ ] Collect 20 real customer transcripts
- [ ] Get NBA catalog from Salesforce
- [ ] Create ground truth annotations (with QA team)

**Day 3: Compression Pipeline**
- [ ] Compress all 20 transcripts using CLM
- [ ] Compress NBA catalog
- [ ] Validate compression quality (spot check)

**Day 4: Test Harness**
- [ ] Build test execution script
- [ ] Set up API calls to all 3 models
- [ ] Build cost/latency tracking

**Day 5: LLM Judge Setup**
- [ ] Create judge prompt template
- [ ] Test judge on sample cases
- [ ] Validate judge consistency

### Week 2: Execution (Days 6-10)

**Day 6-7: Run Tests**
- [ ] Execute all 6 test configurations (T1-T6)
- [ ] Run on all 20 transcripts
- [ ] Total: 120 test runs (6 configs × 20 transcripts)

**Day 8: Judge Evaluation**
- [ ] Run LLM judge on all pairs
- [ ] Compare T1 vs T5 (primary comparison)
- [ ] Compare T2 vs T5, T3 vs T6 (secondary)

**Day 9: Analysis**
- [ ] Calculate aggregate metrics
- [ ] Generate comparison charts
- [ ] Calculate annual savings projections

**Day 10: Report**
- [ ] Create executive summary
- [ ] Build presentation deck
- [ ] Prepare demo for stakeholders

---

## 📋 Test Execution Checklist

### Pre-Test
- [ ] 20 customer transcripts collected
- [ ] NBA catalog exported from Salesforce
- [ ] Ground truth annotations completed
- [ ] All transcripts compressed and validated
- [ ] NBA catalog compressed
- [ ] Test harness code written and tested
- [ ] LLM judge prompt finalized
- [ ] API keys configured for all 3 models

### During Test
- [ ] Log all API calls
- [ ] Track token counts (input + output)
- [ ] Measure latency for each call
- [ ] Store all raw responses
- [ ] Handle API errors gracefully
- [ ] Monitor rate limits

### Post-Test
- [ ] All 120 tests completed successfully
- [ ] Judge evaluations complete
- [ ] Metrics calculated and validated
- [ ] Results analyzed and documented
- [ ] Presentation prepared

---

## 🎯 Success Criteria

### Must-Have Results

1. **Accuracy Maintained**
   - CLM + Sonnet scores ≥ 90% of Natural + Opus score
   - LLM judge confirms CLM quality

2. **Cost Reduction Proven**
   - CLM shows >80% cost reduction
   - Projected annual savings calculated

3. **Latency Improvement Shown**
   - CLM faster than natural language
   - Acceptable for real-time agent guidance

### Nice-to-Have Results

1. **CLM + Haiku Competitive**
   - If Haiku with CLM ≥ Sonnet without CLM
   - Opens door to even cheaper deployment

2. **CLM Improves Model Performance**
   - CLM + Model X > Natural + Model X
   - Shows CLM adds signal, not just compression

---

## 📊 Reporting Template

### Executive Summary Format

```markdown
# CLM vs Natural Language NBA Test Results

## Key Findings

**Winner: CLM-Compressed Transcripts on Claude Sonnet 4.5**

- ✅ Accuracy: 95% (same as Natural Language on Opus 4.1)
- ✅ Cost: $0.0007/request (94.5% reduction vs baseline)
- ✅ Latency: 0.4s (84% faster than baseline)
- ✅ Annual Savings: $1.1M (at 50,000 requests/day)

## Test Matrix Results

[Insert comparison table]

## LLM Judge Evaluation

[Insert judge scores and winner analysis]

## Recommendation

Deploy CLM transcript compression for NBA feature using Claude Sonnet 4.5.
ROI: Savings within 2 days of deployment.
```

---

## 🔧 Code Templates

### Test Execution Script

```python
import time
import json
from anthropic import Anthropic

class NBATestHarness:
    def __init__(self):
        self.client = Anthropic(api_key="...")
        self.results = []
    
    def run_all_tests(self, transcripts, nba_catalog, ground_truths):
        """Run all 6 test configurations on all transcripts"""
        
        test_configs = [
            ('T1', 'natural', 'claude-opus-4.1'),
            ('T2', 'natural', 'claude-sonnet-4.5'),
            ('T3', 'natural', 'claude-haiku-4'),
            ('T4', 'clm', 'claude-opus-4.1'),
            ('T5', 'clm', 'claude-sonnet-4.5'),
            ('T6', 'clm', 'claude-haiku-4'),
        ]
        
        for transcript_id, transcript in transcripts.items():
            for test_id, input_format, model in test_configs:
                result = self.run_single_test(
                    test_id=test_id,
                    transcript_id=transcript_id,
                    transcript=transcript,
                    nba_catalog=nba_catalog,
                    input_format=input_format,
                    model=model,
                    ground_truth=ground_truths[transcript_id]
                )
                self.results.append(result)
                print(f"✓ Completed {test_id} for {transcript_id}")
        
        return self.results
    
    def run_single_test(self, test_id, transcript_id, transcript, 
                       nba_catalog, input_format, model, ground_truth):
        """Run single test case"""
        # [Implementation from earlier]
        pass
    
    def judge_results(self, results):
        """Use LLM judge to evaluate results"""
        # [Implementation from earlier]
        pass
    
    def generate_report(self, results, judgments):
        """Generate executive summary"""
        # [Implementation from earlier]
        pass
```

---

## 💡 Key Insights to Prove

### Primary Insight
> "CLM enables us to use cheaper models with the same quality as expensive models with natural language."

### Supporting Insights

1. **Token Efficiency = Cost Efficiency**
   - 94.5% token reduction = 94.5% cost reduction
   - Same information, compressed representation

2. **Structured Data Helps LLMs**
   - CLM provides structure LLMs understand natively
   - JSON-like format matches training data
   - May actually IMPROVE accuracy vs prose

3. **Latency Wins Are Bonus**
   - Fewer tokens = faster processing
   - Faster = better agent experience
   - Enables real-time use cases

4. **Scale Amplifies Savings**
   - Every request saves $0.06
   - 50,000 requests/day = $3,000/day savings
   - $1.1M/year savings on NBA feature alone

---

## 🎯 Next Steps After Tests

### If Results Positive (T5 ≥ T1)

1. **Week 3: Production Pilot**
   - Deploy CLM for 1% of NBA requests
   - Monitor quality in production
   - Validate cost savings

2. **Week 4: Ramp Up**
   - Increase to 10% of requests
   - Continue monitoring
   - Prepare for full rollout

3. **Month 2: Full Deployment**
   - 100% of NBA requests use CLM
   - Measure actual savings
   - Expand to other features

### If Results Need Iteration

1. **Identify Gaps**
   - Which test cases failed?
   - What patterns are missed?

2. **Enhance Compression**
   - Add missing semantic tokens
   - Refine NBA catalog compression

3. **Re-test**
   - Run focused tests on problem areas
   - Validate improvements

---

## 📞 Stakeholder Communication

### Daily Updates (Week of Testing)
```
Day X Update:
- Tests completed: X/120
- Issues encountered: [list]
- Early observations: [insights]
- On track for: [date]
```

### Final Report (End of Week 2)
```
CLM NBA Test Results - Executive Summary

RESULT: [Winner announcement]

METRICS:
- Accuracy: [score]
- Cost Reduction: [percentage]
- Latency Improvement: [percentage]
- Annual Savings: [dollar amount]

RECOMMENDATION: [Deploy/Iterate/Stop]

NEXT STEPS: [Action items]
```
