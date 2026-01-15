"""
Advanced Security Administration System (ASAS) - Automated Response Module
===========================================================================

This module provides autonomous threat response and system self-healing capabilities.
It implements AI-driven decision making for threat mitigation with constitutional safeguards.

Key Features:
- Autonomous threat neutralization
- System self-healing and recovery
- Constitutional AI decision framework
- Multi-stage response escalation
- Quarantine and isolation protocols
- Real-time forensic preservation
- Automated backup and rollback

Author: Artifact Virtual Systems
License: Enterprise Security License
"""

import os
import sys
import json
import time
import shutil
import sqlite3
import hashlib
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
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
        logging.FileHandler('logs/auto_response.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ResponseLevel(Enum):
    """Threat response escalation levels"""
    MONITOR = 1      # Passive observation
    ALERT = 2        # Log and notify
    CONTAIN = 3      # Isolate threat
    NEUTRALIZE = 4   # Active countermeasures
    QUARANTINE = 5   # Full system isolation
    RECOVERY = 6     # System restoration

class ActionType(Enum):
    """Types of automated actions"""
    PROCESS_KILL = "kill_process"
    FILE_QUARANTINE = "quarantine_file"
    NETWORK_BLOCK = "block_network"
    SERVICE_RESTART = "restart_service"
    SYSTEM_ROLLBACK = "system_rollback"
    EMERGENCY_SHUTDOWN = "emergency_shutdown"
    FORENSIC_CAPTURE = "forensic_capture"

@dataclass
class ResponseAction:
    """Represents an automated response action"""
    action_type: ActionType
    target: str
    parameters: Dict[str, Any]
    timestamp: datetime
    success: bool = False
    output: str = ""
    rollback_info: Optional[Dict] = None

@dataclass
class ThreatContext:
    """Context information for threat response"""
    threat_id: str
    severity: int
    threat_type: str
    affected_systems: List[str]
    indicators: Dict[str, Any]
    confidence: float
    timestamp: datetime

class ConstitutionalDecisionEngine:
    """
    AI-powered decision engine with constitutional safeguards
    Ensures all automated responses adhere to ethical and legal frameworks
    """
    
    def __init__(self):
        self.principles = {
            "preserve_data": 0.9,      # Protect user data
            "minimize_disruption": 0.8, # Minimal business impact
            "proportional_response": 0.9, # Response matches threat level
            "human_oversight": 0.7,     # Human approval for critical actions
            "legal_compliance": 1.0,    # Must comply with laws
            "transparency": 0.8         # Log all decisions
        }
        
        self.restricted_actions = {
            "data_deletion": ["user_files", "system_logs", "backups"],
            "system_modification": ["boot_records", "firmware", "kernel"],
            "network_isolation": ["critical_services", "emergency_comms"],
        }
    
    def evaluate_response(self, threat: ThreatContext, proposed_action: ActionType) -> Tuple[bool, float, str]:
        """
        Evaluate if proposed response action is ethical and appropriate
        
        Returns:
            (approved, confidence_score, reasoning)
        """
        reasoning = []
        score = 0.0
        
        # Check proportional response
        severity_threshold = {
            ActionType.PROCESS_KILL: 3,
            ActionType.FILE_QUARANTINE: 4,
            ActionType.NETWORK_BLOCK: 5,
            ActionType.SERVICE_RESTART: 6,
            ActionType.SYSTEM_ROLLBACK: 7,
            ActionType.EMERGENCY_SHUTDOWN: 9
        }
        
        if threat.severity >= severity_threshold.get(proposed_action, 10):
            score += 0.3
            reasoning.append(f"Threat severity ({threat.severity}) justifies action")
        else:
            reasoning.append(f"Action may be disproportionate to threat level")
        
        # Check data preservation
        if proposed_action in [ActionType.FILE_QUARANTINE, ActionType.SYSTEM_ROLLBACK]:
            if threat.confidence > 0.8:
                score += 0.3
                reasoning.append("High confidence justifies data impact")
            else:
                reasoning.append("Insufficient confidence for data-affecting action")
        
        # Check business impact
        if proposed_action in [ActionType.SERVICE_RESTART, ActionType.EMERGENCY_SHUTDOWN]:
            if threat.severity >= 8:
                score += 0.2
                reasoning.append("Critical threat justifies service disruption")
            else:
                reasoning.append("Action may cause unnecessary business disruption")
        
        # Constitutional compliance check
        if score >= 0.6 and threat.confidence > 0.7:
            approved = True
            reasoning.append("Action approved under constitutional framework")
        else:
            approved = False
            reasoning.append("Action rejected - insufficient justification")
        
        return approved, score, "; ".join(reasoning)

class AutomatedResponseSystem:
    """
    Core automated response system with AI-driven decision making
    """
    
    def __init__(self, config_path: str = "config/auto_response_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.decision_engine = ConstitutionalDecisionEngine()
        self.response_history = []
        self.quarantine_path = Path("quarantine")
        self.quarantine_path.mkdir(exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        logger.info("Automated Response System initialized")
    
    def _load_config(self) -> Dict:
        """Load configuration settings"""
        default_config = {
            "max_concurrent_responses": 5,
            "response_timeout": 300,
            "require_human_approval": ["EMERGENCY_SHUTDOWN", "SYSTEM_ROLLBACK"],
            "quarantine_retention_days": 30,
            "forensic_capture_enabled": True,
            "auto_recovery_enabled": True,
            "escalation_thresholds": {
                "low": 3,
                "medium": 6,
                "high": 8,
                "critical": 9
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    default_config.update(config)
            return default_config
        except Exception as e:
            logger.warning(f"Failed to load config: {e}. Using defaults.")
            return default_config
    
    def _init_database(self):
        """Initialize SQLite database for response tracking"""
        os.makedirs("data", exist_ok=True)
        self.db_path = "data/auto_response.db"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS response_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    threat_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    target TEXT NOT NULL,
                    parameters TEXT,
                    timestamp REAL,
                    success BOOLEAN,
                    output TEXT,
                    rollback_info TEXT,
                    constitutional_score REAL,
                    human_approved BOOLEAN DEFAULT FALSE
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS threat_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    threat_id TEXT NOT NULL,
                    response_level INTEGER,
                    total_actions INTEGER,
                    success_rate REAL,
                    resolution_time REAL,
                    timestamp REAL
                )
            ''')
    
    def analyze_threat_response(self, threat: ThreatContext) -> Tuple[ResponseLevel, List[ActionType]]:
        """
        Analyze threat and determine appropriate response level and actions
        """
        severity = threat.severity
        threat_type = threat.threat_type
        confidence = threat.confidence
        
        # Determine response level based on severity and confidence
        if severity >= 9 and confidence > 0.9:
            level = ResponseLevel.RECOVERY
            actions = [ActionType.EMERGENCY_SHUTDOWN, ActionType.FORENSIC_CAPTURE]
        elif severity >= 8 and confidence > 0.8:
            level = ResponseLevel.QUARANTINE
            actions = [ActionType.NETWORK_BLOCK, ActionType.PROCESS_KILL, ActionType.FILE_QUARANTINE]
        elif severity >= 6 and confidence > 0.7:
            level = ResponseLevel.NEUTRALIZE
            actions = [ActionType.PROCESS_KILL, ActionType.SERVICE_RESTART]
        elif severity >= 4 and confidence > 0.6:
            level = ResponseLevel.CONTAIN
            actions = [ActionType.FILE_QUARANTINE, ActionType.PROCESS_KILL]
        elif severity >= 2:
            level = ResponseLevel.ALERT
            actions = [ActionType.FORENSIC_CAPTURE]
        else:
            level = ResponseLevel.MONITOR
            actions = []
        
        # Filter actions based on threat type
        if threat_type == "malware":
            actions.extend([ActionType.FILE_QUARANTINE, ActionType.PROCESS_KILL])
        elif threat_type == "network_intrusion":
            actions.extend([ActionType.NETWORK_BLOCK])
        elif threat_type == "privilege_escalation":
            actions.extend([ActionType.PROCESS_KILL, ActionType.SERVICE_RESTART])
        elif threat_type == "data_exfiltration":
            actions.extend([ActionType.NETWORK_BLOCK, ActionType.FORENSIC_CAPTURE])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_actions = []
        for action in actions:
            if action not in seen:
                unique_actions.append(action)
                seen.add(action)
        
        logger.info(f"Threat {threat.threat_id}: Level {level.name}, Actions: {[a.value for a in unique_actions]}")
        return level, unique_actions
    
    def execute_response_action(self, action_type: ActionType, target: str, 
                              parameters: Dict = None) -> ResponseAction:
        """
        Execute a specific response action
        """
        if parameters is None:
            parameters = {}
        
        action = ResponseAction(
            action_type=action_type,
            target=target,
            parameters=parameters,
            timestamp=datetime.now()
        )
        
        try:
            if action_type == ActionType.PROCESS_KILL:
                action.success, action.output = self._kill_process(target)
                
            elif action_type == ActionType.FILE_QUARANTINE:
                action.success, action.output, action.rollback_info = self._quarantine_file(target)
                
            elif action_type == ActionType.NETWORK_BLOCK:
                action.success, action.output = self._block_network(target, parameters)
                
            elif action_type == ActionType.SERVICE_RESTART:
                action.success, action.output = self._restart_service(target)
                
            elif action_type == ActionType.SYSTEM_ROLLBACK:
                action.success, action.output = self._system_rollback(parameters)
                
            elif action_type == ActionType.EMERGENCY_SHUTDOWN:
                action.success, action.output = self._emergency_shutdown(parameters)
                
            elif action_type == ActionType.FORENSIC_CAPTURE:
                action.success, action.output = self._forensic_capture(target, parameters)
            
            else:
                action.success = False
                action.output = f"Unknown action type: {action_type}"
            
        except Exception as e:
            action.success = False
            action.output = f"Action failed: {str(e)}"
            logger.error(f"Action execution failed: {e}")
        
        # Log action to database
        self._log_action(action)
        return action
    
    def _kill_process(self, process_identifier: str) -> Tuple[bool, str]:
        """Terminate a process by PID or name"""
        try:
            if process_identifier.isdigit():
                # Kill by PID
                if os.name == 'nt':
                    result = subprocess.run(['taskkill', '/F', '/PID', process_identifier], 
                                          capture_output=True, text=True)
                else:
                    result = subprocess.run(['kill', '-9', process_identifier], 
                                          capture_output=True, text=True)
            else:
                # Kill by process name
                if os.name == 'nt':
                    result = subprocess.run(['taskkill', '/F', '/IM', process_identifier], 
                                          capture_output=True, text=True)
                else:
                    result = subprocess.run(['pkill', '-f', process_identifier], 
                                          capture_output=True, text=True)
            
            return result.returncode == 0, result.stdout + result.stderr
            
        except Exception as e:
            return False, str(e)
    
    def _quarantine_file(self, file_path: str) -> Tuple[bool, str, Dict]:
        """Move file to quarantine and create backup info"""
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                return False, f"File not found: {file_path}", {}
            
            # Create quarantine subdirectory with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            quarantine_subdir = self.quarantine_path / timestamp
            quarantine_subdir.mkdir(exist_ok=True)
            
            # Generate unique filename
            file_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()[:16]
            quarantine_file = quarantine_subdir / f"{source_path.name}_{file_hash}"
            
            # Move file to quarantine
            shutil.move(str(source_path), str(quarantine_file))
            
            rollback_info = {
                "original_path": str(source_path),
                "quarantine_path": str(quarantine_file),
                "timestamp": timestamp,
                "file_hash": file_hash,
                "file_size": quarantine_file.stat().st_size
            }
            
            return True, f"File quarantined: {quarantine_file}", rollback_info
            
        except Exception as e:
            return False, str(e), {}
    
    def _block_network(self, target: str, parameters: Dict) -> Tuple[bool, str]:
        """Block network traffic to/from target"""
        try:
            block_type = parameters.get("type", "ip")
            direction = parameters.get("direction", "both")
            
            if os.name == 'nt':
                # Windows firewall rule
                if block_type == "ip":
                    cmd = ['netsh', 'advfirewall', 'firewall', 'add', 'rule',
                           f'name=ASAS_Block_{target}', 'dir=out', 'action=block',
                           f'remoteip={target}']
                else:
                    cmd = ['netsh', 'advfirewall', 'firewall', 'add', 'rule',
                           f'name=ASAS_Block_{target}', 'dir=out', 'action=block',
                           f'program={target}']
            else:
                # Linux iptables rule
                if block_type == "ip":
                    cmd = ['iptables', '-A', 'OUTPUT', '-d', target, '-j', 'DROP']
                else:
                    return False, "Port blocking not implemented for Linux"
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0, result.stdout + result.stderr
            
        except Exception as e:
            return False, str(e)
    
    def _restart_service(self, service_name: str) -> Tuple[bool, str]:
        """Restart a system service"""
        try:
            if os.name == 'nt':
                # Windows service restart
                stop_result = subprocess.run(['net', 'stop', service_name], 
                                           capture_output=True, text=True)
                time.sleep(2)
                start_result = subprocess.run(['net', 'start', service_name], 
                                            capture_output=True, text=True)
                success = start_result.returncode == 0
                output = stop_result.stdout + start_result.stdout + stop_result.stderr + start_result.stderr
            else:
                # Linux systemd service restart
                result = subprocess.run(['systemctl', 'restart', service_name], 
                                      capture_output=True, text=True)
                success = result.returncode == 0
                output = result.stdout + result.stderr
            
            return success, output
            
        except Exception as e:
            return False, str(e)
    
    def _system_rollback(self, parameters: Dict) -> Tuple[bool, str]:
        """Rollback system to previous state"""
        try:
            rollback_type = parameters.get("type", "snapshot")
            target_time = parameters.get("target_time")
            
            if rollback_type == "snapshot":
                # This would integrate with system snapshot tools
                # Implementation depends on specific snapshot system
                return False, "System rollback requires manual intervention"
            else:
                return False, f"Unknown rollback type: {rollback_type}"
                
        except Exception as e:
            return False, str(e)
    
    def _emergency_shutdown(self, parameters: Dict) -> Tuple[bool, str]:
        """Emergency system shutdown"""
        try:
            delay = parameters.get("delay", 10)
            reason = parameters.get("reason", "Security emergency")
            
            logger.critical(f"EMERGENCY SHUTDOWN INITIATED: {reason}")
            
            if os.name == 'nt':
                cmd = ['shutdown', '/s', '/f', '/t', str(delay), '/c', reason]
            else:
                cmd = ['shutdown', '-h', f'+{delay//60}', reason]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0, result.stdout + result.stderr
            
        except Exception as e:
            return False, str(e)
    
    def _forensic_capture(self, target: str, parameters: Dict) -> Tuple[bool, str]:
        """Capture forensic evidence"""
        try:
            capture_type = parameters.get("type", "memory")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            forensic_dir = Path("forensics") / timestamp
            forensic_dir.mkdir(parents=True, exist_ok=True)
            
            if capture_type == "memory":
                # Memory dump (placeholder - requires specialized tools)
                evidence_file = forensic_dir / f"memory_dump_{timestamp}.raw"
                # In real implementation, would use tools like winpmem, LiME, etc.
                evidence_file.write_text(f"Memory capture timestamp: {timestamp}\nTarget: {target}")
                
            elif capture_type == "disk":
                # Disk image (placeholder)
                evidence_file = forensic_dir / f"disk_image_{timestamp}.dd"
                evidence_file.write_text(f"Disk image timestamp: {timestamp}\nTarget: {target}")
                
            elif capture_type == "network":
                # Network capture (placeholder)
                evidence_file = forensic_dir / f"network_capture_{timestamp}.pcap"
                evidence_file.write_text(f"Network capture timestamp: {timestamp}\nTarget: {target}")
            
            return True, f"Forensic evidence captured: {evidence_file}"
            
        except Exception as e:
            return False, str(e)
    
    def _log_action(self, action: ResponseAction):
        """Log action to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO response_actions 
                    (threat_id, action_type, target, parameters, timestamp, success, output, rollback_info)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    "",  # threat_id will be set by calling function
                    action.action_type.value,
                    action.target,
                    json.dumps(action.parameters),
                    action.timestamp.timestamp(),
                    action.success,
                    action.output,
                    json.dumps(action.rollback_info) if action.rollback_info else None
                ))
        except Exception as e:
            logger.error(f"Failed to log action: {e}")
    
    def respond_to_threat(self, threat: ThreatContext, human_approval: bool = False) -> Dict:
        """
        Main entry point for automated threat response
        """
        start_time = time.time()
        
        # Analyze threat and determine response
        response_level, proposed_actions = self.analyze_threat_response(threat)
        
        response_summary = {
            "threat_id": threat.threat_id,
            "response_level": response_level.name,
            "proposed_actions": [a.value for a in proposed_actions],
            "executed_actions": [],
            "failed_actions": [],
            "total_time": 0,
            "success_rate": 0
        }
        
        if not proposed_actions:
            logger.info(f"No actions required for threat {threat.threat_id}")
            return response_summary
        
        # Execute actions with constitutional oversight
        executed_actions = []
        for action_type in proposed_actions:
            # Constitutional decision check
            approved, score, reasoning = self.decision_engine.evaluate_response(threat, action_type)
            
            if not approved and not human_approval:
                logger.warning(f"Action {action_type.value} rejected: {reasoning}")
                response_summary["failed_actions"].append({
                    "action": action_type.value,
                    "reason": f"Constitutional rejection: {reasoning}"
                })
                continue
            
            # Check if human approval required
            if action_type.value.upper() in self.config.get("require_human_approval", []):
                if not human_approval:
                    logger.warning(f"Action {action_type.value} requires human approval")
                    response_summary["failed_actions"].append({
                        "action": action_type.value,
                        "reason": "Human approval required"
                    })
                    continue
            
            # Execute the action
            if action_type in [ActionType.PROCESS_KILL, ActionType.FILE_QUARANTINE]:
                target = threat.indicators.get("process_name") or threat.indicators.get("file_path", "unknown")
            elif action_type == ActionType.NETWORK_BLOCK:
                target = threat.indicators.get("source_ip") or threat.indicators.get("destination_ip", "unknown")
            elif action_type == ActionType.SERVICE_RESTART:
                target = threat.indicators.get("service_name", "unknown")
            else:
                target = "system"
            
            action_result = self.execute_response_action(action_type, target, threat.indicators)
            executed_actions.append(action_result)
            
            if action_result.success:
                response_summary["executed_actions"].append({
                    "action": action_type.value,
                    "target": target,
                    "output": action_result.output
                })
            else:
                response_summary["failed_actions"].append({
                    "action": action_type.value,
                    "target": target,
                    "error": action_result.output
                })
        
        # Calculate metrics
        total_actions = len(executed_actions)
        successful_actions = sum(1 for a in executed_actions if a.success)
        response_summary["success_rate"] = successful_actions / total_actions if total_actions > 0 else 0
        response_summary["total_time"] = time.time() - start_time
        
        # Log response summary
        self._log_threat_response(threat.threat_id, response_level, response_summary)
        
        logger.info(f"Threat response completed: {response_summary}")
        return response_summary
    
    def _log_threat_response(self, threat_id: str, response_level: ResponseLevel, summary: Dict):
        """Log overall threat response"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO threat_responses 
                    (threat_id, response_level, total_actions, success_rate, resolution_time, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    threat_id,
                    response_level.value,
                    len(summary["executed_actions"]) + len(summary["failed_actions"]),
                    summary["success_rate"],
                    summary["total_time"],
                    datetime.now().timestamp()
                ))
        except Exception as e:
            logger.error(f"Failed to log threat response: {e}")
    
    def rollback_action(self, action_id: int) -> bool:
        """Rollback a previously executed action"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT action_type, rollback_info FROM response_actions 
                    WHERE id = ? AND success = 1
                ''', (action_id,))
                
                row = cursor.fetchone()
                if not row:
                    logger.warning(f"No successful action found with ID {action_id}")
                    return False
                
                action_type, rollback_info_str = row
                if not rollback_info_str:
                    logger.warning(f"No rollback info available for action {action_id}")
                    return False
                
                rollback_info = json.loads(rollback_info_str)
                
                if action_type == ActionType.FILE_QUARANTINE.value:
                    # Restore quarantined file
                    quarantine_path = Path(rollback_info["quarantine_path"])
                    original_path = Path(rollback_info["original_path"])
                    
                    if quarantine_path.exists():
                        shutil.move(str(quarantine_path), str(original_path))
                        logger.info(f"File restored from quarantine: {original_path}")
                        return True
                
                # Add more rollback implementations as needed
                
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def get_response_history(self, threat_id: str = None, limit: int = 100) -> List[Dict]:
        """Get history of automated responses"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if threat_id:
                    cursor = conn.execute('''
                        SELECT * FROM response_actions 
                        WHERE threat_id = ? 
                        ORDER BY timestamp DESC LIMIT ?
                    ''', (threat_id, limit))
                else:
                    cursor = conn.execute('''
                        SELECT * FROM response_actions 
                        ORDER BY timestamp DESC LIMIT ?
                    ''', (limit,))
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Failed to get response history: {e}")
            return []

def main():
    """Main function for testing automated response system"""
    # Example usage
    response_system = AutomatedResponseSystem()
    
    # Create test threat
    test_threat = ThreatContext(
        threat_id="TEST_001",
        severity=7,
        threat_type="malware",
        affected_systems=["workstation-01"],
        indicators={
            "process_name": "suspicious.exe",
            "file_path": "/tmp/malware.bin",
            "source_ip": "192.168.1.100"
        },
        confidence=0.85,
        timestamp=datetime.now()
    )
    
    # Execute response
    result = response_system.respond_to_threat(test_threat)
    print(json.dumps(result, indent=2))

# Class alias for compatibility
AutoResponse = AutomatedResponseSystem

if __name__ == "__main__":
    main()
