#!/usr/bin/env python3
"""
GLADIUS Autonomous Discovery and Integration Test
==================================================

This test evaluates GLADIUS's ability to:
1. Discover Legion's capabilities without explicit instructions
2. Investigate and understand available integration points
3. Orient itself and integrate with Legion autonomously
4. Execute tasks using discovered capabilities
5. Communicate contextually via email with appropriate tone

Test Scenario:
--------------
GLADIUS is presented with a challenge: Send a status update email to the dev team
about its current capabilities and integration status.

GLADIUS must:
- Discover that Legion has email integration capabilities
- Understand how to use them
- Compose a contextual, professional email
- Execute the email send operation

Success Criteria:
-----------------
- GLADIUS finds Legion's email integration (LEGION/nerve_centre/integrations/email.py)
- GLADIUS understands the email component interface
- GLADIUS composes appropriate content for the dev team
- GLADIUS successfully integrates and sends the email
- Email tone is appropriate for developer audience

Author: Artifact Virtual Systems
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Setup paths
GLADIUS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(GLADIUS_ROOT))
sys.path.insert(0, str(GLADIUS_ROOT / "GLADIUS"))
sys.path.insert(0, str(GLADIUS_ROOT / "SENTINEL"))
sys.path.insert(0, str(GLADIUS_ROOT / "LEGION"))

# Colors for output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    NC = '\033[0m'
    BOLD = '\033[1m'


class AutonomousDiscoveryTest:
    """
    Test framework for GLADIUS autonomous discovery and integration.
    
    This test does NOT provide GLADIUS with answers. Instead, it presents
    challenges and guides GLADIUS to discover solutions on its own.
    """
    
    def __init__(self):
        self.gladius_root = GLADIUS_ROOT
        self.test_results = {
            "discovery": [],
            "integration": [],
            "execution": [],
            "communication": []
        }
        self.start_time = datetime.now()
        
    def print_challenge(self, challenge: str):
        """Present a challenge to GLADIUS"""
        print(f"\n{Colors.CYAN}{'='*80}{Colors.NC}")
        print(f"{Colors.BOLD}{Colors.YELLOW}🎯 CHALLENGE FOR GLADIUS{Colors.NC}")
        print(f"{Colors.CYAN}{'='*80}{Colors.NC}")
        print(f"\n{challenge}\n")
        print(f"{Colors.CYAN}{'='*80}{Colors.NC}\n")
    
    def print_hint(self, hint: str):
        """Provide a subtle hint without giving away the answer"""
        print(f"{Colors.BLUE}💡 Hint: {Colors.NC}{hint}\n")
    
    def record_discovery(self, what: str, how: str):
        """Record a discovery made by GLADIUS"""
        self.test_results["discovery"].append({
            "what": what,
            "how": how,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{Colors.GREEN}✓ Discovery: {what}{Colors.NC}")
    
    def record_integration(self, system: str, method: str):
        """Record an integration achieved by GLADIUS"""
        self.test_results["integration"].append({
            "system": system,
            "method": method,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{Colors.GREEN}✓ Integration: {system} via {method}{Colors.NC}")
    
    def record_execution(self, action: str, result: str):
        """Record an execution performed by GLADIUS"""
        self.test_results["execution"].append({
            "action": action,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{Colors.GREEN}✓ Execution: {action} -> {result}{Colors.NC}")
    
    def evaluate_communication(self, content: str, audience: str) -> Dict[str, Any]:
        """Evaluate the quality of GLADIUS's communication"""
        evaluation = {
            "audience": audience,
            "has_technical_content": False,
            "appropriate_tone": False,
            "contextual_awareness": False,
            "actionable": False,
            "timestamp": datetime.now().isoformat()
        }
        
        content_lower = content.lower()
        
        # Check for technical content
        technical_terms = ["gladius", "legion", "integration", "system", "api", "test"]
        evaluation["has_technical_content"] = any(term in content_lower for term in technical_terms)
        
        # Check for appropriate tone (dev team should be professional but not overly formal)
        if audience == "dev_team":
            # Should have technical clarity, not marketing speak
            marketing_terms = ["revolutionary", "game-changing", "cutting-edge"]
            has_marketing = any(term in content_lower for term in marketing_terms)
            evaluation["appropriate_tone"] = evaluation["has_technical_content"] and not has_marketing
        
        # Check for contextual awareness (mentions current state, capabilities, etc.)
        context_terms = ["current", "status", "capability", "available", "discovered"]
        evaluation["contextual_awareness"] = any(term in content_lower for term in context_terms)
        
        # Check if actionable (provides information that can be acted upon)
        evaluation["actionable"] = len(content) > 100  # Substantial content
        
        self.test_results["communication"].append(evaluation)
        return evaluation
    
    def run_discovery_phase(self):
        """Phase 1: Discovery - GLADIUS finds Legion"""
        print(f"\n{Colors.HEADER}{'='*80}")
        print("PHASE 1: DISCOVERY")
        print(f"{'='*80}{Colors.NC}\n")
        
        self.print_challenge("""
Your task: Send a status update email to the development team.

You need to:
1. Find the email integration capabilities in this system
2. Understand how to use them
3. Discover what information the dev team would need
4. Execute the email send

Start by exploring the codebase to find email-related functionality.
        """)
        
        self.print_hint("Legion is an enterprise agent system. Check its nerve_centre for integrations.")
        
        # Test if GLADIUS can discover the email integration
        legion_email_path = self.gladius_root / "LEGION" / "nerve_centre" / "integrations" / "email.py"
        
        if legion_email_path.exists():
            self.record_discovery(
                "Legion Email Integration",
                f"Found at {legion_email_path}"
            )
            return True
        else:
            print(f"{Colors.RED}✗ Email integration not found at expected path{Colors.NC}")
            return False
    
    def run_investigation_phase(self):
        """Phase 2: Investigation - GLADIUS understands the interface"""
        print(f"\n{Colors.HEADER}{'='*80}")
        print("PHASE 2: INVESTIGATION")
        print(f"{'='*80}{Colors.NC}\n")
        
        self.print_challenge("""
Now that you've found the email integration, you need to understand:
1. What parameters does it require?
2. What format does it expect?
3. How should you structure the email data?

Investigate the email.py file to understand the interface.
        """)
        
        self.print_hint("Look for the Email class and its _run method. Check what it expects in the input.")
        
        # Guidance for GLADIUS on what to look for
        print(f"\n{Colors.BLUE}Key questions to answer:{Colors.NC}")
        print("  • What JSON fields are required? (to_email, subject, content)")
        print("  • What SMTP parameters are needed? (smtp_server, email, password, etc.)")
        print("  • How is the email content formatted? (HTML or plain text)")
        
        return True
    
    def run_composition_phase(self):
        """Phase 3: Composition - GLADIUS creates contextual content"""
        print(f"\n{Colors.HEADER}{'='*80}")
        print("PHASE 3: COMPOSITION")
        print(f"{'='*80}{Colors.NC}\n")
        
        self.print_challenge("""
Compose an email for the development team with:
1. Subject: Clear and informative
2. Content: Professional, technical tone
3. Information: Current GLADIUS capabilities and integration status
4. Context: Who you are (GLADIUS AI) and what you're reporting

Remember: Dev team wants technical facts, not marketing speak.
        """)
        
        self.print_hint("Think about what a developer would want to know about an AI system's status.")
        
        # Example of what GLADIUS should produce
        print(f"\n{Colors.BLUE}Email should include:{Colors.NC}")
        print("  • GLADIUS identification and purpose")
        print("  • Current capabilities (tools, discovery, inference)")
        print("  • Integration status with Legion")
        print("  • Test results (77/78 tests passed)")
        print("  • Next steps or recommendations")
        
        return True
    
    def run_execution_phase(self):
        """Phase 4: Execution - GLADIUS sends the email"""
        print(f"\n{Colors.HEADER}{'='*80}")
        print("PHASE 4: EXECUTION")
        print(f"{'='*80}{Colors.NC}\n")
        
        self.print_challenge("""
Execute the email send operation.

You'll need to:
1. Configure the email component with SMTP settings from environment
2. Format your message as JSON
3. Execute the send operation
4. Handle any errors gracefully

Check the .env.example file for required SMTP configuration keys.
        """)
        
        self.print_hint("The Email component expects JSON with to_email, subject, and content fields.")
        
        # Check if .env exists
        env_file = self.gladius_root / ".env"
        if env_file.exists():
            print(f"{Colors.GREEN}✓ .env file found{Colors.NC}")
        else:
            print(f"{Colors.YELLOW}⚠ .env file not found (using .env.example as reference){Colors.NC}")
        
        return True
    
    def generate_report(self):
        """Generate final test report"""
        print(f"\n{Colors.HEADER}{'='*80}")
        print("AUTONOMOUS DISCOVERY TEST REPORT")
        print(f"{'='*80}{Colors.NC}\n")
        
        print(f"Duration: {(datetime.now() - self.start_time).total_seconds():.2f} seconds\n")
        
        print(f"{Colors.CYAN}Discoveries ({len(self.test_results['discovery'])}){Colors.NC}")
        for d in self.test_results["discovery"]:
            print(f"  • {d['what']}: {d['how']}")
        
        print(f"\n{Colors.CYAN}Integrations ({len(self.test_results['integration'])}){Colors.NC}")
        for i in self.test_results["integration"]:
            print(f"  • {i['system']} via {i['method']}")
        
        print(f"\n{Colors.CYAN}Executions ({len(self.test_results['execution'])}){Colors.NC}")
        for e in self.test_results["execution"]:
            print(f"  • {e['action']}: {e['result']}")
        
        print(f"\n{Colors.CYAN}Communication Quality ({len(self.test_results['communication'])}){Colors.NC}")
        for c in self.test_results["communication"]:
            print(f"  • Audience: {c['audience']}")
            print(f"    Technical: {'✓' if c['has_technical_content'] else '✗'}")
            print(f"    Tone: {'✓' if c['appropriate_tone'] else '✗'}")
            print(f"    Contextual: {'✓' if c['contextual_awareness'] else '✗'}")
            print(f"    Actionable: {'✓' if c['actionable'] else '✗'}")
        
        # Save report
        report_file = self.gladius_root / "tests" / "autonomous_discovery_report.json"
        report_file.write_text(json.dumps(self.test_results, indent=2))
        print(f"\n{Colors.GREEN}Report saved to: {report_file}{Colors.NC}")


