# LLM Abstraction Subsystem Architecture

## Purpose
This subsystem abstracts and manages interactions with large language models, providing a unified, secure, and maintainable interface for enterprise-grade workflows.

## Components
- **Config Manager**: Loads all provider settings from `llm_config.json` and secrets from `.env`
- **Provider Factory**: Instantiates only the active provider
- **Core Interface**: Unified API for LLM operations (query, context, metadata)
- **Algorithmic Layer**: Prompt engineering, context management, output post-processing
- **Security Layer**: Authentication, authorization, compliance checks
- **Integration Hooks**: Connects to other NC subsystems (Core, Matrix, Security, etc.)

## Technical Blueprint
- Centralized configuration in `/enterprise/config/llm_config.json`
- Only one provider active at a time, easily swappable
- Testable via `tests/` with mock and real endpoints

## Expansion Points
- Add new providers by updating the config and implementing provider classes
- Integrate with NC agents for autonomous operation

See `blueprint.md` for technical blueprints and integration diagrams.
