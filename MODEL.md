# Gladius Model Architecture

> Native AI Model Strategy: From Tool Router to Full Autonomous Intelligence

---

## Vision

Gladius aims to evolve from using external models to running **fully native AI** that:
1. Routes tools with sub-10ms latency
2. Performs reasoning without external APIs
3. Generates analysis and content autonomously
4. Learns from its own operation history
5. Eventually replaces both tiny routers AND large language models

---

## Model Evolution Path

```mermaid
flowchart TD
    Phase1["Phase 1 (Current):<br/>Ollama (qwen2.5)<br/>External LLM<br/>~100ms latency"]
    Phase2["Phase 2 (Next):<br/>Fine-tuned GGUF<br/>Tool Router<br/>&lt;10ms latency"]
    Phase3["Phase 3 (Target):<br/>Gladius Native<br/>Full Model<br/>&lt;50ms all tasks"]

    Phase1 -- "Pattern Fallback (~0.5 confidence)" --> Phase2
    Phase2 -- "Native Tool Calls (~0.9 confidence)" --> Phase3
    Phase3 -- "Full Autonomy (Self-improving)" --> Phase3
```

---

## Current Architecture

### Layer 1: Tool Routing (Implemented)

```mermaid
flowchart TD
    UserQuery["User Query"] --> NativeToolRouter["Native Tool Router"]
    NativeToolRouter -- "10ms" --> NativeGGUF["Native GGUF"]
    NativeToolRouter -- "100ms" --> OllamaAPI["Ollama API"]
    NativeToolRouter -- "&lt;1ms" --> PatternMatch["Pattern Match"]
    NativeGGUF --> ToolRoutingResult
    OllamaAPI --> ToolRoutingResult
    PatternMatch --> ToolRoutingResult
    ToolRoutingResult["ToolRoutingResult<br/>{tool, args, confidence}"]
```

### Layer 2: Reasoning (Ollama via Main Pipeline)

```mermaid
flowchart TD
    AnalysisRequest["Analysis Request"] --> SyndicateMain["Syndicate Main"]
    SyndicateMain --> Ollama["Ollama (llama3.2)"]
    Ollama --> JournalReport["Journal / Report Generation"]
```

### Layer 3: Embeddings (Hektor/TF-IDF)

```mermaid
flowchart TD
    Text["Text"] --> Embedder["Embedder"]
    Embedder --> Vector["384-dim Vector"]
    Vector --> HektorVDB["Hektor VDB"]
```

---

## Target Model Specifications

### Tool Router Model (Phase 2)

```mermaid
flowchart TD
    Base["Base: SmolLM2-135M-Instruct"] --> Size["Size: ~100MB (Q4_K_M)"]
    Size --> Context["Context: 512 tokens"]
    Context --> Latency["Latency: &lt;10ms"]
    Latency --> Task["Task: Tool selection only"]
```

### Full Model (Phase 3 - Gladius Native)

```mermaid
flowchart TD
    Architecture["Architecture: Transformer (custom)"] --> Parameters["Parameters: 1B-3B"]
    Parameters --> Context["Context: 4K-8K tokens"]
    Context --> Quantization["Quantization: Q4_K_M"]
    Quantization --> Format["Format: GGUF"]
```

---

## LoRA vs Full Fine-tune: Analysis

### For Tool Router (Recommended: LoRA)

```mermaid
flowchart TD
    LoRA["LoRA"]
    FullFineTune["Full Fine-tune"]

    LoRA -- "Pros: Fast training, Small adapter, Easy to iterate" --> LoRA_Pros[""]
    LoRA -- "Cons: Slightly lower quality" --> LoRA_Cons[""]

    FullFineTune -- "Pros: Maximum quality" --> FullFineTune_Pros[""]
    FullFineTune -- "Cons: Slow, Large output, Hard to iterate" --> FullFineTune_Cons[""]
```

### For Full Model (Recommended: Full Fine-tune + LoRA layers)

```mermaid
flowchart TD
    BaseTraining["Base Training: Full fine-tune"] --> Specialization["Specialization: LoRA adapters"]
    Specialization --> Personalization["Personalization: LoRA adapters"]
```

---

## Training Pipeline

### 1. Data Collection

```mermaid
flowchart TD
    ToolHistory["Tool History"] --> Dataset["Combined Dataset"]
    Predictions["Successful Predictions"] --> Dataset
    SyntheticVariants["Synthetic Variants"] --> Dataset
```

### 2. Fine-tuning

```mermaid
flowchart TD
    BaseModel["Base Model"] --> FineTuning["Fine-tuning"]
    TrainingData["Training Data"] --> FineTuning
    FineTuning --> LoRAAdapter["LoRA Adapter"]
```

### 3. Quantization

```mermaid
flowchart TD
    FineTunedModel["Fine-tuned Model"] --> Quantization["Quantization"]
    Quantization --> QuantizedModel["Quantized Model"]
```

### 4. Validation

```mermaid
flowchart TD
    TestSet["Test Set"] --> Validation["Validation"]
    Model["Model"] --> Validation
    Validation --> ValidationResults["Validation Results"]
```

---

## Model Files Structure

```mermaid
flowchart TD
    Models["models/"]
    BaseModels["base_models/"]
    LoRA["lora/"]
    Production["production/"]
    TrainingData["training_data/"]

    Models --> BaseModels
    Models --> LoRA
    Models --> Production
    Models --> TrainingData

    BaseModels --> SmolLM2["smollm2-135m.gguf"]
    BaseModels --> Qwen["qwen2.5-0.5b.gguf"]

    LoRA --> ToolRouter["tool-router/adapter.gguf"]
    LoRA --> GoldAnalyst["gold-analyst/adapter.gguf"]

    Production --> ToolRouterProd["tool-router.gguf"]
    Production --> GladiusCore["gladius-core.gguf"]

    TrainingData --> CombinedTraining["combined_training.jsonl"]
```

---

*Last updated: 2026-01-13*  
*Document version: 1.0.0*

