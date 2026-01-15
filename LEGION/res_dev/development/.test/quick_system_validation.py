#!/usr/bin/env python3
"""
Quick System Validation for Artifact Virtual Recovery
Tests basic import functionality of rebuilt systems
"""
import sys
import os
from pathlib import Path

# Add workspace to Python path
workspace_path = Path(__file__).parent.parent.parent  # Go to project root
sys.path.insert(0, str(workspace_path))
sys.path.insert(0, str(workspace_path / "tools"))
sys.path.insert(0, str(workspace_path / "workshop"))
print(f"Added to Python path: {workspace_path}")


def test_imports():
    """Test importing all rebuilt systems"""
    results = {}

    # Test tools
    try:
        from tools.backup.backup_system import BackupSystem

        results["backup_system"] = "SUCCESS"
    except Exception as e:
        results["backup_system"] = f"FAILED: {e}"

    try:
        from tools.analysis.advanced_analysis import AdvancedAnalysisEngine

        results["analysis_system"] = "SUCCESS"
    except Exception as e:
        results["analysis_system"] = f"FAILED: {e}"

    # Test production systems
    try:
        from workshop.production.intelligent_production_crew import (
            IntelligentProductionCrew,
        )

        results["production_crew"] = "SUCCESS"
    except Exception as e:
        results["production_crew"] = f"FAILED: {e}"

    try:
        from workshop.production.devops_monitoring_dashboard import (
            DevOpsMonitoringDashboard,
        )

        results["monitoring_dashboard"] = "SUCCESS"
    except Exception as e:
        results["monitoring_dashboard"] = f"FAILED: {e}"

    try:
        from workshop.production.enterprise_cicd_pipeline import EnterpriseCICDPipeline

        results["cicd_pipeline"] = "SUCCESS"
    except Exception as e:
        results["cicd_pipeline"] = f"FAILED: {e}"
    # Test automation systems
    try:
        from workshop.automations.production.agent_templates import AgentFactory

        results["agent_templates"] = "SUCCESS"
    except Exception as e:
        results["agent_templates"] = f"FAILED: {e}"

    try:
        from workshop.automations.production.workflow_orchestrator import WorkflowEngine

        results["workflow_orchestrator"] = "SUCCESS"
    except Exception as e:
        results["workflow_orchestrator"] = f"FAILED: {e}"

    try:
        from workshop.automations.enterprise_automation_orchestrator import (
            EnterpriseAutomationOrchestrator,
        )

        results["enterprise_orchestrator"] = "SUCCESS"
    except Exception as e:
        results["enterprise_orchestrator"] = f"FAILED: {e}"

    # Test build and iteration systems
    try:
        from workshop._build.build_automation import BuildAutomationSystem

        results["build_automation"] = "SUCCESS"
    except Exception as e:
        results["build_automation"] = f"FAILED: {e}"

    try:
        from workshop.iterate.intelligent_iteration_engine import (
            IntelligentIterationEngine,
        )

        results["iteration_engine"] = "SUCCESS"
    except Exception as e:
        results["iteration_engine"] = f"FAILED: {e}"

    return results


def test_functionality():
    """Test basic functionality of key systems"""
    results = {}

    # Test backup system initialization
    try:
        from tools.backup.backup_system import BackupSystem

        backup = BackupSystem(workspace_path)
        results["backup_init"] = "SUCCESS"
    except Exception as e:
        results["backup_init"] = f"FAILED: {e}"
    # Test production crew initialization
    try:
        from workshop.production.intelligent_production_crew import (
            IntelligentProductionCrew,
        )

        crew = IntelligentProductionCrew(workspace_path)
        results["crew_init"] = "SUCCESS"
    except Exception as e:
        results["crew_init"] = f"FAILED: {e}"

    # Test orchestrator initialization
    try:
        from workshop.automations.enterprise_automation_orchestrator import (
            EnterpriseAutomationOrchestrator,
        )

        orchestrator = EnterpriseAutomationOrchestrator(str(workspace_path))
        results["orchestrator_init"] = "SUCCESS"
    except Exception as e:
        results["orchestrator_init"] = f"FAILED: {e}"

    return results


def main():
    """Run all validation tests"""
    print("ARTIFACT VIRTUAL SYSTEM VALIDATION")
    print("=" * 50)

    # Import tests
    print("IMPORT TESTS")
    print("-" * 20)
    import_results = test_imports()

    for test_name, result in import_results.items():
        print(f"{test_name:<25} {result}")

    # Functionality tests
    print("\nFUNCTIONALITY TESTS")
    print("-" * 25)
    func_results = test_functionality()

    for test_name, result in func_results.items():
        print(f"{test_name:<25} {result}")

    # Summary
    all_results = {**import_results, **func_results}
    total_tests = len(all_results)
    passed_tests = len([r for r in all_results.values() if "SUCCESS" in r])
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

    print(f"\nSUMMARY")
    print("-" * 12)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")

    if success_rate >= 80:
        print("SYSTEM READY - All critical systems operational")
        return 0
    elif success_rate >= 60:
        print("SYSTEM PARTIAL - Some issues detected")
        return 1
    else:
        print("CRITICAL - Major system failures detected")
        return 1


if __name__ == "__main__":
    exit(main())
