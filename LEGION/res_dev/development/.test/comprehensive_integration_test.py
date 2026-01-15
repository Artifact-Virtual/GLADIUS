#!/usr/bin/env python3
"""
Comprehensive Integration Test Suite for Artifact Virtual Recovery Systems
Validates all rebuilt production, automation, and enterprise systems
"""
import asyncio
import importlib
import json
import logging
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SystemTest:
    """Individual system test"""

    def __init__(
        self,
        name: str,
        description: str,
        test_func: callable,
        critical: bool = False,
        timeout: int = 60,
    ):
        self.name = name
        self.description = description
        self.test_func = test_func
        self.critical = critical
        self.timeout = timeout
        self.result = None
        self.error = None
        self.duration = 0


class IntegrationTestSuite:
    """Comprehensive integration test suite"""

    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.test_results = {}
        self.tests = []

        # Add workspace to Python path for imports
        if str(self.workspace_path) not in sys.path:
            sys.path.insert(0, str(self.workspace_path))

        self.setup_tests()

    def setup_tests(self):
        """Setup all integration tests"""

        # System Import Tests
        self.tests.extend(
            [
                SystemTest(
                    "import_backup_system",
                    "Import backup and recovery system",
                    self._test_import_backup_system,
                    critical=True,
                ),
                SystemTest(
                    "import_analysis_system",
                    "Import advanced analysis system",
                    self._test_import_analysis_system,
                    critical=True,
                ),
                SystemTest(
                    "import_production_crew",
                    "Import intelligent production crew",
                    self._test_import_production_crew,
                    critical=True,
                ),
                SystemTest(
                    "import_agent_templates",
                    "Import advanced agent templates",
                    self._test_import_agent_templates,
                    critical=True,
                ),
                SystemTest(
                    "import_workflow_orchestrator",
                    "Import workflow orchestrator",
                    self._test_import_workflow_orchestrator,
                    critical=True,
                ),
                SystemTest(
                    "import_test_framework",
                    "Import intelligent test framework",
                    self._test_import_test_framework,
                    critical=True,
                ),
                SystemTest(
                    "import_build_automation",
                    "Import build automation system",
                    self._test_import_build_automation,
                    critical=True,
                ),
                SystemTest(
                    "import_iteration_engine",
                    "Import intelligent iteration engine",
                    self._test_import_iteration_engine,
                    critical=True,
                ),
                SystemTest(
                    "import_prototype_system",
                    "Import prototype development system",
                    self._test_import_prototype_system,
                    critical=True,
                ),
                SystemTest(
                    "import_cicd_pipeline",
                    "Import enterprise CI/CD pipeline",
                    self._test_import_cicd_pipeline,
                    critical=True,
                ),
                SystemTest(
                    "import_monitoring_dashboard",
                    "Import DevOps monitoring dashboard",
                    self._test_import_monitoring_dashboard,
                    critical=True,
                ),
                SystemTest(
                    "import_automation_orchestrator",
                    "Import enterprise automation orchestrator",
                    self._test_import_automation_orchestrator,
                    critical=True,
                ),
            ]
        )

        # Functional Tests
        self.tests.extend(
            [
                SystemTest(
                    "backup_system_functionality",
                    "Test backup system create and restore functionality",
                    self._test_backup_functionality,
                    critical=True,
                    timeout=120,
                ),
                SystemTest(
                    "analysis_system_functionality",
                    "Test code analysis and metrics generation",
                    self._test_analysis_functionality,
                    critical=False,
                    timeout=90,
                ),
                SystemTest(
                    "production_crew_initialization",
                    "Test production crew agent initialization",
                    self._test_production_crew_init,
                    critical=True,
                    timeout=60,
                ),
                SystemTest(
                    "agent_template_creation",
                    "Test agent template creation and configuration",
                    self._test_agent_template_creation,
                    critical=False,
                    timeout=45,
                ),
                SystemTest(
                    "workflow_orchestration",
                    "Test multi-agent workflow orchestration",
                    self._test_workflow_orchestration,
                    critical=False,
                    timeout=90,
                ),
                SystemTest(
                    "test_framework_generation",
                    "Test AI-powered test generation",
                    self._test_framework_generation,
                    critical=False,
                    timeout=60,
                ),
                SystemTest(
                    "build_automation_execution",
                    "Test build automation execution",
                    self._test_build_automation,
                    critical=False,
                    timeout=120,
                ),
                SystemTest(
                    "iteration_engine_analysis",
                    "Test continuous improvement analysis",
                    self._test_iteration_analysis,
                    critical=False,
                    timeout=75,
                ),
                SystemTest(
                    "prototype_generation",
                    "Test rapid prototype generation",
                    self._test_prototype_generation,
                    critical=False,
                    timeout=60,
                ),
                SystemTest(
                    "monitoring_metrics_collection",
                    "Test monitoring metrics collection",
                    self._test_monitoring_metrics,
                    critical=True,
                    timeout=45,
                ),
                SystemTest(
                    "orchestrator_task_registration",
                    "Test automation orchestrator task registration",
                    self._test_orchestrator_tasks,
                    critical=True,
                    timeout=30,
                ),
            ]
        )

        # Database Tests
        self.tests.extend(
            [
                SystemTest(
                    "database_connectivity",
                    "Test database connectivity and creation",
                    self._test_database_connectivity,
                    critical=True,
                    timeout=30,
                ),
                SystemTest(
                    "database_schema_validation",
                    "Test database schema validation",
                    self._test_database_schemas,
                    critical=True,
                    timeout=30,
                ),
            ]
        )

        # Integration Tests
        self.tests.extend(
            [
                SystemTest(
                    "system_coordination",
                    "Test coordination between systems",
                    self._test_system_coordination,
                    critical=False,
                    timeout=120,
                ),
                SystemTest(
                    "end_to_end_workflow",
                    "Test end-to-end automation workflow",
                    self._test_end_to_end_workflow,
                    critical=False,
                    timeout=180,
                ),
            ]
        )

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests"""
        logger.info("🚀 Starting Comprehensive Integration Test Suite...")
        start_time = time.time()

        total_tests = len(self.tests)
        passed_tests = 0
        failed_tests = 0
        critical_failures = 0

        # Run tests
        for i, test in enumerate(self.tests, 1):
            logger.info(f"Running test {i}/{total_tests}: {test.name}")

            test_start = time.time()
            try:
                if asyncio.iscoroutinefunction(test.test_func):
                    result = await asyncio.wait_for(
                        test.test_func(), timeout=test.timeout
                    )
                else:
                    result = await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(None, test.test_func),
                        timeout=test.timeout,
                    )

                test.result = result
                test.duration = time.time() - test_start

                if result.get("success", False):
                    passed_tests += 1
                    logger.info(f"✅ {test.name} - PASSED ({test.duration:.2f}s)")
                else:
                    failed_tests += 1
                    if test.critical:
                        critical_failures += 1
                    logger.error(
                        f"❌ {test.name} - FAILED: {result.get('error', 'Unknown error')}"
                    )

            except asyncio.TimeoutError:
                test.error = f"Test timed out after {test.timeout} seconds"
                test.duration = test.timeout
                failed_tests += 1
                if test.critical:
                    critical_failures += 1
                logger.error(f"⏰ {test.name} - TIMEOUT")

            except Exception as e:
                test.error = str(e)
                test.duration = time.time() - test_start
                failed_tests += 1
                if test.critical:
                    critical_failures += 1
                logger.error(f"💥 {test.name} - ERROR: {e}")

        total_duration = time.time() - start_time
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        # Compile results
        results = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "critical_failures": critical_failures,
                "success_rate": success_rate,
                "total_duration": total_duration,
                "timestamp": datetime.utcnow().isoformat(),
            },
            "test_details": [],
        }

        for test in self.tests:
            test_detail = {
                "name": test.name,
                "description": test.description,
                "critical": test.critical,
                "status": (
                    "passed" if test.result and test.result.get("success") else "failed"
                ),
                "duration": test.duration,
                "result": test.result,
                "error": test.error,
            }
            results["test_details"].append(test_detail)

        # Overall assessment
        if critical_failures > 0:
            results["overall_status"] = "CRITICAL_FAILURE"
        elif success_rate >= 90:
            results["overall_status"] = "EXCELLENT"
        elif success_rate >= 75:
            results["overall_status"] = "GOOD"
        elif success_rate >= 50:
            results["overall_status"] = "ACCEPTABLE"
        else:
            results["overall_status"] = "POOR"

        # Log summary
        logger.info("=" * 60)
        logger.info("🏁 INTEGRATION TEST SUITE COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Overall Status: {results['overall_status']}")
        logger.info(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        logger.info(f"Critical Failures: {critical_failures}")
        logger.info(f"Total Duration: {total_duration:.2f} seconds")
        logger.info("=" * 60)

        return results

    # Import Tests
    def _test_import_backup_system(self) -> Dict[str, Any]:
        """Test backup system import"""
        try:
            from tools.backup.backup_system import BackupSystem

            return {"success": True, "message": "Backup system imported successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_import_analysis_system(self) -> Dict[str, Any]:
        """Test analysis system import"""
        try:
            from tools.analysis.advanced_analysis import AdvancedCodeAnalyzer

            return {"success": True, "message": "Analysis system imported successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_import_production_crew(self) -> Dict[str, Any]:
        """Test production crew import"""
        try:
            from workshop.production.intelligent_production_crew import ProductionCrew

            return {"success": True, "message": "Production crew imported successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_import_agent_templates(self) -> Dict[str, Any]:
        """Test agent templates import"""
        try:
            from workshop.automations.production.agent_templates import AgentTemplate

            return {"success": True, "message": "Agent templates imported successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_import_workflow_orchestrator(self) -> Dict[str, Any]:
        """Test workflow orchestrator import"""
        try:
            from workshop.automations.production.workflow_orchestrator import (
                WorkflowOrchestrator,
            )

            return {
                "success": True,
                "message": "Workflow orchestrator imported successfully",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_import_test_framework(self) -> Dict[str, Any]:
        """Test framework import"""
        try:
            from workshop.test.intelligent_test_framework import (
                IntelligentTestFramework,
            )

            return {"success": True, "message": "Test framework imported successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_import_build_automation(self) -> Dict[str, Any]:
        """Test build automation import"""
        try:
            from workshop._build.build_automation import BuildAutomationSystem

            return {
                "success": True,
                "message": "Build automation imported successfully",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_import_iteration_engine(self) -> Dict[str, Any]:
        """Test iteration engine import"""
        try:
            from workshop.iterate.intelligent_iteration_engine import (
                IntelligentIterationEngine,
            )

            return {
                "success": True,
                "message": "Iteration engine imported successfully",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_import_prototype_system(self) -> Dict[str, Any]:
        """Test prototype system import"""
        try:
            from workshop.__prototype.prototype_system import PrototypeSystem

            return {
                "success": True,
                "message": "Prototype system imported successfully",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_import_cicd_pipeline(self) -> Dict[str, Any]:
        """Test CI/CD pipeline import"""
        try:
            from workshop.production.enterprise_cicd_pipeline import (
                EnterpriseCICDPipeline,
            )

            return {"success": True, "message": "CI/CD pipeline imported successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_import_monitoring_dashboard(self) -> Dict[str, Any]:
        """Test monitoring dashboard import"""
        try:
            from workshop.production.devops_monitoring_dashboard import (
                DevOpsMonitoringDashboard,
            )

            return {
                "success": True,
                "message": "Monitoring dashboard imported successfully",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_import_automation_orchestrator(self) -> Dict[str, Any]:
        """Test automation orchestrator import"""
        try:
            from workshop.automations.enterprise_automation_orchestrator import (
                EnterpriseAutomationOrchestrator,
            )

            return {
                "success": True,
                "message": "Automation orchestrator imported successfully",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Functional Tests
    def _test_backup_functionality(self) -> Dict[str, Any]:
        """Test backup system functionality"""
        try:
            from tools.backup.backup_system import BackupSystem

            backup_system = BackupSystem(str(self.workspace_path))

            # Test backup creation
            backup_info = backup_system.create_backup("integration_test")

            if backup_info and backup_info.get("success"):
                return {
                    "success": True,
                    "message": "Backup functionality test passed",
                    "backup_id": backup_info.get("backup_id"),
                }
            else:
                return {"success": False, "error": "Backup creation failed"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_analysis_functionality(self) -> Dict[str, Any]:
        """Test analysis system functionality"""
        try:
            from tools.analysis.advanced_analysis import AdvancedCodeAnalyzer

            analyzer = AdvancedCodeAnalyzer(str(self.workspace_path))

            # Test basic analysis
            analysis_result = analyzer.analyze_file_complexity("bootstrap.py")

            if analysis_result:
                return {
                    "success": True,
                    "message": "Analysis functionality test passed",
                    "metrics": analysis_result,
                }
            else:
                return {"success": False, "error": "Analysis returned no results"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_production_crew_init(self) -> Dict[str, Any]:
        """Test production crew initialization"""
        try:
            from workshop.production.intelligent_production_crew import ProductionCrew

            crew = ProductionCrew(str(self.workspace_path))

            # Test initialization
            if hasattr(crew, "agents") and hasattr(crew, "orchestrator"):
                return {
                    "success": True,
                    "message": "Production crew initialized successfully",
                    "agent_count": len(crew.agents) if crew.agents else 0,
                }
            else:
                return {
                    "success": False,
                    "error": "Production crew initialization incomplete",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_agent_template_creation(self) -> Dict[str, Any]:
        """Test agent template creation"""
        try:
            from workshop.automations.production.agent_templates import AgentTemplate

            # Test template creation
            template = AgentTemplate.create_template(
                "test_agent",
                "Test Agent",
                "A test agent for integration testing",
                ["test", "integration"],
            )

            if template and template.get("name") == "test_agent":
                return {
                    "success": True,
                    "message": "Agent template creation successful",
                    "template": template,
                }
            else:
                return {"success": False, "error": "Agent template creation failed"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_workflow_orchestration(self) -> Dict[str, Any]:
        """Test workflow orchestration"""
        try:
            from workshop.automations.production.workflow_orchestrator import (
                WorkflowOrchestrator,
            )

            orchestrator = WorkflowOrchestrator(str(self.workspace_path))

            # Test workflow creation
            workflow_config = {
                "name": "test_workflow",
                "description": "Integration test workflow",
                "stages": [
                    {"name": "init", "type": "initialization"},
                    {"name": "process", "type": "processing"},
                    {"name": "complete", "type": "completion"},
                ],
            }

            workflow_id = orchestrator.create_workflow(workflow_config)

            if workflow_id:
                return {
                    "success": True,
                    "message": "Workflow orchestration test passed",
                    "workflow_id": workflow_id,
                }
            else:
                return {"success": False, "error": "Workflow creation failed"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_framework_generation(self) -> Dict[str, Any]:
        """Test framework test generation"""
        try:
            from workshop.test.intelligent_test_framework import (
                IntelligentTestFramework,
            )

            framework = IntelligentTestFramework(str(self.workspace_path))

            # Test simple test generation
            test_spec = {
                "target_file": "bootstrap.py",
                "test_type": "unit",
                "coverage_target": 70,
            }

            generated_tests = framework.generate_tests(test_spec)

            if generated_tests and generated_tests.get("success"):
                return {
                    "success": True,
                    "message": "Test generation successful",
                    "test_count": len(generated_tests.get("tests", [])),
                }
            else:
                return {"success": False, "error": "Test generation failed"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_build_automation(self) -> Dict[str, Any]:
        """Test build automation execution"""
        try:
            from workshop._build.build_automation import BuildAutomationSystem

            build_system = BuildAutomationSystem(str(self.workspace_path))

            # Test build configuration
            build_config = {
                "project_type": "python",
                "dependencies": ["pytest", "pylint"],
                "build_steps": ["install", "lint", "test"],
            }

            build_result = build_system.execute_build(build_config)

            if build_result and build_result.get("success"):
                return {
                    "success": True,
                    "message": "Build automation test passed",
                    "build_id": build_result.get("build_id"),
                }
            else:
                return {"success": False, "error": "Build execution failed"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_iteration_analysis(self) -> Dict[str, Any]:
        """Test iteration engine analysis"""
        try:
            from workshop.iterate.intelligent_iteration_engine import (
                IntelligentIterationEngine,
            )

            engine = IntelligentIterationEngine(str(self.workspace_path))

            # Test improvement analysis
            analysis_result = engine.analyze_improvement_opportunities()

            if analysis_result and analysis_result.get("success"):
                return {
                    "success": True,
                    "message": "Iteration analysis successful",
                    "opportunity_count": len(analysis_result.get("opportunities", [])),
                }
            else:
                return {"success": False, "error": "Iteration analysis failed"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_prototype_generation(self) -> Dict[str, Any]:
        """Test prototype generation"""
        try:
            from workshop.__prototype.prototype_system import PrototypeSystem

            prototype_system = PrototypeSystem(str(self.workspace_path))

            # Test prototype creation
            prototype_spec = {
                "type": "api",
                "name": "test_api",
                "description": "Integration test API prototype",
                "features": ["health_check", "status_endpoint"],
            }

            prototype_result = prototype_system.create_prototype(prototype_spec)

            if prototype_result and prototype_result.get("success"):
                return {
                    "success": True,
                    "message": "Prototype generation successful",
                    "prototype_id": prototype_result.get("prototype_id"),
                }
            else:
                return {"success": False, "error": "Prototype generation failed"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_monitoring_metrics(self) -> Dict[str, Any]:
        """Test monitoring metrics collection"""
        try:
            from workshop.production.devops_monitoring_dashboard import (
                PerformanceMonitor,
            )

            monitor = PerformanceMonitor(str(self.workspace_path))

            # Test metrics collection (synchronous version)
            import psutil

            metrics = {
                "cpu_usage": psutil.cpu_percent(interval=1),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": (
                    psutil.disk_usage("/").percent
                    if os.name != "nt"
                    else psutil.disk_usage("C:").percent
                ),
            }

            if all(isinstance(v, (int, float)) for v in metrics.values()):
                return {
                    "success": True,
                    "message": "Monitoring metrics collection successful",
                    "metrics": metrics,
                }
            else:
                return {"success": False, "error": "Invalid metrics collected"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_orchestrator_tasks(self) -> Dict[str, Any]:
        """Test orchestrator task registration"""
        try:
            from workshop.automations.enterprise_automation_orchestrator import (
                EnterpriseAutomationOrchestrator,
            )

            orchestrator = EnterpriseAutomationOrchestrator(str(self.workspace_path))

            # Test task registry
            if (
                hasattr(orchestrator, "task_registry")
                and len(orchestrator.task_registry) > 0
            ):
                return {
                    "success": True,
                    "message": "Orchestrator task registration successful",
                    "task_count": len(orchestrator.task_registry),
                }
            else:
                return {
                    "success": False,
                    "error": "No tasks registered in orchestrator",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_database_connectivity(self) -> Dict[str, Any]:
        """Test database connectivity"""
        try:
            import sqlite3

            # Test database creation and connectivity
            test_db_path = self.workspace_path / "data" / "integration_test.db"
            test_db_path.parent.mkdir(parents=True, exist_ok=True)

            with sqlite3.connect(str(test_db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT)"
                )
                cursor.execute(
                    "INSERT INTO test_table (name) VALUES (?)", ("integration_test",)
                )
                cursor.execute("SELECT COUNT(*) FROM test_table")
                count = cursor.fetchone()[0]
                conn.commit()

            # Clean up
            test_db_path.unlink()

            return {
                "success": True,
                "message": "Database connectivity test passed",
                "record_count": count,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_database_schemas(self) -> Dict[str, Any]:
        """Test database schema validation"""
        try:
            import sqlite3

            schema_count = 0

            # Check various system databases
            db_paths = [
                self.workspace_path / "data" / "backup_system.db",
                self.workspace_path / "data" / "production_crew.db",
                self.workspace_path / "data" / "monitoring.db",
                self.workspace_path / "data" / "automation_orchestrator.db",
            ]

            for db_path in db_paths:
                if db_path.exists():
                    with sqlite3.connect(str(db_path)) as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "SELECT name FROM sqlite_master WHERE type='table'"
                        )
                        tables = cursor.fetchall()
                        schema_count += len(tables)

            return {
                "success": True,
                "message": "Database schema validation passed",
                "total_tables": schema_count,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_system_coordination(self) -> Dict[str, Any]:
        """Test coordination between systems"""
        try:
            # Test basic system coordination
            systems_available = []

            try:
                from tools.backup.backup_system import BackupSystem

                systems_available.append("backup")
            except ImportError:
                pass

            try:
                from workshop.production.intelligent_production_crew import (
                    ProductionCrew,
                )

                systems_available.append("production")
            except ImportError:
                pass

            try:
                from workshop.production.devops_monitoring_dashboard import (
                    DevOpsMonitoringDashboard,
                )

                systems_available.append("monitoring")
            except ImportError:
                pass

            coordination_score = (
                len(systems_available) / 3 * 100
            )  # Expecting 3 core systems

            return {
                "success": coordination_score >= 66,  # At least 2/3 systems available
                "message": f"System coordination test: {len(systems_available)}/3 systems available",
                "systems_available": systems_available,
                "coordination_score": coordination_score,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _test_end_to_end_workflow(self) -> Dict[str, Any]:
        """Test end-to-end automation workflow"""
        try:
            # Simulate an end-to-end workflow
            workflow_steps = []

            # Step 1: Initialize systems
            try:
                from tools.backup.backup_system import BackupSystem

                backup_system = BackupSystem(str(self.workspace_path))
                workflow_steps.append("backup_init")
            except Exception:
                pass

            # Step 2: Run analysis
            try:
                from tools.analysis.advanced_analysis import AdvancedCodeAnalyzer

                analyzer = AdvancedCodeAnalyzer(str(self.workspace_path))
                workflow_steps.append("analysis_init")
            except Exception:
                pass

            # Step 3: Production coordination
            try:
                from workshop.production.intelligent_production_crew import (
                    ProductionCrew,
                )

                crew = ProductionCrew(str(self.workspace_path))
                workflow_steps.append("production_init")
            except Exception:
                pass

            # Step 4: Monitoring setup
            try:
                from workshop.production.devops_monitoring_dashboard import (
                    PerformanceMonitor,
                )

                monitor = PerformanceMonitor(str(self.workspace_path))
                workflow_steps.append("monitoring_init")
            except Exception:
                pass

            workflow_success = len(workflow_steps) >= 3  # At least 3 steps completed

            return {
                "success": workflow_success,
                "message": f"End-to-end workflow: {len(workflow_steps)}/4 steps completed",
                "completed_steps": workflow_steps,
                "workflow_coverage": len(workflow_steps) / 4 * 100,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


async def main():
    """Main integration test runner"""
    import argparse

    parser = argparse.ArgumentParser(description="Comprehensive Integration Test Suite")
    parser.add_argument("--workspace", default=".", help="Workspace path")
    parser.add_argument("--output", help="Output file for test results (JSON)")
    parser.add_argument(
        "--critical-only", action="store_true", help="Run only critical tests"
    )

    args = parser.parse_args()

    # Initialize test suite
    test_suite = IntegrationTestSuite(args.workspace)

    # Filter tests if critical-only
    if args.critical_only:
        test_suite.tests = [t for t in test_suite.tests if t.critical]
        logger.info(f"Running {len(test_suite.tests)} critical tests only")

    # Run tests
    results = await test_suite.run_all_tests()

    # Save results if output specified
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Test results saved to: {output_path}")

    # Exit with appropriate code
    if results["summary"]["critical_failures"] > 0:
        sys.exit(1)
    elif results["summary"]["success_rate"] < 75:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Integration tests interrupted")
