#!/usr/bin/env python3
"""
build_class Launcher

This launcher script initializes the appropriate adapter and starts
the build_class autonomous execution kernel.

Usage:
    # Primary (recommended): llama.cpp local server
    export ADAPTER_TYPE=llamacpp
    export LLAMA_SERVER_URL=http://localhost:8080
    python run.py
    
    # Alternative: Anthropic Claude API
    export ADAPTER_TYPE=anthropic
    export ANTHROPIC_API_KEY="your-key-here"
    python run.py
    
    # Testing: Mock adapter (no LLM needed)
    export ADAPTER_TYPE=mock
    python run.py

Environment variables can also be set in a .env file.
"""

import sys
import os

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[INFO] Loaded configuration from .env file")
except ImportError:
    pass  # dotenv not installed, using environment variables only

def get_adapter():
    """Initialize and return the appropriate adapter based on configuration"""
    adapter_type = os.environ.get("ADAPTER_TYPE", "llamacpp").lower()
    
    print(f"[INFO] Adapter type: {adapter_type}")
    
    if adapter_type == "llamacpp" or adapter_type == "llama":
        # Primary adapter: llama.cpp
        try:
            from adapter import LlamaCppAdapter
            adapter = LlamaCppAdapter()
            server_url = os.environ.get("LLAMA_SERVER_URL", "http://localhost:8080")
            print(f"[INFO] Using llama.cpp server at: {server_url}")
            print(f"[INFO] Max tokens: {os.environ.get('LLAMA_MAX_TOKENS', '2048')}")
            print(f"[INFO] Temperature: {os.environ.get('LLAMA_TEMPERATURE', '0.7')}")
            return adapter
        except Exception as e:
            print(f"[ERROR] Failed to initialize llama.cpp adapter: {e}")
            print("\nMake sure llama.cpp server is running:")
            print("  ./server -m /path/to/model.gguf --port 8080")
            print("\nOr use mock adapter for testing:")
            print("  export ADAPTER_TYPE=mock")
            sys.exit(1)
    
    elif adapter_type == "anthropic":
        # Alternative adapter: Anthropic
        # Check for API key
        if "ANTHROPIC_API_KEY" not in os.environ or not os.environ["ANTHROPIC_API_KEY"]:
            print("\n[ERROR] ANTHROPIC_API_KEY environment variable not set or empty")
            print("\nPlease set your API key:")
            print("  export ANTHROPIC_API_KEY='your-api-key-here'")
            print("\nOr use llama.cpp (recommended):")
            print("  export ADAPTER_TYPE=llamacpp")
            sys.exit(1)
        
        try:
            from adapter import AnthropicAdapter
            adapter = AnthropicAdapter()
            print(f"[INFO] Model: {os.environ.get('MODEL', 'claude-3-opus-20240229')}")
            return adapter
        except Exception as e:
            print(f"[ERROR] Failed to initialize Anthropic adapter: {e}")
            sys.exit(1)
    
    elif adapter_type == "mock":
        # Testing adapter: Mock
        try:
            from adapter import MockAdapter
            adapter = MockAdapter()
            print("[INFO] Using mock adapter (interactive testing mode)")
            print("[INFO] You will be prompted to provide LLM responses")
            return adapter
        except Exception as e:
            print(f"[ERROR] Failed to initialize Mock adapter: {e}")
            sys.exit(1)
    
    else:
        print(f"[ERROR] Unknown adapter type: {adapter_type}")
        print("Supported types: 'llamacpp' (primary), 'anthropic', 'mock'")
        sys.exit(1)

# Import and initialize
try:
    from build_class import main
except ImportError as e:
    print(f"[ERROR] Error importing modules: {e}")
    print("\nMake sure all required files are present:")
    print("  - adapter.py")
    print("  - build_class.py")
    sys.exit(1)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Initializing build_class...")
    print("="*60)
    
    try:
        adapter = get_adapter()
        main(adapter)
    except KeyboardInterrupt:
        print("\n\nShutdown requested. Goodbye!")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
