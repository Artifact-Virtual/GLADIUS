#!/usr/bin/env python3
"""
GLADIUS 1B Multi-Expert Training Pipeline
==========================================

Builds GLADIUS from scratch using knowledge distillation from multiple expert models.
Each expert brings unique strengths to create a superior hybrid model.

Expert Teachers:
- Qwen2.5-1.5B:    Best tool-calling, multilingual, structured output
- Llama-3.2-1B:    Strong reasoning, English fluency
- Phi-3-mini:      Mathematical reasoning, code generation
- Gemma-2-2b:      Safety, instruction following

Strategy:
1. Initialize custom architecture with our own random weights
2. Distill knowledge from each expert into specific capabilities
3. Use ensemble distillation for general knowledge
4. Progressive training with capability merging
5. Export to GGUF for deployment

Target: 1 billion parameters with custom weights (NOT fine-tuning)

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
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
import traceback

# === PATH CONFIGURATION (Universal - relocatable) ===
SCRIPT_DIR = Path(__file__).parent.resolve()
GLADIUS_DIR = SCRIPT_DIR.parent.resolve()
PROJECT_ROOT = GLADIUS_DIR.parent.resolve()

# ALL files stay within GLADIUS directory - fully contained
# tmp/ directory for large cache/checkpoint files
TMP_BASE = GLADIUS_DIR / "tmp"
MODELS_DIR = GLADIUS_DIR / "models"
PRIMARY_DIR = MODELS_DIR / "gladius_primary"
CHECKPOINTS_DIR = TMP_BASE / "checkpoints"
EXPERTS_DIR = TMP_BASE / "experts_cache"
DATA_DIR = SCRIPT_DIR / "data"
LOGS_DIR = TMP_BASE / "logs"
CACHE_DIR = TMP_BASE / "cache"
TMP_DIR = TMP_BASE / "downloads"

# Ensure directories exist
for d in [MODELS_DIR, PRIMARY_DIR, CHECKPOINTS_DIR, EXPERTS_DIR, DATA_DIR, LOGS_DIR, CACHE_DIR, TMP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Set environment for HuggingFace to use our cache
os.environ['HF_HOME'] = str(CACHE_DIR)
os.environ['TRANSFORMERS_CACHE'] = str(CACHE_DIR)
os.environ['TMPDIR'] = str(TMP_DIR)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s │ %(levelname)-8s │ %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / f"moe_training_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GLADIUS.MoE_Trainer")


@dataclass
class ExpertModel:
    """Configuration for an expert teacher model"""
    name: str
    hf_id: str
    strengths: List[str]
    weight: float = 1.0  # Contribution weight in ensemble
    loaded: bool = False


# Expert teacher definitions - Diverse models for maximum edge
# Each expert brings unique architectural patterns and capabilities
EXPERT_TEACHERS = [
    ExpertModel(
        name="qwen",
        hf_id="Qwen/Qwen2.5-1.5B-Instruct",
        strengths=["tool_calling", "structured_output", "multilingual", "json_generation"],
        weight=1.5  # Primary for tool-calling - best in class
    ),
    ExpertModel(
        name="llama",
        hf_id="meta-llama/Llama-3.2-1B-Instruct",
        strengths=["reasoning", "fluency", "english_excellence", "conversation"],
        weight=1.3  # Strong reasoning backbone
    ),
    ExpertModel(
        name="phi",
        hf_id="microsoft/phi-2",
        strengths=["mathematics", "code_generation", "logic", "step_by_step", "compression"],
        weight=1.2  # Exceptional reasoning density
    ),
    ExpertModel(
        name="tinyllama",
        hf_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        strengths=["fast_inference", "safety", "instruction_following", "general_knowledge"],
        weight=1.0  # Fallback for Gemma (gated model)
    ),
]


@dataclass
class GladiusArchitecture:
    """Custom GLADIUS model architecture configuration"""
    # CPU-optimized: ~350M parameters (fits in 16GB RAM with expert models)
    hidden_size: int = 1024
    intermediate_size: int = 2816  # ~2.75x hidden
    num_hidden_layers: int = 16
    num_attention_heads: int = 16
    num_key_value_heads: int = 4  # GQA for efficiency
    vocab_size: int = 151665  # Match Qwen tokenizer
    max_position_embeddings: int = 2048  # Reduced for memory
    rope_theta: float = 10000.0
    rms_norm_eps: float = 1e-6
    initializer_range: float = 0.02
    use_cache: bool = False  # Disabled during training
    tie_word_embeddings: bool = False
    
    @property
    def total_params(self) -> int:
        """Estimate total parameters"""
        # Embedding
        embed = self.vocab_size * self.hidden_size
        
        # Per layer
        # QKV projections
        qkv = self.hidden_size * (self.hidden_size + 2 * (self.hidden_size // self.num_attention_heads * self.num_key_value_heads))
        # Output projection
        o_proj = self.hidden_size * self.hidden_size
        # MLP
        mlp = 3 * self.hidden_size * self.intermediate_size
        # Norms
        norms = 2 * self.hidden_size
        
        per_layer = qkv + o_proj + mlp + norms
        total_layers = per_layer * self.num_hidden_layers
        
        # LM head
        lm_head = self.vocab_size * self.hidden_size if not self.tie_word_embeddings else 0
        
        # Final norm
        final_norm = self.hidden_size
        
        return embed + total_layers + lm_head + final_norm


@dataclass
class TrainingState:
    """Persistent training state for recovery"""
    phase: int = 0
    epoch: int = 0
    step: int = 0
    current_params: int = 0
    target_params: int = 1_000_000_000
    experts_distilled: List[str] = field(default_factory=list)
    learning_rate: float = 1e-4
    total_training_hours: float = 0.0
    loss_history: List[float] = field(default_factory=list)
    capability_scores: Dict[str, float] = field(default_factory=dict)
    status: str = "initialized"
    started_at: str = ""
    last_checkpoint: str = ""
    hardware: str = "unknown"
    
    def save(self, path: Path):
        with open(path, 'w') as f:
            json.dump(asdict(self), f, indent=2)
    
    @classmethod
    def load(cls, path: Path) -> 'TrainingState':
        if path.exists():
            with open(path) as f:
                return cls(**json.load(f))
        return cls()


class MultiExpertDistiller:
    """Distills knowledge from multiple expert models into GLADIUS"""
    
    def __init__(self, architecture: GladiusArchitecture = None):
        self.architecture = architecture or GladiusArchitecture()
        self.state_path = CHECKPOINTS_DIR / "moe_training_state.json"
        self.state = TrainingState.load(self.state_path)
        self.running = True
        self.experts: Dict[str, Any] = {}
        self.tokenizer = None
        self.student_model = None
        self.cpu_mode = False
        self.expert_catalog = [ExpertModel(**asdict(exp)) for exp in EXPERT_TEACHERS]
        
        # Detect hardware
        self._detect_hardware()
        
        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info(f"GLADIUS MoE Trainer initialized")
        logger.info(f"Target parameters: {self.architecture.total_params:,}")
        logger.info(f"Hardware: {self.state.hardware}")
    
    def _detect_hardware(self):
        """Detect available hardware"""
        try:
            import torch
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1e9
                self.state.hardware = f"CUDA ({gpu_name}, {gpu_mem:.1f}GB)"
                self.device = "cuda"
                self.cpu_mode = False
            else:
                self.state.hardware = "CPU"
                self.device = "cpu"
                self.cpu_mode = True
                self._apply_cpu_optimizations()
        except:
            self.state.hardware = "CPU (torch not loaded)"
            self.device = "cpu"
            self.cpu_mode = True
            self._apply_cpu_optimizations()

    def _apply_cpu_optimizations(self):
        """Adjust architecture and settings for CPU-only environments."""
        logger.warning("GPU not detected. Enabling CPU-optimized configuration for GLADIUS training.")
        # Reduce architecture footprint for CPU training
        self.architecture = GladiusArchitecture(
            hidden_size=768,
            intermediate_size=2048,
            num_hidden_layers=12,
            num_attention_heads=12,
            num_key_value_heads=4,
            vocab_size=min(self.architecture.vocab_size, 120_000),
            max_position_embeddings=1024,
            rope_theta=self.architecture.rope_theta,
            rms_norm_eps=self.architecture.rms_norm_eps,
            initializer_range=self.architecture.initializer_range,
            use_cache=self.architecture.use_cache,
            tie_word_embeddings=self.architecture.tie_word_embeddings,
        )
        # Limit expert distillation set to top performers to reduce memory pressure
        if len(self.expert_catalog) > 2:
            self.expert_catalog = self.expert_catalog[:2]
            logger.warning("Limiting expert distillation to top 2 experts for CPU mode.")
        self.state.hardware = (self.state.hardware or "CPU") + " [optimized CPU mode]"
    
    def _signal_handler(self, signum, frame):
        logger.info("Shutdown signal received, saving state...")
        self.running = False
        self._save_checkpoint("interrupt")
    
    def _save_checkpoint(self, reason: str = "scheduled"):
        self.state.last_checkpoint = datetime.now().isoformat()
        self.state.save(self.state_path)
        logger.info(f"Checkpoint saved ({reason}): step {self.state.step}")
    
    def has_checkpoint(self) -> bool:
        """Return True if a saved state exists."""
        return self.state_path.exists()
    
    def load_checkpoint(self) -> None:
        """Reload training state from disk."""
        if not self.state_path.exists():
            raise FileNotFoundError(f"No checkpoint found at {self.state_path}")
        self.state = TrainingState.load(self.state_path)
        logger.info(
            "Checkpoint loaded: phase=%s step=%s epochs=%s experts=%s",
            self.state.phase,
            self.state.step,
            self.state.epoch,
            ", ".join(self.state.experts_distilled) or "none",
        )
    
    def check_dependencies(self) -> bool:
        """Ensure all required packages are installed"""
        required = ["torch", "transformers", "datasets", "accelerate"]
        missing = []
        
        for pkg in required:
            try:
                __import__(pkg)
            except ImportError:
                missing.append(pkg)
        
        if missing:
            logger.info(f"Installing missing packages: {missing}")
            try:
                if "torch" in missing:
                    if self.device == "cuda":
                        torch_cmd = [
                            sys.executable, "-m", "pip", "install", "-q",
                            "torch==2.2.1", "torchvision==0.17.1", "torchaudio==2.2.1",
                            "--index-url", "https://download.pytorch.org/whl/cu121"
                        ]
                    else:
                        torch_cmd = [
                            sys.executable, "-m", "pip", "install", "-q",
                            "--extra-index-url", "https://download.pytorch.org/whl/cpu",
                            "torch==2.2.1+cpu", "torchvision==0.17.1+cpu", "torchaudio==2.2.1+cpu"
                        ]
                    logger.info("Installing PyTorch stack optimized for %s", self.device.upper())
                    subprocess.run(torch_cmd, check=True)
                    missing = [pkg for pkg in missing if pkg != "torch"]
                if missing:
                    remapped = []
                    for pkg in missing:
                        if pkg == "transformers":
                            remapped.append("transformers>=4.40.0")
                        elif pkg == "datasets":
                            remapped.append("datasets>=2.18.0")
                        elif pkg == "accelerate":
                            remapped.append("accelerate>=0.28.0")
                        else:
                            remapped.append(pkg)
                    subprocess.run([
                        sys.executable, "-m", "pip", "install", "-q",
                        *remapped,
                        "sentencepiece", "protobuf"
                    ], check=True)
                return True
            except Exception as e:
                logger.error(f"Failed to install: {e}")
                return False
        return True
    
    def load_expert(self, expert: ExpertModel) -> Optional[Tuple[Any, Any]]:
        """Load an expert teacher model"""
        logger.info(f"Loading expert: {expert.name} ({expert.hf_id})")
        
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            # Set cache directory
            os.environ['HF_HOME'] = str(CACHE_DIR)
            os.environ['TRANSFORMERS_CACHE'] = str(CACHE_DIR)
            
            # Check for local models first (tmp/models/)
            local_models_dir = TMP_BASE / "models"
            hf_name = expert.hf_id.split("/")[-1]
            local_paths = [
                local_models_dir / hf_name,
                local_models_dir / hf_name.replace("-Instruct", ""),
                local_models_dir / f"{hf_name.replace('-Instruct', '')}-meta",
                local_models_dir / expert.name,
            ]
            
            model_path = expert.hf_id  # Default to HF ID
            
            for local_path in local_paths:
                if local_path.exists():
                    # Check for model files
                    has_safetensors = list(local_path.glob("*.safetensors"))
                    has_bin = list(local_path.glob("*.bin"))
                    has_pth = list(local_path.glob("*.pth"))
                    
                    if has_safetensors or has_bin:
                        model_path = str(local_path)
                        logger.info(f"Using local model: {local_path}")
                        break
                    elif has_pth:
                        # Meta format - need to convert or use HF
                        logger.info(f"Found Meta format at {local_path}, using HF for compatibility")
                        continue
            
            tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=True,
                cache_dir=CACHE_DIR
            )
            
            if self.device == "cuda":
                model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    trust_remote_code=True,
                    cache_dir=CACHE_DIR
                )
            else:
                model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True,
                    trust_remote_code=True,
                    cache_dir=CACHE_DIR
                )
            
            model.eval()
            expert.loaded = True
            logger.info(f"Loaded {expert.name}: {sum(p.numel() for p in model.parameters()):,} params")
            return model, tokenizer
            
        except Exception as e:
            logger.error(f"Failed to load {expert.name}: {e}")
            return None
    
    def create_student_model(self) -> Any:
        """Create the GLADIUS student model from scratch"""
        logger.info("Creating GLADIUS student model from scratch...")
        
        from transformers import LlamaConfig, LlamaForCausalLM
        import torch
        
        # Use Llama architecture as base (most compatible)
        config = LlamaConfig(
            hidden_size=self.architecture.hidden_size,
            intermediate_size=self.architecture.intermediate_size,
            num_hidden_layers=self.architecture.num_hidden_layers,
            num_attention_heads=self.architecture.num_attention_heads,
            num_key_value_heads=self.architecture.num_key_value_heads,
            vocab_size=self.architecture.vocab_size,
            max_position_embeddings=self.architecture.max_position_embeddings,
            rope_theta=self.architecture.rope_theta,
            rms_norm_eps=self.architecture.rms_norm_eps,
            initializer_range=self.architecture.initializer_range,
            use_cache=self.architecture.use_cache,
            tie_word_embeddings=self.architecture.tie_word_embeddings,
        )
        
        # Create model with random initialization
        model = LlamaForCausalLM(config)
        
        # Custom weight initialization for better training
        def init_weights(module):
            if isinstance(module, torch.nn.Linear):
                torch.nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    torch.nn.init.zeros_(module.bias)
            elif isinstance(module, torch.nn.Embedding):
                torch.nn.init.normal_(module.weight, mean=0.0, std=config.initializer_range)
        
        model.apply(init_weights)
        
        param_count = sum(p.numel() for p in model.parameters())
        self.state.current_params = param_count
        
        logger.info(f"Created GLADIUS: {param_count:,} parameters")
        logger.info(f"Architecture: {self.architecture.num_hidden_layers}L, {self.architecture.hidden_size}H, {self.architecture.num_attention_heads}A")
        
        return model
    
    def generate_capability_data(self, capability: str, count: int = 500) -> List[Dict]:
        """Generate training data for a specific capability"""
        import random
        
        data_generators = {
            "tool_calling": self._gen_tool_calling_data,
            "structured_output": self._gen_structured_data,
            "reasoning": self._gen_reasoning_data,
            "code_generation": self._gen_code_data,
            "instruction_following": self._gen_instruction_data,
            "conversation": self._gen_conversation_data,
        }
        
        generator = data_generators.get(capability, self._gen_general_data)
        return generator(count)
    
    def _gen_tool_calling_data(self, count: int) -> List[Dict]:
        """Generate tool-calling training samples"""
        import random
        
        tools = {
            "read_db": {"args": ["name", "query"], "examples": [
                ("Query the syndicate database", {"name": "syndicate", "query": "SELECT * FROM predictions"}),
                ("Get gold analysis from hektor", {"name": "hektor", "query": "SELECT * FROM analysis WHERE asset='XAUUSD'"}),
            ]},
            "write_db": {"args": ["name", "table", "data"], "examples": [
                ("Save this prediction", {"name": "syndicate", "table": "predictions", "data": {"bias": "BULLISH"}}),
            ]},
            "search": {"args": ["query", "k"], "examples": [
                ("Find gold analysis", {"query": "gold price trends", "k": 5}),
                ("Search for market patterns", {"query": "bullish momentum", "k": 10}),
            ]},
            "remember": {"args": ["key", "value"], "examples": [
                ("Remember gold is bullish", {"key": "gold_bias", "value": "Bullish targeting 2750"}),
            ]},
            "recall": {"args": ["query", "k"], "examples": [
                ("What do you know about gold?", {"query": "gold", "k": 5}),
            ]},
            "run_syndicate": {"args": ["symbol", "mode"], "examples": [
                ("Analyze gold", {"symbol": "XAUUSD", "mode": "full"}),
                ("Quick BTC analysis", {"symbol": "BTCUSD", "mode": "quick"}),
            ]},
            "send_discord": {"args": ["message", "channel"], "examples": [
                ("Send alert to Discord", {"message": "Gold breakout!", "channel": "alerts"}),
            ]},
            "send_email": {"args": ["to", "subject", "body"], "examples": [
                ("Email the report", {"to": "team@artifactvirtual.com", "subject": "Report", "body": "..."}),
            ]},
        }
        
        samples = []
        system = "You are GLADIUS. Respond with JSON: {\"tool\": \"name\", \"args\": {...}}"
        
        for _ in range(count):
            tool_name = random.choice(list(tools.keys()))
            tool = tools[tool_name]
            if tool["examples"]:
                query, args = random.choice(tool["examples"])
                prefix = random.choice(["", "Please ", "Can you ", "I need you to "])
                samples.append({
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": f"{prefix}{query}"},
                        {"role": "assistant", "content": json.dumps({"tool": tool_name, "args": args})}
                    ]
                })
        
        return samples
    
    def _gen_structured_data(self, count: int) -> List[Dict]:
        """Generate structured output samples"""
        samples = []
        system = "You are GLADIUS. Always respond in valid JSON format."
        
        examples = [
            ("Analyze this market: Gold at 2700, RSI 72, volume up", 
             {"analysis": {"asset": "XAUUSD", "price": 2700, "rsi": 72, "volume_trend": "increasing", "bias": "bullish"}}),
            ("Summarize: S&P up 1.2%, Nasdaq flat, bonds selling off",
             {"summary": {"sp500": "+1.2%", "nasdaq": "0%", "bonds": "selling", "overall": "risk-on"}}),
        ]
        
        for _ in range(count):
            query, response = examples[_ % len(examples)]
            samples.append({
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": query},
                    {"role": "assistant", "content": json.dumps(response)}
                ]
            })
        
        return samples
    
    def _gen_reasoning_data(self, count: int) -> List[Dict]:
        """Generate reasoning samples"""
        samples = []
        system = "You are GLADIUS. Think step by step before answering."
        
        examples = [
            ("Should we go long on gold here?",
             "Let me analyze:\n1. Price: At 2700, near resistance\n2. RSI: 72 shows overbought\n3. Volume: Increasing on breakout attempts (bullish)\n4. Fundamentals: Fed dovish (bullish)\n\nConclusion: Bullish bias but wait for pullback to 2680 support for better entry."),
        ]
        
        for _ in range(count):
            query, response = examples[_ % len(examples)]
            samples.append({
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": query},
                    {"role": "assistant", "content": response}
                ]
            })
        
        return samples
    
    def _gen_code_data(self, count: int) -> List[Dict]:
        """Generate code samples"""
        samples = []
        system = "You are GLADIUS. Write clean, efficient code."
        
        examples = [
            ("Write a function to calculate RSI",
             "```python\ndef calculate_rsi(prices, period=14):\n    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]\n    gains = [d if d > 0 else 0 for d in deltas]\n    losses = [-d if d < 0 else 0 for d in deltas]\n    \n    avg_gain = sum(gains[:period]) / period\n    avg_loss = sum(losses[:period]) / period\n    \n    if avg_loss == 0:\n        return 100\n    \n    rs = avg_gain / avg_loss\n    rsi = 100 - (100 / (1 + rs))\n    return rsi\n```"),
        ]
        
        for _ in range(count):
            query, response = examples[_ % len(examples)]
            samples.append({
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": query},
                    {"role": "assistant", "content": response}
                ]
            })
        
        return samples
    
    def _gen_instruction_data(self, count: int) -> List[Dict]:
        samples = []
        system = "You are GLADIUS. Follow instructions precisely."
        
        examples = [
            ("List 3 support levels for gold at 2700",
             "Support levels for XAUUSD at 2700:\n1. 2680 - Recent swing low\n2. 2650 - 20-day MA\n3. 2620 - Previous resistance turned support"),
        ]
        
        for _ in range(count):
            query, response = examples[_ % len(examples)]
            samples.append({
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": query},
                    {"role": "assistant", "content": response}
                ]
            })
        
        return samples
    
    def _gen_conversation_data(self, count: int) -> List[Dict]:
        return self._gen_general_data(count)
    
    def _gen_general_data(self, count: int) -> List[Dict]:
        samples = []
        system = "You are GLADIUS, the native AI for Artifact Virtual Enterprise."
        
        examples = [
            ("What are you?", "I am GLADIUS, the native AI for Artifact Virtual Enterprise. I specialize in market analysis, tool execution, and autonomous operations."),
            ("What can you do?", "I can analyze markets, execute tools, manage databases, send communications, and operate autonomously across the Artifact infrastructure."),
        ]
        
        for _ in range(count):
            query, response = examples[_ % len(examples)]
            samples.append({
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": query},
                    {"role": "assistant", "content": response}
                ]
            })
        
        return samples
    
    def distill_from_expert(self, expert: ExpertModel, student_model: Any, tokenizer: Any) -> float:
        """Distill knowledge from one expert into student"""
        import torch
        from torch.utils.data import DataLoader, Dataset
        
        logger.info(f"Distilling from {expert.name}...")
        
        # Load expert
        result = self.load_expert(expert)
        if not result:
            return 0.0
        
        teacher_model, teacher_tokenizer = result
        
        # Generate capability-specific data
        all_data = []
        for capability in expert.strengths:
            data = self.generate_capability_data(capability, 200)
            all_data.extend(data)
        
        logger.info(f"Generated {len(all_data)} samples for {expert.name}")
        
        # Prepare for distillation
        class DistillDataset(Dataset):
            def __init__(self, data, tokenizer, max_length=512):
                self.data = data
                self.tokenizer = tokenizer
                self.max_length = max_length
            
            def __len__(self):
                return len(self.data)
            
            def __getitem__(self, idx):
                item = self.data[idx]
                # Format as chat
                text = ""
                for msg in item.get("messages", []):
                    role = msg["role"]
                    content = msg["content"]
                    text += f"<|{role}|>\n{content}\n"
                
                tokens = self.tokenizer(
                    text,
                    truncation=True,
                    max_length=self.max_length,
                    padding="max_length",
                    return_tensors="pt"
                )
                return {
                    "input_ids": tokens["input_ids"].squeeze(),
                    "attention_mask": tokens["attention_mask"].squeeze()
                }
        
        dataset = DistillDataset(all_data, tokenizer)
        dataloader = DataLoader(dataset, batch_size=1, shuffle=True)
        
        # Distillation training
        student_model.train()
        optimizer = torch.optim.AdamW(student_model.parameters(), lr=1e-4, weight_decay=0.01)
        
        total_loss = 0.0
        steps = 0
        
        for batch in dataloader:
            if not self.running:
                break
            
            input_ids = batch["input_ids"].to(self.device)
            attention_mask = batch["attention_mask"].to(self.device)
            
            # Get teacher logits (no grad)
            with torch.no_grad():
                teacher_outputs = teacher_model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )
                teacher_logits = teacher_outputs.logits
            
            # Get student logits
            student_outputs = student_model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=input_ids
            )
            student_logits = student_outputs.logits
            
            # Handle vocab size mismatch - truncate to smaller vocab
            min_vocab = min(student_logits.size(-1), teacher_logits.size(-1))
            student_logits = student_logits[..., :min_vocab]
            teacher_logits = teacher_logits[..., :min_vocab]
            
            # KL divergence loss (distillation)
            temperature = 2.0
            kl_loss = torch.nn.functional.kl_div(
                torch.nn.functional.log_softmax(student_logits / temperature, dim=-1),
                torch.nn.functional.softmax(teacher_logits / temperature, dim=-1),
                reduction="batchmean"
            ) * (temperature ** 2)
            
            # Combined loss: distillation + cross-entropy
            ce_loss = student_outputs.loss
            loss = 0.5 * kl_loss + 0.5 * ce_loss
            
            # Backward
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(student_model.parameters(), 1.0)
            optimizer.step()
            
            total_loss += loss.item()
            steps += 1
            
            if steps % 50 == 0:
                avg = total_loss / steps
                logger.info(f"  Step {steps}: Loss = {loss.item():.4f} (avg: {avg:.4f})")
                # Update state for dashboard
                self.state.step = steps
                self.state.current_expert = expert.name
                self.state.loss_history.append(loss.item())
                self._save_checkpoint("step")
        
        # Cleanup teacher - IMPORTANT for memory
        del teacher_model
        del teacher_tokenizer
        import gc
        gc.collect()
        if self.device == "cuda":
            torch.cuda.empty_cache()
        
        logger.info(f"Unloaded {expert.name} to free memory")
        
        avg_loss = total_loss / max(steps, 1)
        logger.info(f"Distillation from {expert.name} complete. Avg loss: {avg_loss:.4f}")
        
        return avg_loss
    
    def train_full_pipeline(self, max_hours: float = 72.0):
        """Run the full multi-expert training pipeline"""
        logger.info("=" * 70)
        logger.info("        GLADIUS 1B MULTI-EXPERT TRAINING PIPELINE")
        logger.info("=" * 70)
        logger.info(f"Architecture: {self.architecture.num_hidden_layers}L, {self.architecture.hidden_size}H")
        logger.info(f"Target parameters: {self.architecture.total_params:,}")
        logger.info(f"Experts: {[e.name for e in self.expert_catalog]}")
        logger.info(f"Hardware: {self.state.hardware}")
        logger.info(f"Max hours: {max_hours}")
        logger.info("=" * 70)
        
        # Check dependencies
        if not self.check_dependencies():
            logger.error("Dependency check failed")
            return
        
        import torch
        
        self.state.started_at = datetime.now().isoformat()
        self.state.status = "training"
        start_time = time.time()
        
        try:
            # Phase 0: Create student model
            logger.info("\n" + "=" * 50)
            logger.info("PHASE 0: Creating GLADIUS Student Model")
            logger.info("=" * 50)
            
            self.student_model = self.create_student_model()
            self.student_model.to(self.device)
            
            # Load tokenizer (use Qwen's - open and excellent for tool-calling)
            from transformers import AutoTokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                "Qwen/Qwen2.5-1.5B-Instruct",
                cache_dir=CACHE_DIR,
                trust_remote_code=True
            )
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self._save_checkpoint("model_created")
            
            # Phase 1-4: Distill from each expert
            for i, expert in enumerate(self.expert_catalog):
                if not self.running:
                    break
                
                # Check time limit
                elapsed_hours = (time.time() - start_time) / 3600
                if elapsed_hours >= max_hours:
                    logger.info(f"Time limit reached ({max_hours}h)")
                    break
                
                logger.info(f"\n" + "=" * 50)
                logger.info(f"PHASE {i+1}: Distilling from {expert.name.upper()}")
                logger.info(f"Strengths: {expert.strengths}")
                logger.info("=" * 50)
                
                self.state.phase = i + 1
                
                loss = self.distill_from_expert(expert, self.student_model, self.tokenizer)
                
                self.state.experts_distilled.append(expert.name)
                self.state.capability_scores[expert.name] = 1.0 - min(loss, 1.0)
                self.state.loss_history.append(loss)
                
                self._save_checkpoint(f"expert_{expert.name}_complete")
            
            # Phase 5: Final training pass
            if self.running:
                logger.info(f"\n" + "=" * 50)
                logger.info("PHASE 5: Final Unified Training")
                logger.info("=" * 50)
                
                # Combine all capabilities
                all_data = []
                for cap in ["tool_calling", "reasoning", "code_generation", "instruction_following"]:
                    all_data.extend(self.generate_capability_data(cap, 300))
                
                # Quick fine-tuning pass
                from torch.utils.data import DataLoader, Dataset
                
                class FinalDataset(Dataset):
                    def __init__(self, data, tokenizer):
                        self.data = data
                        self.tokenizer = tokenizer
                    
                    def __len__(self):
                        return len(self.data)
                    
                    def __getitem__(self, idx):
                        item = self.data[idx]
                        text = ""
                        for msg in item.get("messages", []):
                            text += f"<|{msg['role']}|>\n{msg['content']}\n"
                        
                        tokens = self.tokenizer(text, truncation=True, max_length=512, 
                                               padding="max_length", return_tensors="pt")
                        return {
                            "input_ids": tokens["input_ids"].squeeze(),
                            "attention_mask": tokens["attention_mask"].squeeze()
                        }
                
                dataset = FinalDataset(all_data, self.tokenizer)
                dataloader = DataLoader(dataset, batch_size=1, shuffle=True)
                
                self.student_model.train()
                optimizer = torch.optim.AdamW(self.student_model.parameters(), lr=5e-5)
                
                for batch in dataloader:
                    if not self.running:
                        break
                    
                    input_ids = batch["input_ids"].to(self.device)
                    attention_mask = batch["attention_mask"].to(self.device)
                    
                    outputs = self.student_model(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        labels=input_ids
                    )
                    
                    loss = outputs.loss
                    optimizer.zero_grad()
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(self.student_model.parameters(), 1.0)
                    optimizer.step()
                    
                    self.state.step += 1
            
            # Save final model
            logger.info(f"\n" + "=" * 50)
            logger.info("PHASE 6: Saving GLADIUS Model")
            logger.info("=" * 50)
            
            save_path = PRIMARY_DIR / "gladius-1b-v1"
            save_path.mkdir(parents=True, exist_ok=True)
            
            self.student_model.save_pretrained(str(save_path))
            self.tokenizer.save_pretrained(str(save_path))
            
            # Save config
            config_info = {
                "name": "gladius-1b",
                "version": "1.0.0",
                "parameters": self.state.current_params,
                "architecture": asdict(self.architecture),
                "experts_used": self.state.experts_distilled,
                "capability_scores": self.state.capability_scores,
                "training_hours": (time.time() - start_time) / 3600,
                "created": datetime.now().isoformat()
            }
            
            with open(save_path / "gladius_config.json", 'w') as f:
                json.dump(config_info, f, indent=2)
            
            logger.info(f"Model saved to: {save_path}")
            
            # Final state update
            self.state.total_training_hours = (time.time() - start_time) / 3600
            self.state.status = "completed"
            self._save_checkpoint("training_complete")
            
            # Summary
            logger.info("\n" + "=" * 70)
            logger.info("        GLADIUS 1B TRAINING COMPLETE")
            logger.info("=" * 70)
            logger.info(f"Total parameters: {self.state.current_params:,}")
            logger.info(f"Training time: {self.state.total_training_hours:.2f} hours")
            logger.info(f"Experts distilled: {self.state.experts_distilled}")
            logger.info(f"Model location: {save_path}")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"Training error: {e}")
            logger.error(traceback.format_exc())
            self.state.status = "failed"
            self._save_checkpoint("error")
            raise


def print_banner():
    banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║          G L A D I U S   M U L T I - E X P E R T   T R A I N E R    ║
║                                                                      ║
║     Knowledge Distillation from Qwen + Llama + Phi + Gemma           ║
║     Building Native 1B Parameter Model with Custom Weights           ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="GLADIUS Multi-Expert Trainer")
    parser.add_argument("--hours", type=float, default=72, help="Max training hours")
    parser.add_argument("--status", action="store_true", help="Show training status")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.status:
        state = TrainingState.load(CHECKPOINTS_DIR / "moe_training_state.json")
        print(f"\nTraining Status:")
        print(f"  Phase: {state.phase}/6")
        print(f"  Step: {state.step}")
        print(f"  Parameters: {state.current_params:,}")
        print(f"  Status: {state.status}")
        print(f"  Experts distilled: {state.experts_distilled}")
        print(f"  Hours: {state.total_training_hours:.2f}")
        print(f"  Last checkpoint: {state.last_checkpoint}")
        return
    
    trainer = MultiExpertDistiller()
    trainer.train_full_pipeline(max_hours=args.hours)


if __name__ == "__main__":
    main()
