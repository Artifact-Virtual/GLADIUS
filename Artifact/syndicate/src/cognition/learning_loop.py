"""
Cognition Learning Loop - Autonomous learning with prediction feedback.

Integrates:
- Training data generation from tool history
- Self-improvement engine for system upgrades
- Native tool calling for cognition-driven learning
- Prediction learning from market outcomes

This is the core learning loop that makes the system self-improving.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

from .memory_module import MemoryModule
from .syndicate_integration import SyndicateCognition
from .training_generator import TrainingDataGenerator, TrainingDataset, FineTuningPipeline
from .self_improvement import (
    SelfImprovementEngine,
    ImprovementProposal,
    ImprovementCategory,
    ProposalStatus
)
from .tool_calling import TOOL_REGISTRY


@dataclass
class LearningCycleResult:
    """Result of a learning cycle."""
    cycle_id: str
    timestamp: str
    
    # Data ingestion
    reports_ingested: int
    predictions_processed: int
    
    # Training data
    training_examples_generated: int
    training_data_path: Optional[str]
    
    # Improvement proposals
    proposals_created: int
    proposals_completed: int
    
    # Learning metrics
    pattern_success_rate: Optional[float]
    confidence_score: Optional[float]
    
    # Status
    success: bool
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cycle_id": self.cycle_id,
            "timestamp": self.timestamp,
            "reports_ingested": self.reports_ingested,
            "predictions_processed": self.predictions_processed,
            "training_examples_generated": self.training_examples_generated,
            "training_data_path": self.training_data_path,
            "proposals_created": self.proposals_created,
            "proposals_completed": self.proposals_completed,
            "pattern_success_rate": self.pattern_success_rate,
            "confidence_score": self.confidence_score,
            "success": self.success,
            "errors": self.errors
        }


class CognitionLearningLoop:
    """
    Autonomous learning loop for continuous improvement.
    
    Runs the following cycle:
    1. Ingest new reports and data into vector memory
    2. Process prediction outcomes for learning
    3. Generate training data from tool usage
    4. Analyze patterns and create improvement proposals
    5. Execute approved improvements
    6. Benchmark and create snapshots
    """
    
    def __init__(
        self,
        base_dir: str = ".",
        data_dir: str = "./data",
        output_dir: str = "./output",
        logger: Optional[logging.Logger] = None
    ):
        self.base_dir = Path(base_dir).resolve()
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize components
        self.cognition = SyndicateCognition(
            data_dir=str(self.data_dir),
            output_dir=str(self.output_dir),
            logger=self.logger
        )
        
        self.memory = MemoryModule(
            base_dir=str(self.base_dir),
            workspace_dir=str(self.output_dir),
            logger=self.logger,
            vector_store=self.cognition.store
        )
        
        self.training_gen = TrainingDataGenerator(
            output_dir=str(self.data_dir / "training"),
            logger=self.logger
        )
        
        self.improvement = SelfImprovementEngine(
            base_dir=str(self.base_dir),
            proposals_dir=str(self.data_dir / "improvements" / "proposals"),
            snapshots_dir=str(self.data_dir / "improvements" / "snapshots"),
            logger=self.logger
        )
        
        # Cycle tracking
        self.cycle_history: List[LearningCycleResult] = []
        self._load_cycle_history()
        
        self.logger.info("[LEARNING] Initialized cognition learning loop")
    
    def _load_cycle_history(self):
        """Load previous cycle history."""
        history_path = self.data_dir / "learning" / "cycle_history.json"
        if history_path.exists():
            try:
                with open(history_path, 'r') as f:
                    data = json.load(f)
                    # Just keep the dicts, don't recreate dataclass objects
                    self.cycle_history = data.get("cycles", [])
            except Exception as e:
                self.logger.warning(f"[LEARNING] Failed to load history: {e}")
    
    def _save_cycle_history(self):
        """Save cycle history."""
        history_dir = self.data_dir / "learning"
        history_dir.mkdir(parents=True, exist_ok=True)
        history_path = history_dir / "cycle_history.json"
        
        with open(history_path, 'w') as f:
            json.dump({"cycles": [c if isinstance(c, dict) else c.to_dict() for c in self.cycle_history]}, f, indent=2)
    
    def run_cycle(self, current_gold_price: Optional[float] = None) -> LearningCycleResult:
        """
        Run a single learning cycle.
        
        Args:
            current_gold_price: Current gold price for evaluating predictions
        
        Returns:
            LearningCycleResult with cycle metrics
        """
        cycle_id = f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logger.info(f"[LEARNING] Starting cycle: {cycle_id}")
        
        result = LearningCycleResult(
            cycle_id=cycle_id,
            timestamp=datetime.now().isoformat(),
            reports_ingested=0,
            predictions_processed=0,
            training_examples_generated=0,
            training_data_path=None,
            proposals_created=0,
            proposals_completed=0,
            pattern_success_rate=None,
            confidence_score=None,
            success=True
        )
        
        try:
            # Step 1: Ingest new reports
            result.reports_ingested = self._ingest_reports()
            
            # Step 2: Process prediction outcomes
            if current_gold_price:
                result.predictions_processed = self._process_predictions(current_gold_price)
            
            # Step 3: Generate training data
            result.training_examples_generated, result.training_data_path = self._generate_training_data()
            
            # Step 4: Analyze and create improvement proposals
            result.proposals_created = self._analyze_and_propose()
            
            # Step 5: Execute approved improvements
            result.proposals_completed = self._execute_improvements()
            
            # Step 6: Get learning metrics
            accuracy = self.cognition.get_prediction_accuracy()
            result.pattern_success_rate = accuracy.get("win_rate")
            result.confidence_score = accuracy.get("confidence_score")
            
        except Exception as e:
            self.logger.error(f"[LEARNING] Cycle error: {e}")
            result.success = False
            result.errors.append(str(e))
        
        # Save result
        self.cycle_history.append(result.to_dict())
        self._save_cycle_history()
        
        self.logger.info(f"[LEARNING] Cycle complete: {cycle_id}")
        self.logger.info(f"  Reports: {result.reports_ingested}, Training: {result.training_examples_generated}")
        self.logger.info(f"  Success Rate: {result.pattern_success_rate}%, Confidence: {result.confidence_score}")
        
        return result
    
    def _ingest_reports(self) -> int:
        """Ingest new reports into vector memory."""
        counts = self.cognition.ingest_all_reports()
        return sum(counts.values())
    
    def _process_predictions(self, current_gold_price: float) -> int:
        """Process and evaluate pending predictions."""
        updates = self.cognition.update_pending_predictions(current_gold_price)
        return len(updates)
    
    def _generate_training_data(self) -> Tuple[int, Optional[str]]:
        """Generate training data from tool usage history."""
        # Get history from memory module
        history_result = self.memory.get_history(last_n=100)
        history = history_result.data if history_result.success else []
        
        # Generate datasets
        datasets = []
        
        if history:
            datasets.append(self.training_gen.generate_from_history(history, "history"))
        
        datasets.append(self.training_gen.generate_synthetic(n_per_category=5, dataset_name="synthetic"))
        datasets.append(self.training_gen.generate_from_tool_schemas("schemas"))
        
        if not datasets:
            return 0, None
        
        # Combine and export
        combined = self.training_gen.combine_datasets(datasets, "combined_training")
        paths = self.training_gen.export_all([combined], formats=["llama"])
        
        total_examples = len(combined.examples)
        output_path = paths.get("combined_training_llama")
        
        return total_examples, output_path
    
    def _analyze_and_propose(self) -> int:
        """Analyze patterns and create improvement proposals."""
        proposals_created = 0
        
        # Analyze prediction accuracy
        accuracy = self.cognition.get_prediction_accuracy()
        
        # If accuracy is low, propose cognition improvements
        if accuracy.get("win_rate", 0) < 50 and accuracy.get("total", 0) >= 5:
            proposal = self.improvement.create_proposal(
                title="Improve prediction accuracy",
                category=ImprovementCategory.ACCURACY,
                summary=f"Win rate is {accuracy['win_rate']}%. Need to improve pattern recognition.",
                items=[
                    {
                        "description": "Analyze losing predictions for common patterns",
                        "rationale": "Understanding failures helps improve",
                        "impact": "high",
                        "risk": "low",
                        "effort": "2 hours"
                    },
                    {
                        "description": "Add more historical context to predictions",
                        "rationale": "Similar situations provide guidance",
                        "impact": "medium",
                        "risk": "low",
                        "effort": "1 hour"
                    }
                ]
            )
            self.improvement.submit_for_review(proposal.id)
            proposals_created += 1
        
        # Check if memory is being used effectively
        memory_stats = self.memory.list_databases()
        if memory_stats.success and len(memory_stats.data) < 2:
            proposal = self.improvement.create_proposal(
                title="Expand memory access",
                category=ImprovementCategory.MEMORY,
                summary="Limited databases connected. Should add more data sources.",
                items=[
                    {
                        "description": "Connect additional SQLite databases",
                        "rationale": "More data = better context",
                        "impact": "medium",
                        "risk": "low",
                        "effort": "30 minutes"
                    }
                ]
            )
            proposals_created += 1
        
        return proposals_created
    
    def _execute_improvements(self) -> int:
        """Execute approved improvements."""
        completed = 0
        
        # Find approved proposals without implementation plans
        approved = self.improvement.list_proposals(status=ProposalStatus.APPROVED)
        
        for proposal in approved:
            if not proposal.implementation_plan:
                # Auto-generate implementation plan
                tasks = [f"Execute: {item.description}" for item in proposal.items]
                tasks.append("Verify changes")
                tasks.append("Update documentation if needed")
                
                self.improvement.create_implementation_plan(
                    proposal.id,
                    plan=f"Implementation plan for {proposal.title}",
                    checklist_items=tasks
                )
        
        # Find implementing proposals and check progress
        implementing = self.improvement.list_proposals(status=ProposalStatus.IMPLEMENTING)
        
        for proposal in implementing:
            if proposal.progress() >= 100:
                self.improvement.complete_implementation(proposal.id)
                completed += 1
        
        return completed
    
    def run_benchmark(self, n_cycles: int = 10) -> Dict[str, Any]:
        """
        Run multiple cycles and benchmark improvements.
        
        Args:
            n_cycles: Number of cycles to run
        
        Returns:
            Benchmark results comparing start to end
        """
        self.logger.info(f"[LEARNING] Starting benchmark: {n_cycles} cycles")
        
        # Create initial snapshot
        initial_snapshot = self.improvement.create_snapshot(
            name="benchmark_start",
            description=f"Benchmark start with {n_cycles} cycles planned",
            files_to_backup=[
                str(self.data_dir / "training"),
                str(self.data_dir / "vectors")
            ]
        )
        
        # Get initial metrics
        initial_accuracy = self.cognition.get_prediction_accuracy()
        initial_stats = self.cognition.stats()
        
        results = []
        for i in range(n_cycles):
            self.logger.info(f"[BENCHMARK] Cycle {i+1}/{n_cycles}")
            result = self.run_cycle()
            results.append(result.to_dict())
        
        # Get final metrics
        final_accuracy = self.cognition.get_prediction_accuracy()
        final_stats = self.cognition.stats()
        
        # Create final snapshot
        final_snapshot = self.improvement.create_snapshot(
            name="benchmark_end",
            description=f"Benchmark complete after {n_cycles} cycles",
            files_to_backup=[
                str(self.data_dir / "training"),
                str(self.data_dir / "vectors")
            ]
        )
        
        # Calculate improvements
        benchmark = {
            "n_cycles": n_cycles,
            "initial_snapshot": initial_snapshot.id,
            "final_snapshot": final_snapshot.id,
            "initial_metrics": {
                "win_rate": initial_accuracy.get("win_rate", 0),
                "confidence": initial_accuracy.get("confidence_score", 0),
                "total_predictions": initial_accuracy.get("total", 0),
                "document_count": initial_stats.get("document_count", 0)
            },
            "final_metrics": {
                "win_rate": final_accuracy.get("win_rate", 0),
                "confidence": final_accuracy.get("confidence_score", 0),
                "total_predictions": final_accuracy.get("total", 0),
                "document_count": final_stats.get("document_count", 0)
            },
            "improvements": {
                "win_rate_delta": final_accuracy.get("win_rate", 0) - initial_accuracy.get("win_rate", 0),
                "confidence_delta": final_accuracy.get("confidence_score", 0) - initial_accuracy.get("confidence_score", 0),
                "documents_added": final_stats.get("document_count", 0) - initial_stats.get("document_count", 0)
            },
            "totals": {
                "reports_ingested": sum(r.get("reports_ingested", 0) for r in results),
                "training_examples": sum(r.get("training_examples_generated", 0) for r in results),
                "proposals_created": sum(r.get("proposals_created", 0) for r in results),
                "proposals_completed": sum(r.get("proposals_completed", 0) for r in results),
                "errors": sum(len(r.get("errors", [])) for r in results)
            },
            "cycle_results": results
        }
        
        # Save benchmark
        benchmark_path = self.data_dir / "learning" / f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        benchmark_path.parent.mkdir(parents=True, exist_ok=True)
        with open(benchmark_path, 'w') as f:
            json.dump(benchmark, f, indent=2)
        
        self.logger.info(f"[BENCHMARK] Complete. Win rate: {initial_accuracy.get('win_rate', 0)} -> {final_accuracy.get('win_rate', 0)}")
        
        return benchmark
    
    def get_learning_feedback(self) -> str:
        """Get comprehensive learning feedback for AI context."""
        parts = ["# Cognition Learning Feedback\n"]
        
        # Prediction accuracy
        parts.append(self.cognition.generate_learning_feedback())
        parts.append("")
        
        # Recent cycles
        if self.cycle_history:
            parts.append("## Recent Learning Cycles\n")
            for cycle in self.cycle_history[-5:]:
                if isinstance(cycle, dict):
                    parts.append(f"- **{cycle.get('cycle_id', 'unknown')}**: {cycle.get('reports_ingested', 0)} reports, {cycle.get('training_examples_generated', 0)} examples")
                else:
                    parts.append(f"- **{cycle.cycle_id}**: {cycle.reports_ingested} reports, {cycle.training_examples_generated} examples")
            parts.append("")
        
        # Improvement status
        parts.append("## Improvement Status\n")
        improvement_stats = self.improvement.stats()
        for status, count in improvement_stats.get("by_status", {}).items():
            if count > 0:
                parts.append(f"- {status}: {count}")
        parts.append("")
        
        # Memory status
        parts.append("## Memory Status\n")
        db_result = self.memory.list_databases()
        if db_result.success:
            for db in db_result.data:
                parts.append(f"- {db['name']} ({db['type']})")
        parts.append("")
        
        return "\n".join(parts)
    
    def stats(self) -> Dict[str, Any]:
        """Get comprehensive learning loop statistics."""
        return {
            "cycles_run": len(self.cycle_history),
            "cognition": self.cognition.stats(),
            "memory": {
                "databases": len(self.memory.databases),
                "tools": len(self.memory.tools),
                "history_size": len(self.memory.history)
            },
            "improvements": self.improvement.stats(),
            "training": {
                "output_dir": str(self.training_gen.output_dir)
            }
        }
    
    def close(self):
        """Clean up resources."""
        self.cognition.close()
        self.memory.close()
        self._save_cycle_history()
        self.logger.info("[LEARNING] Closed learning loop")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Convenience function for running a quick learning cycle
def run_learning_cycle(
    base_dir: str = ".",
    current_gold_price: Optional[float] = None
) -> LearningCycleResult:
    """Run a single learning cycle."""
    with CognitionLearningLoop(base_dir=base_dir) as loop:
        return loop.run_cycle(current_gold_price=current_gold_price)


# Convenience function for running a benchmark
def run_benchmark(
    base_dir: str = ".",
    n_cycles: int = 10
) -> Dict[str, Any]:
    """Run a benchmark of multiple cycles."""
    with CognitionLearningLoop(base_dir=base_dir) as loop:
        return loop.run_benchmark(n_cycles=n_cycles)
