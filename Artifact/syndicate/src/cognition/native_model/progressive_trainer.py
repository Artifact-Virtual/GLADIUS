"""
Progressive Tool Learning - Train Gladius GGUF model progressively.

Philosophy:
- Start with simplest tools (no args) → progress to complex
- Never let accuracy fall below 100%
- Recursive refinement until mastery
- Each tier must be perfect before advancing

Tiers:
1. Zero-arg tools: list_databases, get_tools, get_history
2. Single-arg tools: list_dir, read_file, file_exists
3. Query tools: search, recall, get_context, hybrid_search
4. Complex tools: remember, read_db, write_file
5. Multi-modal: full infra + automata integration
"""

import json
import logging
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import random


@dataclass
class ToolComplexity:
    """Tool with complexity rating."""
    name: str
    tier: int  # 1-5
    args: List[str]
    description: str
    examples: List[Dict[str, Any]] = field(default_factory=list)


# Tool registry organized by complexity
TOOL_COMPLEXITY_TIERS = {
    1: [  # Zero-arg tools
        ToolComplexity("list_databases", 1, [], "List all available databases"),
        ToolComplexity("get_tools", 1, [], "List available tools"),
        ToolComplexity("get_history", 1, ["last_n"], "Get operation history"),
    ],
    2: [  # Single-arg tools
        ToolComplexity("list_dir", 2, ["path"], "List directory contents"),
        ToolComplexity("read_file", 2, ["path"], "Read file contents"),
        ToolComplexity("file_exists", 2, ["path"], "Check if file exists"),
    ],
    3: [  # Query-based tools
        ToolComplexity("search", 3, ["query", "k"], "Semantic search"),
        ToolComplexity("recall", 3, ["query", "k"], "Recall memories"),
        ToolComplexity("get_context", 3, ["query", "k"], "Get context for analysis"),
        ToolComplexity("hybrid_search", 3, ["query", "k", "lexical_weight"], "Hybrid search"),
    ],
    4: [  # Complex tools
        ToolComplexity("remember", 4, ["key", "value", "metadata"], "Store memory"),
        ToolComplexity("forget", 4, ["key"], "Forget memory"),
        ToolComplexity("read_db", 4, ["name", "query"], "Query database"),
        ToolComplexity("write_file", 4, ["path", "content"], "Write to file"),
    ],
    5: [  # Multi-modal / advanced
        ToolComplexity("write_db", 5, ["name", "query", "params"], "Write to database"),
        ToolComplexity("execute_workflow", 5, ["workflow_id", "params"], "Execute workflow"),
        ToolComplexity("schedule_task", 5, ["task", "schedule", "params"], "Schedule task"),
        ToolComplexity("publish_content", 5, ["platform", "content", "metadata"], "Publish content"),
    ],
}


@dataclass
class TierProgress:
    """Progress for a training tier."""
    tier: int
    tools: List[str]
    examples_generated: int
    accuracy: float
    iterations: int
    complete: bool
    timestamp: str


