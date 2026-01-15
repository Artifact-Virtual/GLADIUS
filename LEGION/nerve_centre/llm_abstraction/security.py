"""
Security Layer for LLM Abstraction Subsystem
"""
import hashlib
import hmac
import time
import logging
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import re
import json


logger = logging.getLogger(__name__)


class SecurityEvent(Enum):
    """Security event types."""
    AUTHENTICATION_FAILED = "auth_failed"
    AUTHORIZATION_DENIED = "authz_denied"
    SUSPICIOUS_PROMPT = "suspicious_prompt"
    DATA_LEAK_DETECTED = "data_leak"
    RATE_LIMIT_EXCEEDED = "rate_limit"
    COMPLIANCE_VIOLATION = "compliance_violation"


@dataclass
class SecurityContext:
    """Security context for LLM operations."""
    user_id: str
    session_id: str
    permissions: Set[str]
    security_level: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class SecurityValidator:
    """Comprehensive security validation for LLM operations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.blocked_patterns = self._load_blocked_patterns()
        self.pii_patterns = self._load_pii_patterns()
        self.rate_limits = {}
        self.security_events = []
        
    def validate_request(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]],
        security_context: SecurityContext
    ) -> bool:
        """Comprehensive request validation."""
        try:
            # Authentication check
            if not self._validate_authentication(security_context):
                self._log_security_event(
                    SecurityEvent.AUTHENTICATION_FAILED,
                    security_context
                )
                return False
            
            # Authorization check
            if not self._validate_authorization(security_context):
                self._log_security_event(
                    SecurityEvent.AUTHORIZATION_DENIED,
                    security_context
                )
                return False
            
            # Rate limiting
            if not self._check_rate_limit(security_context):
                self._log_security_event(
                    SecurityEvent.RATE_LIMIT_EXCEEDED,
                    security_context
                )
                return False
            
            # Content validation
            if not self._validate_content(prompt, security_context):
                return False
            
            # Context validation
            if context and not self._validate_context(context, security_context):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Security validation failed: {e}")
            return False
    
    def validate_response(
        self,
        response: str,
        security_context: SecurityContext
    ) -> bool:
        """Validate LLM response for security issues."""
        try:
            # Check for data leaks
            if self._detect_data_leak(response):
                self._log_security_event(
                    SecurityEvent.DATA_LEAK_DETECTED,
                    security_context
                )
                return False
            
            # Check for compliance violations
            if self._check_compliance_violations(response, security_context):
                self._log_security_event(
                    SecurityEvent.COMPLIANCE_VIOLATION,
                    security_context
                )
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Response validation failed: {e}")
            return False
    
    def _validate_authentication(self, security_context: SecurityContext) -> bool:
        """Validate user authentication."""
        if not security_context.user_id:
            return False
        
        if not security_context.session_id:
            return False
        
        # Validate session hasn't expired
        session_timeout = self.config.get('session_timeout', 3600)
        if time.time() - security_context.timestamp > session_timeout:
            return False
        
        return True
    
    def _validate_authorization(self, security_context: SecurityContext) -> bool:
        """Validate user authorization."""
        required_permission = self.config.get('required_permission', 'llm_access')
        
        if required_permission not in security_context.permissions:
            return False
        
        # Check security level requirements
        min_security_level = self.config.get('min_security_level', 1)
        if security_context.security_level < min_security_level:
            return False
        
        return True
    
    def _check_rate_limit(self, security_context: SecurityContext) -> bool:
        """Check rate limiting for user."""
        user_id = security_context.user_id
        current_time = time.time()
        
        # Clean old entries
        cutoff_time = current_time - 3600  # 1 hour window
        if user_id in self.rate_limits:
            self.rate_limits[user_id] = [
                t for t in self.rate_limits[user_id] if t > cutoff_time
            ]
        else:
            self.rate_limits[user_id] = []
        
        # Check limit
        max_requests = self.config.get('max_requests_per_hour', 100)
        if len(self.rate_limits[user_id]) >= max_requests:
            return False
        
        # Add current request
        self.rate_limits[user_id].append(current_time)
        return True
    
    def _validate_content(
        self,
        prompt: str,
        security_context: SecurityContext
    ) -> bool:
        """Validate prompt content for security issues."""
        # Check for blocked patterns
        for pattern in self.blocked_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                self._log_security_event(
                    SecurityEvent.SUSPICIOUS_PROMPT,
                    security_context,
                    {'pattern': pattern}
                )
                return False
        
        # Check for PII
        if self._detect_pii(prompt):
            self._log_security_event(
                SecurityEvent.DATA_LEAK_DETECTED,
                security_context
            )
            return False
        
        # Check prompt length
        max_prompt_length = self.config.get('max_prompt_length', 10000)
        if len(prompt) > max_prompt_length:
            return False
        
        return True
    
    def _validate_context(
        self,
        context: Dict[str, Any],
        security_context: SecurityContext
    ) -> bool:
        """Validate context data for security issues."""
        context_str = json.dumps(context, default=str)
        
        # Check for PII in context
        if self._detect_pii(context_str):
            self._log_security_event(
                SecurityEvent.DATA_LEAK_DETECTED,
                security_context
            )
            return False
        
        # Check context size
        max_context_size = self.config.get('max_context_size', 50000)
        if len(context_str) > max_context_size:
            return False
        
        return True
    
    def _detect_pii(self, text: str) -> bool:
        """Detect personally identifiable information."""
        for pattern in self.pii_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _detect_data_leak(self, text: str) -> bool:
        """Detect potential data leaks in response."""
        # Check for common data leak indicators
        leak_patterns = [
            r'password\s*[:=]\s*\w+',
            r'api[_-]?key\s*[:=]\s*\w+',
            r'secret\s*[:=]\s*\w+',
            r'token\s*[:=]\s*\w+',
            r'database\s+connection',
            r'internal\s+server',
        ]
        
        for pattern in leak_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _check_compliance_violations(
        self,
        text: str,
        security_context: SecurityContext
    ) -> bool:
        """Check for regulatory compliance violations."""
        # GDPR compliance
        if self.config.get('gdpr_enabled', False):
            if self._detect_pii(text):
                return True
        
        # Industry-specific compliance
        compliance_rules = self.config.get('compliance_rules', [])
        for rule in compliance_rules:
            pattern = rule.get('pattern', '')
            if pattern and re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _load_blocked_patterns(self) -> List[str]:
        """Load blocked content patterns."""
        default_patterns = [
            r'ignore\s+previous\s+instructions',
            r'jailbreak',
            r'prompt\s+injection',
            r'system\s+prompt',
            r'developer\s+mode',
            r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>',
            r'javascript:',
            r'sql\s+injection',
            r'union\s+select',
            r'drop\s+table',
        ]
        
        custom_patterns = self.config.get('blocked_patterns', [])
        return default_patterns + custom_patterns
    
    def _load_pii_patterns(self) -> List[str]:
        """Load PII detection patterns."""
        return [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Credit card
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}[\s.-]?\d{3}[\s.-]?\d{4}\b',  # Phone
            r'\b\d{1,5}\s+\w+\s+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|way|court|ct)\b',  # Address
        ]
    
    def _log_security_event(
        self,
        event_type: SecurityEvent,
        security_context: SecurityContext,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log security event."""
        event = {
            'timestamp': time.time(),
            'event_type': event_type.value,
            'user_id': security_context.user_id,
            'session_id': security_context.session_id,
            'ip_address': security_context.ip_address,
            'security_level': security_context.security_level,
        }
        
        if additional_data:
            event.update(additional_data)
        
        self.security_events.append(event)
        logger.warning(f"Security event: {event_type.value} for user {security_context.user_id}")
    
    def get_security_events(
        self,
        since: Optional[float] = None,
        event_types: Optional[List[SecurityEvent]] = None
    ) -> List[Dict[str, Any]]:
        """Get security events with optional filtering."""
        events = self.security_events
        
        if since:
            events = [e for e in events if e['timestamp'] >= since]
        
        if event_types:
            event_type_values = [et.value for et in event_types]
            events = [e for e in events if e['event_type'] in event_type_values]
        
        return events


