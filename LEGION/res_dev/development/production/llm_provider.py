#!/usr/bin/env python3
"""
LLM Provider Integration for Production Pipeline
Unified interface for code generation and file structure creation
"""

import os
import json
import logging
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# LangChain imports
try:
    from langchain_core.language_models import BaseLanguageModel
    from langchain_openai import ChatOpenAI
    from langchain_community.llms import Ollama
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_core.prompts import ChatPromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    BaseLanguageModel = None


@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    provider: str = "ollama"  # ollama, openai, anthropic, huggingface
    model: str = "Artifact_Virtual/raegen:latest" 
    temperature: float = 0.1
    max_tokens: int = 4096
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30


@dataclass
class CodeGenerationRequest:
    """Request for code generation"""
    project_name: str
    description: str
    requirements: Dict[str, Any]
    file_structure: Optional[Dict[str, Any]] = None
    custom_instructions: Optional[str] = None
    target_language: str = "python"
    framework: Optional[str] = None


@dataclass
class GeneratedCode:
    """Generated code response"""
    files: Dict[str, str]  # filename -> content
    structure: Dict[str, Any]  # directory structure
    dependencies: List[str]  # required packages
    instructions: str  # setup/usage instructions
    metadata: Dict[str, Any]  # additional info


class LLMProvider:
    """Base LLM provider interface"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.llm = None
        
    async def initialize(self) -> bool:
        """Initialize the LLM connection"""
        raise NotImplementedError
        
    async def generate_code(self, request: CodeGenerationRequest) -> GeneratedCode:
        """Generate code based on request"""
        raise NotImplementedError
        
    async def generate_file_structure(self, request: CodeGenerationRequest) -> Dict[str, Any]:
        """Generate project file structure"""
        raise NotImplementedError


class OllamaProvider(LLMProvider):
    """Ollama LLM provider"""
    
    async def initialize(self) -> bool:
        """Initialize Ollama connection"""
        try:
            if not LANGCHAIN_AVAILABLE:
                self.logger.error("LangChain not available")
                return False
                
            # Check if Ollama is running
            if not await self._check_ollama_service():
                self.logger.error("Ollama service not running")
                return False
                
            # Check if model is available
            if not await self._check_model_available():
                self.logger.info(f"Pulling model: {self.config.model}")
                await self._pull_model()
                
            self.llm = Ollama(
                model=self.config.model,
                temperature=self.config.temperature,
                num_predict=self.config.max_tokens
            )
            
            # Test connection
            test_response = await self._test_connection()
            if not test_response:
                return False
                
            self.logger.info(f"Ollama provider initialized with model: {self.config.model}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Ollama: {str(e)}")
            return False
            
    async def _check_ollama_service(self) -> bool:
        """Check if Ollama service is running"""
        try:
            result = await asyncio.create_subprocess_exec(
                "ollama", "list",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            return result.returncode == 0
        except Exception:
            return False
            
    async def _check_model_available(self) -> bool:
        """Check if the model is available locally"""
        try:
            result = await asyncio.create_subprocess_exec(
                "ollama", "list",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            if result.returncode == 0:
                models = stdout.decode().lower()
                return self.config.model.lower() in models
            return False
        except Exception:
            return False
            
    async def _pull_model(self) -> bool:
        """Pull the model if not available"""
        try:
            process = await asyncio.create_subprocess_exec(
                "ollama", "pull", self.config.model,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            return process.returncode == 0
        except Exception as e:
            self.logger.error(f"Failed to pull model: {str(e)}")
            return False
            
    async def _test_connection(self) -> bool:
        """Test LLM connection"""
        try:
            response = self.llm.invoke("Hello, respond with 'OK' if you can hear me.")
            return "OK" in response.upper()
        except Exception as e:
            self.logger.error(f"LLM test failed: {str(e)}")
            return False
            
    async def generate_code(self, request: CodeGenerationRequest) -> GeneratedCode:
        """Generate code using Ollama"""
        try:
            # Create comprehensive prompt
            prompt = self._create_code_generation_prompt(request)
            
            # Generate response
            response = self.llm.invoke(prompt)
            
            # Parse response into structured format
            generated_code = self._parse_code_response(response, request)
            
            return generated_code
            
        except Exception as e:
            self.logger.error(f"Code generation failed: {str(e)}")
            return GeneratedCode(
                files={},
                structure={},
                dependencies=[],
                instructions=f"Error: {str(e)}",
                metadata={"error": True}
            )
            
    async def generate_file_structure(self, request: CodeGenerationRequest) -> Dict[str, Any]:
        """Generate project file structure"""
        try:
            prompt = self._create_structure_prompt(request)
            response = self.llm.invoke(prompt)
            structure = self._parse_structure_response(response)
            return structure
        except Exception as e:
            self.logger.error(f"Structure generation failed: {str(e)}")
            return {}
            
    def _create_code_generation_prompt(self, request: CodeGenerationRequest) -> str:
        """Create prompt for code generation"""
        prompt = f"""
