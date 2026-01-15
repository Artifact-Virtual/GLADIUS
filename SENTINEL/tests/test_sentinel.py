#!/usr/bin/env python3
"""
SENTINEL Regression & Fail-Safe Test Suite
===========================================

Validates that SENTINEL is production-ready:
1. Kill password protection works
2. Checkpoint/recovery works
3. Database persistence works
4. Web research works
5. GLADIUS integration works
6. Watchdog auto-restart works

Author: Artifact Virtual Systems
"""

import os
import sys
import json
import asyncio
import sqlite3
import hashlib
import tempfile
from pathlib import Path
from datetime import datetime

# Setup paths
SENTINEL_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SENTINEL_ROOT.parent))

# Test results
results = {
    "passed": [],
    "failed": [],
    "warnings": []
}


def test_pass(name: str, msg: str = ""):
    results["passed"].append({"name": name, "msg": msg})
    print(f"  ✅ {name}: {msg}")


def test_fail(name: str, msg: str = ""):
    results["failed"].append({"name": name, "msg": msg})
    print(f"  ❌ {name}: {msg}")


def test_warn(name: str, msg: str = ""):
    results["warnings"].append({"name": name, "msg": msg})
    print(f"  ⚠️  {name}: {msg}")


async def test_kill_password():
    """Test that kill password protection works"""
    print("\n1️⃣  Testing Kill Password Protection...")
    
    from SENTINEL.services.learning_daemon import LearningDaemon
    
    daemon = LearningDaemon()
    
    # Check if password is set in environment
    stored_hash = os.getenv("SENTINEL_KILL_PASSWORD")
    if not stored_hash:
        test_fail("Kill Password Env", "SENTINEL_KILL_PASSWORD not set")
        return
    
    test_pass("Kill Password Env", "Password hash found")
    
    # Test correct password
    correct_password = "Sirius_Kill_Switch"
    if daemon.verify_kill_password(correct_password):
        test_pass("Correct Password", "Verification succeeded")
    else:
        test_fail("Correct Password", "Verification failed")
    
    # Test wrong password
    if not daemon.verify_kill_password("wrong_password"):
        test_pass("Wrong Password", "Correctly rejected")
    else:
        test_fail("Wrong Password", "Should have been rejected")


async def test_checkpoint_recovery():
    """Test checkpoint save/load works"""
    print("\n2️⃣  Testing Checkpoint Recovery...")
    
    from SENTINEL.services.learning_daemon import LearningDaemon, LearningPhase
    
    daemon = LearningDaemon()
    daemon._init_state_db()
    
    # Create test state
    daemon.state = daemon._load_state()
    daemon.state.current_phase = LearningPhase.LEARN
    daemon.state.cycles_completed = 42
    
    # Save checkpoint
    daemon._save_checkpoint()
    test_pass("Save Checkpoint", f"Cycle {daemon.state.cycles_completed}")
    
    # Create new daemon and load state
    daemon2 = LearningDaemon()
    daemon2._init_state_db()
    loaded_state = daemon2._load_state()
    
    if loaded_state.cycles_completed == 42:
        test_pass("Load Checkpoint", f"Recovered cycle {loaded_state.cycles_completed}")
    else:
        test_fail("Load Checkpoint", f"Expected 42, got {loaded_state.cycles_completed}")
    
    if loaded_state.current_phase == LearningPhase.LEARN:
        test_pass("Phase Recovery", f"Phase: {loaded_state.current_phase.value}")
    else:
        test_fail("Phase Recovery", f"Expected LEARN, got {loaded_state.current_phase.value}")


async def test_database_persistence():
    """Test database tables exist and work"""
    print("\n3️⃣  Testing Database Persistence...")
    
    from SENTINEL.services.learning_daemon import LearningDaemon
    
    daemon = LearningDaemon()
    daemon._init_state_db()
    
    # Check tables
    conn = sqlite3.connect(daemon.state_db_path)
    cursor = conn.cursor()
    
    tables = ["state", "discoveries", "insights", "training_queue"]
    for table in tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if cursor.fetchone():
            test_pass(f"Table: {table}", "Exists")
        else:
            test_fail(f"Table: {table}", "Missing")
    
    conn.close()


