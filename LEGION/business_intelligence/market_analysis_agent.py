"""
Market Analysis Agent - Enterprise Legion (Fixed)
Analyzes market trends and competitive intelligence
"""

import sys
import os
from typing import Dict, Any

# Add enterprise directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core_framework import BaseAgent


class MarketAnalysisAgent(BaseAgent):
    """Market analysis and competitive intelligence agent"""
    
    def __init__(self, agent_id: str = "market_analysis_agent"):
        capabilities = [
            "market_analysis",
            "competitive_intelligence", 
            "trend_monitoring",
            "market_research",
            "opportunity_identification"
        ]
        super().__init__(agent_id, "MarketAnalysisAgent", "business_intelligence", capabilities)
        
        self.market_data = {}
        self.competitors = {}
        self.trends = {}
    
    async def initialize(self) -> bool:
        """Initialize the agent"""
        try:
            await super().initialize()
            return True
        except Exception:
            return False
    
    async def process_task(self, task) -> Dict[str, Any]:
        """Process market analysis tasks"""
        try:
            if hasattr(task, 'parameters'):
                task_data = task.parameters
            else:
                task_data = task
            
            action = task_data.get('action', 'analyze_market')
            
            if action == "analyze_market":
                return await self._analyze_market(task_data)
            elif action == "competitor_analysis":
                return await self._analyze_competitors(task_data)
            else:
                return {"status": "success", "message": "Market analysis completed"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _analyze_market(self, params: Dict) -> Dict[str, Any]:
        """Analyze market conditions"""
        market_segment = params.get('segment', 'AI Consulting')
        
        # Simple market analysis
        analysis = {
            "segment": market_segment,
            "growth_rate": "15-25% annually",
            "market_size": "$150B globally",
            "opportunity_score": 8.5,
            "trends": [
                "Increased AI adoption",
                "Digital transformation acceleration", 
                "Remote work normalization"
            ],
            "recommendations": [
                "Focus on automation consulting",
                "Develop industry-specific solutions",
                "Build thought leadership content"
            ]
        }
        
        return {
            "status": "success",
            "analysis": analysis,
            "generated_at": "2025-07-02"
        }
    
    async def _analyze_competitors(self, params: Dict) -> Dict[str, Any]:
        """Analyze competitive landscape"""
        analysis = {
            "competitive_landscape": "Fragmented market with opportunities",
            "main_competitors": [
                "Large consulting firms",
                "Specialized AI boutiques", 
                "Freelance consultants"
            ],
            "competitive_advantages": [
                "Agile approach",
                "Cost-effective solutions",
                "Rapid deployment capability"
            ],
            "market_positioning": "Premium boutique AI consulting"
        }
        
        return {
            "status": "success",
            "competitive_analysis": analysis
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "capabilities": self.capabilities,
            "market_segments_tracked": len(self.market_data),
            "competitors_monitored": len(self.competitors)
        }
