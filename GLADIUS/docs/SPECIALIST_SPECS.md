# GLADIUS v2.0 - Specialist Specifications

> **Version**: 2.0.0-alpha  
> **Date**: 2026-02-01

---

## Specialist Module Detailed Specifications

### 1. Intent Decoder (`specialists/intent/`)

#### Purpose
Transform raw user input into structured, actionable intent representation.

#### Architecture
```
Input Text → Tokenizer → Encoder (2M params) → Intent Head → Slot Head
                                                    ↓            ↓
                                              Intent Vector   Slot Dict
```

#### Model Spec
| Property | Value |
|----------|-------|
| Parameters | ~2M |
| Hidden Dim | 256 |
| Layers | 4 |
| Attention Heads | 4 |
| Vocab Size | 32000 (shared) |
| Output | Intent embedding (256d) + slots |

#### Training Data
- Intent classification datasets
- Slot filling datasets  
- Synthesized ambiguous queries
- Multi-intent examples

#### Output Schema
```python
{
    "intent_embedding": float[256],
    "primary_intent": str,
    "sub_intents": list[str],
    "confidence": float,
    "slots": dict[str, any],
    "requires_clarification": bool,
    "suggested_clarifications": list[str]
}
```

---

### 2. Context Manager (`specialists/context/`)

#### Purpose
Maintain working memory, retrieve relevant long-term context, compress history.

#### Architecture
```
Current Input ──┐
                ├──► Context Encoder ──► Query Hektor ──► Merge ──► Context Vector
History ────────┘         │                    │
                          ▼                    ▼
                    Working Memory      Retrieved Memories
```

#### Model Spec
| Property | Value |
|----------|-------|
| Parameters | ~3M |
| Hidden Dim | 384 |
| Layers | 6 |
| Attention Heads | 6 |
| Context Window | 4096 tokens |
| Output | Context embedding (384d) |

#### Capabilities
1. **Working Memory**: Last N turns, compressed
2. **Episodic Retrieval**: Similar past interactions
3. **Semantic Retrieval**: Related concepts from Hektor
4. **Temporal Awareness**: Time-weighted relevance

#### Output Schema
```python
{
    "context_embedding": float[384],
    "working_memory": list[dict],
    "retrieved_memories": list[{"content": str, "relevance": float}],
    "memory_summary": str,
    "context_tokens_used": int
}
```

---

### 3. Action Executor (`specialists/action/`)

#### Purpose
Convert decisions into tool calls, monitor execution, handle errors.

#### Architecture
```
Decision + Context ──► Action Planner ──► Tool Selector ──► Param Filler ──► Execute
                                               │                  │
                                               ▼                  ▼
                                          Tool Registry      Validation
```

#### Model Spec
| Property | Value |
|----------|-------|
| Parameters | ~2M |
| Hidden Dim | 256 |
| Layers | 4 |
| Tool Embedding Dim | 128 |
| Max Tools | 256 |
| Output | Action plan + tool calls |

#### Capabilities
1. **Tool Selection**: Match intent to appropriate tools
2. **Parameter Inference**: Fill tool parameters from context
3. **Execution Monitoring**: Track tool execution state
4. **Error Recovery**: Retry logic, alternative tools

#### Output Schema
```python
{
    "action_plan": [
        {
            "tool": str,
            "params": dict,
            "confidence": float,
            "fallback": str | None
        }
    ],
    "execution_order": list[int],
    "parallel_groups": list[list[int]],
    "expected_outcome": str
}
```

---

### 4. Reasoning Engine (`specialists/reasoning/`)

#### Purpose
Logical deduction, planning, chain-of-thought, causal reasoning.

#### Architecture
```
Problem ──► Decomposer ──► Step Generator ──► Verifier ──► Conclusion
                │               │                │
                ▼               ▼                ▼
           Sub-problems   Reasoning Steps   Validity Check
```

#### Model Spec
| Property | Value |
|----------|-------|
| Parameters | ~5M |
| Hidden Dim | 512 |
| Layers | 8 |
| Attention Heads | 8 |
| Max Reasoning Steps | 20 |
| Output | Reasoning trace + conclusion |

