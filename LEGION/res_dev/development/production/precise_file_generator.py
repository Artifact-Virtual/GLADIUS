#!/usr/bin/env python3
"""
Precise File Structure Generator
Advanced LLM-powered file structure and code generation with precise control
"""

import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from llm_provider import LLMManager


@dataclass
class FileSpec:
    """Specification for a single file"""
    name: str
    path: str
    type: str  # py, md, txt, json, yml, dockerfile, etc.
    content: str
    description: str
    is_executable: bool = False
    permissions: str = "644"


@dataclass
class ProjectSpec:
    """Complete project specification"""
    name: str
    description: str
    language: str
    framework: Optional[str]
    project_type: str
    version: str
    author: str
    license: str

    # Structure specifications
    files: List[FileSpec]
    directories: List[str]
    dependencies: List[str]
    dev_dependencies: List[str]

    # Meta information
    readme_content: str
    setup_instructions: str
    usage_examples: str
    api_documentation: str

    # Configuration
    include_tests: bool = True
    include_docs: bool = True
    include_config: bool = True
    include_ci_cd: bool = False
    include_docker: bool = False


class PreciseFileGenerator:
    """Generates precise file structures using advanced LLM prompting"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.llm_manager = LLMManager()
        self.config_path = config_path
        self.templates = self._load_file_templates()
        
    def _load_file_templates(self) -> Dict[str, str]:
        """Load file templates for different types"""
        return {
            "python_main": '''#!/usr/bin/env python3
"""
{description}
"""

import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class {class_name}:
    """Main {project_name} class"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Initializing {project_name}")
    
    def run(self):
        """Main execution method"""
        self.logger.info("Starting {project_name}")
        
        # TODO: Implement main functionality
        
        self.logger.info("Completed successfully")


def main():
    """Entry point"""
    try:
        app = {class_name}()
        app.run()
    except Exception as e:
        logger.error(f"Error: {{e}}")
        sys.exit(1)


if __name__ == "__main__":
    main()
''',
            
            "python_test": '''#!/usr/bin/env python3
"""
Tests for {project_name}
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from {module_name} import {class_name}


class Test{class_name}(unittest.TestCase):
    """Test cases for {class_name}"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.app = {class_name}()
    
    def test_initialization(self):
        """Test proper initialization"""
        self.assertIsNotNone(self.app)
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        # TODO: Add specific tests
        pass


if __name__ == "__main__":
    unittest.main()
''',
            
            "requirements": '''# Production dependencies
{dependencies}

# Development dependencies (install with: pip install -r requirements-dev.txt)
''',
            
            "requirements_dev": '''# Development dependencies
pytest>=7.0.0
pytest-cov>=4.0.0
black>=22.0.0
flake8>=5.0.0
mypy>=0.991
pre-commit>=2.20.0
''',
            
            "readme": '''# {project_name}

{description}

## Features

{features}

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd {project_name}

# Install dependencies
pip install -r requirements.txt
```

## Usage

{usage_examples}

## Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest

# Run linting
flake8 src/
black src/
```

## License

{license}

## Author

{author}
''',
            
            "dockerfile": '''FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY *.py ./

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose port (if web application)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD python -c "print('healthy')" || exit 1

