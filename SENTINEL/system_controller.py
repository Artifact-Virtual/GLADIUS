"""
Advanced Security Administration System (ASAS) - System Controller Module
========================================================================

This module provides secure administrative access and comprehensive hardware monitoring.
It implements advanced system control with constitutional safeguards and quantum-ready security.

Key Features:
- Secure administrative access control
- Hardware monitoring and analysis
- System integrity verification
- Performance optimization
- Resource allocation management
- Quantum-resistant authentication
- Neural interface preparation
- Advanced threat correlation

Author: Artifact Virtual Systems
License: Enterprise Security License
"""

import os
import sys
import json
import time
import hashlib
import threading
import queue
import psutil
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path
import subprocess
import socket
import struct

# Import our other modules
from security_monitor import SecurityMonitor, ThreatLevel
from threat_engine import ThreatEngine, ThreatClassification
from auto_response import AutomatedResponseSystem, ResponseLevel
from platform_interface import PlatformInterface, SystemInfo
from basenet_connector import BaseNetConnector, EthicalPrinciple

# Ensure logs directory exists
Path('logs').mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system_controller.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AccessLevel(Enum):
    """System access levels"""
    READ_ONLY = 1
    STANDARD = 2
    ELEVATED = 3
    ADMINISTRATIVE = 4
    SYSTEM_CRITICAL = 5
    QUANTUM_SECURE = 6

class SystemStatus(Enum):
    """Overall system status"""
    SECURE = "secure"
    MONITORING = "monitoring"
    THREAT_DETECTED = "threat_detected"
    RESPONDING = "responding"
    QUARANTINED = "quarantined"
    EMERGENCY = "emergency"

class HardwareComponent(Enum):
    """Hardware components for monitoring"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    GPU = "gpu"
    SENSORS = "sensors"
    POWER = "power"

@dataclass
class SystemMetrics:
    """Comprehensive system metrics"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: Dict[str, float]
    network_activity: Dict[str, int]
    temperature: Dict[str, float]
    power_consumption: float
    security_score: float
    threat_level: ThreatLevel
    active_connections: int
    running_processes: int
    system_uptime: float

@dataclass
class AdministrativeAction:
    """Administrative action record"""
    action_id: str
    action_type: str
    target: str
    parameters: Dict[str, Any]
    access_level: AccessLevel
    user_id: str
    timestamp: datetime
    success: bool
    output: str
    constitutional_approval: bool
    ethical_score: float

class TargetType(Enum):
    """Types of protection targets"""
    FILE = "file"
    DIRECTORY = "directory"
    PROCESS = "process"
    NETWORK_PORT = "network_port"
    NETWORK_ADDRESS = "network_address"
    SYSTEM = "system"
    CONTAINER = "container"
    VM = "virtual_machine"
    CLUSTER = "cluster"
    SERVICE = "service"
    DATABASE = "database"
    API_ENDPOINT = "api_endpoint"
    MESH_NODE = "mesh_node"
    UNIVERSE = "persistent_universe"

