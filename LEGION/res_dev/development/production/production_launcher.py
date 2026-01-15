#!/usr/bin/env python3
"""
Production Pipeline Launcher
Starts the complete production automation system with submission handling
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path


def start_production_crew():
    """Start the production crew system"""
    print("🚀 Starting Production Crew System...")
    
    try:
        # Import and start the production crew
        sys.path.append(str(Path(__file__).parent))
        from intelligent_production_crew import IntelligentProductionCrew
        
        crew = IntelligentProductionCrew()
        
        # Run in background
        print("✅ Production Crew System started successfully")
        return crew
        
    except Exception as e:
        print(f"❌ Error starting Production Crew: {str(e)}")
        return None


def process_submissions():
    """Process any existing submissions"""
    print("📋 Processing existing submissions...")
    
    try:
        # Try enhanced handler first
        try:
            from submission_handler_enhanced import EnhancedSubmissionHandler
            
            submissions_dir = Path(__file__).parent / 'submissions'
            handler = EnhancedSubmissionHandler(str(submissions_dir))
            handler.process_all_submissions_sync()
            
            print("✅ Submissions processed with enhanced handler")
            
        except ImportError:
            # Fallback to simple handler
            from simple_submission_handler import SimpleSubmissionHandler
            
            submissions_dir = Path(__file__).parent / 'submissions'
            handler = SimpleSubmissionHandler(str(submissions_dir))
            handler.process_all_submissions()
            
            print("✅ Submissions processed with simple handler")
        
    except Exception as e:
        print(f"❌ Error processing submissions: {str(e)}")
        # Print more details for debugging
        import traceback
        traceback.print_exc()


def show_status():
    """Show system status"""
    print("\n" + "="*60)
    print("🏭 PRODUCTION PIPELINE STATUS")
    print("="*60)
    
    # Check if submissions directory exists
    submissions_dir = Path(__file__).parent / 'submissions'
    if submissions_dir.exists():
        md_files = list(submissions_dir.glob('*.md'))
        txt_files = list(submissions_dir.glob('*.txt'))
        project_files = [f for f in md_files + txt_files 
                        if 'readme' not in f.name.lower()]
        
        print(f"📁 Submissions Directory: {submissions_dir}")
        print(f"📄 Pending Projects: {len(project_files)}")
        
        if project_files:
            print("   Pending files:")
            for file in project_files:
                print(f"   - {file.name}")
    else:
        print("❌ Submissions directory not found")
    
    # Check processed files
    processed_dir = submissions_dir / 'processed'
    if processed_dir.exists():
        processed_files = list(processed_dir.glob('*.md')) + list(processed_dir.glob('*.txt'))
        print(f"✅ Processed Projects: {len(processed_files)}")
    
    print("\n📖 How to submit projects:")
    print("1. Create a .md or .txt file in the submissions folder")
    print("2. Optionally add a .json file with the same name for instructions")
    print("3. Run this script to process submissions")
    print("="*60)


def main():
    """Main function"""
    print("🏭 Artifact Virtual - Production Pipeline")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'status':
            show_status()
            return
        elif command == 'submit':
            process_submissions()
            return
        elif command == 'help':
            print("Available commands:")
            print("  python production_launcher.py start    - Start full pipeline")
            print("  python production_launcher.py submit   - Process submissions")
            print("  python production_launcher.py status   - Show system status")
            print("  python production_launcher.py help     - Show this help")
            return
    
    # Default: start full pipeline
    print("Starting full production pipeline...")
    
    # Start production crew
    crew = start_production_crew()
    if not crew:
        print("❌ Failed to start production crew. Exiting.")
        return
    
    # Process any existing submissions
    process_submissions()
    
    # Show final status
    show_status()
    
    print("\n🎯 Production pipeline is ready!")
    print("Place .md or .txt files in the submissions folder to create new projects.")


if __name__ == "__main__":
    main()
