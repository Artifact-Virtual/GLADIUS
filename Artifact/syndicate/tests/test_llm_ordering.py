import os
import logging
import importlib

import pytest

from main import Config, FallbackLLMProvider


def test_prefer_ollama_over_gemini(monkeypatch):
    # Force Ollama preference
    monkeypatch.setenv("PREFER_OLLAMA", "1")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy_key")

    # Dummy providers
    class DummyOllama:
        def __init__(self, *args, **kwargs):
            self.name = "Ollama (mock)"
            self.is_available = True

    class DummyGemini:
        def __init__(self, *args, **kwargs):
            self.name = "Gemini (mock)"
            self.is_available = True

    # Patch provider classes in main
    import main as main_mod
    monkeypatch.setattr(main_mod, "OllamaProvider", DummyOllama)
    monkeypatch.setattr(main_mod, "GeminiProvider", DummyGemini)

    cfg = Config()
    fb = FallbackLLMProvider(cfg, logging.getLogger("test"))

    # Ollama should be selected as primary
    assert fb._current is not None
    assert fb._current.name.startswith("Ollama")
    assert fb._providers[0].name.startswith("Ollama")
