#!/usr/bin/env python3
"""
Matrix Subsystem Setup Script
Sets up the complete matrix subsystem with code executor integration
"""

import asyncio
import logging
import sys
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MatrixSetup:
    """Setup manager for the matrix subsystem"""
    
    def __init__(self):
        self.nerve_centre_path = Path(__file__).parent.parent
        self.matrix_path = self.nerve_centre_path / 'matrix'
        self.executor_path = self.matrix_path / 'executor_manager'
        
    async def setup_complete_system(self):
        """Setup the complete matrix system"""
        logger.info("Starting Matrix Subsystem Setup...")
        
        try:
            # 1. Verify paths
            await self._verify_paths()
            
            # 2. Install dependencies
            await self._install_dependencies()
            
            # 3. Setup executor manager
            await self._setup_executor_manager()
            
            # 4. Test integrations
            await self._test_integrations()
            
            logger.info("✅ Matrix Subsystem setup completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            return False
    
    async def _verify_paths(self):
        """Verify all required paths exist"""
        logger.info("Verifying paths...")
        
        required_paths = [
            self.matrix_path,
            self.executor_path,
            self.matrix_path / 'deepdoc',
            self.matrix_path / 'graphrag',
            self.matrix_path / 'nlp',
            self.nerve_centre_path / 'foundry' / 'helm'
        ]
        
        for path in required_paths:
            if not path.exists():
                raise FileNotFoundError(f"Required path not found: {path}")
            logger.info(f"✓ Found: {path}")
    
    async def _install_dependencies(self):
        """Install required dependencies"""
        logger.info("Installing dependencies...")
        
        # Matrix executor manager dependencies
        executor_requirements = self.executor_path / 'requirements.txt'
        if executor_requirements.exists():
            logger.info("Installing executor manager dependencies...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', str(executor_requirements)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"Executor dependencies install failed: {result.stderr}")
            else:
                logger.info("✓ Executor dependencies installed")
        
        # Additional dependencies for MCP integration
        additional_deps = [
            'aiohttp',
            'psutil',
            'beartype'  # For deepdoc type checking
        ]
        
        for dep in additional_deps:
            logger.info(f"Installing {dep}...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', dep
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✓ {dep} installed")
            else:
                logger.warning(f"Failed to install {dep}: {result.stderr}")
    
    async def _setup_executor_manager(self):
        """Setup the executor manager"""
        logger.info("Setting up executor manager...")
        
        # Check if Docker is available
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✓ Docker is available")
                docker_available = True
            else:
                logger.warning("Docker not available - will use local execution fallback")
                docker_available = False
        except FileNotFoundError:
            logger.warning("Docker not found - will use local execution fallback")
            docker_available = False
        
        # Test Python and Node.js availability for local execution
        for runtime, command in [('Python', 'python3'), ('Node.js', 'node')]:
            try:
                result = subprocess.run([command, '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"✓ {runtime} is available: {result.stdout.strip()}")
                else:
                    logger.warning(f"{runtime} not available")
            except FileNotFoundError:
                logger.warning(f"{runtime} not found")
    
    async def _test_integrations(self):
        """Test the MCP and code executor integrations"""
        logger.info("Testing integrations...")
        
        try:
            # Test MCP integration
            from llm_abstraction.mcp.integration import MCPLLMIntegrator
            
            integrator = MCPLLMIntegrator()
            success = await integrator.initialize()
            
            if success:
                logger.info("✓ MCP integration test passed")
                
                # Test code executor functions
                if integrator.executor_functions:
                    logger.info("✓ Code executor functions available")
                    
                    # Test basic function definitions
                    func_defs = integrator.executor_functions.get_function_definitions()
                    logger.info(f"✓ {len(func_defs)} code execution functions defined")
                    
                    # Test system info
                    system_info = await integrator.executor_functions.get_executor_info()
                    logger.info(f"✓ System info: {system_info.get('platform', 'Unknown')}")
                else:
                    logger.warning("Code executor functions not available")
                
                await integrator.shutdown()
            else:
                logger.warning("MCP integration test failed")
                
        except Exception as e:
            logger.error(f"Integration test failed: {e}")
    
    def print_setup_summary(self):
        """Print setup summary and next steps"""
        print("\n" + "="*60)
        print("🚀 MATRIX SUBSYSTEM SETUP COMPLETE")
        print("="*60)
        print()
        print("📁 KEY COMPONENTS:")
        print(f"   • Matrix Core: {self.matrix_path}")
        print(f"   • Executor Manager: {self.executor_path}")
        print(f"   • Helm Charts: {self.nerve_centre_path / 'foundry' / 'helm'}")
        print()
        print("🔧 AVAILABLE MODULES:")
        print("   • deepdoc/ - Advanced document processing")
        print("   • graphrag/ - Graph retrieval-augmented generation")
        print("   • nlp/ - Natural language processing")
        print("   • organized_retrieval.py - Hierarchical retrieval")
        print("   • executor_manager/ - Code execution service")
        print()
        print("⚡ NEXT STEPS:")
        print("   1. Start executor manager:")
        print(f"      cd {self.nerve_centre_path}/llm_abstraction")
        print("      python start_executor_manager.py")
        print()
        print("   2. Test MCP integration:")
        print("      python test_mcp_integration.py")
        print()
        print("   3. Deploy with Helm (optional):")
        print(f"      cd {self.nerve_centre_path}/foundry/helm")
        print("      helm install matrix-system .")
        print()
        print("📖 DOCUMENTATION:")
        print(f"   • Architecture: {self.matrix_path}/ARCHITECTURE.md")
        print(f"   • Foundry docs: {self.nerve_centre_path}/foundry/ARCHITECTURE.md")
        print()
        print("="*60)


async def main():
    """Main setup function"""
    print("🔧 Matrix Subsystem Setup")
    print("Setting up the complete matrix subsystem with code execution...")
    print()
    
    setup = MatrixSetup()
    
    try:
        success = await setup.setup_complete_system()
        
        if success:
            setup.print_setup_summary()
            return 0
        else:
            print("\n❌ Setup failed. Check the logs above for details.")
            return 1
            
    except KeyboardInterrupt:
        logger.info("Setup interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
