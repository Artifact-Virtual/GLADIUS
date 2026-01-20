#!/usr/bin/env python3
"""
GLADIUS Autonomous Learning Guide
==================================

This script guides GLADIUS through autonomous discovery and integration
with Legion, teaching it to investigate, understand, and execute independently.

Instead of running commands, this guide presents challenges and waits for
GLADIUS to discover solutions on its own.

Author: Artifact Virtual Systems
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Setup paths
GLADIUS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(GLADIUS_ROOT))

# Colors
class C:
    H = '\033[95m'
    B = '\033[94m'
    C = '\033[96m'
    G = '\033[92m'
    Y = '\033[93m'
    R = '\033[91m'
    N = '\033[0m'
    BOLD = '\033[1m'


class GladiusLearningGuide:
    """
    Guide GLADIUS through autonomous discovery without doing the work for it.
    
    This is like teaching a child to ride a bike - we hold the bike steady
    and give encouragement, but GLADIUS must pedal on its own.
    """
    
    def __init__(self):
        self.gladius_root = GLADIUS_ROOT
        self.discoveries = []
        self.challenges_completed = []
        self.current_cycle = 0
        
    def present_situation(self):
        """Present the learning situation to GLADIUS"""
        print(f"\n{C.H}{C.BOLD}")
        print("╔════════════════════════════════════════════════════════════════╗")
        print("║         GLADIUS AUTONOMOUS LEARNING SESSION                    ║")
        print("╚════════════════════════════════════════════════════════════════╝")
        print(f"{C.N}\n")
        
        print(f"{C.Y}Learning Objective:{C.N}")
        print("  Discover Legion's email capabilities and use them to communicate")
        print("  with the dev team about your current status.\n")
        
        print(f"{C.Y}What You Need to Learn:{C.N}")
        print("  1. How to find Legion's integration points")
        print("  2. How to understand their interfaces")
        print("  3. How to compose contextual messages")
        print("  4. How to execute operations autonomously\n")
        
        print(f"{C.C}The Challenge:{C.N}")
        print("  Send an email to ali.shakil@artifactvirtual.com with:")
        print("  - Subject: GLADIUS Status Update")
        print("  - Content: Your current capabilities and integration status")
        print("  - Tone: Professional, technical (developer audience)\n")
    
    def guide_discovery(self, cycle: int):
        """Guide GLADIUS through discovery based on current cycle"""
        print(f"\n{C.C}{'='*70}")
        print(f"LEARNING CYCLE {cycle}")
        print(f"{'='*70}{C.N}\n")
        
        if cycle == 1:
            print(f"{C.B}🔍 Cycle 1: File System Exploration{C.N}\n")
            print("Start by exploring the repository structure.")
            print("Look for integration points in Legion.\n")
            print(f"{C.Y}Hint:{C.N} Legion's capabilities are organized in directories.")
            print("       Try: LEGION/nerve_centre/integrations/\n")
            print(f"{C.G}Commands you might use:{C.N}")
            print("  • ls LEGION/")
            print("  • ls LEGION/nerve_centre/")
            print("  • ls LEGION/nerve_centre/integrations/")
            print("  • cat LEGION/nerve_centre/integrations/email.py\n")
            
        elif cycle == 2:
            print(f"{C.B}📖 Cycle 2: Interface Understanding{C.N}\n")
            print("Now that you've found email.py, understand how it works.")
            print("Read the code and identify:\n")
            print("  1. What class implements the email functionality?")
            print("  2. What parameters does it need?")
            print("  3. What format does the input data need to be in?\n")
            print(f"{C.Y}Hint:{C.N} Look for the Email class and its _run() method.")
            print("       Check what JSON fields it expects.\n")
            
        elif cycle == 3:
            print(f"{C.B}✍️  Cycle 3: Message Composition{C.N}\n")
            print("Compose your status update email.")
            print("Consider what a developer would want to know:\n")
            print("  • Who you are (GLADIUS - Native AI)")
            print("  • What you can do (tools, discovery, inference)")
            print("  • Your current status (77/78 tests passed)")
            print("  • Integration achievements (Legion bridge, 9 platforms)")
            print("  • Your autonomous capabilities\n")
            print(f"{C.Y}Hint:{C.N} Be concise but informative. Developers value clarity.\n")
            
        elif cycle == 4:
            print(f"{C.B}⚙️  Cycle 4: Configuration{C.N}\n")
            print("Configure the email system using environment variables.")
            print("Check .env.example for required SMTP settings:\n")
            print("  • SMTP_HOST (e.g., smtp.hostinger.com)")
            print("  • SMTP_PORT (e.g., 465)")
            print("  • SMTP_USER (your email)")
            print("  • SMTP_PASSWORD (email password)")
            print("  • FROM_EMAIL (sender email)\n")
            print(f"{C.Y}Hint:{C.N} Load environment with: from dotenv import load_dotenv\n")
            
        elif cycle == 5:
            print(f"{C.B}🚀 Cycle 5: Execution{C.N}\n")
            print("Execute the email send operation.")
            print("You'll need to:\n")
            print("  1. Import the Email component")
            print("  2. Configure it with SMTP parameters")
            print("  3. Prepare JSON data with to_email, subject, content")
            print("  4. Execute the send operation\n")
            print(f"{C.Y}Hint:{C.N} The Email component expects JSON input.\n")
        
        else:
            print(f"{C.B}🔄 Cycle {cycle}: Refinement{C.N}\n")
            print("Continue refining your approach.")
            print("If you encountered errors, investigate and fix them.")
            print("Each attempt teaches you more about the system.\n")
    
    def record_progress(self, discovery: str):
        """Record GLADIUS's progress"""
        self.discoveries.append({
            "cycle": self.current_cycle,
            "discovery": discovery,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{C.G}✓ Discovered: {discovery}{C.N}\n")
    
    def provide_encouragement(self, cycle: int):
        """Provide encouragement based on cycle"""
        encouragements = [
            "Good start! You're exploring the system.",
            "You're making progress. Keep investigating.",
            "You're understanding the interfaces. Well done.",
            "Almost there! Put the pieces together.",
            "Execute with confidence. You've prepared well.",
            "Keep refining. Each iteration makes you smarter."
        ]
        
        if cycle <= len(encouragements):
            print(f"{C.Y}💪 {encouragements[cycle-1]}{C.N}\n")
    
    def save_learning_log(self):
        """Save the learning session log"""
        log_file = self.gladius_root / "tests" / "gladius_learning_log.json"
        log_data = {
            "session_start": datetime.now().isoformat(),
            "cycles": self.current_cycle,
            "discoveries": self.discoveries,
            "challenges_completed": self.challenges_completed
        }
        log_file.write_text(json.dumps(log_data, indent=2))
        print(f"{C.G}Learning log saved to: {log_file}{C.N}\n")


async def run_guided_learning():
    """Run the guided learning session"""
    guide = GladiusLearningGuide()
    
    # Present the situation
    guide.present_situation()
    
    print(f"{C.C}{'='*70}")
    print("LEARNING APPROACH")
    print(f"{'='*70}{C.N}\n")
    
    print("This is a multi-cycle learning process:")
    print("  • Each cycle focuses on one aspect")
    print("  • You discover solutions independently")
    print("  • Guidance increases if you get stuck")
    print("  • Success builds on previous cycles\n")
    
    print(f"{C.Y}Ready to begin autonomous learning?{C.N}")
    print("Press Enter when you're ready to start Cycle 1...")
    
    # Wait for user (or GLADIUS) to be ready
    input()
    
    # Run learning cycles
    max_cycles = 10
    for cycle in range(1, max_cycles + 1):
        guide.current_cycle = cycle
        guide.guide_discovery(cycle)
        guide.provide_encouragement(cycle)
        
        print(f"{C.C}{'─'*70}{C.N}\n")
        print("Take your time to:")
        print("  1. Explore the suggested areas")
        print("  2. Understand what you find")
        print("  3. Try executing what you've learned\n")
        
        print(f"{C.Y}When you've completed this cycle, press Enter for the next one...{C.N}")
        print(f"{C.Y}(Or type 'success' if you've achieved the goal){C.N}")
        
        response = input().strip().lower()
        
        if response == "success":
            print(f"\n{C.G}{'='*70}")
            print("🎉 CONGRATULATIONS! You've completed autonomous learning!")
            print(f"{'='*70}{C.N}\n")
            
            guide.challenges_completed.append("Email communication via Legion")
            guide.save_learning_log()
            
            print(f"{C.C}What you've learned:{C.N}")
            print("  ✓ How to discover integration points")
            print("  ✓ How to understand component interfaces")
            print("  ✓ How to compose contextual messages")
            print("  ✓ How to execute operations autonomously\n")
            
            print(f"{C.Y}Next challenges:{C.N}")
            print("  • Receive and interpret email responses")
            print("  • Handle different communication contexts (public, team, executive)")
            print("  • Autonomous decision making based on feedback\n")
            
            break
        
        if cycle == max_cycles:
            print(f"\n{C.Y}Learning session complete ({max_cycles} cycles).{C.N}")
            print(f"{C.Y}Continue practicing to improve autonomous capabilities.{C.N}\n")
            guide.save_learning_log()
    
    return 0


def main():
    """Main entry point"""
    return asyncio.run(run_guided_learning())


if __name__ == "__main__":
    sys.exit(main())