# Run application
CMD ["python", "main.py"]
''',
            
            "gitignore": '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Environment variables
.env
.env.local

# Database
*.db
*.sqlite

# Cache
.cache/
.pytest_cache/

# Coverage
.coverage
htmlcov/
''',
            
            "setup_py": '''#!/usr/bin/env python3
"""
Setup script for {project_name}
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text().strip().split('\\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="{project_name}",
    version="{version}",
    description="{description}",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="{author}",
    packages=find_packages(where="src"),
    package_dir={{"": "src"}},
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={{
        "console_scripts": [
            "{project_name}={module_name}.main:main",
        ],
    }},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
'''
        }
    
    async def generate_precise_project(
        self, 
        project_name: str,
        description: str,
        requirements: Dict[str, Any],
        custom_instructions: Optional[str] = None
    ) -> ProjectSpec:
        """Generate a precise project specification"""
        
        self.logger.info(f"Generating precise project: {project_name}")
        
        # Initialize LLM
        await self.llm_manager.initialize()
        
        # Create detailed prompt for project generation
        prompt = self._create_precise_generation_prompt(
            project_name, description, requirements, custom_instructions
        )
        
        # Generate project specification
        try:
            response = await self.llm_manager.generate_with_prompt(prompt)
            project_spec = self._parse_project_specification(response, project_name)
            
            # Enhance with templates
            enhanced_spec = await self._enhance_with_templates(project_spec)
            
            self.logger.info(f"Generated {len(enhanced_spec.files)} files")
            return enhanced_spec
            
        except Exception as e:
            self.logger.error(f"Failed to generate project: {e}")
            return self._create_fallback_project(project_name, description)
    
    def _create_precise_generation_prompt(
        self,
        project_name: str,
        description: str, 
        requirements: Dict[str, Any],
        custom_instructions: Optional[str]
    ) -> str:
        """Create a precise prompt for project generation"""
        
        prompt = f"""You are an expert software architect and developer. Generate a complete, production-ready project specification.

PROJECT DETAILS:
- Name: {project_name}
- Description: {description}
- Language: {requirements.get('language', 'python')}
- Framework: {requirements.get('framework', 'standard')}
- Type: {requirements.get('project_type', 'automated_agent')}

REQUIREMENTS:
{json.dumps(requirements, indent=2)}

CUSTOM INSTRUCTIONS:
{custom_instructions or 'Follow Python best practices'}

Generate a complete project with precise specifications. Return ONLY a JSON object with this exact structure:

{{
    "project_info": {{
        "name": "{project_name}",
        "description": "detailed description",
        "language": "python",
        "framework": "framework_name",
        "project_type": "type",
        "version": "1.0.0",
        "author": "Artifact Virtual",
        "license": "MIT"
    }},
    "directory_structure": {{
        "src/": {{
            "{project_name}/": {{
                "__init__.py": {{"type": "python", "description": "Package initialization"}},
                "main.py": {{"type": "python", "description": "Main application entry point"}},
                "core.py": {{"type": "python", "description": "Core functionality"}},
                "utils.py": {{"type": "python", "description": "Utility functions"}},
                "config.py": {{"type": "python", "description": "Configuration management"}}
            }}
        }},
        "tests/": {{
            "__init__.py": {{"type": "python", "description": "Test package init"}},
            "test_main.py": {{"type": "python", "description": "Main functionality tests"}},
            "test_core.py": {{"type": "python", "description": "Core functionality tests"}}
        }},
        "docs/": {{
            "README.md": {{"type": "markdown", "description": "Project documentation"}},
            "API.md": {{"type": "markdown", "description": "API documentation"}}
        }},
        "config/": {{
            "settings.json": {{"type": "json", "description": "Application settings"}},
            "logging.yml": {{"type": "yaml", "description": "Logging configuration"}}
        }}
    }},
    "root_files": {{
        "requirements.txt": {{"type": "text", "description": "Python dependencies"}},
        "requirements-dev.txt": {{"type": "text", "description": "Development dependencies"}},
        "setup.py": {{"type": "python", "description": "Package setup script"}},
        "README.md": {{"type": "markdown", "description": "Main project README"}},
        ".gitignore": {{"type": "text", "description": "Git ignore file"}},
        "Dockerfile": {{"type": "dockerfile", "description": "Docker container definition"}},
        "pyproject.toml": {{"type": "toml", "description": "Python project configuration"}}
    }},
    "dependencies": {{
        "production": ["requests", "pydantic", "click"],
        "development": ["pytest", "black", "flake8", "mypy"]
    }},
    "file_contents": {{
        "src/{project_name}/main.py": "# Complete main.py implementation\\nfrom .core import CoreEngine\\n\\ndef main():\\n    engine = CoreEngine()\\n    engine.run()\\n\\nif __name__ == '__main__':\\n    main()",
        "src/{project_name}/core.py": "# Complete core.py implementation\\nclass CoreEngine:\\n    def __init__(self):\\n        pass\\n    def run(self):\\n        print('Running core engine')"
    }},
    "setup_instructions": "1. Install Python 3.8+\\n2. Create virtual environment\\n3. Install dependencies\\n4. Run tests\\n5. Execute main application",
    "usage_examples": "python -m {project_name}.main\\npython setup.py install",
    "features": ["Feature 1", "Feature 2", "Feature 3"]
}}

Requirements for code generation:
1. All files must have complete, working implementations
2. Include proper error handling and logging
3. Follow PEP 8 style guidelines
4. Add comprehensive docstrings
5. Include type hints where appropriate
6. Create modular, maintainable code
7. Add configuration management
8. Include proper test coverage
9. Generate production-ready code only

Generate ONLY the JSON response with complete implementations.
"""
        return prompt
    
    def _parse_project_specification(self, response: str, project_name: str) -> ProjectSpec:
        """Parse LLM response into ProjectSpec"""
        try:
            # Extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                data = json.loads(json_str)
                
                # Extract project info
                project_info = data.get('project_info', {})
                
                # Parse directory structure and files
                files = []
                directories = []
                
                # Process directory structure
                dir_struct = data.get('directory_structure', {})
                root_files = data.get('root_files', {})
                file_contents = data.get('file_contents', {})
                
                # Create file specs
                for file_path, content in file_contents.items():
                    file_spec = FileSpec(
                        name=Path(file_path).name,
                        path=file_path,
                        type=self._get_file_type(file_path),
                        content=content,
                        description=f"Generated file: {file_path}"
                    )
                    files.append(file_spec)
                
                # Extract directories
                directories = self._extract_directories(dir_struct)
                
                # Create project spec
                return ProjectSpec(
                    name=project_info.get('name', project_name),
                    description=project_info.get('description', ''),
                    language=project_info.get('language', 'python'),
                    framework=project_info.get('framework'),
                    project_type=project_info.get('project_type', 'application'),
                    version=project_info.get('version', '1.0.0'),
                    author=project_info.get('author', 'Artifact Virtual'),
                    license=project_info.get('license', 'MIT'),
                    files=files,
                    directories=directories,
                    dependencies=data.get('dependencies', {}).get('production', []),
                    dev_dependencies=data.get('dependencies', {}).get('development', []),
                    readme_content=self._generate_readme_content(data),
                    setup_instructions=data.get('setup_instructions', ''),
                    usage_examples=data.get('usage_examples', ''),
                    api_documentation=data.get('api_documentation', '')
                )
                
        except Exception as e:
            self.logger.error(f"Failed to parse project spec: {e}")
            
        # Fallback
        return self._create_fallback_project(project_name, "Generated project")
    
    def _get_file_type(self, file_path: str) -> str:
        """Determine file type from path"""
        suffix = Path(file_path).suffix.lower()
        type_map = {
            '.py': 'python',
            '.md': 'markdown', 
            '.txt': 'text',
            '.json': 'json',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.toml': 'toml',
            '.cfg': 'config',
            '.ini': 'config',
            '': 'dockerfile' if 'dockerfile' in file_path.lower() else 'text'
        }
        return type_map.get(suffix, 'text')
    
    def _extract_directories(self, dir_struct: Dict[str, Any]) -> List[str]:
        """Extract directory paths from structure"""
        directories = []
        
        def extract_dirs(struct: Dict[str, Any], base_path: str = ""):
            for key, value in struct.items():
                if key.endswith('/'):
                    # This is a directory
                    dir_path = base_path + key
                    directories.append(dir_path.rstrip('/'))
                    if isinstance(value, dict):
                        extract_dirs(value, dir_path)
        
        extract_dirs(dir_struct)
        return directories
    
    def _generate_readme_content(self, data: Dict[str, Any]) -> str:
        """Generate README content from parsed data"""
        project_info = data.get('project_info', {})
        features = data.get('features', [])
        usage = data.get('usage_examples', '')
        
        return self.templates['readme'].format(
            project_name=project_info.get('name', 'Project'),
            description=project_info.get('description', 'A generated project'),
            features='\n'.join(f"- {feature}" for feature in features),
            usage_examples=usage,
            license=project_info.get('license', 'MIT'),
            author=project_info.get('author', 'Artifact Virtual')
        )
    
    async def _enhance_with_templates(self, spec: ProjectSpec) -> ProjectSpec:
        """Enhance project spec with template-based files"""
        enhanced_files = []
        
        for file_spec in spec.files:
            # If file content is basic, enhance with template
            if len(file_spec.content.strip()) < 50:  # Basic placeholder
                enhanced_content = self._apply_template(file_spec, spec)
                if enhanced_content:
                    file_spec.content = enhanced_content
            
            enhanced_files.append(file_spec)
        
        # Add missing essential files
        essential_files = self._generate_essential_files(spec)
        for essential_file in essential_files:
            if not any(f.path == essential_file.path for f in enhanced_files):
                enhanced_files.append(essential_file)
        
        spec.files = enhanced_files
        return spec
    
    def _apply_template(self, file_spec: FileSpec, spec: ProjectSpec) -> Optional[str]:
        """Apply appropriate template to file"""
        template_map = {
            'main.py': 'python_main',
            'test_': 'python_test',
            'requirements.txt': 'requirements',
            'requirements-dev.txt': 'requirements_dev',
            'README.md': 'readme',
            'Dockerfile': 'dockerfile',
            '.gitignore': 'gitignore',
            'setup.py': 'setup_py'
        }
        
        for pattern, template_name in template_map.items():
            if pattern in file_spec.name:
                if template_name in self.templates:
                    return self._format_template(
                        self.templates[template_name], spec, file_spec
                    )
        
        return None
    
    def _format_template(self, template: str, spec: ProjectSpec, file_spec: FileSpec) -> str:
        """Format template with project data"""
        class_name = ''.join(word.capitalize() for word in spec.name.split('_'))
        module_name = spec.name.lower().replace('-', '_')
        
        return template.format(
            project_name=spec.name,
            description=spec.description,
            class_name=class_name,
            module_name=module_name,
            version=spec.version,
            author=spec.author,
            license=spec.license,
            dependencies='\n'.join(spec.dependencies),
            features='\n'.join(f"- Feature {i+1}" for i in range(3)),
            usage_examples=spec.usage_examples or f"python -m {module_name}"
        )
    
    def _generate_essential_files(self, spec: ProjectSpec) -> List[FileSpec]:
        """Generate essential project files"""
        essential = []
        
        # Requirements file
        if not any('requirements.txt' in f.path for f in spec.files):
            essential.append(FileSpec(
                name="requirements.txt",
                path="requirements.txt",
                type="text",
                content='\n'.join(spec.dependencies) + '\n',
                description="Python dependencies"
            ))
        
        # README
        if not any('README.md' in f.path for f in spec.files):
            essential.append(FileSpec(
                name="README.md",
                path="README.md", 
                type="markdown",
                content=spec.readme_content,
                description="Project documentation"
            ))
        
        # .gitignore
        essential.append(FileSpec(
            name=".gitignore",
            path=".gitignore",
            type="text",
            content=self.templates['gitignore'],
            description="Git ignore file"
        ))
        
        return essential
    
    def _create_fallback_project(self, name: str, description: str) -> ProjectSpec:
        """Create fallback project specification"""
        class_name = ''.join(word.capitalize() for word in name.split('_'))
        
        files = [
            FileSpec(
                name="main.py",
                path="src/main.py",
                type="python",
                content=self._format_template(
                    self.templates['python_main'],
                    ProjectSpec(
                        name=name, description=description, language="python",
                        framework=None, project_type="application", 
                        version="1.0.0", author="Artifact Virtual", license="MIT",
                        files=[], directories=[], dependencies=[], dev_dependencies=[],
                        readme_content="", setup_instructions="", usage_examples="",
                        api_documentation=""
                    ),
                    None
                ),
                description="Main application file"
            ),
            FileSpec(
                name="requirements.txt",
                path="requirements.txt",
                type="text", 
                content="# Add dependencies here\n",
                description="Python dependencies"
            )
        ]
        
        return ProjectSpec(
            name=name,
            description=description,
            language="python",
            framework=None,
            project_type="application",
            version="1.0.0",
            author="Artifact Virtual", 
            license="MIT",
            files=files,
            directories=["src/", "tests/", "docs/"],
            dependencies=[],
            dev_dependencies=["pytest", "black", "flake8"],
            readme_content=f"# {name}\n\n{description}",
            setup_instructions="1. Install dependencies\n2. Run application",
            usage_examples=f"python src/main.py",
            api_documentation=""
        )
    
    async def create_project_files(self, spec: ProjectSpec, output_dir: Path) -> bool:
        """Create actual project files from specification"""
        try:
            self.logger.info(f"Creating project files in: {output_dir}")
            
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create directories
            for directory in spec.directories:
                dir_path = output_dir / directory
                dir_path.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"Created directory: {dir_path}")
            
            # Create files
            for file_spec in spec.files:
                file_path = output_dir / file_spec.path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write file content
                file_path.write_text(file_spec.content, encoding='utf-8')
                
                # Set executable if needed
                if file_spec.is_executable:
                    file_path.chmod(0o755)
                
                self.logger.debug(f"Created file: {file_path}")
            
            # Create project summary
            summary_path = output_dir / "PROJECT_SUMMARY.json"
            summary_data = {
                "generated_at": datetime.now().isoformat(),
                "project_spec": asdict(spec),
                "file_count": len(spec.files),
                "directory_count": len(spec.directories)
            }
            summary_path.write_text(json.dumps(summary_data, indent=2))
            
            self.logger.info(f"Successfully created {len(spec.files)} files and {len(spec.directories)} directories")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create project files: {e}")
            return False


# Testing and validation functions
async def test_precise_generation():
    """Test the precise file generator"""
    generator = PreciseFileGenerator()
    
    # Test project generation
    spec = await generator.generate_precise_project(
        project_name="test_agent",
        description="A test automated agent for data processing",
        requirements={
            "language": "python",
            "framework": "asyncio",
            "project_type": "automated_agent",
            "features": ["data_processing", "file_handling", "logging"]
        },
        custom_instructions="Create a production-ready agent with error handling"
    )
    
    print(f"Generated project: {spec.name}")
    print(f"Files: {len(spec.files)}")
    print(f"Directories: {len(spec.directories)}")
    
    # Create project files
    output_dir = Path("generated_projects") / spec.name
    success = await generator.create_project_files(spec, output_dir)
    
    if success:
        print(f"Project created successfully in: {output_dir}")
    else:
        print("Failed to create project files")


if __name__ == "__main__":
    asyncio.run(test_precise_generation())
