#!/usr/bin/env python3
"""
GLADIUS Dual Training System
============================

Dual training system that trains both:
1. Qwen Operational (for current infrastructure use)
2. GLADIUS Primary (custom architecture being built)

This allows the system to operate NOW with Qwen while building GLADIUS in parallel.

Usage:
    python dual_trainer.py [--qwen-only] [--primary-only] [--epochs EPOCHS]
"""

import sys
import argparse
from pathlib import Path
from gladius_moe_trainer import GladiusMoETrainer, logger


def train_qwen_operational(epochs=3, batch_size=4):
    """Train Qwen operational model for infrastructure use."""
    logger.info("=" * 70)
    logger.info("Training Qwen Operational (Infrastructure AI)")
    logger.info("=" * 70)
    
    try:
        # For now, we'll use the MOE trainer which includes Qwen
        trainer = GladiusMoETrainer()
        
        logger.info("Training Qwen for operational infrastructure...")
        # The MOE trainer already trains Qwen as one of the experts
        trainer.train(epochs=epochs, batch_size=batch_size)
        
        logger.info("Qwen operational training completed")
        return True
        
    except Exception as e:
        logger.error(f"Qwen training failed: {e}")
        return False


def train_primary_model(epochs=3, batch_size=4):
    """Train GLADIUS primary custom architecture."""
    logger.info("=" * 70)
    logger.info("Training GLADIUS Primary (Custom Architecture)")
    logger.info("=" * 70)
    
    try:
        trainer = GladiusMoETrainer()
        
        logger.info("Training GLADIUS primary model...")
        trainer.train(epochs=epochs, batch_size=batch_size)
        
        logger.info("GLADIUS primary training completed")
        return True
        
    except Exception as e:
        logger.error(f"Primary training failed: {e}")
        return False


def main():
    """Main dual training entry point."""
    parser = argparse.ArgumentParser(description="GLADIUS Dual Training System")
    parser.add_argument("--qwen-only", action="store_true", 
                       help="Train only Qwen operational model")
    parser.add_argument("--primary-only", action="store_true",
                       help="Train only GLADIUS primary model")
    parser.add_argument("--epochs", type=int, default=3,
                       help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=4,
                       help="Training batch size")
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("GLADIUS DUAL TRAINING SYSTEM")
    logger.info("=" * 70)
    logger.info("Track 1: Qwen2.5-1.5B + LoRA (Operational)")
    logger.info("Track 2: GLADIUS Primary (Custom Architecture)")
    logger.info("=" * 70)
    
    success = True
    
    if args.qwen_only:
        success = train_qwen_operational(args.epochs, args.batch_size)
    elif args.primary_only:
        success = train_primary_model(args.epochs, args.batch_size)
    else:
        # Train both in sequence
        logger.info("Training both models in sequence...")
        success = train_qwen_operational(args.epochs, args.batch_size)
        if success:
            success = train_primary_model(args.epochs, args.batch_size)
    
    if success:
        logger.info("=" * 70)
        logger.info("Dual training completed successfully!")
        logger.info("=" * 70)
        return 0
    else:
        logger.error("Dual training failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
