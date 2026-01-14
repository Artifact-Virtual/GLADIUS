"""
GLADIUS Router Module
=====================

Pattern-based and GGUF inference routing for tool selection.

Components:
- pattern_router.py   TF-IDF based routing (current)
- gguf_router.py      GGUF model inference (target)

Usage:
    from GLADIUS.router.pattern_router import PatternRouter
    
    router = PatternRouter()
    result = router.route("Search for gold analysis")
"""

def get_router():
    """Get the pattern router instance."""
    from .pattern_router import PatternRouter
    return PatternRouter()
