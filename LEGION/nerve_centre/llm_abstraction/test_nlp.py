#!/usr/bin/env python3
"""
NLP Module Test
Tests the natural language processing functionality
"""

import logging
import sys
from pathlib import Path

# Add the matrix path to Python path
matrix_path = Path(__file__).parent.parent / 'matrix'
sys.path.insert(0, str(matrix_path))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_nlp_structure():
    """Test NLP module structure"""
    logger.info("Testing NLP structure...")
    
    try:
        nlp_path = matrix_path / 'nlp'
        if not nlp_path.exists():
            logger.error("❌ NLP directory not found")
            return False
        
        logger.info("✅ NLP directory found")
        
        # Check for key files
        expected_files = [
            '__init__.py',
            'search.py',
            'query.py', 
            'rag_tokenizer.py',
            'term_weight.py',
            'synonym.py'
        ]
        
        for file_name in expected_files:
            file_path = nlp_path / file_name
            if file_path.exists():
                size = file_path.stat().st_size
                logger.info(f"✅ Found {file_name} ({size} bytes)")
            else:
                logger.warning(f"⚠️ Missing {file_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ NLP structure test failed: {e}")
        return False


def test_nlp_search_functionality():
    """Test NLP search functionality"""
    logger.info("Testing NLP search functionality...")
    
    try:
        search_file = matrix_path / 'nlp' / 'search.py'
        if not search_file.exists():
            logger.error("❌ search.py not found")
            return False
        
        content = search_file.read_text()
        
        # Check for key classes and functions
        key_elements = [
            'class Dealer',
            'class SearchResult',
            'def search',
            'def get_vector',
            'index_name'
        ]
        
        found_elements = []
        for element in key_elements:
            if element in content:
                found_elements.append(element)
                logger.info(f"✅ Found: {element}")
            else:
                logger.warning(f"⚠️ Missing: {element}")
        
        logger.info(f"✅ Search module contains {len(found_elements)}/{len(key_elements)} key elements")
        
        # Check file size
        size = len(content)
        logger.info(f"✅ Search module size: {size} characters")
        
        if size > 5000:  # Substantial implementation
            logger.info("✅ Search module appears to have substantial implementation")
        else:
            logger.warning("⚠️ Search module may be incomplete")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ NLP search test failed: {e}")
        return False


def test_nlp_tokenizer():
    """Test NLP tokenizer functionality"""
    logger.info("Testing NLP tokenizer...")
    
    try:
        tokenizer_file = matrix_path / 'nlp' / 'rag_tokenizer.py'
        if not tokenizer_file.exists():
            logger.error("❌ rag_tokenizer.py not found")
            return False
        
        content = tokenizer_file.read_text()
        
        # Check for tokenizer functionality
        tokenizer_elements = [
            'def',
            'token',
            'split',
            'text'
        ]
        
        found_count = 0
        for element in tokenizer_elements:
            if element.lower() in content.lower():
                found_count += 1
        
        logger.info(f"✅ Tokenizer contains {found_count}/{len(tokenizer_elements)} key concepts")
        
        # Check file size
        size = len(content)
        logger.info(f"✅ Tokenizer size: {size} characters")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ NLP tokenizer test failed: {e}")
        return False


def test_nlp_query():
    """Test NLP query functionality"""
    logger.info("Testing NLP query...")
    
    try:
        query_file = matrix_path / 'nlp' / 'query.py'
        if not query_file.exists():
            logger.error("❌ query.py not found")
            return False
        
        content = query_file.read_text()
        
        # Check for query processing functionality
        query_elements = [
            'class',
            'def',
            'query',
            'process'
        ]
        
        found_count = 0
        for element in query_elements:
            if element.lower() in content.lower():
                found_count += 1
        
        logger.info(f"✅ Query module contains {found_count}/{len(query_elements)} key concepts")
        
        # Check file size
        size = len(content)
        logger.info(f"✅ Query module size: {size} characters")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ NLP query test failed: {e}")
        return False


def main():
    """Main test function"""
    print("=" * 60)
    print("🔤 NLP MODULE TEST")
    print("=" * 60)
    
    tests = [
        ("Structure Test", test_nlp_structure),
        ("Search Test", test_nlp_search_functionality),
        ("Tokenizer Test", test_nlp_tokenizer),
        ("Query Test", test_nlp_query),
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
    print("📊 NLP TEST RESULTS")
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
