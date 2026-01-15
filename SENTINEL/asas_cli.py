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
    from .basenet_connector import BaseNetConnector, AIRequest, AIModelType
    from .system_controller import SystemController
except ImportError:
    # Fallback for direct execution
    from security_monitor import SecurityMonitor
    from threat_engine import ThreatEngine
    from auto_response import AutoResponse
    from platform_interface import PlatformInterface
    from basenet_connector import BaseNetConnector, AIRequest, AIModelType
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
    
    # ============================================================================
    # THREAT ANALYSIS COMMANDS
    # ============================================================================
    
    async def cmd_threat_analyze(self, args):
        """Analyze threat events"""
        print(f"\n{Fore.CYAN}=== Threat Analysis ==={Style.RESET_ALL}")
        
        if not self.threat_engine:
            await self.initialize_components()
        
        # Get recent events from security monitor
        if self.security_monitor and hasattr(self.security_monitor, 'events'):
            events = self.security_monitor.events[-args.limit:] if args.limit else self.security_monitor.events
            if events:
                self.print_status(f"Analyzing {len(events)} event(s)...", "INFO")
                try:
                    assessment = self.threat_engine.analyze_events(events)
                    print(f"\n{Fore.YELLOW}Threat Assessment:{Style.RESET_ALL}")
                    print(f"  Threat Level: {self.get_threat_color(assessment.get('threat_level', 'normal'))}{assessment.get('threat_level', 'normal').upper()}{Style.RESET_ALL}")
                    print(f"  Confidence: {assessment.get('confidence_score', 0):.2%}")
                    print(f"  Category: {assessment.get('threat_category', 'unknown')}")
                    if assessment.get('indicators'):
                        print(f"\n{Fore.YELLOW}Indicators:{Style.RESET_ALL}")
                        for indicator in assessment.get('indicators', []):
                            print(f"    • {indicator}")
                    if assessment.get('recommended_actions'):
                        print(f"\n{Fore.YELLOW}Recommended Actions:{Style.RESET_ALL}")
                        for action in assessment.get('recommended_actions', []):
                            print(f"    • {action}")
                except Exception as e:
                    self.print_status(f"Analysis failed: {str(e)}", "ERROR")
            else:
                self.print_status("No events to analyze", "WARNING")
        else:
            self.print_status("No events available", "WARNING")
    
    async def cmd_threat_signatures(self, args):
        """Manage threat signatures"""
        print(f"\n{Fore.CYAN}=== Threat Signatures ==={Style.RESET_ALL}")
        
        if not self.threat_engine:
            await self.initialize_components()
        
        if args.action == 'list':
            if hasattr(self.threat_engine, 'threat_signatures'):
                signatures = self.threat_engine.threat_signatures
                print(f"\nLoaded Signatures: {len(signatures)}")
                for sig in signatures[:args.limit]:
                    print(f"\n  ID: {sig.signature_id}")
                    print(f"  Name: {sig.name}")
                    print(f"  Category: {sig.category.value}")
                    print(f"  Confidence: {sig.confidence:.2%}")
                    print(f"  Indicators: {', '.join(sig.indicators[:3])}...")
            else:
                self.print_status("No signatures loaded", "WARNING")
        elif args.action == 'reload':
            self.print_status("Reloading threat signatures...", "INFO")
            try:
                if hasattr(self.threat_engine, '_load_threat_signatures'):
                    self.threat_engine._load_threat_signatures()
                    self.print_status("Signatures reloaded successfully", "SUCCESS")
            except Exception as e:
                self.print_status(f"Failed to reload signatures: {str(e)}", "ERROR")
    
    # ============================================================================
    # RESPONSE COMMANDS
    # ============================================================================
    
    async def cmd_response_history(self, args):
        """View response action history"""
        print(f"\n{Fore.CYAN}=== Response History ==={Style.RESET_ALL}")
        
        if not self.auto_response:
            await self.initialize_components()
        
        try:
            history = self.auto_response.get_response_history(
                threat_id=args.threat_id if hasattr(args, 'threat_id') else None,
                limit=args.limit
            )
            
            if history:
                print(f"\nShowing {len(history)} response action(s):")
                for record in history:
                    print(f"\n  Timestamp: {record.get('timestamp', 'N/A')}")
                    print(f"  Threat ID: {record.get('threat_id', 'N/A')}")
                    print(f"  Action: {record.get('action_type', 'N/A')}")
                    print(f"  Status: {record.get('status', 'N/A')}")
                    print(f"  Result: {record.get('result', 'N/A')}")
            else:
                self.print_status("No response history found", "WARNING")
        except Exception as e:
            self.print_status(f"Failed to retrieve history: {str(e)}", "ERROR")
    
    async def cmd_response_rollback(self, args):
        """Rollback a response action"""
        print(f"\n{Fore.CYAN}=== Rollback Response Action ==={Style.RESET_ALL}")
        
        if not self.auto_response:
            await self.initialize_components()
        
        if not args.confirm:
            print(f"{Fore.YELLOW}Warning: This will rollback action {args.action_id}{Style.RESET_ALL}")
            confirm = input("Continue? (yes/no): ")
            if confirm.lower() != 'yes':
                self.print_status("Rollback cancelled", "WARNING")
                return
        
        try:
            success = self.auto_response.rollback_action(args.action_id)
            if success:
                self.print_status(f"Action {args.action_id} rolled back successfully", "SUCCESS")
            else:
                self.print_status(f"Failed to rollback action {args.action_id}", "ERROR")
        except Exception as e:
            self.print_status(f"Rollback failed: {str(e)}", "ERROR")
    
    # ============================================================================
    # PLATFORM COMMANDS
    # ============================================================================
    
    async def cmd_platform_info(self, args):
        """Display platform information"""
        print(f"\n{Fore.CYAN}=== Platform Information ==={Style.RESET_ALL}")
        
        if not self.platform_interface:
            await self.initialize_components()
        
        try:
            sys_info = self.platform_interface.get_system_info()
            print(f"\n{Fore.YELLOW}System Details:{Style.RESET_ALL}")
            print(f"  OS: {sys_info.os_type.value}")
            print(f"  OS Version: {sys_info.os_version}")
            print(f"  Architecture: {sys_info.architecture}")
            print(f"  Hostname: {sys_info.hostname}")
            print(f"  CPU Count: {sys_info.cpu_count}")
            print(f"  Memory Total: {sys_info.memory_total / (1024**3):.2f} GB")
            print(f"  Running Processes: {sys_info.running_processes}")
            
            if args.hardware:
                hw_info = self.platform_interface.get_hardware_info()
                print(f"\n{Fore.YELLOW}Hardware Information:{Style.RESET_ALL}")
                for key, value in hw_info.items():
                    print(f"  {key}: {value}")
        except Exception as e:
            self.print_status(f"Failed to get platform info: {str(e)}", "ERROR")
    
    async def cmd_platform_processes(self, args):
        """List running processes"""
        print(f"\n{Fore.CYAN}=== Process List ==={Style.RESET_ALL}")
        
        if not self.platform_interface:
            await self.initialize_components()
        
        try:
            processes = self.platform_interface.get_process_list(
                filter_by_name=args.filter if hasattr(args, 'filter') else None
            )
            
            print(f"\nFound {len(processes)} process(es):")
            print(f"\n{'PID':<8} {'Name':<30} {'Status':<12} {'Memory %':<12}")
            print("-" * 62)
            
            for proc in processes[:args.limit]:
                print(f"{proc.pid:<8} {proc.name[:28]:<30} {proc.status:<12} {proc.memory_percent:<12.1f}")
        except Exception as e:
            self.print_status(f"Failed to list processes: {str(e)}", "ERROR")
    
    async def cmd_platform_network(self, args):
        """Display network connections"""
        print(f"\n{Fore.CYAN}=== Network Connections ==={Style.RESET_ALL}")
        
        if not self.platform_interface:
            await self.initialize_components()
        
        try:
            connections = self.platform_interface.get_network_connections(
                filter_by_state=args.state if hasattr(args, 'state') else None
            )
            
            print(f"\nFound {len(connections)} connection(s):")
            print(f"\n{'Protocol':<8} {'Local Address':<25} {'Remote Address':<25} {'Status':<12}")
            print("-" * 70)
            
            for conn in connections[:args.limit]:
                local = f"{conn.get('local_address', '')}:{conn.get('local_port', '')}"
                remote = f"{conn.get('remote_address', '')}:{conn.get('remote_port', '')}"
                print(f"{conn.get('protocol', ''):<8} {local:<25} {remote:<25} {conn.get('status', ''):<12}")
        except Exception as e:
            self.print_status(f"Failed to list connections: {str(e)}", "ERROR")
    
    async def cmd_platform_execute(self, args):
        """Execute a command via platform interface"""
        print(f"\n{Fore.CYAN}=== Execute Command ==={Style.RESET_ALL}")
        
        if not self.platform_interface:
            await self.initialize_components()
        
        if not args.confirm:
            print(f"{Fore.YELLOW}Warning: About to execute: {args.command}{Style.RESET_ALL}")
            confirm = input("Continue? (yes/no): ")
            if confirm.lower() != 'yes':
                self.print_status("Execution cancelled", "WARNING")
                return
        
        try:
            result = self.platform_interface.execute_command(
                args.command,
                timeout=args.timeout if hasattr(args, 'timeout') else 30
            )
            
            print(f"\n{Fore.YELLOW}Exit Code:{Style.RESET_ALL} {result.exit_code}")
            if result.stdout:
                print(f"\n{Fore.YELLOW}Output:{Style.RESET_ALL}")
                print(result.stdout)
            if result.stderr:
                print(f"\n{Fore.RED}Errors:{Style.RESET_ALL}")
                print(result.stderr)
        except Exception as e:
            self.print_status(f"Execution failed: {str(e)}", "ERROR")
    
    # ============================================================================
    # BASENET/AI COMMANDS
    # ============================================================================
    
    async def cmd_ai_query(self, args):
        """Query AI model"""
        print(f"\n{Fore.CYAN}=== AI Query ==={Style.RESET_ALL}")
        
        if not self.basenet_connector:
            await self.initialize_components()
        
        try:
            request = AIRequest(
                request_id=f"cli_{int(time.time())}",
                user_id="cli_user",
                timestamp=datetime.now(),
                model_type=AIModelType.THREAT_ANALYSIS,
                query=args.query,
                context={"source": "cli"},
                priority=5
            )
            
            self.print_status("Querying AI model...", "INFO")
            response = await self.basenet_connector.query_ai_model(request)
            
            if response:
                print(f"\n{Fore.YELLOW}AI Response:{Style.RESET_ALL}")
                print(f"  Response: {response.response_text}")
                # Use getattr for safe attribute access
                confidence = getattr(response.confidence, 'value', response.confidence)
                print(f"  Confidence: {confidence}")
                if response.recommendations:
                    print(f"  Recommendations: {', '.join(response.recommendations)}")
            else:
                self.print_status("No response from AI model", "WARNING")
        except Exception as e:
            self.print_status(f"AI query failed: {str(e)}", "ERROR")
    
    async def cmd_ai_history(self, args):
        """View AI query history"""
        print(f"\n{Fore.CYAN}=== AI Query History ==={Style.RESET_ALL}")
        
        if not self.basenet_connector:
            await self.initialize_components()
        
        try:
            history = self.basenet_connector.get_ai_history(limit=args.limit)
            
            if history:
                print(f"\nShowing {len(history)} query/queries:")
                for record in history:
                    print(f"\n  Timestamp: {record.get('timestamp', 'N/A')}")
                    print(f"  Request ID: {record.get('request_id', 'N/A')}")
                    print(f"  Model: {record.get('model_type', 'N/A')}")
                    print(f"  Query: {record.get('query', 'N/A')[:80]}...")
            else:
                self.print_status("No AI history found", "WARNING")
        except Exception as e:
            self.print_status(f"Failed to retrieve history: {str(e)}", "ERROR")
    
    # ============================================================================
    # HARDWARE/SYSTEM COMMANDS
    # ============================================================================
    
    async def cmd_hardware_metrics(self, args):
        """Display hardware metrics"""
        print(f"\n{Fore.CYAN}=== Hardware Metrics ==={Style.RESET_ALL}")
        
        if not self.system_controller:
            await self.initialize_components()
        
        try:
            if hasattr(self.system_controller, 'hardware_monitor'):
                metrics = self.system_controller.hardware_monitor.collect_hardware_metrics()
                
                print(f"\n{Fore.YELLOW}CPU:{Style.RESET_ALL}")
                print(f"  Usage: {metrics.cpu_usage:.1f}%")
                if metrics.temperature.get('cpu'):
                    print(f"  Temperature: {metrics.temperature['cpu']:.1f}°C")
                
                print(f"\n{Fore.YELLOW}Memory:{Style.RESET_ALL}")
                print(f"  Usage: {metrics.memory_usage:.1f}%")
                
                print(f"\n{Fore.YELLOW}Disk:{Style.RESET_ALL}")
                for device, usage in metrics.disk_usage.items():
                    print(f"  {device}: {usage:.1f}%")
                
                print(f"\n{Fore.YELLOW}Network:{Style.RESET_ALL}")
                for iface, bytes_count in metrics.network_activity.items():
                    print(f"  {iface}: {bytes_count / (1024**2):.2f} MB")
                
                print(f"\n{Fore.YELLOW}Security:{Style.RESET_ALL}")
                print(f"  Threat Level: {metrics.threat_level.value if hasattr(metrics.threat_level, 'value') else metrics.threat_level}")
                print(f"  Security Score: {metrics.security_score:.1f}/100")
                
                if metrics.temperature.get('gpu'):
                    print(f"\n{Fore.YELLOW}GPU:{Style.RESET_ALL}")
                    print(f"  Temperature: {metrics.temperature['gpu']:.1f}°C")
            else:
                self.print_status("Hardware monitor not available", "WARNING")
        except Exception as e:
            self.print_status(f"Failed to get metrics: {str(e)}", "ERROR")
    
    async def cmd_system_admin(self, args):
        """Execute administrative action"""
        print(f"\n{Fore.CYAN}=== Administrative Action ==={Style.RESET_ALL}")
        
        if not self.system_controller:
            await self.initialize_components()
        
        if not args.confirm:
            print(f"{Fore.YELLOW}Warning: About to execute administrative action{Style.RESET_ALL}")
            print(f"  Action: {args.action}")
            print(f"  Target: {args.target}")
            confirm = input("Continue? (yes/no): ")
            if confirm.lower() != 'yes':
                self.print_status("Action cancelled", "WARNING")
                return
        
        try:
            result = self.system_controller.execute_administrative_action(
                action_type=args.action,
                target=args.target,
                parameters=json.loads(args.parameters) if hasattr(args, 'parameters') and args.parameters else {}
            )
            
            if result.get('success'):
                self.print_status(f"Action executed successfully: {result.get('message')}", "SUCCESS")
            else:
                self.print_status(f"Action failed: {result.get('message')}", "ERROR")
        except Exception as e:
            self.print_status(f"Administrative action failed: {str(e)}", "ERROR")
    
    # ============================================================================
    # TARGET MANAGEMENT COMMANDS
    # ============================================================================
    
    async def cmd_target_add(self, args):
        """Add a protection target"""
        print(f"\n{Fore.CYAN}=== Add Protection Target ==={Style.RESET_ALL}")
        
        if not self.system_controller:
            await self.initialize_components()
        
        try:
            result = self.system_controller.add_protection_target(
                name=args.name,
                target_type=args.type,
                path_or_address=args.path,
                description=args.description if hasattr(args, 'description') else "",
                priority=args.priority if hasattr(args, 'priority') else 5,
                metadata=json.loads(args.metadata) if hasattr(args, 'metadata') and args.metadata else None
            )
            
            if result.get('success'):
                self.print_status(f"Target added: {result.get('target_id')}", "SUCCESS")
                print(f"  Name: {args.name}")
                print(f"  Type: {args.type}")
                print(f"  Path: {args.path}")
            else:
                self.print_status(f"Failed to add target: {result.get('error')}", "ERROR")
        except Exception as e:
            self.print_status(f"Failed to add target: {str(e)}", "ERROR")
    
    async def cmd_target_remove(self, args):
        """Remove a protection target"""
        print(f"\n{Fore.CYAN}=== Remove Protection Target ==={Style.RESET_ALL}")
        
        if not self.system_controller:
            await self.initialize_components()
        
        if not args.confirm:
            print(f"{Fore.YELLOW}Warning: About to remove target {args.target_id}{Style.RESET_ALL}")
            confirm = input("Continue? (yes/no): ")
            if confirm.lower() != 'yes':
                self.print_status("Removal cancelled", "WARNING")
                return
        
        try:
            result = self.system_controller.remove_protection_target(args.target_id)
            
            if result.get('success'):
                self.print_status(result.get('message'), "SUCCESS")
            else:
                self.print_status(result.get('error'), "ERROR")
        except Exception as e:
            self.print_status(f"Failed to remove target: {str(e)}", "ERROR")
    
    async def cmd_target_list(self, args):
        """List protection targets"""
        print(f"\n{Fore.CYAN}=== Protection Targets ==={Style.RESET_ALL}")
        
        if not self.system_controller:
            await self.initialize_components()
        
        try:
            targets = self.system_controller.list_protection_targets(
                target_type=args.type if hasattr(args, 'type') and args.type else None,
                status=args.status if hasattr(args, 'status') and args.status else None
            )
            
            if targets:
                print(f"\nFound {len(targets)} target(s):")
                print(f"\n{'ID':<18} {'Name':<25} {'Type':<15} {'Priority':<10} {'Status':<12}")
                print("-" * 90)
                
                for target in targets[:args.limit if hasattr(args, 'limit') else 50]:
                    target_id = target['target_id'][:16]
                    name = target['name'][:23]
                    target_type = target['target_type'][:13]
                    priority = target['priority']
                    status = target['status']
                    
                    # Color code by status
                    if status == 'protected':
                        status_color = Fore.GREEN
                    elif status == 'compromised':
                        status_color = Fore.RED
                    elif status == 'active':
                        status_color = Fore.YELLOW
                    else:
                        status_color = Fore.WHITE
                    
                    print(f"{target_id:<18} {name:<25} {target_type:<15} {priority:<10} {status_color}{status:<12}{Style.RESET_ALL}")
            else:
                self.print_status("No protection targets found", "WARNING")
        except Exception as e:
            self.print_status(f"Failed to list targets: {str(e)}", "ERROR")
    
    async def cmd_target_check(self, args):
        """Check a protection target"""
        print(f"\n{Fore.CYAN}=== Check Protection Target ==={Style.RESET_ALL}")
        
        if not self.system_controller:
            await self.initialize_components()
        
        try:
            result = self.system_controller.check_protection_target(args.target_id)
            
            if result:
                print(f"\n{Fore.YELLOW}Target Status:{Style.RESET_ALL}")
                print(f"  ID: {args.target_id}")
                print(f"  Name: {result.get('name', 'N/A')}")
                print(f"  Status: {result.get('status', 'N/A')}")
                print(f"  Exists: {'✓' if result.get('exists') else '✗'}")
                print(f"  Accessible: {'✓' if result.get('accessible') else '✗'}")
                
                if result.get('details'):
                    print(f"\n{Fore.YELLOW}Details:{Style.RESET_ALL}")
                    for key, value in result['details'].items():
                        print(f"  {key}: {value}")
                
                if result.get('error'):
                    self.print_status(f"Error: {result['error']}", "ERROR")
            else:
                self.print_status("Target not found", "ERROR")
        except Exception as e:
            self.print_status(f"Failed to check target: {str(e)}", "ERROR")
    
    async def cmd_target_info(self, args):
        """Get detailed target information"""
        print(f"\n{Fore.CYAN}=== Target Information ==={Style.RESET_ALL}")
        
        if not self.system_controller:
            await self.initialize_components()
        
        try:
            target = self.system_controller.get_protection_target(args.target_id)
            
            if target:
                print(f"\n{Fore.YELLOW}Target Details:{Style.RESET_ALL}")
                print(f"  ID: {target['target_id']}")
                print(f"  Name: {target['name']}")
                print(f"  Type: {target['target_type']}")
                print(f"  Path/Address: {target['path_or_address']}")
                print(f"  Description: {target.get('description', 'N/A')}")
                print(f"  Priority: {target['priority']}/10")
                print(f"  Status: {target['status']}")
                print(f"  Created: {target['created_at']}")
                print(f"  Last Checked: {target['last_checked']}")
                print(f"  Threat Count: {target['threat_count']}")
                print(f"  Monitoring: {'Enabled' if target['monitoring_enabled'] else 'Disabled'}")
                print(f"  Auto Response: {'Enabled' if target['auto_response_enabled'] else 'Disabled'}")
                
                if target.get('metadata'):
                    print(f"\n{Fore.YELLOW}Metadata:{Style.RESET_ALL}")
                    for key, value in target['metadata'].items():
                        print(f"  {key}: {value}")
                
                # Get recent events
                if args.events:
                    events = self.system_controller.get_target_events(args.target_id, limit=10)
                    if events:
                        print(f"\n{Fore.YELLOW}Recent Events:{Style.RESET_ALL}")
                        for event in events:
                            severity_color = Fore.RED if event['severity'] in ['high', 'critical'] else Fore.YELLOW
                            print(f"  [{event['timestamp']}] {severity_color}{event['severity']}{Style.RESET_ALL} - {event['event_type']}: {event['description']}")
            else:
                self.print_status("Target not found", "ERROR")
        except Exception as e:
            self.print_status(f"Failed to get target info: {str(e)}", "ERROR")

