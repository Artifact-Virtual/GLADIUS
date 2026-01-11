import sys
from pathlib import Path
import pytest
from datetime import datetime

# ensure project package root is importable
proj_root = Path(__file__).resolve().parents[3]
if str(proj_root) not in sys.path:
    sys.path.insert(0, str(proj_root))

from deployment.automata.ai_engine.publish_worker import PublishWorker


class FakeContentStore:
    def __init__(self):
        self.items = {}

    def list(self, status=None):
        return [v for v in self.items.values() if v.get('status') == status]

    def update_status(self, item_id, new_status, **kwargs):
        if item_id in self.items:
            self.items[item_id]['status'] = new_status
            for k, v in kwargs.items():
                self.items[item_id][k] = v


class BadSocialManager:
    async def post_content(self, platform, content):
        raise RuntimeError('Platform LinkedIn not enabled or not found')


class FakeOrchestrator:
    def __init__(self):
        self.social_manager = BadSocialManager()


def test_publish_worker_records_publish_error():
    store = FakeContentStore()
    # create a final item that is ready to publish
    store.items['item1'] = {'id': 'item1', 'status': 'final', 'text': 'hello', 'title': 't', 'platform': 'LinkedIn'}

    worker = PublishWorker(content_store=store, orchestrator=FakeOrchestrator())

    res = worker.run_once()

    assert 'error' in res or ('id' in res and store.items['item1']['status'] == 'failed')
    assert store.items['item1'].get('publish_error') is not None
    assert 'LinkedIn' in store.items['item1']['publish_error'] or 'not found' in store.items['item1']['publish_error']
