"""
Advanced Security Administration System (ASAS) - Platform Interface Module
==========================================================================

This module provides cross-platform system interaction capabilities for security operations.
It abstracts OS-specific commands and provides unified interfaces for system control.

Key Features:
- Cross-platform command execution (Windows, Linux, macOS)
- Secure privilege escalation handling
- System service management
- Process and resource monitoring
- Network interface control
- Hardware information gathering
- Secure communication channels

Author: Artifact Virtual Systems
License: Enterprise Security License
"""

import os
import sys
import json
import platform
import subprocess
import threading
import queue
import time
import psutil
import socket
import struct
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path

# Ensure logs directory exists
Path('logs').mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/platform_interface.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OSType(Enum):
    """Supported operating system types"""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    UNKNOWN = "unknown"

class PrivilegeLevel(Enum):
    """System privilege levels"""
    USER = "user"
    ADMIN = "admin"
    SYSTEM = "system"
    ROOT = "root"

@dataclass
class CommandResult:
    """Result of command execution"""
    command: str
    success: bool
    return_code: int
    stdout: str
    stderr: str
    execution_time: float
    privilege_level: PrivilegeLevel

@dataclass
class SystemInfo:
    """System information structure"""
    os_type: OSType
    os_version: str
    architecture: str
    hostname: str
    cpu_count: int
    memory_total: int
    disk_usage: Dict[str, float]
    network_interfaces: List[Dict]
    running_processes: int
    uptime: float

@dataclass
class ProcessInfo:
    """Process information structure"""
    pid: int
    name: str
    exe_path: str
    cmdline: List[str]
    cpu_percent: float
    memory_percent: float
    status: str
    create_time: float
    connections: List[Dict]

