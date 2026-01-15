#!/usr/bin/env python3
"""
LLM-Enhanced Production Agents
Integrates LLM capabilities with the production pipeline
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

# Import our LLM provider
from llm_provider import (
    LLMManager, 
    LLMConfig, 
    CodeGenerationRequest, 
    create_code_request
)


class LLMEnhancedAgent:
    """Base class for LLM-enhanced production agents"""
    
    def __init__(self, agent_name: str, llm_manager: LLMManager):
        self.agent_name = agent_name
        self.llm_manager = llm_manager
        self.logger = logging.getLogger(f"{__name__}.{agent_name}")
        
    async def generate_implementation(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate implementation using LLM"""
        raise NotImplementedError


class LLMRequirementsAgent(LLMEnhancedAgent):
    """Requirements analysis agent with LLM support"""
    
    async def analyze_requirements(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and enhance project requirements using LLM"""
        try:
            # Create requirements analysis prompt
            prompt = f"""
Analyze the following project requirements and provide detailed specifications:

PROJECT: {project_data.get('name', 'Unknown')}
DESCRIPTION: {project_data.get('description', '')}
TYPE: {project_data.get('type', 'automated_agent')}

Existing Requirements:
{json.dumps(project_data.get('requirements', {}), indent=2)}

Generate comprehensive technical specifications including:
1. Detailed functional requirements
2. Technical architecture recommendations  
3. Dependencies and libraries needed
4. File structure suggestions
5. Implementation phases
6. Testing requirements
7. Documentation needs

Return as JSON with this structure:
{{
    "functional_requirements": [...],
    "technical_requirements": {{
        "architecture": "...",
        "dependencies": [...],
        "frameworks": [...]
    }},
    "file_structure": {{...}},
    "implementation_phases": [...],
    "testing_strategy": "...",
    "documentation_needs": [...]
}}
"""
            
            # Use LLM to analyze requirements
            request = CodeGenerationRequest(
                project_name=project_data.get('name', 'project'),
                description=prompt,
                requirements=project_data.get('requirements', {}),
                target_language='python'
            )
            
            result = await self.llm_manager.generate_project(request)
            
            # Parse enhanced requirements from LLM response
            enhanced_requirements = self._parse_requirements_response(result.instructions)
            
            return {
                'status': 'completed',
                'enhanced_requirements': enhanced_requirements,
                'suggested_structure': result.structure,
                'dependencies': result.dependencies,
                'metadata': result.metadata
            }
            
        except Exception as e:
            self.logger.error(f"Requirements analysis failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'fallback_requirements': project_data.get('requirements', {})
            }
            
    def _parse_requirements_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM requirements response"""
        try:
            # Try to extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
            else:
                return {'parsed': False, 'raw_response': response}
        except json.JSONDecodeError:
            return {'parsed': False, 'raw_response': response}


class LLMPlanningAgent(LLMEnhancedAgent):
    """Planning agent with LLM support"""
    
    async def create_implementation_plan(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed implementation plan using LLM"""
        try:
            prompt = f"""
Create a detailed implementation plan for this project:

REQUIREMENTS:
{json.dumps(requirements, indent=2)}

Generate a comprehensive implementation plan including:
1. Project structure and organization
2. Implementation phases with timelines
3. File-by-file implementation order
4. Dependencies and setup requirements
5. Testing approach and test files needed
6. Deployment and distribution strategy
7. Documentation plan

Return as JSON with this structure:
{{
    "project_structure": {{
        "directories": [...],
        "core_files": [...],
        "test_files": [...],
        "doc_files": [...]
    }},
    "implementation_phases": [
        {{
            "phase": 1,
            "name": "Core Setup",
            "files": [...],
            "estimated_time": "...",
            "dependencies": [...]
        }}
    ],
    "file_order": [...],
    "setup_requirements": [...],
    "testing_strategy": {{...}},
    "deployment_plan": {{...}}
}}
"""
            
            request = create_code_request(
                project_name="implementation_plan",
                description=prompt,
                requirements=requirements
            )
            
            result = await self.llm_manager.generate_structure(request)
            
            return {
                'status': 'completed',
                'implementation_plan': result,
                'estimated_files': len(result.get('core_files', [])),
                'phases': result.get('implementation_phases', [])
            }
            
        except Exception as e:
            self.logger.error(f"Planning failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'fallback_plan': self._create_basic_plan(requirements)
            }
            
    def _create_basic_plan(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create basic fallback plan"""
        return {
            "project_structure": {
                "directories": ["src", "tests", "docs"],
                "core_files": ["main.py", "requirements.txt", "README.md"],
                "test_files": ["test_main.py"],
                "doc_files": ["README.md"]
            },
            "implementation_phases": [
                {
                    "phase": 1,
                    "name": "Basic Setup",
                    "files": ["main.py", "requirements.txt"],
                    "estimated_time": "1 hour"
                }
            ]
        }


class LLMCodingAgent(LLMEnhancedAgent):
    """Coding agent with LLM support"""
    
    async def generate_code_files(self, plan: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actual code files using LLM"""
        try:
            # Extract project details
            project_name = requirements.get('name', 'generated_project')
            description = requirements.get('description', '')
            
            # Create comprehensive code generation request
            request = create_code_request(
                project_name=project_name,
                description=description,
                requirements=requirements,
                custom_instructions=self._create_coding_instructions(plan, requirements)
            )
            
            # Generate code using LLM
            result = await self.llm_manager.generate_project(request)
            
            # Validate and enhance generated code
            validated_files = await self._validate_generated_code(result.files)
            
            return {
                'status': 'completed',
                'generated_files': validated_files,
                'file_structure': result.structure,
                'dependencies': result.dependencies,
                'setup_instructions': result.instructions,
                'metadata': result.metadata
            }
            
        except Exception as e:
            self.logger.error(f"Code generation failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'generated_files': {}
            }
            
    def _create_coding_instructions(self, plan: Dict[str, Any], requirements: Dict[str, Any]) -> str:
        """Create detailed coding instructions for LLM"""
        instructions = f"""
CODING INSTRUCTIONS:

1. Follow the implementation plan phases
2. Include comprehensive error handling and logging
3. Add type hints and docstrings
4. Follow PEP 8 style guidelines
5. Include unit tests for all functions
6. Add configuration file support
7. Implement proper CLI interface if applicable
8. Include comprehensive README with examples

IMPLEMENTATION PLAN:
{json.dumps(plan, indent=2)}

SPECIFIC REQUIREMENTS:
- Target Language: {requirements.get('target_language', 'python')}
- Framework: {requirements.get('framework', 'standard library')}
- Agent Types: {requirements.get('agent_types', [])}
- Custom Instructions: {requirements.get('custom_instructions', '')}

Generate production-ready, well-documented code with proper structure.
"""
        return instructions
        
    async def _validate_generated_code(self, files: Dict[str, str]) -> Dict[str, str]:
        """Validate and potentially fix generated code"""
        validated_files = {}
        
        for filename, content in files.items():
            try:
                # Basic validation for Python files
                if filename.endswith('.py'):
                    # Check for basic syntax issues
                    compile(content, filename, 'exec')
                    
                # Add file to validated set
                validated_files[filename] = content
                
            except SyntaxError as e:
                self.logger.warning(f"Syntax error in {filename}: {str(e)}")
                # Try to fix common issues or skip file
                validated_files[filename] = self._fix_syntax_issues(content, filename)
            except Exception as e:
                self.logger.warning(f"Validation error in {filename}: {str(e)}")
                validated_files[filename] = content  # Include anyway with warning
                
        return validated_files
        
    def _fix_syntax_issues(self, content: str, filename: str) -> str:
        """Attempt to fix common syntax issues"""
        # Add basic fixes for common LLM generation issues
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Remove incomplete triple quotes
            if line.count('"""') == 1 and not any(prev.count('"""') % 2 for prev in fixed_lines):
                line = line.replace('"""', '')
            
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)


class LLMTestingAgent(LLMEnhancedAgent):
    """Testing agent with LLM support"""
    
    async def generate_tests(self, code_files: Dict[str, str], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive tests using LLM"""
        try:
            # Create test generation prompt
            prompt = f"""
Generate comprehensive unit tests for the following code files:

PROJECT: {requirements.get('name', 'Unknown')}

CODE FILES:
{json.dumps({k: v[:500] + "..." if len(v) > 500 else v for k, v in code_files.items()}, indent=2)}

Generate tests that cover:
1. Unit tests for all functions and classes
2. Integration tests for key workflows
3. Error handling and edge cases
4. Performance tests where applicable
5. Mock tests for external dependencies

Return test files in this format:
{{
    "test_main.py": "complete test file content",
    "test_utils.py": "complete test file content",
    "conftest.py": "pytest configuration"
}}

Use pytest framework with proper fixtures and mocking.
"""
            
            request = create_code_request(
                project_name="test_generation",
                description=prompt,
                requirements=requirements,
                target_language="python"
            )
            
            result = await self.llm_manager.generate_project(request)
            
            return {
                'status': 'completed',
                'test_files': result.files,
                'test_coverage_plan': self._analyze_test_coverage(result.files, code_files),
                'test_instructions': result.instructions
            }
            
        except Exception as e:
            self.logger.error(f"Test generation failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'test_files': {}
            }
            
    def _analyze_test_coverage(self, test_files: Dict[str, str], code_files: Dict[str, str]) -> Dict[str, Any]:
        """Analyze test coverage"""
        coverage_info = {
            'total_code_files': len(code_files),
            'total_test_files': len(test_files),
            'coverage_ratio': len(test_files) / max(1, len(code_files))
        }
        
        return coverage_info


class LLMDeploymentAgent(LLMEnhancedAgent):
    """Deployment agent with LLM support"""
    
    async def create_deployment_package(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create deployment package using LLM"""
        try:
            prompt = f"""
Create deployment configuration for this project:

PROJECT DATA:
{json.dumps(project_data, indent=2)}

Generate deployment files including:
1. Dockerfile for containerization
2. docker-compose.yml for multi-service setup
3. requirements.txt with pinned versions
4. setup.py for package distribution
5. CI/CD configuration (.github/workflows)
6. Environment configuration files
7. Deployment documentation

Return as JSON with file contents.
"""
            
            request = create_code_request(
                project_name="deployment_package",
                description=prompt,
                requirements=project_data.get('requirements', {}),
                target_language="yaml"
            )
            
            result = await self.llm_manager.generate_project(request)
            
            return {
                'status': 'completed',
                'deployment_files': result.files,
                'deployment_instructions': result.instructions,
                'deployment_structure': result.structure
            }
            
        except Exception as e:
            self.logger.error(f"Deployment package creation failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e)
            }


class LLMProductionPipeline:
    """Enhanced production pipeline with LLM integration"""
    
    def __init__(self, llm_config: Optional[LLMConfig] = None):
        self.llm_config = llm_config or LLMConfig()
        self.llm_manager = None
        self.agents = {}
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> bool:
        """Initialize the LLM-enhanced pipeline"""
        try:
            # Initialize LLM manager
            self.llm_manager = LLMManager(self.llm_config)
            if not await self.llm_manager.initialize():
                self.logger.error("Failed to initialize LLM manager")
                return False
                
            # Initialize enhanced agents
            self.agents = {
                'requirements': LLMRequirementsAgent('requirements', self.llm_manager),
                'planning': LLMPlanningAgent('planning', self.llm_manager),
                'coding': LLMCodingAgent('coding', self.llm_manager),
                'testing': LLMTestingAgent('testing', self.llm_manager),
                'deployment': LLMDeploymentAgent('deployment', self.llm_manager)
            }
            
            self.logger.info("LLM-enhanced production pipeline initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Pipeline initialization failed: {str(e)}")
            return False
            
    async def process_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process project through LLM-enhanced pipeline"""
        try:
            results = {}
            
            # Phase 1: Requirements Analysis
            self.logger.info("Phase 1: Analyzing requirements...")
            requirements_result = await self.agents['requirements'].analyze_requirements(project_data)
            results['requirements'] = requirements_result
            
            if requirements_result['status'] != 'completed':
                return {'status': 'failed', 'phase': 'requirements', 'results': results}
                
            # Phase 2: Planning
            self.logger.info("Phase 2: Creating implementation plan...")
            enhanced_requirements = requirements_result.get('enhanced_requirements', project_data.get('requirements', {}))
            planning_result = await self.agents['planning'].create_implementation_plan(enhanced_requirements)
            results['planning'] = planning_result
            
            if planning_result['status'] != 'completed':
                return {'status': 'failed', 'phase': 'planning', 'results': results}
                
            # Phase 3: Code Generation
            self.logger.info("Phase 3: Generating code...")
            plan = planning_result.get('implementation_plan', {})
            coding_result = await self.agents['coding'].generate_code_files(plan, enhanced_requirements)
            results['coding'] = coding_result
            
            if coding_result['status'] != 'completed':
                return {'status': 'failed', 'phase': 'coding', 'results': results}
                
            # Phase 4: Test Generation
            self.logger.info("Phase 4: Generating tests...")
            generated_files = coding_result.get('generated_files', {})
            testing_result = await self.agents['testing'].generate_tests(generated_files, enhanced_requirements)
            results['testing'] = testing_result
            
            # Phase 5: Deployment Package
            self.logger.info("Phase 5: Creating deployment package...")
            deployment_result = await self.agents['deployment'].create_deployment_package({
                'code_files': generated_files,
                'test_files': testing_result.get('test_files', {}),
                'requirements': enhanced_requirements,
                'structure': coding_result.get('file_structure', {})
            })
            results['deployment'] = deployment_result
            
            return {
                'status': 'completed',
                'project_name': project_data.get('name', 'unknown'),
                'results': results,
                'total_files_generated': len(generated_files) + len(testing_result.get('test_files', {})) + len(deployment_result.get('deployment_files', {}))
            }
            
        except Exception as e:
            self.logger.error(f"Project processing failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'results': results
            }


# Example usage function
async def test_llm_pipeline():
    """Test the LLM-enhanced pipeline"""
    # Configure LLM
    config = LLMConfig(
        provider="ollama",
        model="Artifact_Virtual/raegen:latest",
        temperature=0.1
    )
    
    # Initialize pipeline
    pipeline = LLMProductionPipeline(config)
    if not await pipeline.initialize():
        print("Failed to initialize pipeline")
        return
        
    # Test project
    test_project = {
        'name': 'smart_file_organizer',
        'description': 'AI-powered file organization system with automatic categorization',
        'type': 'automated_agent',
        'requirements': {
            'programming_languages': ['python'],
            'frameworks': ['pathlib', 'watchdog'],
            'features': ['file_monitoring', 'ai_categorization', 'backup_system'],
            'dependencies': ['watchdog', 'pillow', 'python-magic']
        },
        'custom_instructions': 'Focus on safety and reversibility of operations'
    }
    
    # Process project
    result = await pipeline.process_project(test_project)
    
    print(f"Pipeline result: {result['status']}")
    if result['status'] == 'completed':
        print(f"Generated {result['total_files_generated']} files")
    else:
        print(f"Failed at phase: {result.get('phase', 'unknown')}")


if __name__ == "__main__":
    asyncio.run(test_llm_pipeline())
