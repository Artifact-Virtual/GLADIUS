<br>

<p align="center">
  <img src="https://img.shields.io/badge/Language-C++-blue.svg" alt="C++">
  <img src="https://img.shields.io/badge/Python-3.10+-yellow.svg" alt="Python">
  <img src="https://img.shields.io/badge/AI-Native-brightgreen.svg" alt="Native AI">
  <img src="https://img.shields.io/badge/VectorDB-Hektor-informational.svg" alt="Hektor VDB">
  <img src="https://img.shields.io/github/last-commit/adam/gladius?style=flat-square" alt="Last Commit">
  <img src="https://img.shields.io/github/commit-activity/m/adam/gladius?style=flat-square" alt="Commit Activity">
  <img src="https://img.shields.io/github/issues/adam/gladius?style=flat-square" alt="Issues">
  <img src="https://img.shields.io/github/license/adam/gladius?style=flat-square" alt="License">
</p>

---

## Overview

Gladius is an **Autonomous Enterprise Operating System** with a fully native AI stack—no external API dependencies. It manages multiple business artifacts through unified cognition, native vectorization, and semantic memory. Core features include a native C++ vector database (Hektor), native tool routing, and autonomous learning.

---

## Architecture

```mermaid
flowchart TD
    A["GLADIUS<br/>(Autonomous Enterprise Manager)"]
    subgraph Core
        B["Hektor VDB<br/>SIMD/HNSW"]
        C["Native Router<br/>(tool <10ms)"]
        D["Memory Module<br/>(16 tools)"]
    end
    E["MODEL STACK<br/>Native GGUF (<10ms) → Ollama (~100ms) → Fallback"]
    F1["ALPHA<br/>Syndicate<br/>Research"]
    F2["BETA<br/>Cthulu<br/>Trading"]
    F3["THETA<br/>(Future)<br/>Publishing"]

    A --> Core
    Core --> E
    E --> F1
    E --> F2
    E --> F3
```

---

## Native AI Model Stack

```mermaid
flowchart LR
    A["Tool Routing<br/>Native GGUF<br/>&lt;10ms<br/>🚧 Training ready"]
    B["Fallback<br/>Pattern Match<br/>&lt;1ms<br/>✅ Working"]
    C["Reasoning<br/>Ollama<br/>~100ms<br/>✅ Production"]
    D["Embeddings<br/>TF-IDF + Hektor<br/>&lt;5ms<br/>✅ Production"]

    subgraph ModelStack
        A
        B
        C
        D
    end
```

**Evolution Path:**

```mermaid
flowchart LR
    P1["Phase 1<br/>Ollama + patterns"]
    P2["Phase 2<br/>Fine-tuned GGUF"]
    P3["Phase 3<br/>Gladius Native (full autonomy)"]
    P1 --> P2 --> P3
```

---

## Core Systems

```mermaid
flowchart TD
    H["Hektor VDB<br/>Native C++ vectors"]
    R["Native Router<br/>Tool routing"]
    M["Memory Module<br/>16 tools, multi-DB"]
    I["Infra API<br/>Market data, portfolios"]
    D["Dashboard<br/>Control panel"]
    S["Syndicate<br/>Market intelligence"]
    C["Cthulu<br/>MQL5/MT5 trading"]

    H --> R
    R --> M
    M --> I
    I --> D
    D --> S
    S --> C
```

---

## Roadmap

```mermaid
gantt
    dateFormat  YYYY-MM-DD
    title       Gladius Roadmap

    section Phase 2.1
    Native_tool_router_GGUF      :done,    p21, 2026-01-01, 2026-03-31
    section Phase 2.2
    Domain_specialist_gold_trading :active, p22, 2026-04-01, 2026-06-30
    section Phase 3
    Gladius_Native_full_autonomy   :        p3, 2026-07-01, 2026-12-31
```

---

## 🏗️ Architecture

```mermaid
flowchart TD
    subgraph GLADIUS [GLADIUS (Autonomous Enterprise Manager)]
        Hektor["Hektor VDB<br/>SIMD/HNSW"]
        Router["Native Router<br/>(tool <10ms)"]
        Memory["Memory Module<br/>(16 tools)"]
        ModelStack["MODEL STACK<br/>Native GGUF (<10ms) → Ollama (~100ms) → Fallback"]
    end
    GLADIUS -->|Manages| Alpha["ALPHA<br/>Syndicate<br/>Research"]
    GLADIUS -->|Manages| Beta["BETA<br/>Cthulu<br/>Trading"]
    GLADIUS -->|Manages| Theta["THETA<br/>(Future)<br/>Publishing"]
```

---

## 🧠 Native AI Model Stack

```mermaid
flowchart TB
    ToolRouting["Tool Routing<br/>Native GGUF<br/><10ms<br/>🚧 Training ready"]
    Fallback["Fallback<br/>Pattern Match<br/><1ms<br/>✅ Working"]
    Reasoning["Reasoning<br/>Ollama<br/>~100ms<br/>✅ Production"]
    Embeddings["Embeddings<br/>TF-IDF + Hektor<br/><5ms<br/>✅ Production"]

    ToolRouting --> Fallback
    ToolRouting --> Reasoning
    ToolRouting --> Embeddings
```

**Evolution Path:**

```mermaid
flowchart LR
    Phase1["Phase 1 (current)<br/>Ollama + patterns"]
    Phase2["Phase 2 (next)<br/>Fine-tuned GGUF"]
    Phase3["Phase 3 (target)<br/>Gladius Native (full autonomy)"]
    Phase1 --> Phase2 --> Phase3
```

---

