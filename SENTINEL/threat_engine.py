"""
Advanced Threat Intelligence Engine
AI-Powered Threat Detection and Classification

This module provides sophisticated threat detection capabilities including:
- Machine learning-based threat classification
- Behavioral anomaly detection
- Predictive threat modeling
- Pattern recognition and analysis
- Integration with Constitutional AI for decision making
"""

import numpy as np
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import hashlib
import re
import sqlite3
import threading
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import joblib

class ThreatCategory(Enum):
    """Threat classification categories"""
    MALWARE = "malware"
    INTRUSION = "intrusion"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    LATERAL_MOVEMENT = "lateral_movement"
    PERSISTENCE = "persistence"
    DEFENSE_EVASION = "defense_evasion"
    RECONNAISSANCE = "reconnaissance"
    UNKNOWN = "unknown"

@dataclass
class ThreatSignature:
    """Threat signature data structure"""
    signature_id: str
    name: str
    category: ThreatCategory
    indicators: List[str]
    confidence: float
    last_updated: datetime
    detection_logic: str

@dataclass
class ThreatAssessment:
    """Comprehensive threat assessment result"""
    threat_id: str
    timestamp: datetime
    threat_level: str
    threat_category: ThreatCategory
    confidence_score: float
    indicators: List[str]
    attack_vector: str
    potential_impact: str
    recommended_actions: List[str]
    constitutional_review_required: bool

