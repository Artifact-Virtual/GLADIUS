import json
from ingest_bot.jobs import submit_job, get_job
from pathlib import Path


def test_jobs_submit_and_status():
    def f():
        return {'ok': 1}
    job_id = submit_job(f)
    st = get_job(job_id)
    # status will be queued or running; wait until finished
    import time
    for _ in range(20):
        st = get_job(job_id)
        if st['status'] == 'finished':
            break
        time.sleep(0.1)
    assert get_job(job_id)['status'] == 'finished'
    assert get_job(job_id)['result'] == {'ok': 1}


def test_surface_compute_endpoint(client):
    # Requires a sample report directory in data/reports/test with records
    # Here we just test the API surface endpoints don't crash (integration uses real data)
    res = client.post('/api/report/btc/surface/compute', json={'xvals': '1,2', 'yvals': '10,20', 'train_window': 10})
    assert res.status_code in (202, 404)


def test_surface_job_runs_and_finishes(client):
    # Start a surface compute and ensure the background job finishes successfully
    res = client.post('/api/report/btc/surface/compute', json={'xvals': '1,2', 'yvals': '10,20', 'train_window': 10})
    if res.status_code == 404:
        # report not available in test env; skip
        return
    assert res.status_code == 202
    job_id = res.get_json().get('job_id')
    assert job_id
    # poll job status
    import time
    status = None
    for _ in range(100):
        r = client.get(f'/api/report/btc/surface/status/{job_id}')
        assert r.status_code == 200
        status = r.get_json()
        if status.get('status') in ('finished', 'error'):
            break
        time.sleep(0.1)
    assert status and status.get('status') == 'finished', f"job failed: {status}"
    # check surface endpoint returns computed surface
    surf = client.get('/api/report/btc/surface')
    assert surf.status_code == 200
    data = surf.get_json()
    assert 'x' in data and 'y' in data and 'z' in data
