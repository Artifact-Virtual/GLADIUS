"""
Resource Optimization Agent - Enterprise Legion
Optimizes resource allocation and utilization across the organization
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import uuid
import numpy as np

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core_framework import BaseAgent, AgentTask, AgentMessage

logger = logging.getLogger(__name__)


@dataclass
class Resource:
    """Resource definition"""
    resource_id: str
    name: str
    type: str
    capacity: float
    current_utilization: float
    cost_per_unit: float
    availability_schedule: Dict[str, Any]
    constraints: List[str]
    location: Optional[str] = None


@dataclass
class ResourceRequest:
    """Resource request from agents"""
    request_id: str
    requesting_agent: str
    resource_type: str
    quantity_needed: float
    priority: int
    start_time: datetime
    duration_minutes: int
    constraints: List[str]
    status: str = "pending"


class ResourceOptimizationAgent(BaseAgent):
    """Advanced resource optimization and allocation agent"""
    
    def __init__(self, agent_id: str = "resourceoptimizationagent"):
        capabilities = ["resource_optimization", "performance_tuning"]
        super().__init__(agent_id, "ResourceOptimizationAgent", "automation", capabilities)
        self.resources = {}
        self.resource_requests = {}
        self.allocation_history = []
        self.optimization_algorithms = {
            "linear_programming": self._linear_programming_optimization,
            "genetic_algorithm": self._genetic_algorithm_optimization,
            "greedy": self._greedy_optimization
        }
        self.integration_points = [
            "workflow_orchestrator",
            "task_scheduler",
            "performance_monitor",
            "financial_analysis"
        ]
        self._initialize_resources()
    
    async def initialize(self) -> bool:
        """Initialize the agent"""
        try:
            self.logger.info(f"Initializing {self.agent_id}...")
            # Basic initialization
            self.logger.info(f"{self.agent_id} initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.agent_id}: {e}")
            return False

    async def process_task(self, task) -> Dict[str, Any]:
        """Process resource optimization tasks"""
        try:
            # Handle both AgentTask objects and dicts
            if hasattr(task, 'parameters'):
                task_data = task.parameters
                task_type = getattr(task, 'task_type', 'resource_optimization')
            else:
                task_data = task
                task_type = task.get('task_type', 'resource_optimization')
            
            action = task_data.get("action", task_type)
            
            if action == "optimize_allocation":
                return await self._optimize_resource_allocation(task.parameters)
            elif action == "request_resource":
                return await self._handle_resource_request(task.parameters)
            elif action == "release_resource":
                return await self._release_resource(task.parameters)
            elif action == "analyze_utilization":
                return await self._analyze_utilization(task.parameters)
            elif action == "forecast_demand":
                return await self._forecast_resource_demand(task.parameters)
            elif action == "cost_optimization":
                return await self._optimize_costs(task.parameters)
            else:
                return {"status": "error", "message": "Unknown action"}
                
        except Exception as e:
            logger.error(f"Error in resource optimization: {e}")
            return {"status": "error", "message": str(e)}
    
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle messages from other agents"""
        try:
            if message.message_type == "resource_request":
                result = await self._process_resource_request(message.payload)
                return self._create_response(message, "resource_response", result)
            elif message.message_type == "resource_status_update":
                await self._update_resource_status(message.payload)
            elif message.message_type == "demand_forecast_request":
                result = await self._generate_demand_forecast(message.payload)
                return self._create_response(message, "forecast_response", result)
            elif message.message_type == "optimization_request":
                result = await self._run_optimization(message.payload)
                return self._create_response(message, "optimization_response", result)
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return None
    
    def _create_response(self, original_message: AgentMessage, 
                        response_type: str, payload: Dict) -> AgentMessage:
        """Create response message"""
        return AgentMessage(
            id=str(uuid.uuid4()),
            source_agent=self.agent_id,
            target_agent=original_message.source_agent,
            message_type=response_type,
            payload=payload,
            timestamp=datetime.now()
        )
    
    async def _optimize_resource_allocation(self, params: Dict) -> Dict[str, Any]:
        """Optimize resource allocation using selected algorithm"""
        algorithm = params.get("algorithm", "greedy")
        time_horizon = params.get("time_horizon_hours", 24)
        
        if algorithm not in self.optimization_algorithms:
            return {"status": "error", "message": "Unknown algorithm"}
        
        optimization_func = self.optimization_algorithms[algorithm]
        result = await optimization_func(time_horizon)
        
        # Apply optimization results
        if result["status"] == "success":
            await self._apply_optimization_results(result["allocations"])
            
            # Notify relevant agents
            await self.send_message(
                "workflow_orchestrator",
                "resource_optimization_complete",
                {"optimization_id": result["optimization_id"]}
            )
        
        return result
    
    async def _linear_programming_optimization(self, time_horizon: int) -> Dict[str, Any]:
        """Linear programming optimization (simplified implementation)"""
        try:
            optimization_id = str(uuid.uuid4())
            
            # Collect active requests
            active_requests = [
                req for req in self.resource_requests.values()
                if req.status == "pending"
            ]
            
            if not active_requests:
                return {
                    "status": "success",
                    "optimization_id": optimization_id,
                    "allocations": [],
                    "message": "No pending requests to optimize"
                }
            
            # Simple allocation algorithm (in production, use actual LP solver)
            allocations = []
            available_resources = dict(self.resources)
            
            # Sort requests by priority and efficiency
            sorted_requests = sorted(
                active_requests,
                key=lambda r: (r.priority, -r.quantity_needed),
                reverse=True
            )
            
            for request in sorted_requests:
                best_resource = self._find_best_resource(request, available_resources)
                
                if best_resource:
                    allocation = {
                        "request_id": request.request_id,
                        "resource_id": best_resource.resource_id,
                        "allocated_quantity": min(request.quantity_needed, best_resource.capacity),
                        "start_time": request.start_time.isoformat(),
                        "end_time": (request.start_time + timedelta(minutes=request.duration_minutes)).isoformat(),
                        "efficiency_score": self._calculate_efficiency(request, best_resource)
                    }
                    allocations.append(allocation)
                    
                    # Update available capacity
                    best_resource.current_utilization += allocation["allocated_quantity"]
            
            return {
                "status": "success",
                "optimization_id": optimization_id,
                "algorithm": "linear_programming",
                "allocations": allocations,
                "total_requests": len(active_requests),
                "allocated_requests": len(allocations),
                "efficiency_score": np.mean([a["efficiency_score"] for a in allocations]) if allocations else 0
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _genetic_algorithm_optimization(self, time_horizon: int) -> Dict[str, Any]:
        """Genetic algorithm optimization (simplified implementation)"""
        try:
            optimization_id = str(uuid.uuid4())
            
            # Simplified GA implementation
            population_size = 50
            generations = 100
            
            active_requests = [
                req for req in self.resource_requests.values()
                if req.status == "pending"
            ]
            
            if not active_requests:
                return {
                    "status": "success",
                    "optimization_id": optimization_id,
                    "allocations": [],
                    "message": "No pending requests to optimize"
                }
            
            # Generate initial population (random allocations)
            population = self._generate_initial_population(active_requests, population_size)
            
            best_solution = None
            best_fitness = -float('inf')
            
            for generation in range(generations):
                # Evaluate fitness
                fitness_scores = [self._evaluate_fitness(solution) for solution in population]
                
                # Track best solution
                max_fitness_idx = np.argmax(fitness_scores)
                if fitness_scores[max_fitness_idx] > best_fitness:
                    best_fitness = fitness_scores[max_fitness_idx]
                    best_solution = population[max_fitness_idx]
                
                # Selection, crossover, mutation (simplified)
                new_population = self._evolve_population(population, fitness_scores)
                population = new_population
            
            allocations = self._solution_to_allocations(best_solution, active_requests)
            
            return {
                "status": "success",
                "optimization_id": optimization_id,
                "algorithm": "genetic_algorithm",
                "allocations": allocations,
                "fitness_score": best_fitness,
                "generations": generations
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _greedy_optimization(self, time_horizon: int) -> Dict[str, Any]:
        """Greedy optimization algorithm"""
        try:
            optimization_id = str(uuid.uuid4())
            
            active_requests = [
                req for req in self.resource_requests.values()
                if req.status == "pending"
            ]
            
            if not active_requests:
                return {
                    "status": "success",
                    "optimization_id": optimization_id,
                    "allocations": [],
                    "message": "No pending requests to optimize"
                }
            
            allocations = []
            available_resources = {k: dict(v.__dict__) for k, v in self.resources.items()}
            
            # Sort by priority and efficiency ratio
            sorted_requests = sorted(
                active_requests,
                key=lambda r: r.priority * (1 / max(r.quantity_needed, 1)),
                reverse=True
            )
            
            for request in sorted_requests:
                best_allocation = None
                best_efficiency = -1
                
                for resource_id, resource_data in available_resources.items():
                    if resource_data["current_utilization"] + request.quantity_needed <= resource_data["capacity"]:
                        efficiency = self._calculate_efficiency_dict(request, resource_data)
                        
                        if efficiency > best_efficiency:
                            best_efficiency = efficiency
                            best_allocation = {
                                "request_id": request.request_id,
                                "resource_id": resource_id,
                                "allocated_quantity": request.quantity_needed,
                                "start_time": request.start_time.isoformat(),
                                "end_time": (request.start_time + timedelta(minutes=request.duration_minutes)).isoformat(),
                                "efficiency_score": efficiency
                            }
                
                if best_allocation:
                    allocations.append(best_allocation)
                    # Update available capacity
                    resource_id = best_allocation["resource_id"]
                    available_resources[resource_id]["current_utilization"] += request.quantity_needed
            
            total_efficiency = np.mean([a["efficiency_score"] for a in allocations]) if allocations else 0
            
            return {
                "status": "success",
                "optimization_id": optimization_id,
                "algorithm": "greedy",
                "allocations": allocations,
                "total_requests": len(active_requests),
                "allocated_requests": len(allocations),
                "allocation_rate": len(allocations) / len(active_requests) * 100,
                "average_efficiency": total_efficiency
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _find_best_resource(self, request: ResourceRequest, available_resources: Dict) -> Optional[Resource]:
        """Find the best resource for a request"""
        best_resource = None
        best_score = -1
        
        for resource in available_resources.values():
            if (resource.type == request.resource_type and
                resource.current_utilization + request.quantity_needed <= resource.capacity):
                
                score = self._calculate_efficiency(request, resource)
                if score > best_score:
                    best_score = score
                    best_resource = resource
        
        return best_resource
    
    def _calculate_efficiency(self, request: ResourceRequest, resource: Resource) -> float:
        """Calculate allocation efficiency score"""
        # Factor in cost, utilization, and constraint satisfaction
        cost_factor = 1 / (resource.cost_per_unit + 1)
        utilization_factor = 1 - (resource.current_utilization / resource.capacity)
        constraint_factor = len(set(request.constraints) & set(resource.constraints)) / max(len(request.constraints), 1)
        
        return (cost_factor * 0.4 + utilization_factor * 0.4 + constraint_factor * 0.2)
    
    def _calculate_efficiency_dict(self, request: ResourceRequest, resource_data: Dict) -> float:
        """Calculate efficiency from resource dictionary"""
        cost_factor = 1 / (resource_data["cost_per_unit"] + 1)
        utilization_factor = 1 - (resource_data["current_utilization"] / resource_data["capacity"])
        constraint_factor = len(set(request.constraints) & set(resource_data.get("constraints", []))) / max(len(request.constraints), 1)
        
        return (cost_factor * 0.4 + utilization_factor * 0.4 + constraint_factor * 0.2)
    
    async def _handle_resource_request(self, params: Dict) -> Dict[str, Any]:
        """Handle new resource request"""
        request = ResourceRequest(
            request_id=str(uuid.uuid4()),
            requesting_agent=params.get("requesting_agent"),
            resource_type=params.get("resource_type"),
            quantity_needed=params.get("quantity_needed"),
            priority=params.get("priority", 1),
            start_time=datetime.fromisoformat(params.get("start_time", datetime.now().isoformat())),
            duration_minutes=params.get("duration_minutes", 60),
            constraints=params.get("constraints", [])
        )
        
        self.resource_requests[request.request_id] = request
        
        # Try immediate allocation for high-priority requests
        if request.priority >= 8:
            allocation_result = await self._try_immediate_allocation(request)
            if allocation_result["status"] == "success":
                request.status = "allocated"
                return allocation_result
        
        return {
            "status": "success",
            "request_id": request.request_id,
            "message": "Request queued for optimization"
        }
    
    async def _try_immediate_allocation(self, request: ResourceRequest) -> Dict[str, Any]:
        """Try to allocate resource immediately"""
        best_resource = self._find_best_resource(request, self.resources)
        
        if best_resource:
            best_resource.current_utilization += request.quantity_needed
            
            allocation = {
                "request_id": request.request_id,
                "resource_id": best_resource.resource_id,
                "allocated_quantity": request.quantity_needed,
                "start_time": request.start_time.isoformat(),
                "end_time": (request.start_time + timedelta(minutes=request.duration_minutes)).isoformat()
            }
            
            self.allocation_history.append(allocation)
            
            return {
                "status": "success",
                "allocation": allocation,
                "immediate": True
            }
        
        return {"status": "failed", "message": "No available resources"}
    
    async def _release_resource(self, params: Dict) -> Dict[str, Any]:
        """Release allocated resource"""
        allocation_id = params.get("allocation_id")
        resource_id = params.get("resource_id")
        quantity = params.get("quantity")
        
        if resource_id in self.resources:
            resource = self.resources[resource_id]
            resource.current_utilization = max(0, resource.current_utilization - quantity)
            
            # Log release
            logger.info(f"Released {quantity} units of resource {resource_id}")
            
            return {
                "status": "success",
                "resource_id": resource_id,
                "released_quantity": quantity,
                "new_utilization": resource.current_utilization
            }
        
        return {"status": "error", "message": "Resource not found"}
    
    async def _analyze_utilization(self, params: Dict) -> Dict[str, Any]:
        """Analyze resource utilization patterns"""
        time_window = params.get("time_window_hours", 24)
        
        utilization_analysis = {}
        
        for resource_id, resource in self.resources.items():
            utilization_rate = resource.current_utilization / resource.capacity
            
            analysis = {
                "resource_id": resource_id,
                "name": resource.name,
                "type": resource.type,
                "current_utilization_rate": utilization_rate,
                "capacity": resource.capacity,
                "cost_per_unit": resource.cost_per_unit,
                "status": self._get_utilization_status(utilization_rate),
                "recommendations": self._get_utilization_recommendations(utilization_rate)
            }
            
            utilization_analysis[resource_id] = analysis
        
        # Overall statistics
        all_rates = [r.current_utilization / r.capacity for r in self.resources.values()]
        
        summary = {
            "total_resources": len(self.resources),
            "average_utilization": np.mean(all_rates) if all_rates else 0,
            "underutilized_resources": sum(1 for rate in all_rates if rate < 0.5),
            "overutilized_resources": sum(1 for rate in all_rates if rate > 0.8),
            "optimal_resources": sum(1 for rate in all_rates if 0.5 <= rate <= 0.8)
        }
        
        return {
            "status": "success",
            "summary": summary,
            "resource_analysis": utilization_analysis,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_utilization_status(self, utilization_rate: float) -> str:
        """Get utilization status description"""
        if utilization_rate < 0.3:
            return "underutilized"
        elif utilization_rate < 0.7:
            return "optimal"
        elif utilization_rate < 0.9:
            return "high"
        else:
            return "overutilized"
    
    def _get_utilization_recommendations(self, utilization_rate: float) -> List[str]:
        """Get recommendations based on utilization"""
        recommendations = []
        
        if utilization_rate < 0.3:
            recommendations.extend([
                "Consider reallocating capacity to other resources",
                "Investigate reasons for low demand",
                "Evaluate cost-effectiveness of maintaining full capacity"
            ])
        elif utilization_rate > 0.8:
            recommendations.extend([
                "Consider increasing capacity",
                "Implement load balancing",
                "Schedule maintenance during low-demand periods"
            ])
        
        return recommendations
    
    async def _forecast_resource_demand(self, params: Dict) -> Dict[str, Any]:
        """Forecast future resource demand"""
        forecast_horizon = params.get("forecast_days", 7)
        resource_type = params.get("resource_type")
        
        # Simple forecasting based on historical patterns
        historical_data = self._get_historical_usage(resource_type, forecast_horizon * 2)
        
        if not historical_data:
            return {
                "status": "success",
                "forecast": [],
                "message": "Insufficient historical data for forecasting"
            }
        
        # Calculate trend and seasonality (simplified)
        daily_averages = []
        for day in range(forecast_horizon):
            # Simple moving average with trend
            if len(historical_data) >= 7:
                recent_avg = np.mean(historical_data[-7:])
                trend = (historical_data[-1] - historical_data[-7]) / 7 if len(historical_data) >= 7 else 0
                forecast_value = recent_avg + (trend * day)
            else:
                forecast_value = np.mean(historical_data)
            
            daily_averages.append(max(0, forecast_value))
        
        forecast_data = []
        for i, demand in enumerate(daily_averages):
            forecast_date = datetime.now() + timedelta(days=i+1)
            forecast_data.append({
                "date": forecast_date.isoformat(),
                "predicted_demand": round(demand, 2),
                "confidence_interval": [
                    round(demand * 0.8, 2),
                    round(demand * 1.2, 2)
                ]
            })
        
        return {
            "status": "success",
            "resource_type": resource_type,
            "forecast_horizon_days": forecast_horizon,
            "forecast": forecast_data,
            "methodology": "moving_average_with_trend"
        }
    
    def _get_historical_usage(self, resource_type: str, days: int) -> List[float]:
        """Get historical usage data (simplified simulation)"""
        # In production, this would query actual historical data
        # Simulating with realistic patterns
        base_usage = 50.0
        seasonal_pattern = [0.8, 0.9, 1.0, 1.2, 1.3, 1.1, 0.7]  # Weekly pattern
        
        historical_data = []
        for day in range(days):
            day_of_week = day % 7
            seasonal_factor = seasonal_pattern[day_of_week]
            noise = np.random.normal(0, 0.1)
            usage = base_usage * seasonal_factor * (1 + noise)
            historical_data.append(max(0, usage))
        
        return historical_data
    
    async def _optimize_costs(self, params: Dict) -> Dict[str, Any]:
        """Optimize resource costs"""
        optimization_target = params.get("target", "minimize_total_cost")
        
        cost_analysis = {}
        total_current_cost = 0
        optimization_opportunities = []
        
        for resource_id, resource in self.resources.items():
            current_cost = resource.current_utilization * resource.cost_per_unit
            total_current_cost += current_cost
            
            # Analyze cost optimization opportunities
            utilization_rate = resource.current_utilization / resource.capacity
            
            if utilization_rate < 0.5:
                potential_savings = (resource.capacity - resource.current_utilization) * resource.cost_per_unit * 0.3
                optimization_opportunities.append({
                    "resource_id": resource_id,
                    "type": "reduce_capacity",
                    "potential_savings": potential_savings,
                    "current_utilization": utilization_rate
                })
            elif utilization_rate > 0.9:
                additional_cost = resource.capacity * resource.cost_per_unit * 0.1
                optimization_opportunities.append({
                    "resource_id": resource_id,
                    "type": "increase_capacity",
                    "additional_cost": additional_cost,
                    "current_utilization": utilization_rate
                })
            
            cost_analysis[resource_id] = {
                "current_cost": current_cost,
                "cost_per_unit": resource.cost_per_unit,
                "utilization_rate": utilization_rate,
                "efficiency_score": self._calculate_cost_efficiency(resource)
            }
        
        # Calculate potential savings
        total_potential_savings = sum(
            opp.get("potential_savings", 0) for opp in optimization_opportunities
            if opp["type"] == "reduce_capacity"
        )
        
        return {
            "status": "success",
            "total_current_cost": total_current_cost,
            "cost_analysis": cost_analysis,
            "optimization_opportunities": optimization_opportunities,
            "potential_savings": total_potential_savings,
            "optimization_recommendations": self._generate_cost_recommendations(optimization_opportunities)
        }
    
    def _calculate_cost_efficiency(self, resource: Resource) -> float:
        """Calculate cost efficiency score for a resource"""
        if resource.capacity == 0:
            return 0
        
        utilization_efficiency = resource.current_utilization / resource.capacity
        cost_efficiency = 1 / (resource.cost_per_unit + 1)
        
        return (utilization_efficiency * 0.7 + cost_efficiency * 0.3)
    
    def _generate_cost_recommendations(self, opportunities: List[Dict]) -> List[str]:
        """Generate cost optimization recommendations"""
        recommendations = []
        
        reduce_capacity_ops = [op for op in opportunities if op["type"] == "reduce_capacity"]
        increase_capacity_ops = [op for op in opportunities if op["type"] == "increase_capacity"]
        
        if reduce_capacity_ops:
            total_savings = sum(op["potential_savings"] for op in reduce_capacity_ops)
            recommendations.append(f"Reduce capacity for {len(reduce_capacity_ops)} underutilized resources (potential savings: ${total_savings:.2f})")
        
        if increase_capacity_ops:
            recommendations.append(f"Consider increasing capacity for {len(increase_capacity_ops)} overutilized resources")
        
        if not opportunities:
            recommendations.append("Current resource allocation appears optimal")
        
        return recommendations
    
    def _initialize_resources(self):
        """Initialize sample resources"""
        self.resources = {
            "compute_cluster_1": Resource(
                resource_id="compute_cluster_1",
                name="Primary Compute Cluster",
                type="compute",
                capacity=100.0,
                current_utilization=45.0,
                cost_per_unit=0.50,
                availability_schedule={"24/7": True},
                constraints=["high_security", "gpu_enabled"]
            ),
            "database_server_1": Resource(
                resource_id="database_server_1",
                name="Main Database Server",
                type="database",
                capacity=50.0,
                current_utilization=30.0,
                cost_per_unit=0.75,
                availability_schedule={"24/7": True},
                constraints=["high_availability", "encrypted"]
            ),
            "storage_system_1": Resource(
                resource_id="storage_system_1",
                name="Enterprise Storage",
                type="storage",
                capacity=1000.0,
                current_utilization=650.0,
                cost_per_unit=0.05,
                availability_schedule={"24/7": True},
                constraints=["redundant", "high_speed"]
            )
        }
    
    def _generate_initial_population(self, requests: List[ResourceRequest], size: int) -> List[List]:
        """Generate initial population for genetic algorithm"""
        population = []
        available_resources = list(self.resources.keys())
        
        for _ in range(size):
            solution = []
            for request in requests:
                # Random resource assignment
                compatible_resources = [
                    r for r in available_resources
                    if self.resources[r].type == request.resource_type
                ]
                if compatible_resources:
                    solution.append(np.random.choice(compatible_resources))
                else:
                    solution.append(None)
            population.append(solution)
        
        return population
    
    def _evaluate_fitness(self, solution: List) -> float:
        """Evaluate fitness of a solution"""
        total_score = 0
        resource_usage = {r_id: 0 for r_id in self.resources.keys()}
        
        for i, resource_id in enumerate(solution):
            if resource_id is None:
                continue
                
            request = list(self.resource_requests.values())[i]
            resource = self.resources[resource_id]
            
            # Check capacity constraint
            if resource_usage[resource_id] + request.quantity_needed > resource.capacity:
                total_score -= 100  # Penalty for constraint violation
                continue
            
            # Add efficiency score
            efficiency = self._calculate_efficiency(request, resource)
            total_score += efficiency * request.priority
            
            resource_usage[resource_id] += request.quantity_needed
        
        return total_score
    
    def _evolve_population(self, population: List[List], fitness_scores: List[float]) -> List[List]:
        """Evolve population through selection, crossover, and mutation"""
        new_population = []
        
        # Keep best solutions (elitism)
        elite_count = max(1, len(population) // 10)
        elite_indices = np.argsort(fitness_scores)[-elite_count:]
        for idx in elite_indices:
            new_population.append(population[idx].copy())
        
        # Generate rest through crossover and mutation
        while len(new_population) < len(population):
            # Tournament selection
            parent1 = self._tournament_selection(population, fitness_scores)
            parent2 = self._tournament_selection(population, fitness_scores)
            
            # Crossover
            child = self._crossover(parent1, parent2)
            
            # Mutation
            child = self._mutate(child)
            
            new_population.append(child)
        
        return new_population
    
    def _tournament_selection(self, population: List[List], fitness_scores: List[float]) -> List:
        """Tournament selection for genetic algorithm"""
        tournament_size = 3
        tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        winner_idx = tournament_indices[np.argmax(tournament_fitness)]
        return population[winner_idx].copy()
    
    def _crossover(self, parent1: List, parent2: List) -> List:
        """Single-point crossover"""
        if len(parent1) <= 1:
            return parent1.copy()
        
        crossover_point = np.random.randint(1, len(parent1))
        child = parent1[:crossover_point] + parent2[crossover_point:]
        return child
    
    def _mutate(self, solution: List) -> List:
        """Mutation operation"""
        mutation_rate = 0.1
        available_resources = list(self.resources.keys())
        
        for i in range(len(solution)):
            if np.random.random() < mutation_rate:
                # Random reassignment
                request = list(self.resource_requests.values())[i]
                compatible_resources = [
                    r for r in available_resources
                    if self.resources[r].type == request.resource_type
                ]
                if compatible_resources:
                    solution[i] = np.random.choice(compatible_resources)
        
        return solution
    
    def _solution_to_allocations(self, solution: List, requests: List[ResourceRequest]) -> List[Dict]:
        """Convert GA solution to allocation format"""
        allocations = []
        
        for i, resource_id in enumerate(solution):
            if resource_id is None:
                continue
                
            request = requests[i]
            resource = self.resources[resource_id]
            
            allocation = {
                "request_id": request.request_id,
                "resource_id": resource_id,
                "allocated_quantity": request.quantity_needed,
                "start_time": request.start_time.isoformat(),
                "end_time": (request.start_time + timedelta(minutes=request.duration_minutes)).isoformat(),
                "efficiency_score": self._calculate_efficiency(request, resource)
            }
            allocations.append(allocation)
        
        return allocations
    
    async def _apply_optimization_results(self, allocations: List[Dict]):
        """Apply optimization results to resource allocations"""
        for allocation in allocations:
            resource_id = allocation["resource_id"]
            request_id = allocation["request_id"]
            
            # Update resource utilization
            if resource_id in self.resources:
                self.resources[resource_id].current_utilization += allocation["allocated_quantity"]
            
            # Update request status
            if request_id in self.resource_requests:
                self.resource_requests[request_id].status = "allocated"
            
            # Store allocation history
            self.allocation_history.append(allocation)
        
        logger.info(f"Applied {len(allocations)} resource allocations")
    
    async def _process_resource_request(self, payload: Dict) -> Dict[str, Any]:
        """Process resource request from message"""
        return await self._handle_resource_request(payload)
    
    async def _update_resource_status(self, payload: Dict):
        """Update resource status from external systems"""
        resource_id = payload.get("resource_id")
        updates = payload.get("updates", {})
        
        if resource_id in self.resources:
            resource = self.resources[resource_id]
            
            if "current_utilization" in updates:
                resource.current_utilization = updates["current_utilization"]
            if "capacity" in updates:
                resource.capacity = updates["capacity"]
            if "cost_per_unit" in updates:
                resource.cost_per_unit = updates["cost_per_unit"]
            
            logger.info(f"Updated resource {resource_id} status")
    
    async def _generate_demand_forecast(self, payload: Dict) -> Dict[str, Any]:
        """Generate demand forecast from message request"""
        return await self._forecast_resource_demand(payload)
    
    async def _run_optimization(self, payload: Dict) -> Dict[str, Any]:
        """Run optimization from message request"""
        return await self._optimize_resource_allocation(payload)
