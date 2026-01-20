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
pipeline_tag: reinforcement-learning
model-index:
- name: Gladius
  results: []
---

<div align="center">

*A **1 billion** parameter model trained via multi-expert knowledge distillation*

[![Artifact Virtual](https://img.shields.io/badge/ARTIFACT-ML-indigo)](https://github.com/Artifact-ML)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)

**GROUND ZERO**

</div>

---
# GLADIUS: NATIVE

**Document Version:** 2.0.0  
**Date:** 2026-01-15  
**Status:** Development Build  

---

## Table of Contents

1. [Overview](#1-overview)
2. [Model Architecture](#2-model-architecture)
3. [Safetensors Analysis](#3-safetensors-analysis)
4. [Training Methodology](#4-training-methodology)
5. [Training Progress](#5-training-progress)
6. [File Structure](#6-file-structure)
7. [Usage Instructions](#7-usage-instructions)
8. [Limitations](#8-limitations)
9. [Checksums](#9-checksums)
10. [Appendix](#10-appendix)

---

## 1. Overview

GLADIUS is a decoder-only transformer language model trained via knowledge distillation from multiple expert teacher models. This document provides exhaustive technical details for the current development build.

### 1.1 Model Identification

| Field | Value |
|-------|-------|
| Model Name | GLADIUS-125M-v1 |
| Model ID | `amuzetnoM/Gladius` |
| Architecture | LlamaForCausalLM |
| Framework | PyTorch + Transformers |
| Precision | float32 |
| File Format | SafeTensors |

### 1.2 Current Status

| Metric | Value |
|--------|-------|
| Training Status | In Progress |
| Training Phase | 2 of 4 (Qwen distillation) |
| Current Step | 380 |
| Experts Completed | 0/2 (qwen in progress) |
| Current Loss | 61.39 |
| Initial Loss | 128.58 |
| Loss Reduction | 52.3% |

---

## 2. Model Architecture

### 2.1 Configuration Parameters

```json
{
  "architectures": ["LlamaForCausalLM"],
  "model_type": "llama",
  "hidden_size": 768,
  "intermediate_size": 2048,
  "num_hidden_layers": 12,
  "num_attention_heads": 12,
  "num_key_value_heads": 4,
  "head_dim": 64,
  "vocab_size": 32000,
  "max_position_embeddings": 2048,
  "hidden_act": "silu",
  "rms_norm_eps": 1e-06,
  "rope_theta": 10000.0,
  "rope_scaling": null,
  "attention_bias": false,
  "attention_dropout": 0.0,
  "mlp_bias": false,
  "initializer_range": 0.02,
  "tie_word_embeddings": false,
  "use_cache": false,
  "bos_token_id": 1,
  "eos_token_id": 2,
  "pretraining_tp": 1,
  "dtype": "float32",
  "transformers_version": "4.57.5"
}
```

### 2.2 Architecture Explanation

**Grouped Query Attention (GQA)**
- Query heads: 12
- Key/Value heads: 4
- Ratio: 3:1
- This reduces memory usage and increases inference speed while maintaining quality.

**SwiGLU MLP**
- Activation: SiLU (Sigmoid Linear Unit)
- Gate projection: 768 → 2048
- Up projection: 768 → 2048
- Down projection: 2048 → 768
- Intermediate multiplier: 2.67x hidden size

**RoPE (Rotary Position Embeddings)**
- Base frequency (theta): 10000.0
- Maximum positions: 2048
- No scaling applied

**RMSNorm**
- Applied before attention (pre-norm architecture)
- Applied before MLP
- Epsilon: 1e-6

### 2.3 Parameter Count Breakdown

| Component | Formula | Parameters |
|-----------|---------|------------|
| **Embedding** | vocab × hidden | 32,000 × 768 = 24,576,000 |
| **LM Head** | hidden × vocab | 768 × 32,000 = 24,576,000 |
| **Final Norm** | hidden | 768 |
| **Per Layer** | (see below) | 6,292,992 |
| **12 Layers** | 12 × per_layer | 75,515,904 |
| **Total** | | **124,668,672** |

**Per-Layer Breakdown (×12):**

| Sub-component | Shape | Parameters |
|---------------|-------|------------|
| Q projection | [768, 768] | 589,824 |
| K projection | [256, 768] | 196,608 |
| V projection | [256, 768] | 196,608 |
| O projection | [768, 768] | 589,824 |
| Gate projection | [2048, 768] | 1,572,864 |
| Up projection | [2048, 768] | 1,572,864 |
| Down projection | [768, 2048] | 1,572,864 |
| Input LayerNorm | [768] | 768 |
| Post-Attn LayerNorm | [768] | 768 |
| **Layer Total** | | **6,292,992** |

---

## 3. Safetensors Analysis

### 3.1 File Information

| Property | Value |
|----------|-------|
| Filename | model.safetensors |
| Size | 498,687,008 bytes (475.57 MB) |
| Format | SafeTensors (format: "pt") |
| Tensor Count | 111 |
| Data Type | torch.float32 (4 bytes per parameter) |

### 3.2 SHA-256 Checksum

```
9f54bcd00193a6c4d340d2ba0857092856730814b60c305842a3c878bb572ade
```

### 3.3 Tensor Manifest

#### Embedding and Output Layers

| Tensor Name | Shape | Parameters | Size (MB) |
|-------------|-------|------------|-----------|
| model.embed_tokens.weight | [32000, 768] | 24,576,000 | 93.75 |
| lm_head.weight | [32000, 768] | 24,576,000 | 93.75 |
| model.norm.weight | [768] | 768 | 0.003 |

#### Per-Layer Tensors (×12 layers)

Each layer (0-11) contains exactly 9 tensors:

| Tensor Name | Shape | Parameters |
|-------------|-------|------------|
| model.layers.{i}.input_layernorm.weight | [768] | 768 |
| model.layers.{i}.self_attn.q_proj.weight | [768, 768] | 589,824 |
| model.layers.{i}.self_attn.k_proj.weight | [256, 768] | 196,608 |
| model.layers.{i}.self_attn.v_proj.weight | [256, 768] | 196,608 |
| model.layers.{i}.self_attn.o_proj.weight | [768, 768] | 589,824 |
| model.layers.{i}.post_attention_layernorm.weight | [768] | 768 |
| model.layers.{i}.mlp.gate_proj.weight | [2048, 768] | 1,572,864 |
| model.layers.{i}.mlp.up_proj.weight | [2048, 768] | 1,572,864 |
| model.layers.{i}.mlp.down_proj.weight | [768, 2048] | 1,572,864 |

### 3.4 Memory Requirements

| Precision | Model Size | Inference (est.) | Training (est.) |
|-----------|------------|------------------|-----------------|
| float32 | 475.57 MB | ~600 MB | ~2.5 GB |
| float16 | 237.78 MB | ~350 MB | ~1.5 GB |
| int8 | 118.89 MB | ~200 MB | N/A |
| int4 | 59.45 MB | ~100 MB | N/A |

---

## 4. Training Methodology

### 4.1 Knowledge Distillation

The model was trained using knowledge distillation from larger expert teacher models. This approach transfers learned representations from pre-trained models to a smaller student model.

**Distillation Loss Function:**

```
L_total = 0.5 × L_KL + 0.5 × L_CE

Where:
L_KL = KL(softmax(student_logits/T), softmax(teacher_logits/T)) × T²
L_CE = CrossEntropy(student_logits, labels)
T = 2.0 (temperature)
```

### 4.2 Expert Teachers

| Expert | Model ID | Parameters | Specialization |
|--------|----------|------------|----------------|
| Qwen | Qwen/Qwen2.5-1.5B-Instruct | 1.54B | Tool-calling, JSON, multilingual |
| TinyLlama | TinyLlama/TinyLlama-1.1B-Chat-v1.0 | 1.1B | Instruction following, safety |

### 4.3 Training Configuration

| Parameter | Value |
|-----------|-------|
| Batch Size | 1 |
| Gradient Accumulation | 8 |
| Effective Batch Size | 8 |
| Learning Rate | 1e-4 |
| Optimizer | AdamW |
| Weight Decay | 0.01 |
| Gradient Clipping | 1.0 |
| Max Sequence Length | 512 |
| Steps per Expert | 1000 |

### 4.4 Hardware Environment

| Component | Specification |
|-----------|---------------|
| Device | CPU |
| CPU | Intel Core i3-1005G1 @ 1.20GHz |
| RAM | 16 GB |
| GPU | None |
| Storage | SSD |
| OS | Linux |

---

## 5. Training Progress

### 5.1 Timeline

| Timestamp | Event |
|-----------|-------|
| 2026-01-15T15:04:28 | Training started |
| 2026-01-15T15:16:57 | Last checkpoint (step 380) |
| 2026-01-15T20:49:00 | Report generated |

### 5.2 Loss Curve

The following loss values were recorded during training (sampled every 10 steps):

```
Step    Loss     Δ from Start
────────────────────────────────
  0     128.58   baseline
 10     127.20   -1.1%
 20     120.69   -6.1%
 30     110.13   -14.3%
 40     104.32   -18.9%
 50      99.55   -22.6%
 60      95.40   -25.8%
 70      92.24   -28.3%
 80      89.51   -30.4%
 90      86.10   -33.0%
100      83.74   -34.9%
110      81.76   -36.4%
120      79.95   -37.8%
130      78.53   -38.9%
140      77.58   -39.7%
150      75.99   -40.9%
160      74.81   -41.8%
170      73.83   -42.6%
180      72.90   -43.3%
190      72.19   -43.9%
200      71.51   -44.4%
210      70.50   -45.2%
220      69.76   -45.7%
230      69.11   -46.2%
240      68.48   -46.7%
250      67.94   -47.2%
260      67.41   -47.6%
270      66.64   -48.2%
280      66.05   -48.6%
290      65.54   -49.0%
300      65.02   -49.4%
310      64.58   -49.8%
320      64.15   -50.1%
330      63.52   -50.6%
340      63.04   -51.0%
350      62.61   -51.3%
360      62.17   -51.7%
370      61.78   -52.0%
380      61.39   -52.3%
```

### 5.3 Convergence Analysis

| Metric | Value |
|--------|-------|
| Initial Loss | 128.58 |
| Current Loss | 61.39 |
| Absolute Reduction | 67.19 |
| Percentage Reduction | 52.3% |
| Average Loss/Step | -0.177 |
| Steps Completed | 380 |
| Steps Remaining | 620 (Qwen) + 1000 (TinyLlama) |

---

## 6. File Structure

### 6.1 Model Directory

```
models/gladius_primary/gladius-125m-v1/
├── model.safetensors        # 498.7 MB - Model weights
├── config.json              # 668 B - Architecture config
├── tokenizer.json           # 3.6 MB - Tokenizer vocabulary
├── tokenizer_config.json    # 951 B - Tokenizer settings
├── special_tokens_map.json  # 551 B - Special token definitions
├── generation_config.json   # 133 B - Generation defaults
└── chat_template.jinja      # 410 B - Chat formatting template
```

### 6.2 Tokenizer Information

| Property | Value |
|----------|-------|
| Type | PreTrainedTokenizerFast |
| Vocabulary Size | 32,000 |
| BOS Token | `<s>` (id: 1) |
| EOS Token | `</s>` (id: 2) |
| UNK Token | `<unk>` (id: 0) |
| Padding Token | `</s>` (id: 2) |
| Chat Template | Jinja2 |

---

## 7. Usage Instructions

### 7.1 Loading the Model

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("amuzetnoM/Gladius")
tokenizer = AutoTokenizer.from_pretrained("amuzetnoM/Gladius")
```

### 7.2 Inference Example

```python
import torch

prompt = "What is the capital of France?"
inputs = tokenizer(prompt, return_tensors="pt")

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=50,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
        pad_token_id=tokenizer.eos_token_id
    )

response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)
```

### 7.3 Memory Requirements

| Task | float32 | float16 |
|------|---------|---------|
| Model Loading | 476 MB | 238 MB |
| Inference (seq=512) | ~600 MB | ~350 MB |
| Inference (seq=2048) | ~1.2 GB | ~700 MB |

---

## 8. Limitations

### 8.1 Current Limitations

1. **Incomplete Training**: Model has completed only 380/2000 total training steps.
2. **Limited Experts**: Only Qwen distillation is in progress; TinyLlama not started.
3. **Output Quality**: Responses may be incoherent or repetitive due to incomplete training.
4. **Vocabulary Mismatch**: Uses 32K vocab (TinyLlama-based) which differs from Qwen's 151K vocab.
5. **No Safety Training**: Model has not undergone safety fine-tuning or RLHF.
6. **CPU-Only Training**: Training was performed on CPU, limiting batch size and speed.

### 8.2 Known Issues

- Loss reduction slowing as training progresses (expected behavior)
- Model may output repeated tokens or fragments
- Tool-calling capability not yet verified
- Long-context generation untested

### 8.3 Not Recommended For

- Production deployments
- Safety-critical applications
- Applications requiring factual accuracy
- Multi-turn conversations
- Code generation

---

## 9. Checksums

### 9.1 File Checksums

| File | SHA-256 |
|------|---------|
| model.safetensors | `9f54bcd00193a6c4d340d2ba0857092856730814b60c305842a3c878bb572ade` |

### 9.2 Verification

```bash
sha256sum model.safetensors
# Expected: 9f54bcd00193a6c4d340d2ba0857092856730814b60c305842a3c878bb572ade
```

---

## 10. Appendix

### 10.1 Complete Tensor List

```
lm_head.weight                                    [32000, 768]
model.embed_tokens.weight                         [32000, 768]
model.norm.weight                                 [768]
model.layers.0.input_layernorm.weight             [768]
model.layers.0.mlp.down_proj.weight               [768, 2048]
model.layers.0.mlp.gate_proj.weight               [2048, 768]
model.layers.0.mlp.up_proj.weight                 [2048, 768]
model.layers.0.post_attention_layernorm.weight    [768]
model.layers.0.self_attn.k_proj.weight            [256, 768]
model.layers.0.self_attn.o_proj.weight            [768, 768]
model.layers.0.self_attn.q_proj.weight            [768, 768]
model.layers.0.self_attn.v_proj.weight            [256, 768]
model.layers.1.input_layernorm.weight             [768]
model.layers.1.mlp.down_proj.weight               [768, 2048]
model.layers.1.mlp.gate_proj.weight               [2048, 768]
model.layers.1.mlp.up_proj.weight                 [2048, 768]
model.layers.1.post_attention_layernorm.weight    [768]
model.layers.1.self_attn.k_proj.weight            [256, 768]
model.layers.1.self_attn.o_proj.weight            [768, 768]
model.layers.1.self_attn.q_proj.weight            [768, 768]
model.layers.1.self_attn.v_proj.weight            [256, 768]
model.layers.2.input_layernorm.weight             [768]
model.layers.2.mlp.down_proj.weight               [768, 2048]
model.layers.2.mlp.gate_proj.weight               [2048, 768]
model.layers.2.mlp.up_proj.weight                 [2048, 768]
model.layers.2.post_attention_layernorm.weight    [768]
model.layers.2.self_attn.k_proj.weight            [256, 768]
model.layers.2.self_attn.o_proj.weight            [768, 768]
model.layers.2.self_attn.q_proj.weight            [768, 768]
model.layers.2.self_attn.v_proj.weight            [256, 768]
model.layers.3.input_layernorm.weight             [768]
model.layers.3.mlp.down_proj.weight               [768, 2048]
model.layers.3.mlp.gate_proj.weight               [2048, 768]
model.layers.3.mlp.up_proj.weight                 [2048, 768]
model.layers.3.post_attention_layernorm.weight    [768]
model.layers.3.self_attn.k_proj.weight            [256, 768]
model.layers.3.self_attn.o_proj.weight            [768, 768]
model.layers.3.self_attn.q_proj.weight            [768, 768]
model.layers.3.self_attn.v_proj.weight            [256, 768]
model.layers.4.input_layernorm.weight             [768]
model.layers.4.mlp.down_proj.weight               [768, 2048]
model.layers.4.mlp.gate_proj.weight               [2048, 768]
model.layers.4.mlp.up_proj.weight                 [2048, 768]
model.layers.4.post_attention_layernorm.weight    [768]
model.layers.4.self_attn.k_proj.weight            [256, 768]
model.layers.4.self_attn.o_proj.weight            [768, 768]
model.layers.4.self_attn.q_proj.weight            [768, 768]
model.layers.4.self_attn.v_proj.weight            [256, 768]
model.layers.5.input_layernorm.weight             [768]
model.layers.5.mlp.down_proj.weight               [768, 2048]
model.layers.5.mlp.gate_proj.weight               [2048, 768]
model.layers.5.mlp.up_proj.weight                 [2048, 768]
model.layers.5.post_attention_layernorm.weight    [768]
model.layers.5.self_attn.k_proj.weight            [256, 768]
model.layers.5.self_attn.o_proj.weight            [768, 768]
model.layers.5.self_attn.q_proj.weight            [768, 768]
model.layers.5.self_attn.v_proj.weight            [256, 768]
model.layers.6.input_layernorm.weight             [768]
model.layers.6.mlp.down_proj.weight               [768, 2048]
model.layers.6.mlp.gate_proj.weight               [2048, 768]
model.layers.6.mlp.up_proj.weight                 [2048, 768]
model.layers.6.post_attention_layernorm.weight    [768]
model.layers.6.self_attn.k_proj.weight            [256, 768]
model.layers.6.self_attn.o_proj.weight            [768, 768]
model.layers.6.self_attn.q_proj.weight            [768, 768]
model.layers.6.self_attn.v_proj.weight            [256, 768]
model.layers.7.input_layernorm.weight             [768]
model.layers.7.mlp.down_proj.weight               [768, 2048]
model.layers.7.mlp.gate_proj.weight               [2048, 768]
model.layers.7.mlp.up_proj.weight                 [2048, 768]
model.layers.7.post_attention_layernorm.weight    [768]
model.layers.7.self_attn.k_proj.weight            [256, 768]
model.layers.7.self_attn.o_proj.weight            [768, 768]
model.layers.7.self_attn.q_proj.weight            [768, 768]
model.layers.7.self_attn.v_proj.weight            [256, 768]
model.layers.8.input_layernorm.weight             [768]
model.layers.8.mlp.down_proj.weight               [768, 2048]
model.layers.8.mlp.gate_proj.weight               [2048, 768]
model.layers.8.mlp.up_proj.weight                 [2048, 768]
model.layers.8.post_attention_layernorm.weight    [768]
model.layers.8.self_attn.k_proj.weight            [256, 768]
model.layers.8.self_attn.o_proj.weight            [768, 768]
model.layers.8.self_attn.q_proj.weight            [768, 768]
model.layers.8.self_attn.v_proj.weight            [256, 768]
model.layers.9.input_layernorm.weight             [768]
model.layers.9.mlp.down_proj.weight               [768, 2048]
model.layers.9.mlp.gate_proj.weight               [2048, 768]
model.layers.9.mlp.up_proj.weight                 [2048, 768]
model.layers.9.post_attention_layernorm.weight    [768]
model.layers.9.self_attn.k_proj.weight            [256, 768]
model.layers.9.self_attn.o_proj.weight            [768, 768]
model.layers.9.self_attn.q_proj.weight            [768, 768]
model.layers.9.self_attn.v_proj.weight            [256, 768]
model.layers.10.input_layernorm.weight            [768]
model.layers.10.mlp.down_proj.weight              [768, 2048]
model.layers.10.mlp.gate_proj.weight              [2048, 768]
model.layers.10.mlp.up_proj.weight                [2048, 768]
model.layers.10.post_attention_layernorm.weight   [768]
model.layers.10.self_attn.k_proj.weight           [256, 768]
model.layers.10.self_attn.o_proj.weight           [768, 768]
model.layers.10.self_attn.q_proj.weight           [768, 768]
model.layers.10.self_attn.v_proj.weight           [256, 768]
model.layers.11.input_layernorm.weight            [768]
model.layers.11.mlp.down_proj.weight              [768, 2048]
model.layers.11.mlp.gate_proj.weight              [2048, 768]
model.layers.11.mlp.up_proj.weight                [2048, 768]
model.layers.11.post_attention_layernorm.weight   [768]
model.layers.11.self_attn.k_proj.weight           [256, 768]
model.layers.11.self_attn.o_proj.weight           [768, 768]
model.layers.11.self_attn.q_proj.weight           [768, 768]
model.layers.11.self_attn.v_proj.weight           [256, 768]
```

### 10.2 Raw Loss Data

```json
[128.57879638671875, 127.20331573486328, 120.69094921293713, 110.13394854145665, 104.31602357073528, 99.55007104312672, 95.40429287269467, 92.23711293180224, 89.50634516021351, 86.09717341831752, 83.7358569154645, 81.75625620661555, 79.95060004872724, 78.53474238446651, 77.5772081875632, 75.9855439394515, 74.81200504895322, 73.83143853304679, 72.89652891844017, 72.1909675298561, 71.50870216901029, 70.50224174029454, 69.76016766992629, 69.1093349787064, 68.48188161256402, 67.93610207303112, 67.4084893588362, 66.63655255729422, 66.05062290612489, 65.53774519720439, 65.02452437822208, 64.57979699039765, 64.14566163630501, 63.52046715889092, 63.043596474655914, 62.611123891977165, 62.17351185383889, 61.78107300215976, 61.38993682260588]
```

---

**Document End**

