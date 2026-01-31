# GLADIUS Native Architecture

> **Version**: 1.1  
> **Architecture**: Native Transformer (GLADIUS-LM)  
> **License**: Proprietary - Artifact Virtual Enterprise  
> **Last Updated**: 2026-01-31

## Overview

GLADIUS is a **100% native language model** built from scratch for Artifact Virtual Enterprise. Unlike fine-tuned derivatives of existing models, GLADIUS uses a custom architecture trained entirely on proprietary data.

```
┌─────────────────────────────────────────────────────────────────┐
│                    GLADIUS NATIVE ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Input Embeddings                      │   │
│  │                  vocab_size × hidden_size                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Transformer Blocks × N                      │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │  RMSNorm → GQA Attention (RoPE) → Residual      │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │  RMSNorm → SwiGLU MLP → Residual                │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                      RMSNorm                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   LM Head (Linear)                       │   │
│  │                hidden_size → vocab_size                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Model Variants

| Variant | Parameters | Hidden | Layers | Heads | KV Heads | Context | GGUF Size |
|---------|------------|--------|--------|-------|----------|---------|-----------|
| gladius1.1:24M  | ~24M  | 256  | 6  | 4  | 2 | 2048 | ~49 MB |
| gladius1.1:71M  | ~71M  | 512  | 12 | 8  | 4 | 2048 | ~140 MB |
| gladius1.1:150M | ~150M | 768  | 16 | 12 | 4 | 4096 | ~300 MB |
| gladius1.1:500M | ~500M | 1024 | 24 | 16 | 4 | 4096 | ~1 GB |

## Core Components

### 1. RMSNorm (Root Mean Square Normalization)

```python
class RMSNorm:
    """
    Simplified layer normalization without mean centering.
    More stable and efficient than LayerNorm.
    
    x_norm = x * rsqrt(mean(x²) + ε) * weight
    """
    eps: float = 1e-6
```

**Why RMSNorm?**
- 15% faster than LayerNorm
- Equivalent or better training stability
- Used by Llama, Qwen, and modern architectures

### 2. Rotary Position Embedding (RoPE)

```python
class RotaryEmbedding:
    """
    Relative positional encoding via rotation matrices.
    Encodes position information directly into attention.
    
    q_rotated = q * cos(θ) + rotate_half(q) * sin(θ)
    k_rotated = k * cos(θ) + rotate_half(k) * sin(θ)
    """
    theta: float = 10000.0
    max_seq_len: int = 2048
```

**Why RoPE?**
- Enables length extrapolation
- Better relative position encoding
- No learned parameters (efficient)

### 3. Grouped Query Attention (GQA)

```python
class GladiusAttention:
    """
    Multi-head attention with grouped key-value heads.
    Reduces memory while maintaining quality.
    
    Q: num_attention_heads
    K,V: num_key_value_heads (shared across groups)
    """
    num_heads: int = 8
    num_kv_heads: int = 4  # 2:1 ratio
```

**Why GQA?**
- 2x memory reduction vs MHA
- Minimal quality loss
- Faster inference

### 4. SwiGLU MLP

```python
class GladiusMLP:
    """
    Gated Linear Unit with Swish activation.
    
    output = down_proj(silu(gate_proj(x)) * up_proj(x))
    """
    intermediate_size: int  # ~2.75× hidden_size
```

**Why SwiGLU?**
- Superior to ReLU/GELU
- Better gradient flow
- Used by modern LLMs

## Configuration Schema

```json
{
  "architecture": "gladius",
  "vocab_size": 32000,
  "hidden_size": 512,
  "intermediate_size": 1408,
  "num_hidden_layers": 12,
  "num_attention_heads": 8,
  "num_key_value_heads": 4,
  "max_position_embeddings": 2048,
  "rope_theta": 10000.0,
  "rms_norm_eps": 1e-6,
  "tie_word_embeddings": false
}
```

## Training Specifications

### Data Format
```jsonl
{"text": "<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_input}<|im_end|>\n<|im_start|>assistant\n{response}<|im_end|>"}
```

### Training Hyperparameters
| Parameter | Value |
|-----------|-------|
| Optimizer | AdamW |
| Learning Rate | 1e-4 |
| Weight Decay | 0.01 |
| Batch Size | 2-8 (CPU) / 32-64 (GPU) |
| Gradient Clipping | 1.0 |
| Warmup Steps | 100 |
| Max Sequence Length | 256-2048 |

### Hardware Requirements

| Variant | Training (CPU) | Training (GPU) | Inference |
|---------|----------------|----------------|-----------|
| 24M  | 4GB RAM, 1hr   | 2GB VRAM, 5min | 1GB RAM |
| 71M  | 8GB RAM, 4hr   | 4GB VRAM, 20min | 2GB RAM |
| 150M | 16GB RAM, 12hr | 8GB VRAM, 1hr | 4GB RAM |
| 500M | 32GB RAM, 48hr | 16GB VRAM, 4hr | 8GB RAM |

## GGUF Format

GLADIUS models are distributed in GGUF format for efficient inference:

```
GGUF Header
├── Magic: 0x46554747 ("GGUF")
├── Version: 3
├── Tensor Count
└── Metadata Count

