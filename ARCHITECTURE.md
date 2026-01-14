# System Architecture

> Autonomous Enterprise Operating System with Native AI

---

## High-Level Architecture

```mermaid
flowchart TD
       subgraph GLADIUS [GLADIUS (Autonomous Enterprise Manager)]
              subgraph COGNITION_ENGINE [COGNITION ENGINE]
                     HEKTOR[Hektor VDB<br/>SIMD/HNSW<br/>Vectors]
                     TOOL_ROUTER[Native Tool Router<br/>(<10ms)]
                     MEMORY[Memory Module<br/>Multi-DB]
                     LEARNING[Learning Loop<br/>Training]
                     CONSENSUS[Consensus System<br/>Discord/Email]
                     CONTEXT[Context Manager<br/>Summarization]
                     HEKTOR --> MODEL_STACK
                     TOOL_ROUTER --> MODEL_STACK
                     MEMORY --> MODEL_STACK
                     LEARNING --> MODEL_STACK
                     CONSENSUS --> MODEL_STACK
                     CONTEXT --> MODEL_STACK
                     subgraph MODEL_STACK [MODEL STACK]
                            TOOL_ROUTER2[Tool Router<br/>(tiny GGUF)<br/><10ms]
                            OLLAMA[Ollama LLM<br/>(fallback)<br/>~100ms]
                            GLADIUS_NATIVE[Gladius Native<br/>(future: full)<br/><50ms all tasks]
                     end
              end
       end
       GLADIUS -->|Artifact Alpha| ALPHA[ARTIFACT ALPHA<br/>Syndicate<br/>Research]
       GLADIUS -->|Artifact Beta| BETA[ARTIFACT BETA<br/>Cthulu<br/>Trading]
       GLADIUS -->|Artifact Theta| THETA[ARTIFACT THETA<br/>(Future)<br/>Publishing]
```

---

## Data Flow

```mermaid
flowchart TD
       MarketSources[Market Sources<br/>(yfinance, FRED)] --> SyndicatePipeline
       subgraph SyndicatePipeline [SYNDICATE PIPELINE]
              Journals[Journals]
              Premarket[Premarket]
              Catalysts[Catalysts]
              Calendar[Calendar]
              Journals -->| | CognitionEngine
              Premarket -->| | CognitionEngine
              Catalysts -->| | CognitionEngine
              Calendar -->| | CognitionEngine
       end
       subgraph CognitionEngine [COGNITION ENGINE]
              NativeToolRouter[NativeToolRouter<br/>(route → execute)]
              HektorVDB[Hektor VDB<br/>(ingest → search)]
              TrainingGenerator[TrainingGenerator<br/>(history → dataset)]
              ModelTrainer[ModelTrainer<br/>(train → deploy)]
              ContextManager[ContextManager<br/>(summarize → coherence)]
              ConsensusSystem[ConsensusSystem<br/>(vote → escalate)]
              NativeToolRouter --> HektorVDB
              HektorVDB --> TrainingGenerator
              TrainingGenerator --> ModelTrainer
              TrainingGenerator --> ConsensusSystem
              ContextManager --> TrainingGenerator
       end
       SyndicatePipeline --> CognitionEngine
       ModelTrainer -->|Trade Signals| Cthulu[Cthulu<br/>(Execution)]
       ConsensusSystem -->|Approved| SelfImprove[Self Improve<br/>(Execute)]
```

---

## Cognition Engine Architecture

```mermaid
flowchart TD
       subgraph COGNITION_ENGINE [COGNITION ENGINE]
              subgraph HEKTOR_VDB [HEKTOR VDB]
                     HNSW[HNSW Vectors]
                     BM25[BM25 Lexical]
                     Hybrid[Hybrid Search]
              end
              subgraph INFERENCE_LAYER [INFERENCE LAYER]
                     Llama[llama.cpp<br/>GGUF/GGM]
                     ONNX[ONNX Runtime]
                     NativeEmb[Native Embeddings]
              end
              subgraph MEMORY_MODULE [MEMORY MODULE]
                     MultiDB[Multi-Database Access]
                     ToolCalling[Native Tool Calling]
              end
              subgraph CONSENSUS_LAYER [CONSENSUS LAYER]
                     DiscordVote[Discord Voting]
                     EmailEscalate[Email Escalation]
                     ContextManage[Context Management]
              end
              subgraph FALLBACK_LAYER [FALLBACK LAYER]
                     SQLite[SQLite persistence]
                     TFIDF[TF-IDF embeddings]
                     JSON[JSON export]
              end
       end
```

---

## Consensus System Flow

