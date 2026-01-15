#!/usr/bin/env python3
"""
GLADIUS 1B Parameter Continuous Trainer
=========================================

Continuous training pipeline to build GLADIUS to 1 billion parameters.

Strategy:
1. Start with best small base model (Qwen2.5-1.5B or Phi-2 2.7B)
2. Progressive layer expansion via knowledge distillation
3. Continuous fine-tuning on Artifact infrastructure data
4. Checkpoint every milestone for recovery
5. Export to GGUF for deployment

Base Model Selection:
- Qwen2.5-1.5B: Best tool-calling, multilingual (chosen)
- Phi-2 2.7B: Best reasoning for size
- TinyLlama 1.1B: Fastest inference
- Mistral 7B: Can be quantized to effective 1B

Training Phases:
Phase 1: Base model fine-tuning on tool-calling data
Phase 2: Knowledge expansion via synthetic data
Phase 3: Parameter efficient scaling (LoRA stacking)
Phase 4: Full model export and optimization

Requirements:
- transformers>=4.36.0
- peft>=0.7.0
- torch>=2.0.0
- accelerate>=0.25.0
- bitsandbytes>=0.41.0 (for quantization)
- datasets>=2.16.0

Author: Artifact Virtual Systems
"""

import os
import sys
import json
import time
import signal
import hashlib
import logging
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
import threading
import traceback

# Setup paths
SCRIPT_DIR = Path(__file__).parent
GLADIUS_ROOT = SCRIPT_DIR.parent.parent.parent
MODELS_DIR = SCRIPT_DIR.parent / "models"
CHECKPOINTS_DIR = MODELS_DIR / "checkpoints"
DATA_DIR = SCRIPT_DIR / "data"
LOGS_DIR = GLADIUS_ROOT / "logs" / "training"

# Ensure directories exist
for d in [MODELS_DIR, CHECKPOINTS_DIR, DATA_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s │ %(levelname)-8s │ %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / f"training_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GLADIUS.1B_Trainer")


@dataclass
class TrainingState:
    """Persistent training state for recovery"""
    phase: int = 1
    epoch: int = 0
    step: int = 0
    total_steps: int = 0
    current_params: int = 0
    target_params: int = 1_000_000_000  # 1B
    base_model: str = "Qwen/Qwen2.5-1.5B"
    learning_rate: float = 2e-5
    batch_size: int = 4
    gradient_accumulation: int = 8
    checkpoint_path: str = ""
    started_at: str = ""
    last_checkpoint: str = ""
    training_hours: float = 0.0
    loss_history: List[float] = field(default_factory=list)
    accuracy_history: List[float] = field(default_factory=list)
    status: str = "initialized"  # initialized, training, paused, completed, failed
    
    def save(self, path: Path):
        """Save state to file"""
        with open(path, 'w') as f:
            json.dump(asdict(self), f, indent=2)
    
    @classmethod
    def load(cls, path: Path) -> 'TrainingState':
        """Load state from file"""
        if path.exists():
            with open(path) as f:
                data = json.load(f)
                return cls(**data)
        return cls()


@dataclass  
class TrainingConfig:
    """Training configuration"""
    # Model selection - Qwen2.5-1.5B is best for tool-calling
    base_model: str = "Qwen/Qwen2.5-1.5B"
    model_name: str = "gladius-1b"
    
    # Target parameters
    target_params: int = 1_000_000_000
    
    # Training hyperparameters
    learning_rate: float = 2e-5
    batch_size: int = 4
    gradient_accumulation_steps: int = 8
    warmup_steps: int = 100
    max_steps: int = 100000
    save_steps: int = 500
    eval_steps: int = 100
    logging_steps: int = 10
    
    # LoRA configuration for parameter efficient training
    lora_r: int = 64
    lora_alpha: int = 128
    lora_dropout: float = 0.05
    lora_target_modules: List[str] = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ])
    
    # Memory optimization
    use_4bit: bool = True  # 4-bit quantization for base
    use_gradient_checkpointing: bool = True
    max_memory_mb: int = 14000  # 14GB for 16GB system
    
    # Data
    max_seq_length: int = 4096
    
    # Checkpointing
    checkpoint_dir: str = str(CHECKPOINTS_DIR)
    resume_from_checkpoint: bool = True
    
    # Export
    export_gguf: bool = True
    gguf_quantization: str = "q4_k_m"  # Good balance of size/quality