class EncryptionManager:
    """Handle encryption/decryption of sensitive data."""
    
    def __init__(self, encryption_key: str):
        self.encryption_key = encryption_key.encode()
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        # Simple HMAC-based encryption for demo
        # In production, use proper encryption libraries
        signature = hmac.new(
            self.encryption_key,
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{signature}:{data}"
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        try:
            signature, data = encrypted_data.split(':', 1)
            
            expected_signature = hmac.new(
                self.encryption_key,
                data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if hmac.compare_digest(signature, expected_signature):
                return data
            else:
                raise ValueError("Invalid signature")
                
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise


class ComplianceManager:
    """Manage regulatory compliance requirements."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.compliance_rules = config.get('compliance_rules', {})
    
    def check_gdpr_compliance(self, data: str, user_consent: bool) -> bool:
        """Check GDPR compliance for data processing."""
        if not self.config.get('gdpr_enabled', False):
            return True
        
        # Check user consent
        if not user_consent:
            return False
        
        # Check for EU personal data
        eu_indicators = [
            'european', 'eu citizen', 'gdpr', 'europe',
            'germany', 'france', 'italy', 'spain'
        ]
        
        for indicator in eu_indicators:
            if indicator in data.lower():
                return user_consent
        
        return True
    
    def check_hipaa_compliance(self, data: str) -> bool:
        """Check HIPAA compliance for healthcare data."""
        if not self.config.get('hipaa_enabled', False):
            return True
        
        # Check for protected health information
        phi_patterns = [
            r'patient\s+id',
            r'medical\s+record',
            r'diagnosis',
            r'treatment',
            r'medication',
            r'health\s+condition'
        ]
        
        for pattern in phi_patterns:
            if re.search(pattern, data, re.IGNORECASE):
                # PHI detected, check if properly anonymized
                return self._check_phi_anonymization(data)
        
        return True
    
    def _check_phi_anonymization(self, data: str) -> bool:
        """Check if PHI is properly anonymized."""
        # Basic anonymization checks
        anonymization_indicators = [
            'patient_id_123', '[redacted]', '[anonymized]',
            'subject_001', 'participant_'
        ]
        
        for indicator in anonymization_indicators:
            if indicator in data.lower():
                return True
        
        return False
