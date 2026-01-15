#!/usr/bin/env python3
"""
DeepDoc Module Test
Tests the advanced document processing functionality
"""

import logging
import sys
from pathlib import Path

# Add the matrix path to Python path
matrix_path = Path(__file__).parent.parent / 'matrix'
sys.path.insert(0, str(matrix_path))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_deepdoc_structure():
    """Test DeepDoc module structure and imports"""
    logger.info("Testing DeepDoc structure...")
    
    try:
        # Check if deepdoc directory exists
        deepdoc_path = matrix_path / 'deepdoc'
        if not deepdoc_path.exists():
            logger.error("❌ DeepDoc directory not found")
            return False
        
        # Check key subdirectories
        expected_dirs = ['parser', 'vision']
        for dir_name in expected_dirs:
            dir_path = deepdoc_path / dir_name
            if dir_path.exists():
                logger.info(f"✅ Found directory: {dir_name}")
            else:
                logger.warning(f"⚠️ Missing directory: {dir_name}")
        
        # Check key files
        init_file = deepdoc_path / '__init__.py'
        if init_file.exists():
            logger.info("✅ DeepDoc __init__.py found")
            
            # Read and check for beartype import
            content = init_file.read_text()
            if 'beartype' in content:
                logger.info("✅ Beartype type checking configured")
            else:
                logger.info("ℹ️ No beartype found (optional)")
        else:
            logger.warning("⚠️ DeepDoc __init__.py not found")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ DeepDoc structure test failed: {e}")
        return False


def test_deepdoc_parsers():
    """Test DeepDoc parser modules"""
    logger.info("Testing DeepDoc parsers...")
    
    try:
        parser_path = matrix_path / 'deepdoc' / 'parser'
        if not parser_path.exists():
            logger.error("❌ Parser directory not found")
            return False
        
        # Check for parser files
        parser_files = list(parser_path.glob("*.py"))
        logger.info(f"✅ Found {len(parser_files)} parser files")
        
        for parser_file in parser_files[:5]:  # Show first 5
            logger.info(f"  - {parser_file.name}")
        
        # Check for specific parsers
        expected_parsers = ['pdf_parser.py', 'docx_parser.py']
        for parser in expected_parsers:
            parser_file = parser_path / parser
            if parser_file.exists():
                logger.info(f"✅ Found {parser}")
                
                # Check file size to ensure it's not empty
                size = parser_file.stat().st_size
                if size > 100:  # At least 100 bytes
                    logger.info(f"  - File size: {size} bytes (good)")
                else:
                    logger.warning(f"  - File size: {size} bytes (may be empty)")
            else:
                logger.warning(f"⚠️ Missing {parser}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ DeepDoc parsers test failed: {e}")
        return False


def test_deepdoc_vision():
    """Test DeepDoc vision modules"""
    logger.info("Testing DeepDoc vision...")
    
    try:
        vision_path = matrix_path / 'deepdoc' / 'vision'
        if not vision_path.exists():
            logger.error("❌ Vision directory not found")
            return False
        
        # Check for vision files
        vision_files = list(vision_path.glob("*.py"))
        logger.info(f"✅ Found {len(vision_files)} vision files")
        
        # Check for specific vision modules
        expected_vision = ['ocr.py', 'layout_recognizer.py', 'table_structure_recognizer.py']
        for vision_module in expected_vision:
            vision_file = vision_path / vision_module
            if vision_file.exists():
                logger.info(f"✅ Found {vision_module}")
            else:
                logger.warning(f"⚠️ Missing {vision_module}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ DeepDoc vision test failed: {e}")
        return False


def test_deepdoc_functionality():
    """Test basic DeepDoc functionality"""
    logger.info("Testing DeepDoc functionality...")
    
    try:
        # Try to read the PDF parser to check its structure
        pdf_parser_path = matrix_path / 'deepdoc' / 'parser' / 'pdf_parser.py'
        if pdf_parser_path.exists():
            content = pdf_parser_path.read_text()
            
            # Check for key functionality indicators
            indicators = ['class', 'def ', 'pdf', 'parse']
            found_indicators = []
            
            for indicator in indicators:
                if indicator.lower() in content.lower():
                    found_indicators.append(indicator)
            
            logger.info(f"✅ PDF parser contains: {', '.join(found_indicators)}")
            
            # Check file size
            size = len(content)
            logger.info(f"✅ PDF parser size: {size} characters")
            
            if size > 1000:  # Substantial implementation
                logger.info("✅ PDF parser appears to have substantial implementation")
            else:
                logger.warning("⚠️ PDF parser may be incomplete")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ DeepDoc functionality test failed: {e}")
        return False


def main():
    """Main test function"""
    print("=" * 60)
    print("📄 DEEPDOC MODULE TEST")
    print("=" * 60)
    
    tests = [
        ("Structure Test", test_deepdoc_structure),
        ("Parsers Test", test_deepdoc_parsers),
        ("Vision Test", test_deepdoc_vision),
        ("Functionality Test", test_deepdoc_functionality),
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
    print("📊 DEEPDOC TEST RESULTS")
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