#### Capabilities
1. **Deductive Reasoning**: If A then B, A therefore B
2. **Inductive Reasoning**: Pattern generalization
3. **Abductive Reasoning**: Best explanation inference
4. **Planning**: Multi-step goal achievement
5. **Verification**: Self-check reasoning validity

#### Output Schema
```python
{
    "reasoning_trace": [
        {"step": int, "thought": str, "type": str, "confidence": float}
    ],
    "conclusion": str,
    "confidence": float,
    "alternative_conclusions": list[str],
    "assumptions": list[str],
    "validity_score": float
}
```

---

### 5. Math Processor (`specialists/math/`)

#### Purpose
Numerical computation, symbolic math, statistics, equation solving.

#### Architecture
```
Expression ──► Parser ──► Symbolic Engine ──► Numerical Engine ──► Result
                              │                     │
                              ▼                     ▼
                        Symbolic Result      Numerical Result
```

#### Model Spec
| Property | Value |
|----------|-------|
| Parameters | ~3M |
| Hidden Dim | 384 |
| Layers | 6 |
| Precision | float64 |
| Symbolic Support | SymPy integration |
| Output | Numerical + symbolic results |

#### Capabilities
1. **Arithmetic**: Basic operations with high precision
2. **Algebra**: Equation solving, simplification
3. **Calculus**: Derivatives, integrals (symbolic)
4. **Statistics**: Distributions, hypothesis testing
5. **Linear Algebra**: Matrix operations

#### Output Schema
```python
{
    "numerical_result": float | list | matrix,
    "symbolic_result": str | None,
    "computation_steps": list[str],
    "precision": int,
    "unit": str | None,
    "confidence": float
}
```

---

### 6. Code Synthesizer (`specialists/code/`)

#### Purpose
Code generation, debugging, refactoring, explanation.

#### Architecture
```
Specification ──► Intent Parser ──► Code Generator ──► Validator ──► Code
                                          │               │
                                          ▼               ▼
                                     Draft Code      Syntax/Logic Check
```

#### Model Spec
| Property | Value |
|----------|-------|
| Parameters | ~5M |
| Hidden Dim | 512 |
| Layers | 8 |
| Attention Heads | 8 |
| Languages | Python, JS, Bash, Go, Rust |
| Max Code Length | 2048 tokens |
| Output | Code + explanation |

#### Capabilities
1. **Generation**: From spec to code
2. **Completion**: Continue partial code
3. **Debugging**: Identify and fix errors
4. **Refactoring**: Improve existing code
5. **Explanation**: Document code behavior

#### Output Schema
```python
{
    "code": str,
    "language": str,
    "explanation": str,
    "imports_required": list[str],
    "test_cases": list[dict],
    "complexity": {"time": str, "space": str},
    "confidence": float
}
```

---

### 7. Memory Integrator (`specialists/memory/`)

#### Purpose
Bridge between all specialists and Hektor VDB, handle encoding/retrieval.

#### Architecture
```
Content ──► Encoder ──► Hektor Store
                              │
Query ──► Encoder ──► Hektor Search ──► Decoder ──► Retrieved Content
```

#### Model Spec
| Property | Value |
|----------|-------|
| Parameters | ~2M |
| Embedding Dim | 768 (Hektor compatible) |
| Encoder Layers | 4 |
| Decoder Layers | 2 |
| Batch Size | 32 |
| Output | Embeddings + decoded content |

#### Capabilities
1. **Semantic Encoding**: Convert any content to vectors
2. **Similarity Search**: Find related memories
3. **Clustering**: Group related memories
4. **Consolidation**: Merge redundant memories
5. **Forgetting**: Prune low-value memories

#### Output Schema
```python
{
    "embedding": float[768],
    "stored_id": str,
    "retrieved": [
        {"id": str, "content": str, "similarity": float, "metadata": dict}
    ],
    "cluster_id": str | None
}
```

---

### 8. Tool Interface (`specialists/tools/`)