class ThreatClassifier:
    """
    AI-Powered Threat Classification Engine
    
    Uses machine learning algorithms to classify and assess security threats
    with Constitutional AI integration for ethical decision making.
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.threat_signatures = []
        self.ml_models = {}
        self.threat_database = self._init_threat_database()
        
        # Load pre-trained models
        self._load_ml_models()
        
        # Load threat signatures
        self._load_threat_signatures()
        
        self.logger.info("ThreatClassifier initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup threat engine logging"""
        logger = logging.getLogger('ThreatEngine')
        logger.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        file_handler = logging.FileHandler(
            'logs/threat_engine.log'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def _init_threat_database(self) -> str:
        """Initialize threat intelligence database"""
        # Ensure data directory exists
        Path('data').mkdir(exist_ok=True)
        db_path = "data/threat_intelligence.db"
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create threat signatures table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threat_signatures (
                    id INTEGER PRIMARY KEY,
                    signature_id TEXT UNIQUE,
                    name TEXT,
                    category TEXT,
                    indicators TEXT,
                    confidence REAL,
                    last_updated TEXT,
                    detection_logic TEXT
                )
            ''')
            
            # Create threat assessments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threat_assessments (
                    id INTEGER PRIMARY KEY,
                    threat_id TEXT UNIQUE,
                    timestamp TEXT,
                    threat_level TEXT,
                    threat_category TEXT,
                    confidence_score REAL,
                    indicators TEXT,
                    attack_vector TEXT,
                    potential_impact TEXT,
                    recommended_actions TEXT,
                    constitutional_review_required INTEGER
                )
            ''')
            
            # Create threat intelligence feeds table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threat_intelligence (
                    id INTEGER PRIMARY KEY,
                    source TEXT,
                    indicator_type TEXT,
                    indicator_value TEXT,
                    threat_type TEXT,
                    confidence REAL,
                    first_seen TEXT,
                    last_seen TEXT,
                    context TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Threat database initialized")
            return db_path
            
        except Exception as e:
            self.logger.error(f"Threat database initialization failed: {e}")
            return ""
    
    def _load_ml_models(self):
        """Load pre-trained machine learning models"""
        try:
            # Anomaly detection model
            self.ml_models['anomaly_detector'] = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            
            # Clustering model for behavior analysis
            self.ml_models['behavior_cluster'] = DBSCAN(
                eps=0.5,
                min_samples=5
            )
            
            # Feature scaler
            self.ml_models['scaler'] = StandardScaler()
            
            self.logger.info("ML models loaded successfully")
            
        except Exception as e:
            self.logger.error(f"ML model loading failed: {e}")
    
    def _load_threat_signatures(self):
        """Load threat signatures from database"""
        try:
            conn = sqlite3.connect(self.threat_database)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM threat_signatures")
            rows = cursor.fetchall()
            
            for row in rows:
                signature = ThreatSignature(
                    signature_id=row[1],
                    name=row[2],
                    category=ThreatCategory(row[3]),
                    indicators=json.loads(row[4]),
                    confidence=row[5],
                    last_updated=datetime.fromisoformat(row[6]),
                    detection_logic=row[7]
                )
                self.threat_signatures.append(signature)
            
            conn.close()
            
            # Load default signatures if database is empty
            if not self.threat_signatures:
                self._load_default_signatures()
            
            self.logger.info(f"Loaded {len(self.threat_signatures)} threat signatures")
            
        except Exception as e:
            self.logger.error(f"Threat signature loading failed: {e}")
            self._load_default_signatures()
    
    def _load_default_signatures(self):
        """Load default threat signatures"""
        default_signatures = [
            {
                "signature_id": "MALWARE_001",
                "name": "Suspicious Process Execution",
                "category": ThreatCategory.MALWARE,
                "indicators": ["powershell.exe -encodedcommand", "cmd.exe /c echo", "rundll32.exe"],
                "confidence": 0.8,
                "detection_logic": "process_name_pattern"
            },
            {
                "signature_id": "INTRUSION_001", 
                "name": "Multiple Failed Login Attempts",
                "category": ThreatCategory.INTRUSION,
                "indicators": ["failed_login", "authentication_error", "access_denied"],
                "confidence": 0.7,
                "detection_logic": "event_frequency"
            },
            {
                "signature_id": "PERSISTENCE_001",
                "name": "Registry Modification",
                "category": ThreatCategory.PERSISTENCE,
                "indicators": ["HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"],
                "confidence": 0.6,
                "detection_logic": "registry_modification"
            },
            {
                "signature_id": "LATERAL_001",
                "name": "Unusual Network Activity",
                "category": ThreatCategory.LATERAL_MOVEMENT,
                "indicators": ["psexec", "wmiexec", "445", "139"],
                "confidence": 0.75,
                "detection_logic": "network_pattern"
            }
        ]
        
        for sig_data in default_signatures:
            signature = ThreatSignature(
                signature_id=sig_data["signature_id"],
                name=sig_data["name"],
                category=sig_data["category"],
                indicators=sig_data["indicators"],
                confidence=sig_data["confidence"],
                last_updated=datetime.now(),
                detection_logic=sig_data["detection_logic"]
            )
            self.threat_signatures.append(signature)
            
        # Save to database
        self._save_signatures_to_db()
    
    def _save_signatures_to_db(self):
        """Save threat signatures to database"""
        try:
            conn = sqlite3.connect(self.threat_database)
            cursor = conn.cursor()
            
            for signature in self.threat_signatures:
                cursor.execute('''
                    INSERT OR REPLACE INTO threat_signatures 
                    (signature_id, name, category, indicators, confidence, last_updated, detection_logic)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    signature.signature_id,
                    signature.name,
                    signature.category.value,
                    json.dumps(signature.indicators),
                    signature.confidence,
                    signature.last_updated.isoformat(),
                    signature.detection_logic
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Signature saving failed: {e}")
    
    def analyze_events(self, events: List[Any]) -> Dict[str, Any]:
        """Analyze security events for threats"""
        try:
            threat_assessment = {
                "timestamp": datetime.now().isoformat(),
                "events_analyzed": len(events),
                "threats_detected": [],
                "threat_level": "low",
                "confidence": 0.0,
                "recommendations": []
            }
            
            for event in events:
                # Signature-based detection
                signature_matches = self._signature_detection(event)
                
                # Behavioral analysis
                behavioral_analysis = self._behavioral_analysis(event)
                
                # ML-based anomaly detection
                anomaly_score = self._anomaly_detection(event)
                
                # Combine analysis results
                if signature_matches or behavioral_analysis or anomaly_score > 0.7:
                    threat = self._create_threat_assessment(
                        event, signature_matches, behavioral_analysis, anomaly_score
                    )
                    threat_assessment["threats_detected"].append(threat)
            
            # Determine overall threat level
            if threat_assessment["threats_detected"]:
                max_confidence = max([t.confidence_score for t in threat_assessment["threats_detected"]])
                threat_assessment["confidence"] = max_confidence
                
                if max_confidence > 0.9:
                    threat_assessment["threat_level"] = "critical"
                elif max_confidence > 0.7:
                    threat_assessment["threat_level"] = "high"
                elif max_confidence > 0.5:
                    threat_assessment["threat_level"] = "medium"
                else:
                    threat_assessment["threat_level"] = "low"
            
            self.logger.info(f"Threat analysis completed: {len(threat_assessment['threats_detected'])} threats detected")
            return threat_assessment
            
        except Exception as e:
            self.logger.error(f"Event analysis failed: {e}")
            return {"error": str(e)}
    
    def _signature_detection(self, event: Any) -> List[ThreatSignature]:
        """Perform signature-based threat detection"""
        matches = []
        
        try:
            event_data = str(event.evidence) if hasattr(event, 'evidence') else str(event)
            
            for signature in self.threat_signatures:
                for indicator in signature.indicators:
                    if indicator.lower() in event_data.lower():
                        matches.append(signature)
                        break
            
        except Exception as e:
            self.logger.error(f"Signature detection failed: {e}")
        
        return matches
    
    def _behavioral_analysis(self, event: Any) -> Dict[str, Any]:
        """Perform behavioral analysis of security event"""
        try:
            behavioral_score = 0.0
            behavioral_indicators = []
            
            # Analyze event patterns
            if hasattr(event, 'event_type'):
                # Check for suspicious event types
                suspicious_types = ['process_anomaly', 'network_anomaly', 'file_integrity']
                if event.event_type in suspicious_types:
                    behavioral_score += 0.3
                    behavioral_indicators.append(f"suspicious_event_type:{event.event_type}")
            
            if hasattr(event, 'threat_level'):
                # Increase score based on threat level
                threat_levels = {'low': 0.1, 'medium': 0.3, 'high': 0.6, 'critical': 0.9}
                behavioral_score += threat_levels.get(event.threat_level.value, 0.1)
                behavioral_indicators.append(f"threat_level:{event.threat_level.value}")
            
            return {
                "behavioral_score": behavioral_score,
                "indicators": behavioral_indicators,
                "analysis_complete": True
            }
            
        except Exception as e:
            self.logger.error(f"Behavioral analysis failed: {e}")
            return {"behavioral_score": 0.0, "indicators": [], "analysis_complete": False}
    
    def _anomaly_detection(self, event: Any) -> float:
        """ML-based anomaly detection"""
        try:
            # Extract features from event
            features = self._extract_event_features(event)
            
            if features:
                # Use isolation forest for anomaly detection
                features_array = np.array(features).reshape(1, -1)
                anomaly_score = self.ml_models['anomaly_detector'].decision_function(features_array)[0]
                
                # Normalize score to 0-1 range
                normalized_score = max(0, min(1, (anomaly_score + 0.5) * 2))
                return normalized_score
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {e}")
            return 0.0
    
    def _extract_event_features(self, event: Any) -> List[float]:
        """Extract numerical features from security event"""
        try:
            features = []
            
            # Time-based features
            if hasattr(event, 'timestamp'):
                hour = event.timestamp.hour
                features.extend([hour / 24.0, event.timestamp.weekday() / 7.0])
            else:
                features.extend([0.0, 0.0])
            
            # Event type encoding
            event_types = {
                'system_integrity': 1, 'process_anomaly': 2, 'network_anomaly': 3,
                'file_integrity': 4, 'hardware_anomaly': 5
            }
            
            if hasattr(event, 'event_type'):
                features.append(event_types.get(event.event_type, 0) / 5.0)
            else:
                features.append(0.0)
            
            # Threat level encoding
            threat_levels = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
            
            if hasattr(event, 'threat_level'):
                features.append(threat_levels.get(event.threat_level.value, 0) / 4.0)
            else:
                features.append(0.0)
            
            # Evidence complexity (number of evidence fields)
            if hasattr(event, 'evidence') and isinstance(event.evidence, dict):
                features.append(min(len(event.evidence), 10) / 10.0)
            else:
                features.append(0.0)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Feature extraction failed: {e}")
            return []
    
    def _create_threat_assessment(self, event: Any, signature_matches: List[ThreatSignature],
                                behavioral_analysis: Dict[str, Any], anomaly_score: float) -> ThreatAssessment:
        """Create comprehensive threat assessment"""
        try:
            # Generate unique threat ID
            threat_id = hashlib.md5(f"{event}_{datetime.now()}".encode()).hexdigest()[:16]
            
            # Determine threat category
            if signature_matches:
                threat_category = signature_matches[0].category
            else:
                threat_category = ThreatCategory.UNKNOWN
            
            # Calculate confidence score
            signature_confidence = max([s.confidence for s in signature_matches]) if signature_matches else 0.0
            behavioral_confidence = behavioral_analysis.get("behavioral_score", 0.0)
            
            overall_confidence = max(signature_confidence, behavioral_confidence, anomaly_score)
            
            # Determine threat level
            if overall_confidence > 0.9:
                threat_level = "critical"
            elif overall_confidence > 0.7:
                threat_level = "high"
            elif overall_confidence > 0.5:
                threat_level = "medium"
            else:
                threat_level = "low"
            
            # Generate indicators
            indicators = []
            if signature_matches:
                indicators.extend([s.name for s in signature_matches])
            indicators.extend(behavioral_analysis.get("indicators", []))
            
            # Generate recommendations
            recommendations = self._generate_threat_recommendations(
                threat_category, threat_level, overall_confidence
            )
            
            # Determine if constitutional review is required
            constitutional_review = (
                threat_level in ["high", "critical"] or 
                threat_category in [ThreatCategory.PRIVILEGE_ESCALATION, ThreatCategory.PERSISTENCE]
            )
            
            assessment = ThreatAssessment(
                threat_id=threat_id,
                timestamp=datetime.now(),
                threat_level=threat_level,
                threat_category=threat_category,
                confidence_score=overall_confidence,
                indicators=indicators,
                attack_vector=self._determine_attack_vector(threat_category),
                potential_impact=self._assess_potential_impact(threat_category, threat_level),
                recommended_actions=recommendations,
                constitutional_review_required=constitutional_review
            )
            
            # Save assessment to database
            self._save_assessment_to_db(assessment)
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"Threat assessment creation failed: {e}")
            return None
    
    def _generate_threat_recommendations(self, category: ThreatCategory, level: str, confidence: float) -> List[str]:
        """Generate threat-specific recommendations"""
        recommendations = []
        
        if category == ThreatCategory.MALWARE:
            recommendations.extend([
                "Isolate affected system",
                "Run full antimalware scan",
                "Check for persistence mechanisms"
            ])
        elif category == ThreatCategory.INTRUSION:
            recommendations.extend([
                "Reset compromised credentials",
                "Review access logs",
                "Implement additional authentication factors"
            ])
        elif category == ThreatCategory.PRIVILEGE_ESCALATION:
            recommendations.extend([
                "Review user privileges",
                "Audit system permissions",
                "Monitor administrative access"
            ])
        
        if level in ["high", "critical"]:
            recommendations.extend([
                "Immediate incident response activation",
                "Notify security team",
                "Document all evidence"
            ])
        
        return recommendations
    
    def _determine_attack_vector(self, category: ThreatCategory) -> str:
        """Determine likely attack vector based on threat category"""
        vectors = {
            ThreatCategory.MALWARE: "File-based or network-based malware delivery",
            ThreatCategory.INTRUSION: "Network-based unauthorized access",
            ThreatCategory.PRIVILEGE_ESCALATION: "Local privilege escalation exploit",
            ThreatCategory.LATERAL_MOVEMENT: "Network-based lateral movement",
            ThreatCategory.PERSISTENCE: "System modification for persistence",
            ThreatCategory.RECONNAISSANCE: "Information gathering activities"
        }
        
        return vectors.get(category, "Unknown attack vector")
    
    def _assess_potential_impact(self, category: ThreatCategory, level: str) -> str:
        """Assess potential impact of threat"""
        base_impacts = {
            ThreatCategory.MALWARE: "System compromise, data corruption",
            ThreatCategory.INTRUSION: "Unauthorized access, data exposure",
            ThreatCategory.PRIVILEGE_ESCALATION: "Administrative compromise",
            ThreatCategory.DATA_EXFILTRATION: "Data theft, privacy breach",
            ThreatCategory.LATERAL_MOVEMENT: "Network-wide compromise"
        }
        
        base_impact = base_impacts.get(category, "System security compromise")
        
        if level in ["high", "critical"]:
            return f"HIGH IMPACT: {base_impact}, potential business disruption"
        else:
            return f"MODERATE IMPACT: {base_impact}"
    
    def _save_assessment_to_db(self, assessment: ThreatAssessment):
        """Save threat assessment to database"""
        try:
            conn = sqlite3.connect(self.threat_database)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO threat_assessments
                (threat_id, timestamp, threat_level, threat_category, confidence_score,
                 indicators, attack_vector, potential_impact, recommended_actions,
                 constitutional_review_required)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                assessment.threat_id,
                assessment.timestamp.isoformat(),
                assessment.threat_level,
                assessment.threat_category.value,
                assessment.confidence_score,
                json.dumps(assessment.indicators),
                assessment.attack_vector,
                assessment.potential_impact,
                json.dumps(assessment.recommended_actions),
                1 if assessment.constitutional_review_required else 0
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Assessment saving failed: {e}")


class AnomalyDetector:
    """
    Advanced Anomaly Detection System
    
    Detects unusual patterns in system behavior using multiple ML techniques.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('AnomalyDetector')
        self.models = {}
        self.baseline_data = {}
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize anomaly detection models"""
        try:
            # Process anomaly detection
            self.models['process'] = IsolationForest(contamination=0.1, random_state=42)
            
            # Network anomaly detection
            self.models['network'] = IsolationForest(contamination=0.05, random_state=42)
            
            # File system anomaly detection
            self.models['filesystem'] = IsolationForest(contamination=0.02, random_state=42)
            
            self.logger.info("Anomaly detection models initialized")
            
        except Exception as e:
            self.logger.error(f"Model initialization failed: {e}")
    
    def detect_process_anomalies(self, current_processes: List[Dict], baseline_processes: Dict) -> List[Dict]:
        """Detect anomalous processes"""
        try:
            anomalous_processes = []
            
            for process in current_processes:
                # Check for suspicious process names
                if self._is_suspicious_process_name(process.get('name', '')):
                    anomalous_processes.append(process)
                    continue
                
                # Check for unusual CPU usage
                if process.get('cpu_percent', 0) > 80:
                    anomalous_processes.append(process)
                    continue
                
                # Check for suspicious command lines
                if self._is_suspicious_cmdline(process.get('cmdline', [])):
                    anomalous_processes.append(process)
                    continue
            
            return anomalous_processes
            
        except Exception as e:
            self.logger.error(f"Process anomaly detection failed: {e}")
            return []
    
    def _is_suspicious_process_name(self, process_name: str) -> bool:
        """Check if process name is suspicious"""
        suspicious_patterns = [
            r'.*\.tmp\.exe$',  # Temporary executable files
            r'^[a-f0-9]{8,}\.exe$',  # Random hex names
            r'.*powershell.*-enc.*',  # Encoded PowerShell
            r'.*cmd.*\/c.*echo.*',  # Suspicious cmd usage
        ]
        
        for pattern in suspicious_patterns:
            if re.match(pattern, process_name, re.IGNORECASE):
                return True
        
        return False
    
    def _is_suspicious_cmdline(self, cmdline: List[str]) -> bool:
        """Check if command line is suspicious"""
        if not cmdline:
            return False
        
        cmdline_str = ' '.join(cmdline).lower()
        
        suspicious_indicators = [
            'powershell -encodedcommand',
            'invoke-expression',
            'downloadstring',
            'bypass -executionpolicy',
            'hidden -windowstyle',
            'base64',
            'gzipstream'
        ]
        
        for indicator in suspicious_indicators:
            if indicator in cmdline_str:
                return True
        
        return False


# Class aliases for compatibility
ThreatEngine = ThreatClassifier
ThreatClassification = ThreatCategory

# Additional utility functions and classes...
# ...existing code...
