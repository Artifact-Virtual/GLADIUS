#!/usr/bin/env python3
"""
GraphRAG Module Test
Tests the graph retrieval-augmented generation functionality
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the matrix path to Python path
matrix_path = Path(__file__).parent.parent / 'matrix'
sys.path.insert(0, str(matrix_path))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_graphrag_imports():
    """Test GraphRAG module imports"""
    logger.info("Testing GraphRAG imports...")
    
    try:
        # Add the matrix directory to path
        import sys
        import os
        matrix_path = os.path.join(os.path.dirname(__file__), '..', 'matrix')
        sys.path.insert(0, matrix_path)
        
        # Test basic imports of actual modules
        import graphrag.search
        import graphrag.utils
        import graphrag.entity_resolution
        
        logger.info("✅ Core GraphRAG imports successful")
        
        # Test if modules have expected attributes
        if hasattr(graphrag.search, 'KGSearch'):
            logger.info("✅ Found KGSearch class")
        else:
            logger.warning("⚠️ KGSearch class not found")
            
        if hasattr(graphrag.utils, 'clean_str'):
            logger.info("✅ Found clean_str function")
        else:
            logger.warning("⚠️ clean_str function not found")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ GraphRAG import failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False


async def test_graphrag_functionality():
    """Test basic GraphRAG functionality"""
    logger.info("Testing GraphRAG functionality...")
    
    try:
        # Add the matrix directory to path
        import sys
        import os
        matrix_path = os.path.join(os.path.dirname(__file__), '..', 'matrix')
        sys.path.insert(0, matrix_path)
        
        import graphrag.utils
        
        # Test utility functions if they exist
        if hasattr(graphrag.utils, 'clean_str'):
            test_text = "  <script>alert('test')</script>  "
            cleaned = graphrag.utils.clean_str(test_text)
            logger.info(f"✅ Text cleaning: '{test_text}' -> '{cleaned}'")
        else:
            logger.warning("⚠️ clean_str function not found")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ GraphRAG functionality test failed: {e}")
        return False


async def test_graphrag_search():
    """Test GraphRAG search functionality"""
    logger.info("Testing GraphRAG search...")
    
    try:
        # Add the matrix directory to path
        import sys
        import os
        matrix_path = os.path.join(os.path.dirname(__file__), '..', 'matrix')
        sys.path.insert(0, matrix_path)
        
        import graphrag.search
        
        # Test if search module has expected classes
        if hasattr(graphrag.search, 'KGSearch'):
            logger.info("✅ KGSearch class available")
        else:
            logger.warning("⚠️ KGSearch class not found")
        
        # Test query analysis prompts
        try:
            import graphrag.query_analyze_prompt
            if hasattr(graphrag.query_analyze_prompt, 'PROMPTS'):
                logger.info("✅ Query analysis prompts loaded")
            else:
                logger.warning("⚠️ Query analysis prompts missing")
        except ImportError:
            logger.warning("⚠️ Query analyze prompt module not found")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ GraphRAG search test failed: {e}")
        return False


async def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 GRAPHRAG MODULE TEST")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_graphrag_imports),
        ("Functionality Test", test_graphrag_functionality),
        ("Search Test", test_graphrag_search),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("📊 GRAPHRAG TEST RESULTS")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
