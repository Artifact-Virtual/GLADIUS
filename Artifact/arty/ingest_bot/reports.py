from __future__ import annotations

import json
import csv
from pathlib import Path
from typing import Dict, Any


def save_report(report: Dict[str, Any], dest: Path) -> None:
    """Persist analysis report to a directory.

    Writes:
    - summary.json
    - predictions.json
    - evals.json
    - last_rows.csv
    - optionally copies 'plot' and other images if present in report
    """
    dest.mkdir(parents=True, exist_ok=True)

    (dest / "summary.json").write_text(json.dumps(report.get("summary", {}), indent=2), encoding="utf-8")
    (dest / "predictions.json").write_text(json.dumps(report.get("predictions", {}), indent=2), encoding="utf-8")
    (dest / "evals.json").write_text(json.dumps(report.get("evals", {}), indent=2), encoding="utf-8")

    # last_rows CSV
    last_rows = report.get("last_rows", [])
    if last_rows:
        keys = list(last_rows[0].keys())
        with (dest / "last_rows.csv").open("w", newline='', encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=keys)
            writer.writeheader()
            for r in last_rows:
                writer.writerow({k: r.get(k) for k in keys})

    # copy plot files if exist
    plot = report.get("plot")
    if plot:
        p = Path(plot)
        if p.exists():
            import shutil
            try:
                # avoid copying if it's the same file
                dst = dest / p.name
                if p.resolve() != dst.resolve():
                    shutil.copy2(p, dst)
            except Exception:
                # best-effort: don't fail the entire report save for file copy issues
                pass

    # save parameter surface if present
    if report.get('surface') is not None:
        (dest / 'surface.json').write_text(json.dumps(report['surface']), encoding='utf-8')

    # save entire report for convenience (make JSON-serializable)
    serializable = dict(report)
    if 'last_rows' in serializable:
        rows = []
        for r in serializable['last_rows']:
            rr = {}
            for k, v in r.items():
                try:
                    if hasattr(v, 'isoformat'):
                        rr[k] = v.isoformat()
                    else:
                        rr[k] = float(v) if isinstance(v, (int, float)) else v
                except Exception:
                    rr[k] = str(v)
            rows.append(rr)
        serializable['last_rows'] = rows

    with (dest / "report.json").open("w", encoding="utf-8") as fh:
        json.dump(serializable, fh, indent=2)