#### Purpose
Interact with 100+ registered external tools, handle I/O formatting.

#### Architecture
```
Tool Request ──► Tool Matcher ──► Schema Validator ──► Executor ──► Output Parser
                     │                  │                              │
                     ▼                  ▼                              ▼
              Tool Registry      Param Validation              Structured Output
```

#### Model Spec
| Property | Value |
|----------|-------|
| Parameters | ~3M |
| Tool Embedding Dim | 256 |
| Max Registered Tools | 512 |
| Schema Format | JSON Schema |
| Output | Tool result + metadata |

#### Capabilities
1. **Tool Discovery**: Find appropriate tool for task
2. **Schema Mapping**: Map intent to tool parameters
3. **Execution**: Invoke tools safely
4. **Output Parsing**: Structure tool outputs
5. **Error Handling**: Graceful degradation

#### Tool Categories (100+)
- **File Operations**: read, write, search, glob
- **Code Tools**: lint, format, test, build
- **Data Tools**: parse, transform, validate
- **Network Tools**: fetch, api_call, webhook
- **System Tools**: process, env, config
- **AI Tools**: embed, classify, generate

#### Output Schema
```python
{
    "tool_name": str,
    "execution_status": "success" | "error" | "timeout",
    "result": any,
    "stdout": str,
    "stderr": str,
    "duration_ms": int,
    "tokens_used": int
}
```

---

## Central Nexus Specification

### Purpose
Orchestrate all specialists, route queries, aggregate outputs.

### Architecture
```
Input ──► Specialist Scorer ──► Top-K Selection ──► Parallel Execution ──► Aggregator
                │                     │                    │                    │
                ▼                     ▼                    ▼                    ▼
          All Specialists      Selected Set         Specialist Outputs    Final Output
```

### Model Spec
| Property | Value |
|----------|-------|
| Parameters | ~5M |
| Hidden Dim | 512 |
| Layers | 6 |
| Specialist Attention | Cross-attention |
| Max Active Specialists | 4 |
| Output | Aggregated response |

### Routing Logic
```python
def route(self, input_embedding, specialist_states):
    # Score each specialist's relevance
    scores = self.scorer(input_embedding, specialist_states)
    
    # Select top-k specialists
    top_k = torch.topk(scores, k=self.max_active)
    
    # Execute in parallel
    outputs = parallel_execute(top_k.indices)
    
    # Weighted aggregation
    weights = F.softmax(top_k.values, dim=-1)
    final = sum(w * o for w, o in zip(weights, outputs))
    
    return final, {
        "activated_specialists": top_k.indices.tolist(),
        "weights": weights.tolist()
    }
```

---

## Total Parameter Count

| Module | Parameters |
|--------|------------|
| Central Nexus | 5M |
| Intent Decoder | 2M |
| Context Manager | 3M |
| Action Executor | 2M |
| Reasoning Engine | 5M |
| Math Processor | 3M |
| Code Synthesizer | 5M |
| Memory Integrator | 2M |
| Tool Interface | 3M |
| **TOTAL** | **~30M** |

This is significantly smaller than monolithic LLMs while achieving specialized excellence.

---

## Training Requirements

### Compute
- GPU: RTX 3090 or better (for parallel specialist training)
- CPU: 16+ cores (for CPU-mode training)
- RAM: 32GB minimum
- Storage: 100GB for datasets + checkpoints

### Data Requirements (per specialist)
- Intent Decoder: 500K intent examples
- Context Manager: 1M conversation turns
- Action Executor: 100K tool usage examples
- Reasoning Engine: 500K reasoning traces
- Math Processor: 1M math problems
- Code Synthesizer: 5M code snippets
- Memory Integrator: Self-supervised on Hektor
- Tool Interface: 50K tool invocations

### Training Time Estimates
- Per specialist: 4-8 hours (GPU), 24-48 hours (CPU)
- Nexus training: 8-12 hours
- Joint fine-tuning: 4-6 hours
- **Total**: ~1 week for full system

---

*"Specialization enables mastery. Coordination enables intelligence."*