async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Advanced Security Administration System (ASAS) Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Command Categories:
  Core System:     start, stop, status, monitor, scan, config, logs
  Threat Analysis: threat-analyze, threat-signatures
  Response:        response-history, response-rollback
  Platform:        platform-info, platform-processes, platform-network, platform-execute
  AI/BaseNet:      ai-query, ai-history
  Hardware:        hardware-metrics, system-admin
  Target Mgmt:     target-add, target-remove, target-list, target-check, target-info

Examples:
  # Core Operations
  asas start --monitor                    Start ASAS with real-time monitoring
  asas scan --type full                   Run full security scan
  asas status                             Show system status
  
  # Threat Analysis
  asas threat-analyze --limit 20          Analyze recent 20 events
  asas threat-signatures list             List loaded threat signatures
  
  # Response Management
  asas response-history --limit 50        View last 50 response actions
  asas response-rollback 123              Rollback action with ID 123
  
  # Platform Operations
  asas platform-info --hardware           Show detailed platform info
  asas platform-processes --filter python List Python processes
  asas platform-network --state ESTABLISHED  Show established connections
  
  # AI/BaseNet
  asas ai-query "analyze security posture"  Query AI for threat analysis
  asas ai-history --limit 10              View recent AI queries
  
  # Hardware/System
  asas hardware-metrics                   Display hardware metrics
  asas system-admin reboot localhost      Execute admin action
  
  # Target Management
  asas target-add "MyApp" file /app/critical.db --priority 10
  asas target-add "WebServer" network_port 443 --description "HTTPS"
  asas target-add "DataCluster" cluster 10.0.0.0/24 --priority 8
  asas target-list --status protected     List all protected targets
  asas target-check abc123def456          Check target status
  asas target-info abc123def456 --events  View target details and events
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
    
    # ========== THREAT ANALYSIS COMMANDS ==========
    
    # Threat analyze command
    threat_analyze_parser = subparsers.add_parser('threat-analyze', help='Analyze threat events')
    threat_analyze_parser.add_argument('--limit', type=int, default=10, help='Number of recent events to analyze')
    
    # Threat signatures command
    threat_sig_parser = subparsers.add_parser('threat-signatures', help='Manage threat signatures')
    threat_sig_parser.add_argument('action', choices=['list', 'reload'], help='Action to perform')
    threat_sig_parser.add_argument('--limit', type=int, default=10, help='Number of signatures to display')
    
    # ========== RESPONSE COMMANDS ==========
    
    # Response history command
    response_history_parser = subparsers.add_parser('response-history', help='View response action history')
    response_history_parser.add_argument('--threat-id', type=str, help='Filter by threat ID')
    response_history_parser.add_argument('--limit', type=int, default=20, help='Number of records to show')
    
    # Response rollback command
    response_rollback_parser = subparsers.add_parser('response-rollback', help='Rollback a response action')
    response_rollback_parser.add_argument('action_id', type=int, help='Action ID to rollback')
    response_rollback_parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
    
    # ========== PLATFORM COMMANDS ==========
    
    # Platform info command
    platform_info_parser = subparsers.add_parser('platform-info', help='Display platform information')
    platform_info_parser.add_argument('--hardware', action='store_true', help='Include hardware details')
    
    # Platform processes command
    platform_proc_parser = subparsers.add_parser('platform-processes', help='List running processes')
    platform_proc_parser.add_argument('--filter', type=str, help='Filter by process name')
    platform_proc_parser.add_argument('--limit', type=int, default=50, help='Number of processes to show')
    
    # Platform network command
    platform_net_parser = subparsers.add_parser('platform-network', help='Display network connections')
    platform_net_parser.add_argument('--state', type=str, help='Filter by connection state')
    platform_net_parser.add_argument('--limit', type=int, default=50, help='Number of connections to show')
    
    # Platform execute command
    platform_exec_parser = subparsers.add_parser('platform-execute', help='Execute command via platform interface')
    platform_exec_parser.add_argument('command', type=str, help='Command to execute')
    platform_exec_parser.add_argument('--timeout', type=int, default=30, help='Timeout in seconds')
    platform_exec_parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
    
    # ========== BASENET/AI COMMANDS ==========
    
    # AI query command
    ai_query_parser = subparsers.add_parser('ai-query', help='Query AI model')
    ai_query_parser.add_argument('query', type=str, help='Query text')
    
    # AI history command
    ai_history_parser = subparsers.add_parser('ai-history', help='View AI query history')
    ai_history_parser.add_argument('--limit', type=int, default=20, help='Number of records to show')
    
    # ========== HARDWARE/SYSTEM COMMANDS ==========
    
    # Hardware metrics command
    hw_metrics_parser = subparsers.add_parser('hardware-metrics', help='Display hardware metrics')
    
    # System admin command
    sys_admin_parser = subparsers.add_parser('system-admin', help='Execute administrative action')
    sys_admin_parser.add_argument('action', type=str, help='Action type to execute')
    sys_admin_parser.add_argument('target', type=str, help='Target for the action')
    sys_admin_parser.add_argument('--parameters', type=str, help='JSON parameters for the action')
    sys_admin_parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
    
    # ========== TARGET MANAGEMENT COMMANDS ==========
    
    # Target add command
    target_add_parser = subparsers.add_parser('target-add', help='Add a protection target')
    target_add_parser.add_argument('name', type=str, help='Target name')
    target_add_parser.add_argument('type', type=str, 
                                  choices=['file', 'directory', 'process', 'network_port', 'network_address', 
                                          'system', 'container', 'virtual_machine', 'cluster', 'service',
                                          'database', 'api_endpoint', 'mesh_node', 'persistent_universe'],
                                  help='Target type')
    target_add_parser.add_argument('path', type=str, help='Path, address, or identifier')
    target_add_parser.add_argument('--description', type=str, default='', help='Target description')
    target_add_parser.add_argument('--priority', type=int, default=5, choices=range(1, 11), help='Priority (1-10)')
    target_add_parser.add_argument('--metadata', type=str, help='JSON metadata')
    
    # Target remove command
    target_remove_parser = subparsers.add_parser('target-remove', help='Remove a protection target')
    target_remove_parser.add_argument('target_id', type=str, help='Target ID to remove')
    target_remove_parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
    
    # Target list command
    target_list_parser = subparsers.add_parser('target-list', help='List protection targets')
    target_list_parser.add_argument('--type', type=str, help='Filter by target type')
    target_list_parser.add_argument('--status', type=str, help='Filter by status')
    target_list_parser.add_argument('--limit', type=int, default=50, help='Number of targets to show')
    
    # Target check command
    target_check_parser = subparsers.add_parser('target-check', help='Check a protection target')
    target_check_parser.add_argument('target_id', type=str, help='Target ID to check')
    
    # Target info command
    target_info_parser = subparsers.add_parser('target-info', help='Get detailed target information')
    target_info_parser.add_argument('target_id', type=str, help='Target ID')
    target_info_parser.add_argument('--events', action='store_true', help='Show recent events')
    
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
        # Convert dash commands to underscore for method lookup
        command_name = args.command.replace('-', '_')
        command_method = getattr(asas, f'cmd_{command_name}')
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
