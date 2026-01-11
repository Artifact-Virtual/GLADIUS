"""Publish worker: polls ContentStore for final items and publishes them (schedules posts).

Provides run_once for tests and start/stop loops for background mode.
"""
import threading
import time
import logging
import json
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


class PublishWorker:
    def __init__(self, content_store, orchestrator=None, interval: int = 30):
        self.content_store = content_store
        self.orchestrator = orchestrator
        self.interval = interval
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("PublishWorker started")

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("PublishWorker stopped")

    def _run_loop(self):
        while not self._stop_event.is_set():
            try:
                self.run_once()
            except Exception as e:
                logger.exception(f"PublishWorker run error: {e}")
            time.sleep(self.interval)

    def run_once(self):
        # Find one final item without published_at and publish it
        finals = self.content_store.list(status='final')
        if not finals:
            return None
        item = None
        # Prefer items with export_path but accept any final item without published_at
        for it in finals:
            if it.get('published_at'):
                continue
            if it.get('export_path'):
                item = it
                break
        if not item:
            # fallback: pick first final without published_at
            for it in finals:
                if not it.get('published_at'):
                    item = it
                    break
        if not item:
            return None

        item_id = item['id']
        logger.info(f"PublishWorker: publishing {item_id}")
        # Attempt to schedule immediate post via orchestrator if available
        publish_result = None
        try:
            # Prefer posting directly via social_manager for immediate feedback
            if self.orchestrator and getattr(self.orchestrator, 'social_manager', None):
                import asyncio
                social = self.orchestrator.social_manager
                # Assume social_manager.post_content is async and returns dict
                res = asyncio.run(social.post_content(platform=item.get('platform','LinkedIn'), content={'text': item.get('text') or item.get('content',{}), 'title': item.get('title')}))
                publish_result = res if isinstance(res, dict) else {'success': True, 'post_id': res}
            elif self.orchestrator:
                # Fall back to scheduling which will be picked up by the orchestrator
                import asyncio
                post_id = asyncio.run(self.orchestrator.schedule_post(platform=item.get('platform','LinkedIn'), content={'text': item.get('text') or item.get('content',{}), 'title': item.get('title')}))
                publish_result = {'success': True, 'post_id': post_id}
            else:
                # simulate publish
                publish_result = {'success': True, 'post_id': f"sim_{item_id}", 'url': f"https://mocked.platform/sim_{item_id}", 'analytics': {'likes':0}}
        except Exception as e:
            logger.exception(f"Failed to publish {item_id}: {e}")
            publish_result = {'success': False, 'error': str(e)}

        # record result
        if publish_result.get('success'):
            pub_url = publish_result.get('url') or f"https://mocked.platform/{publish_result.get('post_id')}"
            metrics = publish_result.get('analytics') or publish_result.get('metrics') or {}
            # store URL and metrics
            self.content_store.update_status(item_id, 'published', published_url=pub_url, published_at=datetime.now(timezone.utc).isoformat(), publish_metrics=json.dumps(metrics))
            logger.info(f"Published {item_id} -> {pub_url} (metrics={metrics})")
            return {'id': item_id, 'url': pub_url}
        else:
            # Mark as failed
            self.content_store.update_status(item_id, 'failed', publish_error=publish_result.get('error'))
            logger.warning(f"Publish failed for {item_id}: {publish_result.get('error')}")
            return {'id': item_id, 'error': publish_result.get('error')}