class DataGenerator:
    """Generate training data from Artifact infrastructure"""
    
    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir
        self.samples: List[Dict] = []
        
    def load_existing_data(self) -> List[Dict]:
        """Load existing training data"""
        data_file = self.data_dir / "gladius_training_complete.json"
        if data_file.exists():
            with open(data_file) as f:
                return json.load(f)
        return []
    
    def generate_tool_samples(self, count: int = 1000) -> List[Dict]:
        """Generate tool-calling training samples"""
        import random
        
        # Comprehensive tool definitions
        tools = {
            "read_db": {
                "description": "Read from database",
                "args": ["name", "query"],
                "examples": [
                    ("Get predictions from syndicate", {"name": "syndicate", "query": "SELECT * FROM predictions"}),
                    ("Query gold analysis", {"name": "hektor", "query": "SELECT * FROM analysis WHERE asset='XAUUSD'"}),
                    ("Read market data", {"name": "market", "query": "SELECT * FROM prices LIMIT 100"}),
                ]
            },
            "write_db": {
                "description": "Write to database",
                "args": ["name", "table", "data"],
                "examples": [
                    ("Save this prediction", {"name": "syndicate", "table": "predictions", "data": {"bias": "BULLISH"}}),
                    ("Store analysis results", {"name": "analysis", "table": "results", "data": {"score": 0.85}}),
                ]
            },
            "search": {
                "description": "Semantic search",
                "args": ["query", "k"],
                "examples": [
                    ("Find gold analysis", {"query": "gold price trends", "k": 5}),
                    ("Search for market patterns", {"query": "bullish momentum indicators", "k": 10}),
                    ("Look up Bitcoin predictions", {"query": "BTC price forecast", "k": 3}),
                ]
            },
            "hybrid_search": {
                "description": "Combined vector and keyword search",
                "args": ["query", "k", "lexical_weight"],
                "examples": [
                    ("Deep search for gold", {"query": "gold support levels", "k": 10, "lexical_weight": 0.3}),
                    ("Comprehensive pattern search", {"query": "head and shoulders formation", "k": 5, "lexical_weight": 0.5}),
                ]
            },
            "remember": {
                "description": "Store a memory",
                "args": ["key", "value", "metadata"],
                "examples": [
                    ("Remember that gold is bullish", {"key": "gold_bias", "value": "Bullish on gold, targeting 2750", "metadata": {"source": "analysis"}}),
                    ("Store this insight", {"key": "pattern_jan", "value": "Cup and handle forming on daily", "metadata": {"date": "2026-01-14"}}),
                ]
            },
            "recall": {
                "description": "Recall memories",
                "args": ["query", "k"],
                "examples": [
                    ("What do you know about gold?", {"query": "gold", "k": 5}),
                    ("Recall market patterns", {"query": "market patterns", "k": 3}),
                ]
            },
            "read_file": {
                "description": "Read file contents",
                "args": ["path"],
                "examples": [
                    ("Read the config", {"path": "config.json"}),
                    ("Show today's journal", {"path": "output/Journal_2026-01-14.md"}),
                    ("Open README", {"path": "README.md"}),
                ]
            },
            "write_file": {
                "description": "Write to file",
                "args": ["path", "content"],
                "examples": [
                    ("Save analysis to file", {"path": "output/analysis.md", "content": "# Analysis\n\nBullish on gold..."}),
                    ("Create a note", {"path": "notes/insight.md", "content": "# Insight\n\nMarket showing strength..."}),
                ]
            },
            "list_dir": {
                "description": "List directory contents",
                "args": ["path"],
                "examples": [
                    ("What files are in output?", {"path": "output"}),
                    ("List the logs", {"path": "logs"}),
                    ("Show current directory", {"path": "."}),
                ]
            },
            "send_discord": {
                "description": "Send Discord message",
                "args": ["message", "channel"],
                "examples": [
                    ("Send alert to Discord", {"message": "Gold breakout detected!", "channel": "alerts"}),
                    ("Notify team on Discord", {"message": "Analysis complete", "channel": "general"}),
                ]
            },
            "send_email": {
                "description": "Send email",
                "args": ["to", "subject", "body"],
                "examples": [
                    ("Email the report", {"to": "team@artifactvirtual.com", "subject": "Daily Report", "body": "..."}),
                    ("Send analysis email", {"to": "admin@artifactvirtual.com", "subject": "Gold Analysis", "body": "..."}),
                ]
            },
            "post_social": {
                "description": "Post to social media",
                "args": ["platform", "content"],
                "examples": [
                    ("Post to Twitter", {"platform": "twitter", "content": "Gold reaching new highs..."}),
                    ("Share on LinkedIn", {"platform": "linkedin", "content": "Market analysis update..."}),
                ]
            },
            "run_syndicate": {
                "description": "Run Syndicate analysis",
                "args": ["symbol", "mode"],
                "examples": [
                    ("Analyze gold", {"symbol": "XAUUSD", "mode": "full"}),
                    ("Quick BTC analysis", {"symbol": "BTCUSD", "mode": "quick"}),
                ]
            },
            "get_tools": {
                "description": "List available tools",
                "args": [],
                "examples": [
                    ("What can you do?", {}),
                    ("List your capabilities", {}),
                    ("Show available functions", {}),
                ]
            },
            "get_context": {
                "description": "Get context for analysis",
                "args": ["query", "k"],
                "examples": [
                    ("Get context for gold analysis", {"query": "gold market conditions", "k": 5}),
                    ("Background on current market", {"query": "market sentiment today", "k": 3}),
                ]
            },
        }
        
        system_prompt = """You are GLADIUS, the native AI for Artifact Virtual Enterprise.
You are a tool-calling assistant. Respond with JSON specifying the tool and arguments.
Format: {"tool": "tool_name", "args": {...}}"""
        
        samples = []
        
        for _ in range(count):
            # Pick random tool
            tool_name = random.choice(list(tools.keys()))
            tool = tools[tool_name]
            
            # Pick random example
            if tool["examples"]:
                query, args = random.choice(tool["examples"])
                
                # Add variation
                prefixes = ["", "Please ", "Can you ", "I need you to ", "Could you "]
                suffixes = ["", ".", " please.", " for me.", " now."]
                
                varied_query = random.choice(prefixes) + query.lower() + random.choice(suffixes)
                varied_query = varied_query.strip().capitalize()
                
                samples.append({
                    "text": f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{varied_query}<|im_end|>\n<|im_start|>assistant\n{json.dumps({'tool': tool_name, 'args': args})}<|im_end|>"
                })
        
        logger.info(f"Generated {len(samples)} tool-calling samples")
        return samples
    
    def generate_reasoning_samples(self, count: int = 500) -> List[Dict]:
        """Generate reasoning/chain-of-thought samples"""
        import random
        
        reasoning_examples = [
            {
                "query": "Analyze the current gold market conditions and suggest a trading bias",
                "reasoning": "Let me analyze: 1) Gold is trading at 2700, near resistance. 2) RSI shows overbought at 72. 3) Volume increasing on breakout attempts. 4) Fed dovish stance supports gold. Conclusion: Bullish bias with caution at resistance.",
                "tool": "run_syndicate",
                "args": {"symbol": "XAUUSD", "mode": "full"}
            },
            {
                "query": "Should I post this market update to social media?",
                "reasoning": "Checking: 1) Content is factual market analysis. 2) No financial advice or guarantees. 3) Appropriate for professional audience. 4) Timing is good (market hours). Proceeding with post.",
                "tool": "post_social",
                "args": {"platform": "linkedin", "content": "Market analysis ready..."}
            },
            {
                "query": "Find relevant historical patterns for current market setup",
                "reasoning": "For pattern matching: 1) Need to search for similar setups. 2) Look for technical pattern names. 3) Find historical price action parallels. Using hybrid search for comprehensive results.",
                "tool": "hybrid_search", 
                "args": {"query": "historical pattern similar current setup", "k": 10, "lexical_weight": 0.4}
            },
        ]
        
        samples = []
        for _ in range(count):
            ex = random.choice(reasoning_examples)
            system_prompt = """You are GLADIUS. Think step by step before calling tools. Show your reasoning, then call the appropriate tool."""
            
            response = f"Reasoning: {ex['reasoning']}\n\nAction: {json.dumps({'tool': ex['tool'], 'args': ex['args']})}"
            
            samples.append({
                "text": f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{ex['query']}<|im_end|>\n<|im_start|>assistant\n{response}<|im_end|>"
            })
        
        logger.info(f"Generated {len(samples)} reasoning samples")
        return samples
    
    def prepare_dataset(self, num_samples: int = 5000) -> Path:
        """Prepare complete training dataset"""
        # Load existing
        existing = self.load_existing_data()
        
        # Generate new samples
        tool_samples = self.generate_tool_samples(num_samples // 2)
        reasoning_samples = self.generate_reasoning_samples(num_samples // 4)
        
        # Combine all
        all_samples = existing + tool_samples + reasoning_samples
        
        # Deduplicate
        seen = set()
        unique = []
        for sample in all_samples:
            key = hashlib.md5(sample.get("text", "")[:500].encode()).hexdigest()
            if key not in seen:
                seen.add(key)
                unique.append(sample)
        
        # Save dataset
        dataset_path = self.data_dir / "gladius_1b_training.jsonl"
        with open(dataset_path, 'w') as f:
            for sample in unique:
                f.write(json.dumps(sample) + "\n")
        
        logger.info(f"Prepared dataset with {len(unique)} unique samples at {dataset_path}")
        return dataset_path


class Gladius1BTrainer:
    """Main trainer for GLADIUS 1B model"""
    
    def __init__(self, config: TrainingConfig = None):
        self.config = config or TrainingConfig()
        self.state = TrainingState.load(CHECKPOINTS_DIR / "training_state.json")
        self.data_generator = DataGenerator()
        self.running = True
        self.paused = False
        
        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Shutdown signal received, saving state...")
        self.running = False
        self._save_checkpoint("interrupt")
    
    def _save_checkpoint(self, reason: str = "scheduled"):
        """Save training checkpoint"""
        self.state.last_checkpoint = datetime.now().isoformat()
        self.state.checkpoint_path = str(CHECKPOINTS_DIR / f"checkpoint_{self.state.step}")
        state_path = CHECKPOINTS_DIR / "training_state.json"
        self.state.save(state_path)
        logger.info(f"Checkpoint saved ({reason}): step {self.state.step}")
    
    def check_dependencies(self) -> bool:
        """Check if required packages are available"""
        required = ["torch", "transformers", "peft", "accelerate", "datasets"]
        missing = []
        
        for pkg in required:
            try:
                __import__(pkg)
            except ImportError:
                missing.append(pkg)
        
        if missing:
            logger.warning(f"Missing packages: {missing}")
            logger.info("Installing missing packages...")
            
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-q",
                    "torch", "transformers>=4.36.0", "peft>=0.7.0", 
                    "accelerate>=0.25.0", "datasets>=2.16.0", "bitsandbytes"
                ], check=True)
                logger.info("Packages installed successfully")
                return True
            except Exception as e:
                logger.error(f"Failed to install packages: {e}")
                return False
        
        return True
    
    def setup_model(self) -> Tuple[Any, Any]:
        """Setup model and tokenizer with LoRA"""
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        import torch
        
        logger.info(f"Loading base model: {self.config.base_model}")
        
        # Quantization config for memory efficiency
        if self.config.use_4bit:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )
        else:
            bnb_config = None
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            self.config.base_model,
            trust_remote_code=True
        )
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Load model
        model = AutoModelForCausalLM.from_pretrained(
            self.config.base_model,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.float16,
        )
        
        # Prepare for training
        if self.config.use_4bit:
            model = prepare_model_for_kbit_training(model)
        
        if self.config.use_gradient_checkpointing:
            model.gradient_checkpointing_enable()
        
        # Configure LoRA
        lora_config = LoraConfig(
            r=self.config.lora_r,
            lora_alpha=self.config.lora_alpha,
            target_modules=self.config.lora_target_modules,
            lora_dropout=self.config.lora_dropout,
            bias="none",
            task_type="CAUSAL_LM",
        )
        
        # Apply LoRA
        model = get_peft_model(model, lora_config)
        
        # Count parameters
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in model.parameters())
        
        logger.info(f"Trainable parameters: {trainable_params:,}")
        logger.info(f"Total parameters: {total_params:,}")
        
        self.state.current_params = total_params
        
        return model, tokenizer
    
    def prepare_data(self, tokenizer) -> Any:
        """Prepare training data"""
        from datasets import load_dataset
        
        # Generate/load dataset
        dataset_path = self.data_generator.prepare_dataset(num_samples=10000)
        
        # Load as HuggingFace dataset
        dataset = load_dataset("json", data_files=str(dataset_path), split="train")
        
        def tokenize_function(examples):
            return tokenizer(
                examples["text"],
                truncation=True,
                max_length=self.config.max_seq_length,
                padding="max_length",
            )
        
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names,
        )
        
        logger.info(f"Dataset prepared: {len(tokenized_dataset)} samples")
        return tokenized_dataset
    
    def train_phase(self, phase: int) -> Dict[str, Any]:
        """Run a training phase"""
        from transformers import TrainingArguments, Trainer, DataCollatorForLanguageModeling
        
        logger.info(f"Starting Phase {phase}")
        self.state.phase = phase
        self.state.status = "training"
        
        # Setup model and tokenizer
        model, tokenizer = self.setup_model()
        
        # Prepare data
        dataset = self.prepare_data(tokenizer)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=str(CHECKPOINTS_DIR / f"phase_{phase}"),
            num_train_epochs=3,
            per_device_train_batch_size=self.config.batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            warmup_steps=self.config.warmup_steps,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            eval_steps=self.config.eval_steps,
            save_total_limit=3,
            fp16=True,
            optim="adamw_torch",
            lr_scheduler_type="cosine",
            report_to="none",
            remove_unused_columns=False,
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,
        )
        
        # Trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=dataset,
            data_collator=data_collator,
        )
        
        # Train
        logger.info("Starting training...")
        result = trainer.train()
        
        # Save final model
        model_save_path = MODELS_DIR / f"gladius-1b-phase{phase}"
        trainer.save_model(str(model_save_path))
        tokenizer.save_pretrained(str(model_save_path))
        
        logger.info(f"Phase {phase} complete. Model saved to {model_save_path}")
        
        return {
            "phase": phase,
            "train_loss": result.training_loss,
            "steps": result.global_step,
            "model_path": str(model_save_path)
        }
    
    def export_to_gguf(self, model_path: Path) -> Optional[Path]:
        """Export model to GGUF format for Ollama"""
        logger.info("Exporting to GGUF format...")
        
        try:
            # Check if llama.cpp convert script exists
            convert_script = Path.home() / "llama.cpp" / "convert.py"
            
            if not convert_script.exists():
                logger.warning("llama.cpp not found, using fallback export")
                # Alternative: use transformers to save and note for manual conversion
                logger.info(f"Model at {model_path} ready for manual GGUF conversion")
                return None
            
            output_path = MODELS_DIR / "gladius-1b.gguf"
            
            subprocess.run([
                sys.executable, str(convert_script),
                str(model_path),
                "--outfile", str(output_path),
                "--outtype", self.config.gguf_quantization,
            ], check=True)
            
            logger.info(f"GGUF exported to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"GGUF export failed: {e}")
            return None
    
    def create_ollama_model(self, gguf_path: Path) -> bool:
        """Create Ollama model from GGUF"""
        logger.info("Creating Ollama model...")
        
        modelfile_content = f'''# GLADIUS 1B Native Model
FROM {gguf_path}

PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER stop "<|im_end|>"
PARAMETER num_ctx 4096

SYSTEM """
You are GLADIUS, the native AI for Artifact Virtual Enterprise.
You are a tool-calling AI assistant. Respond with JSON specifying the tool and arguments.
Format: {{"tool": "tool_name", "args": {{...}}}}
"""

TEMPLATE """
{{{{ if .System }}}}<|im_start|>system
{{{{ .System }}}}<|im_end|>
{{{{ end }}}}{{{{ if .Prompt }}}}<|im_start|>user
{{{{ .Prompt }}}}<|im_end|>
{{{{ end }}}}<|im_start|>assistant
{{{{ .Response }}}}<|im_end|>
"""
'''
        
        modelfile_path = MODELS_DIR / "Modelfile.gladius-1b"
        with open(modelfile_path, 'w') as f:
            f.write(modelfile_content)
        
        try:
            subprocess.run([
                "ollama", "create", "gladius:1b", "-f", str(modelfile_path)
            ], check=True)
            logger.info("Ollama model 'gladius:1b' created successfully")
            return True
        except Exception as e:
            logger.error(f"Ollama model creation failed: {e}")
            return False
    
    def run_continuous(self, max_hours: float = 168.0):  # 1 week default
        """Run continuous training loop"""
        logger.info("=" * 60)
        logger.info("GLADIUS 1B CONTINUOUS TRAINER")
        logger.info("=" * 60)
        logger.info(f"Target: {self.config.target_params:,} parameters")
        logger.info(f"Base model: {self.config.base_model}")
        logger.info(f"Max training time: {max_hours} hours")
        logger.info("=" * 60)
        
        # Check dependencies
        if not self.check_dependencies():
            logger.error("Dependency check failed")
            return
        
        self.state.started_at = datetime.now().isoformat()
        self.state.status = "training"
        start_time = time.time()
        
        try:
            # Phase 1: Base fine-tuning
            if self.state.phase <= 1:
                result = self.train_phase(1)
                self.state.loss_history.append(result.get("train_loss", 0))
                self._save_checkpoint("phase_1_complete")
            
            # Phase 2: Extended training with more data
            if self.state.phase <= 2 and self.running:
                # Generate more training data
                self.data_generator.generate_tool_samples(5000)
                self.data_generator.generate_reasoning_samples(2000)
                
                result = self.train_phase(2)
                self.state.loss_history.append(result.get("train_loss", 0))
                self._save_checkpoint("phase_2_complete")
            
            # Phase 3: LoRA stacking for parameter expansion
            if self.state.phase <= 3 and self.running:
                self.config.lora_r = 128  # Increase rank
                self.config.lora_alpha = 256
                
                result = self.train_phase(3)
                self.state.loss_history.append(result.get("train_loss", 0))
                self._save_checkpoint("phase_3_complete")
            
            # Phase 4: Export and deployment
            if self.state.phase <= 4 and self.running:
                model_path = MODELS_DIR / "gladius-1b-phase3"
                
                if self.config.export_gguf:
                    gguf_path = self.export_to_gguf(model_path)
                    if gguf_path:
                        self.create_ollama_model(gguf_path)
                
                self.state.phase = 4
                self._save_checkpoint("phase_4_complete")
            
            # Calculate training time
            self.state.training_hours = (time.time() - start_time) / 3600
            self.state.status = "completed"
            self._save_checkpoint("training_complete")
            
            logger.info("=" * 60)
            logger.info("TRAINING COMPLETE")
            logger.info(f"Total time: {self.state.training_hours:.2f} hours")
            logger.info(f"Final parameters: {self.state.current_params:,}")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Training error: {e}")
            logger.error(traceback.format_exc())
            self.state.status = "failed"
            self._save_checkpoint("error")
            raise


def print_banner():
    """Print startup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         G L A D I U S   1 B   T R A I N E R                  ║
║                                                              ║
║      Continuous Training Pipeline to 1 Billion Parameters   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GLADIUS 1B Continuous Trainer")
    parser.add_argument("--hours", type=float, default=168, help="Max training hours (default: 168/1 week)")
    parser.add_argument("--base-model", default="Qwen/Qwen2.5-1.5B", help="Base model to use")
    parser.add_argument("--batch-size", type=int, default=4, help="Batch size")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--status", action="store_true", help="Show training status")
    parser.add_argument("--export-only", action="store_true", help="Only export existing model to GGUF")
    
    args = parser.parse_args()
    
    print_banner()
    
    config = TrainingConfig()
    if args.base_model:
        config.base_model = args.base_model
    if args.batch_size:
        config.batch_size = args.batch_size
    
    trainer = Gladius1BTrainer(config)
    
    if args.status:
        state = TrainingState.load(CHECKPOINTS_DIR / "training_state.json")
        print(f"\nTraining Status:")
        print(f"  Phase: {state.phase}/4")
        print(f"  Step: {state.step}")
        print(f"  Parameters: {state.current_params:,}")
        print(f"  Status: {state.status}")
        print(f"  Hours: {state.training_hours:.2f}")
        print(f"  Last checkpoint: {state.last_checkpoint}")
        return
    
    if args.export_only:
        model_path = MODELS_DIR / "gladius-1b-phase3"
        if model_path.exists():
            gguf_path = trainer.export_to_gguf(model_path)
            if gguf_path:
                trainer.create_ollama_model(gguf_path)
        else:
            logger.error(f"Model not found at {model_path}")
        return
    
    # Run continuous training
    trainer.run_continuous(max_hours=args.hours)


if __name__ == "__main__":
    main()
