# Cthulu Model Architecture Proposal

**Status:** 🔮 FUTURE VISION - NOT IN SCOPE  
**Created:** 2026-01-10  
**Classification:** Design Speculation / Research Notes

---

## Overview

This document explores the concept of transforming Cthulu from a **rule-based autonomous trading system** into a **self-contained GGUF model** (or similar architecture) that embodies the system's decision-making capabilities in a single, deployable neural artifact.

The vision: A real-time, autonomous trading intelligence that processes incoming market data, news, and system state to generate trading decisions—all within a compact, quantized model that can run locally without external dependencies.

---

## Why This Feels AGI-Adjacent

Cthulu already exhibits several characteristics that align with autonomous intelligence:

| Characteristic | Current Implementation | Model-Native Vision |
|----------------|----------------------|---------------------|
| **Multi-modal input** | OHLCV, indicators, news, calendar | Unified embedding space |
| **Context awareness** | Market regime detection, session tracking | Transformer attention over context window |
| **Adaptive behavior** | Dynamic strategy selection | Learned policy network |
| **Risk-aware decisions** | Rule-based risk manager | Embedded risk priors in weights |
| **Continuous operation** | 24/7 trading loop | Streaming inference |
| **Self-correction** | Exit strategies, drawdown protection | Learned loss aversion |

---

## Proposed Architecture

### Option A: GGUF Trading Model (Quantized Transformer)

```mermaid
flowchart TB
    subgraph INPUTS["📥 Input Embeddings"]
        MARKET["Market Embed<br/>(OHLCV + Indicators)"]
        NEWS["News Embed<br/>(Sentiment)"]
        STATE["State Embed<br/>(Position Info)"]
    end
    
    subgraph MODEL["🧠 CTHULU.GGUF (~2-7B params)"]
        direction TB
        FUSION["Multi-Head Cross-Attention<br/>Market ↔ News ↔ State"]
        DECISION["Decision Transformer Blocks<br/>(states → actions → rewards)"]
        
        subgraph HEADS["Output Heads"]
            ACTION["Action Head<br/>BUY/SELL/HOLD"]
            SIZE["Size Head<br/>Position Size"]
            RISK["Risk Head<br/>SL/TP Levels"]
        end
    end
    
    MARKET --> FUSION
    NEWS --> FUSION
    STATE --> FUSION
    FUSION --> DECISION
    DECISION --> ACTION
    DECISION --> SIZE
    DECISION --> RISK
    
    style MODEL fill:#9b59b6,stroke:#8e44ad,color:#fff
    style INPUTS fill:#3498db,stroke:#2980b9,color:#fff
    style HEADS fill:#27ae60,stroke:#1e8449,color:#fff
```

### Option B: State Space Model (Mamba-style)

For real-time streaming with O(1) inference per timestep:

```mermaid
flowchart LR
    subgraph INPUT["Input Stream"]
        BAR["bar_t"]
        NEWST["news_t"]
        STATET["state_t"]
    end
    
    SSM["SSM Block<br/>(Selective State Space)<br/>━━━━━━━━━━━━━<br/>Recurrent State<br/>No Attention Needed"]
    
    POLICY["Action Policy<br/>━━━━━━━━━━━━━<br/>BUY/SELL/HOLD<br/>+ Parameters"]
    
    INPUT --> SSM
    SSM --> POLICY
    
    style SSM fill:#e74c3c,stroke:#c0392b,color:#fff
    style POLICY fill:#27ae60,stroke:#1e8449,color:#fff
```

### Option C: Mixture of Experts (MoE) Trading Model

Route to specialized sub-models based on detected regime:

```mermaid
flowchart TB
    INPUT["Market Data Input"]
    
    ROUTER["🎯 Router<br/>(Regime Detection)<br/>━━━━━━━━━━━━━<br/>ADX + Volatility Analysis"]
    
    subgraph EXPERTS["Specialized Experts"]
        TREND["📈 Trending Expert<br/>Trend-Following<br/>EMA/SMA Crossover"]
        RANGE["↔️ Ranging Expert<br/>Mean Reversion<br/>Bollinger/RSI"]
        VOLATILE["⚡ Volatile Expert<br/>Scalping<br/>Fast EMA + Momentum"]
    end
    
    OUTPUT["Combined Output<br/>(Weighted by Router)"]
    
    INPUT --> ROUTER
    ROUTER -->|"Trending Market"| TREND
    ROUTER -->|"Ranging Market"| RANGE
    ROUTER -->|"Volatile Market"| VOLATILE
    TREND --> OUTPUT
    RANGE --> OUTPUT
    VOLATILE --> OUTPUT
    
    style ROUTER fill:#f39c12,stroke:#d68910,color:#000
    style EXPERTS fill:#3498db,stroke:#2980b9,color:#fff
```

---

## Training Pipeline

```mermaid
flowchart LR
    subgraph PHASE1["Phase 1: Imitation Learning"]
        HIST["Historical<br/>Trade Decisions"]
        BC["Behavioral<br/>Cloning"]
    end
    
    subgraph PHASE2["Phase 2: Reinforcement Learning"]
        SIM["Simulated<br/>Market Env"]
        RL["RL Training<br/>(PPO/DQN)"]
        REWARD["Reward:<br/>Sharpe Ratio"]
    end
    
    subgraph PHASE3["Phase 3: Adversarial"]
        SELFPLAY["Self-Play"]
        CHAOS["Adversarial<br/>Scenarios"]
    end
    
    BASE["Base Model"]
    FINAL["Final GGUF"]
    
    HIST --> BC --> BASE
    BASE --> RL
    SIM --> RL
    REWARD --> RL
    RL --> SELFPLAY
    CHAOS --> SELFPLAY
    SELFPLAY --> FINAL
    
    style PHASE1 fill:#3498db,stroke:#2980b9,color:#fff
    style PHASE2 fill:#9b59b6,stroke:#8e44ad,color:#fff
    style PHASE3 fill:#e74c3c,stroke:#c0392b,color:#fff
```

