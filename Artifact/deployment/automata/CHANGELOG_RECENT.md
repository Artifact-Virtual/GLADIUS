# Recent Changes (most recent at top)

Date: 2026-01-11

- Added editorial pipeline endpoints and CLI integration
  - `POST /api/content/generate` (already present) saves drafts to `content_items` in context DB when content generated
  - `POST /api/content/editorial` runs batch editorial pipeline and writes final markdown files
  - `POST /api/content/drafts` (create a draft manually)
  - `GET /api/content/drafts` (list drafts; optional `status` filter)
  - `POST /api/content/drafts/<id>/finalize` (finalize a single draft, produce final markdown and update DB)

- Added `ai_engine/content_store.py` - ContentStore DAO
  - Creates `content_items` table in `~/.automata/context.db`
  - CRUD helpers: `create`, `list`, `get`, `update_status`

- Content storage locations
  - Drafts (CLI & generator): `Artifact/research_outputs/articles/draft_*.json` (existing)
  - Final articles: `Artifact/deployment/research_outputs/articles/final_*.md`
  - Batch summaries: `Artifact/deployment/research_outputs/articles/summary_*.md`

- AI Provider handling
  - Added/validated Ollama local model usage (`AI_PROVIDER=ollama`, `AI_MODEL=llama3.2` recommended)
  - Gemini was tested; ADC required for cloud-based Gemini usage

- Notes and next steps
  - Added `CONTENT_PIPELINES.md` documenting DB tables and recommended pipelines
  - Next: add background workers for editorial batch processing and embedding computation, add UI controls to manage drafts and finalization
