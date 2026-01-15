"""
SENTINEL Services
=================

Background services for continuous operation.

Components:
- learning_daemon.py    Continuous learning loop (DISCOVER → LEARN → TRAIN → UPGRADE → REVIEW)
- watchdog.py          Process monitor with auto-restart
- research_daemon.py   Web research crawler (arXiv, MIT, GitHub)

Usage:
    # Start the learning daemon
    python -m SENTINEL.services.learning_daemon start
    
    # Start the watchdog (manages all daemons)
    python -m SENTINEL.services.watchdog start
    
    # Stop with password
    python -m SENTINEL.services.watchdog stop --password="your_password"
"""

from pathlib import Path

SERVICES_DIR = Path(__file__).parent


def start_all():
    """Start all SENTINEL services via watchdog"""
    from .watchdog import Watchdog
    import asyncio
    
    watchdog = Watchdog()
    asyncio.run(watchdog.run())


def stop_all(password: str) -> bool:
    """Stop all SENTINEL services"""
    from .watchdog import Watchdog
    
    watchdog = Watchdog()
    return watchdog.stop(password)


def get_status() -> dict:
    """Get status of all services"""
    from .watchdog import Watchdog
    
    watchdog = Watchdog()
    return watchdog.get_status()
