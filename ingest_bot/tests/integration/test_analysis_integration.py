import os
import json
import pytest
from pathlib import Path

from ingest_bot.orchestrator import main as orchestrator_main
from ingest_bot.analysis import analyze_records

pytestmark = pytest.mark.skipif(os.environ.get('RUN_INTEGRATION') != '1', reason='Integration tests require RUN_INTEGRATION=1')


def test_full_integration_btc(tmp_path):
    # run an orchestrator live run for BTC and then run analysis/backtest/plot
    since = '2025-01-01T00:00:00'
    rc = orchestrator_main(['--once', '--source', 'btc', '--adapter', 'yfinance_adapter', '--since', since, '--dest-dir', str(tmp_path / 'data'), '--save-records'])
    assert rc == 0
    records_file = Path(tmp_path / 'data' / 'btc' / 'records.json')
    assert records_file.exists()
    report = analyze_records(records_file, save_plots_to=Path(tmp_path / 'reports'))
    assert 'summary' in report
    assert Path(report['plot']).exists()
