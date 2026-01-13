# General intelligence — organized by complexity (low → high)

## 💼 Business & productivity
- Decision support — forecasting, prescriptive analytics, optimization engines
- Knowledge work automation — automated note‑taking, summarization, contract analysis
- Customer‑facing automation — chatbots, virtual agents, personalized recommendations

## 🎨 Creative media
- Generative media — images, video, music, 3D assets, VFX pipelines (diffusion, GANs)
- Narrative & game AI — procedural content generation, dialog systems, NPC behavior
- Content pipelines — automated editing, localization, adaptive content generation

## Core data infrastructure (ingest & storage)
- Data ingestion & integration — APIs, streaming, scraping, IoT telemetry (Kafka, Kinesis, Playwright, sensor drivers)
- Data storage & versioning — object stores, data lakes, data versioning (S3, Delta Lake, LakeFS, DVC)
- Data labeling & augmentation — managed platforms, synthetic data, active learning (Labelbox, Scale AI, GANs/diffusion)
- Data quality & lineage — validation, drift detection, lineage tools (Great Expectations, WhyLabs)

## 🔍 Search & retrieval / Perception basics
- Vector search & retrieval — embeddings, ANN stores (FAISS, Milvus, Pinecone)
- Perception & interaction
    - Computer vision — detection, segmentation, 3D reconstruction, SLAM
    - Audio & speech — ASR, TTS, voice conversion, speaker recognition
    - NLP & language — LLMs, summarization, translation, QA, instruction‑following, code generation

## 🧪 Simulation, robotics & domain applications
- Simulation & control — physics/environment simulators (Isaac Gym, MuJoCo, Brax, Unity, Unreal)
- Robot stacks & controllers — ROS, MoveIt, real‑time motion control, sim‑to‑real
- Digital twins — system replicas for planning/testing
- Scientific & domain applications — literature mining, lab automation (safety/ethics), healthcare analytics, materials/chemistry modeling

## 🧠 Model development & training
- Frameworks & libs — PyTorch, TensorFlow, JAX
- Distributed & efficient training — multi‑GPU, ZeRO/DeepSpeed, Spark, Horovod
- AutoML & hyperparameter tuning — Optuna, Ray Tune, AutoGluon
- Pretraining & fine‑tuning — supervised, self‑supervised, RLHF, reward modeling
- Federated & privacy‑preserving training — federated learning, DP‑SGD, secure aggregation
- Synthetic experiment generation — simulated data/scenario generation for rare events

## ⚡️ Model optimization & deployment
- Compression & optimization — quantization, pruning, structured sparsity, distillation
- Model compilers & runtimes — TVM, TensorRT, ONNX Runtime
- Serving & scaling — Triton, TorchServe, BentoML, serverless inference
- Edge & IoT deployment — TFLite, ONNX, edge orchestration, OTA updates

## 📈 MLOps, observability & lifecycle
- Lifecycle platforms — MLflow, Kubeflow, TFX, SageMaker
- CI/CD for ML — training CI, model promotion, canaries, shadow testing
- Monitoring & SLOs — telemetry, drift detection, Prometheus, Grafana
- Experiment tracking & reproducibility — experiment DBs, artifact registries

## 🤖 Agents, orchestration & automation
- General‑purpose agent frameworks — LangChain, AutoGen, Ray, Copilot‑style orchestration
- Multi‑agent systems — coordination, negotiation, emergent behavior testing
- RPA & system automation — UiPath, Power Automate, Playwright, Selenium
- Self‑improvement loops — self‑monitoring agents, automated retraining pipelines (with governance)

## 🛡 Security, robustness & safety tooling
- Adversarial testing & red teaming — robustness evaluation, stress tests, jailbreak checks (ethical)
- Privacy & secure computation — homomorphic encryption, secure enclaves (SGX), private inference
- Monitoring for misuse — anomaly detection, content moderation, tripwires, policy enforcement

## 🔍 Explainability, verification & governance
- Interpretability tools — SHAP, LIME, Integrated Gradients, concept activation
- Formal verification & testing — model checking, constrained verification for controllers
- Governance & compliance — model cards, documentation, audit trails, regulatory reporting
- Fairness & bias auditing — fairness metrics, counterfactual testing, remediation tooling

## 💾 Intellectual property & provenance
- Model & data provenance — lineage tracking, dataset fingerprints, licensing metadata
- Watermarking & traceability — synthetic content watermarking, attribution tools

## 🧾 Legal, ethics & human oversight
- Regulatory compliance — audit workflows, compliance checks, human‑in‑the‑loop approvals
- Safety operations — incident response, model recall mechanisms, escalation
- Ethical auditing — third‑party reviews, independent red teams, stakeholder engagement

## 🔭 Evaluation & benchmarking
- Standard & custom benchmarks — MMLU, BIG-bench, domain benchmarks
- Continuous evaluation — online A/B tests, adversarial evaluation suites, user feedback loops

## 🧩 Emerging / AGI‑centric capabilities (highest complexity)
- Long‑term memory & retrieval systems — persistent episodic memory stores, lifelong learning
- Meta‑learning / self‑improvement — agents that adapt architectures, hyperparameters, strategies
- Capability containment & oversight — dynamic capability gating, provable tripwires
- Multi‑modal cognitive architectures — integrated reasoning across modalities and timescales

Quick reference cheat‑sheet (examples)
- Data: Kafka, S3, DVC
- Training: PyTorch, DeepSpeed, Optuna
- Serving: Triton, BentoML, ONNX
- Agents: LangChain, Ray, AutoGen
- Search: FAISS, Pinecone, Milvus