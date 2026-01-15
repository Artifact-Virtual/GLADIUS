"""
SENTINEL-GLADIUS Integration
============================

Provides GLADIUS native model as the AI provider for SENTINEL.
Replaces external AI providers (Ollama, OpenAI, etc.)

Author: Artifact Virtual Systems
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("SENTINEL.GladiusProvider")


@dataclass
class GladiusRequest:
    """Request to GLADIUS model"""
    request_id: str
    task: str
    query: str
    context: Dict[str, Any]
    constraints: List[str]
    priority: int
    timestamp: datetime


@dataclass
class GladiusResponse:
    """Response from GLADIUS model"""
    request_id: str
    decision: str
    confidence: float
    reasoning: List[str]
    tool_used: Optional[str]
    result: Any
    latency_ms: float
    timestamp: datetime


class GladiusProvider:
    """
    GLADIUS Native AI Provider for SENTINEL.
    
    Replaces external AI providers with the native GLADIUS model.
    Falls back to pattern-based routing if model not available.
    """
    
    def __init__(self):
        self.gladius_path = Path(__file__).parent.parent.parent / "GLADIUS"
        self._router = None
        self._available = False
        self._initialize()
    
    def _initialize(self):
        """Initialize connection to GLADIUS"""
        try:
            # Try to import GLADIUS router
            sys.path.insert(0, str(self.gladius_path.parent))
            from GLADIUS.router.pattern_router import NativeToolRouter
            self._router = NativeToolRouter()
            self._available = True
            logger.info("GLADIUS provider initialized with native router")
        except ImportError as e:
            logger.warning(f"GLADIUS native router not available: {e}")
            self._available = False
        except Exception as e:
            logger.error(f"Failed to initialize GLADIUS: {e}")
            self._available = False
    
    @property
    def is_available(self) -> bool:
        """Check if GLADIUS is available"""
        return self._available
    
    async def query(self, request: GladiusRequest) -> GladiusResponse:
        """
        Query GLADIUS model for a decision.
        
        Args:
            request: GladiusRequest with task and context
            
        Returns:
            GladiusResponse with decision and confidence
        """
        start_time = datetime.now()
        
        try:
            if self._available and self._router:
                # Use native routing
                result = await self._route_query(request)
            else:
                # Fallback to pattern-based analysis
                result = await self._fallback_analysis(request)
            
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return GladiusResponse(
                request_id=request.request_id,
                decision=result.get("decision", "unknown"),
                confidence=result.get("confidence", 0.5),
                reasoning=result.get("reasoning", []),
                tool_used=result.get("tool"),
                result=result.get("result"),
                latency_ms=latency_ms,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"GLADIUS query error: {e}")
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return GladiusResponse(
                request_id=request.request_id,
                decision="error",
                confidence=0.0,
                reasoning=[str(e)],
                tool_used=None,
                result=None,
                latency_ms=latency_ms,
                timestamp=datetime.now()
            )
    
    async def _route_query(self, request: GladiusRequest) -> Dict[str, Any]:
        """Route query through GLADIUS native router"""
        query_text = f"{request.task}: {request.query}"
        
        # Route to appropriate tool
        routing_result = self._router.route(query_text)
        
        tool = routing_result.get("tool", "unknown")
        confidence = routing_result.get("confidence", 0.5)
        
        # Determine decision based on task type
        decision = self._determine_decision(request.task, tool, request.context)
        
        return {
            "decision": decision,
            "confidence": confidence,
            "tool": tool,
            "result": routing_result,
            "reasoning": [
                f"Routed to tool: {tool}",
                f"Confidence: {confidence:.2%}",
                f"Task type: {request.task}"
            ]
        }
    
    async def _fallback_analysis(self, request: GladiusRequest) -> Dict[str, Any]:
        """Fallback pattern-based analysis"""
        query_lower = request.query.lower()
        task_lower = request.task.lower()
        
        # Simple pattern matching for security decisions
        if "threat" in task_lower or "security" in task_lower:
            if any(kw in query_lower for kw in ["critical", "urgent", "attack"]):
                return {
                    "decision": "block",
                    "confidence": 0.85,
                    "reasoning": ["High-risk keywords detected"],
                    "tool": "threat_analyzer"
                }
            elif any(kw in query_lower for kw in ["suspicious", "unusual"]):
                return {
                    "decision": "investigate",
                    "confidence": 0.7,
                    "reasoning": ["Medium-risk indicators found"],
                    "tool": "investigation"
                }
            else:
                return {
                    "decision": "allow",
                    "confidence": 0.6,
                    "reasoning": ["No immediate threat indicators"],
                    "tool": "monitoring"
                }
        
        # Default response
        return {
            "decision": "review",
            "confidence": 0.5,
            "reasoning": ["Fallback analysis - requires manual review"],
            "tool": None
        }
    
    def _determine_decision(self, task: str, tool: str, context: Dict) -> str:
        """Determine decision based on task and context"""
        task_lower = task.lower()
        
        # Threat analysis
        if "threat" in task_lower:
            severity = context.get("severity", 5)
            if severity >= 8:
                return "block"
            elif severity >= 5:
                return "investigate"
            else:
                return "monitor"
        
        # Compliance check
        if "compliance" in task_lower:
            violations = context.get("violations", [])
            if violations:
                return "remediate"
            return "compliant"
        
        # Default
        return "allow"
    
    async def analyze_threat(self, threat_data: Dict) -> Dict[str, Any]:
        """Analyze a security threat using GLADIUS"""
        request = GladiusRequest(
            request_id=f"threat_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            task="threat_analysis",
            query=json.dumps(threat_data),
            context=threat_data,
            constraints=["harm_prevention", "proportionality"],
            priority=threat_data.get("severity", 5),
            timestamp=datetime.now()
        )
        
        response = await self.query(request)
        
        return {
            "decision": response.decision,
            "confidence": response.confidence,
            "reasoning": response.reasoning,
            "recommended_action": self._map_decision_to_action(response.decision)
        }
    
    def _map_decision_to_action(self, decision: str) -> str:
        """Map decision to actionable response"""
        action_map = {
            "block": "Immediately block and alert security team",
            "investigate": "Initiate investigation protocol",
            "monitor": "Increase monitoring level",
            "allow": "Continue normal operation",
            "remediate": "Execute remediation playbook",
            "compliant": "No action required",
            "review": "Queue for manual review"
        }
        return action_map.get(decision, "Unknown action")
    
    async def validate_ethical_compliance(self, action: str, context: Dict) -> Dict[str, Any]:
        """Validate action against ethical constraints using GLADIUS"""
        request = GladiusRequest(
            request_id=f"ethics_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            task="ethical_validation",
            query=f"Validate action: {action}",
            context=context,
            constraints=[
                "harm_prevention",
                "proportionality",
                "transparency",
                "privacy_protection"
            ],
            priority=8,
            timestamp=datetime.now()
        )
        
        response = await self.query(request)
        
        # Ethical score based on confidence
        ethical_score = response.confidence if response.decision != "block" else 1.0 - response.confidence
        
        return {
            "ethical_score": ethical_score,
            "approved": response.decision in ["allow", "compliant", "monitor"],
            "violations": [] if response.decision in ["allow", "compliant"] else response.reasoning,
            "recommendations": response.reasoning
        }


# Singleton instance
_provider_instance: Optional[GladiusProvider] = None


def get_provider() -> GladiusProvider:
    """Get or create GLADIUS provider instance"""
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = GladiusProvider()
    return _provider_instance


async def query_gladius(
    task: str,
    query: str,
    context: Optional[Dict] = None,
    constraints: Optional[List[str]] = None
) -> GladiusResponse:
    """
    Convenience function to query GLADIUS.
    
    Example:
        response = await query_gladius(
            task="threat_analysis",
            query="Unusual login pattern detected",
            context={"severity": 7, "source_ip": "10.0.0.1"}
        )
    """
    provider = get_provider()
    
    request = GladiusRequest(
        request_id=f"q_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        task=task,
        query=query,
        context=context or {},
        constraints=constraints or [],
        priority=5,
        timestamp=datetime.now()
    )
    
    return await provider.query(request)
