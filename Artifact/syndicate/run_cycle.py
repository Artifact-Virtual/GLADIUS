#!/usr/bin/env python3
"""
Run a single Syndicate cycle and capture metrics.
"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def count_files(path, pattern):
    """Count files matching pattern in path."""
    p = Path(path)
    return len(list(p.glob(pattern))) if p.exists() else 0

def get_cortex_stats():
    """Get current cortex memory stats."""
    cortex_path = Path('data/cortex_memory.json')
    if cortex_path.exists():
        with open(cortex_path) as f:
            cortex = json.load(f)
        return {
            'total_wins': cortex.get('total_wins', 0),
            'total_losses': cortex.get('total_losses', 0),
            'win_streak': cortex.get('win_streak', 0),
            'loss_streak': cortex.get('loss_streak', 0),
            'last_bias': cortex.get('last_bias', 'UNKNOWN'),
            'last_price_gold': cortex.get('last_price_gold', 0),
            'history_count': len(cortex.get('history', [])),
        }
    return {}

def create_snapshot(cycle_num):
    """Create a benchmark snapshot."""
    db_path = Path('data/syndicate.db')
    
    snapshot = {
        'timestamp': datetime.now().isoformat(),
        'cycle': cycle_num,
        'cortex': get_cortex_stats(),
        'outputs': {
            'journals': count_files('output/reports/journals', '*.md'),
            'charts': count_files('output/charts', '*.png'),
            'catalysts': count_files('output/reports/catalysts', '*.md'),
            'analysis': count_files('output/reports/analysis', '*.md'),
            'economic': count_files('output/reports/economic', '*.md'),
            'institutional': count_files('output/reports/institutional', '*.md'),
        },
        'db_size_kb': db_path.stat().st_size // 1024 if db_path.exists() else 0
    }
    
    Path('benchmarks').mkdir(exist_ok=True)
    snapshot_file = f'benchmarks/snapshot_cycle_{cycle_num}.json'
    with open(snapshot_file, 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    return snapshot

def run_cycle():
    """Run a single analysis cycle."""
    result = subprocess.run(
        [sys.executable, 'main.py', '--once'],
        capture_output=True,
        text=True,
        timeout=600
    )
    return result.returncode == 0

if __name__ == '__main__':
    cycle_num = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    
    print(f"\n{'='*60}")
    print(f"CYCLE {cycle_num}")
    print(f"{'='*60}")
    
    # Run the cycle
    print("Running analysis cycle...")
    success = run_cycle()
    
    # Create snapshot
    snapshot = create_snapshot(cycle_num)
    
    print(f"\nCycle {cycle_num} {'completed' if success else 'FAILED'}")
    print(f"  Wins: {snapshot['cortex'].get('total_wins', 0)}")
    print(f"  Losses: {snapshot['cortex'].get('total_losses', 0)}")
    print(f"  Last Bias: {snapshot['cortex'].get('last_bias', 'UNKNOWN')}")
    print(f"  Gold Price: ${snapshot['cortex'].get('last_price_gold', 0):.2f}")
    print(f"  Journals: {snapshot['outputs']['journals']}")
    print(f"  Charts: {snapshot['outputs']['charts']}")
    print(f"  DB Size: {snapshot['db_size_kb']} KB")
