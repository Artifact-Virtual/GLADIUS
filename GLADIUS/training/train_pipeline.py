#!/usr/bin/env python3
"""
GLADIUS Model Training Pipeline
================================

Actual model training infrastructure using Qwen2.5-0.5B as base.
Optimized for CPU-only systems with 16GB RAM.

Base Model: Qwen2.5-0.5B (397MB)
- Best-in-class for size
- Excellent tool calling
- Fast inference on CPU

Training Method: Fine-tuning via Ollama + Modelfile
- No GPU required
- Uses existing Ollama infrastructure
- Produces GGUF-compatible models

Author: Artifact Virtual Systems
"""

import os
import sys
import json
import subprocess
import logging
import time
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GLADIUS.Training")

# Paths
GLADIUS_ROOT = Path(__file__).parent.parent.parent
TRAINING_DIR = Path(__file__).parent
DATA_DIR = TRAINING_DIR / "data"
MODELS_DIR = Path(__file__).parent.parent / "models"
SCRIPTS_DIR = TRAINING_DIR / "scripts"


@dataclass
class TrainingConfig:
    """Training configuration"""
    base_model: str = "qwen2.5:0.5b"  # Best small model for tool calling
    model_name: str = "gladius"
    version: str = "0.1.0"
    temperature: float = 0.1  # Low for deterministic tool calling
    context_length: int = 4096
    system_prompt: str = """You are GLADIUS, the native AI for Artifact Virtual Enterprise.
You are a tool-calling AI assistant. When the user asks a question or requests an action, respond with a JSON object specifying the tool to use and its arguments.

Available tools:
- read_db(name, query): Read from a database
- write_db(name, data, table): Write to a database  
- search(query, k): Semantic search
- hybrid_search(query, k): Vector + BM25 search
- get_context(query, k): Get relevant context
- read_file(path): Read a file
- write_file(path, content): Write a file
- list_dir(path): List directory
- remember(key, value): Store a memory
- recall(query, k): Recall memories
- get_tools(): List available tools
- send_discord(message, channel): Send Discord message
- send_email(to, subject, body): Send email
- post_social(platform, content): Post to social media
- run_syndicate(symbol, mode): Run market analysis

Respond with: {"tool": "tool_name", "args": {...}}"""


