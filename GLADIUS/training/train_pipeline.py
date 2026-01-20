#!/usr/bin/env python3
"""
GLADIUS Training Pipeline
=========================

Main training pipeline for GLADIUS native AI model.
This is a wrapper around the MOE trainer that provides a simple interface
for the main training pipeline.

Usage:
    python train_pipeline.py [--max-hours HOURS]
"""

import sys
from pathlib import Path

# Import the main MOE trainer
from gladius_moe_trainer import MultiExpertDistiller, logger

def main():
    """Main training pipeline entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GLADIUS Training Pipeline")
    parser.add_argument("--max-hours", type=float, default=72.0, 
                       help="Maximum training hours (default: 72)")
    parser.add_argument("--resume", action="store_true", 
                       help="Resume from checkpoint")
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("GLADIUS Training Pipeline Starting")
    logger.info("=" * 70)
    logger.info(f"Max hours: {args.max_hours}")
    logger.info(f"Resume from checkpoint: {args.resume}")
    logger.info("=" * 70)
    
    try:
        # Initialize trainer
        trainer = MultiExpertDistiller()
        
        # Load checkpoint if resuming
        if args.resume:
            logger.info("Attempting to resume from checkpoint...")
            trainer.load_checkpoint()
        
        # Run training
        logger.info("Starting training pipeline...")
        trainer.train_full_pipeline(max_hours=args.max_hours)
        
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
