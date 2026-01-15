#!/usr/bin/env python3
"""
Enterprise Legion Installation & Setup Script
Unified setup for the AI-powered enterprise management platform.
Handles all Python and Node dependencies, environment prep, DBs, and config.
"""

import os
import sys
import subprocess
import sqlite3
import json
import platform
import shutil
import urllib.request
import zipfile
import tarfile
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def install_dependencies():
    """Install required Python dependencies from requirements.txt"""
    print("📦 Installing Python dependencies...")
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path])
        print("✅ Python dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False

def install_dashboard_dependencies():
    """Install Node dependencies for the React dashboard."""
    dashboard_dir = os.path.join(os.path.dirname(__file__), 'reporting', 'dashboards')
    pkg_path = os.path.join(dashboard_dir, 'package.json')
    if not os.path.exists(pkg_path):
        print(f"❌ Dashboard package.json not found in {dashboard_dir}")
        return False
    print(f"📦 Installing dashboard (Node) dependencies in {dashboard_dir} ...")
    try:
        subprocess.check_call(['npm', 'install'], cwd=dashboard_dir)
        print("✅ Dashboard Node dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dashboard Node dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        "data",
        "logs",
        "config",
        "backups",
        "frontend-analyzer"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def initialize_databases():
    """Initialize SQLite databases"""
    print("🗄️ Initializing databases...")
    
    # CRM Database
    crm_db_path = "data/crm.db"
    with sqlite3.connect(crm_db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                company TEXT,
                status TEXT DEFAULT 'New',
                value REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER,
                activity_type TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lead_id) REFERENCES leads (id)
            )
        """)
    print("✅ CRM database initialized")
    
    # Projects Database
    projects_db_path = "data/projects.db"
    with sqlite3.connect(projects_db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'Active',
                budget REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                assignee TEXT,
                status TEXT DEFAULT 'Todo',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        """)
    print("✅ Projects database initialized")
    
    # Enterprise Operations Database
    enterprise_db_path = "data/enterprise_operations.db"
    with sqlite3.connect(enterprise_db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS business_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                metric_type TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                activity TEXT NOT NULL,
                status TEXT DEFAULT 'Completed',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    print("✅ Enterprise operations database initialized")

def create_config_files():
    """Create default configuration files"""
    print("⚙️ Creating configuration files...")
    
    # Integration configuration
    config_path = "config/integrations.json"
    default_config = {
        "email": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "",
            "password": "",
            "use_tls": True
        },
        "crm": {
            "db_path": "data/crm.db"
        },
        "projects": {
            "db_path": "data/projects.db"
        },
        "apis": {
            "coingecko": "https://api.coingecko.com/api/v3",
            "frankfurter": "https://api.frankfurter.app",
            "spacex": "https://api.spacexdata.com/v4",
            "weather": "https://wttr.in",
            "github": "https://api.github.com"
        }
    }
    
    with open(config_path, 'w') as f:
        json.dump(default_config, f, indent=2)
    print(f"✅ Created configuration: {config_path}")

def run_system_check():
    """Run a basic system check"""
    print("🔍 Running system check...")
    
    try:
        # Test imports
        import asyncio
        import aiohttp
        import sqlite3
        print("✅ All core modules available")
        
        # Test database connections
        for db_path in ["data/crm.db", "data/projects.db", "data/enterprise_operations.db"]:
            with sqlite3.connect(db_path) as conn:
                conn.execute("SELECT 1")
        print("✅ Database connections working")
        
        return True
    except Exception as e:
        print(f"❌ System check failed: {e}")
        return False

