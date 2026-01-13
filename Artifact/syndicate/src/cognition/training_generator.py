"""
Training Data Generator - Generate fine-tuning data from tool call history.

Creates training datasets in formats suitable for:
- llama.cpp fine-tuning (GGUF)
- ONNX model training
- LoRA adapters

The goal is to train a tiny GGUF model that can call tools natively
without relying on third-party LLMs.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
import hashlib

from .tool_calling import ToolRegistry, TOOL_REGISTRY, ToolDefinition


@dataclass
class TrainingExample:
    """A single training example for tool calling."""
    id: str
    prompt: str
    tool_call: Dict[str, Any]  # {"tool": name, "args": {...}}
    result: Any
    success: bool
    context: Optional[str] = None
    category: str = "general"
    timestamp: str = ""
    
    def to_chat_format(self) -> Dict[str, Any]:
        """Convert to chat format for instruction tuning."""
        return {
            "messages": [
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": self.prompt},
                {"role": "assistant", "content": json.dumps(self.tool_call)},
            ],
            "metadata": {
                "id": self.id,
                "category": self.category,
                "success": self.success,
                "timestamp": self.timestamp
            }
        }
    
    def to_completion_format(self) -> Dict[str, Any]:
        """Convert to completion format for causal LM training."""
        full_prompt = f"{self._get_system_prompt()}\n\nUser: {self.prompt}\nAssistant:"
        completion = json.dumps(self.tool_call)
        
        return {
            "prompt": full_prompt,
            "completion": completion,
            "metadata": {
                "id": self.id,
                "category": self.category
            }
        }
    
    def to_tool_format(self) -> Dict[str, Any]:
        """Convert to tool-calling format (OpenAI-style)."""
        return {
            "messages": [
                {"role": "user", "content": self.prompt}
            ],
            "tool_calls": [
                {
                    "type": "function",
                    "function": {
                        "name": self.tool_call.get("tool"),
                        "arguments": json.dumps(self.tool_call.get("args", {}))
                    }
                }
            ],
            "tool_results": [
                {
                    "tool_call_id": self.id,
                    "output": json.dumps(self.result) if not isinstance(self.result, str) else self.result
                }
            ]
        }
    
    def _get_system_prompt(self) -> str:
        """Get appropriate system prompt."""
        return """You are a tool-calling AI assistant. When the user asks a question or requests an action, respond with a JSON object specifying the tool to use and its arguments.

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