---

## Input Tokenization

```mermaid
flowchart LR
    subgraph RAW["Raw Inputs"]
        OHLCV["OHLCV Data"]
        IND["Indicators<br/>RSI, ATR, etc."]
        NEWSRAW["News Headlines"]
        POS["Position State"]
    end
    
    subgraph TOKENS["Token Sequence"]
        direction TB
        T1["[MARKET_START]"]
        T2["[OHLC_BIN_42]"]
        T3["[RSI_30]"]
        T4["[ATR_HIGH]"]
        T5["[SESSION_LONDON]"]
        T6["[NEWS_START]"]
        T7["[SENTIMENT_BEARISH]"]
        T8["[STATE_START]"]
        T9["[POSITION_LONG]"]
        T10["[ACTION_START]"]
    end
    
    OUTPUT["Model Output:<br/>[HOLD] [SIZE_0] [SL_UNCHANGED]"]
    
    RAW --> TOKENS --> OUTPUT
    
    style TOKENS fill:#2c3e50,stroke:#1a252f,color:#fff
```

---

## Inference Pipeline

```mermaid
flowchart LR
    subgraph LIVE["Live System"]
        DATA["Real-time<br/>Market Data"]
        TOK["Tokenizer<br/>(<1ms)"]
        MODEL["GGUF Model<br/>(<10ms GPU<br/><100ms CPU)"]
        DECODE["Action<br/>Decoder"]
        EXEC["Execution<br/>Engine"]
    end
    
    DATA --> TOK --> MODEL --> DECODE --> EXEC
    EXEC -->|"State Feedback"| DATA
    
    style MODEL fill:#9b59b6,stroke:#8e44ad,color:#fff
    style EXEC fill:#27ae60,stroke:#1e8449,color:#fff
```

### Latency Targets
- Tokenization: <1ms
- Model inference: <10ms (quantized, GPU) / <100ms (CPU)
- End-to-end decision: <50ms

---

## Model Variants

| Variant | Params | Quantization | Use Case |
|---------|--------|--------------|----------|
| cthulu-nano | 125M | Q4_K_M | Edge/mobile, ultra-fast |
| cthulu-small | 350M | Q5_K_M | Local CPU inference |
| cthulu-base | 1.3B | Q4_K_S | Balanced performance |
| cthulu-large | 7B | Q4_0 | Maximum capability |

---

## Key Challenges

```mermaid
mindmap
  root((Challenges))
    Non-Stationarity
      Markets change over time
      Mitigation: Continuous fine-tuning
      Mitigation: Regime-aware training
    Execution Reality
      Model → Valid broker orders
      Mitigation: Constrained decoding
      Mitigation: Action space validation
    Risk Boundaries
      Cannot exceed limits
      Mitigation: Hard-coded guardrails
      Mitigation: Risk head supervision
    Interpretability
      Why did model decide?
      Mitigation: Attention visualization
      Mitigation: Decision logging
    Overfitting
      Historical data bias
      Mitigation: Cross-validation
      Mitigation: Out-of-sample testing
```

---

## Integration with Current Cthulu

```mermaid
flowchart TB
    subgraph CURRENT["Current Architecture"]
        direction LR
        D1["DataLayer"] --> S1["Strategy<br/>(rule-based)"]
        S1 --> R1["RiskManager"]
        R1 --> E1["ExecutionEngine"]
    end
    
    subgraph FUTURE["Future Architecture"]
        direction LR
        D2["DataLayer"] --> M2["ChuluModel<br/>(learned policy)"]
        M2 --> R2["RiskManager<br/>(hard-coded safety)"]
        R2 --> E2["ExecutionEngine<br/>(hard-coded safety)"]
    end
    
    CURRENT -->|"Evolution"| FUTURE
    
    style S1 fill:#e74c3c,stroke:#c0392b,color:#fff
    style M2 fill:#9b59b6,stroke:#8e44ad,color:#fff
    style R2 fill:#27ae60,stroke:#1e8449,color:#fff
    style E2 fill:#27ae60,stroke:#1e8449,color:#fff
```

The `RiskManager` and `ExecutionEngine` remain as hard-coded safety layers.

---

## Research Questions

1. **Tokenization**: How to best encode continuous market data for transformer input?
2. **Sequence length**: How much history should the model see? (1 hour? 1 day? 1 week?)
3. **Multi-asset**: Single model for all symbols or symbol-specific fine-tuning?
4. **Real-time adaptation**: Online learning during live trading?
5. **Uncertainty quantification**: Can the model express confidence in its decisions?

---

## Next Steps (When In Scope)

- [ ] Design tokenizer for market data + indicators
- [ ] Collect and format training dataset from Cthulu history
- [ ] Prototype small transformer on historical decisions
- [ ] Evaluate against rule-based baseline
- [ ] Iterate on architecture based on results

---

## References

- Decision Transformer (Chen et al., 2021)
- Mamba: Linear-Time Sequence Modeling (Gu & Dao, 2023)
- GGUF format specification (llama.cpp)
- Alpaca/FinGPT financial LLM approaches
- Reinforcement Learning for Trading (various)

---

*This document is a thought experiment. Implementation is NOT in current scope.*