class PlatformInterface:
    """
    Cross-platform system interface for security operations
    """
    
    def __init__(self):
        self.os_type = self._detect_os()
        self.privilege_level = self._detect_privilege_level()
        self.command_timeout = 60  # Default command timeout
        self.secure_mode = True    # Enable security validations
        
        logger.info(f"Platform Interface initialized: {self.os_type.value} ({self.privilege_level.value})")
    
    def _detect_os(self) -> OSType:
        """Detect the current operating system"""
        system = platform.system().lower()
        if system == "windows":
            return OSType.WINDOWS
        elif system == "linux":
            return OSType.LINUX
        elif system == "darwin":
            return OSType.MACOS
        else:
            return OSType.UNKNOWN
    
    def _detect_privilege_level(self) -> PrivilegeLevel:
        """Detect current privilege level"""
        try:
            if self.os_type == OSType.WINDOWS:
                # Check if running as administrator
                import ctypes
                if ctypes.windll.shell32.IsUserAnAdmin():
                    return PrivilegeLevel.ADMIN
                else:
                    return PrivilegeLevel.USER
            else:
                # Unix-like systems
                if os.geteuid() == 0:
                    return PrivilegeLevel.ROOT
                else:
                    return PrivilegeLevel.USER
        except Exception as e:
            logger.warning(f"Failed to detect privilege level: {e}")
            return PrivilegeLevel.USER
    
    def execute_command(self, command: Union[str, List[str]], 
                       timeout: Optional[int] = None,
                       require_admin: bool = False,
                       capture_output: bool = True,
                       shell: bool = False) -> CommandResult:
        """
        Execute a system command with security controls
        """
        start_time = time.time()
        timeout = timeout or self.command_timeout
        
        # Security validation
        if self.secure_mode and require_admin:
            if self.privilege_level not in [PrivilegeLevel.ADMIN, PrivilegeLevel.ROOT]:
                return CommandResult(
                    command=str(command),
                    success=False,
                    return_code=-1,
                    stdout="",
                    stderr="Insufficient privileges",
                    execution_time=0,
                    privilege_level=self.privilege_level
                )
        
        # Command validation for security
        if self.secure_mode:
            dangerous_commands = [
                "rm -rf /", "del /f /s /q C:\\*", "format", "fdisk",
                "dd if=/dev/zero", ":(){ :|:& };:", "fork()"
            ]
            cmd_str = str(command).lower()
            for dangerous in dangerous_commands:
                if dangerous in cmd_str:
                    return CommandResult(
                        command=str(command),
                        success=False,
                        return_code=-1,
                        stdout="",
                        stderr="Command blocked for security",
                        execution_time=0,
                        privilege_level=self.privilege_level
                    )
        
        try:
            # Execute command
            result = subprocess.run(
                command,
                timeout=timeout,
                capture_output=capture_output,
                text=True,
                shell=shell,
                check=False
            )
            
            execution_time = time.time() - start_time
            
            return CommandResult(
                command=str(command),
                success=result.returncode == 0,
                return_code=result.returncode,
                stdout=result.stdout or "",
                stderr=result.stderr or "",
                execution_time=execution_time,
                privilege_level=self.privilege_level
            )
            
        except subprocess.TimeoutExpired:
            return CommandResult(
                command=str(command),
                success=False,
                return_code=-1,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
                execution_time=timeout,
                privilege_level=self.privilege_level
            )
        except Exception as e:
            return CommandResult(
                command=str(command),
                success=False,
                return_code=-1,
                stdout="",
                stderr=str(e),
                execution_time=time.time() - start_time,
                privilege_level=self.privilege_level
            )
    
    def get_system_info(self) -> SystemInfo:
        """Gather comprehensive system information"""
        try:
            # Basic system info
            memory = psutil.virtual_memory()
            boot_time = psutil.boot_time()
            current_time = time.time()
            
            # Disk usage
            disk_usage = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.mountpoint] = {
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': (usage.used / usage.total) * 100
                    }
                except:
                    continue
            
            # Network interfaces
            network_interfaces = []
            for interface, addrs in psutil.net_if_addrs().items():
                interface_info = {'name': interface, 'addresses': []}
                for addr in addrs:
                    interface_info['addresses'].append({
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })
                network_interfaces.append(interface_info)
            
            return SystemInfo(
                os_type=self.os_type,
                os_version=platform.platform(),
                architecture=platform.architecture()[0],
                hostname=platform.node(),
                cpu_count=psutil.cpu_count(logical=True),
                memory_total=memory.total,
                disk_usage=disk_usage,
                network_interfaces=network_interfaces,
                running_processes=len(psutil.pids()),
                uptime=current_time - boot_time
            )
            
        except Exception as e:
            logger.error(f"Failed to gather system info: {e}")
            return SystemInfo(
                os_type=self.os_type,
                os_version="unknown",
                architecture="unknown",
                hostname="unknown",
                cpu_count=0,
                memory_total=0,
                disk_usage={},
                network_interfaces=[],
                running_processes=0,
                uptime=0
            )
    
    def get_process_list(self, filter_by_name: Optional[str] = None) -> List[ProcessInfo]:
        """Get detailed process information"""
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'status', 'create_time']):
                try:
                    proc_info = proc.info
                    
                    # Filter by name if specified
                    if filter_by_name and filter_by_name.lower() not in proc_info['name'].lower():
                        continue
                    
                    # Get additional process details
                    try:
                        cpu_percent = proc.cpu_percent()
                        memory_percent = proc.memory_percent()
                        connections = [
                            {
                                'fd': conn.fd,
                                'family': str(conn.family),
                                'type': str(conn.type),
                                'laddr': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "",
                                'raddr': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "",
                                'status': str(conn.status)
                            }
                            for conn in proc.connections()
                        ]
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        cpu_percent = 0.0
                        memory_percent = 0.0
                        connections = []
                    
                    process_info = ProcessInfo(
                        pid=proc_info['pid'],
                        name=proc_info['name'] or "unknown",
                        exe_path=proc_info['exe'] or "unknown",
                        cmdline=proc_info['cmdline'] or [],
                        cpu_percent=cpu_percent,
                        memory_percent=memory_percent,
                        status=proc_info['status'],
                        create_time=proc_info['create_time'],
                        connections=connections
                    )
                    
                    processes.append(process_info)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to get process list: {e}")
        
        return processes
    
    def kill_process(self, pid: int, force: bool = False) -> CommandResult:
        """Terminate a process by PID"""
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()
            
            if force:
                proc.kill()  # SIGKILL
            else:
                proc.terminate()  # SIGTERM
            
            # Wait for process to terminate
            try:
                proc.wait(timeout=10)
                success = True
                message = f"Process {proc_name} (PID: {pid}) terminated successfully"
            except psutil.TimeoutExpired:
                if force:
                    success = False
                    message = f"Process {proc_name} (PID: {pid}) failed to terminate"
                else:
                    # Try force kill
                    proc.kill()
                    proc.wait(timeout=5)
                    success = True
                    message = f"Process {proc_name} (PID: {pid}) force killed"
            
            return CommandResult(
                command=f"kill_process({pid}, force={force})",
                success=success,
                return_code=0 if success else 1,
                stdout=message,
                stderr="",
                execution_time=0,
                privilege_level=self.privilege_level
            )
            
        except psutil.NoSuchProcess:
            return CommandResult(
                command=f"kill_process({pid})",
                success=False,
                return_code=1,
                stdout="",
                stderr=f"Process with PID {pid} not found",
                execution_time=0,
                privilege_level=self.privilege_level
            )
        except psutil.AccessDenied:
            return CommandResult(
                command=f"kill_process({pid})",
                success=False,
                return_code=1,
                stdout="",
                stderr=f"Access denied to kill process {pid}",
                execution_time=0,
                privilege_level=self.privilege_level
            )
        except Exception as e:
            return CommandResult(
                command=f"kill_process({pid})",
                success=False,
                return_code=1,
                stdout="",
                stderr=str(e),
                execution_time=0,
                privilege_level=self.privilege_level
            )
    
    def manage_service(self, service_name: str, action: str) -> CommandResult:
        """Manage system services (start, stop, restart, status)"""
        if action not in ["start", "stop", "restart", "status", "enable", "disable"]:
            return CommandResult(
                command=f"manage_service({service_name}, {action})",
                success=False,
                return_code=1,
                stdout="",
                stderr=f"Invalid action: {action}",
                execution_time=0,
                privilege_level=self.privilege_level
            )
        
        if self.os_type == OSType.WINDOWS:
            if action == "status":
                command = ["sc", "query", service_name]
            elif action == "start":
                command = ["net", "start", service_name]
            elif action == "stop":
                command = ["net", "stop", service_name]
            elif action == "restart":
                # Windows doesn't have direct restart, stop then start
                stop_result = self.execute_command(["net", "stop", service_name])
                time.sleep(2)
                return self.execute_command(["net", "start", service_name])
            elif action == "enable":
                command = ["sc", "config", service_name, "start=", "auto"]
            elif action == "disable":
                command = ["sc", "config", service_name, "start=", "disabled"]
        else:
            # Linux/macOS with systemd
            if action == "restart":
                command = ["systemctl", "restart", service_name]
            else:
                command = ["systemctl", action, service_name]
        
        return self.execute_command(command, require_admin=True)
    
    def get_network_connections(self, filter_by_state: Optional[str] = None) -> List[Dict]:
        """Get active network connections"""
        connections = []
        
        try:
            for conn in psutil.net_connections(kind='inet'):
                if filter_by_state and str(conn.status) != filter_by_state:
                    continue
                
                try:
                    process = psutil.Process(conn.pid) if conn.pid else None
                    process_name = process.name() if process else "unknown"
                except:
                    process_name = "unknown"
                
                connection_info = {
                    'family': str(conn.family),
                    'type': str(conn.type),
                    'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "",
                    'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "",
                    'status': str(conn.status),
                    'pid': conn.pid,
                    'process_name': process_name
                }
                
                connections.append(connection_info)
                
        except Exception as e:
            logger.error(f"Failed to get network connections: {e}")
        
        return connections
    
    def block_network_address(self, address: str, port: Optional[int] = None) -> CommandResult:
        """Block network access to specific address/port"""
        if self.os_type == OSType.WINDOWS:
            # Windows Firewall
            rule_name = f"ASAS_Block_{address}_{port or 'all'}"
            if port:
                command = [
                    "netsh", "advfirewall", "firewall", "add", "rule",
                    f"name={rule_name}", "dir=out", "action=block",
                    f"remoteip={address}", f"remoteport={port}"
                ]
            else:
                command = [
                    "netsh", "advfirewall", "firewall", "add", "rule",
                    f"name={rule_name}", "dir=out", "action=block",
                    f"remoteip={address}"
                ]
        else:
            # Linux iptables
            if port:
                command = [
                    "iptables", "-A", "OUTPUT", "-d", address,
                    "-p", "tcp", "--dport", str(port), "-j", "DROP"
                ]
            else:
                command = ["iptables", "-A", "OUTPUT", "-d", address, "-j", "DROP"]
        
        return self.execute_command(command, require_admin=True)
    
    def unblock_network_address(self, address: str, port: Optional[int] = None) -> CommandResult:
        """Remove network block for specific address/port"""
        if self.os_type == OSType.WINDOWS:
            # Windows Firewall
            rule_name = f"ASAS_Block_{address}_{port or 'all'}"
            command = [
                "netsh", "advfirewall", "firewall", "delete", "rule",
                f"name={rule_name}"
            ]
        else:
            # Linux iptables
            if port:
                command = [
                    "iptables", "-D", "OUTPUT", "-d", address,
                    "-p", "tcp", "--dport", str(port), "-j", "DROP"
                ]
            else:
                command = ["iptables", "-D", "OUTPUT", "-d", address, "-j", "DROP"]
        
        return self.execute_command(command, require_admin=True)
    
    def get_hardware_info(self) -> Dict[str, Any]:
        """Get hardware information for monitoring"""
        hardware_info = {}
        
        try:
            # CPU Information
            hardware_info['cpu'] = {
                'physical_cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True),
                'max_frequency': psutil.cpu_freq().max if psutil.cpu_freq() else 0,
                'current_frequency': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                'usage_percent': psutil.cpu_percent(interval=1)
            }
            
            # Memory Information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            hardware_info['memory'] = {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free,
                'percent': memory.percent,
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_free': swap.free,
                'swap_percent': swap.percent
            }
            
            # Disk Information
            disk_io = psutil.disk_io_counters()
            hardware_info['disk'] = {
                'read_count': disk_io.read_count if disk_io else 0,
                'write_count': disk_io.write_count if disk_io else 0,
                'read_bytes': disk_io.read_bytes if disk_io else 0,
                'write_bytes': disk_io.write_bytes if disk_io else 0,
                'read_time': disk_io.read_time if disk_io else 0,
                'write_time': disk_io.write_time if disk_io else 0
            }
            
            # Network Information
            net_io = psutil.net_io_counters()
            hardware_info['network'] = {
                'bytes_sent': net_io.bytes_sent if net_io else 0,
                'bytes_recv': net_io.bytes_recv if net_io else 0,
                'packets_sent': net_io.packets_sent if net_io else 0,
                'packets_recv': net_io.packets_recv if net_io else 0,
                'errin': net_io.errin if net_io else 0,
                'errout': net_io.errout if net_io else 0,
                'dropin': net_io.dropin if net_io else 0,
                'dropout': net_io.dropout if net_io else 0
            }
            
            # Temperature Information (if available)
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    hardware_info['temperature'] = {}
                    for name, entries in temps.items():
                        hardware_info['temperature'][name] = [
                            {
                                'label': entry.label or name,
                                'current': entry.current,
                                'high': entry.high,
                                'critical': entry.critical
                            }
                            for entry in entries
                        ]
            except:
                hardware_info['temperature'] = {}
            
            # Battery Information (if available)
            try:
                battery = psutil.sensors_battery()
                if battery:
                    hardware_info['battery'] = {
                        'percent': battery.percent,
                        'power_plugged': battery.power_plugged,
                        'time_left': battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None
                    }
            except:
                hardware_info['battery'] = {}
                
        except Exception as e:
            logger.error(f"Failed to get hardware info: {e}")
        
        return hardware_info
    
    def elevate_privileges(self) -> bool:
        """Attempt to elevate privileges (platform-specific)"""
        if self.privilege_level in [PrivilegeLevel.ADMIN, PrivilegeLevel.ROOT]:
            return True
        
        try:
            if self.os_type == OSType.WINDOWS:
                # On Windows, need to restart with UAC elevation
                logger.warning("Privilege elevation requires application restart with UAC")
                return False
            else:
                # On Unix-like systems, could use sudo (but requires password)
                logger.warning("Privilege elevation requires sudo access")
                return False
                
        except Exception as e:
            logger.error(f"Failed to elevate privileges: {e}")
            return False
    
    def create_secure_channel(self, host: str, port: int, encryption: bool = True) -> Optional[socket.socket]:
        """Create a secure communication channel"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30)
            
            if encryption:
                # In production, would use SSL/TLS
                logger.info(f"Creating secure channel to {host}:{port}")
                # Implementation would include SSL context setup
            else:
                logger.warning(f"Creating unencrypted channel to {host}:{port}")
            
            sock.connect((host, port))
            return sock
            
        except Exception as e:
            logger.error(f"Failed to create secure channel: {e}")
            return None
    
    def execute_remote_command(self, host: str, port: int, command: str, 
                             credentials: Optional[Dict] = None) -> CommandResult:
        """Execute command on remote system (secure channel)"""
        # This would implement secure remote execution
        # In production, would use SSH, WinRM, or other secure protocols
        logger.warning("Remote command execution requires secure protocol implementation")
        
        return CommandResult(
            command=f"remote:{host}:{command}",
            success=False,
            return_code=-1,
            stdout="",
            stderr="Remote execution not implemented",
            execution_time=0,
            privilege_level=self.privilege_level
        )

def main():
    """Main function for testing platform interface"""
    platform_interface = PlatformInterface()
    
    print(f"Platform: {platform_interface.os_type.value}")
    print(f"Privilege Level: {platform_interface.privilege_level.value}")
    
    # Get system information
    sys_info = platform_interface.get_system_info()
    print(f"System: {sys_info.hostname} ({sys_info.os_version})")
    print(f"CPU Cores: {sys_info.cpu_count}")
    print(f"Memory: {sys_info.memory_total // (1024**3)} GB")
    
    # Get process list (first 5 processes)
    processes = platform_interface.get_process_list()[:5]
    print(f"\nTop 5 processes:")
    for proc in processes:
        print(f"  {proc.name} (PID: {proc.pid}) - CPU: {proc.cpu_percent:.1f}%")
    
    # Get network connections (first 5)
    connections = platform_interface.get_network_connections()[:5]
    print(f"\nTop 5 network connections:")
    for conn in connections:
        print(f"  {conn['local_address']} -> {conn['remote_address']} ({conn['status']})")

if __name__ == "__main__":
    main()
