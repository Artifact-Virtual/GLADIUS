#!/usr/bin/env python3
"""
LLM-Enhanced Production Crew Integration
Adds LLM capabilities to the existing production pipeline
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

# Import existing production crew components
from intelligent_production_crew import (
    IntelligentProductionCrew,
    ProductionAgent,
    AgentRole,
    ProductionTask,
    TaskStatus
)

# Import our LLM components
from llm_provider import LLMManager, LLMConfig, create_code_request
from llm_enhanced_agents import (
    LLMRequirementsAgent,
    LLMPlanningAgent, 
    LLMCodingAgent,
    LLMTestingAgent,
    LLMDeploymentAgent
)


class LLMEnhancedRequirementsAgent(ProductionAgent):
    """Enhanced requirements agent with LLM capabilities"""
    
    def __init__(self, workspace_root: Path, llm_manager: LLMManager):
        super().__init__("llm_req_agent_001", AgentRole.REQUIREMENTS, workspace_root)
        self.llm_agent = LLMRequirementsAgent('requirements', llm_manager)
        
    async def _execute_task(self, task: ProductionTask) -> Dict[str, Any]:
        """Execute requirements analysis with LLM enhancement"""
        self.logger.info(f"LLM-enhanced requirements analysis for task {task.task_id}")
        
        try:
            # Prepare project data for LLM
            project_data = {
                'name': task.project_name,
                'description': task.description,
                'requirements': task.requirements,
                'type': 'automated_agent'
            }
            
            # Use LLM agent for analysis
            llm_result = await self.llm_agent.analyze_requirements(project_data)
            
            if llm_result['status'] == 'completed':
                # Enhance with LLM insights
                enhanced_requirements = llm_result.get('enhanced_requirements', {})
                suggested_structure = llm_result.get('suggested_structure', {})
                dependencies = llm_result.get('dependencies', [])
                
                return {
                    "requirements_spec": enhanced_requirements,
                    "suggested_structure": suggested_structure,
                    "dependencies": dependencies,
                    "validation_passed": True,
                    "llm_enhanced": True,
                    "recommendations": self._extract_recommendations(enhanced_requirements)
                }
            else:
                # Fallback to traditional analysis
                self.logger.warning("LLM analysis failed, using traditional method")
                return await self._traditional_requirements_analysis(task)
                
        except Exception as e:
            self.logger.error(f"LLM requirements analysis failed: {str(e)}")
            return await self._traditional_requirements_analysis(task)
            
    async def _traditional_requirements_analysis(self, task: ProductionTask) -> Dict[str, Any]:
        """Fallback traditional requirements analysis"""
        return {
            "requirements_spec": task.requirements,
            "validation_passed": True,
            "llm_enhanced": False,
            "recommendations": ["Use traditional development approach"]
        }
        
    def _extract_recommendations(self, enhanced_requirements: Dict[str, Any]) -> List[str]:
        """Extract actionable recommendations from LLM analysis"""
        recommendations = []
        
        if 'technical_requirements' in enhanced_requirements:
            tech_reqs = enhanced_requirements['technical_requirements']
            if 'architecture' in tech_reqs:
                recommendations.append(f"Use {tech_reqs['architecture']} architecture")
            if 'frameworks' in tech_reqs:
                recommendations.append(f"Consider frameworks: {', '.join(tech_reqs['frameworks'])}")
                
        return recommendations


class LLMEnhancedPlanningAgent(ProductionAgent):
    """Enhanced planning agent with LLM capabilities"""
    
    def __init__(self, workspace_root: Path, llm_manager: LLMManager):
        super().__init__("llm_plan_agent_001", AgentRole.PLANNING, workspace_root)
        self.llm_agent = LLMPlanningAgent('planning', llm_manager)
        
    async def _execute_task(self, task: ProductionTask) -> Dict[str, Any]:
        """Execute planning with LLM enhancement"""
        self.logger.info(f"LLM-enhanced planning for task {task.task_id}")
        
        try:
            # Get requirements from previous phase
            requirements_spec = task.deliverables.get("requirements_spec", task.requirements)
            
            # Use LLM agent for planning
            planning_result = await self.llm_agent.create_implementation_plan(requirements_spec)
            
            if planning_result['status'] == 'completed':
                implementation_plan = planning_result.get('implementation_plan', {})
                
                return {
                    "architecture": self._extract_architecture(implementation_plan),
                    "implementation_plan": implementation_plan,
                    "timeline": self._estimate_timeline_from_plan(implementation_plan),
                    "resources": self._estimate_resources_from_plan(implementation_plan),
                    "milestones": self._extract_milestones(implementation_plan),
                    "llm_enhanced": True
                }
            else:
                # Fallback to traditional planning
                return await self._traditional_planning(task)
                
        except Exception as e:
            self.logger.error(f"LLM planning failed: {str(e)}")
            return await self._traditional_planning(task)
            
    async def _traditional_planning(self, task: ProductionTask) -> Dict[str, Any]:
        """Fallback traditional planning"""
        return {
            "architecture": {"type": "simple", "components": []},
            "implementation_plan": {"phases": []},
            "timeline": {"total_duration_days": 5},
            "resources": {"developers_required": 1},
            "milestones": [],
            "llm_enhanced": False
        }
        
    def _extract_architecture(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Extract architecture from LLM plan"""
        return plan.get('project_structure', {})
        
    def _estimate_timeline_from_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate timeline from LLM plan"""
        phases = plan.get('implementation_phases', [])
        total_days = sum(phase.get('estimated_days', 1) for phase in phases)
        
        return {
            "total_duration_days": total_days,
            "phases": phases
        }
        
    def _estimate_resources_from_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate resources from LLM plan"""
        return {
            "developers_required": 1,
            "estimated_hours": plan.get('estimated_hours', 40),
            "skills_required": plan.get('skills_required', ['python']),
            "tools_required": plan.get('tools_required', ['git'])
        }
        
    def _extract_milestones(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract milestones from LLM plan"""
        phases = plan.get('implementation_phases', [])
        milestones = []
        
        for i, phase in enumerate(phases):
            milestones.append({
                "milestone": f"phase_{i+1}_complete",
                "description": phase.get('name', f"Phase {i+1}"),
                "deliverables": phase.get('files', [])
            })
            
        return milestones


class LLMEnhancedCodingAgent(ProductionAgent):
    """Enhanced coding agent with LLM capabilities"""
    
    def __init__(self, workspace_root: Path, llm_manager: LLMManager):
        super().__init__("llm_code_agent_001", AgentRole.CODING, workspace_root)
        self.llm_agent = LLMCodingAgent('coding', llm_manager)
        
    async def _execute_task(self, task: ProductionTask) -> Dict[str, Any]:
        """Execute code generation with LLM"""
        self.logger.info(f"LLM-enhanced code generation for task {task.task_id}")
        
        try:
            # Get plan and requirements from previous phases
            plan = task.deliverables.get("implementation_plan", {})
            requirements = task.deliverables.get("requirements_spec", task.requirements)
            
            # Use LLM agent for code generation
            coding_result = await self.llm_agent.generate_code_files(plan, requirements)
            
            if coding_result['status'] == 'completed':
                generated_files = coding_result.get('generated_files', {})
                
                # Save generated files to workspace
                project_dir = await self._create_project_directory(task.project_name)
                await self._save_generated_files(project_dir, generated_files)
                
                return {
                    "generated_files": generated_files,
                    "file_count": len(generated_files),
                    "project_directory": str(project_dir),
                    "file_structure": coding_result.get('file_structure', {}),
                    "dependencies": coding_result.get('dependencies', []),
                    "setup_instructions": coding_result.get('setup_instructions', ''),
                    "llm_enhanced": True
                }
            else:
                # Fallback to basic code generation
                return await self._basic_code_generation(task)
                
        except Exception as e:
            self.logger.error(f"LLM code generation failed: {str(e)}")
            return await self._basic_code_generation(task)
            
    async def _create_project_directory(self, project_name: str) -> Path:
        """Create project directory in workspace"""
        project_dir = self.workspace_root / "workshop" / "projects" / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir
        
    async def _save_generated_files(self, project_dir: Path, files: Dict[str, str]):
        """Save generated files to project directory"""
        for filename, content in files.items():
            file_path = project_dir / filename
            
            # Create subdirectories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        self.logger.info(f"Saved {len(files)} files to {project_dir}")
        
    async def _basic_code_generation(self, task: ProductionTask) -> Dict[str, Any]:
        """Fallback basic code generation"""
        project_dir = await self._create_project_directory(task.project_name)
        
        # Create basic files
        basic_files = {
            "main.py": f"""#!/usr/bin/env python3
\"""
{task.project_name}
{task.description}
\"""

def main():
    print("Hello from {task.project_name}!")

if __name__ == "__main__":
    main()
""",
            "README.md": f"""# {task.project_name}

{task.description}

## Usage

```bash
python main.py
```
"""
        }
        
        await self._save_generated_files(project_dir, basic_files)
        
        return {
            "generated_files": basic_files,
            "file_count": len(basic_files),
            "project_directory": str(project_dir),
            "llm_enhanced": False
        }