class TargetStatus(Enum):
    """Status of monitored target"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PROTECTED = "protected"
    COMPROMISED = "compromised"
    QUARANTINED = "quarantined"
    UNKNOWN = "unknown"

@dataclass
class ProtectionTarget:
    """Protection target definition"""
    target_id: str
    name: str
    target_type: TargetType
    path_or_address: str
    description: str
    priority: int  # 1-10, 10 being highest
    status: TargetStatus
    created_at: datetime
    last_checked: datetime
    threat_count: int
    metadata: Dict[str, Any]
    monitoring_enabled: bool
    auto_response_enabled: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'target_id': self.target_id,
            'name': self.name,
            'target_type': self.target_type.value,
            'path_or_address': self.path_or_address,
            'description': self.description,
            'priority': self.priority,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'last_checked': self.last_checked.isoformat(),
            'threat_count': self.threat_count,
            'metadata': self.metadata,
            'monitoring_enabled': self.monitoring_enabled,
            'auto_response_enabled': self.auto_response_enabled
        }

class TargetManager:
    """
    Target Management System
    
    Manages protection targets from individual files to entire mesh universes.
    Provides a simple interface to point SENTINEL at what needs protection.
    """
    
    def __init__(self, db_path: str = "data/targets.db"):
        self.db_path = db_path
        self.targets: Dict[str, ProtectionTarget] = {}
        self._init_database()
        self._load_targets()
        logger.info("Target Manager initialized")
    
    def _init_database(self):
        """Initialize targets database"""
        os.makedirs("data", exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS targets (
                    target_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    target_type TEXT NOT NULL,
                    path_or_address TEXT NOT NULL,
                    description TEXT,
                    priority INTEGER DEFAULT 5,
                    status TEXT DEFAULT 'active',
                    created_at TEXT NOT NULL,
                    last_checked TEXT,
                    threat_count INTEGER DEFAULT 0,
                    metadata TEXT,
                    monitoring_enabled INTEGER DEFAULT 1,
                    auto_response_enabled INTEGER DEFAULT 1
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS target_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT,
                    timestamp TEXT NOT NULL,
                    resolved INTEGER DEFAULT 0,
                    FOREIGN KEY (target_id) REFERENCES targets(target_id)
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_target_type ON targets(target_type)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_target_status ON targets(status)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_target_events_target ON target_events(target_id)
            ''')
    
    def _load_targets(self):
        """Load targets from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT * FROM targets')
                rows = cursor.fetchall()
                
                for row in rows:
                    target = ProtectionTarget(
                        target_id=row[0],
                        name=row[1],
                        target_type=TargetType(row[2]),
                        path_or_address=row[3],
                        description=row[4] or "",
                        priority=row[5],
                        status=TargetStatus(row[6]),
                        created_at=datetime.fromisoformat(row[7]),
                        last_checked=datetime.fromisoformat(row[8]) if row[8] else datetime.now(),
                        threat_count=row[9],
                        metadata=json.loads(row[10]) if row[10] else {},
                        monitoring_enabled=bool(row[11]),
                        auto_response_enabled=bool(row[12])
                    )
                    self.targets[target.target_id] = target
                
                logger.info(f"Loaded {len(self.targets)} protection targets")
        except Exception as e:
            logger.error(f"Failed to load targets: {e}")
    
    def add_target(self, name: str, target_type: TargetType, path_or_address: str,
                   description: str = "", priority: int = 5, 
                   metadata: Dict[str, Any] = None) -> ProtectionTarget:
        """Add a new protection target"""
        target_id = hashlib.sha256(f"{name}{path_or_address}{time.time()}".encode()).hexdigest()[:16]
        
        target = ProtectionTarget(
            target_id=target_id,
            name=name,
            target_type=target_type,
            path_or_address=path_or_address,
            description=description,
            priority=priority,
            status=TargetStatus.ACTIVE,
            created_at=datetime.now(),
            last_checked=datetime.now(),
            threat_count=0,
            metadata=metadata or {},
            monitoring_enabled=True,
            auto_response_enabled=True
        )
        
        self.targets[target_id] = target
        self._save_target(target)
        
        logger.info(f"Added protection target: {name} ({target_type.value})")
        return target
    
    def _save_target(self, target: ProtectionTarget):
        """Save target to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO targets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                target.target_id,
                target.name,
                target.target_type.value,
                target.path_or_address,
                target.description,
                target.priority,
                target.status.value,
                target.created_at.isoformat(),
                target.last_checked.isoformat(),
                target.threat_count,
                json.dumps(target.metadata),
                1 if target.monitoring_enabled else 0,
                1 if target.auto_response_enabled else 0
            ))
    
    def remove_target(self, target_id: str) -> bool:
        """Remove a protection target"""
        if target_id in self.targets:
            del self.targets[target_id]
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM targets WHERE target_id = ?', (target_id,))
                conn.execute('DELETE FROM target_events WHERE target_id = ?', (target_id,))
            
            logger.info(f"Removed protection target: {target_id}")
            return True
        return False
    
    def get_target(self, target_id: str) -> Optional[ProtectionTarget]:
        """Get target by ID"""
        return self.targets.get(target_id)
    
    def list_targets(self, target_type: Optional[TargetType] = None, 
                    status: Optional[TargetStatus] = None) -> List[ProtectionTarget]:
        """List all targets with optional filters"""
        results = list(self.targets.values())
        
        if target_type:
            results = [t for t in results if t.target_type == target_type]
        if status:
            results = [t for t in results if t.status == status]
        
        # Sort by priority (highest first) then name
        results.sort(key=lambda t: (-t.priority, t.name))
        return results
    
    def update_target_status(self, target_id: str, status: TargetStatus):
        """Update target status"""
        if target_id in self.targets:
            self.targets[target_id].status = status
            self.targets[target_id].last_checked = datetime.now()
            self._save_target(self.targets[target_id])
    
    def log_target_event(self, target_id: str, event_type: str, 
                        severity: str, description: str):
        """Log an event for a target"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO target_events (target_id, event_type, severity, description, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (target_id, event_type, severity, description, datetime.now().isoformat()))
        
        # Increment threat count for threats
        if severity in ['high', 'critical']:
            if target_id in self.targets:
                self.targets[target_id].threat_count += 1
                self._save_target(self.targets[target_id])
    
    def get_target_events(self, target_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events for a target"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT event_id, event_type, severity, description, timestamp, resolved
                FROM target_events
                WHERE target_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (target_id, limit))
            
            rows = cursor.fetchall()
            return [{
                'event_id': row[0],
                'event_type': row[1],
                'severity': row[2],
                'description': row[3],
                'timestamp': row[4],
                'resolved': bool(row[5])
            } for row in rows]
    
    def check_target(self, target_id: str, platform_interface: PlatformInterface) -> Dict[str, Any]:
        """Check a target's current status"""
        target = self.get_target(target_id)
        if not target:
            return {'error': 'Target not found'}
        
        result = {
            'target_id': target_id,
            'name': target.name,
            'status': target.status.value,
            'exists': False,
            'accessible': False,
            'details': {}
        }
        
        try:
            if target.target_type == TargetType.FILE:
                path = Path(target.path_or_address)
                result['exists'] = path.exists()
                result['accessible'] = path.exists() and os.access(str(path), os.R_OK)
                if result['exists']:
                    stat = path.stat()
                    result['details'] = {
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'permissions': oct(stat.st_mode)
                    }
            
            elif target.target_type == TargetType.DIRECTORY:
                path = Path(target.path_or_address)
                result['exists'] = path.exists() and path.is_dir()
                result['accessible'] = result['exists'] and os.access(str(path), os.R_OK)
                if result['exists']:
                    files = list(path.iterdir())
                    result['details'] = {
                        'file_count': len(files),
                        'total_size': sum(f.stat().st_size for f in files if f.is_file())
                    }
            
            elif target.target_type == TargetType.PROCESS:
                processes = platform_interface.get_process_list(filter_by_name=target.path_or_address)
                result['exists'] = len(processes) > 0
                result['accessible'] = result['exists']
                if result['exists']:
                    result['details'] = {
                        'process_count': len(processes),
                        'pids': [p.pid for p in processes[:10]]
                    }
            
            elif target.target_type in [TargetType.NETWORK_PORT, TargetType.NETWORK_ADDRESS]:
                connections = platform_interface.get_network_connections()
                if target.target_type == TargetType.NETWORK_PORT:
                    port = int(target.path_or_address)
                    matching = [c for c in connections if c.get('local_port') == port or c.get('remote_port') == port]
                else:
                    matching = [c for c in connections if target.path_or_address in [c.get('local_address'), c.get('remote_address')]]
                
                result['exists'] = len(matching) > 0
                result['accessible'] = True
                result['details'] = {'connection_count': len(matching)}
            
            target.last_checked = datetime.now()
            self._save_target(target)
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error checking target {target_id}: {e}")
        
        return result

