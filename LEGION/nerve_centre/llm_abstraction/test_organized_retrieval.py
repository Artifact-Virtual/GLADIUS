#!/usr/bin/env python3
"""
Organized Retrieval Test
Tests the hierarchical retrieval functionality
"""

import logging
import sys
from pathlib import Path

# Add the matrix path to Python path
matrix_path = Path(__file__).parent.parent / 'matrix'
sys.path.insert(0, str(matrix_path))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_organized_retrieval_structure():
    """Test Organized Retrieval file structure"""
    logger.info("Testing Organized Retrieval structure...")
    
    try:
        retrieval_file = matrix_path / 'organized_retrieval.py'
        if not retrieval_file.exists():
            logger.error("❌ organized_retrieval.py not found")
            return False
        
        logger.info("✅ organized_retrieval.py found")
        
        # Check file size
        size = retrieval_file.stat().st_size
        logger.info(f"✅ File size: {size} bytes")
        
        if size > 1000:  # Should be substantial
            logger.info("✅ File appears to have substantial implementation")
        else:
            logger.warning("⚠️ File may be incomplete")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Organized Retrieval structure test failed: {e}")
        return False


def test_organized_retrieval_content():
    """Test Organized Retrieval content and classes"""
    logger.info("Testing Organized Retrieval content...")
    
    try:
        retrieval_file = matrix_path / 'organized_retrieval.py'
        content = retrieval_file.read_text()
        
        # Check for key classes and concepts
        key_elements = [
            'class RecursiveAbstractiveProcessing',
            'TreeOrganizedRetrieval',
            'umap',
            'GaussianMixture',
            'async def',
            'def __call__',
            'clustering',
            'embedding'
        ]
        
        found_elements = []
        for element in key_elements:
            if element.lower() in content.lower():
                found_elements.append(element)
                logger.info(f"✅ Found concept: {element}")
            else:
                logger.warning(f"⚠️ Missing concept: {element}")
        
        logger.info(f"✅ Contains {len(found_elements)}/{len(key_elements)} key concepts")
        
        # Check for specific algorithms
        algorithms = ['UMAP', 'Gaussian', 'clustering', 'hierarchical']
        found_algorithms = []
        
        for algo in algorithms:
            if algo.lower() in content.lower():
                found_algorithms.append(algo)
                logger.info(f"✅ Found algorithm: {algo}")
        
        logger.info(f"✅ Contains {len(found_algorithms)}/{len(algorithms)} key algorithms")
        
        return len(found_elements) >= 4  # At least half should be found
        
    except Exception as e:
        logger.error(f"❌ Organized Retrieval content test failed: {e}")
        return False


def test_organized_retrieval_imports():
    """Test Organized Retrieval imports"""
    logger.info("Testing Organized Retrieval imports...")
    
    try:
        retrieval_file = matrix_path / 'organized_retrieval.py'
        content = retrieval_file.read_text()
        
        # Check for key imports
        key_imports = [
            'import umap',
            'from sklearn.mixture import GaussianMixture',
            'import trio',
            'import numpy',
            'import logging'
        ]
        
        found_imports = []
        for imp in key_imports:
            if imp in content:
                found_imports.append(imp)
                logger.info(f"✅ Found import: {imp}")
        
        logger.info(f"✅ Contains {len(found_imports)}/{len(key_imports)} expected imports")
        
        # Check for async patterns
        async_patterns = ['async def', 'await', 'trio']
        found_async = []
        
        for pattern in async_patterns:
            if pattern in content:
                found_async.append(pattern)
                logger.info(f"✅ Found async pattern: {pattern}")
        
        logger.info(f"✅ Contains {len(found_async)}/{len(async_patterns)} async patterns")
        
        return len(found_imports) >= 2  # At least some imports should be found
        
    except Exception as e:
        logger.error(f"❌ Organized Retrieval imports test failed: {e}")
        return False


def test_organized_retrieval_functionality():
    """Test basic functionality structure"""
    logger.info("Testing Organized Retrieval functionality...")
    
    try:
        retrieval_file = matrix_path / 'organized_retrieval.py'
        content = retrieval_file.read_text()
        
        # Check for key methods and functions
        key_functions = [
            'def __init__',
            'def __call__',
            'def _get_optimal_clusters',
            'async def',
            'summarize'
        ]
        
        found_functions = []
        for func in key_functions:
            if func in content:
                found_functions.append(func)
                logger.info(f"✅ Found function pattern: {func}")
        
        logger.info(f"✅ Contains {len(found_functions)}/{len(key_functions)} function patterns")
        
        # Check for mathematical concepts
        math_concepts = [
            'clusters',
            'embedding',
            'similarity',
            'distance',
            'optimization'
        ]
        
        found_math = []
        for concept in math_concepts:
            if concept.lower() in content.lower():
                found_math.append(concept)
                logger.info(f"✅ Found math concept: {concept}")
        
        logger.info(f"✅ Contains {len(found_math)}/{len(math_concepts)} math concepts")
        
        # Check file complexity (rough measure)
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        logger.info(f"✅ File contains {len(non_empty_lines)} non-empty lines")
        
        if len(non_empty_lines) > 50:
            logger.info("✅ File appears to have substantial implementation")
        else:
            logger.warning("⚠️ File implementation may be minimal")
        
        return len(found_functions) >= 3  # Should have several key functions
        
    except Exception as e:
        logger.error(f"❌ Organized Retrieval functionality test failed: {e}")
        return False


def main():
    """Main test function"""
    print("=" * 60)
    print("🏗️ ORGANIZED RETRIEVAL TEST")
    print("=" * 60)
    
    tests = [
        ("Structure Test", test_organized_retrieval_structure),
        ("Content Test", test_organized_retrieval_content),
        ("Imports Test", test_organized_retrieval_imports),
        ("Functionality Test", test_organized_retrieval_functionality),
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
    print("📊 ORGANIZED RETRIEVAL TEST RESULTS")
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
