# GLADIUS Training CLI Documentation

> **Module**: `/GLADIUS/gladius_train`  
> **Version**: 1.0.0  
> **Last Updated**: 2026-01-15  
> **Purpose**: Comprehensive CLI for GLADIUS model training operations

---

## Overview

The GLADIUS Training CLI (`gladius_train`) provides a unified interface for:

1. **Model Management** - Download and track expert models
2. **Training Orchestration** - Start, stop, and monitor training
3. **Progress Monitoring** - Live dashboard and status reporting
4. **Model Export** - Convert to GGUF for deployment
5. **Validation** - Test trained models

---

## Quick Start

```bash
# Navigate to GLADIUS directory
cd /home/adam/worxpace/gladius/GLADIUS

# Check current status
./gladius_train status

# List all models and download status
./gladius_train models

# Download missing required models
./gladius_train download

# Start indefinite training
./gladius_train train

# Monitor progress (live dashboard)
./gladius_train dashboard
```

---

## Commands Reference

### `status` - Show Training Status

Displays current training state, progress, and expert completion.

```bash
./gladius_train status
```

**Output includes:**
- Current training status (not_started, training, paused, completed, failed)
- Phase progress (0-6)
- Current expert being distilled
- Step count and loss
- Parameter count and target progress
- Total training hours
- Hardware detected (CPU/CUDA)

---

### `models` - List Expert Models

Shows all expert models with their download status, size, and requirements.

```bash
./gladius_train models
```

**Expert Models (by priority):**

| Model | HuggingFace ID | Size | Weight |
|-------|----------------|------|--------|
| Qwen 2.5 1.5B | Qwen/Qwen2.5-1.5B-Instruct | ~3GB | 1.5 |
| Llama 3.2 1B | meta-llama/Llama-3.2-1B-Instruct | ~2.5GB | 1.3 |
| Phi-2 | microsoft/phi-2 | ~5.5GB | 1.2 |
| TinyLlama 1.1B | TinyLlama/TinyLlama-1.1B-Chat-v1.0 | ~2.2GB | 1.0 |

**Status indicators:**
- `✓ Ready` - Model downloaded and verified
- `◐ Partial` - Download incomplete
- `○ Missing` - Not downloaded

---

### `download` - Download Models

Download expert models from HuggingFace.

```bash
# Download all required models
./gladius_train download

# Download specific model
./gladius_train download qwen
./gladius_train download phi
./gladius_train download gemma

# Download all models (including optional)
./gladius_train download --all

# Force re-download
./gladius_train download --force
```

**Model names:** `qwen`, `llama`, `phi`, `tinyllama`

**Storage location:** All models stored in `/GLADIUS/tmp/` directory:
- Cache: `tmp/cache/` (HuggingFace cache)
- Models: `tmp/models/` (extracted models)
- Experts: `tmp/experts_cache/` (training cache)

---

### `train` - Start Training

Begin multi-expert knowledge distillation training.

```bash
# Train indefinitely (until interrupted)
./gladius_train train

# Train for specific duration
./gladius_train train --hours 72
./gladius_train train --hours 168  # 1 week

# Resume from checkpoint
./gladius_train resume
```

**Training Phases:**
1. **Phase 0** - Create student model (1B parameters, random init)
2. **Phase 1** - Distill from Qwen (tool-calling, JSON)
3. **Phase 2** - Distill from Llama (reasoning, fluency)
4. **Phase 3** - Distill from Phi (math, code)
5. **Phase 4** - Distill from TinyLlama (safety, instructions)
6. **Phase 5** - Final unified training
7. **Phase 6** - Save and export

**Stopping Training:**
- Press `Ctrl+C` to stop gracefully with checkpoint
- Training will resume from last checkpoint

---

### `resume` - Resume Training

Continue training from the last checkpoint.

```bash
./gladius_train resume

# Resume with time limit
./gladius_train resume --hours 24
```

---

### `dashboard` - Live Dashboard

Real-time training progress visualization.

```bash
./gladius_train dashboard
```

**Dashboard shows:**
- Model status and phase
- Parameter growth progress bar
- Expert distillation progress
- Loss curve (ASCII chart)
- Training time and milestones

---

### `export` - Export to GGUF

Convert trained model to GGUF format for deployment.

```bash
./gladius_train export
```