You are an expert software developer. Generate a complete, production-ready implementation for the following project:

PROJECT: {request.project_name}
DESCRIPTION: {request.description}
LANGUAGE: {request.target_language}
FRAMEWORK: {request.framework or "Standard library"}

REQUIREMENTS:
{json.dumps(request.requirements, indent=2)}

CUSTOM INSTRUCTIONS:
{request.custom_instructions or "Follow best practices"}

Generate a complete project with:
1. All necessary files with full implementation
2. Clear directory structure
3. Dependencies list
4. Setup and usage instructions
5. Error handling and logging
6. Documentation and comments

Format your response as JSON:
{{
    "files": {{
        "filename1.py": "file content here",
        "filename2.py": "file content here"
    }},
    "structure": {{
        "project_root/": {{
            "src/": {{}},
            "tests/": {{}},
            "docs/": {{}}
        }}
    }},
    "dependencies": ["package1", "package2"],
    "instructions": "Step by step setup instructions",
    "metadata": {{
        "language": "{request.target_language}",
        "framework": "{request.framework}",
        "version": "1.0.0"
    }}
}}

Generate ONLY the JSON response with complete, working code.
"""
        return prompt
        
    def _create_structure_prompt(self, request: CodeGenerationRequest) -> str:
        """Create prompt for file structure generation"""
        prompt = f"""
Generate an optimal file structure for this project:

PROJECT: {request.project_name}
DESCRIPTION: {request.description}
LANGUAGE: {request.target_language}
FRAMEWORK: {request.framework or "Standard"}

Return ONLY a JSON object representing the directory structure:
{{
    "project_name/": {{
        "src/": {{
            "main.py": null,
            "utils/": {{
                "__init__.py": null
            }}
        }},
        "tests/": {{}},
        "docs/": {{}},
        "requirements.txt": null,
        "README.md": null
    }}
}}
"""
        return prompt
        
    def _parse_code_response(self, response: str, request: CodeGenerationRequest) -> GeneratedCode:
        """Parse LLM response into GeneratedCode object"""
        try:
            # Try to extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)
                
                return GeneratedCode(
                    files=data.get('files', {}),
                    structure=data.get('structure', {}),
                    dependencies=data.get('dependencies', []),
                    instructions=data.get('instructions', ''),
                    metadata=data.get('metadata', {})
                )
            else:
                # Fallback: create basic structure
                return self._create_fallback_code(request)
                
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse JSON response, using fallback")
            return self._create_fallback_code(request)
            
    def _parse_structure_response(self, response: str) -> Dict[str, Any]:
        """Parse structure response"""
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
            else:
                return {}
        except json.JSONDecodeError:
            return {}
            
    def _create_fallback_code(self, request: CodeGenerationRequest) -> GeneratedCode:
        """Create fallback code structure"""
        return GeneratedCode(
            files={
                "main.py": f"""#!/usr/bin/env python3
\"""
{request.project_name}
{request.description}
\"""

import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    \"""Main function\"""
    logger.info("Starting {request.project_name}")
    
    # TODO: Implement main functionality
    print("Hello from {request.project_name}!")
    
    logger.info("Completed successfully")

if __name__ == "__main__":
    main()
""",
                "requirements.txt": "# Add dependencies here\n",
                "README.md": f"""# {request.project_name}

{request.description}

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```
"""
            },
            structure={
                f"{request.project_name}/": {
                    "main.py": None,
                    "requirements.txt": None,
                    "README.md": None
                }
            },
            dependencies=[],
            instructions="1. Install dependencies\n2. Run main.py",
            metadata={"fallback": True}
        )


