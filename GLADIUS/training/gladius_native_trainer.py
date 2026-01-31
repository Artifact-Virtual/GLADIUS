#!/usr/bin/env python3
"""
GLADIUS Native Model Trainer
============================

Trains a native GLADIUS model from scratch - NO third-party model dependencies.
Optimized for CPU training with limited RAM.

Architecture: Custom transformer (Llama-style)
Target: ~150M parameters (CPU-trainable, expandable later)
Output: Native GGUF file

Usage:
    python gladius_native_trainer.py [--epochs N] [--export-gguf]
"""

import os
import sys
import json
import math
import time
import logging
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

# Setup paths
SCRIPT_DIR = Path(__file__).parent.resolve()
GLADIUS_DIR = SCRIPT_DIR.parent.resolve()
MODELS_DIR = GLADIUS_DIR / "models"
DATA_DIR = SCRIPT_DIR / "data"
OUTPUT_DIR = MODELS_DIR / "native"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(GLADIUS_DIR / "tmp" / "native_training.log")
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# NATIVE GLADIUS ARCHITECTURE
# =============================================================================

@dataclass
class GladiusConfig:
    """Native GLADIUS model configuration - CPU optimized"""
    vocab_size: int = 32000  # Standard vocab size
    hidden_size: int = 512   # Reduced for CPU
    intermediate_size: int = 1408  # ~2.75x hidden
    num_hidden_layers: int = 12
    num_attention_heads: int = 8
    num_key_value_heads: int = 4  # GQA
    max_position_embeddings: int = 2048
    rope_theta: float = 10000.0
    rms_norm_eps: float = 1e-6
    
    @property
    def head_dim(self) -> int:
        return self.hidden_size // self.num_attention_heads
    
    @property
    def total_params(self) -> int:
        embed = self.vocab_size * self.hidden_size * 2  # embed + lm_head
        per_layer = (
            4 * self.hidden_size * self.hidden_size +  # attention
            3 * self.hidden_size * self.intermediate_size +  # MLP
            2 * self.hidden_size  # norms
        )
        return embed + per_layer * self.num_hidden_layers
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def for_size(cls, target_params_m: int = 150):
        """Create config targeting specific parameter count"""
        if target_params_m <= 50:
            return cls(hidden_size=256, num_hidden_layers=6, num_attention_heads=4, num_key_value_heads=2)
        elif target_params_m <= 150:
            return cls(hidden_size=512, num_hidden_layers=12, num_attention_heads=8, num_key_value_heads=4)
        elif target_params_m <= 500:
            return cls(hidden_size=1024, num_hidden_layers=16, num_attention_heads=16, num_key_value_heads=4)
        else:
            return cls(hidden_size=2048, num_hidden_layers=24, num_attention_heads=32, num_key_value_heads=8)


class RMSNorm(nn.Module):
    """Root Mean Square Layer Normalization"""
    def __init__(self, hidden_size: int, eps: float = 1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(hidden_size))
        self.eps = eps
    
    def forward(self, x):
        variance = x.pow(2).mean(-1, keepdim=True)
        x = x * torch.rsqrt(variance + self.eps)
        return self.weight * x


