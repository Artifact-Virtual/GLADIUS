"""Minimal Flask dashboard to browse saved reports and parameter surfaces.

Run: python -m ingest_bot.dashboard --host 0.0.0.0 --port 8050

This server serves a simple HTML UI that fetches JSON from /api/report/<name>
and renders Plotly charts client-side.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from flask import Flask, jsonify, render_template, send_from_directory, request

app = Flask(__name__, template_folder=str(Path(__file__).parent / 'templates'))

REPORT_ROOT = Path(__file__).parent / 'data' / 'reports'


@app.route('/')
def index():
    return render_template('dashboard.html')


@app.route('/api/reports')
def list_reports():
    root = REPORT_ROOT
    if not root.exists():
        return jsonify([])
    items = [p.name for p in root.iterdir() if p.is_dir()]
    return jsonify(items)


@app.route('/api/report/<name>')
def get_report(name: str):
    p = REPORT_ROOT / name
    if not p.exists():
        return jsonify({'error': 'not found'}), 404
    data = {}
    for fname in ('summary.json', 'predictions.json', 'evals.json'):
        f = p / fname
        if f.exists():
            data[fname.replace('.json', '')] = json.loads(f.read_text(encoding='utf-8'))
    # include surface if available
    sf = p / 'surface.json'
    if sf.exists():
        data['surface'] = json.loads(sf.read_text(encoding='utf-8'))
    return jsonify(data)


@app.route('/api/report/<name>/timeseries')
def report_timeseries(name: str):
    """Return timeseries data (prices, indicators, equity, drawdown, returns) for Plotly charts."""
    p = REPORT_ROOT / name
    # prefer report JSON if present (contains last_rows, plot references)
    report_file = p / 'report.json'
    if report_file.exists():
        r = json.loads(report_file.read_text(encoding='utf-8'))
        # last_rows is list of dicts with timestamp and close and indicators
        last_rows = r.get('last_rows', [])
        series = { 'timestamps': [], 'close': [] }
        # optional: sma_*, bias_* columns
        sma_keys = [k for k in last_rows[0].keys() if k.startswith('sma_')] if last_rows else []
        sma_series = {k: [] for k in sma_keys}
        equity = []
        drawdown = []
        # attempt to load equity/drawdown from data/reports
        for row in last_rows:
            series['timestamps'].append(row.get('timestamp'))
            series['close'].append(row.get('close'))
            for k in sma_keys:
                sma_series[k].append(row.get(k))
        # look for persisted equity and drawdown images/data if available
        # also attempt to load data/reports/<name>/report.json for metrics
        metrics_file = p / 'report.json'
        # assemble response
        resp = {'series': series, 'sma': sma_series, 'meta': r.get('summary', {})}
        return jsonify(resp)
    # fallback: read raw records
    records_path = Path(__file__).parent.parent / 'data' / name / 'records.json'
    if not records_path.exists():
        return jsonify({'error': 'not found'}), 404
    data = json.loads(records_path.read_text(encoding='utf-8'))
    # build series
    timestamps = [r.get('timestamp') for r in data]
    close = [r.get('close') for r in data]
    return jsonify({'series': {'timestamps': timestamps, 'close': close}, 'sma': {}, 'meta': {}})


@app.route('/api/report/<name>/surface')
def compute_surface(name: str):
    """Compute or return saved parameter surface for a report.

    Query params (optional): xkey, ykey, xvals (comma list), yvals (comma list), train_window
    This endpoint will return cached surface if available.
    To start an async computation, POST to `/api/report/<name>/surface/compute`.
    """
    p = REPORT_ROOT / name
    if not p.exists():
        return jsonify({'error': 'not found'}), 404

    # look for existing surface
    sf = p / 'surface.json'
    if sf.exists():
        return jsonify(json.loads(sf.read_text(encoding='utf-8')))

    return jsonify({'status': 'not_computed'}), 202


@app.route('/api/report/<name>/surface/compute', methods=['POST'])
def start_surface_compute(name: str):
    """Start background computation of parameter surface.

    Accepts JSON body with keys: xkey, ykey, xvals (comma list), yvals (comma list), train_window
    Returns job id.
    """
    p = REPORT_ROOT / name
    if not p.exists():
        return jsonify({'error': 'not found'}), 404

    body = request.get_json() or {}
    xkey = body.get('xkey', 'lags')
    ykey = body.get('ykey', 'train')
    xvals = body.get('xvals', '1,2,3,4,5')
    yvals = body.get('yvals', '10,20,30')
    xs = [int(x) for x in str(xvals).split(',') if x]
    ys = [int(y) for y in str(yvals).split(',') if y]
    train_window = int(body.get('train_window', 30))

    records_path = Path(__file__).parent.parent / 'data' / name / 'records.json'

    from ingest_bot.jobs import submit_job

    def job_fn():
        # prefer raw records.json if available, otherwise attempt to use last_rows from saved report
        if records_path.exists():
            data = json.loads(records_path.read_text(encoding='utf-8'))
        else:
            report_file = p / 'report.json'
            if report_file.exists():
                r = json.loads(report_file.read_text(encoding='utf-8'))
                data = r.get('last_rows', [])
            else:
                raise RuntimeError('records not found')

        from ingest_bot.analysis import records_to_df
        df = records_to_df(data)
        series = df['close']
        from ingest_bot.backtest import parameter_surface

        def model_factory(params):
            # Lightweight linear predictor using numpy least-squares to avoid heavy deps in background job
            import numpy as _np
            def _model(train_series):
                arr = _np.array(train_series.values, dtype=float)
                lags = int(params.get('lags', 3))
                if len(arr) <= lags:
                    return float(arr[-1])
                X = []
                y = []
                for i in range(lags, len(arr)):
                    X.append(arr[i-lags:i])
                    y.append(arr[i])
                X = _np.asarray(X)
                y = _np.asarray(y)
                try:
                    coef, *_ = _np.linalg.lstsq(X, y, rcond=None)
                    last = arr[-lags:]
                    pred = float(_np.dot(last, coef))
                except Exception:
                    pred = float(arr[-1])
                return pred
            return _model

        grid = parameter_surface(series, model_factory, {xkey: xs, ykey: ys}, train_window=train_window)
        import numpy as _np
        grid_serializable = {'x': grid['x'], 'y': grid['y'], 'z': _np.nan_to_num(grid['z']).tolist()}
        (p / 'surface.json').write_text(json.dumps(grid_serializable), encoding='utf-8')
        return {'surface': grid_serializable}

    job_id = submit_job(job_fn, job_meta={'name': name})
    return jsonify({'job_id': job_id}), 202


@app.route('/api/report/<name>/surface/status/<job_id>')
def surface_status(name: str, job_id: str):
    from ingest_bot.jobs import get_job
    status = get_job(job_id)
    return jsonify(status)


@app.route('/reports/<name>/<filename>')
def serve_report_file(name: str, filename: str):
    p = REPORT_ROOT / name
    return send_from_directory(str(p), filename)


def main(argv: Optional[list] = None) -> None:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--port', type=int, default=8050)
    args = p.parse_args(argv)

    app.run(host=args.host, port=args.port, debug=False)


if __name__ == '__main__':
    main()
