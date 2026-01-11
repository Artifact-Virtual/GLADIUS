import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import tempfile
from automata.ai_engine.content_store import ContentStore
from automata.ai_engine.editorial_worker import EditorialWorker
from automata.ai_engine.publish_worker import PublishWorker

class DummyAI:
    def __init__(self):
        pass
    async def generate(self, prompt, system_message=None, temperature=None, max_tokens=None):
        # Return a predictable JSON editing result
        return {'content': '{"title": "Edited","article":"Edited text","summary":"short","tags":["tag1"]}'}


def test_editorial_worker_run_once(tmp_path):
    db = tmp_path / 'ctx.db'
    cs = ContentStore(str(db))
    cs.create('d1','LinkedIn','Topic1', {'text':'Draft content'}, status='draft')
    dummy_generator = type('G', (), {'ai_provider': DummyAI()})()
    worker = EditorialWorker(content_store=cs, content_generator=dummy_generator)
    res = worker.run_once()
    assert res == 'd1'
    it = cs.get('d1')
    assert it['status'] == 'final'
    assert it['export_path'] is not None


def test_publish_worker_run_once(tmp_path):
    db = tmp_path / 'ctx2.db'
    cs = ContentStore(str(db))
    # Create final item
    cs.create('f1','LinkedIn','Topic1', {'text':'Final content'}, status='final')
    worker = PublishWorker(content_store=cs, orchestrator=None)
    res = worker.run_once()
    assert res and res['id'] == 'f1'
    it = cs.get('f1')
    assert it['status'] == 'published'
    assert it.get('published_url') is not None