"""
Enhanced External Systems Integration Agent
Coordinates with free, open-source, and headless integration endpoints
"""

import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime
import sys
import os

# Add enterprise directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from legion.core_framework import BaseAgent

try:
    from enterprise.operations.integration_endpoints_clean import (
        create_integration_suite
    )
except ImportError:
    integration_endpoints_available = False
else:
    integration_endpoints_available = True

logger = logging.getLogger(__name__)


class EnhancedExternalSystemsIntegrationAgent(BaseAgent):
    """Enhanced agent for external systems integration with real endpoints"""
    
    def __init__(self, agent_id: str = "enhanced_external_systems_integration"):
        capabilities = [
            "crm_management",
            "email_automation", 
            "financial_data",
            "project_coordination",
            "public_api_access",
            "integration_monitoring",
            "campaign_management"
        ]
        
        super().__init__(
            agent_id, 
            "Enhanced External Systems Integration Agent",
            "operations", 
            capabilities
        )
        
        self.integrations = None
        self.active_campaigns = {}
        self.scheduled_tasks = {}
        self.integration_status = {}
        
    async def initialize(self) -> bool:
        """Initialize integration suite"""
        try:
            await super().initialize()
            
            if integration_endpoints_available:
                self.integrations = await create_integration_suite()
                self.logger.info("External systems integrations initialized")
                return True
            else:
                self.logger.warning(
                    "Integration endpoints not available, running in mock mode"
                )
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to initialize integrations: {e}")
            return False
    
    async def cleanup(self):
        """Clean up integration connections"""
        if self.integrations:
            await self.integrations["manager"].close()
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute integration task"""
        task_type = task.get("type")
        
        try:
            if task_type == "crm_add_lead":
                return await self._handle_crm_lead(task)
            elif task_type == "email_send":
                return await self._handle_email_send(task)
            elif task_type == "email_campaign":
                return await self._handle_email_campaign(task)
            elif task_type == "finance_data":
                return await self._handle_finance_data(task)
            elif task_type == "project_create":
                return await self._handle_project_create(task)
            elif task_type == "project_task":
                return await self._handle_project_task(task)
            elif task_type == "public_api_data":
                return await self._handle_public_api(task)
            elif task_type == "integration_status":
                return await self._handle_status_check(task)
            else:
                return {
                    "success": False,
                    "error": f"Unknown task type: {task_type}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error executing task {task_type}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _handle_crm_lead(self, task: Dict) -> Dict:
        """Handle CRM lead operations"""
        if not self.integrations:
            return self._mock_response("crm_lead", task)
            
        crm = self.integrations["crm"]
        operation = task.get("operation", "add")
        
        if operation == "add":
            lead_data = task.get("lead_data", {})
            lead_id = await crm.add_lead(lead_data)
            return {
                "success": lead_id is not None,
                "lead_id": lead_id,
                "operation": "add_lead",
                "timestamp": datetime.now().isoformat()
            }
        
        elif operation == "update_status":
            lead_id = task.get("lead_id")
            status = task.get("status")
            success = await crm.update_lead_status(lead_id, status)
            return {
                "success": success,
                "lead_id": lead_id,
                "new_status": status,
                "operation": "update_status",
                "timestamp": datetime.now().isoformat()
            }
        
        elif operation == "get_leads":
            status_filter = task.get("status")
            leads = await crm.get_leads(status_filter)
            return {
                "success": True,
                "leads": leads,
                "count": len(leads),
                "operation": "get_leads",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _handle_email_send(self, task: Dict) -> Dict:
        """Handle single email sending"""
        if not self.integrations:
            return self._mock_response("email_send", task)
            
        email = self.integrations["email"]
        
        to_email = task.get("to_email")
        subject = task.get("subject")
        body = task.get("body")
        html_body = task.get("html_body")
        
        success = await email.send_email(to_email, subject, body, html_body)
        return {
            "success": success,
            "to_email": to_email,
            "subject": subject,
            "operation": "send_email",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_email_campaign(self, task: Dict) -> Dict:
        """Handle email campaign"""
        if not self.integrations:
            return self._mock_response("email_campaign", task)
            
        email = self.integrations["email"]
        
        recipients = task.get("recipients", [])
        subject = task.get("subject")
        template = task.get("template")
        data = task.get("data", {})
        
        results = await email.send_campaign(recipients, subject, template, data)
        
        # Store campaign for tracking
        campaign_id = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.active_campaigns[campaign_id] = {
            "results": results,
            "timestamp": datetime.now().isoformat(),
            "recipients_count": len(recipients)
        }
        
        return {
            "success": True,
            "campaign_id": campaign_id,
            "results": results,
            "operation": "email_campaign",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_finance_data(self, task: Dict) -> Dict:
        """Handle financial data requests"""
        if not self.integrations:
            return self._mock_response("finance_data", task)
            
        finance = self.integrations["finance"]
        data_type = task.get("data_type")
        
        if data_type == "crypto":
            coins = task.get("coins")
            data = await finance.get_crypto_prices(coins)
        elif data_type == "exchange_rates":
            base = task.get("base", "USD")
            data = await finance.get_exchange_rates(base)
        elif data_type == "market":
            symbol = task.get("symbol", "AAPL")
            data = await finance.get_market_data(symbol)
        else:
            return {
                "success": False,
                "error": f"Unknown data type: {data_type}",
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "success": bool(data),
            "data": data,
            "data_type": data_type,
            "operation": "finance_data",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_project_create(self, task: Dict) -> Dict:
        """Handle project creation"""
        if not self.integrations:
            return self._mock_response("project_create", task)
            
        pm = self.integrations["projects"]
        project_data = task.get("project_data", {})
        
        project_id = await pm.create_project(project_data)
        return {
            "success": project_id is not None,
            "project_id": project_id,
            "operation": "create_project",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_project_task(self, task: Dict) -> Dict:
        """Handle project task operations"""
        if not self.integrations:
            return self._mock_response("project_task", task)
            
        pm = self.integrations["projects"]
        operation = task.get("operation", "add")
        
        if operation == "add":
            task_data = task.get("task_data", {})
            task_id = await pm.add_task(task_data)
            return {
                "success": task_id is not None,
                "task_id": task_id,
                "operation": "add_task",
                "timestamp": datetime.now().isoformat()
            }
        
        elif operation == "get_projects":
            status = task.get("status")
            projects = await pm.get_projects(status)
            return {
                "success": True,
                "projects": projects,
                "count": len(projects),
                "operation": "get_projects",
                "timestamp": datetime.now().isoformat()
            }
        
        elif operation == "get_tasks":
            project_id = task.get("project_id")
            status = task.get("status")
            tasks = await pm.get_tasks(project_id, status)
            return {
                "success": True,
                "tasks": tasks,
                "count": len(tasks),
                "operation": "get_tasks",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _handle_public_api(self, task: Dict) -> Dict:
        """Handle public API requests"""
        if not self.integrations:
            return self._mock_response("public_api", task)
            
        api = self.integrations["public_apis"]
        api_type = task.get("api_type")
        
        if api_type == "spacex":
            limit = task.get("limit", 5)
            data = await api.get_spacex_launches(limit)
        elif api_type == "weather":
            location = task.get("location", "New York")
            data = await api.get_weather(location)
        elif api_type == "github":
            user = task.get("user")
            limit = task.get("limit", 5)
            data = await api.get_github_repos(user, limit)
        else:
            return {
                "success": False,
                "error": f"Unknown API type: {api_type}",
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "success": bool(data),
            "data": data,
            "api_type": api_type,
            "operation": "public_api_data",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_status_check(self, task: Dict) -> Dict:
        """Check integration status"""
        status = {
            "integrations_active": self.integrations is not None,
            "active_campaigns": len(self.active_campaigns),
            "scheduled_tasks": len(self.scheduled_tasks),
            "timestamp": datetime.now().isoformat()
        }
        
        if self.integrations:
            status["connectivity"] = {}
            
            # Test finance APIs
            try:
                finance = self.integrations["finance"]
                crypto_data = await finance.get_crypto_prices(["bitcoin"])
                status["connectivity"]["coingecko"] = bool(crypto_data)
                
                rates_data = await finance.get_exchange_rates()
                status["connectivity"]["frankfurter"] = bool(rates_data)
            except Exception as e:
                status["connectivity"]["finance_error"] = str(e)
            
            # Test public APIs
            try:
                api = self.integrations["public_apis"]
                spacex_data = await api.get_spacex_launches(1)
                status["connectivity"]["spacex"] = bool(spacex_data)
            except Exception as e:
                status["connectivity"]["spacex_error"] = str(e)
        
        return {
            "success": True,
            "status": status,
            "operation": "status_check",
            "timestamp": datetime.now().isoformat()
        }
    
    def _mock_response(self, operation_type: str, task: Dict) -> Dict:
        """Generate mock response when integrations are not available"""
        return {
            "success": True,
            "mock": True,
            "operation": operation_type,
            "message": "Mock response - integrations not available",
            "task": task,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_enhanced_capabilities(self) -> List[str]:
        """Get enhanced agent capabilities"""
        base_capabilities = [
            "CRM lead management (local SQLite)",
            "Email automation (SMTP)",
            "Financial data (CoinGecko, Frankfurter, Marketstack)",
            "Project management (local SQLite)",
            "Public APIs (SpaceX, Weather, GitHub)",
            "Integration status monitoring",
            "Campaign tracking",
            "Task scheduling coordination"
        ]
        
        if self.integrations:
            return base_capabilities
        else:
            return [cap + " (Mock Mode)" for cap in base_capabilities]
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get detailed integration status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "integrations_available": integration_endpoints_available,
            "integrations_active": self.integrations is not None,
            "active_campaigns": len(self.active_campaigns),
            "scheduled_tasks": len(self.scheduled_tasks),
            "capabilities": self.get_enhanced_capabilities(),
            "last_updated": datetime.now().isoformat()
        }
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming message"""
        message_type = message.get("type")
        
        if message_type == "integration_request":
            return await self.execute_task(message.get("task", {}))
        elif message_type == "status_request":
            return self.get_integration_status()
        elif message_type == "capabilities_request":
            return {"capabilities": self.get_enhanced_capabilities()}
        else:
            return await super().process_message(message)
