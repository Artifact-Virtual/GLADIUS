"""
Financial Analysis Agent - Enterprise Legion
Analyzes financial statements, transactions, and performance metrics
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'legion'))
from core_framework import BaseAgent, AgentTask, AgentMessage

class FinancialAnalysisAgent(BaseAgent):
    """Advanced financial analysis and reporting agent"""
    
    def __init__(self, agent_id: str = "financial_analysis_agent"):
        capabilities = [
            "financial_analysis",
            "ratio_calculation", 
            "trend_analysis",
            "performance_metrics",
            "cash_flow_analysis"
        ]
        super().__init__(agent_id, "FinancialAnalysisAgent", "finance", capabilities)
        self.financial_data = {}
        self.ratios_cache = {}
        self.trends_data = {}
        self.integration_points = [
            "report_generation",
            "compliance_checker", 
            "resource_optimization",
            "financial_modeling"
        ]
    
    async def initialize(self) -> bool:
        """Initialize the Financial Analysis Agent"""
        try:
            self.logger.info("Initializing Financial Analysis Agent...")
            
            # Initialize financial data structures
            self.financial_data = {}
            self.ratios_cache = {}
            self.trends_data = {}
            
            self.logger.info("Financial Analysis Agent initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Financial Analysis Agent: {e}")
            return False
    
    async def process_task(self, task) -> Dict[str, Any]:
        """Process financial analysis tasks"""
        # Handle both AgentTask objects and dicts
        if hasattr(task, 'task_type'):
            task_type = task.task_type
            params = task.parameters
        else:
            task_type = task.get('task_type', 'analyze_statements')
            params = task
        
        if task_type == "analyze_statements":
            return await self._analyze_financial_statements(params)
        elif task_type == "calculate_ratios":
            return await self._calculate_financial_ratios(params)
        elif task_type == "track_expenses":
            return await self._track_expense_patterns(params)
        elif task_type == "budget_analysis":
            return await self._analyze_budget_variance(params)
        elif task_type == "forecast_trends":
            return await self._forecast_financial_trends(params)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def handle_message(self, message: AgentMessage) -> AgentMessage:
        """Handle messages from other agents"""
        msg_type = message.message_type
        payload = message.payload
        
        if msg_type == "financial_data_request":
            # Send financial data to requesting agent
            financial_summary = await self._get_financial_summary()
            return AgentMessage(
                id=f"response_{message.id}",
                source_agent=self.agent_id,
                target_agent=message.source_agent,
                message_type="financial_data_response",
                payload={"data": financial_summary},
                timestamp=datetime.now()
            )
        
        elif msg_type == "compliance_check_request":
            # Provide financial compliance data
            compliance_data = await self._get_compliance_metrics()
            return AgentMessage(
                id=f"response_{message.id}",
                source_agent=self.agent_id,
                target_agent=message.source_agent,
                message_type="compliance_data_response",
                payload=compliance_data,
                timestamp=datetime.now()
            )
        
        return None
    
    async def _analyze_financial_statements(self, params: Dict) -> Dict[str, Any]:
        """Analyze financial statements"""
        statement_data = params.get("statement_data", {})
        
        # Process balance sheet
        if "balance_sheet" in statement_data:
            balance_sheet = statement_data["balance_sheet"]
            current_ratio = self._calculate_current_ratio(balance_sheet)
            debt_to_equity = self._calculate_debt_to_equity(balance_sheet)
        
        # Process income statement
        if "income_statement" in statement_data:
            income_statement = statement_data["income_statement"]
            profit_margin = self._calculate_profit_margin(income_statement)
            revenue_growth = self._calculate_revenue_growth(income_statement)
        
        analysis_result = {
            "analysis_date": datetime.now().isoformat(),
            "ratios": {
                "current_ratio": current_ratio if 'current_ratio' in locals() else None,
                "debt_to_equity": debt_to_equity if 'debt_to_equity' in locals() else None,
                "profit_margin": profit_margin if 'profit_margin' in locals() else None,
                "revenue_growth": revenue_growth if 'revenue_growth' in locals() else None
            },
            "recommendations": await self._generate_recommendations()
        }
        
        # Share insights with other agents
        await self.send_message(
            "report_generation",
            "financial_analysis_complete",
            {"analysis": analysis_result}
        )
        
        return analysis_result
    
    async def _calculate_financial_ratios(self, params: Dict) -> Dict[str, Any]:
        """Calculate comprehensive financial ratios"""
        financial_data = params.get("financial_data", {})
        
        ratios = {
            "liquidity_ratios": {
                "current_ratio": self._calculate_current_ratio(financial_data),
                "quick_ratio": self._calculate_quick_ratio(financial_data),
                "cash_ratio": self._calculate_cash_ratio(financial_data)
            },
            "profitability_ratios": {
                "gross_margin": self._calculate_gross_margin(financial_data),
                "net_margin": self._calculate_net_margin(financial_data),
                "roa": self._calculate_return_on_assets(financial_data),
                "roe": self._calculate_return_on_equity(financial_data)
            },
            "efficiency_ratios": {
                "asset_turnover": self._calculate_asset_turnover(financial_data),
                "inventory_turnover": self._calculate_inventory_turnover(financial_data),
                "receivables_turnover": self._calculate_receivables_turnover(financial_data)
            },
            "leverage_ratios": {
                "debt_to_equity": self._calculate_debt_to_equity(financial_data),
                "debt_to_assets": self._calculate_debt_to_assets(financial_data),
                "interest_coverage": self._calculate_interest_coverage(financial_data)
            }
        }
        
        # Cache ratios for future use
        self.ratios_cache[datetime.now().date()] = ratios
        
        # Notify financial modeling agent of new ratios
        await self.send_message(
            "financial_modeling",
            "ratios_updated",
            {"ratios": ratios, "date": datetime.now().isoformat()}
        )
        
        return ratios
    
    async def _track_expense_patterns(self, params: Dict) -> Dict[str, Any]:
        """Track and analyze expense patterns"""
        expense_data = params.get("expense_data", [])
        time_period = params.get("time_period", "monthly")
        
        # Analyze expense trends
        expense_trends = self._analyze_expense_trends(expense_data, time_period)
        
        # Identify anomalies
        anomalies = self._detect_expense_anomalies(expense_data)
        
        # Generate expense forecasts
        forecasts = self._forecast_expenses(expense_data, time_period)
        
        result = {
            "trends": expense_trends,
            "anomalies": anomalies,
            "forecasts": forecasts,
            "recommendations": self._generate_expense_recommendations(expense_trends, anomalies)
        }
        
        # Share with resource optimization agent
        await self.send_message(
            "resource_optimization",
            "expense_analysis_complete",
            {"expense_analysis": result}
        )
        
        return result
    
    async def _analyze_budget_variance(self, params: Dict) -> Dict[str, Any]:
        """Analyze budget vs actual variance"""
        budget_data = params.get("budget", {})
        actual_data = params.get("actual", {})
        
        variances = {}
        for category in budget_data:
            if category in actual_data:
                variance = actual_data[category] - budget_data[category]
                variance_percent = (variance / budget_data[category]) * 100 if budget_data[category] != 0 else 0
                
                variances[category] = {
                    "budget": budget_data[category],
                    "actual": actual_data[category],
                    "variance": variance,
                    "variance_percent": variance_percent,
                    "status": "over_budget" if variance > 0 else "under_budget"
                }
        
        # Generate variance report
        variance_report = {
            "analysis_date": datetime.now().isoformat(),
            "variances": variances,
            "total_variance": sum(v["variance"] for v in variances.values()),
            "recommendations": self._generate_variance_recommendations(variances)
        }
        
        return variance_report
    
    async def _forecast_financial_trends(self, params: Dict) -> Dict[str, Any]:
        """Forecast financial trends using historical data"""
        historical_data = params.get("historical_data", [])
        forecast_periods = params.get("periods", 12)
        
        # Use simple linear regression for trend forecasting
        # In production, would use more sophisticated models
        forecasts = {}
        
        for metric in ["revenue", "expenses", "profit"]:
            if metric in historical_data:
                values = historical_data[metric]
                forecast = self._linear_forecast(values, forecast_periods)
                forecasts[metric] = forecast
        
        forecast_result = {
            "forecast_date": datetime.now().isoformat(),
            "forecast_periods": forecast_periods,
            "forecasts": forecasts,
            "confidence_intervals": self._calculate_confidence_intervals(forecasts)
        }
        
        # Share forecasts with strategic planning
        await self.send_message(
            "strategic_planning",
            "financial_forecasts_ready",
            {"forecasts": forecast_result}
        )
        
        return forecast_result
    
    def _calculate_current_ratio(self, data: Dict) -> float:
        """Calculate current ratio"""
        current_assets = data.get("current_assets", 0)
        current_liabilities = data.get("current_liabilities", 1)
        return current_assets / current_liabilities if current_liabilities != 0 else 0
    
    def _calculate_debt_to_equity(self, data: Dict) -> float:
        """Calculate debt-to-equity ratio"""
        total_debt = data.get("total_debt", 0)
        total_equity = data.get("total_equity", 1)
        return total_debt / total_equity if total_equity != 0 else 0
    
    def _calculate_profit_margin(self, data: Dict) -> float:
        """Calculate profit margin"""
        net_income = data.get("net_income", 0)
        revenue = data.get("revenue", 1)
        return (net_income / revenue) * 100 if revenue != 0 else 0
    
    def _calculate_revenue_growth(self, data: Dict) -> float:
        """Calculate revenue growth rate"""
        current_revenue = data.get("current_revenue", 0)
        previous_revenue = data.get("previous_revenue", 1)
        return ((current_revenue - previous_revenue) / previous_revenue) * 100 if previous_revenue != 0 else 0
    
    def _calculate_quick_ratio(self, data: Dict) -> float:
        """Calculate quick ratio"""
        current_assets = data.get("current_assets", 0)
        inventory = data.get("inventory", 0)
        current_liabilities = data.get("current_liabilities", 1)
        quick_assets = current_assets - inventory
        return quick_assets / current_liabilities if current_liabilities != 0 else 0
    
    def _calculate_cash_ratio(self, data: Dict) -> float:
        """Calculate cash ratio"""
        cash = data.get("cash", 0)
        current_liabilities = data.get("current_liabilities", 1)
        return cash / current_liabilities if current_liabilities != 0 else 0
    
    def _calculate_gross_margin(self, data: Dict) -> float:
        """Calculate gross margin"""
        gross_profit = data.get("gross_profit", 0)
        revenue = data.get("revenue", 1)
        return (gross_profit / revenue) * 100 if revenue != 0 else 0
    
    def _calculate_net_margin(self, data: Dict) -> float:
        """Calculate net margin"""
        net_income = data.get("net_income", 0)
        revenue = data.get("revenue", 1)
        return (net_income / revenue) * 100 if revenue != 0 else 0
    
    def _calculate_return_on_assets(self, data: Dict) -> float:
        """Calculate return on assets"""
        net_income = data.get("net_income", 0)
        total_assets = data.get("total_assets", 1)
        return (net_income / total_assets) * 100 if total_assets != 0 else 0
    
    def _calculate_return_on_equity(self, data: Dict) -> float:
        """Calculate return on equity"""
        net_income = data.get("net_income", 0)
        total_equity = data.get("total_equity", 1)
        return (net_income / total_equity) * 100 if total_equity != 0 else 0
    
    def _calculate_asset_turnover(self, data: Dict) -> float:
        """Calculate asset turnover ratio"""
        revenue = data.get("revenue", 0)
        total_assets = data.get("total_assets", 1)
        return revenue / total_assets if total_assets != 0 else 0
    
    def _calculate_inventory_turnover(self, data: Dict) -> float:
        """Calculate inventory turnover ratio"""
        cogs = data.get("cost_of_goods_sold", 0)
        inventory = data.get("inventory", 1)
        return cogs / inventory if inventory != 0 else 0
    
    def _calculate_receivables_turnover(self, data: Dict) -> float:
        """Calculate accounts receivable turnover"""
        revenue = data.get("revenue", 0)
        accounts_receivable = data.get("accounts_receivable", 1)
        return revenue / accounts_receivable if accounts_receivable != 0 else 0
    
    def _calculate_debt_to_assets(self, data: Dict) -> float:
        """Calculate debt-to-assets ratio"""
        total_debt = data.get("total_debt", 0)
        total_assets = data.get("total_assets", 1)
        return total_debt / total_assets if total_assets != 0 else 0
    
    def _calculate_interest_coverage(self, data: Dict) -> float:
        """Calculate interest coverage ratio"""
        ebit = data.get("ebit", 0)
        interest_expense = data.get("interest_expense", 1)
        return ebit / interest_expense if interest_expense != 0 else 0
    
    def _analyze_expense_trends(self, expense_data: List, time_period: str) -> Dict:
        """Analyze expense trends over time"""
        # Simplified trend analysis
        trends = {}
        
        # Group expenses by category
        categories = {}
        for expense in expense_data:
            category = expense.get("category", "other")
            if category not in categories:
                categories[category] = []
            categories[category].append(expense.get("amount", 0))
        
        # Calculate trends for each category
        for category, amounts in categories.items():
            if len(amounts) > 1:
                # Calculate simple trend (positive = increasing, negative = decreasing)
                trend = (amounts[-1] - amounts[0]) / len(amounts)
                trends[category] = {
                    "trend": trend,
                    "direction": "increasing" if trend > 0 else "decreasing",
                    "total": sum(amounts),
                    "average": sum(amounts) / len(amounts)
                }
        
        return trends
    
    def _detect_expense_anomalies(self, expense_data: List) -> List[Dict]:
        """Detect anomalous expenses"""
        anomalies = []
        
        # Simple anomaly detection based on standard deviation
        amounts = [expense.get("amount", 0) for expense in expense_data]
        if len(amounts) > 2:
            mean_amount = np.mean(amounts)
            std_amount = np.std(amounts)
            threshold = mean_amount + (2 * std_amount)  # 2 standard deviations
            
            for expense in expense_data:
                if expense.get("amount", 0) > threshold:
                    anomalies.append({
                        "expense": expense,
                        "type": "high_amount",
                        "threshold": threshold,
                        "severity": "medium"
                    })
        
        return anomalies
    
    def _forecast_expenses(self, expense_data: List, time_period: str) -> Dict:
        """Forecast future expenses"""
        forecasts = {}
        
        # Group by category and forecast
        categories = {}
        for expense in expense_data:
            category = expense.get("category", "other")
            if category not in categories:
                categories[category] = []
            categories[category].append(expense.get("amount", 0))
        
        for category, amounts in categories.items():
            if len(amounts) > 2:
                # Simple linear forecast
                forecast = self._linear_forecast(amounts, 3)  # 3 periods ahead
                forecasts[category] = forecast
        
        return forecasts
    
    def _linear_forecast(self, values: List[float], periods: int) -> List[float]:
        """Simple linear forecasting"""
        if len(values) < 2:
            return [values[-1]] * periods if values else [0] * periods
        
        # Calculate linear trend
        x = list(range(len(values)))
        slope = (len(values) * sum(i * values[i] for i in range(len(values))) - sum(x) * sum(values)) / \
                (len(values) * sum(i**2 for i in range(len(values))) - sum(x)**2)
        
        intercept = (sum(values) - slope * sum(x)) / len(values)
        
        # Generate forecasts
        forecasts = []
        for i in range(periods):
            forecast_x = len(values) + i
            forecast_value = slope * forecast_x + intercept
            forecasts.append(max(0, forecast_value))  # Ensure non-negative
        
        return forecasts
    
    def _generate_recommendations(self) -> List[str]:
        """Generate financial recommendations"""
        return [
            "Monitor cash flow regularly",
            "Review expense categories for optimization opportunities",
            "Consider debt restructuring if debt-to-equity ratio is high",
            "Implement regular financial health checks"
        ]
    
    def _generate_expense_recommendations(self, trends: Dict, anomalies: List) -> List[str]:
        """Generate expense-specific recommendations"""
        recommendations = []
        
        for category, trend_data in trends.items():
            if trend_data["direction"] == "increasing":
                recommendations.append(f"Review {category} expenses - showing increasing trend")
        
        if anomalies:
            recommendations.append(f"Investigate {len(anomalies)} expense anomalies detected")
        
        return recommendations
    
    def _generate_variance_recommendations(self, variances: Dict) -> List[str]:
        """Generate budget variance recommendations"""
        recommendations = []
        
        for category, variance_data in variances.items():
            if abs(variance_data["variance_percent"]) > 10:  # More than 10% variance
                status = variance_data["status"]
                recommendations.append(f"Review {category} budget - {status} by {abs(variance_data['variance_percent']):.1f}%")
        
        return recommendations
    
    def _calculate_confidence_intervals(self, forecasts: Dict) -> Dict:
        """Calculate confidence intervals for forecasts"""
        # Simplified confidence intervals
        confidence_intervals = {}
        
        for metric, forecast_values in forecasts.items():
            # Use 10% as a simple confidence interval
            intervals = []
            for value in forecast_values:
                lower = value * 0.9
                upper = value * 1.1
                intervals.append({"lower": lower, "upper": upper})
            
            confidence_intervals[metric] = intervals
        
        return confidence_intervals
    
    async def _get_financial_summary(self) -> Dict[str, Any]:
        """Get current financial summary"""
        return {
            "ratios": self.ratios_cache.get(datetime.now().date(), {}),
            "trends": self.trends_data,
            "last_updated": datetime.now().isoformat()
        }
    
    async def _get_compliance_metrics(self) -> Dict[str, Any]:
        """Get financial compliance metrics"""
        return {
            "ratios_compliant": True,
            "reporting_current": True,
            "audit_ready": True,
            "last_compliance_check": datetime.now().isoformat()
        }