```mermaid
flowchart TD
       Proposal[Create Proposal] --> AssessImpact{Assess Impact}
       AssessImpact -->|Low| AutoApprove[Auto-Approve]
       AssessImpact -->|Medium| DiscordVote[Discord Community Vote]
       AssessImpact -->|High/Critical| EmailEscalate[Email to Dev Team]
       DiscordVote --> CollectVotes[Collect Votes]
       CollectVotes --> CheckThreshold{60% Threshold?}
       CheckThreshold -->|Yes| Approve[Approve]
       CheckThreshold -->|No| Reject[Reject]
       EmailEscalate --> AwaitReview[Await Review]
       AwaitReview --> DevDecision{Developer Decision}
       DevDecision -->|Approve| Approve
       DevDecision -->|Reject| Reject
       Approve --> Execute[Execute Improvement]
       Execute --> Snapshot[Create Snapshot]
```

---

## Context Management Flow

```mermaid
flowchart TD
       Events[Events/Observations] --> ContextWindow[Context Window]
       ContextWindow --> CheckTokens{Tokens > 6000?}
       CheckTokens -->|No| Continue[Continue]
       CheckTokens -->|Yes| Summarize[Auto-Summarize]
       Summarize --> CompressOld[Compress Old Entries]
       CompressOld --> StoreSummary[Store Summary]
       StoreSummary --> Continue
       Continue --> ExportContext[Export for Training]
```

---

## Memory Module Architecture

```mermaid
flowchart TD
       subgraph MEMORY_MODULE [MEMORY MODULE]
              UnifiedMemory[UNIFIED MEMORY INTERFACE]
              DatabaseHooks[DATABASE HOOKS]
              NativeTool[NATIVE TOOL CALLING]
              Workspace[WORKSPACE ACCESS]
              UnifiedMemory --> DatabaseHooks
              UnifiedMemory --> NativeTool
              UnifiedMemory --> Workspace
              DatabaseHooks --> HektorVDB[Hektor VDB]
              DatabaseHooks --> SQLiteDB[SQLite DBs]
              DatabaseHooks --> JSONStores[JSON stores]
       end
```

---

## Prediction Learning System

```mermaid
flowchart TD
       MarketAnalysis[Market Analysis] --> PredictBias[Predict Bias]
       PredictBias --> RecordOutcome[Record Outcome]
       RecordOutcome --> GradePerformance[Grade Performance]
       GradePerformance --> PatternFeedback[Pattern Feedback]
       PatternFeedback --> MarketAnalysis
```

---

## Training & Self-Improvement System

```mermaid
flowchart TD
       IngestReports[Ingest Reports] --> GenerateTraining[Generate Training Data]
       GenerateTraining --> ProposeImprove[Propose Improvements]
       ProposeImprove --> RouteConsensus[Route to Consensus]
       RouteConsensus --> ExecuteChanges[Execute Changes]
       ExecuteChanges --> SnapshotBenchmark[Snapshot & Benchmark]
       SnapshotBenchmark --> UpdateContext[Update Context]
       UpdateContext --> IngestReports
```

---

## Digital Footprint Architecture

```mermaid
flowchart TD
    subgraph SYNDICATE [SYNDICATE OUTPUTS]
        Journals[Journals]
        Catalysts[Catalysts]
        Monthly[Monthly Reports]
    end
    
    subgraph PUBLISHING [PUBLISHING MODULE]
        Pipeline[Content Pipeline<br/>Ingest/Approve/Schedule]
        Formatters[Format Adapters<br/>Discord/LinkedIn/Twitter/Notion]
        Router[Platform Router<br/>Auth/Publish/Analytics]
    end
    
    subgraph PLATFORMS [PLATFORMS]
        Discord[Discord<br/>via Arty Bot]
        LinkedIn[LinkedIn<br/>via Arty]
        Twitter[Twitter/X<br/>via Automata]
        Notion[Notion<br/>via API]
    end
    
    Journals --> Pipeline
    Catalysts --> Pipeline
    Monthly --> Pipeline
    Pipeline --> Formatters
    Formatters --> Router
    Router --> Discord
    Router --> LinkedIn
    Router --> Twitter
    Router --> Notion
```

---

## Module Summary

| Module | Purpose | Status |
|--------|---------|--------|
| Hektor VDB | Native C++ vector database with SIMD | ✅ Implemented |
| Memory Module | Multi-database access with 16 tools | ✅ Implemented |
| Tool Calling | Native function definitions | ✅ Implemented |
| Training Generator | Generate fine-tuning data | ✅ Implemented |
| Self-Improvement | Autonomous proposals with audit | ✅ Implemented |
| Learning Loop | Continuous learning cycles | ✅ Implemented |
| Consensus System | Discord voting + email escalation | ✅ Implemented |
| Context Manager | Summarization + coherence | ✅ Implemented |
| Native Tool Router | Pattern-based tool routing | ✅ Implemented |
| Model Trainer | GGUF fine-tuning pipeline | 🚧 In Progress |
| **Digital Footprint** | Content pipeline + publishing | ✅ Implemented |
| **Content Pipeline** | Ingest → Approve → Schedule → Track | ✅ Implemented |
| **Format Adapters** | Platform-specific formatting | ✅ Implemented |
| **Platform Router** | Multi-platform publishing | ✅ Implemented |

---

*Last updated: 2026-01-13*