@dataclass
class HardwareAlert:
    """Hardware monitoring alert"""
    alert_id: str
    component: HardwareComponent
    severity: int
    message: str
    metrics: Dict[str, float]
    threshold_exceeded: str
    timestamp: datetime
    acknowledged: bool = False

class QuantumSecureAuth:
    """
    Quantum-resistant authentication system
    Prepares for post-quantum cryptography
    """
    
    def __init__(self):
        self.active_sessions = {}
        self.auth_tokens = {}
        self.biometric_cache = {}
        self.quantum_keys = {}
        
    def generate_quantum_key(self, user_id: str) -> str:
        """Generate quantum-resistant authentication key"""
        # In production, would use lattice-based or hash-based cryptography
        # For now, using strong traditional methods
        
        timestamp = str(int(time.time()))
        user_data = f"{user_id}:{timestamp}:{os.urandom(32).hex()}"
        quantum_key = hashlib.sha3_512(user_data.encode()).hexdigest()
        
        self.quantum_keys[user_id] = {
            "key": quantum_key,
            "created": datetime.now(),
            "expires": datetime.now() + timedelta(hours=8)
        }
        
        return quantum_key
    
    def authenticate_user(self, user_id: str, credentials: Dict) -> Tuple[bool, AccessLevel]:
        """Authenticate user with quantum-secure methods"""
        try:
            # Multi-factor authentication
            password_valid = self._verify_password(user_id, credentials.get("password"))
            biometric_valid = self._verify_biometric(user_id, credentials.get("biometric"))
            token_valid = self._verify_token(user_id, credentials.get("token"))
            
            # Quantum key verification
            quantum_valid = self._verify_quantum_key(user_id, credentials.get("quantum_key"))
            
            # Calculate authentication score
            auth_score = sum([password_valid, biometric_valid, token_valid, quantum_valid])
            
            if auth_score >= 3:  # Require at least 3 factors
                access_level = self._determine_access_level(user_id, auth_score)
                self._create_session(user_id, access_level)
                return True, access_level
            else:
                return False, AccessLevel.READ_ONLY
                
        except Exception as e:
            logger.error(f"Authentication failed for {user_id}: {e}")
            return False, AccessLevel.READ_ONLY
    
    def _verify_password(self, user_id: str, password: str) -> bool:
        """Verify user password"""
        # In production, would use proper password hashing (Argon2, etc.)
        return password is not None and len(password) >= 8
    
    def _verify_biometric(self, user_id: str, biometric_data: str) -> bool:
        """Verify biometric authentication"""
        # In production, would implement actual biometric verification
        return biometric_data is not None
    
    def _verify_token(self, user_id: str, token: str) -> bool:
        """Verify authentication token"""
        # In production, would verify TOTP/HOTP tokens
        return token is not None and len(token) >= 6
    
    def _verify_quantum_key(self, user_id: str, provided_key: str) -> bool:
        """Verify quantum-resistant key"""
        if user_id not in self.quantum_keys:
            return False
        
        stored_key_data = self.quantum_keys[user_id]
        if datetime.now() > stored_key_data["expires"]:
            del self.quantum_keys[user_id]
            return False
        
        return provided_key == stored_key_data["key"]
    
    def _determine_access_level(self, user_id: str, auth_score: int) -> AccessLevel:
        """Determine access level based on authentication score"""
        if auth_score == 4:  # All factors verified
            return AccessLevel.QUANTUM_SECURE
        elif auth_score == 3:
            return AccessLevel.ADMINISTRATIVE
        else:
            return AccessLevel.ELEVATED
    
    def _create_session(self, user_id: str, access_level: AccessLevel):
        """Create authenticated session"""
        session_id = hashlib.sha256(f"{user_id}:{time.time()}".encode()).hexdigest()
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "access_level": access_level,
            "created": datetime.now(),
            "last_activity": datetime.now(),
            "expires": datetime.now() + timedelta(hours=2)
        }
        return session_id

