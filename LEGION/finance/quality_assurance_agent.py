"""
Quality Assurance Agent (Finance/Reporting) - Enterprise Legion Framework
Ensure data accuracy and compliance across financial operations
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core_framework import BaseAgent, AgentMessage
import uuid


@dataclass
class QualityCheck:
    """Quality check data structure"""
    check_id: str
    check_type: str
    description: str
    severity: str
    status: str
    findings: List[str]
    timestamp: datetime
    source_data: Dict[str, Any]


@dataclass
class AuditTrail:
    """Audit trail data structure"""
    action_id: str
    action_type: str
    agent_id: str
    timestamp: datetime
    data_before: Dict[str, Any]
    data_after: Dict[str, Any]
    validation_result: bool


class QualityAssuranceAgent(BaseAgent):
    """
    Quality Assurance Agent for ensuring data accuracy and compliance
    across financial operations and reporting.
    """
    
    def __init__(self, agent_id: str = "qualityassuranceagent"):
        capabilities = ["quality_assurance", "data_validation"]
        super().__init__(agent_id, "QualityAssuranceAgent", "finance", capabilities)
        self.quality_checks = []
        self.audit_trails = []
        self.compliance_rules = {}
        self.validation_schemas = {}
        self.error_patterns = {}
        self.quality_metrics = {}
        
    async def initialize(self):
        """Initialize the agent with quality rules and validation schemas"""
        await super().initialize()
        
        # Initialize compliance rules and validation schemas
        self._setup_compliance_rules()
        self._setup_validation_schemas()
        self._setup_error_patterns()
        
        # Subscribe to relevant message types
        await self.subscribe_to_messages([
            "financial_data_update",
            "financial_projections_update",
            "report_generation_request",
            "audit_request",
            "compliance_check_request",
            "data_validation_request"
        ])
        
        self.logger.info("Quality Assurance Agent initialized")
        
    def _setup_compliance_rules(self):
        """Setup compliance rules for financial data"""
        self.compliance_rules = {
            'revenue_recognition': {
                'description': 'Revenue recognition compliance',
                'rules': [
                    'Revenue must be recognized when earned',
                    'Revenue must have supporting documentation',
                    'Revenue adjustments must be properly documented'
                ],
                'validation_functions': ['validate_revenue_recognition']
            },
            'expense_classification': {
                'description': 'Expense classification accuracy',
                'rules': [
                    'Expenses must be classified correctly',
                    'Capital vs operational expenses distinction',
                    'Expense timing must be appropriate'
                ],
                'validation_functions': ['validate_expense_classification']
            },
            'financial_reporting': {
                'description': 'Financial reporting standards',
                'rules': [
                    'Reports must include all required sections',
                    'Financial statements must balance',
                    'Disclosures must be complete'
                ],
                'validation_functions': ['validate_financial_reports']
            },
            'data_integrity': {
                'description': 'Data integrity requirements',
                'rules': [
                    'No duplicate transactions',
                    'All amounts must be numeric and valid',
                    'Dates must be valid and logical'
                ],
                'validation_functions': ['validate_data_integrity']
            }
        }
        
    def _setup_validation_schemas(self):
        """Setup validation schemas for different data types"""
        self.validation_schemas = {
            'financial_transaction': {
                'required_fields': ['transaction_id', 'amount', 'date', 'account', 'description'],
                'field_types': {
                    'transaction_id': str,
                    'amount': float,
                    'date': datetime,
                    'account': str,
                    'description': str
                },
                'constraints': {
                    'amount': {'min': -1000000, 'max': 1000000},
                    'date': {'not_future': True}
                }
            },
            'budget_item': {
                'required_fields': ['category', 'budgeted_amount', 'actual_amount', 'period'],
                'field_types': {
                    'category': str,
                    'budgeted_amount': float,
                    'actual_amount': float,
                    'period': str
                },
                'constraints': {
                    'budgeted_amount': {'min': 0},
                    'actual_amount': {'min': 0}
                }
            },
            'financial_report': {
                'required_fields': ['report_type', 'period', 'revenue', 'expenses', 'profit'],
                'field_types': {
                    'report_type': str,
                    'period': str,
                    'revenue': float,
                    'expenses': float,
                    'profit': float
                },
                'constraints': {
                    'revenue': {'min': 0},
                    'expenses': {'min': 0}
                }
            }
        }
        
    def _setup_error_patterns(self):
        """Setup common error patterns to detect"""
        self.error_patterns = {
            'duplicate_transactions': {
                'description': 'Duplicate transaction detection',
                'pattern': 'same_amount_same_date_same_account',
                'severity': 'high'
            },
            'unusual_amounts': {
                'description': 'Unusually large or small amounts',
                'pattern': 'amount_outside_normal_range',
                'severity': 'medium'
            },
            'invalid_dates': {
                'description': 'Invalid or illogical dates',
                'pattern': 'future_dates_or_invalid_format',
                'severity': 'high'
            },
            'missing_documentation': {
                'description': 'Missing supporting documentation',
                'pattern': 'transaction_without_reference',
                'severity': 'medium'
            },
            'account_reconciliation_issues': {
                'description': 'Account reconciliation discrepancies',
                'pattern': 'balance_mismatch',
                'severity': 'high'
            }
        }

    async def process_message(self, message: AgentMessage):
        """Process incoming messages and perform quality checks"""
        try:
            if message.message_type == "financial_data_update":
                await self._validate_financial_data(message)
            elif message.message_type == "financial_projections_update":
                await self._validate_projections_data(message)
            elif message.message_type == "report_generation_request":
                await self._validate_report_request(message)
            elif message.message_type == "audit_request":
                await self._handle_audit_request(message)
            elif message.message_type == "compliance_check_request":
                await self._handle_compliance_check(message)
            elif message.message_type == "data_validation_request":
                await self._handle_validation_request(message)
                
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            
    async def _validate_financial_data(self, message: AgentMessage):
        """Validate incoming financial data"""
        data = message.content
        checks = []
        
        # Perform data integrity checks
        integrity_check = await self._check_data_integrity(data, 'financial_data')
        checks.append(integrity_check)
        
        # Check for error patterns
        pattern_checks = await self._check_error_patterns(data)
        checks.extend(pattern_checks)
        
        # Validate against compliance rules
        compliance_checks = await self._check_compliance_rules(data, 'financial_data')
        checks.extend(compliance_checks)
        
        # Store quality check results
        self.quality_checks.extend(checks)
        
        # Send validation results back
        validation_result = {
            'validation_status': 'passed' if all(check.status == 'passed' for check in checks) else 'failed',
            'checks_performed': len(checks),
            'issues_found': len([check for check in checks if check.status == 'failed']),
            'quality_score': self._calculate_quality_score(checks),
            'recommendations': self._generate_recommendations(checks)
        }
        
        response = AgentMessage(
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type="data_validation_response",
            content=validation_result
        )
        await self.send_message(response)
        
        # Create audit trail
        audit_trail = AuditTrail(
            action_id=f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            action_type="data_validation",
            agent_id=message.sender_id,
            timestamp=datetime.now(),
            data_before={},
            data_after=data,
            validation_result=validation_result['validation_status'] == 'passed'
        )
        self.audit_trails.append(audit_trail)
        
    async def _validate_projections_data(self, message: AgentMessage):
        """Validate financial projections data"""
        data = message.content
        checks = []
        
        # Check projection reasonableness
        reasonableness_check = await self._check_projection_reasonableness(data)
        checks.append(reasonableness_check)
        
        # Check assumption consistency
        consistency_check = await self._check_assumption_consistency(data)
        checks.append(consistency_check)
        
        # Validate projection methodology
        methodology_check = await self._validate_projection_methodology(data)
        checks.append(methodology_check)
        
        self.quality_checks.extend(checks)
        
        # Send results to interested parties
        if any(check.status == 'failed' for check in checks):
            alert = AgentMessage(
                sender_id=self.agent_id,
                recipient_id="financial_modeling_agent",
                message_type="projection_quality_alert",
                content={
                    'issues': [check.findings for check in checks if check.status == 'failed'],
                    'recommendations': self._generate_recommendations(checks)
                }
            )
            await self.send_message(alert)
            
    async def _validate_report_request(self, message: AgentMessage):
        """Validate report generation request"""
        request = message.content
        checks = []
        
        # Validate report parameters
        param_check = await self._validate_report_parameters(request)
        checks.append(param_check)
        
        # Check data completeness for report
        completeness_check = await self._check_report_data_completeness(request)
        checks.append(completeness_check)
        
        # Validate report template compliance
        template_check = await self._validate_report_template(request)
        checks.append(template_check)
        
        self.quality_checks.extend(checks)
        
        # Send validation result
        validation_result = {
            'can_generate_report': all(check.status == 'passed' for check in checks),
            'quality_issues': [check.findings for check in checks if check.status == 'failed'],
            'data_quality_score': self._calculate_quality_score(checks)
        }
        
        response = AgentMessage(
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type="report_validation_response",
            content=validation_result
        )
        await self.send_message(response)
        
    async def _handle_audit_request(self, message: AgentMessage):
        """Handle audit request from compliance or external auditors"""
        request = message.content
        audit_period = request.get('period', 'current_month')
        audit_scope = request.get('scope', 'full')
        
        # Perform comprehensive audit
        audit_results = await self._perform_comprehensive_audit(audit_period, audit_scope)
        
        response = AgentMessage(
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type="audit_response",
            content=audit_results
        )
        await self.send_message(response)
        
    async def _handle_compliance_check(self, message: AgentMessage):
        """Handle compliance check request"""
        request = message.content
        compliance_area = request.get('area', 'all')
        
        # Perform compliance checks
        compliance_results = await self._perform_compliance_checks(compliance_area)
        
        response = AgentMessage(
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type="compliance_check_response",
            content=compliance_results
        )
        await self.send_message(response)
        
    async def _handle_validation_request(self, message: AgentMessage):
        """Handle data validation request"""
        request = message.content
        data = request.get('data', {})
        validation_type = request.get('type', 'general')
        
        # Perform requested validation
        validation_results = await self._perform_validation(data, validation_type)
        
        response = AgentMessage(
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type="validation_response",
            content=validation_results
        )
        await self.send_message(response)
        
    async def _check_data_integrity(self, data: Dict[str, Any], data_type: str) -> QualityCheck:
        """Check data integrity against validation schema"""
        findings = []
        
        schema = self.validation_schemas.get(data_type, {})
        required_fields = schema.get('required_fields', [])
        field_types = schema.get('field_types', {})
        constraints = schema.get('constraints', {})
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                findings.append(f"Missing required field: {field}")
                
        # Check field types
        for field, expected_type in field_types.items():
            if field in data and not isinstance(data[field], expected_type):
                findings.append(f"Invalid type for {field}: expected {expected_type.__name__}")
                
        # Check constraints
        for field, field_constraints in constraints.items():
            if field in data:
                value = data[field]
                
                if 'min' in field_constraints and value < field_constraints['min']:
                    findings.append(f"{field} below minimum value: {field_constraints['min']}")
                    
                if 'max' in field_constraints and value > field_constraints['max']:
                    findings.append(f"{field} above maximum value: {field_constraints['max']}")
                    
                if 'not_future' in field_constraints and isinstance(value, datetime) and value > datetime.now():
                    findings.append(f"{field} contains future date")
        
        return QualityCheck(
            check_id=f"integrity_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            check_type="data_integrity",
            description="Data integrity validation",
            severity="high",
            status="passed" if not findings else "failed",
            findings=findings,
            timestamp=datetime.now(),
            source_data=data
        )
        
    async def _check_error_patterns(self, data: Dict[str, Any]) -> List[QualityCheck]:
        """Check for common error patterns"""
        checks = []
        
        for pattern_name, pattern_info in self.error_patterns.items():
            findings = []
            
            if pattern_name == 'duplicate_transactions':
                findings = await self._detect_duplicate_transactions(data)
            elif pattern_name == 'unusual_amounts':
                findings = await self._detect_unusual_amounts(data)
            elif pattern_name == 'invalid_dates':
                findings = await self._detect_invalid_dates(data)
            elif pattern_name == 'missing_documentation':
                findings = await self._detect_missing_documentation(data)
            elif pattern_name == 'account_reconciliation_issues':
                findings = await self._detect_reconciliation_issues(data)
                
            check = QualityCheck(
                check_id=f"{pattern_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                check_type="error_pattern",
                description=pattern_info['description'],
                severity=pattern_info['severity'],
                status="passed" if not findings else "failed",
                findings=findings,
                timestamp=datetime.now(),
                source_data=data
            )
            checks.append(check)
            
        return checks
        
    async def _check_compliance_rules(self, data: Dict[str, Any], context: str) -> List[QualityCheck]:
        """Check compliance rules"""
        checks = []
        
        for rule_name, rule_info in self.compliance_rules.items():
            findings = []
            
            # Apply validation functions for this rule
            for validation_func in rule_info['validation_functions']:
                if hasattr(self, validation_func):
                    func = getattr(self, validation_func)
                    rule_findings = await func(data, context)
                    findings.extend(rule_findings)
                    
            check = QualityCheck(
                check_id=f"{rule_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                check_type="compliance",
                description=rule_info['description'],
                severity="high",
                status="passed" if not findings else "failed",
                findings=findings,
                timestamp=datetime.now(),
                source_data=data
            )
            checks.append(check)
            
        return checks
        
    async def _detect_duplicate_transactions(self, data: Dict[str, Any]) -> List[str]:
        """Detect duplicate transactions"""
        findings = []
        transactions = data.get('transactions', [])
        
        seen_transactions = set()
        for transaction in transactions:
            # Create a signature for the transaction
            signature = (
                transaction.get('amount'),
                transaction.get('date'),
                transaction.get('account')
            )
            
            if signature in seen_transactions:
                findings.append(f"Potential duplicate transaction: {signature}")
            else:
                seen_transactions.add(signature)
                
        return findings
        
    async def _detect_unusual_amounts(self, data: Dict[str, Any]) -> List[str]:
        """Detect unusually large or small amounts"""
        findings = []
        transactions = data.get('transactions', [])
        
        if transactions:
            amounts = [t.get('amount', 0) for t in transactions]
            if amounts:
                avg_amount = sum(amounts) / len(amounts)
                
                for transaction in transactions:
                    amount = transaction.get('amount', 0)
                    if abs(amount) > avg_amount * 10:  # 10x average
                        findings.append(f"Unusually large amount: {amount}")
                    elif abs(amount) < 0.01 and amount != 0:  # Very small non-zero
                        findings.append(f"Unusually small amount: {amount}")
                        
        return findings
        
    async def _detect_invalid_dates(self, data: Dict[str, Any]) -> List[str]:
        """Detect invalid dates"""
        findings = []
        transactions = data.get('transactions', [])
        
        for transaction in transactions:
            date_value = transaction.get('date')
            if date_value:
                if isinstance(date_value, str):
                    try:
                        parsed_date = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                        if parsed_date > datetime.now():
                            findings.append(f"Future date detected: {date_value}")
                    except ValueError:
                        findings.append(f"Invalid date format: {date_value}")
                elif isinstance(date_value, datetime):
                    if date_value > datetime.now():
                        findings.append(f"Future date detected: {date_value}")
                        
        return findings
        
    async def _detect_missing_documentation(self, data: Dict[str, Any]) -> List[str]:
        """Detect missing documentation"""
        findings = []
        transactions = data.get('transactions', [])
        
        for transaction in transactions:
            if not transaction.get('reference') and not transaction.get('description'):
                findings.append(f"Transaction missing documentation: {transaction.get('transaction_id')}")
                
        return findings
        
    async def _detect_reconciliation_issues(self, data: Dict[str, Any]) -> List[str]:
        """Detect account reconciliation issues"""
        findings = []
        
        # Check if debits equal credits
        debits = sum(t.get('amount', 0) for t in data.get('transactions', []) if t.get('amount', 0) > 0)
        credits = sum(abs(t.get('amount', 0)) for t in data.get('transactions', []) if t.get('amount', 0) < 0)
        
        if abs(debits - credits) > 0.01:  # Allow for small rounding differences
            findings.append(f"Debits ({debits}) do not equal credits ({credits})")
            
        return findings
        
    async def validate_revenue_recognition(self, data: Dict[str, Any], context: str) -> List[str]:
        """Validate revenue recognition compliance"""
        findings = []
        
        revenue_items = data.get('revenue_items', [])
        for item in revenue_items:
            if not item.get('earned_date'):
                findings.append(f"Revenue item missing earned date: {item.get('item_id')}")
            if not item.get('supporting_docs'):
                findings.append(f"Revenue item missing documentation: {item.get('item_id')}")
                
        return findings
        
    async def validate_expense_classification(self, data: Dict[str, Any], context: str) -> List[str]:
        """Validate expense classification"""
        findings = []
        
        expenses = data.get('expenses', [])
        for expense in expenses:
            category = expense.get('category')
            amount = expense.get('amount', 0)
            
            # Check for potential misclassification
            if category == 'office_supplies' and amount > 5000:
                findings.append(f"Large office supply expense may need reclassification: {amount}")
            elif category == 'travel' and amount > 10000:
                findings.append(f"Large travel expense requires additional documentation: {amount}")
                
        return findings
        
    async def validate_financial_reports(self, data: Dict[str, Any], context: str) -> List[str]:
        """Validate financial report completeness"""
        findings = []
        
        if context == 'financial_report':
            required_sections = ['revenue', 'expenses', 'profit', 'cash_flow']
            for section in required_sections:
                if section not in data:
                    findings.append(f"Missing required report section: {section}")
                    
        return findings
        
    def _calculate_quality_score(self, checks: List[QualityCheck]) -> float:
        """Calculate overall quality score"""
        if not checks:
            return 100.0
            
        passed_checks = len([check for check in checks if check.status == 'passed'])
        total_checks = len(checks)
        
        return (passed_checks / total_checks) * 100
        
    def _generate_recommendations(self, checks: List[QualityCheck]) -> List[str]:
        """Generate recommendations based on quality check results"""
        recommendations = []
        
        failed_checks = [check for check in checks if check.status == 'failed']
        
        for check in failed_checks:
            if check.check_type == 'data_integrity':
                recommendations.append("Review data entry processes and validation rules")
            elif check.check_type == 'error_pattern':
                if 'duplicate' in check.description.lower():
                    recommendations.append("Implement duplicate detection in data entry")
                elif 'unusual' in check.description.lower():
                    recommendations.append("Review transaction approval thresholds")
            elif check.check_type == 'compliance':
                recommendations.append(f"Address compliance issues in {check.description}")
                
        return list(set(recommendations))  # Remove duplicates

    async def get_status(self) -> Dict[str, Any]:
        """Get current status of the Quality Assurance Agent"""
        recent_checks = [check for check in self.quality_checks 
                        if check.timestamp > datetime.now() - timedelta(days=7)]
        
        return {
            'agent_id': self.agent_id,
            'status': 'active',
            'total_checks_performed': len(self.quality_checks),
            'recent_checks': len(recent_checks),
            'recent_quality_score': self._calculate_quality_score(recent_checks),
            'compliance_rules': len(self.compliance_rules),
            'validation_schemas': len(self.validation_schemas),
            'audit_trails': len(self.audit_trails)
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