**Requirements:**
- Trained model in `GLADIUS/models/gladius_primary/`
- llama.cpp installed at `~/llama.cpp`

**Output:** `gladius-1b.gguf` in model directory

---

### `validate` - Validate Model

Test the trained model with sample prompts.

```bash
./gladius_train validate
```

**Tests performed:**
- Model loading
- Parameter count verification
- Generation test with tool routing prompt
- Generation test with capability query

---

### `clean` - Clean Temp Files

Remove temporary and log files.

```bash
# Show what will be cleaned
./gladius_train clean

# Actually delete files
./gladius_train clean --confirm
```

---

## Directory Structure

```
GLADIUS/
├── gladius_train              # ← This CLI
├── tmp/                       # Temporary/heavy files (gitignored)
│   ├── models/               # Downloaded models
│   ├── cache/                # HuggingFace cache
│   ├── checkpoints/          # Training checkpoints
│   ├── logs/                 # Training logs
│   ├── downloads/            # Download temp files
│   └── experts_cache/        # Expert model cache
├── training/                 # Training code
│   ├── gladius_moe_trainer.py
│   ├── gladius_1b_trainer.py
│   └── data/                 # Training datasets
├── models/                   # Output models
│   └── gladius_primary/      # Trained GLADIUS model
└── growth/
    └── growth_tracker.py     # Dashboard
```

---

## Training Configuration

### Architecture (Target: 1 Billion Parameters)

| Parameter | Value |
|-----------|-------|
| Hidden Size | 2048 |
| Intermediate Size | 5632 (~2.75x) |
| Layers | 24 |
| Attention Heads | 16 |
| KV Heads (GQA) | 4 |
| Vocab Size | 32000 |
| Max Context | 8192 tokens |
| RoPE Theta | 10000 |

### Training Method

**Multi-Expert Knowledge Distillation:**
1. Initialize student with random weights (NOT fine-tuning)
2. For each expert teacher:
   - Generate capability-specific training data
   - Compute teacher logits (frozen)
   - Train student with KL divergence + cross-entropy loss
   - Temperature scaling (T=2.0)
3. Final unified training pass
4. Export to safetensors/GGUF

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HF_TOKEN` | HuggingFace auth token | ~/.cache/huggingface/token |
| `CUDA_VISIBLE_DEVICES` | GPU selection | All available |

---

## Running Indefinitely

For continuous training until model convergence:

```bash
# Start in screen/tmux for persistence
screen -S gladius-training

# Inside screen
cd /home/adam/worxpace/gladius/GLADIUS
./gladius_train train

# Detach: Ctrl+A, D
# Reattach: screen -r gladius-training
```

Or using nohup:

```bash
cd /home/adam/worxpace/gladius/GLADIUS
nohup ./gladius_train train > logs/training_$(date +%Y%m%d).log 2>&1 &
echo $! > training.pid
```

Monitor:
```bash
tail -f logs/training_*.log

# Or use dashboard
./gladius_train dashboard
```

Stop gracefully:
```bash
# Kill with SIGTERM to trigger checkpoint save
kill $(cat training.pid)
```

---

## Troubleshooting

### Model download fails
```bash
# Check HuggingFace authentication
huggingface-cli whoami

# Login if needed
huggingface-cli login

# Or set token
export HF_TOKEN="your_token"
```

### CUDA out of memory
- Training automatically falls back to CPU
- Reduce batch size in trainer config
- Use gradient checkpointing

### Training hangs
- Check disk space: `df -h`
- Check GPU status: `nvidia-smi`
- View logs: `tail -f tmp/logs/*.log`

### Resume not working
- Check checkpoint exists: `ls tmp/checkpoints/`
- View state: `cat tmp/checkpoints/training_state.json`

---

## Hardware Requirements

**Minimum:**
- CPU: 8 cores
- RAM: 32GB
- Storage: 50GB free

**Recommended:**
- GPU: NVIDIA with 16GB+ VRAM
- RAM: 64GB
- Storage: 100GB+ SSD

**Optimal:**
- GPU: NVIDIA RTX 4090 / A100
- RAM: 128GB
- Storage: 500GB NVMe

---

## Support

For issues or questions:
1. Check logs: `tmp/logs/`
2. View training state: `./gladius_train status`
3. Consult SYSTEM_MAPPING.md for architecture details

---

*Part of the GLADIUS Enterprise AI System*
