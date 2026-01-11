import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import tempfile
import sqlite3
from automata.ai_engine.content_store import ContentStore

def test_content_store_create_list_get_update(tmp_path):
    db = tmp_path / 'test_context.db'
    cs = ContentStore(str(db))

    cs.create(item_id='c1', platform='LinkedIn', topic='T1', content={'text':'Hello world'}, status='draft')
    items = cs.list(status='draft')
    assert len(items) == 1
    it = cs.get('c1')
    assert it['id'] == 'c1'
    assert it['platform'] == 'LinkedIn'

    cs.update_status('c1', 'final', export_path='/tmp/f.md')
    it2 = cs.get('c1')
    assert it2['status'] == 'final'
    assert it2['export_path'] == '/tmp/f.md'