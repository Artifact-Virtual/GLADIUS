#!/usr/bin/env python3
"""
QWEN OPERATIONAL AI
===================

Qwen2.5-1.5B with LoRA fine-tuning for Artifact Virtual infrastructure.

Purpose:
- Immediate operational capability for Artifact tools
- Tool-calling for infrastructure management
- Cognition and pattern-based modeling
- Powers Artifact's automation suite until GLADIUS native is ready

This is NOT GLADIUS. This is Artifact's operational AI that:
1. Manages infrastructure
2. Runs cognition patterns
3. Powers automation
4. Will eventually be replaced by GLADIUS native model

Author: Artifact Virtual Systems
"""

import os
import sys
import json
import time
import signal
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict

# Paths
SCRIPT_DIR = Path(__file__).parent
ARTIFACT_ROOT = SCRIPT_DIR
GLADIUS_ROOT = SCRIPT_DIR.parent
MODELS_DIR = ARTIFACT_ROOT / "models" / "qwen"
CHECKPOINTS_DIR = MODELS_DIR / "checkpoints"
DATA_DIR = ARTIFACT_ROOT / "data" / "training"
LOGS_DIR = GLADIUS_ROOT / "logs" / "qwen"

# Ensure directories
for d in [MODELS_DIR, CHECKPOINTS_DIR, DATA_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | QWEN-OP | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / f"qwen_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Artifact.QwenOperational")


@dataclass
class QwenState:
    """Training state for Qwen operational model"""
    phase: int = 0
    step: int = 0
    epoch: int = 0
    loss: float = 0.0
    status: str = "pending"  # pending, training, ready, failed
    model_path: str = ""
    started_at: str = ""
    training_hours: float = 0.0
    
    def save(self, path: Path):
        with open(path, 'w') as f:
            json.dump(asdict(self), f, indent=2)
    
    @classmethod
    def load(cls, path: Path) -> 'QwenState':
        if path.exists():
            with open(path) as f:
                return cls(**json.load(f))
        return cls()


