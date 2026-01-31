# GLADIUS 1.1:125M

> **The Native AI of Artifact Virtual**

## Overview

GLADIUS is a native decoder-only transformer language model built from scratch with custom initialized weights. It uses knowledge distillation from expert teacher models and exports directly to GGUF for llama.cpp inference.

**Version:** 1.1:125M (125 million parameters)  
**Status:** Development  
**Format:** Native GGUF (llama.cpp compatible)

---

## Technical Specifications

| Parameter | Value |
|-----------|-------|
| Architecture | LlamaForCausalLM |
| Parameters | 124,668,672 (~125M) |
| Hidden Size | 768 |
| Intermediate Size | 2048 |
| Layers | 12 |
| Attention Heads | 12 |
| KV Heads | 4 (GQA) |
| Vocabulary | 32,000 |
| Max Position | 2,048 |
| Precision | float32 → GGUF Q4_K_M |
| Native Format | GGUF |

---

## Architecture

```
┌────────────────────────────────────────────────────┐
│  GLADIUS 1.1:125M ARCHITECTURE                     │
├────────────────────────────────────────────────────┤
│  Embedding:     32,000 × 768 = 24.6M params        │
│  12 Layers:     12 × 6.29M = 75.5M params          │
│  LM Head:       768 × 32,000 = 24.6M params        │
│  Total:         124,668,672 params                 │
└────────────────────────────────────────────────────┘
```

**Features:**
- Grouped Query Attention (3:1 ratio)
- SwiGLU activation (SiLU)
- RoPE positional embeddings (θ=10000)
- RMSNorm (ε=1e-6)

---

## Usage

### With llama.cpp (Primary)

```bash
# Run with llama.cpp server
./llama-server -m gladius-1.1-125M-q4_k_m.gguf -c 2048

# Query
curl http://localhost:8080/completion -d '{"prompt": "Hello"}'
```

### With Python (Development)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("amuzetnoM/Gladius")
tokenizer = AutoTokenizer.from_pretrained("amuzetnoM/Gladius")

inputs = tokenizer("Route this query: search for gold", return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=50)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

---

## Training

```bash
# Start training (auto-detects GPU/CPU)
cd GLADIUS
python training/gladius_trainer.py --epochs 10

# Resume from checkpoint
python training/gladius_trainer.py --resume

# Export to GGUF
python training/gladius_trainer.py --export-gguf
```

---

## Directory Structure

```
GLADIUS/
├── training/           # Training code
│   └── gladius_trainer.py  # Unified CPU/GPU trainer
├── models/             # Model outputs
│   ├── checkpoints/    # Training checkpoints
│   └── gladius_primary/# Production model
├── router/             # Inference routing
├── tools/              # GGUF export tools
│   └── llama.cpp/      # llama.cpp binaries
├── docs/               # Architecture docs
└── tmp/                # Cache (gitignored)
```

---

## Files

| File | Description |
|------|-------------|
| gladius-1.1-125M.gguf | Native GGUF model |
| model.safetensors | HuggingFace weights |
| config.json | Architecture config |
| tokenizer.json | Tokenizer vocabulary |

---

## License

Apache 2.0

---

## Citation

```bibtex
@misc{gladius2026,
  title={GLADIUS: Native AI Model for Artifact Virtual},
  author={Artifact Virtual},
  year={2026},
  url={https://huggingface.co/amuzetnoM/Gladius}
}
```
