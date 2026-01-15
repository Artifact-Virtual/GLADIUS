"""
Compliance Checker Agent - Enterprise Legion Framework
Ensure organizational adherence to regulations and policies
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core_framework import BaseAgent, AgentMessage
import uuid


@dataclass
class ComplianceRule:
    """Compliance rule data structure"""
    rule_id: str
    rule_name: str
    category: str
    description: str
    severity: str
    validation_criteria: Dict[str, Any]
    last_updated: datetime


@dataclass
class ComplianceCheck:
    """Compliance check result data structure"""
    check_id: str
    rule_id: str
    status: str
    findings: List[str]
    risk_level: str
    timestamp: datetime
    data_checked: Dict[str, Any]
    remediation_steps: List[str]


class ComplianceCheckerAgent(BaseAgent):
    """
    Compliance Checker Agent for ensuring organizational adherence
    to regulations, policies, and compliance requirements.
    """
    
    def __init__(self, agent_id: str = "compliancecheckeragent"):
        capabilities = ["compliance_checking", "regulatory_analysis"]
        super().__init__(agent_id, "ComplianceCheckerAgent", "legal", capabilities)
        self.compliance_rules = {}
        self.compliance_checks = []
        self.policy_violations = []
        self.regulatory_requirements = {}
        self.compliance_score = 100.0
        
    async def initialize(self):
        """Initialize the agent with compliance rules and requirements"""
        await super().initialize()
        
        # Setup compliance framework
        self._setup_compliance_rules()
        self._setup_regulatory_requirements()
        
        # Subscribe to relevant message types
        await self.subscribe_to_messages([
            "financial_data_update",
            "operational_data_update",
            "legal_document_update",
            "compliance_check_request",
            "policy_update",
            "audit_preparation_request",
            "regulatory_change_notification"
        ])
        
        self.logger.info("Compliance Checker Agent initialized")
        
    def _setup_compliance_rules(self):
        """Setup comprehensive compliance rules"""
        self.compliance_rules = {
            'data_privacy': ComplianceRule(
                rule_id="privacy_001",
                rule_name="Data Privacy Protection",
                category="data_privacy",
                description="Ensure personal data is protected per privacy regulations",
                severity="high",
                validation_criteria={
                    'data_encryption': True,
                    'access_controls': True,
                    'data_retention_limits': True,
                    'consent_tracking': True
                },
                last_updated=datetime.now()
            ),
            'financial_reporting': ComplianceRule(
                rule_id="finance_001",
                rule_name="Financial Reporting Standards",
                category="financial",
                description="Ensure financial reports meet regulatory standards",
                severity="high",
                validation_criteria={
                    'gaap_compliance': True,
                    'documentation_complete': True,
                    'audit_trail_available': True,
                    'disclosures_accurate': True
                },
                last_updated=datetime.now()
            ),
            'employment_law': ComplianceRule(
                rule_id="hr_001",
                rule_name="Employment Law Compliance",
                category="human_resources",
                description="Ensure compliance with employment regulations",
                severity="medium",
                validation_criteria={
                    'equal_opportunity': True,
                    'wage_hour_compliance': True,
                    'workplace_safety': True,
                    'benefits_compliance': True
                },
                last_updated=datetime.now()
            ),
            'anti_corruption': ComplianceRule(
                rule_id="ethics_001",
                rule_name="Anti-Corruption Compliance",
                category="ethics",
                description="Prevent corruption and ensure ethical business practices",
                severity="high",
                validation_criteria={
                    'gift_policy_compliance': True,
                    'conflict_of_interest_disclosure': True,
                    'third_party_due_diligence': True,
                    'political_contributions_tracking': True
                },
                last_updated=datetime.now()
            ),
            'cybersecurity': ComplianceRule(
                rule_id="security_001",
                rule_name="Cybersecurity Standards",
                category="security",
                description="Maintain cybersecurity compliance standards",
                severity="high",
                validation_criteria={
                    'access_controls': True,
                    'data_protection': True,
                    'incident_response': True,
                    'security_training': True
                },
                last_updated=datetime.now()
            )
        }
        
    def _setup_regulatory_requirements(self):
        """Setup regulatory requirements by jurisdiction/industry"""
        self.regulatory_requirements = {
            'gdpr': {
                'name': 'General Data Protection Regulation',
                'jurisdiction': 'EU',
                'applicable_rules': ['data_privacy'],
                'requirements': [
                    'Data processing consent',
                    'Right to deletion',
                    'Data portability',
                    'Breach notification'
                ]
            },
            'sox': {
                'name': 'Sarbanes-Oxley Act',
                'jurisdiction': 'US',
                'applicable_rules': ['financial_reporting'],
                'requirements': [
                    'Internal controls certification',
                    'CEO/CFO certification',
                    'External auditor independence',
                    'Financial disclosure accuracy'
                ]
            },
            'hipaa': {
                'name': 'Health Insurance Portability and Accountability Act',
                'jurisdiction': 'US',
                'applicable_rules': ['data_privacy', 'cybersecurity'],
                'requirements': [
                    'PHI protection',
                    'Access controls',
                    'Audit logs',
                    'Business associate agreements'
                ]
            }
        }

    async def process_message(self, message: AgentMessage):
        """Process incoming messages and perform compliance checks"""
        try:
            if message.message_type == "financial_data_update":
                await self._check_financial_compliance(message)
            elif message.message_type == "operational_data_update":
                await self._check_operational_compliance(message)
            elif message.message_type == "legal_document_update":
                await self._check_document_compliance(message)
            elif message.message_type == "compliance_check_request":
                await self._handle_compliance_check_request(message)
            elif message.message_type == "policy_update":
                await self._handle_policy_update(message)
            elif message.message_type == "audit_preparation_request":
                await self._handle_audit_preparation(message)
            elif message.message_type == "regulatory_change_notification":
                await self._handle_regulatory_change(message)
                
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            
    async def _check_financial_compliance(self, message: AgentMessage):
        """Check financial data for compliance violations"""
        financial_data = message.content
        checks = []
        
        # Check financial reporting compliance
        financial_rule = self.compliance_rules['financial_reporting']
        check_result = await self._validate_against_rule(
            financial_data, financial_rule, 'financial_data'
        )
        checks.append(check_result)
        
        # Check anti-corruption compliance
        corruption_rule = self.compliance_rules['anti_corruption']
        corruption_check = await self._validate_against_rule(
            financial_data, corruption_rule, 'financial_transactions'
        )
        checks.append(corruption_check)
        
        # Store check results
        self.compliance_checks.extend(checks)
        
        # Update compliance score
        await self._update_compliance_score()
        
        # Send alerts for violations
        violations = [check for check in checks if check.status == 'violation']
        if violations:
            await self._send_compliance_alerts(violations)
            
    async def _check_operational_compliance(self, message: AgentMessage):
        """Check operational data for compliance"""
        operational_data = message.content
        checks = []
        
        # Check cybersecurity compliance
        security_rule = self.compliance_rules['cybersecurity']
        security_check = await self._validate_against_rule(
            operational_data, security_rule, 'operational_systems'
        )
        checks.append(security_check)
        
        # Check employment law compliance
        hr_rule = self.compliance_rules['employment_law']
        hr_check = await self._validate_against_rule(
            operational_data, hr_rule, 'hr_practices'
        )
        checks.append(hr_check)
        
        self.compliance_checks.extend(checks)
        
        # Alert on violations
        violations = [check for check in checks if check.status == 'violation']
        if violations:
            await self._send_compliance_alerts(violations)
            
    async def _check_document_compliance(self, message: AgentMessage):
        """Check legal documents for compliance"""
        document_data = message.content
        checks = []
        
        # Check all applicable rules for document compliance
        for rule_id, rule in self.compliance_rules.items():
            if await self._is_rule_applicable_to_document(rule, document_data):
                check_result = await self._validate_against_rule(
                    document_data, rule, 'legal_document'
                )
                checks.append(check_result)
                
        self.compliance_checks.extend(checks)
        
        # Generate compliance report for document
        compliance_report = await self._generate_document_compliance_report(
            document_data, checks
        )
        
        # Send report back
        response = AgentMessage(
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type="document_compliance_report",
            content=compliance_report
        )
        await self.send_message(response)
        
    async def _validate_against_rule(self, data: Dict[str, Any], 
                                   rule: ComplianceRule, 
                                   context: str) -> ComplianceCheck:
        """Validate data against a specific compliance rule"""
        findings = []
        risk_level = "low"
        status = "compliant"
        
        # Check each validation criterion
        for criterion, required_value in rule.validation_criteria.items():
            actual_value = await self._extract_criterion_value(data, criterion, context)
            
            if actual_value != required_value:
                findings.append(f"Criterion '{criterion}' failed: expected {required_value}, got {actual_value}")
                if rule.severity == "high":
                    risk_level = "high"
                    status = "violation"
                elif rule.severity == "medium" and risk_level != "high":
                    risk_level = "medium"
                    status = "warning"
                    
        # Generate remediation steps for violations
        remediation_steps = []
        if status in ["violation", "warning"]:
            remediation_steps = await self._generate_remediation_steps(rule, findings)
            
        return ComplianceCheck(
            check_id=f"check_{rule.rule_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            rule_id=rule.rule_id,
            status=status,
            findings=findings,
            risk_level=risk_level,
            timestamp=datetime.now(),
            data_checked=data,
            remediation_steps=remediation_steps
        )
        
    async def _extract_criterion_value(self, data: Dict[str, Any], 
                                     criterion: str, context: str) -> Any:
        """Extract the value for a specific compliance criterion"""
        # Map criteria to data extraction logic
        criterion_mappings = {
            'data_encryption': lambda d: d.get('security_settings', {}).get('encryption_enabled', False),
            'access_controls': lambda d: d.get('security_settings', {}).get('access_controls_enabled', False),
            'gaap_compliance': lambda d: d.get('accounting_standards', '') == 'GAAP',
            'documentation_complete': lambda d: d.get('documentation_status', '') == 'complete',
            'equal_opportunity': lambda d: d.get('hr_policies', {}).get('equal_opportunity', False),
            'gift_policy_compliance': lambda d: d.get('ethics_tracking', {}).get('gift_compliance', False)
        }
        
        extraction_func = criterion_mappings.get(criterion)
        if extraction_func:
            try:
                return extraction_func(data)
            except (KeyError, AttributeError):
                return False
        else:
            # Default: check if criterion exists in data
            return data.get(criterion, False)
            
    async def _generate_remediation_steps(self, rule: ComplianceRule, 
                                        findings: List[str]) -> List[str]:
        """Generate remediation steps for compliance violations"""
        remediation_map = {
            'data_privacy': [
                "Implement data encryption for all personal data",
                "Review and update access control policies",
                "Establish data retention and deletion procedures",
                "Implement consent tracking system"
            ],
            'financial_reporting': [
                "Review financial reporting processes",
                "Ensure all transactions are properly documented",
                "Implement audit trail maintenance",
                "Update disclosure procedures"
            ],
            'employment_law': [
                "Review HR policies for compliance",
                "Conduct equal opportunity training",
                "Audit wage and hour practices",
                "Update workplace safety procedures"
            ],
            'anti_corruption': [
                "Update gift and entertainment policies",
                "Implement conflict of interest disclosure process",
                "Conduct third-party due diligence reviews",
                "Review political contribution tracking"
            ],
            'cybersecurity': [
                "Strengthen access control systems",
                "Implement data protection measures",
                "Update incident response procedures",
                "Conduct security awareness training"
            ]
        }
        
        return remediation_map.get(rule.category, ["Review and update compliance procedures"])
        
    async def _update_compliance_score(self):
        """Update overall compliance score"""
        recent_checks = [check for check in self.compliance_checks 
                        if check.timestamp > datetime.now() - timedelta(days=30)]
        
        if not recent_checks:
            self.compliance_score = 100.0
            return
            
        total_checks = len(recent_checks)
        violations = len([check for check in recent_checks if check.status == "violation"])
        warnings = len([check for check in recent_checks if check.status == "warning"])
        
        # Calculate score: violations have more impact than warnings
        violation_penalty = (violations / total_checks) * 50
        warning_penalty = (warnings / total_checks) * 20
        
        self.compliance_score = max(0.0, 100.0 - violation_penalty - warning_penalty)
        
    async def _send_compliance_alerts(self, violations: List[ComplianceCheck]):
        """Send compliance violation alerts"""
        for violation in violations:
            # Determine recipients based on severity and category
            recipients = await self._determine_alert_recipients(violation)
            
            for recipient in recipients:
                alert = AgentMessage(
                    sender_id=self.agent_id,
                    recipient_id=recipient,
                    message_type="compliance_violation_alert",
                    content={
                        'violation': violation.__dict__,
                        'urgency': violation.risk_level,
                        'immediate_action_required': violation.risk_level == "high"
                    }
                )
                await self.send_message(alert)
                
    async def _determine_alert_recipients(self, violation: ComplianceCheck) -> List[str]:
        """Determine who should receive compliance alerts"""
        recipients = []
        
        rule = self.compliance_rules.get(violation.rule_id)
        if not rule:
            return ["legal_team"]
            
        # Route based on category and severity
        if rule.category == "financial":
            recipients.extend(["cfo", "financial_analysis_agent"])
        elif rule.category == "data_privacy":
            recipients.extend(["privacy_officer", "security_audit_agent"])
        elif rule.category == "human_resources":
            recipients.extend(["hr_director"])
        elif rule.category == "security":
            recipients.extend(["ciso", "security_audit_agent"])
        elif rule.category == "ethics":
            recipients.extend(["ethics_officer", "ceo"])
            
        # Always include legal team for high-risk violations
        if violation.risk_level == "high":
            recipients.append("legal_team")
            
        return list(set(recipients))  # Remove duplicates
        
    async def _handle_compliance_check_request(self, message: AgentMessage):
        """Handle requests for compliance checks"""
        request = message.content
        check_type = request.get('type', 'comprehensive')
        scope = request.get('scope', 'all')
        
        if check_type == 'comprehensive':
            results = await self._perform_comprehensive_compliance_check(scope)
        elif check_type == 'specific_rule':
            rule_id = request.get('rule_id')
            results = await self._perform_specific_rule_check(rule_id, request.get('data', {}))
        else:
            results = await self._perform_basic_compliance_check()
            
        response = AgentMessage(
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type="compliance_check_response",
            content=results
        )
        await self.send_message(response)
        
    async def _perform_comprehensive_compliance_check(self, scope: str) -> Dict[str, Any]:
        """Perform comprehensive compliance assessment"""
        # This would integrate with various data sources
        assessment_results = {
            'overall_score': self.compliance_score,
            'rule_compliance': {},
            'violations_summary': {},
            'recommendations': [],
            'next_review_date': (datetime.now() + timedelta(days=90)).isoformat()
        }
        
        # Check each rule
        for rule_id, rule in self.compliance_rules.items():
            if scope == 'all' or rule.category in scope:
                # Simulate compliance check
                mock_data = {'compliance_status': 'review_needed'}
                check_result = await self._validate_against_rule(mock_data, rule, 'assessment')
                
                assessment_results['rule_compliance'][rule_id] = {
                    'status': check_result.status,
                    'risk_level': check_result.risk_level,
                    'last_checked': check_result.timestamp.isoformat()
                }
                
                if check_result.status != 'compliant':
                    assessment_results['violations_summary'][rule_id] = {
                        'findings': check_result.findings,
                        'remediation_steps': check_result.remediation_steps
                    }
                    
        # Generate recommendations
        assessment_results['recommendations'] = await self._generate_compliance_recommendations()
        
        return assessment_results

    async def get_status(self) -> Dict[str, Any]:
        """Get current status of the Compliance Checker Agent"""
        recent_checks = [check for check in self.compliance_checks 
                        if check.timestamp > datetime.now() - timedelta(days=7)]
        
        violations = [check for check in recent_checks if check.status == "violation"]
        warnings = [check for check in recent_checks if check.status == "warning"]
        
        return {
            'agent_id': self.agent_id,
            'status': 'active',
            'compliance_score': self.compliance_score,
            'total_rules': len(self.compliance_rules),
            'recent_checks': len(recent_checks),
            'recent_violations': len(violations),
            'recent_warnings': len(warnings),
            'regulatory_frameworks': len(self.regulatory_requirements),
            'last_assessment': max((check.timestamp for check in self.compliance_checks), 
                                 default=datetime.now()).isoformat() if self.compliance_checks else None
        }
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process assigned tasks"""
        try:
            task_type = task.get('type', 'unknown')
            
            if task_type == 'status_check':
                return {"status": "completed", "agent_status": "active"}
            elif task_type == 'ping':
                return {"status": "completed", "response": "pong"}
            else:
                return {"status": "failed", "error": f"Unknown task type: {task_type}"}
                
        except Exception as e:
            self.logger.error(f"Error processing task: {str(e)}")
            return {"status": "failed", "error": str(e)}

    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle incoming messages from other agents"""
        try:
            # Default handling - can be overridden by specific agents
            self.logger.info(f"Received message of type: {message.message_type}")
            
            if message.message_type == "ping":
                response = AgentMessage(
                    id=str(uuid.uuid4()),
                    source_agent=self.agent_id,
                    target_agent=message.source_agent,
                    message_type="pong",
                    payload={"response": "pong"},
                    timestamp=datetime.now()
                )
                return response
            
            self.performance_metrics["messages_processed"] += 1
            return None
            
        except Exception as e:
            self.logger.error(f"Error handling message: {str(e)}")
            self.performance_metrics["errors"] += 1
            return None

