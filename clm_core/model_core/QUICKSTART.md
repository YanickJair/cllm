# CLLM Model Core: Quick Start

**Get started in 30 minutes.**

---

## Prerequisites

```bash
# Check you have these
python --version  # 3.9+
pip list | grep torch  # 2.0+
pip list | grep transformers  # 4.30+
nvidia-smi  # GPU check (optional for testing)
```

Install if needed:
```bash
pip install torch transformers datasets accelerate
pip install spacy && python -m spacy download en_core_web_sm
```

---

## Step 1: Generate Training Data (5 min)

```bash
# Generate 10K training examples
python generate_training_data.py
```

**Expected output:**
```
🚀 CLLM MODEL CORE - TRAINING DATA GENERATION
✅ Created 10000 training examples
💾 Saved to cllm_training_data.jsonl
💾 Saved to cllm_token_vocab.json
```

**Verify:**
```bash
wc -l cllm_training_data.jsonl  # Should show 10000
head -1 cllm_training_data.jsonl  # Check format
```

---

## Step 2: Test Model Architecture (5 min)

```bash
# Test CLLM model (uses tiny model for testing)
python cllm_model.py
```

**Expected output:**
```
🔧 Initializing CLLM Model...
✅ Loaded 200 CLLM tokens
✅ CLLM Model initialized
🧪 TESTING CLLM MODEL
Generated Response: [some text]
✅ Test complete!
```

If this works, architecture is good! ✅

---

## Step 3: Choose Your Path

### Path A: Quick Test (No GPU, 10 min)

Test training loop without actually training:

```bash
python train_cllm_model.py --dry_run
```

This validates everything works without spending GPU time.

### Path B: GPU Training (Requires GPU)

**Option 1: Local GPU**
```bash
python train_cllm_model.py \
    --num_epochs 1 \
    --batch_size 2 \
    --max_samples 100
```

**Option 2: Cloud GPU (Lambda Labs)**
```bash
# SSH into Lambda instance
ssh ubuntu@<instance-ip>

# Clone your repo
git clone <your-repo>
cd <your-repo>

# Install deps
pip install -r requirements.txt

# Train!
python train_cllm_model.py
```

---

## Step 4: Evaluate Results (5 min)

```bash
# Test the trained model
python evaluate_cllm_model.py
```

Check if model:
- ✅ Understands [REQ:ANALYZE]
- ✅ Processes [TARGET:CODE]
- ✅ Generates sensible outputs

---

## Common Issues

### Issue: Out of Memory

**Solution:**
```bash
# Reduce batch size
python train_cllm_model.py --batch_size 1

# Or use gradient checkpointing
python train_cllm_model.py --gradient_checkpointing
```

### Issue: Model downloads fail

**Solution:**
```bash
# Download model first
huggingface-cli login
huggingface-cli download meta-llama/Llama-2-7b-hf
```

### Issue: Training too slow

**Solution:**
```bash
# Use smaller model for testing
python train_cllm_model.py --base_model "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
```

---

## Quick Architecture Test (No Training Needed)

Want to see if CLLM tokens work? Run this:

```python
from cllm_model import CLLMModel, CLLMConfig

# Initialize (downloads base model, ~14GB)
config = CLLMConfig(base_model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0")
model = CLLMModel(config)

# Test with CLLM tokens
response = model.generate(
    cllm_instruction="[REQ:ANALYZE] [TARGET:CODE]",
    data="def foo(): return 42",
    max_new_tokens=50
)

print(response)
# Output will be random (untrained) but proves architecture works!
```

---

## Next Steps

**If everything works:**
1. ✅ You're ready for full training
2. ✅ Get GPU access (Lambda/RunPod)
3. ✅ Run `train_cllm_model.py` for 3-7 days
4. ✅ Deploy and profit!

**If you hit issues:**
1. Check GPU: `nvidia-smi`
2. Check disk space: `df -h`
3. Check memory: `free -h`
4. Open GitHub issue with error log

---

## Minimal Training Test

Want to train for real but not spend much time/money?

```bash
# 1-hour training test ($1 on Lambda)
python train_cllm_model.py \
    --base_model "TinyLlama/TinyLlama-1.1B-Chat-v1.0" \
    --num_epochs 1 \
    --batch_size 4 \
    --max_samples 1000 \
    --output_dir "./test_checkpoint"
```

**Cost:** ~$1 on cloud GPU
**Time:** ~1 hour
**Purpose:** Validate full pipeline works

---

## GPU Requirements by Model

| Model | VRAM | Training Time | Cost (Lambda) |
|-------|------|---------------|---------------|
| TinyLlama-1.1B | 8GB | 2 days | $50 |
| LLaMA-2-7B | 24GB | 5 days | $200 |
| Mistral-7B | 24GB | 5 days | $200 |
| LLaMA-2-13B | 40GB | 10 days | $500 |

**Recommendation:** Start with TinyLlama for testing, then LLaMA-2-7B for production.

---

## Debugging Checklist

Before asking for help:

```bash
# 1. Check Python version
python --version  # Should be 3.9+

# 2. Check PyTorch
python -c "import torch; print(torch.__version__)"  # 2.0+

# 3. Check GPU
python -c "import torch; print(torch.cuda.is_available())"  # True

# 4. Check training data exists
ls -lh cllm_training_data.jsonl

# 5. Check model downloads
ls -lh ~/.cache/huggingface/hub/

# 6. Test imports
python -c "from cllm_model import CLLMModel; print('OK')"
```

---

## What Success Looks Like

After training, your model should:

```python
# Input: Compressed instruction
model.generate("[REQ:ANALYZE] [TARGET:CODE]", "def foo(): return 42")

# Output: Analysis (not random!)
# "This function named 'foo' returns the integer value 42. It's a simple..."
```

**Key test:** Output should be relevant to the instruction, not random text.

---

## Ready to Start?

```bash
# Clone/navigate to your CLLM project
cd clm_core-project

# Run data generation
python generate_training_data.py

# Test architecture
python cllm_model.py

# If both work: YOU'RE READY! 🚀
```

**Questions?** Check the full build plan: `CLLM_MODEL_CORE_BUILD_PLAN.md`

**Let's build this thing.** 💪