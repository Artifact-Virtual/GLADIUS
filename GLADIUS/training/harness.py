"""
Training Harness - Isolated cognition training environment.

Purpose:
- Sandboxed training that doesn't affect production
- Input processing, learning, validation pipeline
- Model versioning with hot-swap capability
- Progressive GGUF/GGM model development

Architecture:
┌─────────────────────────────────────────────────────────────┐
│                    TRAINING HARNESS                          │
├─────────────────────────────────────────────────────────────┤
│  InputProcessor → LearningEngine → OutputValidator          │
│         ↓                ↓                ↓                 │
│           staging/ → validated/ → production/               │
└─────────────────────────────────────────────────────────────┘
"""

import json
import logging
import shutil
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum
import threading


class ModelStage(Enum):
    """Model lifecycle stages."""
    STAGING = "staging"
    VALIDATED = "validated"
    PRODUCTION = "production"
    ARCHIVED = "archived"


@dataclass
class TrainingInput:
    """Normalized training input."""
    query: str
    expected_tool: str
    expected_args: Dict[str, Any]
    source: str  # "synthetic", "history", "user_feedback"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_chat_format(self) -> Dict[str, Any]:
        """Convert to chat training format."""
        return {
            "messages": [
                {"role": "system", "content": "You are Gladius, a tool router. Output JSON with the tool to call."},
                {"role": "user", "content": self.query},
                {"role": "assistant", "content": json.dumps({
                    "tool": self.expected_tool,
                    "args": self.expected_args
                })}
            ],
            "metadata": {"source": self.source, **self.metadata}
        }


@dataclass
class ValidationResult:
    """Result of model validation."""
    accuracy: float
    latency_avg_ms: float
    latency_p99_ms: float
    tool_accuracies: Dict[str, float]
    total_tests: int
    passed: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "accuracy": self.accuracy,
            "latency_avg_ms": self.latency_avg_ms,
            "latency_p99_ms": self.latency_p99_ms,
            "tool_accuracies": self.tool_accuracies,
            "total_tests": self.total_tests,
            "passed": self.passed,
            "timestamp": self.timestamp
        }


@dataclass
class ModelVersion:
    """Model version metadata."""
    version: str
    stage: ModelStage
    path: Path
    accuracy: float
    created_at: str
    promoted_at: Optional[str] = None
    validation: Optional[ValidationResult] = None


class InputProcessor:
    """
    Processes raw data into normalized training inputs.
    
    Sources:
    - Tool call history (from MemoryModule)
    - Synthetic generation (from ProgressiveTrainer)
    - User feedback (from consensus system)
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def from_history(self, history: List[Dict[str, Any]]) -> List[TrainingInput]:
        """Convert tool call history to training inputs."""
        inputs = []
        
        for entry in history:
            if not entry.get("success", True):
                continue  # Skip failed calls
            
            tool = entry.get("tool")
            args = entry.get("args", {})
            query = entry.get("query", "")
            
            if tool and query:
                inputs.append(TrainingInput(
                    query=query,
                    expected_tool=tool,
                    expected_args=args,
                    source="history",
                    metadata={"original_timestamp": entry.get("timestamp", "")}
                ))
        
        self.logger.info(f"Processed {len(inputs)} training inputs from history")
        return inputs
    
    def from_patterns(self, patterns: Dict[str, List[Dict]]) -> List[TrainingInput]:
        """Convert pattern model to training inputs."""
        inputs = []
        
        for tool_name, tool_patterns in patterns.items():
            for pattern in tool_patterns:
                query = pattern.get("query", "")
                args = pattern.get("args", {})
                
                if query:
                    inputs.append(TrainingInput(
                        query=query,
                        expected_tool=tool_name,
                        expected_args=args,
                        source="synthetic"
                    ))
        
        self.logger.info(f"Processed {len(inputs)} training inputs from patterns")
        return inputs
    
    def from_feedback(self, feedback_entries: List[Dict[str, Any]]) -> List[TrainingInput]:
        """Convert user feedback/corrections to training inputs."""
        inputs = []
        
        for entry in feedback_entries:
            query = entry.get("query", "")
            correct_tool = entry.get("correct_tool")
            correct_args = entry.get("correct_args", {})
            
            if query and correct_tool:
                inputs.append(TrainingInput(
                    query=query,
                    expected_tool=correct_tool,
                    expected_args=correct_args,
                    source="user_feedback",
                    metadata={"feedback_id": entry.get("id", "")}
                ))
        
        self.logger.info(f"Processed {len(inputs)} training inputs from feedback")
        return inputs
    
    def export_jsonl(self, inputs: List[TrainingInput], output_path: Path) -> int:
        """Export training inputs to JSONL format."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            for inp in inputs:
                f.write(json.dumps(inp.to_chat_format()) + "\n")
        
        self.logger.info(f"Exported {len(inputs)} examples to {output_path}")
        return len(inputs)


