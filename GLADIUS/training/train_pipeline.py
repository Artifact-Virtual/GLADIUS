#!/usr/bin/env python3
"""
GLADIUS Training Pipeline
=========================

Main training pipeline for GLADIUS native AI model.
Wrapper around the unified trainer.

Usage:
    python train_pipeline.py [--params M] [--epochs N]
"""

import sys
from pathlib import Path

from gladius_trainer import GladiusTrainer, DATA_DIR, logger

def main():
    """Main training pipeline entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GLADIUS Training Pipeline")
    parser.add_argument("--params", type=int, default=None, help="Target params in millions")
    parser.add_argument("--epochs", type=int, default=3, help="Training epochs")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--export-gguf", action="store_true", help="Export GGUF after training")
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("GLADIUS Training Pipeline")
    logger.info("=" * 70)
    
    try:
        trainer = GladiusTrainer(target_params_m=args.params)
        
        if args.resume:
            trainer.load_checkpoint()
        
        data_path = DATA_DIR / "gladius_1b_training.jsonl"
        trainer.train(data_path, epochs=args.epochs)
        
        if args.export_gguf:
            trainer.export_gguf()
        
        logger.info("Training completed!")
        return 0
        
    except KeyboardInterrupt:
        logger.warning("Training interrupted")
        return 1
    except Exception as e:
        logger.error(f"Training failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