Respond with: {"tool": "tool_name", "args": {...}}"""


@dataclass
class TrainingDataset:
    """A collection of training examples."""
    name: str
    examples: List[TrainingExample] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0"
    
    def add(self, example: TrainingExample):
        """Add an example to the dataset."""
        self.examples.append(example)
    
    def filter_by_category(self, category: str) -> List[TrainingExample]:
        """Filter examples by category."""
        return [e for e in self.examples if e.category == category]
    
    def filter_successful(self) -> List[TrainingExample]:
        """Get only successful examples."""
        return [e for e in self.examples if e.success]
    
    def split(self, train_ratio: float = 0.8) -> Tuple[List[TrainingExample], List[TrainingExample]]:
        """Split into train/validation sets."""
        import random
        examples = self.examples.copy()
        random.shuffle(examples)
        split_idx = int(len(examples) * train_ratio)
        return examples[:split_idx], examples[split_idx:]
    
    def export_jsonl(self, path: str, format: str = "chat"):
        """Export to JSONL format."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            for example in self.examples:
                if format == "chat":
                    line = example.to_chat_format()
                elif format == "completion":
                    line = example.to_completion_format()
                elif format == "tool":
                    line = example.to_tool_format()
                else:
                    line = asdict(example)
                
                f.write(json.dumps(line) + "\n")
    
    def export_for_llama_cpp(self, path: str):
        """Export in format suitable for llama.cpp fine-tuning."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # llama.cpp expects a specific format
        training_data = []
        for example in self.filter_successful():
            training_data.append({
                "text": f"<|im_start|>system\n{example._get_system_prompt()}<|im_end|>\n<|im_start|>user\n{example.prompt}<|im_end|>\n<|im_start|>assistant\n{json.dumps(example.tool_call)}<|im_end|>"
            })
        
        with open(path, 'w') as f:
            json.dump(training_data, f, indent=2)
    
    def stats(self) -> Dict[str, Any]:
        """Get dataset statistics."""
        categories = {}
        for e in self.examples:
            categories[e.category] = categories.get(e.category, 0) + 1
        
        return {
            "total_examples": len(self.examples),
            "successful": len(self.filter_successful()),
            "failed": len(self.examples) - len(self.filter_successful()),
            "categories": categories,
            "created_at": self.created_at,
            "version": self.version
        }


class TrainingDataGenerator:
    """
    Generate training data from tool call history for fine-tuning.
    
    Collects tool usage patterns from the memory module and converts
    them into training examples for native tool calling.
    """
    
    def __init__(
        self,
        output_dir: str = "./data/training",
        logger: Optional[logging.Logger] = None
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger or logging.getLogger(__name__)
        self.registry = TOOL_REGISTRY
        
        # Synthetic example templates
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, List[Dict]]:
        """Load or generate synthetic training templates."""
        return {
            "database": [
                {
                    "prompt": "What databases are available?",
                    "tool": "list_databases",
                    "args": {}
                },
                {
                    "prompt": "Read the last 5 predictions from syndicate database",
                    "tool": "read_db",
                    "args": {"name": "syndicate", "query": "SELECT * FROM predictions ORDER BY date DESC LIMIT 5"}
                },
                {
                    "prompt": "Search for gold price predictions",
                    "tool": "read_db",
                    "args": {"name": "hektor", "query": "gold price predictions"}
                },
            ],
            "search": [
                {
                    "prompt": "Find similar patterns to gold breakout above 2700",
                    "tool": "search",
                    "args": {"query": "gold breakout above 2700", "k": 5}
                },
                {
                    "prompt": "Search for resistance level analysis",
                    "tool": "hybrid_search",
                    "args": {"query": "resistance level analysis", "k": 5}
                },
                {
                    "prompt": "Get historical context for current market conditions",
                    "tool": "get_context",
                    "args": {"query": "current market conditions", "k": 3}
                },
            ],
            "workspace": [
                {
                    "prompt": "Read today's journal",
                    "tool": "read_file",
                    "args": {"path": "output/Journal_2026-01-13.md"}
                },
                {
                    "prompt": "What files are in the output directory?",
                    "tool": "list_dir",
                    "args": {"path": "output"}
                },
                {
                    "prompt": "Save this analysis to a file",
                    "tool": "write_file",
                    "args": {"path": "output/analysis.md", "content": "# Analysis\n..."}
                },
                {
                    "prompt": "Check if config exists",
                    "tool": "file_exists",
                    "args": {"path": "config.json"}
                },
            ],
            "memory": [
                {
                    "prompt": "Remember that gold showed head and shoulders pattern",
                    "tool": "remember",
                    "args": {"key": "gold_pattern_2026", "value": "Gold showed head and shoulders pattern at 2700 resistance"}
                },
                {
                    "prompt": "What do you remember about gold patterns?",
                    "tool": "recall",
                    "args": {"query": "gold patterns", "k": 3}
                },
                {
                    "prompt": "Forget the old trading strategy",
                    "tool": "forget",
                    "args": {"key": "old_strategy"}
                },
            ],
            "introspection": [
                {
                    "prompt": "What tools can you use?",
                    "tool": "get_tools",
                    "args": {}
                },
                {
                    "prompt": "Show me what you've done recently",
                    "tool": "get_history",
                    "args": {"last_n": 10}
                },
            ],
        }
    
    def generate_from_history(
        self,
        history: List[Dict[str, Any]],
        dataset_name: str = "history"
    ) -> TrainingDataset:
        """
        Generate training data from operation history.
        
        Args:
            history: List of operations from MemoryModule.history
            dataset_name: Name for the dataset
        
        Returns:
            TrainingDataset ready for export
        """
        dataset = TrainingDataset(name=dataset_name)
        
        for i, op in enumerate(history):
            # Generate a natural language prompt from the operation
            prompt = self._generate_prompt_from_op(op)
            
            example = TrainingExample(
                id=f"{dataset_name}_{i}_{hashlib.md5(str(op).encode()).hexdigest()[:8]}",
                prompt=prompt,
                tool_call={"tool": op.get("tool"), "args": dict(zip(["arg1", "arg2"], op.get("args", [])))},
                result=op.get("result"),
                success=op.get("success", True),
                category=self._get_tool_category(op.get("tool", "")),
                timestamp=op.get("timestamp", datetime.now().isoformat())
            )
            
            dataset.add(example)
        
        self.logger.info(f"[TRAINING] Generated {len(dataset.examples)} examples from history")
        return dataset
    
    def generate_synthetic(
        self,
        n_per_category: int = 10,
        dataset_name: str = "synthetic"
    ) -> TrainingDataset:
        """
        Generate synthetic training data from templates.
        
        Args:
            n_per_category: Number of examples per category
            dataset_name: Name for the dataset
        
        Returns:
            TrainingDataset with synthetic examples
        """
        dataset = TrainingDataset(name=dataset_name)
        
        for category, templates in self.templates.items():
            for i, template in enumerate(templates):
                if i >= n_per_category:
                    break
                
                example = TrainingExample(
                    id=f"synth_{category}_{i}",
                    prompt=template["prompt"],
                    tool_call={"tool": template["tool"], "args": template["args"]},
                    result={"synthetic": True},
                    success=True,
                    category=category,
                    timestamp=datetime.now().isoformat()
                )
                
                dataset.add(example)
        
        self.logger.info(f"[TRAINING] Generated {len(dataset.examples)} synthetic examples")
        return dataset
    
    def generate_from_tool_schemas(
        self,
        dataset_name: str = "schema"
    ) -> TrainingDataset:
        """
        Generate training examples from tool schemas and their examples.
        
        Uses the examples defined in ToolDefinition objects.
        """
        dataset = TrainingDataset(name=dataset_name)
        
        for tool in self.registry.list_tools():
            for i, ex in enumerate(tool.examples):
                example = TrainingExample(
                    id=f"schema_{tool.name}_{i}",
                    prompt=f"Use {tool.name}: {tool.description[:100]}...",
                    tool_call={"tool": tool.name, "args": ex.get("args", {})},
                    result=ex.get("result"),
                    success=True,
                    category=tool.category,
                    timestamp=datetime.now().isoformat()
                )
                
                dataset.add(example)
        
        self.logger.info(f"[TRAINING] Generated {len(dataset.examples)} examples from schemas")
        return dataset
    
    def combine_datasets(
        self,
        datasets: List[TrainingDataset],
        name: str = "combined"
    ) -> TrainingDataset:
        """Combine multiple datasets into one."""
        combined = TrainingDataset(name=name)
        
        for ds in datasets:
            for example in ds.examples:
                combined.add(example)
        
        return combined
    
    def export_all(
        self,
        datasets: List[TrainingDataset],
        formats: List[str] = ["chat", "completion", "llama"]
    ) -> Dict[str, str]:
        """
        Export datasets in multiple formats.
        
        Returns:
            Dict of format -> file path
        """
        paths = {}
        
        for ds in datasets:
            for fmt in formats:
                if fmt == "llama":
                    path = self.output_dir / f"{ds.name}_llama.json"
                    ds.export_for_llama_cpp(path)
                else:
                    path = self.output_dir / f"{ds.name}_{fmt}.jsonl"
                    ds.export_jsonl(path, format=fmt)
                
                paths[f"{ds.name}_{fmt}"] = str(path)
                self.logger.info(f"[TRAINING] Exported {ds.name} in {fmt} format to {path}")
        
        return paths
    
    def _generate_prompt_from_op(self, op: Dict) -> str:
        """Generate a natural language prompt from an operation."""
        tool = op.get("tool", "unknown")
        args = op.get("args", [])
        
        prompt_templates = {
            "read_db": f"Read from database: {args[0] if args else 'unknown'}",
            "write_db": f"Write to database: {args[0] if args else 'unknown'}",
            "search": f"Search for: {args[0] if args else 'query'}",
            "hybrid_search": f"Find information about: {args[0] if args else 'query'}",
            "get_context": f"Get context for: {args[0] if args else 'topic'}",
            "read_file": f"Read file: {args[0] if args else 'file'}",
            "write_file": f"Write to file: {args[0] if args else 'file'}",
            "list_dir": f"List directory: {args[0] if args else '.'}",
            "remember": f"Remember: {args[0] if args else 'something'}",
            "recall": f"Recall: {args[0] if args else 'memory'}",
        }
        
        return prompt_templates.get(tool, f"Use {tool} with {args}")
    
    def _get_tool_category(self, tool_name: str) -> str:
        """Get category for a tool."""
        tool = self.registry.get(tool_name)
        return tool.category if tool else "unknown"


class FineTuningPipeline:
    """
    Pipeline for fine-tuning a GGUF model on tool calling data.
    
    Uses llama.cpp's training capabilities to create a specialized
    tool-calling model from a base model.
    """
    
    def __init__(
        self,
        base_model: str,
        output_dir: str = "./models/finetuned",
        logger: Optional[logging.Logger] = None
    ):
        self.base_model = Path(base_model)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger or logging.getLogger(__name__)
    
    def prepare_training_data(
        self,
        generator: TrainingDataGenerator,
        history: Optional[List[Dict]] = None
    ) -> Path:
        """Prepare training data for fine-tuning."""
        datasets = []
        
        # Generate from history if available
        if history:
            datasets.append(generator.generate_from_history(history))
        
        # Add synthetic examples
        datasets.append(generator.generate_synthetic(n_per_category=20))
        
        # Add schema examples
        datasets.append(generator.generate_from_tool_schemas())
        
        # Combine all
        combined = generator.combine_datasets(datasets, "tool_calling_training")
        
        # Export for llama.cpp
        output_path = generator.output_dir / "tool_calling_training_llama.json"
        combined.export_for_llama_cpp(output_path)
        
        self.logger.info(f"[FINETUNE] Prepared {len(combined.examples)} training examples")
        return output_path
    
    def train(
        self,
        training_data: Path,
        epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 1e-4,
        lora_rank: int = 8
    ) -> Optional[Path]:
        """
        Run fine-tuning using llama.cpp.
        
        Note: This requires llama.cpp built with training support.
        Returns path to the fine-tuned model or None if not available.
        """
        # Check if llama.cpp training is available
        llama_train = Path("/usr/local/bin/llama-finetune")
        if not llama_train.exists():
            # Try in hektor build
            llama_train = Path("./Artifact/hektor/build/llama.cpp/bin/llama-finetune")
        
        if not llama_train.exists():
            self.logger.warning("[FINETUNE] llama-finetune not found. Training not available.")
            self.logger.info("[FINETUNE] To enable: build llama.cpp with -DLLAMA_BUILD_TRAIN=ON")
            return None
        
        output_model = self.output_dir / f"gladius_tools_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gguf"
        
        # Build command
        cmd = [
            str(llama_train),
            "--model-base", str(self.base_model),
            "--train-data", str(training_data),
            "--save-every", "100",
            "--threads", "4",
            "--ctx-size", "2048",
            "--batch", str(batch_size),
            "--epochs", str(epochs),
            "--learning-rate", str(learning_rate),
            "--lora-out", str(output_model),
            "--lora-r", str(lora_rank)
        ]
        
        self.logger.info(f"[FINETUNE] Starting training: {' '.join(cmd)}")
        
        import subprocess
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            
            if result.returncode == 0:
                self.logger.info(f"[FINETUNE] Training complete: {output_model}")
                return output_model
            else:
                self.logger.error(f"[FINETUNE] Training failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error("[FINETUNE] Training timed out")
            return None
        except Exception as e:
            self.logger.error(f"[FINETUNE] Training error: {e}")
            return None
    
    def validate(self, model_path: Path, test_prompts: List[str]) -> Dict[str, Any]:
        """Validate the fine-tuned model on test prompts."""
        results = {
            "model": str(model_path),
            "tests": [],
            "accuracy": 0.0
        }
        
        # TODO: Implement validation using llama.cpp inference
        self.logger.info(f"[FINETUNE] Validation not yet implemented for {model_path}")
        
        return results
