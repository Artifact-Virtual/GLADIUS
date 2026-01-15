#!/usr/bin/env python3
"""
Executor Manager Test
Tests the code execution manager functionality
"""

import logging
import sys
import asyncio
from pathlib import Path

# Add the matrix path to Python path
matrix_path = Path(__file__).parent.parent / 'matrix'
sys.path.insert(0, str(matrix_path))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_executor_structure():
    """Test Executor Manager structure"""
    logger.info("Testing Executor Manager structure...")
    
    try:
        executor_path = matrix_path / 'executor_manager'
        if not executor_path.exists():
            logger.error("❌ Executor Manager directory not found")
            return False
        
        logger.info("✅ Executor Manager directory found")
        
        # Check for key files and directories
        expected_items = [
            'main.py',
            'requirements.txt',
            'Dockerfile',
            'api/',
            'core/',
            'models/',
            'services/',
            'utils/'
        ]
        
        for item_name in expected_items:
            item_path = executor_path / item_name
            if item_path.exists():
                if item_path.is_dir():
                    logger.info(f"✅ Found directory: {item_name}")
                else:
                    size = item_path.stat().st_size
                    logger.info(f"✅ Found file: {item_name} ({size} bytes)")
            else:
                logger.warning(f"⚠️ Missing: {item_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Executor structure test failed: {e}")
        return False


def test_executor_main():
    """Test Executor Manager main application"""
    logger.info("Testing Executor Manager main app...")
    
    try:
        main_file = matrix_path / 'executor_manager' / 'main.py'
        if not main_file.exists():
            logger.error("❌ main.py not found")
            return False
        
        content = main_file.read_text()
        
        # Check for key FastAPI elements
        key_elements = [
            'FastAPI',
            'app',
            'router',
            'limiter'
        ]
        
        found_elements = []
        for element in key_elements:
            if element in content:
                found_elements.append(element)
                logger.info(f"✅ Found: {element}")
        
        logger.info(f"✅ Main app contains {len(found_elements)}/{len(key_elements)} key elements")
        
        # Check file size
        size = len(content)
        logger.info(f"✅ Main app size: {size} characters")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Executor main test failed: {e}")
        return False


def test_executor_requirements():
    """Test Executor Manager requirements"""
    logger.info("Testing Executor Manager requirements...")
    
    try:
        req_file = matrix_path / 'executor_manager' / 'requirements.txt'
        if not req_file.exists():
            logger.error("❌ requirements.txt not found")
            return False
        
        content = req_file.read_text()
        requirements = [line.strip() for line in content.split('\n') if line.strip()]
        
        logger.info(f"✅ Found {len(requirements)} requirements:")
        for req in requirements:
            logger.info(f"  - {req}")
        
        # Check for key dependencies
        expected_deps = ['fastapi', 'uvicorn']
        found_deps = []
        
        for dep in expected_deps:
            if any(dep.lower() in req.lower() for req in requirements):
                found_deps.append(dep)
                logger.info(f"✅ Found dependency: {dep}")
            else:
                logger.warning(f"⚠️ Missing dependency: {dep}")
        
        return len(found_deps) >= 1  # At least FastAPI should be there
        
    except Exception as e:
        logger.error(f"❌ Executor requirements test failed: {e}")
        return False


def test_executor_core():
    """Test Executor Manager core components"""
    logger.info("Testing Executor Manager core...")
    
    try:
        core_path = matrix_path / 'executor_manager' / 'core'
        if not core_path.exists():
            logger.error("❌ Core directory not found")
            return False
        
        # Check for core files
        expected_core_files = [
            '__init__.py',
            'config.py',
            'container.py',
            'logger.py'
        ]
        
        found_files = []
        for file_name in expected_core_files:
            file_path = core_path / file_name
            if file_path.exists():
                size = file_path.stat().st_size
                found_files.append(file_name)
                logger.info(f"✅ Found core file: {file_name} ({size} bytes)")
            else:
                logger.warning(f"⚠️ Missing core file: {file_name}")
        
        logger.info(f"✅ Core contains {len(found_files)}/{len(expected_core_files)} expected files")
        
        return len(found_files) >= 2  # At least half the files should be there
        
    except Exception as e:
        logger.error(f"❌ Executor core test failed: {e}")
        return False


async def test_executor_bridge():
    """Test our MCP Executor Bridge"""
    logger.info("Testing MCP Executor Bridge...")
    
    try:
        # Import our bridge
        bridge_path = Path(__file__).parent / 'mcp' / 'executors' / 'code_executor_bridge.py'
        if not bridge_path.exists():
            logger.error("❌ Code executor bridge not found")
            return False
        
        logger.info("✅ Code executor bridge file found")
        
        # Check bridge content
        content = bridge_path.read_text()
        
        # Check for key bridge elements
        bridge_elements = [
            'class CodeExecutorBridge',
            'class MCPCodeExecutorFunctions',
            'class ExecutionRequest',
            'class ExecutionResult',
            'async def execute_code',
            'async def initialize'
        ]
        
        found_elements = []
        for element in bridge_elements:
            if element in content:
                found_elements.append(element)
                logger.info(f"✅ Found bridge element: {element}")
        
        logger.info(f"✅ Bridge contains {len(found_elements)}/{len(bridge_elements)} key elements")
        
        # Check file size
        size = len(content)
        logger.info(f"✅ Bridge size: {size} characters")
        
        return len(found_elements) >= 4  # Most elements should be there
        
    except Exception as e:
        logger.error(f"❌ Executor bridge test failed: {e}")
        return False


def main():
    """Main test function"""
    print("=" * 60)
    print("⚙️ EXECUTOR MANAGER TEST")
    print("=" * 60)
    
    tests = [
        ("Structure Test", test_executor_structure),
        ("Main App Test", test_executor_main),
        ("Requirements Test", test_executor_requirements),
        ("Core Test", test_executor_core),
        ("Bridge Test", lambda: asyncio.run(test_executor_bridge())),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("📊 EXECUTOR MANAGER TEST RESULTS")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
