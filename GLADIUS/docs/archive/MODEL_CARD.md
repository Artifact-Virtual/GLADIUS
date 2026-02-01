# GLADIUS Model Card

## Model Details

### Model Description

GLADIUS is a native language model developed by Artifact Virtual Enterprise for autonomous operations. It is designed specifically for tool-calling, function execution, and integration with enterprise systems.

- **Developed by:** Artifact Virtual Enterprise
- **Model type:** Causal Language Model (Decoder-only Transformer)
- **Language:** English (primary), multilingual (limited)
- **License:** Proprietary
- **Architecture:** GLADIUS-LM (Custom Transformer)

### Model Sources

- **Repository:** [https://huggingface.co/amuzetnoM/Gladius](https://huggingface.co/amuzetnoM/Gladius)
- **Documentation:** [GLADIUS/docs/](./ARCHITECTURE.md)

## Uses

### Direct Use

GLADIUS is designed for:
- Tool and function calling
- JSON-structured responses
- Enterprise automation
- Agentic workflows
- System integration

### Downstream Use

- Integration with SENTINEL (monitoring daemon)
- Integration with LEGION (multi-agent orchestration)
- BUILD_CLASS (code generation)
- SYNDICATE (market intelligence)

### Out-of-Scope Use

- General conversational AI (not optimized)
- Creative writing
- Code generation (use BUILD_CLASS instead)
- Medical/legal advice

## Bias, Risks, and Limitations

### Known Limitations

1. **Small Context Window**: 2048 tokens max (can be extended)
2. **Limited Vocabulary**: 32K tokens (expandable)
3. **Tool-Calling Focus**: May not perform well on general tasks
4. **Training Data**: Limited to proprietary datasets

### Recommendations

- Use for intended purpose (tool-calling)
- Validate outputs before execution
- Monitor for unexpected behaviors
- Keep model updated

## Training Details

### Training Data

- Proprietary tool-calling examples
- Function documentation
- System integration patterns
- JSON response formats

### Training Procedure

#### Training Hyperparameters

- **Optimizer:** AdamW
- **Learning rate:** 1e-4
- **Weight decay:** 0.01
- **Batch size:** 2-8 (CPU) / 32-64 (GPU)
- **Epochs:** 3-10
- **Max sequence length:** 256-2048

#### Hardware

- **CPU Training:** 4-core, 8-16GB RAM
- **GPU Training:** NVIDIA with 4-16GB VRAM

## Evaluation

### Testing Data

- Held-out tool-calling examples
- Edge case scenarios
- Error handling tests

### Metrics

| Metric | Value |
|--------|-------|
| Tool-call accuracy | 75-92% (size dependent) |
| JSON validity | 95%+ |
| Response latency | 20-50 tokens/sec (CPU) |

## Environmental Impact

- **Hardware:** CPU-optimized for efficiency
- **Training time:** 4-48 hours (size dependent)
- **Carbon footprint:** Minimal (local training)

## Technical Specifications

### Model Architecture

```
Type: Decoder-only Transformer
Normalization: RMSNorm
Attention: Grouped Query Attention (GQA)
Position: Rotary Position Embedding (RoPE)
Activation: SwiGLU
```

### Compute Infrastructure

- **Training:** CPU or CUDA GPU
- **Inference:** CPU, GPU, or Edge devices
- **Format:** PyTorch, GGUF

## Citation

```bibtex
@misc{gladius2026,
  title={GLADIUS: Native AI for Artifact Virtual Enterprise},
  author={Artifact Virtual ML},
  year={2026},
  howpublished={\url{https://huggingface.co/amuzetnoM/Gladius}},
}
```

## Model Card Authors

Artifact Virtual Engineering Team

## Model Card Contact

- Repository: https://github.com/amuzetnom/gladius
- HuggingFace: https://huggingface.co/amuzetnoM/Gladius
