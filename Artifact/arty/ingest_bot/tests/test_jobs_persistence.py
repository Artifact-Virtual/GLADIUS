import os
import json
import time
from pathlib import Path
from ingest_bot.jobs import submit_job, get_job, JOBS_FILE


def test_jobs_persist(tmp_path):
    # use a temp jobs file
    os.environ['INGEST_JOB_FILE'] = str(tmp_path / 'jobs.json')
    # reload module to pick up env var
    import importlib
    import ingest_bot.jobs as jobs_mod
    importlib.reload(jobs_mod)

    def f():
        return {'ok': True}

    jid = jobs_mod.submit_job(f)
    # wait for completion
    for _ in range(40):
        st = jobs_mod.get_job(jid)
        if st['status'] == 'finished':
            break
        time.sleep(0.05)
    assert jobs_mod.get_job(jid)['status'] == 'finished'
    # check file exists
    jf = Path(os.environ['INGEST_JOB_FILE'])
    assert jf.exists()
    d = json.loads(jf.read_text(encoding='utf-8'))
    assert jid in d
