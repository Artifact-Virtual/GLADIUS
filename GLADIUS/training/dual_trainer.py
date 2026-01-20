#!/usr/bin/env python3
"""
GLADIUS Dual Training System
============================

Dual training system that trains both:
1. Qwen Operational (for current infrastructure use)
2. GLADIUS Primary (custom architecture being built)

This allows the system to operate NOW with Qwen while building GLADIUS in parallel.

Usage:
    python dual_trainer.py [--qwen-only] [--primary-only] [--max-hours HOURS]
"""

import sys
import argparse
from pathlib import Path
from gladius_moe_trainer import MultiExpertDistiller, logger


def train_qwen_operational(max_hours=24.0):
    """Train Qwen operational model for infrastructure use."""
    logger.info("=" * 70)
    logger.info("Training Qwen Operational (Infrastructure AI)")
    logger.info("=" * 70)
    
    try:
        # The MultiExpertDistiller already includes Qwen as one of the experts
        trainer = MultiExpertDistiller()
        
        logger.info("Training with Qwen expert for operational infrastructure...")
        trainer.train_full_pipeline(max_hours=max_hours)
        
        logger.info("Qwen operational training completed")
        return True
        
    except Exception as e:
        logger.error(f"Qwen training failed: {e}")
        return False


def train_primary_model(max_hours=48.0):
    """Train GLADIUS primary custom architecture."""
    logger.info("=" * 70)
    logger.info("Training GLADIUS Primary (Custom Architecture)")
    logger.info("=" * 70)
    
    try:
        trainer = MultiExpertDistiller()
        
        logger.info("Training GLADIUS primary model...")
        trainer.train_full_pipeline(max_hours=max_hours)
        
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
    parser.add_argument("--max-hours", type=float, default=72.0,
                       help="Maximum training hours (default: 72, split if training both)")
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("GLADIUS DUAL TRAINING SYSTEM")
    logger.info("=" * 70)
    logger.info("Track 1: Qwen2.5-1.5B (Operational)")
    logger.info("Track 2: GLADIUS Primary (Custom Architecture)")
    logger.info("=" * 70)
    
    success = True
    
    if args.qwen_only:
        success = train_qwen_operational(args.max_hours)
    elif args.primary_only:
        success = train_primary_model(args.max_hours)
    else:
        # Train both in sequence, split time
        logger.info("Training both models in sequence...")
        qwen_hours = args.max_hours * 0.3  # Qwen gets 30% of time
        primary_hours = args.max_hours * 0.7  # Primary gets 70% of time
        
        success = train_qwen_operational(qwen_hours)
        if success:
            success = train_primary_model(primary_hours)
    
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
