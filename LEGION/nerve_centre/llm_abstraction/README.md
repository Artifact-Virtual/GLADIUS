## LLM Abstraction Subsystem Documentation

### Overview

This subsystem provides a unified, configurable interface for interacting with multiple LLM providers (Ollama, Llama.cpp, OpenAI, Anthropic, etc.) in the enterprise system. It centralizes configuration, optimizes for speed/efficiency, and supports advanced prompt engineering, context management, and output processing.

### Configuration

- All provider settings, optimization flags (FlashAttention, quantization, num_threads), and active provider selection are managed in `/enterprise/config/llm_config.json`.

- Secrets, API keys, and endpoints are managed in `/enterprise/config/.env`.

- Only one provider is active at a time; swapping is done by changing the config.

### Main Components

- `llm_abstraction.py`: Unified entry point for LLM queries. Handles prompt engineering, context optimization, and output processing.

- `providers.py`: Provider classes for Ollama, Llama.cpp, OpenAI, Anthropic, etc. All use config-driven options and optimization flags.

- `provider_factory.py`: Instantiates only the active provider based on config.

- `config_manager.py`: Loads and validates config and environment variables.

- `base.py`: Base classes and enums for providers, requests, responses, and security levels.

### Optimization Features

- FlashAttention, quantization, and multi-threading are supported for local providers (Ollama, Llama.cpp) via config flags.

- Context trimming and prioritization ensure efficient token usage.

- Output ranking uses coherence, relevance, completeness, and accuracy metrics.

### Install & Setup

- Use `install.py` to automate Ollama installation, model pull, and server startup on port 11434 (or as configured).

- For Llama.cpp, follow build/run instructions in the main README or ARCHITECTURE.md.

### Usage

- Query the abstraction via `LLMAbstraction.query(prompt, context, ...)`.

- All requests and responses are structured and include metadata, metrics, and security filtering.

- Advanced orchestration and multi-provider workflows are supported via `LLMOrchestrator`.

### Security

- SecurityLevel enum and output processor filter sensitive content (API keys, secrets, etc.).

- All secrets are loaded from `.env` and never hardcoded.

### Extensibility

- Add new providers by extending `LLMProviderBase` and updating config.

- All logic is modular and testable.

### Troubleshooting

- If the backend server is unavailable, ensure Ollama is running on the configured port.

- Check logs for serialization or import errors; circular imports have been resolved by moving base classes.

### Changelog

- Centralized config and .env

- Provider classes refactored for config-driven options

- Optimization flags added

- Install logic automated

- Documentation fully updated

### See Also

- `/enterprise/config/llm_config.json` for provider settings

- `/enterprise/config/.env` for secrets

- `ARCHITECTURE.md` and `blueprint.md` for system design details
