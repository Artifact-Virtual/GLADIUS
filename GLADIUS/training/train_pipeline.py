#!/usr/bin/env python3
"""
GLADIUS Training Pipeline
=========================

Main training pipeline for GLADIUS native AI model.
This is a wrapper around the MOE trainer that provides a simple interface
for the main training pipeline.

Usage:
    python train_pipeline.py [--epochs EPOCHS] [--batch-size SIZE]
"""

import sys
from pathlib import Path

# Import the main MOE trainer
from gladius_moe_trainer import GladiusMoETrainer, logger

def main():
    """Main training pipeline entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GLADIUS Training Pipeline")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=4, help="Training batch size")
    parser.add_argument("--learning-rate", type=float, default=2e-5, help="Learning rate")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("GLADIUS Training Pipeline Starting")
    logger.info("=" * 70)
    logger.info(f"Epochs: {args.epochs}")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info(f"Learning rate: {args.learning_rate}")
    logger.info(f"Resume from checkpoint: {args.resume}")
    logger.info("=" * 70)
    
    try:
        # Initialize trainer
        trainer = GladiusMoETrainer()
        
        # Run training
        logger.info("Initializing training...")
        result = trainer.train(
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            resume=args.resume
        )
        
        logger.info("=" * 70)
        logger.info("Training completed successfully!")
        logger.info("=" * 70)
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("Training interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Training failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
