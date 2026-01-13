#!/usr/bin/env python3
"""
Native Tool Model Training Script
Trains a tiny GGUF model for native tool calling.

Usage:
    python scripts/train_native_model.py --iterations 100
"""

import os
import sys
import json
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add paths
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT / "Artifact" / "syndicate" / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [TRAIN] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(PROJECT_ROOT / "logs" / "training.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def train_native_model(iterations: int = 100, batch_size: int = 10):
    """
    Train the native tool router model.
    
    Args:
        iterations: Number of training iterations
        batch_size: Examples per batch
    """
    from cognition.training_generator import TrainingDataGenerator
    from cognition.native_model.trainer import ModelTrainer, TrainingConfig
    from cognition.native_model.router import NativeToolRouter
    
    logger.info(f"Starting training: {iterations} iterations, batch size {batch_size}")
    
    # Initialize components
    data_dir = PROJECT_ROOT / "Artifact" / "syndicate" / "data" / "training"
    models_dir = PROJECT_ROOT / "Artifact" / "syndicate" / "models"
    
    generator = TrainingDataGenerator(str(data_dir))
    trainer = ModelTrainer(config=TrainingConfig(
        output_dir=str(models_dir),
        epochs=1,  # Per iteration
        batch_size=batch_size,
    ))
    
    # Training stats
    stats = {
        "start_time": datetime.now().isoformat(),
        "iterations_completed": 0,
        "total_examples": 0,
        "best_accuracy": 0.0,
        "models_created": [],
        "errors": []
    }
    
    for iteration in range(iterations):
        try:
            logger.info(f"Iteration {iteration + 1}/{iterations}")
            
            # Generate training data
            # Combine synthetic + historical data
            synthetic_ds = generator.generate_synthetic(
                n_per_category=5,
                dataset_name=f"iter_{iteration}"
            )
            
            # Convert to training format
            training_data = []
            for ex in synthetic_ds.examples:
                # TrainingExample has to_chat_format() method
                if hasattr(ex, 'to_chat_format'):
                    training_data.append(ex.to_chat_format())
                elif isinstance(ex, dict):
                    training_data.append({
                        "messages": [
                            {"role": "system", "content": "You are a tool router. Output JSON with the tool to call."},
                            {"role": "user", "content": ex.get("input", ex.get("prompt", ""))},
                            {"role": "assistant", "content": json.dumps({"tool": ex.get("expected_tool", "search"), "args": ex.get("expected_args", {})})}
                        ]
                    })
                else:
                    # Try accessing as object attributes
                    training_data.append({
                        "messages": [
                            {"role": "system", "content": "You are a tool router. Output JSON with the tool to call."},
                            {"role": "user", "content": getattr(ex, 'prompt', str(ex))},
                            {"role": "assistant", "content": json.dumps(getattr(ex, 'tool_call', {"tool": "search", "args": {}}))}
                        ]
                    })
            
            stats["total_examples"] += len(training_data)
            
            # Train
            metrics = trainer.train(
                training_data=training_data,
                model_name=f"tool-router-v{iteration + 1}"
            )
            
            if metrics.success:
                stats["models_created"].append({
                    "iteration": iteration + 1,
                    "model_path": metrics.output_model_path,
                    "examples": len(training_data),
                    "time_s": metrics.training_time_s
                })
                
                # Validate if pattern model was created
                if metrics.output_model_path and Path(metrics.output_model_path).exists():
                    if metrics.output_model_path.endswith('.patterns.json'):
                        # Test pattern model routing
                        test_router = NativeToolRouter(
                            pattern_model_path=metrics.output_model_path,
                            use_native=False,
                            use_ollama=False
                        )
                        test_queries = [
                            "Search for gold price",
                            "Read the file config.json",
                            "List files in the data directory",
                            "Remember this: important note",
                            "What do you know about markets?"
                        ]
                        correct = 0
                        for q in test_queries:
                            result = test_router.route(q)
                            if result.success:
                                correct += 1
                        
                        accuracy = correct / len(test_queries) * 100
                        if accuracy > stats["best_accuracy"]:
                            stats["best_accuracy"] = accuracy
                            logger.info(f"New best accuracy: {accuracy:.1f}%")
            
            stats["iterations_completed"] = iteration + 1
            
            # Save progress
            progress_file = models_dir / "training_progress.json"
            with open(progress_file, 'w') as f:
                json.dump(stats, f, indent=2)
            
            # Small delay to avoid CPU saturation
            time.sleep(0.1)
            
        except Exception as e:
            logger.error(f"Iteration {iteration + 1} failed: {e}")
            stats["errors"].append({
                "iteration": iteration + 1,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    # Final stats
    stats["end_time"] = datetime.now().isoformat()
    stats["status"] = "completed"
    
    # Save final progress
    progress_file = models_dir / "training_progress.json"
    with open(progress_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    # Generate final consolidated model
    logger.info("Generating consolidated pattern model...")
    
    # Collect all patterns from iterations
    all_patterns = {}
    for model_info in stats["models_created"]:
        model_path = Path(model_info["model_path"])
        if model_path.exists() and model_path.suffix == '.json':
            try:
                with open(model_path) as f:
                    data = json.load(f)
                    patterns = data.get("patterns", {})
                    for tool, examples in patterns.items():
                        if tool not in all_patterns:
                            all_patterns[tool] = []
                        all_patterns[tool].extend(examples)
            except Exception as e:
                logger.warning(f"Failed to load {model_path}: {e}")
    
    # Deduplicate and save consolidated model
    for tool in all_patterns:
        seen = set()
        unique = []
        for ex in all_patterns[tool]:
            key = ex.get("query", "")[:100]
            if key not in seen:
                seen.add(key)
                unique.append(ex)
        all_patterns[tool] = unique
    
    consolidated_model = {
        "type": "pattern_model",
        "model_name": "tool-router-consolidated",
        "created_at": datetime.now().isoformat(),
        "iterations": stats["iterations_completed"],
        "patterns": all_patterns,
        "total_examples": sum(len(v) for v in all_patterns.values())
    }
    
    consolidated_path = models_dir / "tool-router-consolidated.patterns.json"
    with open(consolidated_path, 'w') as f:
        json.dump(consolidated_model, f, indent=2)
    
    logger.info(f"Training complete!")
    logger.info(f"  Iterations: {stats['iterations_completed']}")
    logger.info(f"  Examples: {stats['total_examples']}")
    logger.info(f"  Best accuracy: {stats['best_accuracy']:.1f}%")
    logger.info(f"  Consolidated model: {consolidated_path}")
    
    return stats


def main():
    parser = argparse.ArgumentParser(description="Train native tool model")
    parser.add_argument("--iterations", type=int, default=100, help="Training iterations")
    parser.add_argument("--batch-size", type=int, default=10, help="Batch size")
    args = parser.parse_args()
    
    # Create logs directory
    (PROJECT_ROOT / "logs").mkdir(exist_ok=True)
    
    stats = train_native_model(
        iterations=args.iterations,
        batch_size=args.batch_size
    )
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
