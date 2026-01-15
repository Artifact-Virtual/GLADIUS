#!/usr/bin/env python3
"""
Enhanced Submission Handler for Production Pipeline
Processes project submissions with LLM integration
"""

import json
import time
import shutil
import logging
import asyncio
from pathlib import Path
from datetime import datetime

# Import LLM integration components
try:
    from llm_integration import LLMEnhancedSubmissionHandler
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# Import fallback crew
try:
    from llm_enhanced_crew import LLMEnhancedCrew
    ENHANCED_CREW_AVAILABLE = True
except ImportError:
    ENHANCED_CREW_AVAILABLE = False
    
# Import standard crew as fallback
try:
    from intelligent_production_crew import IntelligentProductionCrew
    STANDARD_CREW_AVAILABLE = True
except ImportError:
    STANDARD_CREW_AVAILABLE = False


class EnhancedSubmissionHandler:
    """Enhanced handler with LLM integration and fallback support"""
    
    def __init__(self, submissions_dir: str):
        self.submissions_dir = Path(submissions_dir)
        self.processed_dir = self.submissions_dir / "processed"
        self.generated_dir = Path("generated_projects")
        self.setup_logging()
        
        # Setup directories
        self.processed_dir.mkdir(exist_ok=True)
        self.generated_dir.mkdir(exist_ok=True)
        
        # Initialize handlers based on availability
        self.llm_handler = None
        self.crew = None
        
        if LLM_AVAILABLE:
            try:
                self.llm_handler = LLMEnhancedSubmissionHandler(
                    self.submissions_dir, self.generated_dir
                )
                self.logger.info("LLM integration enabled")
            except Exception as e:
                self.logger.warning(f"LLM handler init failed: {e}")
        
        if ENHANCED_CREW_AVAILABLE:
            try:
                self.crew = LLMEnhancedCrew()
                self.logger.info("Enhanced crew available")
            except Exception as e:
                self.logger.warning(f"Enhanced crew init failed: {e}")
        elif STANDARD_CREW_AVAILABLE:
            try:
                self.crew = IntelligentProductionCrew()
                self.logger.info("Standard crew available")
            except Exception as e:
                self.logger.warning(f"Standard crew init failed: {e}")
        
    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('submission_handler.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    async def process_all_submissions(self):
        """Process all submission files asynchronously"""
        self.logger.info("Processing all submissions...")
        
        md_files = list(self.submissions_dir.glob('*.md'))
        txt_files = list(self.submissions_dir.glob('*.txt'))
        
        # Filter out README files
        project_files = [f for f in md_files + txt_files
                         if 'readme' not in f.name.lower()]
        
        if not project_files:
            self.logger.info("No project files found for processing")
            return
            
        for file_path in project_files:
            await self.process_submission(file_path)
    
    def process_all_submissions_sync(self):
        """Synchronous wrapper for processing all submissions"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.process_all_submissions())
        finally:
            loop.close()
            
    async def process_submission(self, file_path: Path):
        """Process a single submission file with LLM integration"""
        try:
            self.logger.info(f"Processing: {file_path.name}")
            
            # Try LLM-enhanced processing first
            if self.llm_handler:
                try:
                    result = await self.llm_handler.process_submission_file(file_path)
                    if result["status"] == "success":
                        self.logger.info(f"LLM processing successful for {file_path.name}")
                        await self.archive_files(file_path, result)
                        return
                    else:
                        self.logger.warning(f"LLM processing failed: {result.get('message')}")
                except Exception as e:
                    self.logger.warning(f"LLM processing error: {e}")
            
            # Fallback to standard processing
            await self.process_submission_standard(file_path)
            
        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {str(e)}")
    
    async def process_submission_standard(self, file_path: Path):
        """Standard submission processing without LLM"""
        try:
            # Read project description
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for instructions file
            instructions_path = file_path.with_suffix('.json')
            instructions = None
            if instructions_path.exists():
                with open(instructions_path, 'r', encoding='utf-8') as f:
                    instructions = json.load(f)
                    
            # Parse project details
            project_details = self.parse_project(content, instructions)
            
            # Submit to production crew
            success = await self.submit_project(project_details, file_path.stem)
            
            if success:
                await self.archive_files(file_path, {"status": "success", "method": "standard"})
                
        except Exception as e:
            self.logger.error(f"Standard processing error for {file_path}: {str(e)}")
            
    def parse_project(self, content: str, instructions: dict = None):
        """Parse project content and instructions"""
        lines = content.strip().split('\n')
        
        # Extract title
        title = "Untitled Project"
        for line in lines:
            if line.strip().startswith('# '):
                title = line.strip()[2:].strip()
                break
                
        project_data = {
            'name': title,
            'description': content,
            'type': 'automated_agent',
            'priority': 'medium',
            'requirements': {
                'programming_languages': ['python'],
                'frameworks': [],
                'dependencies': []
            }
        }
        
        # Merge instructions if provided
        if instructions:
            if 'priority' in instructions:
                project_data['priority'] = instructions['priority']
            if 'requirements' in instructions:
                project_data['requirements'].update(instructions['requirements'])
            if 'custom_instructions' in instructions:
                project_data['custom_instructions'] = instructions['custom_instructions']
                
        return project_data
        
    async def submit_project(self, project_data: dict, project_name: str) -> bool:
        """Submit project to production crew"""
        try:
            if self.crew:
                # Process with available crew
                if hasattr(self.crew, 'process_project'):
                    result = await self.crew.process_project(project_data)
                else:
                    # Fallback for synchronous crews
                    result = self.crew.kickoff(project_data)
                
                self.logger.info(f"Crew processing completed for {project_name}")
                return True
            else:
                self.logger.warning("No crew available for processing")
                return False
                
        except Exception as e:
            self.logger.error(f"Crew submission failed: {e}")
            return False
    
    async def archive_files(self, file_path: Path, result: dict = None):
        """Archive processed files"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Archive the main file
            archived_name = f"{timestamp}_{file_path.name}"
            archived_path = self.processed_dir / archived_name
            shutil.move(str(file_path), str(archived_path))
            
            # Archive instructions file if exists
            instructions_path = file_path.with_suffix('.json')
            if instructions_path.exists():
                archived_instructions = f"{timestamp}_{instructions_path.name}"
                archived_instructions_path = self.processed_dir / archived_instructions
                shutil.move(str(instructions_path), str(archived_instructions_path))
            
            # Save processing result
            if result:
                result_path = self.processed_dir / f"{timestamp}_{file_path.stem}_result.json"
                with open(result_path, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
            
            self.logger.info(f"Archived: {file_path.name} -> {archived_name}")
            
        except Exception as e:
            self.logger.error(f"Archiving failed for {file_path}: {e}")


# Legacy class for backward compatibility  
class SimpleSubmissionHandler(EnhancedSubmissionHandler):
    """Legacy class - redirects to enhanced handler"""
    pass


# Test and utility functions
def main():
    """Main function for testing"""
    submissions_dir = "submissions"
    handler = EnhancedSubmissionHandler(submissions_dir)
    
    print("Enhanced Submission Handler")
    print(f"LLM Available: {LLM_AVAILABLE}")
    print(f"Enhanced Crew Available: {ENHANCED_CREW_AVAILABLE}")
    print(f"Standard Crew Available: {STANDARD_CREW_AVAILABLE}")
    
    # Process submissions
    handler.process_all_submissions_sync()


if __name__ == "__main__":
    main()