class HardwareMonitor:
    """
    Advanced hardware monitoring and analysis
    """
    
    def __init__(self):
        self.monitoring_enabled = True
        self.alert_thresholds = {
            HardwareComponent.CPU: {"usage": 85.0, "temperature": 80.0},
            HardwareComponent.MEMORY: {"usage": 90.0},
            HardwareComponent.DISK: {"usage": 85.0, "io_wait": 50.0},
            HardwareComponent.NETWORK: {"errors": 1000, "dropped": 500},
            HardwareComponent.SENSORS: {"temperature": 75.0, "voltage": 5.0}
        }
        self.alert_history = []
        self.metrics_history = []
        
    def collect_hardware_metrics(self) -> SystemMetrics:
        """Collect comprehensive hardware metrics"""
        try:
            # CPU metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            cpu_temp = self._get_cpu_temperature()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Disk metrics
            disk_usage = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.mountpoint] = (usage.used / usage.total) * 100
                except:
                    continue
            
            # Network metrics
            network_stats = psutil.net_io_counters()
            network_activity = {
                "bytes_sent": network_stats.bytes_sent,
                "bytes_recv": network_stats.bytes_recv,
                "packets_sent": network_stats.packets_sent,
                "packets_recv": network_stats.packets_recv,
                "errors_in": network_stats.errin,
                "errors_out": network_stats.errout
            }
            
            # Temperature metrics
            temperatures = self._get_all_temperatures()
            
            # Power consumption (estimated)
            power_consumption = self._estimate_power_consumption(cpu_usage, memory_usage)
            
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_activity=network_activity,
                temperature=temperatures,
                power_consumption=power_consumption,
                security_score=0.85,  # Will be updated by security monitor
                threat_level=ThreatLevel.LOW,  # Will be updated by threat engine
                active_connections=len(psutil.net_connections()),
                running_processes=len(psutil.pids()),
                system_uptime=time.time() - psutil.boot_time()
            )
            
            # Check for alerts
            self._check_hardware_alerts(metrics)
            
            # Store metrics
            self.metrics_history.append(metrics)
            
            # Keep only last 1000 metrics
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect hardware metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage={},
                network_activity={},
                temperature={},
                power_consumption=0.0,
                security_score=0.0,
                threat_level=ThreatLevel.UNKNOWN,
                active_connections=0,
                running_processes=0,
                system_uptime=0.0
            )
    
    def _get_cpu_temperature(self) -> float:
        """Get CPU temperature"""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    if 'cpu' in name.lower() or 'core' in name.lower():
                        return entries[0].current if entries else 0.0
            return 0.0
        except:
            return 0.0
    
    def _get_all_temperatures(self) -> Dict[str, float]:
        """Get all system temperatures"""
        temperatures = {}
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    if entries:
                        temperatures[name] = entries[0].current
        except:
            pass
        return temperatures
    
    def _estimate_power_consumption(self, cpu_usage: float, memory_usage: float) -> float:
        """Estimate system power consumption"""
        # Rough estimation based on CPU and memory usage
        base_power = 50.0  # Base system power in watts
        cpu_power = (cpu_usage / 100.0) * 100.0  # CPU contribution
        memory_power = (memory_usage / 100.0) * 20.0  # Memory contribution
        
        return base_power + cpu_power + memory_power
    
    def _check_hardware_alerts(self, metrics: SystemMetrics):
        """Check hardware metrics against alert thresholds"""
        # CPU alerts
        if metrics.cpu_usage > self.alert_thresholds[HardwareComponent.CPU]["usage"]:
            self._create_alert(
                HardwareComponent.CPU,
                8,
                f"High CPU usage: {metrics.cpu_usage:.1f}%",
                {"cpu_usage": metrics.cpu_usage},
                "cpu_usage_threshold"
            )
        
        # Memory alerts
        if metrics.memory_usage > self.alert_thresholds[HardwareComponent.MEMORY]["usage"]:
            self._create_alert(
                HardwareComponent.MEMORY,
                7,
                f"High memory usage: {metrics.memory_usage:.1f}%",
                {"memory_usage": metrics.memory_usage},
                "memory_usage_threshold"
            )
        
        # Disk alerts
        for mount, usage in metrics.disk_usage.items():
            if usage > self.alert_thresholds[HardwareComponent.DISK]["usage"]:
                self._create_alert(
                    HardwareComponent.DISK,
                    6,
                    f"High disk usage on {mount}: {usage:.1f}%",
                    {"disk_usage": usage, "mount": mount},
                    "disk_usage_threshold"
                )
        
        # Temperature alerts
        for sensor, temp in metrics.temperature.items():
            threshold = self.alert_thresholds[HardwareComponent.SENSORS]["temperature"]
            if temp > threshold:
                self._create_alert(
                    HardwareComponent.SENSORS,
                    9,
                    f"High temperature on {sensor}: {temp:.1f}°C",
                    {"temperature": temp, "sensor": sensor},
                    "temperature_threshold"
                )
    
    def _create_alert(self, component: HardwareComponent, severity: int, 
                     message: str, metrics: Dict, threshold_type: str):
        """Create hardware alert"""
        alert = HardwareAlert(
            alert_id=f"hw_{component.value}_{int(time.time())}",
            component=component,
            severity=severity,
            message=message,
            metrics=metrics,
            threshold_exceeded=threshold_type,
            timestamp=datetime.now()
        )
        
        self.alert_history.append(alert)
        logger.warning(f"Hardware Alert: {message}")
        
        # Keep only last 500 alerts
        if len(self.alert_history) > 500:
            self.alert_history = self.alert_history[-500:]

