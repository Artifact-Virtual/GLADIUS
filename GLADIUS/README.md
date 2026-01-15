---
license: apache-2.0
language:
- en
tags:
- gladius
- artifact-virtual
- tool-routing
- custom-weights
- knowledge-distillation
pipeline_tag: text-generation
model-index:
- name: Gladius
  results: []
---

# GLADIUS

## Model Description

GLADIUS is a decoder-only transformer language model trained via knowledge distillation from multiple expert teacher models. The model uses randomly initialized weights (not fine-tuned from a pretrained model) and learns from Qwen and TinyLlama teachers.

**Current Build:** Development (incomplete training)

---

## Technical Specifications

| Parameter | Value |
|-----------|-------|
| Architecture | LlamaForCausalLM |
| Parameters | 124,668,672 |
| Hidden Size | 768 |
| Intermediate Size | 2048 |
| Layers | 12 |
| Attention Heads | 12 |
| KV Heads | 4 (GQA) |
| Vocabulary | 32,000 |
| Max Position | 2,048 |
| Precision | float32 |
| File Format | SafeTensors |
| File Size | 475.57 MB |

---

## Architecture Details

```
Embedding:        32,000 × 768 = 24,576,000 params
LM Head:          768 × 32,000 = 24,576,000 params
12 Layers × 6.29M = 75,516,672 params
Total:            124,668,672 params
```

**Per-Layer Components:**
- Self-Attention: Q (768×768), K (256×768), V (256×768), O (768×768)
- MLP: Gate (2048×768), Up (2048×768), Down (768×2048)
- Normalization: Pre-attention RMSNorm, Post-attention RMSNorm

**Features:**
- Grouped Query Attention (3:1 ratio)
- SwiGLU activation (SiLU)
- RoPE positional embeddings (θ=10000)
- RMSNorm (ε=1e-6)

---

## Training Status

| Metric | Value |
|--------|-------|
| Status | In Progress |
| Phase | 2 of 4 |
| Steps Completed | 380 |
| Current Loss | 61.39 |
| Initial Loss | 128.58 |
| Loss Reduction | 52.3% |

**Expert Teachers:**
1. Qwen/Qwen2.5-1.5B-Instruct (in progress)
2. TinyLlama/TinyLlama-1.1B-Chat-v1.0 (pending)

---

## Usage

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("amuzetnoM/Gladius")
tokenizer = AutoTokenizer.from_pretrained("amuzetnoM/Gladius")

inputs = tokenizer("Hello, how are you?", return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=50)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

---

## Limitations

1. Training is incomplete (380/2000 steps)
2. Output quality is limited due to early training stage
3. No safety fine-tuning or RLHF applied
4. Not suitable for production use
5. May produce incoherent or repetitive output

---

## Files

| File | Size | Description |
|------|------|-------------|
| model.safetensors | 475.57 MB | Model weights |
| config.json | 668 B | Architecture configuration |
| tokenizer.json | 3.6 MB | Tokenizer vocabulary |
| tokenizer_config.json | 951 B | Tokenizer settings |
| special_tokens_map.json | 551 B | Special token definitions |
| generation_config.json | 133 B | Generation defaults |

---

## Checksum

```
model.safetensors SHA-256:
9f54bcd00193a6c4d340d2ba0857092856730814b60c305842a3c878bb572ade
```

---

## License

Apache 2.0

---

## Citation

```bibtex
@misc{gladius2026,
  title={GLADIUS: Multi-Expert Knowledge Distillation Model},
  author={Artifact Virtual},
  year={2026},
  publisher={HuggingFace},
  url={https://huggingface.co/amuzetnoM/Gladius}
}
```