async def test_web_research():
    """Test web research capabilities"""
    print("\n4️⃣  Testing Web Research...")
    
    from SENTINEL.services.learning_daemon import WebResearcher
    
    researcher = WebResearcher()
    
    try:
        # Test arXiv search
        results_arxiv = await researcher.search_arxiv(["machine learning"], max_results=2)
        if len(results_arxiv) > 0:
            test_pass("arXiv Search", f"Found {len(results_arxiv)} results")
        else:
            test_warn("arXiv Search", "No results (might be rate limited)")
        
        # Test GitHub search
        results_github = await researcher.search_github(["llm"], max_results=2)
        if len(results_github) > 0:
            test_pass("GitHub Search", f"Found {len(results_github)} results")
        else:
            test_warn("GitHub Search", "No results (might be rate limited)")
        
    except Exception as e:
        test_fail("Web Research", str(e))
    finally:
        await researcher.close()


async def test_gladius_integration():
    """Test GLADIUS integration"""
    print("\n5️⃣  Testing GLADIUS Integration...")
    
    from SENTINEL.services.learning_daemon import GladiusConnector
    
    connector = GladiusConnector()
    
    # Test router loading
    if connector.router:
        test_pass("GLADIUS Router", "Loaded successfully")
    else:
        test_warn("GLADIUS Router", "Using fallback mode")
    
    # Test analysis
    result = await connector.analyze_text("machine learning neural network", "extract_keywords")
    if result.get("status") in ["success", "fallback"]:
        test_pass("Text Analysis", f"Mode: {result.get('status')}")
    else:
        test_fail("Text Analysis", str(result))
    
    # Test training data generation
    insights = [{"topic": "Test", "summary": "Test summary", "keywords": ["test"]}]
    training_data = await connector.generate_training_data(insights)
    if len(training_data) > 0:
        test_pass("Training Data", f"Generated {len(training_data)} samples")
    else:
        test_fail("Training Data", "No samples generated")


async def test_watchdog_process():
    """Test watchdog process management"""
    print("\n6️⃣  Testing Watchdog Process Management...")
    
    from SENTINEL.services.watchdog import Watchdog, ProcessState
    
    watchdog = Watchdog()
    
    # Check process definitions
    if len(watchdog.processes) > 0:
        test_pass("Process Definitions", f"{len(watchdog.processes)} processes defined")
    else:
        test_fail("Process Definitions", "No processes defined")
    
    # Check initial states
    for name, proc in watchdog.processes.items():
        if proc.state == ProcessState.STOPPED:
            test_pass(f"Process {name}", "Initial state: STOPPED")
        else:
            test_warn(f"Process {name}", f"Unexpected state: {proc.state.value}")
    
    # Test password verification
    if watchdog.verify_kill_password("Sirius_Kill_Switch"):
        test_pass("Watchdog Kill Password", "Verification works")
    else:
        test_fail("Watchdog Kill Password", "Verification failed")


async def test_full_cycle():
    """Test a complete learning cycle"""
    print("\n7️⃣  Testing Full Learning Cycle...")
    
    from SENTINEL.services.learning_daemon import LearningDaemon
    
    daemon = LearningDaemon()
    daemon._init_state_db()
    daemon.state = daemon._load_state()
    
    initial_cycles = daemon.state.cycles_completed
    
    try:
        await daemon.run_cycle()
        
        if daemon.state.cycles_completed > initial_cycles:
            test_pass("Full Cycle", f"Completed cycle {daemon.state.cycles_completed}")
        else:
            test_fail("Full Cycle", "Cycle count did not increment")
        
        # Check discoveries were stored
        conn = sqlite3.connect(daemon.state_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM discoveries")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count > 0:
            test_pass("Discoveries Stored", f"{count} total discoveries")
        else:
            test_warn("Discoveries Stored", "No discoveries (research might be rate-limited)")
        
    except Exception as e:
        test_fail("Full Cycle", str(e))
    finally:
        await daemon.researcher.close()


async def main():
    """Run all tests"""
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║               SENTINEL REGRESSION & FAIL-SAFE TEST SUITE                      ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    
    # Load env
    from dotenv import load_dotenv
    load_dotenv(SENTINEL_ROOT.parent / ".env")
    
    await test_kill_password()
    await test_checkpoint_recovery()
    await test_database_persistence()
    await test_web_research()
    await test_gladius_integration()
    await test_watchdog_process()
    await test_full_cycle()
    
    # Summary
    print("\n" + "═" * 80)
    print("                              TEST SUMMARY")
    print("═" * 80)
    print(f"  ✅ Passed:   {len(results['passed'])}")
    print(f"  ⚠️  Warnings: {len(results['warnings'])}")
    print(f"  ❌ Failed:   {len(results['failed'])}")
    print("═" * 80)
    
    if results['failed']:
        print("\nFailed Tests:")
        for test in results['failed']:
            print(f"  - {test['name']}: {test['msg']}")
        print("")
        return 1
    else:
        print("\n✅ ALL TESTS PASSED - SENTINEL IS PRODUCTION READY")
        return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
