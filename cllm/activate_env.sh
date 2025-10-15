#!/bin/bash
# Activation script for CLLM project virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated!"
echo "📦 Installed packages: torch, transformers, accelerate, numpy"
echo "🚀 You can now run: python src/model_core/cllm_model.py"