class RotaryEmbedding(nn.Module):
    """Rotary Position Embedding (RoPE)"""
    def __init__(self, dim: int, max_seq_len: int = 2048, theta: float = 10000.0):
        super().__init__()
        inv_freq = 1.0 / (theta ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv_freq)
        self.max_seq_len = max_seq_len
        self._build_cache(max_seq_len)
    
    def _build_cache(self, seq_len: int):
        t = torch.arange(seq_len, device=self.inv_freq.device)
        freqs = torch.outer(t, self.inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        self.register_buffer("cos_cached", emb.cos())
        self.register_buffer("sin_cached", emb.sin())
    
    def forward(self, x, seq_len: int):
        if seq_len > self.max_seq_len:
            self._build_cache(seq_len)
        return self.cos_cached[:seq_len], self.sin_cached[:seq_len]


def rotate_half(x):
    x1, x2 = x[..., :x.shape[-1]//2], x[..., x.shape[-1]//2:]
    return torch.cat((-x2, x1), dim=-1)


def apply_rotary_pos_emb(q, k, cos, sin):
    q_embed = (q * cos) + (rotate_half(q) * sin)
    k_embed = (k * cos) + (rotate_half(k) * sin)
    return q_embed, k_embed


class GladiusAttention(nn.Module):
    """Multi-head attention with GQA and RoPE"""
    def __init__(self, config: GladiusConfig):
        super().__init__()
        self.num_heads = config.num_attention_heads
        self.num_kv_heads = config.num_key_value_heads
        self.head_dim = config.head_dim
        self.num_kv_groups = self.num_heads // self.num_kv_heads
        
        self.q_proj = nn.Linear(config.hidden_size, self.num_heads * self.head_dim, bias=False)
        self.k_proj = nn.Linear(config.hidden_size, self.num_kv_heads * self.head_dim, bias=False)
        self.v_proj = nn.Linear(config.hidden_size, self.num_kv_heads * self.head_dim, bias=False)
        self.o_proj = nn.Linear(self.num_heads * self.head_dim, config.hidden_size, bias=False)
        
        self.rotary_emb = RotaryEmbedding(self.head_dim, config.max_position_embeddings, config.rope_theta)
    
    def forward(self, x, attention_mask=None):
        B, L, _ = x.shape
        
        q = self.q_proj(x).view(B, L, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(B, L, self.num_kv_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(B, L, self.num_kv_heads, self.head_dim).transpose(1, 2)
        
        # Apply rotary embeddings
        cos, sin = self.rotary_emb(x, L)
        cos = cos.unsqueeze(0).unsqueeze(0)
        sin = sin.unsqueeze(0).unsqueeze(0)
        q, k = apply_rotary_pos_emb(q, k, cos, sin)
        
        # Expand KV for GQA
        if self.num_kv_groups > 1:
            k = k.repeat_interleave(self.num_kv_groups, dim=1)
            v = v.repeat_interleave(self.num_kv_groups, dim=1)
        
        # Attention
        scale = 1.0 / math.sqrt(self.head_dim)
        attn = torch.matmul(q, k.transpose(-2, -1)) * scale
        
        if attention_mask is not None:
            attn = attn + attention_mask
        
        attn = F.softmax(attn, dim=-1)
        out = torch.matmul(attn, v)
        
        out = out.transpose(1, 2).contiguous().view(B, L, -1)
        return self.o_proj(out)


class GladiusMLP(nn.Module):
    """SwiGLU MLP"""
    def __init__(self, config: GladiusConfig):
        super().__init__()
        self.gate_proj = nn.Linear(config.hidden_size, config.intermediate_size, bias=False)
        self.up_proj = nn.Linear(config.hidden_size, config.intermediate_size, bias=False)
        self.down_proj = nn.Linear(config.intermediate_size, config.hidden_size, bias=False)
    
    def forward(self, x):
        return self.down_proj(F.silu(self.gate_proj(x)) * self.up_proj(x))


class GladiusBlock(nn.Module):
    """Transformer block"""
    def __init__(self, config: GladiusConfig):
        super().__init__()
        self.attn = GladiusAttention(config)
        self.mlp = GladiusMLP(config)
        self.input_layernorm = RMSNorm(config.hidden_size, config.rms_norm_eps)
        self.post_attention_layernorm = RMSNorm(config.hidden_size, config.rms_norm_eps)
    
    def forward(self, x, attention_mask=None):
        x = x + self.attn(self.input_layernorm(x), attention_mask)
        x = x + self.mlp(self.post_attention_layernorm(x))
        return x


class GladiusModel(nn.Module):
    """Native GLADIUS Language Model"""
    def __init__(self, config: GladiusConfig):
        super().__init__()
        self.config = config
        
        self.embed_tokens = nn.Embedding(config.vocab_size, config.hidden_size)
        self.layers = nn.ModuleList([GladiusBlock(config) for _ in range(config.num_hidden_layers)])
        self.norm = RMSNorm(config.hidden_size, config.rms_norm_eps)
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
        
        # Initialize weights
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
    
    def forward(self, input_ids, attention_mask=None, labels=None):
        B, L = input_ids.shape
        
        # Causal mask
        causal_mask = torch.triu(torch.full((L, L), float('-inf'), device=input_ids.device), diagonal=1)
        causal_mask = causal_mask.unsqueeze(0).unsqueeze(0)
        
        x = self.embed_tokens(input_ids)
        
        for layer in self.layers:
            x = layer(x, causal_mask)
        
        x = self.norm(x)
        logits = self.lm_head(x)
        
        loss = None
        if labels is not None:
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            loss = F.cross_entropy(shift_logits.view(-1, self.config.vocab_size), shift_labels.view(-1))
        
        return {"loss": loss, "logits": logits}
    
    def generate(self, input_ids, max_new_tokens=100, temperature=0.7, top_p=0.9):
        """Simple generation loop"""
        self.eval()
        with torch.no_grad():
            for _ in range(max_new_tokens):
                outputs = self(input_ids)
                next_token_logits = outputs["logits"][:, -1, :] / temperature
                
                # Top-p sampling
                sorted_logits, sorted_indices = torch.sort(next_token_logits, descending=True)
                cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                sorted_indices_to_remove = cumulative_probs > top_p
                sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                sorted_indices_to_remove[..., 0] = 0
                
                indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
                next_token_logits[indices_to_remove] = float('-inf')
                
                probs = F.softmax(next_token_logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
                input_ids = torch.cat([input_ids, next_token], dim=-1)
                
                # Stop at EOS (token 2 typically)
                if next_token.item() == 2:
                    break
        
        return input_ids


# =============================================================================
# TOKENIZER (Simple BPE-style)
# =============================================================================

class SimpleTokenizer:
    """Simple character/word tokenizer for initial training"""
    def __init__(self, vocab_size: int = 32000):
        self.vocab_size = vocab_size
        self.char_to_id = {}
        self.id_to_char = {}
        self.special_tokens = {
            "<pad>": 0, "<unk>": 1, "<eos>": 2, "<bos>": 3,
            "<|im_start|>": 4, "<|im_end|>": 5,
            "system": 6, "user": 7, "assistant": 8
        }
        
        # Build basic vocab
        self._build_vocab()
    
    def _build_vocab(self):
        idx = len(self.special_tokens)
        
        # Add special tokens
        for token, token_id in self.special_tokens.items():
            self.char_to_id[token] = token_id
            self.id_to_char[token_id] = token
        
        # Add ASCII printable characters
        for c in range(32, 127):
            self.char_to_id[chr(c)] = idx
            self.id_to_char[idx] = chr(c)
            idx += 1
        
        # Add common words/subwords (simplified)
        common_words = [
            "the", "is", "are", "was", "were", "be", "been", "have", "has",
            "tool", "function", "response", "json", "args", "query", "search",
            "read", "write", "file", "database", "memory", "system", "user",
            "assistant", "GLADIUS", "Artifact", "Virtual"
        ]
        for word in common_words:
            if word not in self.char_to_id:
                self.char_to_id[word] = idx
                self.id_to_char[idx] = word
                idx += 1
    
    def encode(self, text: str) -> List[int]:
        """Encode text to token IDs"""
        tokens = [self.special_tokens["<bos>"]]
        i = 0
        while i < len(text):
            # Try to match special tokens first
            matched = False
            for token in sorted(self.special_tokens.keys(), key=len, reverse=True):
                if text[i:].startswith(token):
                    tokens.append(self.special_tokens[token])
                    i += len(token)
                    matched = True
                    break
            
            if not matched:
                # Single character
                c = text[i]
                tokens.append(self.char_to_id.get(c, self.special_tokens["<unk>"]))
                i += 1
        
        tokens.append(self.special_tokens["<eos>"])
        return tokens
    
    def decode(self, ids: List[int]) -> str:
        """Decode token IDs to text"""
        return "".join(self.id_to_char.get(i, "<unk>") for i in ids 
                      if i not in [0, 2, 3])  # Skip pad, eos, bos
    
    def save(self, path: Path):
        """Save tokenizer"""
        with open(path, 'w') as f:
            json.dump({
                "vocab_size": self.vocab_size,
                "char_to_id": self.char_to_id,
                "special_tokens": self.special_tokens
            }, f)
    
    @classmethod
    def load(cls, path: Path):
        """Load tokenizer"""
        with open(path) as f:
            data = json.load(f)
        tok = cls(data["vocab_size"])
        tok.char_to_id = data["char_to_id"]
        tok.id_to_char = {int(k): v for k, v in data.get("id_to_char", {}).items()}
        if not tok.id_to_char:
            tok.id_to_char = {v: k for k, v in tok.char_to_id.items()}
        return tok


# =============================================================================
# DATASET
# =============================================================================

class GladiusDataset(Dataset):
    """Training dataset"""
    def __init__(self, data_path: Path, tokenizer: SimpleTokenizer, max_length: int = 512):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.samples = []
        
        logger.info(f"Loading data from {data_path}")
        with open(data_path) as f:
            for line in f:
                try:
                    data = json.loads(line)
                    text = data.get("text", "")
                    if text:
                        self.samples.append(text)
                except json.JSONDecodeError:
                    continue
        
        logger.info(f"Loaded {len(self.samples)} training samples")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        text = self.samples[idx]
        tokens = self.tokenizer.encode(text)
        
        # Truncate or pad
        if len(tokens) > self.max_length:
            tokens = tokens[:self.max_length]
        else:
            tokens = tokens + [0] * (self.max_length - len(tokens))
        
        tokens = torch.tensor(tokens, dtype=torch.long)
        return {"input_ids": tokens, "labels": tokens.clone()}


# =============================================================================
# TRAINER
# =============================================================================

class NativeTrainer:
    """Native GLADIUS trainer"""
    def __init__(self, config: GladiusConfig = None, target_params_m: int = 150):
        self.config = config or GladiusConfig.for_size(target_params_m)
        self.device = torch.device("cpu")  # CPU training
        
        logger.info(f"Initializing GLADIUS Native Model")
        logger.info(f"  Hidden size: {self.config.hidden_size}")
        logger.info(f"  Layers: {self.config.num_hidden_layers}")
        logger.info(f"  Heads: {self.config.num_attention_heads}")
        logger.info(f"  Parameters: ~{self.config.total_params / 1e6:.1f}M")
        
        self.model = GladiusModel(self.config).to(self.device)
        self.tokenizer = SimpleTokenizer(self.config.vocab_size)
        
        # Optimizer
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=1e-4,
            weight_decay=0.01
        )
    
    def train(self, data_path: Path, epochs: int = 3, batch_size: int = 4, max_length: int = 256):
        """Train the model"""
        dataset = GladiusDataset(data_path, self.tokenizer, max_length)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        self.model.train()
        total_steps = len(dataloader) * epochs
        step = 0
        
        logger.info(f"Starting training: {epochs} epochs, {len(dataloader)} batches/epoch")
        
        for epoch in range(epochs):
            epoch_loss = 0
            for batch in dataloader:
                input_ids = batch["input_ids"].to(self.device)
                labels = batch["labels"].to(self.device)
                
                outputs = self.model(input_ids, labels=labels)
                loss = outputs["loss"]
                
                self.optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                self.optimizer.step()
                
                epoch_loss += loss.item()
                step += 1
                
                if step % 10 == 0:
                    logger.info(f"Step {step}/{total_steps} | Loss: {loss.item():.4f}")
            
            avg_loss = epoch_loss / len(dataloader)
            logger.info(f"Epoch {epoch+1}/{epochs} | Avg Loss: {avg_loss:.4f}")
            
            # Save checkpoint
            self.save_checkpoint(epoch)
    
    def save_checkpoint(self, epoch: int):
        """Save training checkpoint"""
        checkpoint_path = OUTPUT_DIR / f"gladius_native_epoch{epoch}.pt"
        torch.save({
            "epoch": epoch,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "config": self.config.to_dict()
        }, checkpoint_path)
        logger.info(f"Checkpoint saved: {checkpoint_path}")
    
    def save_model(self, path: Path = None):
        """Save final model"""
        path = path or OUTPUT_DIR / "gladius_native_final"
        path.mkdir(parents=True, exist_ok=True)
        
        # Save model weights
        torch.save(self.model.state_dict(), path / "model.pt")
        
        # Save config
        with open(path / "config.json", 'w') as f:
            json.dump(self.config.to_dict(), f, indent=2)
        
        # Save tokenizer
        self.tokenizer.save(path / "tokenizer.json")
        
        logger.info(f"Model saved to {path}")
        return path
    
    def export_gguf(self, output_path: Path = None):
        """Export model to GGUF format"""
        output_path = output_path or OUTPUT_DIR / "gladius_native.gguf"
        
        logger.info(f"Exporting to GGUF: {output_path}")
        
        # Save in format compatible with llama.cpp conversion
        model_path = self.save_model()
        
        # Create a simple GGUF-compatible export
        # Note: Full GGUF export requires llama.cpp tools
        logger.info("Model saved in PyTorch format")
        logger.info("To convert to GGUF, use:")
        logger.info(f"  python -m llama_cpp.convert {model_path} --outfile {output_path}")
        
        return model_path


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="GLADIUS Native Model Trainer")
    parser.add_argument("--params", type=int, default=150, help="Target parameters in millions")
    parser.add_argument("--epochs", type=int, default=3, help="Training epochs")
    parser.add_argument("--batch-size", type=int, default=4, help="Batch size")
    parser.add_argument("--max-length", type=int, default=256, help="Max sequence length")
    parser.add_argument("--export-gguf", action="store_true", help="Export to GGUF")
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("GLADIUS NATIVE MODEL TRAINER")
    logger.info("=" * 70)
    logger.info(f"Target: {args.params}M parameters")
    logger.info(f"Training: {args.epochs} epochs, batch size {args.batch_size}")
    logger.info("NO THIRD-PARTY MODELS - 100% Native")
    logger.info("=" * 70)
    
    # Initialize trainer
    trainer = NativeTrainer(target_params_m=args.params)
    
    # Find training data
    data_path = DATA_DIR / "gladius_1b_training.jsonl"
    if not data_path.exists():
        logger.error(f"Training data not found: {data_path}")
        sys.exit(1)
    
    # Train
    trainer.train(data_path, epochs=args.epochs, batch_size=args.batch_size, max_length=args.max_length)
    
    # Save
    model_path = trainer.save_model()
    
    if args.export_gguf:
        trainer.export_gguf()
    
    logger.info("=" * 70)
    logger.info("GLADIUS Native Training Complete!")
    logger.info(f"Model saved to: {model_path}")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
