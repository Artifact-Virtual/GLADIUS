---
license: apache-2.0
language:
- en
tags:
- gladius
- artifact-virtual
- tool-routing
- enterprise-ai
- custom-weights
pipeline_tag: text-generation
model-index:
- name: Gladius
  results: []
---

# GLADIUS: NATIVE

<div align="center">

**⚔️ Built from Ground Up ⚔️**

*A **1 billion** parameter model trained via multi-expert knowledge distillation*

[![Artifact Virtual](https://img.shields.io/badge/Artifact-ML-indigo)](https://github.com/Artifact-ML)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)

</div>

---

## Overview

GLADIUS is the native AI model powering Artifact Virtual's enterprise infrastructure. Unlike fine-tuned models, GLADIUS is **built from scratch with our own initialized weights** using knowledge distillation from multiple expert teachers.

### Key Differentiators

| Feature | GLADIUS | Typical Fine-tuned Models |
|---------|---------|---------------------------|
| Weight Initialization | **Random (Ours)** | Pretrained weights |
| Architecture | **Custom 1B design** | Fixed from base model |
| Training Method | **Multi-expert distillation** | Single-model fine-tuning |
| Capabilities | **Hybrid strengths** | Single-model characteristics |

---

## Model Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     GLADIUS 1B ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────────┤
│  Hidden Size:           2048                                    │
│  Intermediate Size:     5632 (~2.75x hidden)                   │
│  Layers:               24                                       │
│  Attention Heads:       16 (with GQA: 4 KV heads)              │
│  Vocab Size:            32000                                   │
│  Max Context:           8192 tokens                             │
│  RoPE Theta:            10000                                   │
│  Total Parameters:      ~1,000,000,000                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Expert Teachers

GLADIUS absorbs capabilities from 6 diverse expert models:

| Expert | Model | Strengths | Contribution Weight |
|--------|-------|-----------|---------------------|
| **Qwen** | Qwen2.5-1.5B-Instruct | Tool-calling, JSON, multilingual | 1.5 |
| **Llama** | Llama-3.2-1B-Instruct | Reasoning, English fluency | 1.3 |
| **Phi** | Phi-2 | Math, code, logic | 1.2 |
| **Gemma** | Gemma-2-2b-it | Safety, web knowledge | 1.0 |
| **Mistral** | Mistral-7B-Instruct | Speed, sliding window | 0.8 |
| **TinyLlama** | TinyLlama-1.1B | Fast inference | 0.6 |

---

## Training Methodology

### Phase 1: Architecture Initialization
- Custom LlamaForCausalLM configuration
- Random weight initialization (our weights)
- Grouped Query Attention (GQA) for efficiency

### Phase 2: Expert Distillation
- Each expert teaches specific capabilities
- KL-divergence loss for soft-label learning
- Weighted ensemble combining

### Phase 3: Progressive Scaling
- Gradual capability expansion
- Continuous evaluation against benchmarks
- Self-improvement loops

### Phase 4: GGUF Export
- Quantization for deployment (Q4_K_M, Q8_0)
- Optimized for llama.cpp inference
- <5ms routing latency target

---

## Primary Use Cases

1. **Tool Routing** - Selecting the right tool for any query (<2ms)
2. **Task Execution** - Complex multi-step operations
3. **Research Analysis** - Market intelligence and synthesis
4. **Enterprise Integration** - ERP, CRM, database operations

---

## Current Status

| Metric | Value | Target |
|--------|-------|--------|
| Parameter Count | Training... | 1B |
| Tool Routing Accuracy | 100% (pattern) | 100% |
| Average Latency | 0.93ms | <5ms |
| Training Data | 914+ examples | 100K+ |

---

## Usage

### With Transformers

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("amuzetnoM/Gladius")
tokenizer = AutoTokenizer.from_pretrained("amuzetnoM/Gladius")

prompt = "Route this to the correct tool: Search for gold price analysis"
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=50)
print(tokenizer.decode(outputs[0]))
```

### With llama.cpp (GGUF)

```bash
./main -m gladius-1b-q4_k_m.gguf -p "Your prompt here" -n 256
```

---

## Repository Structure

```
Gladius/
├── models/                  # Trained model weights
│   ├── gladius_primary/    # Primary 1B model
│   └── checkpoints/        # Training checkpoints
├── training/               # Training infrastructure
│   ├── data/               # Training datasets
│   └── scripts/            # Training scripts
├── router/                 # Inference routing
└── docs/                   # Documentation
```

---

## Training Requirements

- **GPU**: NVIDIA GPU with 16GB+ VRAM (24GB recommended)
- **CPU Fallback**: Available but significantly slower
- **Storage**: 100GB+ for model cache and checkpoints
- **RAM**: 32GB+ recommended

---

## License

Apache 2.0 - See [LICENSE](LICENSE) for details.

---

## About Artifact Virtual

GLADIUS is developed by [Artifact Virtual](https://github.com/Artifact-Virtual), an enterprise AI infrastructure company building autonomous business systems.

**Core Components:**
- **GLADIUS** - Native AI model (this repository)
- **SENTINEL** - Guardian monitoring and security
- **LEGION** - Enterprise orchestration
- **SYNDICATE** - Asset research pipeline

---

## Citation

```bibtex
@misc{gladius2026,
  title={GLADIUS: Multi-Expert Knowledge Distillation for Enterprise AI},
  author={Artifact Virtual},
  year={2026},
  publisher={HuggingFace},
  url={https://huggingface.co/amuzetnoM/Gladius}
}
```
