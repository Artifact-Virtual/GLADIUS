"""Editorial worker: polls ContentStore for draft items and finalizes them automatically.

Provides a simple `run_once()` method for deterministic unit tests and a `start()`/`stop()` loop for background usage.
"""
import threading
import time
import logging
from typing import Optional
from datetime import datetime, timezone
from .content_store import ContentStore

logger = logging.getLogger(__name__)


class EditorialWorker:
    def __init__(self, content_store: ContentStore, content_generator=None, interval: int = 30):
        self.content_store = content_store
        self.content_generator = content_generator
        self.interval = interval
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("EditorialWorker started")

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("EditorialWorker stopped")

    def _run_loop(self):
        while not self._stop_event.is_set():
            try:
                self.run_once()
            except Exception as e:
                logger.exception(f"EditorialWorker run error: {e}")
            time.sleep(self.interval)

    def run_once(self):
        # Find one draft and finalize it
        drafts = self.content_store.list(status='draft')
        if not drafts:
            return None
        item = drafts[0]
        item_id = item['id']
        logger.info(f"EditorialWorker: processing draft {item_id}")
        # Use content_generator if provided, otherwise create a simple pass-through
        draft_text = (item.get('content') or {}).get('text', '') if isinstance(item.get('content'), dict) else item.get('content') or ''
        parsed = None
        if self.content_generator and getattr(self.content_generator, 'ai_provider', None):
            # reuse existing _improve_draft helper via content_generator if available
            try:
                # The generator has a _improve_draft helper function in app module; to avoid circular import, do a simple format
                parsed = self._improve_with_ai(draft_text, item.get('topic') or '')
            except Exception as e:
                logger.exception(f"AI improvement failed for {item_id}: {e}")
                parsed = {'title': item.get('topic') or 'Article', 'article': draft_text, 'summary': draft_text[:300], 'tags': []}
        else:
            parsed = {'title': item.get('topic') or 'Article', 'article': draft_text, 'summary': draft_text[:300], 'tags': []}

        # Save final markdown
        out_dir = self.content_store.db_path.parent.parent / 'deployment' / 'research_outputs' / 'articles'
        out_dir.mkdir(parents=True, exist_ok=True)
        filename = f"final_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{item_id}.md"
        md = f"# {parsed.get('title')}\n\n" + (parsed.get('article') or '') + '\n\n' + f"**Summary:** {parsed.get('summary','')}\n\n" + f"**Tags:** {', '.join(parsed.get('tags',[]))}\n"
        fpath = out_dir / filename
        fpath.write_text(md, encoding='utf-8')

        # Update store
        self.content_store.update_status(item_id, 'final', export_path=str(fpath), title=parsed.get('title'), text=(parsed.get('article') or ''))
        logger.info(f"EditorialWorker: finalized draft {item_id} -> {fpath}")
        return item_id

    def _improve_with_ai(self, draft_text, topic):
        # Synchronous wrapper calling content_generator.ai_provider
        import asyncio
        ai = self.content_generator.ai_provider
        prompt = f"You are an expert editor. Improve the following article draft into a polished, publication-ready article. Return a JSON object with keys: title, article (markdown), summary, tags.\n\nDraft:\n{draft_text}\n\nRespond only in JSON."
        res = asyncio.run(ai.generate(prompt=prompt, system_message="You are an assistant that edits and formats articles.", temperature=0.2, max_tokens=1500))
        content = res.get('content', '')
        try:
            import json
            parsed = json.loads(content)
        except Exception:
            parsed = {'title': topic or 'Article', 'article': content, 'summary': content[:300], 'tags': []}
        return parsed
