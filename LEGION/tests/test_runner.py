#!/usr/bin/env python3
"""
Legion Enterprise Dashboard - Phase 6 Testing & Validation
Test Runner and Coordination System

This is the central test orchestration system that manages:
- Component Testing (21.1-21.8)
- Integration Testing (22.1-22.8) 
- Performance Testing (23.1-23.8)

Comprehensive testing framework for enterprise dashboard validation.
"""

import sys
import os
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enterprise_database_service import EnterpriseDatabase
import sqlite3

@dataclass
class TestResult:
    """Test result data structure"""
    test_id: str
    test_name: str
    category: str
    status: str  # 'passed', 'failed', 'skipped', 'running'
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    error_message: Optional[str] = None
    details: Dict[str, Any] = None
    severity: str = 'info'  # 'critical', 'high', 'medium', 'low', 'info'

    def __post_init__(self):
        if self.details is None:
            self.details = {}

@dataclass
class TestSuite:
    """Test suite configuration"""
    suite_name: str
    tests: List[str]
    dependencies: List[str] = None
    timeout: int = 300  # 5 minutes default
    parallel: bool = False

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class TestRunner:
    """
    Comprehensive test runner for Legion Enterprise Dashboard
    
    Manages all Phase 6 testing categories:
    - Component Testing (Individual component validation)
    - Integration Testing (System integration validation)
    - Performance Testing (Performance and load validation)
    """
    
    def __init__(self):
        self.db = EnterpriseDatabase()
        self.test_results: List[TestResult] = []
        self.start_time = time.time()
        
        # Test configuration
        self.test_suites = {
            # Component Testing Suite (21.1-21.8)
            'component_testing': TestSuite(
                suite_name="Component Testing",
                tests=[
                    'test_dashboard_components',
                    'test_data_connections',
                    'test_error_handling',
                    'test_responsive_design',
                    'test_accessibility',
                    'test_large_datasets',
                    'test_concurrent_users',
                    'test_data_accuracy'
                ],
                parallel=True,
                timeout=600
            ),
            
            # Integration Testing Suite (22.1-22.8)
            'integration_testing': TestSuite(
                suite_name="Integration Testing",
                tests=[
                    'test_database_integration',
                    'test_agent_communication',
                    'test_workflow_orchestration',
                    'test_system_metrics',
                    'test_api_monitoring',
                    'test_realtime_streaming',
                    'test_optimization_features',
                    'test_business_intelligence'
                ],
                dependencies=['component_testing'],
                parallel=False,
                timeout=900
            ),
            
            # Performance Testing Suite (23.1-23.8)
            'performance_testing': TestSuite(
                suite_name="Performance Testing",
                tests=[
                    'test_dashboard_load_times',
                    'test_system_performance',
                    'test_memory_usage',
                    'test_network_efficiency',
                    'test_realtime_performance',
                    'test_database_optimization',
                    'test_caching_effectiveness',
                    'test_agent_scalability'
                ],
                dependencies=['component_testing', 'integration_testing'],
                parallel=True,
                timeout=1200
            )
        }
        
        # Create test results table
        self.initialize_test_database()
    
    def initialize_test_database(self):
        """Initialize test results database"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id TEXT NOT NULL,
                    test_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    status TEXT NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL,
                    duration REAL,
                    error_message TEXT,
                    details TEXT,
                    severity TEXT DEFAULT 'info',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL,
                    total_tests INTEGER DEFAULT 0,
                    passed_tests INTEGER DEFAULT 0,
                    failed_tests INTEGER DEFAULT 0,
                    skipped_tests INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            print("✅ Test database initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing test database: {e}")
    
    def record_test_result(self, result: TestResult):
        """Record test result to database"""
        try:
            self.test_results.append(result)
            
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO test_results 
                (test_id, test_name, category, status, start_time, end_time, duration, 
                 error_message, details, severity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.test_id,
                result.test_name,
                result.category,
                result.status,
                result.start_time,
                result.end_time,
                result.duration,
                result.error_message,
                json.dumps(result.details) if result.details else None,
                result.severity
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error recording test result: {e}")
    
    async def run_test_suite(self, suite_name: str) -> Dict[str, Any]:
        """Run a complete test suite"""
        if suite_name not in self.test_suites:
            raise ValueError(f"Unknown test suite: {suite_name}")
        
        suite = self.test_suites[suite_name]
        print(f"\n🚀 Starting {suite.suite_name}")
        print(f"📋 Tests: {len(suite.tests)}")
        print(f"⏱️  Timeout: {suite.timeout}s")
        print(f"🔄 Parallel: {suite.parallel}")
        
        suite_start = time.time()
        suite_results = []
        
        if suite.parallel:
            # Run tests in parallel
            tasks = []
            for test_name in suite.tests:
                task = asyncio.create_task(self.run_individual_test(test_name, suite_name))
                tasks.append(task)
            
            suite_results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # Run tests sequentially
            for test_name in suite.tests:
                result = await self.run_individual_test(test_name, suite_name)
                suite_results.append(result)
        
        suite_end = time.time()
        suite_duration = suite_end - suite_start
        
        # Analyze suite results
        passed = sum(1 for r in suite_results if isinstance(r, TestResult) and r.status == 'passed')
        failed = sum(1 for r in suite_results if isinstance(r, TestResult) and r.status == 'failed')
        skipped = sum(1 for r in suite_results if isinstance(r, TestResult) and r.status == 'skipped')
        
        success_rate = (passed / len(suite.tests)) * 100 if suite.tests else 0
        
        print(f"\n📊 {suite.suite_name} Results:")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   ⏭️  Skipped: {skipped}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        print(f"   ⏱️  Duration: {suite_duration:.2f}s")
        
        return {
            'suite_name': suite_name,
            'results': suite_results,
            'summary': {
                'total': len(suite.tests),
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'success_rate': success_rate,
                'duration': suite_duration
            }
        }
    
    async def run_individual_test(self, test_name: str, category: str) -> TestResult:
        """Run an individual test"""
        test_id = f"{category}_{test_name}_{int(time.time())}"
        start_time = time.time()
        
        print(f"  🔍 Running {test_name}...")
        
        try:
            # Map test names to test methods
            test_method = getattr(self, test_name)
            result = await test_method()
            
            end_time = time.time()
            duration = end_time - start_time
            
            test_result = TestResult(
                test_id=test_id,
                test_name=test_name,
                category=category,
                status='passed' if result['success'] else 'failed',
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                error_message=result.get('error'),
                details=result.get('details', {}),
                severity=result.get('severity', 'info')
            )
            
            self.record_test_result(test_result)
            
            if test_result.status == 'passed':
                print(f"    ✅ {test_name} - PASSED ({duration:.2f}s)")
            else:
                print(f"    ❌ {test_name} - FAILED ({duration:.2f}s)")
                if test_result.error_message:
                    print(f"       Error: {test_result.error_message}")
            
            return test_result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            test_result = TestResult(
                test_id=test_id,
                test_name=test_name,
                category=category,
                status='failed',
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                error_message=str(e),
                severity='high'
            )
            
            self.record_test_result(test_result)
            print(f"    ❌ {test_name} - FAILED ({duration:.2f}s) - {str(e)}")
            
            return test_result
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.status == 'passed')
        failed = sum(1 for r in self.test_results if r.status == 'failed')
        skipped = sum(1 for r in self.test_results if r.status == 'skipped')
        
        success_rate = (passed / total_tests) * 100 if total_tests > 0 else 0
        total_duration = time.time() - self.start_time
        
        # Group results by category
        by_category = {}
        for result in self.test_results:
            if result.category not in by_category:
                by_category[result.category] = []
            by_category[result.category].append(result)
        
        return {
            'summary': {
                'total_tests': total_tests,
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'success_rate': success_rate,
                'total_duration': total_duration,
                'timestamp': datetime.now().isoformat()
            },
            'by_category': by_category,
            'failed_tests': [r for r in self.test_results if r.status == 'failed'],
            'all_results': self.test_results
        }

# Import test implementations
from tests.component_tests import ComponentTests
from tests.integration_tests import IntegrationTests  
from tests.performance_tests import PerformanceTests

# Mixin the test implementations
class CompleteTestRunner(TestRunner, ComponentTests, IntegrationTests, PerformanceTests):
    """Complete test runner with all test implementations"""
    pass

async def main():
    """Main test execution"""
    print("🏁 Legion Enterprise Dashboard - Phase 6 Testing & Validation")
    print("=" * 70)
    
    runner = CompleteTestRunner()
    
    # Run all test suites
    all_results = {}
    
    try:
        # Component Testing (21.1-21.8)
        print("\n" + "=" * 70)
        print("📋 PHASE 6.1: COMPONENT TESTING")
        print("=" * 70)
        component_results = await runner.run_test_suite('component_testing')
        all_results['component_testing'] = component_results
        
        # Integration Testing (22.1-22.8) 
        print("\n" + "=" * 70)
        print("📋 PHASE 6.2: INTEGRATION TESTING")
        print("=" * 70)
        integration_results = await runner.run_test_suite('integration_testing')
        all_results['integration_testing'] = integration_results
        
        # Performance Testing (23.1-23.8)
        print("\n" + "=" * 70)
        print("📋 PHASE 6.3: PERFORMANCE TESTING") 
        print("=" * 70)
        performance_results = await runner.run_test_suite('performance_testing')
        all_results['performance_testing'] = performance_results
        
        # Generate final report
        print("\n" + "=" * 70)
        print("📊 FINAL TEST REPORT")
        print("=" * 70)
        
        report = runner.generate_test_report()
        
        print(f"📈 Overall Results:")
        print(f"   🎯 Total Tests: {report['summary']['total_tests']}")
        print(f"   ✅ Passed: {report['summary']['passed']}")
        print(f"   ❌ Failed: {report['summary']['failed']}")
        print(f"   ⏭️  Skipped: {report['summary']['skipped']}")
        print(f"   📊 Success Rate: {report['summary']['success_rate']:.1f}%")
        print(f"   ⏱️  Total Duration: {report['summary']['total_duration']:.2f}s")
        
        # Save report to file
        report_path = f"test_reports/phase6_test_report_{int(time.time())}.json"
        os.makedirs('test_reports', exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_path}")
        
        # Determine overall pass/fail
        if report['summary']['success_rate'] >= 90:
            print("\n🎉 PHASE 6 TESTING: PASSED")
            print("   Dashboard ready for Phase 7 deployment!")
        elif report['summary']['success_rate'] >= 75:
            print("\n⚠️  PHASE 6 TESTING: PARTIALLY PASSED")
            print("   Review failed tests before proceeding to Phase 7")
        else:
            print("\n❌ PHASE 6 TESTING: FAILED")
            print("   Critical issues must be resolved before deployment")
        
        return report
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR in test execution: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(main())