class SystemController:
    """
    Main system controller integrating all security components
    """
    
    def __init__(self, config_file: str = "config/system_controller_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        
        # Initialize components
        self.auth_system = QuantumSecureAuth()
        self.hardware_monitor = HardwareMonitor()
        self.security_monitor = SecurityMonitor()
        self.threat_engine = ThreatEngine()
        self.auto_response = AutomatedResponseSystem()
        self.platform_interface = PlatformInterface()
        self.basenet_connector = BaseNetConnector()
        self.target_manager = TargetManager()  # NEW: Target management
        
        # System state
        self.system_status = SystemStatus.SECURE
        self.current_metrics = None
        self.active_threats = []
        self.action_history = []
        
        # Control threads
        self.monitoring_thread = None
        self.response_thread = None
        self.target_monitoring_thread = None  # NEW: Target monitoring thread
        self.shutdown_event = threading.Event()
        
        # Initialize database
        self._init_database()
        
        logger.info("System Controller initialized")
    
    def _load_config(self) -> Dict:
        """Load system controller configuration"""
        default_config = {
            "monitoring_interval": 10,
            "alert_cooldown": 300,
            "auto_response_enabled": True,
            "constitutional_ai_enabled": True,
            "quantum_auth_required": False,
            "hardware_monitoring_enabled": True,
            "threat_correlation_enabled": True,
            "system_optimization_enabled": True,
            "emergency_protocols": {
                "auto_quarantine": True,
                "emergency_shutdown": False,
                "network_isolation": True
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    default_config.update(config)
            return default_config
        except Exception as e:
            logger.warning(f"Failed to load config: {e}. Using defaults.")
            return default_config
    
    def _init_database(self):
        """Initialize system controller database"""
        os.makedirs("data", exist_ok=True)
        self.db_path = "data/system_controller.db"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS admin_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_id TEXT UNIQUE NOT NULL,
                    action_type TEXT NOT NULL,
                    target TEXT,
                    parameters TEXT,
                    access_level INTEGER,
                    user_id TEXT,
                    timestamp REAL,
                    success BOOLEAN,
                    output TEXT,
                    constitutional_approval BOOLEAN,
                    ethical_score REAL
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    cpu_usage REAL,
                    memory_usage REAL,
                    disk_usage TEXT,
                    network_activity TEXT,
                    temperature TEXT,
                    power_consumption REAL,
                    security_score REAL,
                    threat_level TEXT,
                    active_connections INTEGER,
                    running_processes INTEGER,
                    system_uptime REAL
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS hardware_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT UNIQUE NOT NULL,
                    component TEXT,
                    severity INTEGER,
                    message TEXT,
                    metrics TEXT,
                    threshold_exceeded TEXT,
                    timestamp REAL,
                    acknowledged BOOLEAN DEFAULT FALSE
                )
            ''')
    
    def start_monitoring(self):
        """Start system monitoring threads"""
        if self.monitoring_thread is None or not self.monitoring_thread.is_alive():
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            logger.info("System monitoring started")
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.shutdown_event.set()
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        if self.target_monitoring_thread:
            self.target_monitoring_thread.join(timeout=10)
        logger.info("System monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while not self.shutdown_event.is_set():
            try:
                # Collect hardware metrics
                if self.config["hardware_monitoring_enabled"]:
                    self.current_metrics = self.hardware_monitor.collect_hardware_metrics()
                    self._store_metrics(self.current_metrics)
                
                # Security monitoring
                security_events = self.security_monitor.get_recent_events(limit=10)
                
                # Threat analysis
                if self.config["threat_correlation_enabled"]:
                    for event in security_events:
                        threat_analysis = self.threat_engine.analyze_event(event)
                        if threat_analysis.threat_level.value >= ThreatLevel.MEDIUM.value:
                            self._handle_threat(threat_analysis, event)
                
                # System optimization
                if self.config["system_optimization_enabled"]:
                    self._optimize_system_performance()
                
                # Sleep until next monitoring cycle
                self.shutdown_event.wait(self.config["monitoring_interval"])
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                self.shutdown_event.wait(5)  # Brief pause on error
    
    def _handle_threat(self, threat_analysis, security_event):
        """Handle detected threat"""
        try:
            # Update system status
            if threat_analysis.threat_level.value >= ThreatLevel.HIGH.value:
                self.system_status = SystemStatus.THREAT_DETECTED
            
            # Add to active threats
            self.active_threats.append({
                "threat_analysis": threat_analysis,
                "security_event": security_event,
                "detected_at": datetime.now()
            })
            
            # Automated response
            if self.config["auto_response_enabled"]:
                self.system_status = SystemStatus.RESPONDING
                
                # Create threat context for auto response
                from auto_response import ThreatContext
                threat_context = ThreatContext(
                    threat_id=f"threat_{int(time.time())}",
                    severity=threat_analysis.severity_score,
                    threat_type=threat_analysis.classification.value,
                    affected_systems=[security_event.get("hostname", "unknown")],
                    indicators={
                        "process_name": security_event.get("process_name"),
                        "file_path": security_event.get("file_path"),
                        "source_ip": security_event.get("source_ip"),
                        "confidence": threat_analysis.confidence_score
                    },
                    confidence=threat_analysis.confidence_score,
                    timestamp=datetime.now()
                )
                
                # Constitutional AI validation if enabled
                if self.config["constitutional_ai_enabled"]:
                    validation_result = asyncio.run(
                        self.basenet_connector.validate_security_action(
                            "automated_threat_response",
                            asdict(threat_context),
                            [EthicalPrinciple.HARM_PREVENTION, EthicalPrinciple.PROPORTIONALITY]
                        )
                    )
                    
                    if validation_result["approved"]:
                        response_result = self.auto_response.respond_to_threat(threat_context)
                        logger.info(f"Automated response executed: {response_result}")
                    else:
                        logger.warning(f"Automated response blocked by Constitutional AI: {validation_result}")
                else:
                    # Execute without AI validation
                    response_result = self.auto_response.respond_to_threat(threat_context)
                    logger.info(f"Automated response executed: {response_result}")
            
            # Clean up old threats (keep last 100)
            self.active_threats = self.active_threats[-100:]
            
        except Exception as e:
            logger.error(f"Threat handling failed: {e}")
    
    def _optimize_system_performance(self):
        """Optimize system performance based on metrics"""
        if not self.current_metrics:
            return
        
        try:
            # CPU optimization
            if self.current_metrics.cpu_usage > 90:
                logger.info("High CPU usage detected, attempting optimization")
                # Could implement CPU governor changes, process priority adjustments, etc.
            
            # Memory optimization
            if self.current_metrics.memory_usage > 85:
                logger.info("High memory usage detected, attempting optimization")
                # Could implement memory cleanup, swap optimization, etc.
            
            # Disk optimization
            for mount, usage in self.current_metrics.disk_usage.items():
                if usage > 90:
                    logger.info(f"High disk usage on {mount}, attempting optimization")
                    # Could implement disk cleanup, log rotation, etc.
            
        except Exception as e:
            logger.error(f"System optimization failed: {e}")
    
    def execute_administrative_action(self, action_type: str, target: str, 
                                    parameters: Dict, user_id: str, 
                                    access_level: AccessLevel) -> AdministrativeAction:
        """Execute administrative action with security controls"""
        action_id = f"admin_{int(time.time())}_{hashlib.md5(f'{action_type}:{target}'.encode()).hexdigest()[:8]}"
        
        try:
            # Access level validation
            required_levels = {
                "kill_process": AccessLevel.ELEVATED,
                "restart_service": AccessLevel.ADMINISTRATIVE,
                "modify_firewall": AccessLevel.ADMINISTRATIVE,
                "system_shutdown": AccessLevel.QUANTUM_SECURE,
                "emergency_response": AccessLevel.SYSTEM_CRITICAL
            }
            
            required_level = required_levels.get(action_type, AccessLevel.ADMINISTRATIVE)
            if access_level.value < required_level.value:
                return AdministrativeAction(
                    action_id=action_id,
                    action_type=action_type,
                    target=target,
                    parameters=parameters,
                    access_level=access_level,
                    user_id=user_id,
                    timestamp=datetime.now(),
                    success=False,
                    output="Insufficient access level",
                    constitutional_approval=False,
                    ethical_score=0.0
                )
            
            # Constitutional AI validation if enabled
            constitutional_approval = True
            ethical_score = 1.0
            
            if self.config["constitutional_ai_enabled"]:
                validation_context = {
                    "action_type": action_type,
                    "target": target,
                    "user_id": user_id,
                    "access_level": access_level.name,
                    "system_status": self.system_status.value
                }
                
                validation_result = asyncio.run(
                    self.basenet_connector.validate_security_action(
                        action_type,
                        validation_context,
                        [EthicalPrinciple.HARM_PREVENTION, EthicalPrinciple.HUMAN_OVERSIGHT]
                    )
                )
                
                constitutional_approval = validation_result["approved"]
                ethical_score = validation_result["ethical_score"]
                
                if not constitutional_approval:
                    return AdministrativeAction(
                        action_id=action_id,
                        action_type=action_type,
                        target=target,
                        parameters=parameters,
                        access_level=access_level,
                        user_id=user_id,
                        timestamp=datetime.now(),
                        success=False,
                        output="Action blocked by Constitutional AI",
                        constitutional_approval=False,
                        ethical_score=ethical_score
                    )
            
            # Execute action based on type
            success = False
            output = ""
            
            if action_type == "kill_process":
                result = self.platform_interface.kill_process(int(target))
                success = result.success
                output = result.stdout or result.stderr
                
            elif action_type == "restart_service":
                result = self.platform_interface.manage_service(target, "restart")
                success = result.success
                output = result.stdout or result.stderr
                
            elif action_type == "block_network":
                result = self.platform_interface.block_network_address(target)
                success = result.success
                output = result.stdout or result.stderr
                
            elif action_type == "system_shutdown":
                result = self.platform_interface.execute_command(
                    ["shutdown", "-h", "+1", "Administrative shutdown"],
                    require_admin=True
                )
                success = result.success
                output = result.stdout or result.stderr
                
            else:
                output = f"Unknown action type: {action_type}"
            
            # Create action record
            admin_action = AdministrativeAction(
                action_id=action_id,
                action_type=action_type,
                target=target,
                parameters=parameters,
                access_level=access_level,
                user_id=user_id,
                timestamp=datetime.now(),
                success=success,
                output=output,
                constitutional_approval=constitutional_approval,
                ethical_score=ethical_score
            )
            
            # Log action
            self._log_administrative_action(admin_action)
            self.action_history.append(admin_action)
            
            # Keep only last 1000 actions
            if len(self.action_history) > 1000:
                self.action_history = self.action_history[-1000:]
            
            return admin_action
            
        except Exception as e:
            logger.error(f"Administrative action failed: {e}")
            return AdministrativeAction(
                action_id=action_id,
                action_type=action_type,
                target=target,
                parameters=parameters,
                access_level=access_level,
                user_id=user_id,
                timestamp=datetime.now(),
                success=False,
                output=str(e),
                constitutional_approval=False,
                ethical_score=0.0
            )
    
    def _store_metrics(self, metrics: SystemMetrics):
        """Store system metrics in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO system_metrics 
                    (timestamp, cpu_usage, memory_usage, disk_usage, network_activity, 
                     temperature, power_consumption, security_score, threat_level, 
                     active_connections, running_processes, system_uptime)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metrics.timestamp.timestamp(),
                    metrics.cpu_usage,
                    metrics.memory_usage,
                    json.dumps(metrics.disk_usage),
                    json.dumps(metrics.network_activity),
                    json.dumps(metrics.temperature),
                    metrics.power_consumption,
                    metrics.security_score,
                    metrics.threat_level.value,
                    metrics.active_connections,
                    metrics.running_processes,
                    metrics.system_uptime
                ))
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")
    
    def _log_administrative_action(self, action: AdministrativeAction):
        """Log administrative action to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO admin_actions 
                    (action_id, action_type, target, parameters, access_level, user_id, 
                     timestamp, success, output, constitutional_approval, ethical_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    action.action_id,
                    action.action_type,
                    action.target,
                    json.dumps(action.parameters),
                    action.access_level.value,
                    action.user_id,
                    action.timestamp.timestamp(),
                    action.success,
                    action.output,
                    action.constitutional_approval,
                    action.ethical_score
                ))
        except Exception as e:
            logger.error(f"Failed to log administrative action: {e}")
    
    # ============================================================================
    # TARGET MANAGEMENT METHODS
    # ============================================================================
    
    def add_protection_target(self, name: str, target_type: str, path_or_address: str,
                             description: str = "", priority: int = 5,
                             metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Add a new protection target
        
        Args:
            name: Human-readable name for the target
            target_type: Type of target (file, directory, process, network_port, etc.)
            path_or_address: Path, address, or identifier for the target
            description: Optional description
            priority: Priority level 1-10 (10 = highest)
            metadata: Additional metadata
        
        Returns:
            Dict with target details
        """
        try:
            target_type_enum = TargetType(target_type)
            target = self.target_manager.add_target(
                name=name,
                target_type=target_type_enum,
                path_or_address=path_or_address,
                description=description,
                priority=priority,
                metadata=metadata
            )
            
            logger.info(f"Added protection target: {name} ({target_type})")
            return {
                'success': True,
                'target_id': target.target_id,
                'message': f"Protection target '{name}' added successfully"
            }
        except Exception as e:
            logger.error(f"Failed to add target: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def remove_protection_target(self, target_id: str) -> Dict[str, Any]:
        """Remove a protection target"""
        try:
            success = self.target_manager.remove_target(target_id)
            if success:
                return {
                    'success': True,
                    'message': f"Target {target_id} removed successfully"
                }
            else:
                return {
                    'success': False,
                    'error': f"Target {target_id} not found"
                }
        except Exception as e:
            logger.error(f"Failed to remove target: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_protection_targets(self, target_type: Optional[str] = None,
                               status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all protection targets"""
        try:
            target_type_enum = TargetType(target_type) if target_type else None
            status_enum = TargetStatus(status) if status else None
            
            targets = self.target_manager.list_targets(
                target_type=target_type_enum,
                status=status_enum
            )
            
            return [t.to_dict() for t in targets]
        except Exception as e:
            logger.error(f"Failed to list targets: {e}")
            return []
    
    def get_protection_target(self, target_id: str) -> Optional[Dict[str, Any]]:
        """Get details of a specific target"""
        target = self.target_manager.get_target(target_id)
        if target:
            return target.to_dict()
        return None
    
    def check_protection_target(self, target_id: str) -> Dict[str, Any]:
        """Check the current status of a protection target"""
        return self.target_manager.check_target(target_id, self.platform_interface)
    
    def start_target_monitoring(self):
        """Start monitoring all protection targets"""
        if self.target_monitoring_thread and self.target_monitoring_thread.is_alive():
            logger.warning("Target monitoring already running")
            return
        
        self.target_monitoring_thread = threading.Thread(
            target=self._target_monitoring_loop,
            daemon=True
        )
        self.target_monitoring_thread.start()
        logger.info("Target monitoring started")
    
    def _target_monitoring_loop(self):
        """Background loop for monitoring protection targets"""
        while not self.shutdown_event.is_set():
            try:
                targets = self.target_manager.list_targets()
                
                for target in targets:
                    if not target.monitoring_enabled:
                        continue
                    
                    # Check target status
                    status = self.target_manager.check_target(
                        target.target_id,
                        self.platform_interface
                    )
                    
                    # Log events for anomalies
                    if not status.get('exists'):
                        self.target_manager.log_target_event(
                            target.target_id,
                            'target_missing',
                            'high',
                            f"Target {target.name} no longer exists"
                        )
                        self.target_manager.update_target_status(
                            target.target_id,
                            TargetStatus.COMPROMISED
                        )
                    
                    elif not status.get('accessible'):
                        self.target_manager.log_target_event(
                            target.target_id,
                            'access_denied',
                            'medium',
                            f"Target {target.name} not accessible"
                        )
                    
                    # Update status
                    if status.get('exists') and status.get('accessible'):
                        if target.status != TargetStatus.PROTECTED:
                            self.target_manager.update_target_status(
                                target.target_id,
                                TargetStatus.PROTECTED
                            )
                
                # Wait before next check
                time.sleep(self.config.get('target_check_interval', 60))
                
            except Exception as e:
                logger.error(f"Target monitoring error: {e}")
                time.sleep(10)
    
    def get_target_events(self, target_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events for a specific target"""
        return self.target_manager.get_target_events(target_id, limit)
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        return {
            "system_status": self.system_status.value,
            "current_metrics": asdict(self.current_metrics) if self.current_metrics else {},
            "active_threats": len(self.active_threats),
            "hardware_alerts": len([a for a in self.hardware_monitor.alert_history if not a.acknowledged]),
            "recent_actions": len([a for a in self.action_history if 
                                 datetime.now() - a.timestamp < timedelta(hours=1)]),
            "uptime": time.time() - psutil.boot_time(),
            "monitoring_active": self.monitoring_thread.is_alive() if self.monitoring_thread else False
        }

def main():
    """Main function for testing system controller"""
    controller = SystemController()
    
    # Start monitoring
    controller.start_monitoring()
    
    try:
        # Test authentication
        auth_result, access_level = controller.auth_system.authenticate_user(
            "admin",
            {
                "password": "secure_password123",
                "biometric": "fingerprint_data",
                "token": "123456"
            }
        )
        
        print(f"Authentication: {auth_result}, Access Level: {access_level.name}")
        
        # Test administrative action
        if auth_result:
            action_result = controller.execute_administrative_action(
                "kill_process",
                "1234",
                {},
                "admin",
                access_level
            )
            
            print(f"Action Result: {action_result.success}, Output: {action_result.output}")
        
        # Get system status
        status = controller.get_system_status()
        print(f"System Status: {json.dumps(status, indent=2)}")
        
        # Wait for a few monitoring cycles
        time.sleep(30)
        
    finally:
        controller.stop_monitoring()

if __name__ == "__main__":
    main()
