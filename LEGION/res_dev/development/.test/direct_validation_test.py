#!/usr/bin/env python3
"""
Direct System Validation Test with Path Configuration
Tests systems with explicit path management
"""
import os
import sys
from pathlib import Path

# Add workspace to Python path explicitly
workspace_path = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_path))


def test_direct_imports():
    """Test direct imports with path configured"""
    print("🔍 DIRECT SYSTEM VALIDATION TEST")
    print("=" * 50)
    print(f"Workspace Path: {workspace_path}")
    print(f"Python Path: {sys.path[:3]}...")
    print()

    results = {}

    # Test 1: Direct file existence
    print("📁 File Existence Check:")
    files_to_check = [
        "tools/backup/backup_system.py",
        "tools/analysis/advanced_analysis.py",
        "workshop/production/intelligent_production_crew.py",
        "workshop/automations/production/agent_templates.py",
        "workshop/production/devops_monitoring_dashboard.py",
    ]

    for file_path in files_to_check:
        full_path = workspace_path / file_path
        exists = full_path.exists()
        print(f"   {file_path}: {'✅' if exists else '❌'}")
        results[file_path] = exists

    print()

    # Test 2: Direct import with exec
    print("🐍 Direct Import Test:")

    try:
        # Test backup system
        backup_path = workspace_path / "tools" / "backup" / "backup_system.py"
        if backup_path.exists():
            with open(backup_path, "r") as f:
                backup_code = f.read()
            exec(compile(backup_code, str(backup_path), "exec"), globals())
            print("   Backup System: ✅ Code executable")
            results["backup_import"] = True
        else:
            print("   Backup System: ❌ File not found")
            results["backup_import"] = False
    except Exception as e:
        print(f"   Backup System: ❌ Error: {e}")
        results["backup_import"] = False

    try:
        # Test monitoring dashboard
        monitor_path = (
            workspace_path
            / "workshop"
            / "production"
            / "devops_monitoring_dashboard.py"
        )
        if monitor_path.exists():
            # Just check if file is readable and valid Python
            with open(monitor_path, "r") as f:
                monitor_code = f.read()
            compile(monitor_code, str(monitor_path), "exec")
            print("   Monitoring Dashboard: ✅ Code compilable")
            results["monitor_import"] = True
        else:
            print("   Monitoring Dashboard: ❌ File not found")
            results["monitor_import"] = False
    except Exception as e:
        print(f"   Monitoring Dashboard: ❌ Error: {e}")
        results["monitor_import"] = False

    print()

    # Test 3: Database connectivity
    print("🗄️ Database Test:")
    try:
        import sqlite3

        test_db = workspace_path / "data" / "validation_test.db"
        test_db.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(str(test_db)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, data TEXT)"
            )
            cursor.execute("INSERT INTO test (data) VALUES (?)", ("validation_test",))
            cursor.execute("SELECT COUNT(*) FROM test")
            count = cursor.fetchone()[0]
            conn.commit()

        print(f"   Database Operations: ✅ {count} records")
        results["database"] = True

        # Clean up
        test_db.unlink()

    except Exception as e:
        print(f"   Database Operations: ❌ Error: {e}")
        results["database"] = False

    print()

    # Test 4: System metrics
    print("📊 System Metrics Test:")
    try:
        import psutil

        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage("C:" if os.name == "nt" else "/").percent

        print(f"   CPU Usage: {cpu}%")
        print(f"   Memory Usage: {memory}%")
        print(f"   Disk Usage: {disk}%")
        print("   System Metrics: ✅ Collected successfully")
        results["metrics"] = True

    except Exception as e:
        print(f"   System Metrics: ❌ Error: {e}")
        results["metrics"] = False

    print()

    # Summary
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

    print("📋 SUMMARY")
    print("-" * 20)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")

    status = (
        "✅ EXCELLENT"
        if success_rate >= 90
        else (
            "✅ GOOD"
            if success_rate >= 75
            else "⚠️ PARTIAL" if success_rate >= 50 else "❌ CRITICAL"
        )
    )

    print(f"Status: {status}")

    return results, success_rate


if __name__ == "__main__":
    test_direct_imports()
