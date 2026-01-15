"""
Report Generation Agent - Enterprise Legion Framework
Create comprehensive reports across all departments
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core_framework import BaseAgent, AgentMessage
import uuid


@dataclass
class ReportSection:
    """Report section data structure"""
    title: str
    content: Dict[str, Any]
    visualization_type: str
    priority: int
    source_agent: str


@dataclass
class Report:
    """Report data structure"""
    report_id: str
    title: str
    sections: List[ReportSection]
    generated_at: datetime
    report_type: str
    recipients: List[str]
    executive_summary: str
    metadata: Dict[str, Any]


class ReportGenerationAgent(BaseAgent):
    """
    Report Generation Agent for creating comprehensive reports across
    all departments. Central hub for aggregating data from all agents.
    """
    
    def __init__(self, agent_id: str = "reportgenerationagent"):
        capabilities = ["report_generation", "data_visualization"]
        super().__init__(agent_id, "ReportGenerationAgent", "finance", capabilities)
        self.report_templates = {}
        self.scheduled_reports = {}
        self.data_cache = {}
        self.report_history = []
        
    async def initialize(self):
        """Initialize the agent with report templates and schedules"""
        await super().initialize()
        
        # Initialize report templates
        self._create_report_templates()
        
        # Schedule default reports
        self._schedule_default_reports()
        
        # Subscribe to relevant message types
        await self.subscribe_to_messages([
            "financial_data_update",
            "financial_projections_update",
            "market_analysis_update",
            "operational_metrics_update",
            "compliance_report_update",
            "performance_metrics_update",
            "report_request",
            "schedule_report_request"
        ])
        
        self.logger.info("Report Generation Agent initialized")
        
    def _create_report_templates(self):
        """Create standard report templates"""
        self.report_templates = {
            'financial_summary': {
                'title': 'Financial Performance Summary',
                'sections': [
                    'revenue_analysis',
                    'cost_analysis',
                    'profitability_metrics',
                    'cash_flow_status',
                    'budget_variance',
                    'financial_projections'
                ],
                'frequency': 'monthly',
                'recipients': ['cfo', 'ceo', 'finance_team']
            },
            'operational_dashboard': {
                'title': 'Operational Performance Dashboard',
                'sections': [
                    'productivity_metrics',
                    'resource_utilization',
                    'task_completion_rates',
                    'workflow_efficiency',
                    'bottleneck_analysis'
                ],
                'frequency': 'weekly',
                'recipients': ['coo', 'operations_team']
            },
            'executive_summary': {
                'title': 'Executive Summary Report',
                'sections': [
                    'key_performance_indicators',
                    'financial_highlights',
                    'operational_updates',
                    'market_insights',
                    'strategic_recommendations',
                    'risk_assessment'
                ],
                'frequency': 'monthly',
                'recipients': ['ceo', 'board_members', 'executives']
            },
            'compliance_report': {
                'title': 'Compliance and Risk Report',
                'sections': [
                    'compliance_status',
                    'audit_findings',
                    'risk_assessment',
                    'security_metrics',
                    'regulatory_updates'
                ],
                'frequency': 'quarterly',
                'recipients': ['legal_team', 'compliance_officer', 'ceo']
            },
            'market_intelligence': {
                'title': 'Market Intelligence Report',
                'sections': [
                    'market_trends',
                    'competitor_analysis',
                    'customer_insights',
                    'industry_analysis',
                    'strategic_opportunities'
                ],
                'frequency': 'monthly',
                'recipients': ['cmo', 'strategy_team', 'sales_team']
            }
        }
        
    def _schedule_default_reports(self):
        """Schedule default recurring reports"""
        now = datetime.now()
        
        for report_type, template in self.report_templates.items():
            frequency = template['frequency']
            
            if frequency == 'weekly':
                next_run = now + timedelta(days=7)
            elif frequency == 'monthly':
                next_run = now + timedelta(days=30)
            elif frequency == 'quarterly':
                next_run = now + timedelta(days=90)
            else:
                next_run = now + timedelta(days=1)
                
            self.scheduled_reports[report_type] = {
                'template': template,
                'next_run': next_run,
                'last_run': None,
                'enabled': True
            }

    async def process_message(self, message: AgentMessage):
        """Process incoming messages and update data cache"""
        try:
            # Cache incoming data for report generation
            self.data_cache[message.message_type] = {
                'data': message.content,
                'timestamp': datetime.now(),
                'source': message.sender_id
            }
            
            # Handle specific message types
            if message.message_type == "report_request":
                await self._handle_report_request(message)
            elif message.message_type == "schedule_report_request":
                await self._handle_schedule_request(message)
            else:
                # Update cached data and check if any reports need generation
                await self._check_scheduled_reports()
                
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            
    async def _handle_report_request(self, message: AgentMessage):
        """Handle ad-hoc report requests"""
        request = message.content
        report_type = request.get('report_type', 'custom')
        
        if report_type in self.report_templates:
            # Generate standard report
            report = await self._generate_report(report_type)
        else:
            # Generate custom report
            report = await self._generate_custom_report(request)
            
        # Send report back to requester
        response = AgentMessage(
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type="report_response",
            content=asdict(report)
        )
        await self.send_message(response)
        
        # Store in report history
        self.report_history.append(report)
        
    async def _handle_schedule_request(self, message: AgentMessage):
        """Handle report scheduling requests"""
        request = message.content
        report_type = request.get('report_type')
        frequency = request.get('frequency', 'monthly')
        recipients = request.get('recipients', [])
        
        if report_type:
            # Create or update scheduled report
            self.scheduled_reports[report_type] = {
                'template': self.report_templates.get(report_type, {}),
                'frequency': frequency,
                'recipients': recipients,
                'next_run': self._calculate_next_run(frequency),
                'enabled': True
            }
            
            self.logger.info(f"Scheduled {report_type} report with {frequency} frequency")
            
    async def _generate_report(self, report_type: str) -> Report:
        """Generate a standard report based on template"""
        template = self.report_templates[report_type]
        sections = []
        
        for section_name in template['sections']:
            section = await self._generate_section(section_name)
            if section:
                sections.append(section)
                
        # Generate executive summary
        executive_summary = await self._generate_executive_summary(sections)
        
        report = Report(
            report_id=f"{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=template['title'],
            sections=sections,
            generated_at=datetime.now(),
            report_type=report_type,
            recipients=template.get('recipients', []),
            executive_summary=executive_summary,
            metadata={
                'data_sources': list(self.data_cache.keys()),
                'generation_time': datetime.now().isoformat(),
                'template_version': '1.0'
            }
        )
        
        return report
        
    async def _generate_custom_report(self, request: Dict[str, Any]) -> Report:
        """Generate a custom report based on request parameters"""
        sections = []
        
        for section_config in request.get('sections', []):
            section = await self._generate_custom_section(section_config)
            if section:
                sections.append(section)
                
        executive_summary = await self._generate_executive_summary(sections)
        
        report = Report(
            report_id=f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=request.get('title', 'Custom Report'),
            sections=sections,
            generated_at=datetime.now(),
            report_type='custom',
            recipients=request.get('recipients', []),
            executive_summary=executive_summary,
            metadata={
                'custom_request': request,
                'generation_time': datetime.now().isoformat()
            }
        )
        
        return report
        
    async def _generate_section(self, section_name: str) -> Optional[ReportSection]:
        """Generate a report section based on cached data"""
        section_generators = {
            'revenue_analysis': self._generate_revenue_section,
            'cost_analysis': self._generate_cost_section,
            'profitability_metrics': self._generate_profitability_section,
            'cash_flow_status': self._generate_cash_flow_section,
            'budget_variance': self._generate_budget_variance_section,
            'financial_projections': self._generate_projections_section,
            'productivity_metrics': self._generate_productivity_section,
            'resource_utilization': self._generate_resource_section,
            'task_completion_rates': self._generate_task_completion_section,
            'workflow_efficiency': self._generate_workflow_section,
            'bottleneck_analysis': self._generate_bottleneck_section,
            'key_performance_indicators': self._generate_kpi_section,
            'financial_highlights': self._generate_financial_highlights_section,
            'operational_updates': self._generate_operational_updates_section,
            'market_insights': self._generate_market_insights_section,
            'strategic_recommendations': self._generate_strategic_recommendations_section,
            'risk_assessment': self._generate_risk_assessment_section,
            'compliance_status': self._generate_compliance_section,
            'audit_findings': self._generate_audit_section,
            'security_metrics': self._generate_security_section,
            'regulatory_updates': self._generate_regulatory_section,
            'market_trends': self._generate_market_trends_section,
            'competitor_analysis': self._generate_competitor_section,
            'customer_insights': self._generate_customer_section,
            'industry_analysis': self._generate_industry_section,
            'strategic_opportunities': self._generate_opportunities_section
        }
        
        generator = section_generators.get(section_name)
        if generator:
            return await generator()
        else:
            self.logger.warning(f"No generator found for section: {section_name}")
            return None
            
    async def _generate_revenue_section(self) -> ReportSection:
        """Generate revenue analysis section"""
        financial_data = self.data_cache.get('financial_data_update', {}).get('data', {})
        projections_data = self.data_cache.get('financial_projections_update', {}).get('data', {})
        
        content = {
            'current_revenue': financial_data.get('total_revenue', 0),
            'revenue_growth': financial_data.get('revenue_growth_rate', 0),
            'revenue_by_source': financial_data.get('revenue_breakdown', {}),
            'projections': projections_data.get('revenue_projections', {}),
            'variance_analysis': self._calculate_revenue_variance(financial_data),
            'trends': self._analyze_revenue_trends(financial_data)
        }
        
        return ReportSection(
            title="Revenue Analysis",
            content=content,
            visualization_type="charts_and_tables",
            priority=1,
            source_agent="financial_analysis_agent"
        )
        
    async def _generate_cost_section(self) -> ReportSection:
        """Generate cost analysis section"""
        financial_data = self.data_cache.get('financial_data_update', {}).get('data', {})
        
        content = {
            'total_costs': financial_data.get('total_costs', 0),
            'cost_breakdown': financial_data.get('cost_breakdown', {}),
            'cost_per_unit': financial_data.get('cost_per_unit', 0),
            'cost_trends': financial_data.get('cost_trends', []),
            'efficiency_metrics': financial_data.get('efficiency_metrics', {}),
            'cost_reduction_opportunities': self._identify_cost_savings(financial_data)
        }
        
        return ReportSection(
            title="Cost Analysis",
            content=content,
            visualization_type="charts_and_tables",
            priority=2,
            source_agent="financial_analysis_agent"
        )
        
    async def _generate_profitability_section(self) -> ReportSection:
        """Generate profitability metrics section"""
        financial_data = self.data_cache.get('financial_data_update', {}).get('data', {})
        
        revenue = financial_data.get('total_revenue', 0)
        costs = financial_data.get('total_costs', 0)
        profit = revenue - costs
        
        content = {
            'gross_profit': profit,
            'profit_margin': (profit / revenue * 100) if revenue > 0 else 0,
            'ebitda': financial_data.get('ebitda', 0),
            'net_income': financial_data.get('net_income', 0),
            'roi': financial_data.get('roi', 0),
            'profitability_trends': financial_data.get('profitability_trends', []),
            'benchmark_comparison': self._compare_to_benchmarks(financial_data)
        }
        
        return ReportSection(
            title="Profitability Metrics",
            content=content,
            visualization_type="kpi_dashboard",
            priority=1,
            source_agent="financial_analysis_agent"
        )
        
    async def _generate_cash_flow_section(self) -> ReportSection:
        """Generate cash flow status section"""
        projections_data = self.data_cache.get('financial_projections_update', {}).get('data', {})
        
        content = {
            'current_cash_position': projections_data.get('current_cash', 0),
            'cash_flow_projections': projections_data.get('cash_flow_projections', []),
            'burn_rate': projections_data.get('burn_rate', 0),
            'runway_months': projections_data.get('runway_months', 0),
            'cash_sources': projections_data.get('cash_sources', {}),
            'cash_uses': projections_data.get('cash_uses', {}),
            'liquidity_analysis': self._analyze_liquidity(projections_data)
        }
        
        return ReportSection(
            title="Cash Flow Status",
            content=content,
            visualization_type="waterfall_chart",
            priority=1,
            source_agent="financial_modeling_agent"
        )
        
    async def _generate_kpi_section(self) -> ReportSection:
        """Generate key performance indicators section"""
        # Aggregate KPIs from all data sources
        kpis = {}
        
        # Financial KPIs
        financial_data = self.data_cache.get('financial_data_update', {}).get('data', {})
        if financial_data:
            kpis.update({
                'revenue_growth': financial_data.get('revenue_growth_rate', 0),
                'profit_margin': financial_data.get('profit_margin', 0),
                'cash_position': financial_data.get('cash_position', 0)
            })
            
        # Operational KPIs
        operational_data = self.data_cache.get('operational_metrics_update', {}).get('data', {})
        if operational_data:
            kpis.update({
                'productivity_score': operational_data.get('productivity_score', 0),
                'efficiency_rating': operational_data.get('efficiency_rating', 0),
                'task_completion_rate': operational_data.get('completion_rate', 0)
            })
            
        # Market KPIs
        market_data = self.data_cache.get('market_analysis_update', {}).get('data', {})
        if market_data:
            kpis.update({
                'market_share': market_data.get('market_share', 0),
                'customer_satisfaction': market_data.get('customer_satisfaction', 0),
                'brand_sentiment': market_data.get('brand_sentiment', 0)
            })
        
        content = {
            'kpis': kpis,
            'targets': self._get_kpi_targets(),
            'performance_vs_target': self._calculate_kpi_performance(kpis),
            'trends': self._analyze_kpi_trends(kpis),
            'alerts': self._generate_kpi_alerts(kpis)
        }
        
        return ReportSection(
            title="Key Performance Indicators",
            content=content,
            visualization_type="kpi_dashboard",
            priority=1,
            source_agent="multiple"
        )
        
    async def _generate_executive_summary(self, sections: List[ReportSection]) -> str:
        """Generate executive summary from report sections"""
        summary_points = []
        
        # Extract key insights from each section
        for section in sections:
            if section.priority <= 2:  # Only include high-priority sections
                key_insight = self._extract_key_insight(section)
                if key_insight:
                    summary_points.append(key_insight)
                    
        # Format as executive summary
        if summary_points:
            summary = "Executive Summary:\n\n"
            for i, point in enumerate(summary_points, 1):
                summary += f"{i}. {point}\n"
        else:
            summary = "Executive Summary: No significant insights available for this reporting period."
            
        return summary
        
    def _extract_key_insight(self, section: ReportSection) -> Optional[str]:
        """Extract key insight from a report section"""
        if section.title == "Revenue Analysis":
            revenue = section.content.get('current_revenue', 0)
            growth = section.content.get('revenue_growth', 0)
            return f"Revenue stands at ${revenue:,.0f} with {growth:.1f}% growth"
            
        elif section.title == "Profitability Metrics":
            margin = section.content.get('profit_margin', 0)
            return f"Profit margin is {margin:.1f}%"
            
        elif section.title == "Cash Flow Status":
            cash = section.content.get('current_cash_position', 0)
            runway = section.content.get('runway_months', 0)
            return f"Cash position: ${cash:,.0f} with {runway:.0f} months runway"
            
        elif section.title == "Key Performance Indicators":
            alerts = section.content.get('alerts', [])
            if alerts:
                return f"KPI Alerts: {len(alerts)} metrics need attention"
                
        return None
        
    def _calculate_revenue_variance(self, financial_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate revenue variance analysis"""
        actual = financial_data.get('total_revenue', 0)
        budgeted = financial_data.get('budgeted_revenue', actual)
        
        variance = actual - budgeted
        variance_percent = (variance / budgeted * 100) if budgeted > 0 else 0
        
        return {
            'actual': actual,
            'budgeted': budgeted,
            'variance': variance,
            'variance_percent': variance_percent
        }
        
    def _analyze_revenue_trends(self, financial_data: Dict[str, Any]) -> List[str]:
        """Analyze revenue trends"""
        trends = []
        
        growth_rate = financial_data.get('revenue_growth_rate', 0)
        if growth_rate > 0.1:
            trends.append("Strong revenue growth trend")
        elif growth_rate < -0.05:
            trends.append("Declining revenue trend")
        else:
            trends.append("Stable revenue trend")
            
        return trends
        
    def _identify_cost_savings(self, financial_data: Dict[str, Any]) -> List[str]:
        """Identify cost reduction opportunities"""
        opportunities = []
        
        cost_breakdown = financial_data.get('cost_breakdown', {})
        for category, amount in cost_breakdown.items():
            if amount > financial_data.get('total_revenue', 0) * 0.3:
                opportunities.append(f"Review {category} costs - represents large expense")
                
        return opportunities
        
    def _compare_to_benchmarks(self, financial_data: Dict[str, Any]) -> Dict[str, str]:
        """Compare metrics to industry benchmarks"""
        # This would typically connect to external benchmark data
        profit_margin = financial_data.get('profit_margin', 0)
        
        benchmarks = {}
        if profit_margin > 20:
            benchmarks['profit_margin'] = "Above industry average"
        elif profit_margin < 10:
            benchmarks['profit_margin'] = "Below industry average"
        else:
            benchmarks['profit_margin'] = "Within industry range"
            
        return benchmarks
        
    def _analyze_liquidity(self, projections_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze liquidity position"""
        cash = projections_data.get('current_cash', 0)
        burn_rate = projections_data.get('burn_rate', 0)
        
        analysis = {
            'liquidity_status': 'healthy' if cash > burn_rate * 6 else 'concerning',
            'recommendations': []
        }
        
        if cash < burn_rate * 3:
            analysis['recommendations'].append("Consider immediate cash conservation measures")
        elif cash < burn_rate * 6:
            analysis['recommendations'].append("Monitor cash position closely")
            
        return analysis
        
    def _get_kpi_targets(self) -> Dict[str, float]:
        """Get KPI targets (would typically come from strategy/planning)"""
        return {
            'revenue_growth': 15.0,
            'profit_margin': 20.0,
            'productivity_score': 85.0,
            'efficiency_rating': 90.0,
            'task_completion_rate': 95.0,
            'customer_satisfaction': 90.0
        }
        
    def _calculate_kpi_performance(self, kpis: Dict[str, float]) -> Dict[str, str]:
        """Calculate KPI performance vs targets"""
        targets = self._get_kpi_targets()
        performance = {}
        
        for kpi, value in kpis.items():
            target = targets.get(kpi, 0)
            if value >= target:
                performance[kpi] = "On Target"
            elif value >= target * 0.9:
                performance[kpi] = "Near Target"
            else:
                performance[kpi] = "Below Target"
                
        return performance
        
    def _analyze_kpi_trends(self, kpis: Dict[str, float]) -> Dict[str, str]:
        """Analyze KPI trends (simplified - would use historical data)"""
        # This would typically analyze historical trends
        trends = {}
        for kpi in kpis.keys():
            trends[kpi] = "Stable"  # Placeholder
        return trends
        
    def _generate_kpi_alerts(self, kpis: Dict[str, float]) -> List[str]:
        """Generate alerts for KPIs that need attention"""
        alerts = []
        performance = self._calculate_kpi_performance(kpis)
        
        for kpi, status in performance.items():
            if status == "Below Target":
                alerts.append(f"{kpi} is below target")
                
        return alerts
        
    def _calculate_next_run(self, frequency: str) -> datetime:
        """Calculate next run time based on frequency"""
        now = datetime.now()
        
        if frequency == 'daily':
            return now + timedelta(days=1)
        elif frequency == 'weekly':
            return now + timedelta(days=7)
        elif frequency == 'monthly':
            return now + timedelta(days=30)
        elif frequency == 'quarterly':
            return now + timedelta(days=90)
        else:
            return now + timedelta(days=1)
            
    async def _check_scheduled_reports(self):
        """Check if any scheduled reports need to be generated"""
        now = datetime.now()
        
        for report_type, schedule in self.scheduled_reports.items():
            if schedule['enabled'] and schedule['next_run'] <= now:
                try:
                    # Generate the scheduled report
                    report = await self._generate_report(report_type)
                    
                    # Send to recipients
                    for recipient in schedule['template'].get('recipients', []):
                        message = AgentMessage(
                            sender_id=self.agent_id,
                            recipient_id=recipient,
                            message_type="scheduled_report",
                            content=asdict(report)
                        )
                        await self.send_message(message)
                    
                    # Update schedule
                    schedule['last_run'] = now
                    schedule['next_run'] = self._calculate_next_run(schedule.get('frequency', 'monthly'))
                    
                    self.logger.info(f"Generated scheduled report: {report_type}")
                    
                except Exception as e:
                    self.logger.error(f"Error generating scheduled report {report_type}: {str(e)}")

    async def get_status(self) -> Dict[str, Any]:
        """Get current status of the Report Generation Agent"""
        return {
            'agent_id': self.agent_id,
            'status': 'active',
            'templates_count': len(self.report_templates),
            'scheduled_reports': len(self.scheduled_reports),
            'data_sources': len(self.data_cache),
            'reports_generated': len(self.report_history),
            'next_scheduled_report': min(
                (schedule['next_run'] for schedule in self.scheduled_reports.values() if schedule['enabled']),
                default=None
            ).isoformat() if any(schedule['enabled'] for schedule in self.scheduled_reports.values()) else None
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

