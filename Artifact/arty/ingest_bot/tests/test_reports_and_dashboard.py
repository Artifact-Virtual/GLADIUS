import json
from pathlib import Path
from ingest_bot.reports import save_report


def test_save_report(tmp_path):
    report = {
        'summary': {'last_close': 100},
        'predictions': {'linear': {'predicted_close': 101}},
        'evals': {'in_sample_linear': {'mse': 1}},
        'last_rows': [{'timestamp': '2020-01-01', 'close': 100}],
        'plot': None
    }
    dest = tmp_path / 'reports' / 'r1'
    save_report(report, dest)
    assert (dest / 'summary.json').exists()
    assert (dest / 'predictions.json').exists()
    assert (dest / 'evals.json').exists()
    assert (dest / 'last_rows.csv').exists()


def test_dashboard_imports(client):
    # smoke test dashboard endpoints (list reports)
    res = client.get('/api/reports')
    assert res.status_code == 200
    # test report fetch (may be empty)
    res2 = client.get('/api/report/btc')
    assert res2.status_code in (200, 404)
