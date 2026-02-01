#!/usr/bin/env python3
"""
Auto-Study Analyst Team

Processes observer data, identifies patterns, performs statistical analysis.
"""

import os
import sys
import json
import math
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import Counter, defaultdict
import statistics

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | ANALYST | %(message)s'
)
logger = logging.getLogger(__name__)


class PatternDetector:
    """Detects patterns in experiment data."""
    
    def __init__(self):
        self.patterns = []
    
    def analyze_decisions(self, decisions: List[Dict]) -> Dict[str, Any]:
        """Analyze decision patterns."""
        if not decisions:
            return {'error': 'No decisions to analyze'}
        
        # Decision distribution
        decision_counts = Counter(d.get('decision', 'unknown') for d in decisions)
        total = sum(decision_counts.values())
        
        distribution = {k: v / total for k, v in decision_counts.items()}
        
        # Sequence analysis
        sequences = self._find_sequences(decisions)
        
        # Confidence stats
        confidences = [d.get('confidence', 0) for d in decisions if 'confidence' in d]
        confidence_stats = {
            'mean': statistics.mean(confidences) if confidences else 0,
            'std': statistics.stdev(confidences) if len(confidences) > 1 else 0,
            'min': min(confidences) if confidences else 0,
            'max': max(confidences) if confidences else 0
        }
        
        # Latency stats
        latencies = [d.get('latency_ms', 0) for d in decisions if 'latency_ms' in d]
        latency_stats = {
            'mean': statistics.mean(latencies) if latencies else 0,
            'std': statistics.stdev(latencies) if len(latencies) > 1 else 0,
            'p95': sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0
        }
        
        return {
            'total_decisions': len(decisions),
            'distribution': distribution,
            'entropy': self._entropy(distribution),
            'sequences': sequences,
            'confidence_stats': confidence_stats,
            'latency_stats': latency_stats
        }
    
    def _find_sequences(self, decisions: List[Dict], min_length: int = 3) -> List[Dict]:
        """Find repeating decision sequences."""
        if len(decisions) < min_length:
            return []
        
        decision_str = ''.join(d.get('decision', 'x')[0] for d in decisions)
        
        sequences = []
        for length in range(min_length, min(10, len(decisions) // 2)):
            counts = Counter()
            for i in range(len(decision_str) - length + 1):
                seq = decision_str[i:i+length]
                counts[seq] += 1
            
            # Find repeated sequences
            for seq, count in counts.most_common(5):
                if count > 2:
                    sequences.append({
                        'sequence': seq,
                        'length': length,
                        'occurrences': count
                    })
        
        return sequences[:10]  # Top 10
    
    def _entropy(self, distribution: Dict[str, float]) -> float:
        """Calculate Shannon entropy."""
        entropy = 0
        for p in distribution.values():
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy
    
    def detect_anomalies(self, metrics: List[Dict]) -> List[Dict]:
        """Detect anomalies in metrics."""
        anomalies = []
        
        if len(metrics) < 10:
            return anomalies
        
        # Extract numeric values for analysis
        for key in ['black_ratio', 'visited_cells', 'latency_ms']:
            values = []
            for m in metrics:
                data = m.get('data', {})
                if isinstance(data, dict):
                    grid_stats = data.get('grid_stats', {})
                    value = grid_stats.get(key) or data.get(key)
                    if value is not None:
                        values.append(float(value))
            
            if len(values) > 5:
                mean = statistics.mean(values)
                std = statistics.stdev(values)
                
                # Find outliers (> 3 std from mean)
                for i, v in enumerate(values):
                    if abs(v - mean) > 3 * std:
                        anomalies.append({
                            'metric': key,
                            'index': i,
                            'value': v,
                            'mean': mean,
                            'std': std,
                            'deviation': (v - mean) / std if std > 0 else 0
                        })
        
        return anomalies


class Analyst:
    """Main analyst class."""
    
    def __init__(self, experiments_dir: str = None):
        self.experiments_dir = Path(experiments_dir or '/home/adam/worxpace/gladius/experiments')
        self.output_dir = self.experiments_dir / 'auto_study' / 'analyst' / 'analysis'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.detector = PatternDetector()
    
    def analyze_experiment(self, experiment_name: str) -> Dict[str, Any]:
        """Analyze a single experiment."""
        experiment_dir = self.experiments_dir / experiment_name
        results_dir = experiment_dir / 'results'
        
        analysis = {
            'experiment': experiment_name,
            'timestamp': datetime.now().isoformat(),
            'status': 'analyzing'
        }
        
        # Find decision logs
        decisions = []
        for log_file in results_dir.rglob('*decisions*.json'):
            try:
                with open(log_file) as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        decisions.extend(data)
            except Exception as e:
                logger.warning(f"Failed to read {log_file}: {e}")
        
        # Find metrics
        metrics = []
        for stats_file in results_dir.rglob('stats.json'):
            try:
                with open(stats_file) as f:
                    metrics.append({
                        'source': str(stats_file),
                        'data': json.load(f)
                    })
            except Exception as e:
                logger.warning(f"Failed to read {stats_file}: {e}")
        
        # Run analysis
        if decisions:
            analysis['decision_analysis'] = self.detector.analyze_decisions(decisions)
        
        if metrics:
            analysis['anomalies'] = self.detector.detect_anomalies(metrics)
            analysis['metrics_count'] = len(metrics)
        
        # Progress estimation
        if metrics:
            latest = metrics[-1].get('data', {})
            step = latest.get('step', 0)
            max_steps = 1000000  # Default
            analysis['progress'] = {
                'current_step': step,
                'estimated_progress': step / max_steps * 100
            }
        
        analysis['status'] = 'complete'
        
        # Save analysis
        output_file = self.output_dir / f"{experiment_name}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        logger.info(f"Analysis saved: {output_file}")
        
        return analysis
    
    def analyze_all(self) -> List[Dict[str, Any]]:
        """Analyze all experiments."""
        results = []
        
        for item in self.experiments_dir.iterdir():
            if item.is_dir() and item.name not in ['auto_study', 'templates', '__pycache__']:
                try:
                    analysis = self.analyze_experiment(item.name)
                    results.append(analysis)
                except Exception as e:
                    logger.error(f"Failed to analyze {item.name}: {e}")
        
        return results


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-Study Analyst Team')
    parser.add_argument('--experiment', type=str, help='Specific experiment to analyze')
    parser.add_argument('--all', action='store_true', help='Analyze all experiments')
    
    args = parser.parse_args()
    
    analyst = Analyst()
    
    if args.experiment:
        result = analyst.analyze_experiment(args.experiment)
        print(json.dumps(result, indent=2))
    else:
        results = analyst.analyze_all()
        print(f"Analyzed {len(results)} experiments")


if __name__ == '__main__':
    main()