class LLMEnhancedTestingAgent(ProductionAgent):
    """Enhanced testing agent with LLM capabilities"""
    
    def __init__(self, workspace_root: Path, llm_manager: LLMManager):
        super().__init__("llm_test_agent_001", AgentRole.TESTING, workspace_root)
        self.llm_agent = LLMTestingAgent('testing', llm_manager)
        
    async def _execute_task(self, task: ProductionTask) -> Dict[str, Any]:
        """Execute test generation with LLM"""
        self.logger.info(f"LLM-enhanced test generation for task {task.task_id}")
        
        try:
            # Get generated code from previous phase
            generated_files = task.deliverables.get("generated_files", {})
            requirements = task.deliverables.get("requirements_spec", task.requirements)
            
            if not generated_files:
                return {"status": "skipped", "reason": "No code files to test"}
                
            # Use LLM agent for test generation
            testing_result = await self.llm_agent.generate_tests(generated_files, requirements)
            
            if testing_result['status'] == 'completed':
                test_files = testing_result.get('test_files', {})
                
                # Save test files
                project_dir = Path(task.deliverables.get("project_directory", ""))
                if project_dir.exists():
                    await self._save_test_files(project_dir, test_files)
                
                return {
                    "test_files": test_files,
                    "test_count": len(test_files),
                    "test_coverage_plan": testing_result.get('test_coverage_plan', {}),
                    "test_instructions": testing_result.get('test_instructions', ''),
                    "llm_enhanced": True
                }
            else:
                # Fallback to basic test generation
                return await self._basic_test_generation(task)
                
        except Exception as e:
            self.logger.error(f"LLM test generation failed: {str(e)}")
            return await self._basic_test_generation(task)
            
    async def _save_test_files(self, project_dir: Path, test_files: Dict[str, str]):
        """Save test files to project directory"""
        test_dir = project_dir / "tests"
        test_dir.mkdir(exist_ok=True)
        
        for filename, content in test_files.items():
            test_file_path = test_dir / filename
            with open(test_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        self.logger.info(f"Saved {len(test_files)} test files to {test_dir}")
        
    async def _basic_test_generation(self, task: ProductionTask) -> Dict[str, Any]:
        """Fallback basic test generation"""
        return {
            "test_files": {},
            "test_count": 0,
            "llm_enhanced": False,
            "status": "basic_fallback"
        }


class LLMEnhancedDeploymentAgent(ProductionAgent):
    """Enhanced deployment agent with LLM capabilities"""
    
    def __init__(self, workspace_root: Path, llm_manager: LLMManager):
        super().__init__("llm_deploy_agent_001", AgentRole.DEPLOYMENT, workspace_root)
        self.llm_agent = LLMDeploymentAgent('deployment', llm_manager)
        
    async def _execute_task(self, task: ProductionTask) -> Dict[str, Any]:
        """Execute deployment package creation with LLM"""
        self.logger.info(f"LLM-enhanced deployment for task {task.task_id}")
        
        try:
            # Collect project data from all phases
            project_data = {
                'name': task.project_name,
                'description': task.description,
                'generated_files': task.deliverables.get("generated_files", {}),
                'test_files': task.deliverables.get("test_files", {}),
                'requirements': task.deliverables.get("requirements_spec", task.requirements),
                'project_directory': task.deliverables.get("project_directory", "")
            }
            
            # Use LLM agent for deployment package creation
            deployment_result = await self.llm_agent.create_deployment_package(project_data)
            
            if deployment_result['status'] == 'completed':
                deployment_files = deployment_result.get('deployment_files', {})
                
                # Save deployment files
                project_dir = Path(project_data.get("project_directory", ""))
                if project_dir.exists():
                    await self._save_deployment_files(project_dir, deployment_files)
                
                return {
                    "deployment_files": deployment_files,
                    "deployment_file_count": len(deployment_files),
                    "deployment_instructions": deployment_result.get('deployment_instructions', ''),
                    "deployment_structure": deployment_result.get('deployment_structure', {}),
                    "llm_enhanced": True
                }
            else:
                # Fallback to basic deployment
                return await self._basic_deployment(task)
                
        except Exception as e:
            self.logger.error(f"LLM deployment failed: {str(e)}")
            return await self._basic_deployment(task)
            
    async def _save_deployment_files(self, project_dir: Path, deployment_files: Dict[str, str]):
        """Save deployment files to project directory"""
        for filename, content in deployment_files.items():
            file_path = project_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        self.logger.info(f"Saved {len(deployment_files)} deployment files to {project_dir}")
        
    async def _basic_deployment(self, task: ProductionTask) -> Dict[str, Any]:
        """Fallback basic deployment"""
        return {
            "deployment_files": {},
            "deployment_file_count": 0,
            "llm_enhanced": False,
            "status": "basic_fallback"
        }


class LLMEnhancedProductionCrew(IntelligentProductionCrew):
    """LLM-Enhanced Production Crew with AI code generation capabilities"""
    
    def __init__(self, workspace_root: Optional[Path] = None, llm_config: Optional[LLMConfig] = None):
        super().__init__(workspace_root)
        
        self.llm_config = llm_config or LLMConfig()
        self.llm_manager = None
        self.llm_initialized = False
        
    async def initialize_llm(self) -> bool:
        """Initialize LLM components"""
        try:
            self.llm_manager = LLMManager(self.llm_config)
            self.llm_initialized = await self.llm_manager.initialize()
            
            if self.llm_initialized:
                # Replace agents with LLM-enhanced versions
                self.agents = {
                    AgentRole.REQUIREMENTS: LLMEnhancedRequirementsAgent(self.workspace_root, self.llm_manager),
                    AgentRole.PLANNING: LLMEnhancedPlanningAgent(self.workspace_root, self.llm_manager),
                    AgentRole.CODING: LLMEnhancedCodingAgent(self.workspace_root, self.llm_manager),
                    AgentRole.TESTING: LLMEnhancedTestingAgent(self.workspace_root, self.llm_manager),
                    AgentRole.DEPLOYMENT: LLMEnhancedDeploymentAgent(self.workspace_root, self.llm_manager)
                }
                
                self.logger.info("LLM-enhanced agents initialized successfully")
                return True
            else:
                self.logger.warning("LLM initialization failed, using standard agents")
                return False
                
        except Exception as e:
            self.logger.error(f"LLM initialization error: {str(e)}")
            return False
            
    async def submit_project(self, project_spec: Dict[str, Any]) -> str:
        """Submit project with LLM enhancement check"""
        # Initialize LLM if not already done
        if not self.llm_initialized:
            await self.initialize_llm()
            
        # Call parent submit method
        task_id = await super().submit_project(project_spec)
        
        # Log LLM status
        if self.llm_initialized:
            self.logger.info(f"Project {task_id} will use LLM-enhanced agents")
        else:
            self.logger.info(f"Project {task_id} will use standard agents (LLM unavailable)")
            
        return task_id
        
    def get_system_status(self) -> Dict[str, Any]:
        """Get enhanced system status including LLM information"""
        base_status = {
            'production_crew': 'active',
            'workspace_root': str(self.workspace_root),
            'agents_count': len(self.agents),
            'active_tasks': len(self.active_tasks)
        }
        
        if self.llm_initialized and self.llm_manager:
            base_status.update({
                'llm_enabled': True,
                'llm_provider': self.llm_config.provider,
                'llm_model': self.llm_config.model
            })
        else:
            base_status.update({
                'llm_enabled': False,
                'llm_status': 'not_initialized'
            })
            
        return base_status


# Convenience function to create and initialize the enhanced crew
async def create_llm_enhanced_crew(workspace_root: Optional[Path] = None, llm_config: Optional[LLMConfig] = None) -> LLMEnhancedProductionCrew:
    """Create and initialize LLM-enhanced production crew"""
    crew = LLMEnhancedProductionCrew(workspace_root, llm_config)
    await crew.initialize_llm()
    return crew


# Example usage and testing
async def test_llm_enhanced_crew():
    """Test the LLM-enhanced production crew"""
    # Create configuration
    llm_config = LLMConfig(
        provider="ollama",
        model="Artifact_Virtual/raegen:latest",
        temperature=0.1
    )
    
    # Create and initialize enhanced crew
    crew = await create_llm_enhanced_crew(llm_config=llm_config)
    
    # Test project submission
    test_project = {
        'name': 'ai_data_processor',
        'description': 'Intelligent data processing agent with ML capabilities',
        'type': 'automated_agent',
        'requirements': {
            'programming_languages': ['python'],
            'frameworks': ['pandas', 'scikit-learn'],
            'features': ['data_ingestion', 'ml_processing', 'automated_reports'],
            'dependencies': ['pandas', 'numpy', 'scikit-learn', 'matplotlib']
        },
        'custom_instructions': 'Focus on modularity and extensibility'
    }
    
    # Submit project
    task_id = await crew.submit_project(test_project)
    print(f"Submitted project with ID: {task_id}")
    
    # Start processing
    # Note: In practice, this would run in the background
    # await crew.process_tasks()
    
    # Get status
    status = crew.get_system_status()
    print(f"System status: {status}")


if __name__ == "__main__":
    asyncio.run(test_llm_enhanced_crew())
