#!/usr/bin/env python3
"""
Simple Test Framework Demo
Demonstrates the core testing capabilities without external dependencies
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleTestFramework:
    """Simplified test framework for demonstration"""

    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root)
        self.tests = {}
        self.results = []

    async def generate_basic_tests(self, code_content: str) -> List[Dict[str, Any]]:
        """Generate basic tests from code content"""
        tests = []
        lines = code_content.split("\n")

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line.startswith("def ") and not line.startswith("def _"):
                func_name = line.split("(")[0].replace("def ", "")

                test = {
                    "test_id": str(uuid4()),
                    "name": f"test_{func_name}_basic",
                    "function": func_name,
                    "type": "unit",
                    "description": f"Test basic functionality of {func_name}",
                    "line_number": i,
                }
                tests.append(test)
                self.tests[test["test_id"]] = test

        return tests

    async def run_tests(self, test_ids: List[str] = None) -> Dict[str, Any]:
        """Run tests and return results"""
        if test_ids is None:
            test_ids = list(self.tests.keys())

        results = {
            "total_tests": len(test_ids),
            "passed": 0,
            "failed": 0,
            "execution_time": 0.0,
            "test_details": [],
        }

        start_time = datetime.now()

        for test_id in test_ids:
            if test_id not in self.tests:
                continue

            test = self.tests[test_id]

            # Simulate test execution
            await asyncio.sleep(0.01)  # Simulate work

            # Mock test result (90% pass rate)
            import random

            passed = random.random() > 0.1

            result = {
                "test_id": test_id,
                "name": test["name"],
                "function": test["function"],
                "status": "passed" if passed else "failed",
                "execution_time_ms": random.randint(10, 100),
            }

            results["test_details"].append(result)

            if passed:
                results["passed"] += 1
            else:
                results["failed"] += 1

        execution_time = (datetime.now() - start_time).total_seconds()
        results["execution_time"] = execution_time
        results["success_rate"] = (
            (results["passed"] / results["total_tests"]) * 100
            if results["total_tests"] > 0
            else 0
        )

        self.results.append(results)
        return results


# Demo function
async def demo_test_framework():
    """Demonstrate the test framework"""
    print("🧪 Simple Test Framework Demo")
    print("=" * 50)

    framework = SimpleTestFramework()

    # Sample code to test
    sample_code = '''
def add_numbers(a, b):
    """Add two numbers together."""
    return a + b

def subtract_numbers(a, b):
    """Subtract b from a."""
    return a - b

def multiply_numbers(a, b):
    """Multiply two numbers."""
    return a * b

def divide_numbers(a, b):
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

class Calculator:
    def calculate(self, operation, a, b):
        if operation == "add":
            return self.add(a, b)
        elif operation == "multiply":
            return self.multiply(a, b)
        return 0
    
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b
'''

    print("📝 Sample Code Analysis:")
    print(f"   Lines of code: {len(sample_code.split())}")
    print(
        f"   Functions detected: {len([line for line in sample_code.split() if line.strip().startswith('def ')])}"
    )

    # Generate tests
    print("\n🔍 Generating Tests...")
    tests = await framework.generate_basic_tests(sample_code)
    print(f"   Generated {len(tests)} test cases:")

    for test in tests[:5]:  # Show first 5
        print(f"   - {test['name']} (testing {test['function']})")

    if len(tests) > 5:
        print(f"   ... and {len(tests) - 5} more")

    # Run tests
    print("\n🚀 Running Tests...")
    results = await framework.run_tests()

    print(f"\n📊 Test Results:")
    print(f"   Total Tests: {results['total_tests']}")
    print(f"   Passed: {results['passed']}")
    print(f"   Failed: {results['failed']}")
    print(f"   Success Rate: {results['success_rate']:.1f}%")
    print(f"   Execution Time: {results['execution_time']:.3f}s")

    # Show detailed results
    print(f"\n📋 Test Details:")
    for result in results["test_details"]:
        status_icon = "✅" if result["status"] == "passed" else "❌"
        print(f"   {status_icon} {result['name']} ({result['execution_time_ms']}ms)")

    print(f"\n🎯 Framework capabilities demonstrated:")
    print(f"   ✓ Automatic test generation from code")
    print(f"   ✓ Test execution with timing")
    print(f"   ✓ Result aggregation and reporting")
    print(f"   ✓ Success rate calculation")

    return results


if __name__ == "__main__":
    asyncio.run(demo_test_framework())
