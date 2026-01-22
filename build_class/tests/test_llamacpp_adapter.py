#!/usr/bin/env python3
"""
Test script for llama.cpp adapter
Tests the adapter without requiring a running server
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_adapter_import():
    """Test that LlamaCppAdapter can be imported"""
    print("Testing adapter import...")
    try:
        from adapter import LlamaCppAdapter, AnthropicAdapter, MockAdapter
        print("✓ All adapters imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import adapters: {e}")
        return False

def test_adapter_init():
    """Test adapter initialization"""
    print("\nTesting adapter initialization...")
    
    # Set test environment
    os.environ["LLAMA_SERVER_URL"] = "http://localhost:8080"
    os.environ["LLAMA_MAX_TOKENS"] = "1024"
    os.environ["LLAMA_TEMPERATURE"] = "0.5"
    
    try:
        from adapter import LlamaCppAdapter
        adapter = LlamaCppAdapter()
        
        # Check attributes
        assert adapter.server_url == "http://localhost:8080"
        assert adapter.max_tokens == 1024
        assert adapter.temperature == 0.5
        
        print("✓ Adapter initialized with correct configuration")
        print(f"  Server URL: {adapter.server_url}")
        print(f"  Max tokens: {adapter.max_tokens}")
        print(f"  Temperature: {adapter.temperature}")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize adapter: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling with invalid server"""
    print("\nTesting error handling...")
    
    os.environ["LLAMA_SERVER_URL"] = "http://invalid-server:9999"
    
    try:
        from adapter import LlamaCppAdapter
        adapter = LlamaCppAdapter()
        
        # Try to call with invalid server - should handle gracefully
        result = adapter.call(
            "You are a helpful assistant",
            [{"role": "user", "content": "Hello"}],
            []
        )
        
        # Should return error response, not crash
        print("✓ Error handled gracefully")
        print(f"  Result type: {type(result)}")
        print(f"  Result: {result}")
        return True
    except Exception as e:
        print(f"✗ Error not handled properly: {e}")
        return False

def test_adapter_swapping():
    """Test that adapters can be easily swapped"""
    print("\nTesting adapter swapping...")
    
    try:
        from adapter import LlamaCppAdapter, AnthropicAdapter, MockAdapter
        
        # Create instances of all adapters
        adapters = {
            "llamacpp": LlamaCppAdapter(),
            "mock": MockAdapter()
        }
        
        print("✓ All adapters can be instantiated")
        print(f"  Available adapters: {list(adapters.keys())}")
        
        # Test that they all have call method
        for name, adapter in adapters.items():
            assert hasattr(adapter, 'call'), f"{name} missing call method"
        
        print("✓ All adapters implement required interface")
        return True
    except Exception as e:
        print(f"✗ Adapter swapping test failed: {e}")
        return False

def main():
    print("="*60)
    print("llama.cpp Adapter Test Suite")
    print("="*60)
    
    tests = [
        test_adapter_import,
        test_adapter_init,
        test_error_handling,
        test_adapter_swapping
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print(f"✗ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