class ProgressiveTrainer:
    """
    Progressive training for Gladius GGUF.
    
    Training loop:
    1. Start with Tier 1 (zero-arg tools)
    2. Generate examples, train, validate
    3. If accuracy < 100%, generate more examples, retrain
    4. When Tier N is perfect, advance to Tier N+1
    5. Continue until all tiers mastered
    """
    
    def __init__(
        self,
        models_dir: str = "./models",
        examples_per_tool: int = 50,
        max_iterations_per_tier: int = 20,
        target_accuracy: float = 100.0,
        logger: Optional[logging.Logger] = None
    ):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.examples_per_tool = examples_per_tool
        self.max_iterations = max_iterations_per_tier
        self.target_accuracy = target_accuracy
        self.logger = logger or logging.getLogger(__name__)
        
        # Progress tracking
        self.progress: Dict[int, TierProgress] = {}
        self.current_tier = 1
        self.total_examples = 0
        self.patterns: Dict[str, List[Dict]] = {}
        
        # Load existing progress
        self._load_progress()
    
    def _load_progress(self):
        """Load existing training progress."""
        progress_file = self.models_dir / "progressive_training.json"
        if progress_file.exists():
            with open(progress_file) as f:
                data = json.load(f)
                self.current_tier = data.get("current_tier", 1)
                self.total_examples = data.get("total_examples", 0)
                self.patterns = data.get("patterns", {})
                for tier_data in data.get("tiers", []):
                    self.progress[tier_data["tier"]] = TierProgress(**tier_data)
    
    def _save_progress(self):
        """Save training progress."""
        progress_file = self.models_dir / "progressive_training.json"
        data = {
            "current_tier": self.current_tier,
            "total_examples": self.total_examples,
            "patterns": self.patterns,
            "tiers": [
                {
                    "tier": p.tier,
                    "tools": p.tools,
                    "examples_generated": p.examples_generated,
                    "accuracy": p.accuracy,
                    "iterations": p.iterations,
                    "complete": p.complete,
                    "timestamp": p.timestamp
                }
                for p in self.progress.values()
            ],
            "last_updated": datetime.now().isoformat()
        }
        with open(progress_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def generate_examples(self, tool: ToolComplexity, n: int) -> List[Dict[str, Any]]:
        """Generate training examples for a tool."""
        examples = []
        
        # Natural language query templates per tool
        templates = {
            # Tier 1 - Zero arg
            "list_databases": [
                "What databases are available?",
                "Show me all databases",
                "List databases",
                "What data stores do we have?",
                "Which databases can I query?",
            ],
            "get_tools": [
                "What tools do you have?",
                "Show available tools",
                "What can you do?",
                "List your capabilities",
                "What functions are available?",
            ],
            "get_history": [
                "Show recent operations",
                "What have you done recently?",
                "Display history",
                "Show last {n} operations",
                "What actions were taken?",
            ],
            # Tier 2 - Single arg
            "list_dir": [
                "List files in {path}",
                "What's in the {path} directory?",
                "Show {path} contents",
                "ls {path}",
                "Directory listing for {path}",
            ],
            "read_file": [
                "Read {path}",
                "Show contents of {path}",
                "Open {path}",
                "Display {path}",
                "Cat {path}",
            ],
            "file_exists": [
                "Does {path} exist?",
                "Check if {path} exists",
                "Is there a file at {path}?",
                "Verify {path} presence",
            ],
            # Tier 3 - Query based
            "search": [
                "Search for {query}",
                "Find {query}",
                "Look for {query}",
                "Query: {query}",
                "Search documents about {query}",
            ],
            "recall": [
                "What do you remember about {query}?",
                "Recall {query}",
                "Remember anything about {query}?",
                "What was stored about {query}?",
            ],
            "get_context": [
                "Get context for {query}",
                "What's the context about {query}?",
                "Context for analyzing {query}",
                "Background on {query}",
            ],
            "hybrid_search": [
                "Hybrid search for {query}",
                "Deep search {query}",
                "Comprehensive search: {query}",
                "Search with BM25: {query}",
            ],
            # Tier 4 - Complex
            "remember": [
                "Remember that {value}",
                "Store this: {value}",
                "Save note: {value}",
                "Memorize: {value}",
            ],
            "forget": [
                "Forget {key}",
                "Delete memory {key}",
                "Remove {key} from memory",
                "Clear {key}",
            ],
            "read_db": [
                "Query {name} database: {query}",
                "SELECT from {name}: {query}",
                "Read {name} for {query}",
                "Database query on {name}",
            ],
            "write_file": [
                "Save {content} to {path}",
                "Write to {path}: {content}",
                "Create file {path} with {content}",
            ],
            # Tier 5 - Advanced
            "write_db": [
                "Insert into {name}: {query}",
                "Write to {name} database",
                "Store in {name}: {params}",
            ],
            "execute_workflow": [
                "Run workflow {workflow_id}",
                "Execute {workflow_id} with {params}",
                "Start workflow {workflow_id}",
            ],
            "schedule_task": [
                "Schedule {task} for {schedule}",
                "Set up recurring {task}",
                "Plan {task} at {schedule}",
            ],
            "publish_content": [
                "Publish to {platform}: {content}",
                "Post on {platform}",
                "Share {content} to {platform}",
            ],
        }
        
        # Sample values for substitution
        paths = ["output/", "data/", "reports/", "config.json", "analysis.md", "Journal_2026-01-13.md"]
        queries = ["gold bullish momentum", "market analysis", "resistance levels", "technical patterns", "sentiment"]
        keys = ["pattern_1", "insight_2026", "trade_setup", "market_regime"]
        values = ["Gold broke above 2700", "Bullish momentum confirmed", "RSI overbought at 75"]
        db_names = ["syndicate", "hektor", "cortex", "gold_standard"]
        
        tool_templates = templates.get(tool.name, [f"Call {tool.name}"])
        
        for i in range(n):
            template = random.choice(tool_templates)
            
            # Substitute placeholders
            query = template.format(
                path=random.choice(paths),
                query=random.choice(queries),
                key=random.choice(keys),
                value=random.choice(values),
                name=random.choice(db_names),
                n=random.randint(5, 20),
                content="Sample content here",
                workflow_id=f"workflow_{random.randint(1, 10)}",
                task="daily_analysis",
                schedule="every 4 hours",
                platform=random.choice(["discord", "linkedin", "twitter"]),
                params="{}",
            )
            
            # Build args based on tool
            args = {}
            if tool.name == "list_dir":
                args = {"path": random.choice(paths).rstrip("/")}
            elif tool.name == "read_file":
                args = {"path": random.choice(paths)}
            elif tool.name == "file_exists":
                args = {"path": random.choice(paths)}
            elif tool.name == "search":
                args = {"query": random.choice(queries), "k": 5}
            elif tool.name == "recall":
                args = {"query": random.choice(queries), "k": 3}
            elif tool.name == "get_context":
                args = {"query": random.choice(queries), "k": 3}
            elif tool.name == "hybrid_search":
                args = {"query": random.choice(queries), "k": 5, "lexical_weight": 0.3}
            elif tool.name == "remember":
                args = {"key": random.choice(keys), "value": random.choice(values)}
            elif tool.name == "forget":
                args = {"key": random.choice(keys)}
            elif tool.name == "read_db":
                args = {"name": random.choice(db_names), "query": "SELECT * FROM data LIMIT 10"}
            elif tool.name == "write_file":
                args = {"path": f"output/gen_{i}.md", "content": "Generated content"}
            elif tool.name == "get_history":
                args = {"last_n": 10}
            # Zero-arg tools have empty args
            
            examples.append({
                "messages": [
                    {"role": "system", "content": "You are Gladius, a tool router. Output JSON with the tool to call."},
                    {"role": "user", "content": query},
                    {"role": "assistant", "content": json.dumps({"tool": tool.name, "args": args})}
                ],
                "metadata": {"tool": tool.name, "tier": tool.tier}
            })
            
            # Also add to patterns
            if tool.name not in self.patterns:
                self.patterns[tool.name] = []
            self.patterns[tool.name].append({"query": query.lower(), "args": args})
        
        return examples
    
    def train_tier(self, tier: int) -> TierProgress:
        """Train all tools in a tier until 100% accuracy."""
        tools = TOOL_COMPLEXITY_TIERS.get(tier, [])
        if not tools:
            self.logger.warning(f"No tools defined for tier {tier}")
            return None
        
        tool_names = [t.name for t in tools]
        self.logger.info(f"Training Tier {tier}: {tool_names}")
        
        progress = TierProgress(
            tier=tier,
            tools=tool_names,
            examples_generated=0,
            accuracy=0.0,
            iterations=0,
            complete=False,
            timestamp=datetime.now().isoformat()
        )
        
        for iteration in range(self.max_iterations):
            # Generate examples for each tool
            all_examples = []
            for tool in tools:
                examples = self.generate_examples(tool, self.examples_per_tool)
                all_examples.extend(examples)
                progress.examples_generated += len(examples)
            
            self.total_examples += len(all_examples)
            
            # Train (update pattern model)
            self._update_pattern_model()
            
            # Validate
            accuracy = self._validate_tier(tier, all_examples)
            progress.accuracy = accuracy
            progress.iterations = iteration + 1
            
            self.logger.info(f"Tier {tier} iteration {iteration + 1}: accuracy={accuracy:.1f}%")
            
            if accuracy >= self.target_accuracy:
                progress.complete = True
                progress.timestamp = datetime.now().isoformat()
                break
            
            # If not perfect, generate more diverse examples
            self.examples_per_tool += 10
        
        self.progress[tier] = progress
        self._save_progress()
        
        return progress
    
    def _update_pattern_model(self):
        """Update the pattern model with current patterns."""
        model_path = self.models_dir / "gladius-progressive.patterns.json"
        
        model_data = {
            "type": "pattern_model",
            "model_name": "gladius-progressive",
            "created_at": datetime.now().isoformat(),
            "patterns": self.patterns,
            "total_examples": self.total_examples,
            "tiers_complete": len([p for p in self.progress.values() if p.complete])
        }
        
        with open(model_path, 'w') as f:
            json.dump(model_data, f, indent=2)
    
    def _validate_tier(self, tier: int, examples: List[Dict]) -> float:
        """Validate accuracy for a tier."""
        from .router import NativeToolRouter
        
        model_path = self.models_dir / "gladius-progressive.patterns.json"
        router = NativeToolRouter(pattern_model_path=str(model_path))
        
        correct = 0
        total = 0
        
        for ex in examples:
            messages = ex.get("messages", [])
            expected_tool = None
            user_query = None
            
            for msg in messages:
                if msg["role"] == "user":
                    user_query = msg["content"]
                elif msg["role"] == "assistant":
                    try:
                        expected = json.loads(msg["content"])
                        expected_tool = expected.get("tool")
                    except:
                        pass
            
            if user_query and expected_tool:
                result = router.route(user_query, prefer_source="pattern")
                if result.tool_name == expected_tool:
                    correct += 1
                total += 1
        
        return (correct / total * 100) if total > 0 else 0.0
    
    def train_all(self) -> Dict[str, Any]:
        """Train all tiers progressively."""
        results = {
            "started_at": datetime.now().isoformat(),
            "tiers": {},
            "total_examples": 0,
            "all_complete": False
        }
        
        for tier in range(1, 6):
            self.logger.info(f"\n{'='*50}")
            self.logger.info(f"STARTING TIER {tier}")
            self.logger.info(f"{'='*50}")
            
            progress = self.train_tier(tier)
            if progress:
                results["tiers"][tier] = {
                    "tools": progress.tools,
                    "examples": progress.examples_generated,
                    "accuracy": progress.accuracy,
                    "iterations": progress.iterations,
                    "complete": progress.complete
                }
                
                if not progress.complete:
                    self.logger.warning(f"Tier {tier} did not reach 100% accuracy")
                    break
        
        results["completed_at"] = datetime.now().isoformat()
        results["total_examples"] = self.total_examples
        results["all_complete"] = all(
            self.progress.get(t, TierProgress(t, [], 0, 0, 0, False, "")).complete
            for t in range(1, 6)
        )
        
        return results
    
    def stats(self) -> Dict[str, Any]:
        """Get training statistics."""
        return {
            "current_tier": self.current_tier,
            "total_examples": self.total_examples,
            "tiers_complete": len([p for p in self.progress.values() if p.complete]),
            "patterns_by_tool": {k: len(v) for k, v in self.patterns.items()},
            "progress": {
                t: {
                    "accuracy": p.accuracy,
                    "iterations": p.iterations,
                    "complete": p.complete
                }
                for t, p in self.progress.items()
            }
        }


def run_progressive_training(models_dir: str = "./models", log_level: int = logging.INFO):
    """Run the full progressive training pipeline."""
    logging.basicConfig(level=log_level, format='%(asctime)s | %(levelname)s | %(message)s')
    logger = logging.getLogger("progressive_trainer")
    
    trainer = ProgressiveTrainer(
        models_dir=models_dir,
        examples_per_tool=50,
        max_iterations_per_tier=20,
        target_accuracy=100.0,
        logger=logger
    )
    
    logger.info("Starting Progressive Training for Gladius GGUF")
    logger.info(f"Current state: {trainer.stats()}")
    
    results = trainer.train_all()
    
    logger.info("\n" + "="*60)
    logger.info("TRAINING COMPLETE")
    logger.info("="*60)
    logger.info(json.dumps(results, indent=2))
    
    return results


if __name__ == "__main__":
    run_progressive_training()
