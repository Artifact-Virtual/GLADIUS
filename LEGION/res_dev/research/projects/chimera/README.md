# Chimera Project

This directory contains the core components of the Chimera project, an agent orchestration system.

## Overview

Chimera is designed to manage and interact with various AI agents, providing different communication protocols for flexibility and scalability.

## Directory Structure

- `agents/`: Contains individual AI agents, each with its own directory and `main.py` implementation.
- `api/`: Implements the FastAPI-based HTTP API for interacting with the agents.
- `core/`: Houses the `ChimeraOrchestrator`, responsible for discovering, loading, and managing agents.
- `grpc/`: Contains the Protocol Buffer definitions, generated gRPC stubs, and the gRPC server and client implementations for high-performance communication.
- `memory/`: (Placeholder) Intended for agent memory management components.

## Getting Started

Refer to the `USAGE_GUIDE.md` file in this directory for detailed instructions on how to run the Chimera Orchestrator, interact with agents via direct execution, FastAPI, and gRPC.