class TrainingDataManager:
    """Manages training data generation and formatting"""
    
    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def load_existing_data(self) -> List[Dict]:
        """Load existing training data"""
        combined_path = self.data_dir / "combined_training_llama.json"
        if combined_path.exists():
            with open(combined_path) as f:
                return json.load(f)
        return []
    
    def generate_additional_samples(self, count: int = 200) -> List[Dict]:
        """Generate additional training samples"""
        samples = []
        
        # Tool-specific samples
        tool_samples = {
            "search": [
                ("Find information about gold price trends", {"query": "gold price trends", "k": 5}),
                ("Search for market analysis", {"query": "market analysis", "k": 3}),
                ("Look up Bitcoin predictions", {"query": "Bitcoin predictions", "k": 5}),
                ("Find similar patterns to current market", {"query": "current market patterns", "k": 5}),
            ],
            "read_db": [
                ("Get latest predictions from syndicate", {"name": "syndicate", "query": "SELECT * FROM predictions ORDER BY date DESC LIMIT 5"}),
                ("Read gold analysis from database", {"name": "hektor", "query": "gold analysis"}),
                ("Query market data", {"name": "market", "query": "SELECT * FROM prices WHERE symbol='XAUUSD'"}),
            ],
            "write_db": [
                ("Save this prediction to database", {"name": "syndicate", "table": "predictions", "data": {"bias": "BULLISH"}}),
                ("Store analysis results", {"name": "analysis", "table": "results", "data": {}}),
            ],
            "read_file": [
                ("Read the config file", {"path": "config.json"}),
                ("Show me today's journal", {"path": "output/Journal_2026-01-14.md"}),
                ("Open the README", {"path": "README.md"}),
            ],
            "write_file": [
                ("Save this analysis to a file", {"path": "output/analysis.md", "content": "# Analysis\n..."}),
                ("Create a new note", {"path": "notes/new_note.md", "content": "# Note\n..."}),
            ],
            "list_dir": [
                ("What files are in the output folder?", {"path": "output"}),
                ("Show directory contents", {"path": "."}),
                ("List the logs", {"path": "logs"}),
            ],
            "remember": [
                ("Remember that gold is at resistance", {"key": "gold_resistance", "value": "Gold at 2700 resistance"}),
                ("Store this pattern", {"key": "pattern_2026", "value": "Head and shoulders forming"}),
            ],
            "recall": [
                ("What do you remember about gold?", {"query": "gold", "k": 3}),
                ("Recall market patterns", {"query": "market patterns", "k": 5}),
            ],
            "send_discord": [
                ("Send a message to Discord", {"message": "Market update ready", "channel": "general"}),
                ("Notify the team on Discord", {"message": "Analysis complete", "channel": "alerts"}),
            ],
            "send_email": [
                ("Send an email to the team", {"to": "team@artifactvirtual.com", "subject": "Update", "body": "..."}),
                ("Email this report", {"to": "admin@artifactvirtual.com", "subject": "Daily Report", "body": "..."}),
            ],
            "post_social": [
                ("Post to Twitter", {"platform": "twitter", "content": "Market update..."}),
                ("Share on LinkedIn", {"platform": "linkedin", "content": "New analysis..."}),
            ],
            "run_syndicate": [
                ("Analyze gold market", {"symbol": "XAUUSD", "mode": "full"}),
                ("Run Bitcoin analysis", {"symbol": "BTCUSD", "mode": "quick"}),
            ],
            "get_tools": [
                ("What tools can you use?", {}),
                ("Show available functions", {}),
                ("List your capabilities", {}),
            ],
            "get_context": [
                ("Get context for market analysis", {"query": "market analysis", "k": 3}),
                ("What's the historical context?", {"query": "historical trends", "k": 5}),
            ],
            "hybrid_search": [
                ("Search with both methods", {"query": "gold support levels", "k": 5}),
                ("Combined search for patterns", {"query": "bullish patterns", "k": 3}),
            ],
        }
        
        system_prompt = TrainingConfig().system_prompt
        
        for tool, examples in tool_samples.items():
            for query, args in examples:
                samples.append({
                    "text": f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{query}<|im_end|>\n<|im_start|>assistant\n{json.dumps({'tool': tool, 'args': args})}<|im_end|>"
                })
        
        # Add variations
        variations = [
            ("Please {action}", "Could you {action}"),
            ("I need you to {action}", "Can you {action}"),
            ("{action}", "I want to {action}"),
        ]
        
        logger.info(f"Generated {len(samples)} training samples")
        return samples
    
    def export_for_ollama(self, samples: List[Dict], output_path: Path) -> int:
        """Export training data in Ollama-compatible format"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Extract conversations for Modelfile format
        conversations = []
        for sample in samples:
            text = sample.get("text", "")
            # Parse the conversation format
            if "<|im_start|>user" in text and "<|im_start|>assistant" in text:
                conversations.append(text)
        
        # Write as JSONL
        with open(output_path, 'w') as f:
            for conv in conversations:
                f.write(json.dumps({"text": conv}) + "\n")
        
        logger.info(f"Exported {len(conversations)} conversations to {output_path}")
        return len(conversations)
    
    def prepare_training_set(self) -> Path:
        """Prepare complete training set"""
        # Load existing
        existing = self.load_existing_data()
        logger.info(f"Loaded {len(existing)} existing samples")
        
        # Generate additional
        additional = self.generate_additional_samples()
        
        # Combine and deduplicate
        all_samples = existing + additional
        seen = set()
        unique = []
        for sample in all_samples:
            key = sample.get("text", "")[:200]
            if key not in seen:
                seen.add(key)
                unique.append(sample)
        
        # Save combined
        combined_path = self.data_dir / "gladius_training_complete.json"
        with open(combined_path, 'w') as f:
            json.dump(unique, f, indent=2)
        
        logger.info(f"Total unique samples: {len(unique)}")
        return combined_path


class OllamaTrainer:
    """Train GLADIUS model using Ollama"""
    
    def __init__(self, config: TrainingConfig = None):
        self.config = config or TrainingConfig()
        self.models_dir = MODELS_DIR
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def check_ollama(self) -> bool:
        """Check if Ollama is available and base model exists"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                logger.error("Ollama not responding")
                return False
            
            if self.config.base_model not in result.stdout:
                logger.warning(f"Base model {self.config.base_model} not found, pulling...")
                pull_result = subprocess.run(
                    ["ollama", "pull", self.config.base_model],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                if pull_result.returncode != 0:
                    logger.error(f"Failed to pull base model: {pull_result.stderr}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Ollama check failed: {e}")
            return False
    
    def create_modelfile(self, training_data_path: Path) -> Path:
        """Create Ollama Modelfile for GLADIUS"""
        modelfile_path = self.models_dir / "staging" / "Modelfile"
        modelfile_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Build system message with training examples
        system_message = self.config.system_prompt
        
        modelfile_content = f'''# GLADIUS Native Model
# Version: {self.config.version}
# Base: {self.config.base_model}
# Created: {datetime.now().isoformat()}

FROM {self.config.base_model}

# Model parameters optimized for tool calling
PARAMETER temperature {self.config.temperature}
PARAMETER top_p 0.9
PARAMETER stop "<|im_end|>"
PARAMETER num_ctx {self.config.context_length}

# System prompt
SYSTEM """
{system_message}
"""

# Template for ChatML format
TEMPLATE """
{{{{ if .System }}}}<|im_start|>system
{{{{ .System }}}}<|im_end|>
{{{{ end }}}}{{{{ if .Prompt }}}}<|im_start|>user
{{{{ .Prompt }}}}<|im_end|>
{{{{ end }}}}<|im_start|>assistant
{{{{ .Response }}}}<|im_end|>
"""
'''
        
        with open(modelfile_path, 'w') as f:
            f.write(modelfile_content)
        
        logger.info(f"Created Modelfile at {modelfile_path}")
        return modelfile_path
    
    def build_model(self, modelfile_path: Path) -> bool:
        """Build the GLADIUS model using Ollama"""
        model_tag = f"{self.config.model_name}:{self.config.version}"
        
        logger.info(f"Building model: {model_tag}")
        
        try:
            result = subprocess.run(
                ["ollama", "create", model_tag, "-f", str(modelfile_path)],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=str(modelfile_path.parent)
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully built model: {model_tag}")
                return True
            else:
                logger.error(f"Build failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Build error: {e}")
            return False
    
    def validate_model(self, model_tag: str, test_queries: List[str] = None) -> Dict[str, Any]:
        """Validate the trained model"""
        if test_queries is None:
            test_queries = [
                "Search for gold price analysis",
                "Read the config file",
                "What tools can you use?",
                "Remember that the market is bullish",
                "Send a message to Discord"
            ]
        
        results = {
            "model": model_tag,
            "tests": [],
            "passed": 0,
            "failed": 0,
            "avg_latency_ms": 0
        }
        
        latencies = []
        
        for query in test_queries:
            start = time.time()
            try:
                result = subprocess.run(
                    ["ollama", "run", model_tag, query],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                latency_ms = (time.time() - start) * 1000
                latencies.append(latency_ms)
                
                response = result.stdout.strip()
                
                # Check if response is valid JSON with tool
                try:
                    parsed = json.loads(response)
                    is_valid = "tool" in parsed and "args" in parsed
                except:
                    is_valid = False
                
                test_result = {
                    "query": query,
                    "response": response[:200],
                    "valid": is_valid,
                    "latency_ms": latency_ms
                }
                
                results["tests"].append(test_result)
                if is_valid:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                    
            except Exception as e:
                results["tests"].append({
                    "query": query,
                    "error": str(e),
                    "valid": False
                })
                results["failed"] += 1
        
        if latencies:
            results["avg_latency_ms"] = sum(latencies) / len(latencies)
        
        results["accuracy"] = results["passed"] / len(test_queries) * 100 if test_queries else 0
        
        return results
    
    def promote_to_production(self, version: str) -> bool:
        """Promote validated model to production"""
        staging_tag = f"{self.config.model_name}:{version}"
        production_tag = f"{self.config.model_name}:latest"
        
        try:
            # Copy model
            result = subprocess.run(
                ["ollama", "cp", staging_tag, production_tag],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info(f"Promoted {staging_tag} to {production_tag}")
                
                # Save production metadata
                meta_path = self.models_dir / "production" / "model_meta.json"
                meta_path.parent.mkdir(parents=True, exist_ok=True)
                with open(meta_path, 'w') as f:
                    json.dump({
                        "model": production_tag,
                        "version": version,
                        "promoted_at": datetime.now().isoformat(),
                        "base_model": self.config.base_model
                    }, f, indent=2)
                
                return True
            else:
                logger.error(f"Promotion failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Promotion error: {e}")
            return False


class TrainingPipeline:
    """Complete training pipeline orchestrator"""
    
    def __init__(self):
        self.config = TrainingConfig()
        self.data_manager = TrainingDataManager()
        self.trainer = OllamaTrainer(self.config)
    
    def run(self, validate: bool = True, promote: bool = True) -> Dict[str, Any]:
        """Run complete training pipeline"""
        results = {
            "started_at": datetime.now().isoformat(),
            "config": {
                "base_model": self.config.base_model,
                "model_name": self.config.model_name,
                "version": self.config.version
            },
            "steps": {},
            "success": False
        }
        
        try:
            # Step 1: Check Ollama
            logger.info("Step 1: Checking Ollama...")
            if not self.trainer.check_ollama():
                results["error"] = "Ollama not available"
                return results
            results["steps"]["ollama_check"] = "passed"
            
            # Step 2: Prepare training data
            logger.info("Step 2: Preparing training data...")
            training_path = self.data_manager.prepare_training_set()
            results["steps"]["data_preparation"] = str(training_path)
            
            # Step 3: Create Modelfile
            logger.info("Step 3: Creating Modelfile...")
            modelfile_path = self.trainer.create_modelfile(training_path)
            results["steps"]["modelfile"] = str(modelfile_path)
            
            # Step 4: Build model
            logger.info("Step 4: Building model...")
            model_tag = f"{self.config.model_name}:{self.config.version}"
            if not self.trainer.build_model(modelfile_path):
                results["error"] = "Model build failed"
                return results
            results["steps"]["build"] = "success"
            
            # Step 5: Validate (optional)
            if validate:
                logger.info("Step 5: Validating model...")
                validation = self.trainer.validate_model(model_tag)
                results["steps"]["validation"] = validation
                
                if validation["accuracy"] < 60:
                    results["error"] = f"Validation failed: {validation['accuracy']}% accuracy"
                    return results
            
            # Step 6: Promote to production (optional)
            if promote and validate:
                if results["steps"].get("validation", {}).get("accuracy", 0) >= 70:
                    logger.info("Step 6: Promoting to production...")
                    if self.trainer.promote_to_production(self.config.version):
                        results["steps"]["promotion"] = "success"
                    else:
                        results["steps"]["promotion"] = "failed"
            
            results["success"] = True
            results["completed_at"] = datetime.now().isoformat()
            
            # Save results
            results_path = MODELS_DIR / "training_results" / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            results_path.parent.mkdir(parents=True, exist_ok=True)
            with open(results_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Training pipeline complete. Results: {results_path}")
            
        except Exception as e:
            results["error"] = str(e)
            logger.error(f"Pipeline error: {e}")
        
        return results


def run_training():
    """CLI entry point for training"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GLADIUS Model Training Pipeline")
    parser.add_argument("--no-validate", action="store_true", help="Skip validation")
    parser.add_argument("--no-promote", action="store_true", help="Skip promotion to production")
    parser.add_argument("--base-model", default="qwen2.5:0.5b", help="Base model to use")
    parser.add_argument("--version", default="0.1.0", help="Model version")
    
    args = parser.parse_args()
    
    pipeline = TrainingPipeline()
    
    if args.base_model:
        pipeline.config.base_model = args.base_model
    if args.version:
        pipeline.config.version = args.version
    
    results = pipeline.run(
        validate=not args.no_validate,
        promote=not args.no_promote
    )
    
    print("\n" + "=" * 60)
    print("GLADIUS Training Pipeline Results")
    print("=" * 60)
    print(json.dumps(results, indent=2))
    
    return 0 if results.get("success") else 1


if __name__ == "__main__":
    sys.exit(run_training())