def get_system_info():
    """Get system architecture and OS information."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "windows":
        return "windows", "amd64" if machine in ["amd64", "x86_64"] else "386"
    elif system == "darwin":
        return "darwin", "arm64" if machine == "arm64" else "amd64"
    elif system == "linux":
        return "linux", "arm64" if machine in ["aarch64", "arm64"] else "amd64"
    else:
        return system, machine


def install_ollama():
    """Install Ollama with cross-platform support."""
    print("🤖 Installing Ollama...")
    
    system, arch = get_system_info()
    
    try:
        if system == "windows":
            print("📥 Downloading Ollama for Windows...")
            url = "https://ollama.com/download/OllamaSetup.exe"
            urllib.request.urlretrieve(url, "OllamaSetup.exe")
            print("⚠️ Please run OllamaSetup.exe manually to complete installation")
            print("⚠️ After installation, restart this script to continue")
            return False
        
        elif system == "darwin":
            print("📥 Installing Ollama for macOS...")
            subprocess.check_call([
                "curl", "-fsSL", "https://ollama.com/install.sh", "|", "sh"
            ], shell=True)
        
        elif system == "linux":
            print("📥 Installing Ollama for Linux...")
            subprocess.check_call([
                "curl", "-fsSL", "https://ollama.com/install.sh", "|", "sh"
            ], shell=True)
        
        else:
            print(f"❌ Unsupported system: {system}")
            return False
        
        # Wait for Ollama to start
        print("⏳ Starting Ollama service...")
        if system in ["darwin", "linux"]:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            import time
            time.sleep(5)  # Wait for service to start
        
        # Pull the default model
        print("📥 Pulling deepseek-r1:latest model...")
        subprocess.check_call(["ollama", "pull", "deepseek-r1:latest"])
        
        # Create alias
        create_ollama_alias()
        
        print("✅ Ollama installed and configured successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Ollama: {e}")
        return False
    except Exception as e:
        print(f"❌ Ollama installation error: {e}")
        return False


def create_ollama_alias():
    """Create cross-platform alias for Ollama."""
    system, _ = get_system_info()
    
    if system == "windows":
        # Create batch file for Windows
        batch_content = '@echo off\nollama run deepseek-r1 %*\n'
        with open("llm.bat", "w") as f:
            f.write(batch_content)
        print("✅ Created llm.bat alias for Windows")
        
    else:
        # Create shell script for Unix-like systems
        script_content = '#!/bin/bash\nollama run deepseek-r1 "$@"\n'
        with open("llm", "w") as f:
            f.write(script_content)
        os.chmod("llm", 0o755)
        
        # Try to add to PATH via shell profiles
        shell_profiles = ["~/.bashrc", "~/.zshrc", "~/.profile"]
        alias_line = f'export PATH="{os.getcwd()}:$PATH"'
        
        for profile in shell_profiles:
            profile_path = os.path.expanduser(profile)
            if os.path.exists(profile_path):
                try:
                    with open(profile_path, "a") as f:
                        f.write(f"\n# Ollama alias\n{alias_line}\n")
                    print(f"✅ Added to {profile}")
                    break
                except Exception:
                    continue
        
        print("✅ Created llm shell script alias")


def install_llamacpp():
    """Install llama.cpp with cross-platform support."""
    print("🔧 Installing llama.cpp...")
    
    system, arch = get_system_info()
    
    try:
        # Create models directory
        Path("models").mkdir(exist_ok=True)
        
        if system == "windows":
            print("📥 Downloading llama.cpp for Windows...")
            if arch == "amd64":
                url = "https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-b3500-bin-win-avx2-x64.zip"
            else:
                url = "https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-b3500-bin-win-avx-x64.zip"
            
            urllib.request.urlretrieve(url, "llamacpp.zip")
            with zipfile.ZipFile("llamacpp.zip", 'r') as zip_ref:
                zip_ref.extractall("llamacpp")
            os.remove("llamacpp.zip")
            
        elif system in ["darwin", "linux"]:
            print("📥 Building llama.cpp from source...")
            subprocess.check_call(["git", "clone", "https://github.com/ggerganov/llama.cpp.git"])
            os.chdir("llama.cpp")
            subprocess.check_call(["make", "-j8"])
            os.chdir("..")
        
        print("✅ llama.cpp installed successfully")
        print("📝 Note: Place your GGUF model files in the 'models/' directory")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install llama.cpp: {e}")
        return False
    except Exception as e:
        print(f"❌ llama.cpp installation error: {e}")
        return False


def setup_llm_providers():
    """Set up all LLM providers."""
    print("🧠 Setting up LLM providers...")
    
    success = True
    
    # Install Ollama (default provider)
    if not install_ollama():
        print("⚠️ Ollama installation failed - continuing without it")
        success = False
    
    # Install llama.cpp (fallback provider)
    if not install_llamacpp():
        print("⚠️ llama.cpp installation failed - continuing without it")
        success = False
    
    # Check for other providers
    print("\n📋 Other providers can be configured via environment variables:")
    print("  - LocalAI: Set LOCALAI_BASE_URL")
    print("  - LM Studio: Set LLMSTUDIO_BASE_URL")
    print("  - OpenAI: Set OPENAI_API_KEY")
    print("  - Gemini: Set GEMINI_API_KEY")
    print("  - Anthropic: Set ANTHROPIC_API_KEY")
    print("  - Hugging Face: Set HUGGINGFACE_API_KEY")
    
    return success


def update_create_directories():
    """Create necessary directories including LLM-related ones."""
    directories = [
        "data",
        "logs", 
        "config",
        "backups",
        "frontend-analyzer",
        "models",  # For llama.cpp models
        "nerve_centre/llm_abstraction/cache",  # For LLM response caching
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def install_ollama_and_start():
    """Install Ollama, pull the configured model, and start the Ollama server."""
    import subprocess
    import shutil
    import json
    import time
    
    # Use relative path from script directory
    config_dir = Path(__file__).parent / 'config'
    config_path = config_dir / 'llm_config.json'
    
    print("\n🦙 Setting up Ollama...")
    # Check if ollama is installed
    ollama_installed = shutil.which('ollama') is not None
    if not ollama_installed:
        print("🔄 Installing Ollama...")
        try:
            subprocess.check_call(['curl', '-fsSL', 'https://ollama.com/install.sh', '|', 'sh'])
            print("✅ Ollama installed.")
        except Exception as e:
            print(f"❌ Failed to install Ollama: {e}")
            return False
    else:
        print("✅ Ollama already installed.")
    # Load model from config
    try:
        if not config_path.exists():
            print(f"⚠️ Config file not found at {config_path}, using defaults")
            model = 'deepseek-r1:latest'
            port = 11434
        else:
            with open(config_path, 'r') as f:
                config = json.load(f)
            model = config['providers']['ollama']['model']
            port = config['providers']['ollama'].get('port', 11434)
    except Exception as e:
        print(f"⚠️ Could not read model from config: {e}, using defaults")
        model = 'deepseek-r1:latest'
        port = 11434
    print(f"🔄 Pulling Ollama model: {model}")
    try:
        subprocess.check_call(['ollama', 'pull', model])
        print(f"✅ Model {model} pulled.")
    except Exception as e:
        print(f"❌ Failed to pull model: {e}")
        return False
    print(f"🚀 Starting Ollama server on port {port}...")
    try:
        subprocess.Popen(['ollama', 'serve', '--port', str(port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3)
        print("✅ Ollama server started.")
        return True
    except Exception as e:
        print(f"❌ Failed to start Ollama server: {e}")
        return False

def main():
    """Main installation and setup process"""
    print("🚀 Enterprise Legion Installation & Setup")
    print("=" * 40)
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    # Install Python dependencies
    if not install_dependencies():
        sys.exit(1)
    # Install dashboard (Node) dependencies
    if not install_dashboard_dependencies():
        sys.exit(1)
    # Create directories (updated version with LLM directories)
    update_create_directories()
    # Set up LLM providers (Ollama, llama.cpp, etc.)
    setup_llm_providers()
    # Initialize databases
    initialize_databases()
    # Create config files
    create_config_files()
    # Run system check
    if not run_system_check():
        sys.exit(1)
    print("\n" + "=" * 40)
    print("✅ Installation & setup completed successfully!")
    print("\nNext steps:")
    print("1. Configure LLM API keys in config/.env (optional)")
    print("2. Configure email settings in config/integrations.json (optional)")
    print("3. Run the complete system: start_enterprise.py")
    print("4. Test LLM providers: python -c \"from nerve_centre.llm_abstraction.provider_factory import get_provider_factory; print(get_provider_factory().get_provider_list())\"")
    print("5. Run tests: python -m pytest tests/test_comprehensive_system.py -v")
    print("\nFor more information, see README.md")
