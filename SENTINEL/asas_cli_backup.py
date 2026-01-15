#!/usr/bin/env python3
"""
Advanced Security Administration System (ASAS) - Command Line Interface
AI-Powered Defensive Cybersecurity Framework

This CLI provides comprehensive control and monitoring capabilities for the ASAS system,
including real-time threat monitoring, system health checks, and security operations.
"""

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from colorama import Fore, Back, Style, init
import psutil
import platform

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Import ASAS components
try:
    from .security_monitor import SecurityMonitor
    from .threat_engine import ThreatEngine
    from .auto_response import AutoResponse
    from .platform_interface import PlatformInterface
    from .basenet_connector import BaseNetConnector
    from .system_controller import SystemController
except ImportError:
    # Fallback for direct execution
    from security_monitor import SecurityMonitor
    from threat_engine import ThreatEngine
    from auto_response import AutoResponse
    from platform_interface import PlatformInterface
    from basenet_connector import BaseNetConnector
    from system_controller import SystemController

class ASASCommandCenter:
    """
    Advanced Security Administration System Command Center
    
    Provides a comprehensive command-line interface for managing and monitoring
    the ASAS defensive cybersecurity framework.
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.config_dir = Path(__file__).parent / "config"
        self.data_dir = Path(__file__).parent / "data"
        self.logs_dir = Path(__file__).parent / "logs"
        
        # Initialize ASAS components
        self.security_monitor = None
        self.threat_engine = None
        self.auto_response = None
        self.platform_interface = None
        self.basenet_connector = None
        self.system_controller = None
        
        # System state
        self.is_running = False
        self.start_time = None
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('ASAS_CLI')
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        logs_dir = Path(__file__).parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # File handler
        fh = logging.FileHandler(logs_dir / f"asas_cli_{datetime.now().strftime('%Y%m%d')}.log")
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
        
    def print_banner(self):
        """Display ASAS system banner"""
        banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║              {Fore.YELLOW}Advanced Security Administration System (ASAS){Fore.CYAN}              ║
║                        {Fore.GREEN}AI-Powered Defensive Cybersecurity{Fore.CYAN}                   ║
║                                                                              ║
║  {Fore.WHITE}🛡️  Real-time Threat Detection    🔍 AI-Powered Analysis{Fore.CYAN}           ║
║  {Fore.WHITE}⚡ Automated Response Systems     🌐 Cross-Platform Protection{Fore.CYAN}     ║
║  {Fore.WHITE}🧠 Constitutional AI Framework   📊 Advanced Monitoring{Fore.CYAN}           ║
║                                                                              ║
║                        {Fore.RED}>>> DEFENSIVE SYSTEMS ONLY <<<{Fore.CYAN}                     ║
╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.WHITE}System Information:{Style.RESET_ALL}
• Platform: {platform.system()} {platform.release()}
• Python: {sys.version.split()[0]}
• Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
• Status: {Fore.GREEN}READY{Style.RESET_ALL}
"""
        print(banner)
        
    async def initialize_components(self):
        """Initialize all ASAS components"""
        try:
            self.print_status("Initializing ASAS components...", "INFO")
            
            # Initialize core components
            self.security_monitor = SecurityMonitor()
            self.threat_engine = ThreatEngine()
            self.auto_response = AutoResponse()
            self.platform_interface = PlatformInterface()
            self.basenet_connector = BaseNetConnector()
            self.system_controller = SystemController()
            
            # Components are initialized in their constructors
            # No additional initialization needed
            
            self.print_status("All ASAS components initialized successfully", "SUCCESS")
            return True
            
        except Exception as e:
            self.print_status(f"Failed to initialize ASAS components: {str(e)}", "ERROR")
            return False
            
    def print_status(self, message: str, level: str = "INFO"):
        """Print colored status message"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        if level == "SUCCESS":
            print(f"{Fore.GREEN}[{timestamp}] ✓ {message}{Style.RESET_ALL}")
        elif level == "ERROR":
            print(f"{Fore.RED}[{timestamp}] ✗ {message}{Style.RESET_ALL}")
        elif level == "WARNING":
            print(f"{Fore.YELLOW}[{timestamp}] ⚠ {message}{Style.RESET_ALL}")
        elif level == "INFO":
            print(f"{Fore.CYAN}[{timestamp}] ℹ {message}{Style.RESET_ALL}")
        else:
            print(f"[{timestamp}] {message}")
            
    async def cmd_status(self, args):
        """Display comprehensive system status"""
        print(f"\n{Fore.CYAN}=== ASAS System Status ==={Style.RESET_ALL}")
        
        # System uptime
        if self.start_time:
            uptime = datetime.now() - self.start_time
            print(f"Uptime: {Fore.GREEN}{uptime}{Style.RESET_ALL}")
        
        # Component status
        components = [
            ("Security Monitor", self.security_monitor),
            ("Threat Engine", self.threat_engine),
            ("Auto Response", self.auto_response),
            ("Platform Interface", self.platform_interface),
            ("BaseNet Connector", self.basenet_connector),
            ("System Controller", self.system_controller)
        ]
        
        print(f"\n{Fore.YELLOW}Component Status:{Style.RESET_ALL}")
        for name, component in components:
            if component and hasattr(component, 'is_active') and component.is_active:
                status = f"{Fore.GREEN}ACTIVE{Style.RESET_ALL}"
            elif component:
                status = f"{Fore.YELLOW}STANDBY{Style.RESET_ALL}"
            else:
                status = f"{Fore.RED}OFFLINE{Style.RESET_ALL}"
            print(f"  • {name}: {status}")
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        print(f"\n{Fore.YELLOW}System Metrics:{Style.RESET_ALL}")
        print(f"  • CPU Usage: {cpu_percent:.1f}%")
        print(f"  • Memory Usage: {memory.percent:.1f}% ({memory.used / (1024**3):.1f}GB / {memory.total / (1024**3):.1f}GB)")
        print(f"  • Disk Usage: {disk.percent:.1f}% ({disk.used / (1024**3):.1f}GB / {disk.total / (1024**3):.1f}GB)")
        
    async def cmd_monitor(self, args):
        """Start real-time monitoring dashboard"""
        print(f"\n{Fore.CYAN}=== Real-time Security Monitor ==={Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Press Ctrl+C to stop monitoring{Style.RESET_ALL}\n")
        
        try:
            while True:
                # Clear screen (cross-platform)
                import os
                os.system('cls' if os.name == 'nt' else 'clear')
                
                # Display header
                print(f"{Fore.CYAN}ASAS Real-time Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
                print("=" * 80)
                
                # Threat level indicator
                threat_level = await self.get_current_threat_level()
                threat_color = self.get_threat_color(threat_level)
                print(f"Current Threat Level: {threat_color}{threat_level.upper()}{Style.RESET_ALL}")
                
                # System metrics
                cpu = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                
                print(f"\nSystem Health:")
                print(f"  CPU: {self.get_bar(cpu, 100)} {cpu:.1f}%")
                print(f"  Memory: {self.get_bar(memory.percent, 100)} {memory.percent:.1f}%")
                
                # Recent threats (if any)
                if self.threat_engine:
                    recent_threats = await self.threat_engine.get_recent_threats(limit=5)
                    if recent_threats:
                        print(f"\n{Fore.RED}Recent Threats:{Style.RESET_ALL}")
                        for threat in recent_threats:
                            print(f"  • {threat.get('timestamp', 'Unknown')} - {threat.get('type', 'Unknown')}")
                
                # Active responses
                if self.auto_response:
                    active_responses = await self.auto_response.get_active_responses()
                    if active_responses:
                        print(f"\n{Fore.YELLOW}Active Responses:{Style.RESET_ALL}")
                        for response in active_responses:
                            print(f"  • {response.get('action', 'Unknown')} - {response.get('status', 'Unknown')}")
                
                print(f"\n{Fore.CYAN}Last Updated: {datetime.now().strftime('%H:%M:%S')}{Style.RESET_ALL}")
                
                await asyncio.sleep(2)  # Update every 2 seconds
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Monitoring stopped by user{Style.RESET_ALL}")
            
    def get_bar(self, value: float, max_value: float, length: int = 20) -> str:
        """Generate a colored progress bar"""
        percent = value / max_value
        filled = int(length * percent)
        bar = "█" * filled + "░" * (length - filled)
        
        if percent < 0.5:
            color = Fore.GREEN
        elif percent < 0.8:
            color = Fore.YELLOW
        else:
            color = Fore.RED
            
        return f"{color}{bar}{Style.RESET_ALL}"
        
    async def get_current_threat_level(self) -> str:
        """Get current system threat level"""
        if self.threat_engine:
            try:
                level = await self.threat_engine.get_threat_level()
                return level
            except:
                pass
        return "normal"
        
    def get_threat_color(self, level: str) -> str:
        """Get color for threat level"""
        colors = {
            "low": Fore.GREEN,
            "normal": Fore.GREEN,
            "elevated": Fore.YELLOW,
            "high": Fore.RED,
            "critical": Fore.RED + Back.YELLOW
        }
        return colors.get(level.lower(), Fore.WHITE)
        
    async def cmd_scan(self, args):
        """Perform comprehensive security scan"""
        print(f"\n{Fore.CYAN}=== Security Scan ==={Style.RESET_ALL}")
        
        # Initialize components if not already done
        if not self.security_monitor:
            self.print_status("Initializing ASAS components...", "INFO")
            success = await self.initialize_components()
            if not success:
                self.print_status("Failed to initialize components", "ERROR")
                return
            
        scan_types = args.type if args.type else ["full"]
        
        for scan_type in scan_types:
            self.print_status(f"Starting {scan_type} scan...", "INFO")
            
            try:
                # All scan types use full_system_scan for now
                # In the future, we could add different scan depths
                results = self.security_monitor.full_system_scan()
                    
                # Display results
                self.display_scan_results(results)
                
            except Exception as e:
                self.print_status(f"Scan failed: {str(e)}", "ERROR")
                
    def display_scan_results(self, results: Dict[str, Any]):
        """Display scan results in formatted output"""
        print(f"\n{Fore.YELLOW}Scan Results:{Style.RESET_ALL}")
        
        # Summary
        total_issues = results.get('total_issues', 0)
        critical_issues = results.get('critical_issues', 0)
        
        if critical_issues > 0:
            print(f"  Critical Issues: {Fore.RED}{critical_issues}{Style.RESET_ALL}")
        if total_issues > 0:
            print(f"  Total Issues: {Fore.YELLOW}{total_issues}{Style.RESET_ALL}")
        else:
            print(f"  {Fore.GREEN}No issues detected{Style.RESET_ALL}")
            
        # Detailed findings
        findings = results.get('findings', [])
        if findings:
            print(f"\n{Fore.YELLOW}Detailed Findings:{Style.RESET_ALL}")
            for finding in findings[:10]:  # Show top 10
                severity = finding.get('severity', 'info').upper()
                color = Fore.RED if severity == 'CRITICAL' else Fore.YELLOW if severity == 'HIGH' else Fore.CYAN
                print(f"  • {color}[{severity}]{Style.RESET_ALL} {finding.get('description', 'Unknown issue')}")
                
    async def cmd_start(self, args):
        """Start ASAS system"""
        if self.is_running:
            self.print_status("ASAS system is already running", "WARNING")
            return
            
        self.print_status("Starting ASAS system...", "INFO")
        
        # Initialize components if not already done
        if not self.system_controller:
            success = await self.initialize_components()
            if not success:
                return
                
        try:
            # Start monitoring on security monitor if available
            if hasattr(self.system_controller, 'start_monitoring'):
                self.system_controller.start_monitoring()
            
            self.is_running = True
            self.start_time = datetime.now()
            
            self.print_status("ASAS system started successfully", "SUCCESS")
            
            # Start monitoring if requested
            if args.monitor:
                await self.cmd_monitor(args)
                
        except Exception as e:
            self.print_status(f"Failed to start ASAS system: {str(e)}", "ERROR")
            
    async def cmd_stop(self, args):
        """Stop ASAS system"""
        if not self.is_running:
            self.print_status("ASAS system is not running", "WARNING")
            return
            
        self.print_status("Stopping ASAS system...", "INFO")
        
        try:
            # Stop monitoring if available
            if self.system_controller and hasattr(self.system_controller, 'stop_monitoring'):
                self.system_controller.stop_monitoring()
                
            self.is_running = False
            self.start_time = None
            
            self.print_status("ASAS system stopped successfully", "SUCCESS")
            
        except Exception as e:
            self.print_status(f"Failed to stop ASAS system: {str(e)}", "ERROR")
            
    async def cmd_config(self, args):
        """Manage ASAS configuration"""
        config_file = self.config_dir / "system_controller_config.json"
        
        if args.show:
            # Show current configuration
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                print(f"\n{Fore.CYAN}Current Configuration:{Style.RESET_ALL}")
                print(json.dumps(config, indent=2))
            else:
                self.print_status("Configuration file not found", "ERROR")
                
        elif args.edit:
            # Open configuration in default editor
            import subprocess
            try:
                subprocess.run(['notepad.exe', str(config_file)] if sys.platform == 'win32' 
                             else ['nano', str(config_file)], check=True)
            except subprocess.CalledProcessError:
                self.print_status("Failed to open configuration editor", "ERROR")
                
    async def cmd_logs(self, args):
        """View ASAS logs"""
        log_files = list(self.logs_dir.glob("*.log"))
        
        if not log_files:
            self.print_status("No log files found", "WARNING")
            return
            
        # Show recent log file by default
        log_file = sorted(log_files)[-1]
        
        if args.tail:
            # Show last N lines
            lines = args.tail
            try:
                with open(log_file, 'r') as f:
                    file_lines = f.readlines()
                    recent_lines = file_lines[-lines:] if len(file_lines) > lines else file_lines
                    
                print(f"\n{Fore.CYAN}Last {len(recent_lines)} lines from {log_file.name}:{Style.RESET_ALL}")
                for line in recent_lines:
                    print(line.rstrip())
                    
            except Exception as e:
                self.print_status(f"Failed to read log file: {str(e)}", "ERROR")
        else:
            # List available log files
            print(f"\n{Fore.CYAN}Available log files:{Style.RESET_ALL}")
            for log_file in sorted(log_files):
                size = log_file.stat().st_size
                modified = datetime.fromtimestamp(log_file.stat().st_mtime)
                print(f"  • {log_file.name} ({size} bytes, modified {modified.strftime('%Y-%m-%d %H:%M')})")

async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Advanced Security Administration System (ASAS) Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  asas start --monitor          Start ASAS with real-time monitoring
  asas scan --type full         Run full security scan
  asas status                   Show system status
  asas monitor                  Show real-time dashboard
  asas logs --tail 50           Show last 50 log lines
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start ASAS system')
    start_parser.add_argument('--monitor', action='store_true', help='Start with real-time monitoring')
    
    # Stop command
    subparsers.add_parser('stop', help='Stop ASAS system')
    
    # Status command
    subparsers.add_parser('status', help='Show system status')
    
    # Monitor command
    subparsers.add_parser('monitor', help='Show real-time monitoring dashboard')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Perform security scan')
    scan_parser.add_argument('--type', choices=['quick', 'full', 'deep'], nargs='+', 
                           help='Scan type(s) to perform')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument('--show', action='store_true', help='Show current configuration')
    config_parser.add_argument('--edit', action='store_true', help='Edit configuration')
    
    # Logs command
    logs_parser = subparsers.add_parser('logs', help='View system logs')
    logs_parser.add_argument('--tail', type=int, metavar='N', help='Show last N lines')
    
    args = parser.parse_args()
    
    # Create command center instance
    asas = ASASCommandCenter()
    
    # Show banner for interactive commands
    if args.command in ['start', 'monitor', 'status'] or not args.command:
        asas.print_banner()
    
    # Handle commands
    if not args.command:
        parser.print_help()
        return
        
    try:
        command_method = getattr(asas, f'cmd_{args.command}')
        await command_method(args)
    except AttributeError:
        print(f"Unknown command: {args.command}")
        parser.print_help()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Operation interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    # Install required packages if not present
    try:
        import colorama
        import psutil
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama", "psutil"])
        import colorama
        import psutil
    
    asyncio.run(main())
