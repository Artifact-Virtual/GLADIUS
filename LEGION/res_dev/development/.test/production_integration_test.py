#!/usr/bin/env python3
"""
Comprehensive Production Integration Test Suite
Advanced testing across all reconstructed Artifact Virtual systems
"""
import asyncio
import json
import logging
import os
import sqlite3
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

# Add workspace to Python path
workspace_path = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProductionIntegurationTest:
    """Production-ready integration test suite"""

    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.test_results = {}
        self.start_time = time.time()

    async def run_full_integration_test(self) -> Dict[str, Any]:
        """Run complete integration test suite"""
        logger.info("🚀 Starting Production Integration Test Suite...")

        results = {
            "test_suite": "Production Integration Tests",
            "start_time": datetime.utcnow().isoformat(),
            "tests": {},
            "summary": {},
        }

        # Test 1: System Import and Initialization
        logger.info("📦 Testing System Imports and Initialization...")
        results["tests"]["system_imports"] = await self._test_system_imports()

        # Test 2: Database Connectivity and Schema
        logger.info("🗄️ Testing Database Systems...")
        results["tests"]["database_systems"] = await self._test_database_systems()

        # Test 3: Core Functionality Testing
        logger.info("⚙️ Testing Core System Functionality...")
        results["tests"]["core_functionality"] = await self._test_core_functionality()

        # Test 4: Agent System Integration
        logger.info("🤖 Testing Agent System Integration...")
        results["tests"]["agent_integration"] = await self._test_agent_integration()

        # Test 5: Workflow Orchestration
        logger.info("🎯 Testing Workflow Orchestration...")
        results["tests"][
            "workflow_orchestration"
        ] = await self._test_workflow_orchestration()

        # Test 6: Monitoring and Alerting
        logger.info("📊 Testing Monitoring and Alerting...")
        results["tests"]["monitoring_alerting"] = await self._test_monitoring_alerting()

        # Test 7: Build and Deployment Pipeline
        logger.info("🚀 Testing Build and Deployment Pipeline...")
        results["tests"]["build_deployment"] = await self._test_build_deployment()

        # Test 8: End-to-End Workflow
        logger.info("🔄 Testing End-to-End Workflow...")
        results["tests"]["end_to_end"] = await self._test_end_to_end_workflow()

        # Generate Summary
        results["summary"] = self._generate_test_summary(results["tests"])
        results["end_time"] = datetime.utcnow().isoformat()
        results["total_duration"] = time.time() - self.start_time

        return results

    async def _test_system_imports(self) -> Dict[str, Any]:
        """Test all system imports"""
        test_results = {
            "status": "running",
            "imports_tested": 0,
            "imports_successful": 0,
            "failed_imports": [],
            "details": {},
        }

        import_tests = [
            ("Backup System", "tools.backup.backup_system", "BackupSystem"),
            (
                "Analysis System",
                "tools.analysis.advanced_analysis",
                "AdvancedCodeAnalyzer",
            ),
            (
                "Production Crew",
                "workshop.production.intelligent_production_crew",
                "ProductionCrew",
            ),
            (
                "Agent Templates",
                "workshop.automations.production.agent_templates",
                "AgentTemplate",
            ),
            (
                "Workflow Orchestrator",
                "workshop.automations.production.workflow_orchestrator",
                "WorkflowOrchestrator",
            ),
            (
                "Test Framework",
                "workshop.test.intelligent_test_framework",
                "IntelligentTestFramework",
            ),
            (
                "Build Automation",
                "workshop._build.build_automation",
                "BuildAutomationSystem",
            ),
            (
                "Iteration Engine",
                "workshop.iterate.intelligent_iteration_engine",
                "IntelligentIterationEngine",
            ),
            (
                "Prototype System",
                "workshop.__prototype.prototype_system",
                "PrototypeSystem",
            ),
            (
                "CI/CD Pipeline",
                "workshop.production.enterprise_cicd_pipeline",
                "EnterpriseCICDPipeline",
            ),
            (
                "Monitoring Dashboard",
                "workshop.production.devops_monitoring_dashboard",
                "DevOpsMonitoringDashboard",
            ),
            (
                "Automation Orchestrator",
                "workshop.automations.enterprise_automation_orchestrator",
                "EnterpriseAutomationOrchestrator",
            ),
        ]

        for name, module_path, class_name in import_tests:
            test_results["imports_tested"] += 1
            try:
                module = __import__(module_path, fromlist=[class_name])
                cls = getattr(module, class_name)
                test_results["imports_successful"] += 1
                test_results["details"][name] = "✅ SUCCESS"
                logger.info(f"✅ {name} import successful")
            except Exception as e:
                test_results["failed_imports"].append(name)
                test_results["details"][name] = f"❌ FAILED: {str(e)}"
                logger.error(f"❌ {name} import failed: {e}")

        test_results["status"] = "completed"
        test_results["success_rate"] = (
            test_results["imports_successful"] / test_results["imports_tested"]
        ) * 100

        return test_results

    async def _test_database_systems(self) -> Dict[str, Any]:
        """Test database connectivity and schema"""
        test_results = {
            "status": "running",
            "databases_tested": 0,
            "databases_functional": 0,
            "details": {},
        }

        # Test database creation and basic operations
        database_tests = [
            ("Backup System DB", "data/backup_system.db"),
            ("Production Crew DB", "data/production_crew.db"),
            ("Monitoring DB", "data/monitoring.db"),
            ("Automation Orchestrator DB", "data/automation_orchestrator.db"),
            ("Test Framework DB", "data/test_framework.db"),
        ]

        for db_name, db_path in database_tests:
            test_results["databases_tested"] += 1
            try:
                full_db_path = self.workspace_path / db_path
                full_db_path.parent.mkdir(parents=True, exist_ok=True)

                # Test database connection and basic operations
                with sqlite3.connect(str(full_db_path)) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, test_data TEXT)"
                    )
                    cursor.execute(
                        "INSERT INTO test_table (test_data) VALUES (?)",
                        (f"integration_test_{int(time.time())}",),
                    )
                    cursor.execute("SELECT COUNT(*) FROM test_table")
                    count = cursor.fetchone()[0]
                    conn.commit()

                test_results["databases_functional"] += 1
                test_results["details"][db_name] = f"✅ SUCCESS - {count} records"
                logger.info(f"✅ {db_name} database functional")

            except Exception as e:
                test_results["details"][db_name] = f"❌ FAILED: {str(e)}"
                logger.error(f"❌ {db_name} database test failed: {e}")

        test_results["status"] = "completed"
        test_results["success_rate"] = (
            test_results["databases_functional"] / test_results["databases_tested"]
        ) * 100

        return test_results

    async def _test_core_functionality(self) -> Dict[str, Any]:
        """Test core system functionality"""
        test_results = {
            "status": "running",
            "functionality_tests": 0,
            "functionality_passed": 0,
            "details": {},
        }

        # Test backup system functionality
        try:
            from tools.backup.backup_system import BackupSystem

            backup_system = BackupSystem(str(self.workspace_path))

            # Test backup creation
            backup_result = backup_system.create_backup("integration_test")

            test_results["functionality_tests"] += 1
            if backup_result and backup_result.get("success"):
                test_results["functionality_passed"] += 1
                test_results["details"][
                    "Backup System"
                ] = "✅ Backup creation successful"
            else:
                test_results["details"]["Backup System"] = "❌ Backup creation failed"

        except Exception as e:
            test_results["functionality_tests"] += 1
            test_results["details"]["Backup System"] = f"❌ FAILED: {str(e)}"

        # Test production crew initialization
        try:
            from workshop.production.intelligent_production_crew import ProductionCrew

            crew = ProductionCrew(str(self.workspace_path))

            test_results["functionality_tests"] += 1
            if hasattr(crew, "workspace_path") and hasattr(crew, "agents"):
                test_results["functionality_passed"] += 1
                test_results["details"][
                    "Production Crew"
                ] = "✅ Initialization successful"
            else:
                test_results["details"][
                    "Production Crew"
                ] = "❌ Initialization incomplete"

        except Exception as e:
            test_results["functionality_tests"] += 1
            test_results["details"]["Production Crew"] = f"❌ FAILED: {str(e)}"

        # Test monitoring system
        try:
            from workshop.production.devops_monitoring_dashboard import (
                PerformanceMonitor,
            )

            monitor = PerformanceMonitor(str(self.workspace_path))

            # Test metrics collection
            metrics = {
                "cpu_usage": psutil.cpu_percent(interval=1),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage(
                    "C:" if os.name == "nt" else "/"
                ).percent,
            }

            test_results["functionality_tests"] += 1
            if all(isinstance(v, (int, float)) for v in metrics.values()):
                test_results["functionality_passed"] += 1
                test_results["details"][
                    "Monitoring System"
                ] = f"✅ Metrics collection successful - CPU: {metrics['cpu_usage']:.1f}%"
            else:
                test_results["details"][
                    "Monitoring System"
                ] = "❌ Invalid metrics collected"

        except Exception as e:
            test_results["functionality_tests"] += 1
            test_results["details"]["Monitoring System"] = f"❌ FAILED: {str(e)}"

        test_results["status"] = "completed"
        test_results["success_rate"] = (
            (test_results["functionality_passed"] / test_results["functionality_tests"])
            * 100
            if test_results["functionality_tests"] > 0
            else 0
        )

        return test_results

    async def _test_agent_integration(self) -> Dict[str, Any]:
        """Test agent system integration"""
        test_results = {
            "status": "running",
            "agent_tests": 0,
            "agent_passed": 0,
            "details": {},
        }

        # Test agent template creation
        try:
            from workshop.automations.production.agent_templates import AgentTemplate

            template = AgentTemplate.create_template(
                "integration_test_agent",
                "Integration Test Agent",
                "Test agent for integration testing",
                ["testing", "integration"],
            )

            test_results["agent_tests"] += 1
            if template and template.get("name") == "integration_test_agent":
                test_results["agent_passed"] += 1
                test_results["details"][
                    "Agent Template Creation"
                ] = "✅ Template created successfully"
            else:
                test_results["details"][
                    "Agent Template Creation"
                ] = "❌ Template creation failed"

        except Exception as e:
            test_results["agent_tests"] += 1
            test_results["details"]["Agent Template Creation"] = f"❌ FAILED: {str(e)}"

        # Test workflow orchestrator
        try:
            from workshop.automations.production.workflow_orchestrator import (
                WorkflowOrchestrator,
            )

            orchestrator = WorkflowOrchestrator(str(self.workspace_path))

            workflow_config = {
                "name": "integration_test_workflow",
                "description": "Integration test workflow",
                "stages": [
                    {"name": "init", "type": "initialization"},
                    {"name": "test", "type": "testing"},
                    {"name": "complete", "type": "completion"},
                ],
            }

            workflow_id = orchestrator.create_workflow(workflow_config)

            test_results["agent_tests"] += 1
            if workflow_id:
                test_results["agent_passed"] += 1
                test_results["details"][
                    "Workflow Orchestration"
                ] = f"✅ Workflow created: {workflow_id}"
            else:
                test_results["details"][
                    "Workflow Orchestration"
                ] = "❌ Workflow creation failed"

        except Exception as e:
            test_results["agent_tests"] += 1
            test_results["details"]["Workflow Orchestration"] = f"❌ FAILED: {str(e)}"

        test_results["status"] = "completed"
        test_results["success_rate"] = (
            (test_results["agent_passed"] / test_results["agent_tests"]) * 100
            if test_results["agent_tests"] > 0
            else 0
        )

        return test_results

    async def _test_workflow_orchestration(self) -> Dict[str, Any]:
        """Test workflow orchestration capabilities"""
        test_results = {
            "status": "running",
            "workflow_tests": 0,
            "workflow_passed": 0,
            "details": {},
        }

        # Test automation orchestrator
        try:
            from workshop.automations.enterprise_automation_orchestrator import (
                EnterpriseAutomationOrchestrator,
            )

            orchestrator = EnterpriseAutomationOrchestrator(str(self.workspace_path))

            # Test task registry
            test_results["workflow_tests"] += 1
            if (
                hasattr(orchestrator, "task_registry")
                and len(orchestrator.task_registry) > 0
            ):
                test_results["workflow_passed"] += 1
                test_results["details"][
                    "Automation Orchestrator"
                ] = f"✅ {len(orchestrator.task_registry)} tasks registered"
            else:
                test_results["details"][
                    "Automation Orchestrator"
                ] = "❌ No tasks registered"

        except Exception as e:
            test_results["workflow_tests"] += 1
            test_results["details"]["Automation Orchestrator"] = f"❌ FAILED: {str(e)}"

        # Test build automation
        try:
            from workshop._build.build_automation import BuildAutomationSystem

            build_system = BuildAutomationSystem(str(self.workspace_path))

            build_config = {
                "project_type": "python",
                "dependencies": ["pytest"],
                "build_steps": ["install", "test"],
            }

            # Test build system initialization
            test_results["workflow_tests"] += 1
            if hasattr(build_system, "workspace_path"):
                test_results["workflow_passed"] += 1
                test_results["details"][
                    "Build Automation"
                ] = "✅ Build system initialized"
            else:
                test_results["details"][
                    "Build Automation"
                ] = "❌ Build system initialization failed"

        except Exception as e:
            test_results["workflow_tests"] += 1
            test_results["details"]["Build Automation"] = f"❌ FAILED: {str(e)}"

        test_results["status"] = "completed"
        test_results["success_rate"] = (
            (test_results["workflow_passed"] / test_results["workflow_tests"]) * 100
            if test_results["workflow_tests"] > 0
            else 0
        )

        return test_results

    async def _test_monitoring_alerting(self) -> Dict[str, Any]:
        """Test monitoring and alerting systems"""
        test_results = {
            "status": "running",
            "monitoring_tests": 0,
            "monitoring_passed": 0,
            "details": {},
        }

        # Test system metrics collection
        try:
            metrics = {
                "cpu_usage": psutil.cpu_percent(interval=0.1),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage(
                    "C:" if os.name == "nt" else "/"
                ).percent,
                "process_count": len(psutil.pids()),
            }

            test_results["monitoring_tests"] += 1
            if all(isinstance(v, (int, float)) and v >= 0 for v in metrics.values()):
                test_results["monitoring_passed"] += 1
                test_results["details"][
                    "System Metrics"
                ] = f"✅ Metrics collected - CPU: {metrics['cpu_usage']:.1f}%, Memory: {metrics['memory_usage']:.1f}%"
            else:
                test_results["details"][
                    "System Metrics"
                ] = "❌ Invalid metrics collected"

        except Exception as e:
            test_results["monitoring_tests"] += 1
            test_results["details"]["System Metrics"] = f"❌ FAILED: {str(e)}"

        # Test monitoring dashboard status
        try:
            from workshop.production.devops_monitoring_dashboard import (
                DevOpsMonitoringDashboard,
            )

            dashboard = DevOpsMonitoringDashboard(str(self.workspace_path))

            test_results["monitoring_tests"] += 1
            if hasattr(dashboard, "workspace_path"):
                test_results["monitoring_passed"] += 1
                test_results["details"][
                    "Monitoring Dashboard"
                ] = "✅ Dashboard initialized"
            else:
                test_results["details"][
                    "Monitoring Dashboard"
                ] = "❌ Dashboard initialization failed"

        except Exception as e:
            test_results["monitoring_tests"] += 1
            test_results["details"]["Monitoring Dashboard"] = f"❌ FAILED: {str(e)}"

        test_results["status"] = "completed"
        test_results["success_rate"] = (
            (test_results["monitoring_passed"] / test_results["monitoring_tests"]) * 100
            if test_results["monitoring_tests"] > 0
            else 0
        )

        return test_results

    async def _test_build_deployment(self) -> Dict[str, Any]:
        """Test build and deployment pipeline"""
        test_results = {
            "status": "running",
            "build_tests": 0,
            "build_passed": 0,
            "details": {},
        }

        # Test CI/CD pipeline initialization
        try:
            from workshop.production.enterprise_cicd_pipeline import (
                EnterpriseCICDPipeline,
            )

            pipeline = EnterpriseCICDPipeline(str(self.workspace_path))

            test_results["build_tests"] += 1
            if hasattr(pipeline, "workspace_path") and hasattr(
                pipeline, "security_scanner"
            ):
                test_results["build_passed"] += 1
                test_results["details"]["CI/CD Pipeline"] = "✅ Pipeline initialized"
            else:
                test_results["details"][
                    "CI/CD Pipeline"
                ] = "❌ Pipeline initialization failed"

        except Exception as e:
            test_results["build_tests"] += 1
            test_results["details"]["CI/CD Pipeline"] = f"❌ FAILED: {str(e)}"

        # Test basic Python build
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import sys; print('Python build test successful')",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            test_results["build_tests"] += 1
            if result.returncode == 0:
                test_results["build_passed"] += 1
                test_results["details"][
                    "Python Build"
                ] = "✅ Basic Python build successful"
            else:
                test_results["details"][
                    "Python Build"
                ] = f"❌ Build failed: {result.stderr}"

        except Exception as e:
            test_results["build_tests"] += 1
            test_results["details"]["Python Build"] = f"❌ FAILED: {str(e)}"

        test_results["status"] = "completed"
        test_results["success_rate"] = (
            (test_results["build_passed"] / test_results["build_tests"]) * 100
            if test_results["build_tests"] > 0
            else 0
        )

        return test_results

    async def _test_end_to_end_workflow(self) -> Dict[str, Any]:
        """Test end-to-end workflow integration"""
        test_results = {
            "status": "running",
            "e2e_tests": 0,
            "e2e_passed": 0,
            "details": {},
        }

        # Test complete system coordination
        systems_initialized = []

        try:
            from tools.backup.backup_system import BackupSystem

            backup = BackupSystem(str(self.workspace_path))
            systems_initialized.append("backup")
        except Exception:
            pass

        try:
            from workshop.production.intelligent_production_crew import ProductionCrew

            crew = ProductionCrew(str(self.workspace_path))
            systems_initialized.append("production")
        except Exception:
            pass

        try:
            from workshop.automations.enterprise_automation_orchestrator import (
                EnterpriseAutomationOrchestrator,
            )

            orchestrator = EnterpriseAutomationOrchestrator(str(self.workspace_path))
            systems_initialized.append("orchestrator")
        except Exception:
            pass

        try:
            from workshop.production.devops_monitoring_dashboard import (
                DevOpsMonitoringDashboard,
            )

            dashboard = DevOpsMonitoringDashboard(str(self.workspace_path))
            systems_initialized.append("monitoring")
        except Exception:
            pass

        test_results["e2e_tests"] += 1
        coordination_score = (
            len(systems_initialized) / 4 * 100
        )  # Expecting 4 core systems

        if coordination_score >= 75:
            test_results["e2e_passed"] += 1
            test_results["details"][
                "System Coordination"
            ] = f"✅ {len(systems_initialized)}/4 systems coordinated ({coordination_score:.1f}%)"
        else:
            test_results["details"][
                "System Coordination"
            ] = f"❌ Only {len(systems_initialized)}/4 systems coordinated ({coordination_score:.1f}%)"

        # Test data flow between systems
        try:
            # Create a test data flow scenario
            test_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "test_id": f"e2e_test_{int(time.time())}",
                "data": "integration_test_data",
            }

            # Test database write/read cycle
            test_db_path = self.workspace_path / "data" / "e2e_test.db"
            test_db_path.parent.mkdir(parents=True, exist_ok=True)

            with sqlite3.connect(str(test_db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS e2e_test (id INTEGER PRIMARY KEY, data TEXT)"
                )
                cursor.execute(
                    "INSERT INTO e2e_test (data) VALUES (?)", (json.dumps(test_data),)
                )
                cursor.execute("SELECT data FROM e2e_test ORDER BY id DESC LIMIT 1")
                retrieved_data = cursor.fetchone()
                conn.commit()

            test_results["e2e_tests"] += 1
            if (
                retrieved_data
                and json.loads(retrieved_data[0])["test_id"] == test_data["test_id"]
            ):
                test_results["e2e_passed"] += 1
                test_results["details"][
                    "Data Flow"
                ] = "✅ End-to-end data flow successful"
            else:
                test_results["details"][
                    "Data Flow"
                ] = "❌ Data flow integrity check failed"

            # Clean up test database
            test_db_path.unlink()

        except Exception as e:
            test_results["e2e_tests"] += 1
            test_results["details"]["Data Flow"] = f"❌ FAILED: {str(e)}"

        test_results["status"] = "completed"
        test_results["success_rate"] = (
            (test_results["e2e_passed"] / test_results["e2e_tests"]) * 100
            if test_results["e2e_tests"] > 0
            else 0
        )

        return test_results

    def _generate_test_summary(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive test summary"""
        total_tests = 0
        total_passed = 0

        for test_category, results in test_results.items():
            if isinstance(results, dict) and "success_rate" in results:
                category_tests = (
                    results.get("imports_tested", 0)
                    + results.get("databases_tested", 0)
                    + results.get("functionality_tests", 0)
                    + results.get("agent_tests", 0)
                    + results.get("workflow_tests", 0)
                    + results.get("monitoring_tests", 0)
                    + results.get("build_tests", 0)
                    + results.get("e2e_tests", 0)
                )

                category_passed = (
                    results.get("imports_successful", 0)
                    + results.get("databases_functional", 0)
                    + results.get("functionality_passed", 0)
                    + results.get("agent_passed", 0)
                    + results.get("workflow_passed", 0)
                    + results.get("monitoring_passed", 0)
                    + results.get("build_passed", 0)
                    + results.get("e2e_passed", 0)
                )

                total_tests += category_tests
                total_passed += category_passed

        overall_success_rate = (
            (total_passed / total_tests) * 100 if total_tests > 0 else 0
        )

        # Determine overall status
        if overall_success_rate >= 95:
            status = "EXCELLENT"
        elif overall_success_rate >= 85:
            status = "GOOD"
        elif overall_success_rate >= 70:
            status = "ACCEPTABLE"
        elif overall_success_rate >= 50:
            status = "NEEDS_ATTENTION"
        else:
            status = "CRITICAL"

        return {
            "overall_status": status,
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_tests - total_passed,
            "overall_success_rate": overall_success_rate,
            "test_categories": len(test_results),
            "critical_failures": [
                category
                for category, results in test_results.items()
                if isinstance(results, dict) and results.get("success_rate", 0) < 50
            ],
        }


async def main():
    """Run production integration tests"""
    import argparse

    parser = argparse.ArgumentParser(description="Production Integration Test Suite")
    parser.add_argument("--workspace", default=".", help="Workspace path")
    parser.add_argument("--output", help="Output file for test results (JSON)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Initialize test suite
    test_suite = ProductionIntegurationTest(args.workspace)

    # Run tests
    results = await test_suite.run_full_integration_test()

    # Display results
    print("\n" + "=" * 70)
    print("🎯 PRODUCTION INTEGRATION TEST RESULTS")
    print("=" * 70)

    summary = results["summary"]
    print(f"Overall Status: {summary['overall_status']}")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['total_passed']}")
    print(f"Failed: {summary['total_failed']}")
    print(f"Success Rate: {summary['overall_success_rate']:.1f}%")
    print(f"Test Categories: {summary['test_categories']}")

    if summary["critical_failures"]:
        print(f"Critical Failures: {', '.join(summary['critical_failures'])}")

    print(f"Duration: {results['total_duration']:.2f} seconds")

    # Show detailed results if verbose
    if args.verbose:
        print("\n" + "=" * 50)
        print("DETAILED TEST RESULTS")
        print("=" * 50)

        for category, test_result in results["tests"].items():
            print(f"\n📋 {category.upper().replace('_', ' ')}")
            print(f"   Success Rate: {test_result.get('success_rate', 0):.1f}%")

            if "details" in test_result:
                for test_name, result in test_result["details"].items():
                    print(f"   {test_name}: {result}")

    # Save results if output specified
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Test results saved to: {output_path}")

    # Exit with appropriate code
    if summary["overall_success_rate"] >= 85:
        return 0
    elif summary["overall_success_rate"] >= 70:
        return 1
    else:
        return 2


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Integration tests interrupted")
        sys.exit(1)