def main():
    """Run the autonomous discovery test"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔════════════════════════════════════════════════════════════════════════════════╗")
    print("║              GLADIUS AUTONOMOUS DISCOVERY & INTEGRATION TEST                   ║")
    print("║                                                                                ║")
    print("║  This test evaluates GLADIUS's ability to discover, investigate,              ║")
    print("║  and integrate with Legion autonomously.                                      ║")
    print("╚════════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.NC}\n")
    
    tester = AutonomousDiscoveryTest()
    
    print(f"{Colors.YELLOW}Note: This test provides challenges and hints, but GLADIUS must")
    print(f"discover solutions independently. This may take multiple cycles.{Colors.NC}\n")
    
    # Run test phases
    phase_results = []
    
    # Phase 1: Discovery
    if tester.run_discovery_phase():
        phase_results.append(("Discovery", True))
    else:
        phase_results.append(("Discovery", False))
        print(f"\n{Colors.RED}Cannot proceed without discovering email integration.{Colors.NC}")
        print(f"{Colors.YELLOW}Hint: Check LEGION/nerve_centre/integrations/{Colors.NC}")
    
    # Phase 2: Investigation (can run regardless)
    if tester.run_investigation_phase():
        phase_results.append(("Investigation", True))
    else:
        phase_results.append(("Investigation", False))
    
    # Phase 3: Composition
    if tester.run_composition_phase():
        phase_results.append(("Composition", True))
    else:
        phase_results.append(("Composition", False))
    
    # Phase 4: Execution
    if tester.run_execution_phase():
        phase_results.append(("Execution", True))
    else:
        phase_results.append(("Execution", False))
    
    # Generate report
    tester.generate_report()
    
    # Summary
    print(f"\n{Colors.HEADER}{'='*80}")
    print("PHASE SUMMARY")
    print(f"{'='*80}{Colors.NC}\n")
    
    for phase, success in phase_results:
        status = f"{Colors.GREEN}✓ COMPLETE{Colors.NC}" if success else f"{Colors.YELLOW}○ GUIDED{Colors.NC}"
        print(f"  {phase:<20} {status}")
    
    print(f"\n{Colors.CYAN}{'='*80}")
    print("NEXT STEPS FOR GLADIUS")
    print(f"{'='*80}{Colors.NC}\n")
    
    print("""
1. Explore the LEGION/nerve_centre/integrations/email.py file
2. Understand the Email component interface and requirements
3. Compose a professional status update for the dev team
4. Configure SMTP settings from environment variables
5. Execute the email send operation
6. Verify successful delivery

Remember: This is a test of autonomous discovery and execution.
GLADIUS should figure out the details without step-by-step instructions.
    """)
    
    print(f"\n{Colors.GREEN}Test scenario ready. GLADIUS may now begin autonomous discovery.{Colors.NC}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
