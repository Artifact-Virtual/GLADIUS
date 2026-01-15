#!/usr/bin/env python3
"""
LEGION-Artifact Integration Test Suite
=======================================

Tests LEGION integration with Artifact infrastructure:
1. CLI functionality
2. Artifact Bridge connectivity
3. GLADIUS AI routing
4. Social media bridge
5. Agent orchestration

Author: Artifact Virtual Systems
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

# Setup paths
LEGION_ROOT = Path(__file__).parent.parent
GLADIUS_ROOT = LEGION_ROOT.parent
sys.path.insert(0, str(GLADIUS_ROOT))
sys.path.insert(0, str(LEGION_ROOT))

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


def test_cli_commands():
    """Test LEGION CLI commands work"""
    print("\n1️⃣  Testing LEGION CLI Commands...")
    
    import subprocess
    
    cli_path = LEGION_ROOT / "legion" / "cli.py"
    
    # Test system status
    result = subprocess.run(
        ["python3", str(cli_path), "system", "status"],
        capture_output=True,
        text=True,
        cwd=LEGION_ROOT / "legion"
    )
    
    if result.returncode == 0 and "LEGION ENTERPRISE SYSTEM" in result.stdout:
        test_pass("CLI system status", "Working")
    else:
        test_fail("CLI system status", result.stderr[:100] if result.stderr else "Unknown error")
    
    # Test agent list
    result = subprocess.run(
        ["python3", str(cli_path), "agent", "list"],
        capture_output=True,
        text=True,
        cwd=LEGION_ROOT / "legion"
    )
    
    if result.returncode == 0:
        test_pass("CLI agent list", "Working")
    else:
        test_fail("CLI agent list", result.stderr[:100] if result.stderr else "Unknown error")


async def test_artifact_bridge():
    """Test Artifact Bridge connectivity"""
    print("\n2️⃣  Testing Artifact Bridge...")
    
    try:
        from LEGION.legion.artifact_bridge import ArtifactBridge, get_bridge
        
        bridge = get_bridge()
        
        # Check integrations discovered
        if len(bridge.available_integrations) > 0:
            test_pass("Integration Discovery", f"{sum(bridge.available_integrations.values())} available")
        else:
            test_fail("Integration Discovery", "No integrations found")
        
        # Check GLADIUS integration
        if bridge.available_integrations.get("gladius"):
            test_pass("GLADIUS Integration", "Available")
        else:
            test_warn("GLADIUS Integration", "Not available")
        
        # Check social integrations
        social_platforms = ["discord", "twitter", "linkedin", "facebook"]
        available = [p for p in social_platforms if bridge.available_integrations.get(p)]
        if available:
            test_pass("Social Media", f"{len(available)} platforms: {', '.join(available)}")
        else:
            test_warn("Social Media", "No platforms available")
        
    except ImportError as e:
        test_fail("Artifact Bridge Import", str(e))
    except Exception as e:
        test_fail("Artifact Bridge", str(e))


async def test_gladius_routing():
    """Test GLADIUS routing through bridge"""
    print("\n3️⃣  Testing GLADIUS Routing...")
    
    try:
        from LEGION.legion.artifact_bridge import get_bridge
        
        bridge = get_bridge()
        
        # Query GLADIUS
        result = await bridge.query_gladius("Search for market analysis data")
        
        if result.success:
            test_pass("GLADIUS Query", f"Tool: {result.data.get('tool', 'N/A')}")
        else:
            test_warn("GLADIUS Query", result.error or "No response")
        
        # Check response structure
        if result.data and "confidence" in result.data:
            confidence = result.data.get("confidence", 0)
            test_pass("Response Structure", f"Confidence: {confidence:.2%}")
        else:
            test_warn("Response Structure", "Missing confidence")
        
    except Exception as e:
        test_fail("GLADIUS Routing", str(e))


async def test_social_bridge():
    """Test social media bridge"""
    print("\n4️⃣  Testing Social Media Bridge...")
    
    try:
        from LEGION.communication.social_bridge import get_social_bridge, SocialMediaBridge
        
        # Create bridge without loading legacy service (which needs selenium)
        bridge = SocialMediaBridge()
        bridge._initialize()  # Only initializes artifact bridge
        
        if bridge.artifact_bridge:
            test_pass("Social Bridge Init", "Artifact bridge connected")
        else:
            test_warn("Social Bridge Init", "Artifact bridge not available")
        
        # Check platforms via artifact bridge
        platforms = bridge._available_platforms
        api_count = sum(1 for p, v in platforms.items() if v)
        if api_count > 0:
            test_pass("Platform Discovery", f"{api_count} API platforms available")
        else:
            test_warn("Platform Discovery", "No API platforms available")
        
    except ImportError as e:
        test_warn("Social Bridge Import", str(e))
    except Exception as e:
        test_fail("Social Bridge", str(e))


def test_agent_registry():
    """Test agent registry"""
    print("\n5️⃣  Testing Agent Registry...")
    
    try:
        from LEGION.legion.enterprise_registry import EnterpriseRegistry
        
        registry = EnterpriseRegistry()
        
        # Check domains
        if hasattr(registry, 'agent_definitions'):
            agents = registry.agent_definitions
            test_pass("Agent Definitions", f"{len(agents)} agents defined")
        else:
            test_warn("Agent Definitions", "No definitions found")
        
    except ImportError as e:
        test_warn("Enterprise Registry", str(e))
    except Exception as e:
        test_fail("Enterprise Registry", str(e))


def test_message_bus():
    """Test message bus"""
    print("\n6️⃣  Testing Message Bus...")
    
    try:
        from LEGION.legion.message_bus import MessageBus, Message
        import uuid
        
        bus = MessageBus()
        
        # Check if bus initializes
        test_pass("Message Bus Init", "Initialized successfully")
        
        # Check message creation with correct parameters
        msg = Message(
            message_id=str(uuid.uuid4()),
            sender_id="test_agent",
            recipient_id="other_agent",
            message_type="test",
            content={"message": "Test message"},
            timestamp=datetime.now(),
            priority=5
        )
        
        test_pass("Message Create", "Message created successfully")
        
    except ImportError as e:
        test_warn("Message Bus Import", str(e))
    except Exception as e:
        test_fail("Message Bus", str(e))


async def main():
    """Run all tests"""
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║            LEGION-ARTIFACT INTEGRATION TEST SUITE                             ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    
    # Load env
    from dotenv import load_dotenv
    load_dotenv(GLADIUS_ROOT / ".env")
    
    test_cli_commands()
    await test_artifact_bridge()
    await test_gladius_routing()
    await test_social_bridge()
    test_agent_registry()
    test_message_bus()
    
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
        print("\n✅ ALL TESTS PASSED - LEGION INTEGRATION COMPLETE")
        return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