class OpenAIProvider(LLMProvider):
    """OpenAI provider (fallback)"""
    
    async def initialize(self) -> bool:
        """Initialize OpenAI"""
        try:
            if not LANGCHAIN_AVAILABLE:
                return False
                
            api_key = self.config.api_key or os.getenv('OPENAI_API_KEY')
            if not api_key:
                self.logger.error("OpenAI API key not found")
                return False
                
            self.llm = ChatOpenAI(
                model=self.config.model,
                api_key=api_key,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI: {str(e)}")
            return False
            
    async def generate_code(self, request: CodeGenerationRequest) -> GeneratedCode:
        """Generate code using OpenAI"""
        # Similar implementation to Ollama but with ChatOpenAI
        # Implementation would be similar to OllamaProvider
        pass
        
    async def generate_file_structure(self, request: CodeGenerationRequest) -> Dict[str, Any]:
        """Generate file structure using OpenAI"""
        pass


class LLMManager:
    """Manages LLM providers and code generation"""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or self._load_default_config()
        self.provider = None
        self.logger = logging.getLogger(__name__)
        
    def _load_default_config(self) -> LLMConfig:
        """Load default configuration"""
        config_path = Path(__file__).parent / "llm_config.json"
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                return LLMConfig(**data)
            except Exception:
                pass
                
        return LLMConfig()  # Use defaults
        
    async def initialize(self) -> bool:
        """Initialize the LLM manager"""
        try:
            # Try providers in order of preference
            providers = [
                ("ollama", OllamaProvider),
                ("openai", OpenAIProvider)
            ]
            
            for provider_name, provider_class in providers:
                if self.config.provider == provider_name or self.config.provider == "auto":
                    self.provider = provider_class(self.config)
                    if await self.provider.initialize():
                        self.logger.info(f"Successfully initialized {provider_name} provider")
                        return True
                    else:
                        self.logger.warning(f"Failed to initialize {provider_name} provider")
                        
            self.logger.error("No LLM providers could be initialized")
            return False
            
        except Exception as e:
            self.logger.error(f"LLM manager initialization failed: {str(e)}")
            return False
            
    async def generate_project(self, request: CodeGenerationRequest) -> GeneratedCode:
        """Generate complete project"""
        if not self.provider:
            raise RuntimeError("LLM provider not initialized")
            
        self.logger.info(f"Generating project: {request.project_name}")
        generated_code = await self.provider.generate_code(request)
        
        if generated_code.files:
            self.logger.info(f"Generated {len(generated_code.files)} files")
        else:
            self.logger.warning("No files generated")
            
        return generated_code
        
    async def generate_structure(self, request: CodeGenerationRequest) -> Dict[str, Any]:
        """Generate project structure only"""
        if not self.provider:
            raise RuntimeError("LLM provider not initialized")
            
        return await self.provider.generate_file_structure(request)
        
    def save_config(self, config_path: Optional[Path] = None):
        """Save current configuration"""
        if not config_path:
            config_path = Path(__file__).parent / "llm_config.json"
            
        try:
            with open(config_path, 'w') as f:
                json.dump(asdict(self.config), f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save config: {str(e)}")
            
    async def generate_with_prompt(self, prompt: str) -> str:
        """Generate response from a simple prompt"""
        if not self.provider:
            raise RuntimeError("LLM provider not initialized")
            
        try:
            # Use the provider's LLM directly for simple generation
            if hasattr(self.provider, 'llm') and self.provider.llm:
                response = self.provider.llm.invoke(prompt)
                return response
            else:
                raise RuntimeError("Provider LLM not available")
                
        except Exception as e:
            self.logger.error(f"Prompt generation failed: {str(e)}")
            raise


# Convenience functions
async def create_llm_manager(config: Optional[LLMConfig] = None) -> LLMManager:
    """Create and initialize LLM manager"""
    manager = LLMManager(config)
    await manager.initialize()
    return manager


def create_code_request(project_name: str, description: str, **kwargs) -> CodeGenerationRequest:
    """Create a code generation request"""
    return CodeGenerationRequest(
        project_name=project_name,
        description=description,
        requirements=kwargs.get('requirements', {}),
        custom_instructions=kwargs.get('custom_instructions'),
        target_language=kwargs.get('target_language', 'python'),
        framework=kwargs.get('framework')
    )


# Example usage
async def main():
    """Example usage"""
    # Create configuration
    config = LLMConfig(
        provider="ollama",
        model="Artifact_Virtual/raegen:latest",
        temperature=0.1
    )
    
    # Initialize manager
    manager = LLMManager(config)
    if not await manager.initialize():
        print("Failed to initialize LLM manager")
        return
        
    # Create request
    request = create_code_request(
        project_name="data_processor",
        description="A data processing agent that handles CSV and JSON files",
        requirements={
            "programming_languages": ["python"],
            "frameworks": ["pandas"],
            "features": ["file_processing", "data_validation"]
        },
        custom_instructions="Include comprehensive error handling and logging"
    )
    
    # Generate code
    result = await manager.generate_project(request)
    
    print(f"Generated {len(result.files)} files:")
    for filename in result.files.keys():
        print(f"  - {filename}")


if __name__ == "__main__":
    asyncio.run(main())
