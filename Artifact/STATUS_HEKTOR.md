Hektor build status

We attempted to build Hektor (pyvdb) but encountered ggml/llama compilation errors on this host (SIMD intrinsics issue). Per decision, Hektor is **skipped for now** and ContextEngine will use the SQLite fallback (`context_embeddings` + brute-force cosine) for similarity search.

If you want to enable Hektor later:
- Build and install `pyvdb` into the runtime venv (see `gladius/vendor/hektor/docs/22_PYTHON_BINDINGS.md`).
- Set `vector_db_path` in Automata config to point to the Hektor DB directory.
- Restart the dashboard - ContextEngine will auto-detect `pyvdb` and use it if available.