class QwenOperationalTrainer:
    """
    Train Qwen2.5-1.5B for Artifact infrastructure operations.
    
    This model handles:
    - Tool calling for Artifact systems
    - Cognition and pattern recognition
    - Automation workflows
    - Infrastructure management
    
    NOT a replacement for GLADIUS - this is Artifact's workhorse until
    GLADIUS native model is complete.
    """
    
    def __init__(self):
        self.model_name = "Qwen/Qwen2.5-1.5B"
        self.state = QwenState.load(CHECKPOINTS_DIR / "qwen_state.json")
        self.running = True
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        logger.info("Shutdown signal received...")
        self.running = False
        self._save_state()
    
    def _save_state(self):
        self.state.save(CHECKPOINTS_DIR / "qwen_state.json")
        logger.info("State saved")
    
    def check_dependencies(self) -> bool:
        """Check and install required packages"""
        required = ["torch", "transformers", "peft", "accelerate", "datasets"]
        missing = []
        
        for pkg in required:
            try:
                __import__(pkg)
            except ImportError:
                missing.append(pkg)
        
        if missing:
            logger.info(f"Installing: {missing}")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-q",
                "torch", "transformers>=4.36.0", "peft>=0.7.0",
                "accelerate>=0.25.0", "datasets>=2.16.0", "bitsandbytes"
            ], check=True)
        
        return True
    
    def generate_training_data(self, output_path: Path, num_samples: int = 5000) -> None:
        """Generate training data for Artifact tool operations"""
        import random
        
        # Artifact infrastructure tools
        tools = {
            "read_db": [
                ("Query the database", {"name": "syndicate", "query": "SELECT * FROM predictions"}),
                ("Get analysis data", {"name": "hektor", "query": "SELECT * FROM analysis"}),
                ("Read market data", {"name": "market", "query": "SELECT * FROM prices"}),
            ],
            "write_db": [
                ("Save prediction", {"name": "syndicate", "table": "predictions", "data": {}}),
                ("Store analysis", {"name": "analysis", "table": "results", "data": {}}),
            ],
            "search": [
                ("Search for gold analysis", {"query": "gold price trends", "k": 5}),
                ("Find market patterns", {"query": "bullish momentum", "k": 10}),
            ],
            "hybrid_search": [
                ("Deep search patterns", {"query": "technical patterns", "k": 10, "lexical_weight": 0.3}),
            ],
            "remember": [
                ("Remember gold is bullish", {"key": "gold_bias", "value": "Bullish", "metadata": {}}),
            ],
            "recall": [
                ("What do you know about gold?", {"query": "gold", "k": 5}),
            ],
            "send_discord": [
                ("Send alert to Discord", {"message": "Alert!", "channel": "alerts"}),
            ],
            "send_email": [
                ("Email report", {"to": "team@artifactvirtual.com", "subject": "Report", "body": "..."}),
            ],
            "post_social": [
                ("Post to Twitter", {"platform": "twitter", "content": "Market update..."}),
                ("Share on LinkedIn", {"platform": "linkedin", "content": "Analysis ready..."}),
            ],
            "run_syndicate": [
                ("Analyze gold", {"symbol": "XAUUSD", "mode": "full"}),
                ("Quick BTC check", {"symbol": "BTCUSD", "mode": "quick"}),
            ],
            "run_legion": [
                ("Deploy agents", {"department": "research", "task": "market_scan"}),
                ("Check agent status", {"department": "all", "task": "status"}),
            ],
            "get_tools": [
                ("What can you do?", {}),
                ("List capabilities", {}),
            ],
        }
        
        system = """You are the Artifact Virtual operational AI.
You manage Artifact's infrastructure, tools, and automation.
Respond with JSON: {"tool": "name", "args": {...}}"""
        
        samples = []
        for _ in range(num_samples):
            tool_name = random.choice(list(tools.keys()))
            query, args = random.choice(tools[tool_name])
            
            # Variations
            prefixes = ["", "Please ", "Can you ", "I need to "]
            query = random.choice(prefixes) + query
            
            samples.append({
                "text": f"<|im_start|>system\n{system}<|im_end|>\n<|im_start|>user\n{query}<|im_end|>\n<|im_start|>assistant\n{json.dumps({'tool': tool_name, 'args': args})}<|im_end|>"
            })
        
        with open(output_path, 'w') as f:
            for s in samples:
                f.write(json.dumps(s) + "\n")
        
        logger.info(f"Generated {len(samples)} training samples")
    
    def train(self) -> bool:
        """Train Qwen with LoRA for Artifact operations"""
        logger.info("=" * 60)
        logger.info("ARTIFACT QWEN OPERATIONAL TRAINER")
        logger.info("=" * 60)
        logger.info(f"Model: {self.model_name}")
        logger.info("Purpose: Artifact infrastructure operations")
        logger.info("=" * 60)
        
        if not self.check_dependencies():
            return False
        
        import torch
        from transformers import (
            AutoModelForCausalLM, AutoTokenizer,
            TrainingArguments, Trainer, DataCollatorForLanguageModeling,
            BitsAndBytesConfig
        )
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from datasets import load_dataset
        
        self.state.status = "training"
        self.state.started_at = datetime.now().isoformat()
        start_time = time.time()
        
        # 4-bit quantization
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )
        
        logger.info(f"Loading {self.model_name}...")
        
        tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.float16,
        )
        
        model = prepare_model_for_kbit_training(model)
        model.gradient_checkpointing_enable()
        
        # LoRA
        lora_config = LoraConfig(
            r=64,
            lora_alpha=128,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                          "gate_proj", "up_proj", "down_proj"],
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM",
        )
        
        model = get_peft_model(model, lora_config)
        
        trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
        total = sum(p.numel() for p in model.parameters())
        logger.info(f"Trainable: {trainable:,} / Total: {total:,}")
        
        # Prepare dataset
        dataset_path = DATA_DIR / "qwen_operational.jsonl"
        if not dataset_path.exists():
            self.generate_training_data(dataset_path)
        
        dataset = load_dataset("json", data_files=str(dataset_path), split="train")
        
        def tokenize(examples):
            return tokenizer(
                examples["text"],
                truncation=True,
                max_length=2048,
                padding="max_length",
            )
        
        tokenized = dataset.map(tokenize, batched=True, remove_columns=dataset.column_names)
        
        training_args = TrainingArguments(
            output_dir=str(CHECKPOINTS_DIR),
            num_train_epochs=3,
            per_device_train_batch_size=4,
            gradient_accumulation_steps=8,
            learning_rate=2e-5,
            warmup_steps=100,
            logging_steps=10,
            save_steps=500,
            save_total_limit=3,
            fp16=True,
            optim="adamw_torch",
            lr_scheduler_type="cosine",
            report_to="none",
            remove_unused_columns=False,
        )
        
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized,
            data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
        )
        
        logger.info("Starting training...")
        result = trainer.train()
        
        # Save
        save_path = MODELS_DIR / "artifact-qwen-operational"
        trainer.save_model(str(save_path))
        tokenizer.save_pretrained(str(save_path))
        
        self.state.status = "ready"
        self.state.loss = result.training_loss
        self.state.step = result.global_step
        self.state.model_path = str(save_path)
        self.state.training_hours = (time.time() - start_time) / 3600
        self._save_state()
        
        logger.info("=" * 60)
        logger.info("TRAINING COMPLETE")
        logger.info(f"Model saved: {save_path}")
        logger.info(f"Loss: {result.training_loss:.4f}")
        logger.info(f"Time: {self.state.training_hours:.2f} hours")
        logger.info("=" * 60)
        
        return True
    
    def status(self):
        """Show current status"""
        print("\n" + "=" * 50)
        print("ARTIFACT QWEN OPERATIONAL STATUS")
        print("=" * 50)
        print(f"Status:      {self.state.status}")
        print(f"Step:        {self.state.step}")
        print(f"Loss:        {self.state.loss:.4f}")
        print(f"Path:        {self.state.model_path or 'Not trained'}")
        print(f"Hours:       {self.state.training_hours:.2f}")
        print("=" * 50 + "\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Artifact Qwen Operational Trainer")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--train", action="store_true", help="Start training")
    args = parser.parse_args()
    
    trainer = QwenOperationalTrainer()
    
    if args.status:
        trainer.status()
    elif args.train:
        trainer.train()
    else:
        trainer.train()


if __name__ == "__main__":
    main()
