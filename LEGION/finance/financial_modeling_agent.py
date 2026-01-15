"""
Financial Modeling Agent - Enterprise Legion Framework
Build predictive financial models and scenario planning
"""

import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import uuid
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core_framework import BaseAgent, AgentMessage


@dataclass
class FinancialScenario:
    """Financial scenario data structure"""
    name: str
    parameters: Dict[str, float]
    probability: float
    projected_revenue: float
    projected_costs: float
    projected_profit: float
    risk_factors: List[str]
    timeline: str


@dataclass
class CashFlowProjection:
    """Cash flow projection data structure"""
    period: str
    cash_inflow: float
    cash_outflow: float
    net_cash_flow: float
    cumulative_cash_flow: float
    confidence_interval: tuple


class FinancialModelingAgent(BaseAgent):
    """
    Financial Modeling Agent for predictive financial analysis and
    scenario planning. Builds and updates financial models for
    forecasting and risk assessment.
    """
    
    def __init__(self, agent_id: str = "financialmodelingagent"):
        capabilities = ["financial_modeling", "forecasting"]
        super().__init__(agent_id, "FinancialModelingAgent", "finance", capabilities)
        self.models = {}
        self.scenarios = {}
        self.projections = {}
        self.market_data = {}
        self.risk_parameters = {
            'market_volatility': 0.15,
            'economic_uncertainty': 0.10,
            'competitive_pressure': 0.08,
            'regulatory_risk': 0.05
        }
        
    async def initialize(self):
        """Initialize the agent with default models and scenarios"""
        await super().initialize()
        
        # Initialize default financial models
        self._create_default_models()
        self._create_base_scenarios()
        
        # Subscribe to relevant message types
        await self.subscribe_to_messages([
            "market_data_update",
            "financial_data_update",
            "scenario_request",
            "model_update_request",
            "projection_request"
        ])
        
        self.logger.info("Financial Modeling Agent initialized with default models")
        
    def _create_default_models(self):
        """Create default financial models"""
        self.models = {
            'dcf_model': {
                'type': 'discounted_cash_flow',
                'parameters': {
                    'discount_rate': 0.10,
                    'growth_rate': 0.03,
                    'terminal_growth': 0.02
                },
                'last_updated': datetime.now()
            },
            'budget_model': {
                'type': 'budget_forecasting',
                'parameters': {
                    'seasonal_factors': [1.0, 0.9, 1.1, 1.2, 1.0, 0.8, 0.7, 0.8, 1.1, 1.3, 1.4, 1.2],
                    'growth_assumptions': 0.05
                },
                'last_updated': datetime.now()
            },
            'risk_model': {
                'type': 'monte_carlo_simulation',
                'parameters': {
                    'simulations': 10000,
                    'volatility': 0.20,
                    'confidence_levels': [0.95, 0.90, 0.80]
                },
                'last_updated': datetime.now()
            }
        }
        
    def _create_base_scenarios(self):
        """Create base financial scenarios"""
        self.scenarios = {
            'optimistic': FinancialScenario(
                name="Optimistic Growth",
                parameters={'revenue_growth': 0.15, 'cost_inflation': 0.03},
                probability=0.25,
                projected_revenue=1500000,
                projected_costs=900000,
                projected_profit=600000,
                risk_factors=['market_saturation'],
                timeline="12_months"
            ),
            'base_case': FinancialScenario(
                name="Base Case",
                parameters={'revenue_growth': 0.08, 'cost_inflation': 0.05},
                probability=0.50,
                projected_revenue=1200000,
                projected_costs=800000,
                projected_profit=400000,
                risk_factors=['competition', 'economic_slowdown'],
                timeline="12_months"
            ),
            'pessimistic': FinancialScenario(
                name="Pessimistic",
                parameters={'revenue_growth': -0.05, 'cost_inflation': 0.08},
                probability=0.25,
                projected_revenue=900000,
                projected_costs=750000,
                projected_profit=150000,
                risk_factors=['recession', 'supply_chain_disruption', 'regulatory_changes'],
                timeline="12_months"
            )
        }

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process assigned tasks"""
        try:
            task_type = task.get('type', 'unknown')
            
            if task_type == 'generate_financial_model':
                model_type = task.get('model_type', 'dcf_model')
                parameters = task.get('parameters', {})
                result = await self._generate_financial_model(model_type, parameters)
                return {"status": "completed", "result": result}
            
            elif task_type == 'create_scenario':
                scenario_params = task.get('scenario_params', {})
                scenario = await self._create_custom_scenario(scenario_params)
                self.scenarios[scenario.name] = scenario
                return {"status": "completed", "scenario": scenario.name}
            
            elif task_type == 'run_projections':
                months = task.get('months', 12)
                projections = await self._generate_comprehensive_projections(months)
                return {"status": "completed", "projections": projections}
            
            elif task_type == 'analyze_risk':
                risk_analysis = await self._generate_risk_projections()
                return {"status": "completed", "risk_analysis": risk_analysis}
            
            else:
                return {"status": "failed", "error": f"Unknown task type: {task_type}"}
                
        except Exception as e:
            self.logger.error(f"Error processing task: {str(e)}")
            return {"status": "failed", "error": str(e)}

    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle incoming messages from other agents"""
        try:
            await self.process_message(message)
            
            # Return response for scenario requests
            if message.message_type == "scenario_request":
                response = AgentMessage(
                    id=str(uuid.uuid4()),
                    source_agent=self.agent_id,
                    target_agent=message.source_agent,
                    message_type="scenario_response",
                    payload={"scenarios": list(self.scenarios.keys())},
                    timestamp=datetime.now()
                )
                return response
                
            self.performance_metrics["messages_processed"] += 1
            return None
            
        except Exception as e:
            self.logger.error(f"Error handling message: {str(e)}")
            self.performance_metrics["errors"] += 1
            return None

    async def process_message(self, message: AgentMessage):
        """Process incoming messages"""
        try:
            if message.message_type == "market_data_update":
                await self._handle_market_data_update(message)
            elif message.message_type == "financial_data_update":
                await self._handle_financial_data_update(message)
            elif message.message_type == "scenario_request":
                await self._handle_scenario_request(message)
            elif message.message_type == "model_update_request":
                await self._handle_model_update_request(message)
            elif message.message_type == "projection_request":
                await self._handle_projection_request(message)
                
        except Exception as e:
            self.logger.error(f"Error processing message {message.message_type}: {str(e)}")
            
    async def _handle_market_data_update(self, message: AgentMessage):
        """Handle market data updates from Market Analysis Agent"""
        market_data = message.content
        self.market_data.update(market_data)
        
        # Update model parameters based on market conditions
        if 'market_volatility' in market_data:
            self.risk_parameters['market_volatility'] = market_data['market_volatility']
            
        if 'economic_indicators' in market_data:
            await self._update_economic_assumptions(market_data['economic_indicators'])
            
        # Recalculate scenarios with new market data
        await self._recalculate_scenarios()
        
        self.logger.info("Updated financial models with new market data")
        
    async def _handle_financial_data_update(self, message: AgentMessage):
        """Handle financial data updates"""
        financial_data = message.content
        
        # Update historical data for model calibration
        await self._calibrate_models(financial_data)
        
        # Generate updated projections
        projections = await self._generate_projections()
        
        # Send updated projections to interested agents
        await self.send_message(AgentMessage(
            sender_id=self.agent_id,
            recipient_id="report_generation_agent",
            message_type="financial_projections_update",
            content=projections
        ))
        
    async def _handle_scenario_request(self, message: AgentMessage):
        """Handle requests for scenario analysis"""
        request_params = message.content
        scenario_name = request_params.get('scenario', 'base_case')
        
        if scenario_name in self.scenarios:
            scenario = self.scenarios[scenario_name]
            
            # Generate detailed scenario analysis
            analysis = await self._analyze_scenario(scenario)
            
            response = AgentMessage(
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type="scenario_analysis_response",
                content=analysis
            )
            await self.send_message(response)
        else:
            # Create custom scenario if parameters provided
            if 'parameters' in request_params:
                custom_scenario = await self._create_custom_scenario(request_params)
                analysis = await self._analyze_scenario(custom_scenario)
                
                response = AgentMessage(
                    sender_id=self.agent_id,
                    recipient_id=message.sender_id,
                    message_type="scenario_analysis_response",
                    content=analysis
                )
                await self.send_message(response)
                
    async def _handle_model_update_request(self, message: AgentMessage):
        """Handle requests to update model parameters"""
        update_params = message.content
        model_type = update_params.get('model_type')
        
        if model_type in self.models:
            self.models[model_type]['parameters'].update(update_params.get('parameters', {}))
            self.models[model_type]['last_updated'] = datetime.now()
            
            # Recalculate projections with updated model
            await self._recalculate_scenarios()
            
            self.logger.info(f"Updated {model_type} model parameters")
            
    async def _handle_projection_request(self, message: AgentMessage):
        """Handle requests for financial projections"""
        request_params = message.content
        projection_type = request_params.get('type', 'cash_flow')
        time_horizon = request_params.get('time_horizon', 12)
        
        if projection_type == 'cash_flow':
            projections = await self._generate_cash_flow_projections(time_horizon)
        elif projection_type == 'revenue':
            projections = await self._generate_revenue_projections(time_horizon)
        elif projection_type == 'risk_analysis':
            projections = await self._generate_risk_projections()
        else:
            projections = await self._generate_comprehensive_projections(time_horizon)
            
        response = AgentMessage(
            sender_id=self.agent_id,
            recipient_id=message.sender_id,
            message_type="projection_response",
            content=projections
        )
        await self.send_message(response)
        
    async def _generate_cash_flow_projections(self, months: int) -> List[CashFlowProjection]:
        """Generate cash flow projections"""
        projections = []
        base_inflow = 100000  # Base monthly cash inflow
        base_outflow = 80000  # Base monthly cash outflow
        cumulative = 0
        
        for month in range(1, months + 1):
            # Apply seasonal factors and growth
            seasonal_factor = self.models['budget_model']['parameters']['seasonal_factors'][(month - 1) % 12]
            growth_factor = (1 + self.models['budget_model']['parameters']['growth_assumptions']) ** (month / 12)
            
            inflow = base_inflow * seasonal_factor * growth_factor
            outflow = base_outflow * growth_factor * (1 + self.risk_parameters['market_volatility'] * np.random.normal(0, 0.1))
            
            net_flow = inflow - outflow
            cumulative += net_flow
            
            # Calculate confidence interval
            volatility = self.risk_parameters['market_volatility']
            confidence_interval = (
                net_flow * (1 - 1.96 * volatility),
                net_flow * (1 + 1.96 * volatility)
            )
            
            projection = CashFlowProjection(
                period=f"Month_{month}",
                cash_inflow=inflow,
                cash_outflow=outflow,
                net_cash_flow=net_flow,
                cumulative_cash_flow=cumulative,
                confidence_interval=confidence_interval
            )
            projections.append(projection)
            
        return projections
        
    async def _generate_revenue_projections(self, months: int) -> Dict[str, Any]:
        """Generate revenue projections"""
        base_revenue = 120000  # Base monthly revenue
        projections = {}
        
        for scenario_name, scenario in self.scenarios.items():
            monthly_revenues = []
            growth_rate = scenario.parameters.get('revenue_growth', 0.05) / 12
            
            for month in range(1, months + 1):
                # Apply growth and seasonal factors
                seasonal_factor = self.models['budget_model']['parameters']['seasonal_factors'][(month - 1) % 12]
                monthly_revenue = base_revenue * (1 + growth_rate) ** month * seasonal_factor
                monthly_revenues.append({
                    'month': month,
                    'revenue': monthly_revenue,
                    'scenario': scenario_name
                })
                
            projections[scenario_name] = {
                'monthly_projections': monthly_revenues,
                'total_projected': sum(r['revenue'] for r in monthly_revenues),
                'probability': scenario.probability
            }
            
        return projections
        
    async def _generate_risk_projections(self) -> Dict[str, Any]:
        """Generate risk analysis projections"""
        monte_carlo_results = await self._run_monte_carlo_simulation()
        
        risk_analysis = {
            'value_at_risk': {
                '95%': np.percentile(monte_carlo_results, 5),
                '90%': np.percentile(monte_carlo_results, 10),
                '80%': np.percentile(monte_carlo_results, 20)
            },
            'expected_return': np.mean(monte_carlo_results),
            'volatility': np.std(monte_carlo_results),
            'risk_factors': self.risk_parameters,
            'scenario_probabilities': {name: scenario.probability for name, scenario in self.scenarios.items()},
            'stress_test_results': await self._run_stress_tests()
        }
        
        return risk_analysis
        
    async def _run_monte_carlo_simulation(self) -> np.ndarray:
        """Run Monte Carlo simulation for risk analysis"""
        num_simulations = self.models['risk_model']['parameters']['simulations']
        volatility = self.models['risk_model']['parameters']['volatility']
        
        # Generate random returns based on scenarios
        results = []
        for _ in range(num_simulations):
            # Select scenario based on probabilities
            scenario = np.random.choice(
                list(self.scenarios.keys()),
                p=[s.probability for s in self.scenarios.values()]
            )
            
            # Generate return with volatility
            base_return = self.scenarios[scenario].projected_profit
            random_factor = np.random.normal(1, volatility)
            simulation_result = base_return * random_factor
            results.append(simulation_result)
            
        return np.array(results)
        
    async def _run_stress_tests(self) -> Dict[str, float]:
        """Run stress tests on financial models"""
        stress_scenarios = {
            'market_crash': {'revenue_shock': -0.30, 'cost_shock': 0.20},
            'recession': {'revenue_shock': -0.15, 'cost_shock': 0.10},
            'supply_disruption': {'revenue_shock': -0.10, 'cost_shock': 0.25},
            'regulatory_change': {'revenue_shock': -0.05, 'cost_shock': 0.15}
        }
        
        stress_results = {}
        base_profit = self.scenarios['base_case'].projected_profit
        
        for scenario_name, shocks in stress_scenarios.items():
            stressed_revenue = self.scenarios['base_case'].projected_revenue * (1 + shocks['revenue_shock'])
            stressed_costs = self.scenarios['base_case'].projected_costs * (1 + shocks['cost_shock'])
            stressed_profit = stressed_revenue - stressed_costs
            
            stress_results[scenario_name] = {
                'profit_impact': stressed_profit - base_profit,
                'profit_change_percent': ((stressed_profit - base_profit) / base_profit) * 100,
                'stressed_profit': stressed_profit
            }
            
        return stress_results
        
    async def _analyze_scenario(self, scenario: FinancialScenario) -> Dict[str, Any]:
        """Analyze a specific financial scenario"""
        analysis = {
            'scenario_name': scenario.name,
            'probability': scenario.probability,
            'financial_metrics': {
                'projected_revenue': scenario.projected_revenue,
                'projected_costs': scenario.projected_costs,
                'projected_profit': scenario.projected_profit,
                'profit_margin': (scenario.projected_profit / scenario.projected_revenue) * 100,
                'roi': (scenario.projected_profit / scenario.projected_costs) * 100
            },
            'risk_assessment': {
                'risk_factors': scenario.risk_factors,
                'risk_score': len(scenario.risk_factors) * 0.1,
                'mitigation_strategies': await self._generate_mitigation_strategies(scenario.risk_factors)
            },
            'cash_flow_impact': await self._calculate_scenario_cash_flow(scenario),
            'timeline': scenario.timeline,
            'confidence_level': 0.95 - (len(scenario.risk_factors) * 0.05)
        }
        
        return analysis
        
    async def _generate_mitigation_strategies(self, risk_factors: List[str]) -> Dict[str, List[str]]:
        """Generate mitigation strategies for risk factors"""
        mitigation_map = {
            'market_saturation': [
                'Develop new market segments',
                'Enhance product differentiation',
                'Expand to new geographic markets'
            ],
            'competition': [
                'Strengthen competitive advantages',
                'Improve customer retention programs',
                'Accelerate innovation cycles'
            ],
            'economic_slowdown': [
                'Diversify revenue streams',
                'Optimize cost structure',
                'Build cash reserves'
            ],
            'recession': [
                'Focus on essential products/services',
                'Implement cost reduction measures',
                'Maintain strong balance sheet'
            ],
            'supply_chain_disruption': [
                'Diversify supplier base',
                'Build strategic inventory',
                'Develop alternative sourcing'
            ],
            'regulatory_changes': [
                'Monitor regulatory developments',
                'Engage with regulatory bodies',
                'Build compliance capabilities'
            ]
        }
        
        strategies = {}
        for risk_factor in risk_factors:
            strategies[risk_factor] = mitigation_map.get(risk_factor, ['Monitor and assess impact'])
            
        return strategies
        
    async def _calculate_scenario_cash_flow(self, scenario: FinancialScenario) -> Dict[str, float]:
        """Calculate cash flow impact for a scenario"""
        monthly_revenue = scenario.projected_revenue / 12
        monthly_costs = scenario.projected_costs / 12
        monthly_net = monthly_revenue - monthly_costs
        
        return {
            'monthly_net_cash_flow': monthly_net,
            'quarterly_net_cash_flow': monthly_net * 3,
            'annual_net_cash_flow': monthly_net * 12,
            'break_even_months': abs(monthly_costs / monthly_net) if monthly_net != 0 else float('inf')
        }
        
    async def _update_economic_assumptions(self, economic_indicators: Dict[str, float]):
        """Update economic assumptions based on indicators"""
        if 'gdp_growth' in economic_indicators:
            # Adjust growth assumptions based on GDP growth
            gdp_growth = economic_indicators['gdp_growth']
            self.models['budget_model']['parameters']['growth_assumptions'] = max(0, gdp_growth * 0.8)
            
        if 'interest_rate' in economic_indicators:
            # Adjust discount rate based on interest rates
            interest_rate = economic_indicators['interest_rate']
            self.models['dcf_model']['parameters']['discount_rate'] = interest_rate + 0.05
            
        if 'inflation_rate' in economic_indicators:
            # Adjust cost inflation assumptions
            inflation_rate = economic_indicators['inflation_rate']
            for scenario in self.scenarios.values():
                scenario.parameters['cost_inflation'] = inflation_rate
                
    async def _calibrate_models(self, financial_data: Dict[str, Any]):
        """Calibrate models based on historical financial data"""
        if 'historical_revenues' in financial_data:
            revenues = financial_data['historical_revenues']
            if len(revenues) >= 12:
                # Calculate seasonal factors from historical data
                avg_revenue = sum(revenues) / len(revenues)
                seasonal_factors = [r / avg_revenue for r in revenues[-12:]]
                self.models['budget_model']['parameters']['seasonal_factors'] = seasonal_factors
                
        if 'historical_volatility' in financial_data:
            volatility = financial_data['historical_volatility']
            self.models['risk_model']['parameters']['volatility'] = volatility
            
    async def _recalculate_scenarios(self):
        """Recalculate all scenarios with updated parameters"""
        for scenario_name, scenario in self.scenarios.items():
            # Update scenario projections based on current model parameters
            growth_rate = self.models['budget_model']['parameters']['growth_assumptions']
            base_revenue = scenario.projected_revenue / (1 + scenario.parameters.get('revenue_growth', 0))
            
            scenario.projected_revenue = base_revenue * (1 + growth_rate)
            scenario.projected_costs = scenario.projected_costs * (1 + scenario.parameters.get('cost_inflation', 0.05))
            scenario.projected_profit = scenario.projected_revenue - scenario.projected_costs
            
        self.logger.info("Recalculated all financial scenarios")
        
    async def _create_custom_scenario(self, params: Dict[str, Any]) -> FinancialScenario:
        """Create a custom financial scenario"""
        return FinancialScenario(
            name=params.get('name', 'Custom Scenario'),
            parameters=params.get('parameters', {}),
            probability=params.get('probability', 0.5),
            projected_revenue=params.get('projected_revenue', 1000000),
            projected_costs=params.get('projected_costs', 700000),
            projected_profit=params.get('projected_revenue', 1000000) - params.get('projected_costs', 700000),
            risk_factors=params.get('risk_factors', []),
            timeline=params.get('timeline', '12_months')
        )
        
    async def _generate_comprehensive_projections(self, months: int) -> Dict[str, Any]:
        """Generate comprehensive financial projections"""
        cash_flow = await self._generate_cash_flow_projections(months)
        revenue = await self._generate_revenue_projections(months)
        risk = await self._generate_risk_projections()
        
        return {
            'cash_flow_projections': [
                {
                    'period': cf.period,
                    'net_cash_flow': cf.net_cash_flow,
                    'cumulative_cash_flow': cf.cumulative_cash_flow,
                    'confidence_interval': cf.confidence_interval
                } for cf in cash_flow
            ],
            'revenue_projections': revenue,
            'risk_analysis': risk,
            'model_assumptions': {model: params['parameters'] for model, params in self.models.items()},
            'last_updated': datetime.now().isoformat()
        }

    async def get_status(self) -> Dict[str, Any]:
        """Get current status of the Financial Modeling Agent"""
        return {
            'agent_id': self.agent_id,
            'status': 'active',
            'models_count': len(self.models),
            'scenarios_count': len(self.scenarios),
            'last_model_update': max(model['last_updated'] for model in self.models.values()).isoformat(),
            'risk_parameters': self.risk_parameters,
            'market_data_age': (datetime.now() - datetime.fromisoformat(
                self.market_data.get('timestamp', datetime.now().isoformat())
            )).total_seconds() / 3600 if self.market_data else None
        }

    async def _generate_financial_model(self, model_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a financial model based on type and parameters"""
        if model_type == 'dcf_model':
            return await self._generate_dcf_model(parameters)
        elif model_type == 'budget_model':
            return await self._generate_budget_model(parameters)
        elif model_type == 'risk_model':
            return await self._generate_risk_model(parameters)
        else:
            raise ValueError(f"Unknown model type: {model_type}")

    async def _generate_dcf_model(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a DCF (Discounted Cash Flow) model"""
        discount_rate = parameters.get('discount_rate', 0.10)
        growth_rate = parameters.get('growth_rate', 0.03)
        terminal_growth = parameters.get('terminal_growth', 0.02)
        
        # Simple DCF calculation
        cash_flows = []
        for year in range(1, 6):
            cf = 100000 * (1 + growth_rate) ** year
            pv = cf / (1 + discount_rate) ** year
            cash_flows.append({'year': year, 'cash_flow': cf, 'present_value': pv})
        
        terminal_value = cash_flows[-1]['cash_flow'] * (1 + terminal_growth) / (discount_rate - terminal_growth)
        total_value = sum(cf['present_value'] for cf in cash_flows) + terminal_value / (1 + discount_rate) ** 5
        
        return {
            'model_type': 'dcf',
            'cash_flows': cash_flows,
            'terminal_value': terminal_value,
            'total_enterprise_value': total_value,
            'parameters': parameters
        }

    async def _generate_budget_model(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a budget forecasting model"""
        growth_rate = parameters.get('growth_rate', 0.05)
        seasonal_factors = parameters.get('seasonal_factors', [1.0] * 12)
        
        base_revenue = 100000
        budget_forecast = []
        
        for month in range(12):
            monthly_revenue = base_revenue * (1 + growth_rate) * seasonal_factors[month % len(seasonal_factors)]
            budget_forecast.append({
                'month': month + 1,
                'revenue': monthly_revenue,
                'costs': monthly_revenue * 0.7,
                'profit': monthly_revenue * 0.3
            })
        
        return {
            'model_type': 'budget',
            'forecast': budget_forecast,
            'total_revenue': sum(b['revenue'] for b in budget_forecast),
            'total_profit': sum(b['profit'] for b in budget_forecast),
            'parameters': parameters
        }

    async def _generate_risk_model(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a risk assessment model"""
        volatility = parameters.get('volatility', 0.20)
        simulations = parameters.get('simulations', 1000)
        
        # Monte Carlo simulation
        results = np.random.normal(100000, 100000 * volatility, simulations)
        
        return {
            'model_type': 'risk',
            'mean_outcome': float(np.mean(results)),
            'std_deviation': float(np.std(results)),
            'percentile_5': float(np.percentile(results, 5)),
            'percentile_95': float(np.percentile(results, 95)),
            'value_at_risk': float(np.percentile(results, 5)),
            'parameters': parameters
        }
