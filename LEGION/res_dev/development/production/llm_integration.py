#!/usr/bin/env python3
"""
LLM Integration Script
Connects the precise file generator to the submission pipeline
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from precise_file_generator import PreciseFileGenerator, ProjectSpec
from llm_enhanced_crew import LLMEnhancedProductionCrew


class LLMProductionIntegrator:
    """Integrates LLM-powered file generation into production pipeline"""
    
    def __init__(self, output_base_dir: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.file_generator = PreciseFileGenerator()
        self.llm_crew = LLMEnhancedProductionCrew()
        self.output_base_dir = output_base_dir or Path("generated_projects")
        
    async def process_submission_with_llm(
        self,
        project_name: str,
        description: str,
        requirements: Dict[str, Any],
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a project submission using LLM-powered generation"""
        
        self.logger.info(f"Processing submission with LLM: {project_name}")
        
        try:
            # Step 1: Generate precise project specification
            project_spec = await self.file_generator.generate_precise_project(
                project_name=project_name,
                description=description,
                requirements=requirements,
                custom_instructions=custom_instructions
            )
            
            # Step 2: Create project files
            project_output_dir = self.output_base_dir / project_name
            file_creation_success = await self.file_generator.create_project_files(
                project_spec, project_output_dir
            )
            
            if not file_creation_success:
                self.logger.error("Failed to create project files")
                return {"status": "error", "message": "File creation failed"}
            
            # Step 3: Run LLM-enhanced crew processing
            crew_result = await self._run_enhanced_crew_processing(
                project_spec, project_output_dir
            )
            
            # Step 4: Generate summary report
            report = self._generate_integration_report(
                project_spec, project_output_dir, crew_result
            )
            
            self.logger.info(f"Successfully processed {project_name}")
            return {
                "status": "success",
                "project_spec": project_spec,
                "output_directory": str(project_output_dir),
                "crew_result": crew_result,
                "report": report
            }
            
        except Exception as e:
            self.logger.error(f"LLM processing failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "project_name": project_name
            }
    
    async def _run_enhanced_crew_processing(
        self,
        project_spec: ProjectSpec,
        project_dir: Path
    ) -> Dict[str, Any]:
        """Run the LLM-enhanced crew on the generated project"""
        
        try:
            # Prepare crew input
            crew_input = {
                "project_name": project_spec.name,
                "description": project_spec.description,
                "requirements": {
                    "language": project_spec.language,
                    "framework": project_spec.framework,
                    "project_type": project_spec.project_type,
                    "dependencies": project_spec.dependencies
                },
                "project_directory": str(project_dir),
                "files": [
                    {
                        "path": file_spec.path,
                        "type": file_spec.type,
                        "description": file_spec.description
                    }
                    for file_spec in project_spec.files
                ]
            }
            
            # Run crew processing
            result = await self.llm_crew.process_project(crew_input)
            
            return {
                "status": "completed",
                "crew_result": result,
                "validation_passed": True
            }
            
        except Exception as e:
            self.logger.error(f"Crew processing failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "validation_passed": False
            }
    
    def _generate_integration_report(
        self,
        project_spec: ProjectSpec,
        project_dir: Path,
        crew_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive integration report"""
        
        report = {
            "project_summary": {
                "name": project_spec.name,
                "description": project_spec.description,
                "language": project_spec.language,
                "framework": project_spec.framework,
                "version": project_spec.version,
                "file_count": len(project_spec.files),
                "directory_count": len(project_spec.directories)
            },
            "generation_details": {
                "dependencies": project_spec.dependencies,
                "dev_dependencies": project_spec.dev_dependencies,
                "includes_tests": project_spec.include_tests,
                "includes_docs": project_spec.include_docs,
                "includes_config": project_spec.include_config
            },
            "file_structure": {
                "files": [
                    {
                        "name": file_spec.name,
                        "path": file_spec.path,
                        "type": file_spec.type,
                        "size": len(file_spec.content),
                        "description": file_spec.description
                    }
                    for file_spec in project_spec.files
                ],
                "directories": project_spec.directories
            },
            "crew_processing": crew_result,
            "output_location": str(project_dir),
            "setup_instructions": project_spec.setup_instructions,
            "usage_examples": project_spec.usage_examples
        }
        
        return report
    
    async def validate_generated_project(self, project_dir: Path) -> Dict[str, Any]:
        """Validate the generated project structure and files"""
        
        validation_results = {
            "structure_valid": True,
            "files_valid": True,
            "syntax_valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Check if directory exists
            if not project_dir.exists():
                validation_results["structure_valid"] = False
                validation_results["errors"].append("Project directory not found")
                return validation_results
            
            # Load project summary
            summary_path = project_dir / "PROJECT_SUMMARY.json"
            if not summary_path.exists():
                validation_results["warnings"].append("Project summary not found")
            
            # Validate essential files
            essential_files = ["README.md", "requirements.txt"]
            for essential_file in essential_files:
                if not (project_dir / essential_file).exists():
                    validation_results["warnings"].append(
                        f"Essential file missing: {essential_file}"
                    )
            
            # Check Python syntax for .py files
            python_files = list(project_dir.rglob("*.py"))
            for py_file in python_files:
                try:
                    compile(py_file.read_text(), str(py_file), 'exec')
                except SyntaxError as e:
                    validation_results["syntax_valid"] = False
                    validation_results["errors"].append(
                        f"Syntax error in {py_file}: {e}"
                    )
            
            self.logger.info(f"Validation completed for {project_dir}")
            
        except Exception as e:
            validation_results["structure_valid"] = False
            validation_results["errors"].append(f"Validation error: {e}")
        
        return validation_results


# Enhanced submission handler with LLM integration
class LLMEnhancedSubmissionHandler:
    """Enhanced submission handler with LLM integration"""
    
    def __init__(self, submissions_dir: Path, output_dir: Path):
        self.submissions_dir = submissions_dir
        self.output_dir = output_dir
        self.integrator = LLMProductionIntegrator(output_dir)
        self.logger = logging.getLogger(__name__)
        
    async def process_submission_file(self, submission_file: Path) -> Dict[str, Any]:
        """Process a submission file with LLM enhancement"""
        
        try:
            # Parse submission
            submission_data = self._parse_submission_file(submission_file)
            
            # Process with LLM integration
            result = await self.integrator.process_submission_with_llm(
                project_name=submission_data["project_name"],
                description=submission_data["description"],
                requirements=submission_data.get("requirements", {}),
                custom_instructions=submission_data.get("custom_instructions")
            )
            
            # Validate generated project
            if result["status"] == "success":
                project_dir = Path(result["output_directory"])
                validation = await self.integrator.validate_generated_project(
                    project_dir
                )
                result["validation"] = validation
            
            # Save processing report
            report_path = self.output_dir / f"{submission_data['project_name']}_report.json"
            with open(report_path, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Submission processing failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def _parse_submission_file(self, submission_file: Path) -> Dict[str, Any]:
        """Parse submission file content"""
        
        content = submission_file.read_text()
        
        # Try to find accompanying JSON instructions
        json_file = submission_file.with_suffix('.json')
        instructions = {}
        if json_file.exists():
            try:
                instructions = json.loads(json_file.read_text())
            except json.JSONDecodeError:
                pass
        
        # Extract project info from content
        lines = content.strip().split('\n')
        project_name = submission_file.stem
        description = content[:200] + "..." if len(content) > 200 else content
        
        # Parse title if markdown
        if submission_file.suffix == '.md':
            for line in lines:
                if line.startswith('# '):
                    project_name = line[2:].strip().lower().replace(' ', '_')
                    break
        
        return {
            "project_name": project_name,
            "description": description,
            "content": content,
            "requirements": instructions.get("requirements", {
                "language": "python",
                "project_type": "automated_agent"
            }),
            "custom_instructions": instructions.get("custom_instructions"),
            "original_file": str(submission_file)
        }


# Test function
async def test_llm_integration():
    """Test the LLM integration system"""
    
    # Setup test environment
    test_dir = Path("test_llm_integration")
    submissions_dir = test_dir / "submissions"
    output_dir = test_dir / "generated"
    
    submissions_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create test submission
    test_submission = submissions_dir / "data_processor.md"
    test_submission.write_text("""# Data Processor Agent

An automated agent for processing CSV data files and generating reports.

## Requirements
- Process CSV files from input directory
- Generate summary statistics
- Create visualization reports
- Handle errors gracefully
- Log all operations

## Features
- Batch processing
- Data validation
- Export to multiple formats
""")
    
    # Create instructions file
    instructions = {
        "requirements": {
            "language": "python",
            "framework": "pandas",
            "project_type": "data_processor",
            "features": ["csv_processing", "reporting", "visualization"]
        },
        "custom_instructions": "Create a robust data processing pipeline with error handling and logging"
    }
    
    instructions_file = submissions_dir / "data_processor.json"
    instructions_file.write_text(json.dumps(instructions, indent=2))
    
    # Test processing
    handler = LLMEnhancedSubmissionHandler(submissions_dir, output_dir)
    result = await handler.process_submission_file(test_submission)
    
    print(f"Processing result: {result['status']}")
    if result["status"] == "success":
        print(f"Generated project in: {result['output_directory']}")
        print(f"Files created: {len(result['project_spec'].files)}")
        
        # Print validation results
        validation = result.get("validation", {})
        print(f"Validation - Structure: {validation.get('structure_valid')}")
        print(f"Validation - Syntax: {validation.get('syntax_valid')}")
        
        if validation.get("errors"):
            print("Errors:", validation["errors"])
        if validation.get("warnings"):
            print("Warnings:", validation["warnings"])
    else:
        print(f"Error: {result.get('message')}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_llm_integration())