Metadata
├── general.architecture: "gladius"
├── general.name: "GLADIUS Native"
├── gladius.context_length
├── gladius.embedding_length
├── gladius.block_count
├── gladius.attention.head_count
├── gladius.attention.head_count_kv
└── gladius.rope.freq_base

Tensor Data (F16)
├── embed_tokens.weight
├── layers.{n}.input_layernorm.weight
├── layers.{n}.attn.q_proj.weight
├── layers.{n}.attn.k_proj.weight
├── layers.{n}.attn.v_proj.weight
├── layers.{n}.attn.o_proj.weight
├── layers.{n}.post_attention_layernorm.weight
├── layers.{n}.mlp.gate_proj.weight
├── layers.{n}.mlp.up_proj.weight
├── layers.{n}.mlp.down_proj.weight
├── norm.weight
└── lm_head.weight
```

## Tokenizer

GLADIUS uses a simple tokenizer optimized for tool-calling:

### Special Tokens
| Token | ID | Purpose |
|-------|-----|---------|
| `<pad>` | 0 | Padding |
| `<unk>` | 1 | Unknown |
| `<eos>` | 2 | End of sequence |
| `<bos>` | 3 | Beginning of sequence |
| `<\|im_start\|>` | 4 | Message start |
| `<\|im_end\|>` | 5 | Message end |

### Vocabulary
- Base: ASCII printable characters (95 tokens)
- Common words: Tool-calling vocabulary
- Total: 32,000 tokens (expandable)

## Inference

### With llama.cpp
```bash
./main -m gladius1.1-71M.gguf -p "What tools do you have?" -n 100
```

### With Ollama
```bash
ollama create gladius1.1:71M -f Modelfile
ollama run gladius1.1:71M
```

### Native Python
```python
from gladius import GladiusModel, GladiusConfig, SimpleTokenizer

config = GladiusConfig.for_size(71)
model = GladiusModel(config)
model.load_state_dict(torch.load("model.pt"))

tokenizer = SimpleTokenizer.load("tokenizer.json")
input_ids = torch.tensor([tokenizer.encode("Hello")])
output = model.generate(input_ids, max_new_tokens=50)
print(tokenizer.decode(output[0].tolist()))
```

## Comparison to Third-Party Models

| Feature | GLADIUS Native | Qwen2.5-0.5B | Llama-3.2-1B |
|---------|----------------|--------------|--------------|
| Architecture | Custom | Qwen | Llama |
| License | Proprietary | Apache 2.0 | Llama License |
| Third-party deps | None | HuggingFace | HuggingFace |
| Training data | Proprietary | Public | Public |
| Tool-calling | Native | Fine-tuned | Fine-tuned |
| Artifact integration | Native | Adapter | Adapter |

## File Inventory

```
GLADIUS/models/native/
├── gladius1.1-24M.gguf        # Small model (test/edge)
├── gladius1.1-71M.gguf        # Default model
├── gladius1.1-150M.gguf       # Enhanced model
├── gladius_native_final/
│   ├── model.pt               # PyTorch weights
│   ├── config.json            # Architecture config
│   └── tokenizer.json         # Tokenizer vocab
└── checkpoints/
    └── gladius_native_epoch{N}.pt
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-01-31 | Native architecture, removed Qwen dependency |
| 1.0 | 2026-01-14 | Initial release (Qwen-based) |

---

**© 2026 Artifact Virtual Enterprise. All rights reserved.**
