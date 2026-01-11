import logging
import os
import importlib

import pytest

from main import Config, FallbackLLMProvider


def test_prefer_provider_promotes_when_available(monkeypatch):
    cfg = Config()

    class DummyOllama:
        def __init__(self, *args, **kwargs):
            self.name = "Ollama (mock)"
            self.is_available = True

    class DummyGemini:
        def __init__(self, *args, **kwargs):
            self.name = "Gemini (mock)"
            self.is_available = True

    monkeypatch.setattr(__import__('main'), 'OllamaProvider', DummyOllama)
    monkeypatch.setattr(__import__('main'), 'GeminiProvider', DummyGemini)

    fb = FallbackLLMProvider(cfg, logging.getLogger("test"))

    # By default (no PREFER_OLLAMA) Gemini would be primary. Force Ollama as primary
    # to simulate config where Gemini isn't current, then prefer Gemini for a task
    fb._current = fb._providers[0] if fb._providers else None

    # Ensure prefer_provider sets Gemini as current when available
    applied = fb.prefer_provider('gemini')
    assert applied
    assert fb._current.name.lower().startswith('gemini')


def test_strict_provider_enforced(monkeypatch, tmp_path):
    # Ensure strict hint forces provider initialization
    monkeypatch.setenv('LLM_PROVIDER', '')
    monkeypatch.setenv('GEMINI_API_KEY', 'dummy')

    # Patch GeminiProvider to a simple available class
    class DummyGemini:
        def __init__(self, *args, **kwargs):
            self.name = "Gemini (mock)"
            self.is_available = True

    monkeypatch.setattr(__import__('main'), 'GeminiProvider', DummyGemini)

    cfg = Config()
    # Create provider with strict:gemini by temporarily setting env inside create
    old = os.environ.get('LLM_PROVIDER')
    try:
        os.environ['LLM_PROVIDER'] = 'gemini'
        fb = FallbackLLMProvider(cfg, logging.getLogger("test"))
        assert fb._current is not None
        assert fb._current.name.lower().startswith('gemini')
    finally:
        if old is None:
            os.environ.pop('LLM_PROVIDER', None)
        else:
            os.environ['LLM_PROVIDER'] = old