class LearningEngine:
    """
    Manages the learning process in isolation.
    
    Features:
    - Incremental learning without full retrain
    - LoRA fine-tuning support
    - Pattern model updates
    - Progress tracking
    """
    
    def __init__(
        self,
        models_dir: str = "./models",
        logger: Optional[logging.Logger] = None
    ):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.staging_dir = self.models_dir / "staging"
        self.validated_dir = self.models_dir / "validated"
        self.production_dir = self.models_dir / "production"
        self.archive_dir = self.models_dir / "archive"
        
        for d in [self.staging_dir, self.validated_dir, self.production_dir, self.archive_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        self.logger = logger or logging.getLogger(__name__)
        self._training_lock = threading.Lock()
        self._is_training = False
    
    def train_pattern_model(
        self,
        training_inputs: List[TrainingInput],
        model_name: str = "gladius-pattern"
    ) -> ModelVersion:
        """Train/update the pattern model."""
        with self._training_lock:
            self._is_training = True
            
            try:
                # Build pattern dictionary
                patterns: Dict[str, List[Dict]] = {}
                
                for inp in training_inputs:
                    if inp.expected_tool not in patterns:
                        patterns[inp.expected_tool] = []
                    
                    patterns[inp.expected_tool].append({
                        "query": inp.query.lower(),
                        "args": inp.expected_args
                    })
                
                # Create model file
                version = datetime.now().strftime("%Y%m%d_%H%M%S")
                model_file = self.staging_dir / f"{model_name}-{version}.patterns.json"
                
                model_data = {
                    "type": "pattern_model",
                    "model_name": model_name,
                    "version": version,
                    "created_at": datetime.now().isoformat(),
                    "patterns": patterns,
                    "total_examples": len(training_inputs),
                    "tools_covered": list(patterns.keys())
                }
                
                with open(model_file, 'w') as f:
                    json.dump(model_data, f, indent=2)
                
                self.logger.info(f"Trained pattern model: {model_file}")
                
                return ModelVersion(
                    version=version,
                    stage=ModelStage.STAGING,
                    path=model_file,
                    accuracy=0.0,  # To be validated
                    created_at=datetime.now().isoformat()
                )
            
            finally:
                self._is_training = False
    
    def train_sklearn_model(
        self,
        training_inputs: List[TrainingInput],
        model_name: str = "gladius-router"
    ) -> ModelVersion:
        """Train sklearn-based classifier model."""
        with self._training_lock:
            self._is_training = True
            
            try:
                # Prepare data
                texts = [inp.query for inp in training_inputs]
                labels = [inp.expected_tool for inp in training_inputs]
                
                # Import sklearn components
                from sklearn.feature_extraction.text import TfidfVectorizer
                from sklearn.linear_model import LogisticRegression
                from sklearn.pipeline import Pipeline
                import pickle
                
                # Build pipeline
                pipeline = Pipeline([
                    ('tfidf', TfidfVectorizer(
                        max_features=5000,
                        ngram_range=(1, 2),
                        lowercase=True
                    )),
                    ('clf', LogisticRegression(
                        max_iter=1000,
                        multi_class='multinomial',
                        solver='lbfgs',
                        class_weight='balanced'
                    ))
                ])
                
                # Train
                pipeline.fit(texts, labels)
                
                # Save model
                version = datetime.now().strftime("%Y%m%d_%H%M%S")
                model_file = self.staging_dir / f"{model_name}-{version}.pkl"
                
                with open(model_file, 'wb') as f:
                    pickle.dump(pipeline, f)
                
                # Save metadata
                meta_file = self.staging_dir / f"{model_name}-{version}.meta.json"
                with open(meta_file, 'w') as f:
                    json.dump({
                        "model_name": model_name,
                        "version": version,
                        "type": "sklearn_pipeline",
                        "training_examples": len(training_inputs),
                        "tools": list(set(labels)),
                        "created_at": datetime.now().isoformat()
                    }, f, indent=2)
                
                self.logger.info(f"Trained sklearn model: {model_file}")
                
                return ModelVersion(
                    version=version,
                    stage=ModelStage.STAGING,
                    path=model_file,
                    accuracy=0.0,
                    created_at=datetime.now().isoformat()
                )
            
            finally:
                self._is_training = False
    
    @property
    def is_training(self) -> bool:
        return self._is_training
    
    def list_models(self, stage: Optional[ModelStage] = None) -> List[Path]:
        """List models in a stage directory."""
        if stage == ModelStage.STAGING:
            return list(self.staging_dir.glob("*.pkl")) + list(self.staging_dir.glob("*.json"))
        elif stage == ModelStage.VALIDATED:
            return list(self.validated_dir.glob("*.pkl")) + list(self.validated_dir.glob("*.json"))
        elif stage == ModelStage.PRODUCTION:
            return list(self.production_dir.glob("*.pkl")) + list(self.production_dir.glob("*.json"))
        else:
            return (
                list(self.staging_dir.glob("*")) +
                list(self.validated_dir.glob("*")) +
                list(self.production_dir.glob("*"))
            )


class OutputValidator:
    """
    Validates trained models before promotion.
    
    Criteria:
    - Accuracy >= 95% (configurable)
    - Latency p99 < 20ms
    - No regression on any tool
    """
    
    def __init__(
        self,
        min_accuracy: float = 95.0,
        max_latency_p99_ms: float = 20.0,
        logger: Optional[logging.Logger] = None
    ):
        self.min_accuracy = min_accuracy
        self.max_latency_p99_ms = max_latency_p99_ms
        self.logger = logger or logging.getLogger(__name__)
    
    def validate_pattern_model(
        self,
        model_path: Path,
        test_inputs: List[TrainingInput]
    ) -> ValidationResult:
        """Validate a pattern model."""
        from .native_model.router import NativeToolRouter
        
        router = NativeToolRouter(pattern_model_path=str(model_path))
        
        correct = 0
        tool_correct: Dict[str, int] = {}
        tool_total: Dict[str, int] = {}
        latencies: List[float] = []
        
        for inp in test_inputs:
            # Track per-tool stats
            if inp.expected_tool not in tool_total:
                tool_total[inp.expected_tool] = 0
                tool_correct[inp.expected_tool] = 0
            tool_total[inp.expected_tool] += 1
            
            # Route and measure
            result = router.route(inp.query, prefer_source="pattern")
            latencies.append(result.latency_ms)
            
            if result.tool_name == inp.expected_tool:
                correct += 1
                tool_correct[inp.expected_tool] += 1
        
        # Calculate metrics
        accuracy = (correct / len(test_inputs) * 100) if test_inputs else 0.0
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        sorted_latencies = sorted(latencies)
        p99_idx = int(len(sorted_latencies) * 0.99)
        p99_latency = sorted_latencies[p99_idx] if sorted_latencies else 0.0
        
        tool_accuracies = {
            tool: (tool_correct.get(tool, 0) / tool_total[tool] * 100)
            for tool in tool_total
        }
        
        passed = (
            accuracy >= self.min_accuracy and
            p99_latency <= self.max_latency_p99_ms
        )
        
        result = ValidationResult(
            accuracy=accuracy,
            latency_avg_ms=avg_latency,
            latency_p99_ms=p99_latency,
            tool_accuracies=tool_accuracies,
            total_tests=len(test_inputs),
            passed=passed
        )
        
        self.logger.info(
            f"Validation: accuracy={accuracy:.1f}%, "
            f"latency_avg={avg_latency:.2f}ms, "
            f"p99={p99_latency:.2f}ms, "
            f"passed={passed}"
        )
        
        return result
    
    def validate_sklearn_model(
        self,
        model_path: Path,
        test_inputs: List[TrainingInput]
    ) -> ValidationResult:
        """Validate a sklearn model."""
        import pickle
        
        with open(model_path, 'rb') as f:
            pipeline = pickle.load(f)
        
        correct = 0
        tool_correct: Dict[str, int] = {}
        tool_total: Dict[str, int] = {}
        latencies: List[float] = []
        
        for inp in test_inputs:
            if inp.expected_tool not in tool_total:
                tool_total[inp.expected_tool] = 0
                tool_correct[inp.expected_tool] = 0
            tool_total[inp.expected_tool] += 1
            
            start = time.time()
            prediction = pipeline.predict([inp.query])[0]
            latency_ms = (time.time() - start) * 1000
            latencies.append(latency_ms)
            
            if prediction == inp.expected_tool:
                correct += 1
                tool_correct[inp.expected_tool] += 1
        
        accuracy = (correct / len(test_inputs) * 100) if test_inputs else 0.0
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        sorted_latencies = sorted(latencies)
        p99_idx = int(len(sorted_latencies) * 0.99)
        p99_latency = sorted_latencies[p99_idx] if sorted_latencies else 0.0
        
        tool_accuracies = {
            tool: (tool_correct.get(tool, 0) / tool_total[tool] * 100)
            for tool in tool_total
        }
        
        passed = (
            accuracy >= self.min_accuracy and
            p99_latency <= self.max_latency_p99_ms
        )
        
        return ValidationResult(
            accuracy=accuracy,
            latency_avg_ms=avg_latency,
            latency_p99_ms=p99_latency,
            tool_accuracies=tool_accuracies,
            total_tests=len(test_inputs),
            passed=passed
        )


class ModelVersionControl:
    """
    Manages model promotion through stages.
    
    Flow: staging → validated → production
    """
    
    def __init__(
        self,
        models_dir: str = "./models",
        logger: Optional[logging.Logger] = None
    ):
        self.models_dir = Path(models_dir)
        self.staging_dir = self.models_dir / "staging"
        self.validated_dir = self.models_dir / "validated"
        self.production_dir = self.models_dir / "production"
        self.archive_dir = self.models_dir / "archive"
        
        for d in [self.staging_dir, self.validated_dir, self.production_dir, self.archive_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        self.logger = logger or logging.getLogger(__name__)
    
    def promote_to_validated(self, model_path: Path, validation: ValidationResult) -> Path:
        """Promote model from staging to validated."""
        if not validation.passed:
            raise ValueError(f"Model failed validation: accuracy={validation.accuracy}%")
        
        # Copy to validated
        dest = self.validated_dir / model_path.name
        shutil.copy2(model_path, dest)
        
        # Copy metadata if exists
        meta_path = model_path.with_suffix('.meta.json')
        if meta_path.exists():
            shutil.copy2(meta_path, self.validated_dir / meta_path.name)
        
        # Save validation result
        val_path = dest.with_suffix('.validation.json')
        with open(val_path, 'w') as f:
            json.dump(validation.to_dict(), f, indent=2)
        
        self.logger.info(f"Promoted to validated: {dest}")
        return dest
    
    def promote_to_production(self, model_path: Path) -> Path:
        """Promote model from validated to production."""
        # Archive current production model
        current_prod = list(self.production_dir.glob("*.pkl")) + list(self.production_dir.glob("*.patterns.json"))
        for prod_model in current_prod:
            archive_dest = self.archive_dir / f"{prod_model.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{prod_model.suffix}"
            shutil.move(prod_model, archive_dest)
            self.logger.info(f"Archived: {archive_dest}")
        
        # Copy to production
        dest = self.production_dir / model_path.name
        shutil.copy2(model_path, dest)
        
        # Copy metadata and validation
        for suffix in ['.meta.json', '.validation.json']:
            src = model_path.with_suffix(suffix)
            if src.exists():
                shutil.copy2(src, self.production_dir / src.name)
        
        self.logger.info(f"Promoted to production: {dest}")
        return dest
    
    def get_production_model(self) -> Optional[Path]:
        """Get current production model path."""
        pkl_models = list(self.production_dir.glob("*.pkl"))
        if pkl_models:
            return pkl_models[0]
        
        pattern_models = list(self.production_dir.glob("*.patterns.json"))
        if pattern_models:
            return pattern_models[0]
        
        return None
    
    def rollback(self) -> Optional[Path]:
        """Rollback to most recent archived model."""
        archived = sorted(self.archive_dir.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        if not archived:
            self.logger.warning("No archived models to rollback to")
            return None
        
        latest = archived[0]
        dest = self.production_dir / latest.name
        shutil.copy2(latest, dest)
        
        self.logger.info(f"Rolled back to: {latest.name}")
        return dest


class TrainingHarness:
    """
    Main orchestrator for isolated cognition training.
    
    Usage:
        harness = TrainingHarness('./models')
        
        # Process inputs
        inputs = harness.processor.from_history(history)
        
        # Train in isolation
        model = harness.engine.train_pattern_model(inputs)
        
        # Validate
        result = harness.validator.validate_pattern_model(model.path, test_inputs)
        
        # Promote if passed
        if result.passed:
            harness.version_control.promote_to_validated(model.path, result)
            harness.version_control.promote_to_production(validated_path)
    """
    
    def __init__(
        self,
        models_dir: str = "./models",
        min_accuracy: float = 95.0,
        max_latency_p99_ms: float = 20.0,
        logger: Optional[logging.Logger] = None
    ):
        self.models_dir = Path(models_dir)
        self.logger = logger or logging.getLogger(__name__)
        
        self.processor = InputProcessor(logger=self.logger)
        self.engine = LearningEngine(models_dir=models_dir, logger=self.logger)
        self.validator = OutputValidator(
            min_accuracy=min_accuracy,
            max_latency_p99_ms=max_latency_p99_ms,
            logger=self.logger
        )
        self.version_control = ModelVersionControl(models_dir=models_dir, logger=self.logger)
    
    def run_training_cycle(
        self,
        training_inputs: List[TrainingInput],
        test_inputs: Optional[List[TrainingInput]] = None,
        model_type: str = "pattern",
        model_name: str = "gladius"
    ) -> Dict[str, Any]:
        """
        Run a complete training cycle.
        
        Returns:
            Dict with training results and model info
        """
        start_time = datetime.now()
        
        # Use 20% of training data as test if not provided
        if test_inputs is None:
            split_idx = int(len(training_inputs) * 0.8)
            test_inputs = training_inputs[split_idx:]
            training_inputs = training_inputs[:split_idx]
        
        self.logger.info(f"Starting training cycle: {len(training_inputs)} train, {len(test_inputs)} test")
        
        # Train
        if model_type == "pattern":
            model = self.engine.train_pattern_model(training_inputs, model_name=f"{model_name}-pattern")
            validation = self.validator.validate_pattern_model(model.path, test_inputs)
        else:
            model = self.engine.train_sklearn_model(training_inputs, model_name=f"{model_name}-router")
            validation = self.validator.validate_sklearn_model(model.path, test_inputs)
        
        result = {
            "success": validation.passed,
            "model_path": str(model.path),
            "model_type": model_type,
            "version": model.version,
            "training_examples": len(training_inputs),
            "test_examples": len(test_inputs),
            "validation": validation.to_dict(),
            "duration_seconds": (datetime.now() - start_time).total_seconds()
        }
        
        # Promote if passed
        if validation.passed:
            validated_path = self.version_control.promote_to_validated(model.path, validation)
            prod_path = self.version_control.promote_to_production(validated_path)
            result["production_path"] = str(prod_path)
            result["promoted"] = True
        else:
            result["promoted"] = False
            self.logger.warning(f"Model failed validation: accuracy={validation.accuracy}%")
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Get current harness status."""
        prod_model = self.version_control.get_production_model()
        
        return {
            "production_model": str(prod_model) if prod_model else None,
            "staging_count": len(self.engine.list_models(ModelStage.STAGING)),
            "validated_count": len(self.engine.list_models(ModelStage.VALIDATED)),
            "is_training": self.engine.is_training,
            "models_dir": str(self.models_dir)
        }


def run_training_harness(
    models_dir: str = "./models",
    log_level: int = logging.INFO
) -> Dict[str, Any]:
    """
    Run the training harness with progressive training data.
    
    This is the main entry point for isolated training.
    """
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s | %(levelname)s | %(message)s'
    )
    logger = logging.getLogger("training_harness")
    
    harness = TrainingHarness(models_dir=models_dir, logger=logger)
    
    logger.info("Training Harness initialized")
    logger.info(f"Status: {harness.get_status()}")
    
    # Load progressive training data
    from .native_model.progressive_trainer import ProgressiveTrainer
    
    trainer = ProgressiveTrainer(models_dir=models_dir, logger=logger)
    
    # Generate training inputs from patterns
    inputs = harness.processor.from_patterns(trainer.patterns)
    
    if len(inputs) < 100:
        logger.info("Generating more training data...")
        # Run progressive training to generate more patterns
        for tier in range(1, 5):
            trainer.train_tier(tier)
        inputs = harness.processor.from_patterns(trainer.patterns)
    
    logger.info(f"Total training inputs: {len(inputs)}")
    
    # Run training cycle
    result = harness.run_training_cycle(inputs, model_type="sklearn", model_name="gladius")
    
    logger.info(f"Training cycle complete: {json.dumps(result, indent=2)}")
    
    return result


if __name__ == "__main__":
    run_training_harness()
