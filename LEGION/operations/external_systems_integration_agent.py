"""
External Systems Integration Agent - Enterprise Legion
Handles integration with CRM, email, financial, and other external systems
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any
import sys
import os

# Add enterprise directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from legion.core_framework import BaseAgent


class ExternalSystemsIntegrationAgent(BaseAgent):
    """Agent for managing external system integrations"""
    
    def __init__(self, agent_id: str = "external_systems_integration_agent"):
        capabilities = [
            "crm_integration",
            "email_automation",
            "financial_system_sync",
            "marketing_automation",
            "project_management_integration",
            "data_synchronization",
            "webhook_management"
        ]
        super().__init__(agent_id, "ExternalSystemsIntegrationAgent", 
                        "operations", capabilities)
        
        self.external_systems = {}
        self.active_integrations = {}
        self.sync_schedules = {}
        self._initialize_system_configs()
    
    async def initialize(self) -> bool:
        """Initialize the external systems integration agent"""
        try:
            await super().initialize()
            self._setup_integration_endpoints()
            self._configure_data_mappings()
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize integration agent: {e}")
            return False
    
    def _initialize_system_configs(self):
        """Initialize external system configurations"""
        self.external_systems = {
            "crm": {
                "name": "Customer Relationship Management",
                "type": "crm",
                "endpoints": {
                    "leads": "/api/v1/leads",
                    "contacts": "/api/v1/contacts",
                    "opportunities": "/api/v1/opportunities"
                },
                "auth_type": "api_key",
                "sync_frequency": "hourly"
            },
            "email_platform": {
                "name": "Email Marketing Platform",
                "type": "email",
                "endpoints": {
                    "campaigns": "/api/v1/campaigns",
                    "lists": "/api/v1/lists",
                    "analytics": "/api/v1/analytics"
                },
                "auth_type": "oauth2",
                "sync_frequency": "daily"
            },
            "financial_system": {
                "name": "Financial Management System",
                "type": "finance",
                "endpoints": {
                    "invoices": "/api/v1/invoices",
                    "payments": "/api/v1/payments",
                    "reports": "/api/v1/reports"
                },
                "auth_type": "api_key",
                "sync_frequency": "daily"
            },
            "project_management": {
                "name": "Project Management Tool",
                "type": "project",
                "endpoints": {
                    "projects": "/api/v1/projects",
                    "tasks": "/api/v1/tasks",
                    "time_tracking": "/api/v1/time"
                },
                "auth_type": "bearer_token",
                "sync_frequency": "real_time"
            }
        }
    
    def _setup_integration_endpoints(self):
        """Setup integration endpoints and webhooks"""
        self.integration_endpoints = {
            "incoming_webhooks": {
                "new_lead": "/webhook/new_lead",
                "payment_received": "/webhook/payment",
                "project_update": "/webhook/project_update"
            },
            "outgoing_apis": {
                "send_email": self._send_email,
                "create_invoice": self._create_invoice,
                "update_crm": self._update_crm,
                "create_project_task": self._create_project_task
            }
        }
    
    def _configure_data_mappings(self):
        """Configure data mappings between systems"""
        self.data_mappings = {
            "lead_to_crm": {
                "enterprise_field": "crm_field",
                "name": "contact_name",
                "email": "email_address",
                "company": "company_name",
                "value": "opportunity_value"
            },
            "invoice_to_financial": {
                "client_id": "customer_id", 
                "amount": "invoice_amount",
                "due_date": "payment_due_date",
                "description": "invoice_description"
            },
            "task_to_project": {
                "task_name": "project_task_title",
                "description": "task_description",
                "assignee": "assigned_user",
                "deadline": "due_date"
            }
        }
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process external system integration tasks"""
        action = task.get("action", "")
        
        try:
            if action == "sync_data":
                return await self._sync_data(task)
            elif action == "send_to_external":
                return await self._send_to_external_system(task)
            elif action == "fetch_from_external":
                return await self._fetch_from_external_system(task)
            elif action == "setup_webhook":
                return await self._setup_webhook(task)
            elif action == "process_webhook":
                return await self._process_webhook(task)
            elif action == "email_automation":
                return await self._handle_email_automation(task)
            else:
                return {"status": "error", "message": f"Unknown action: {action}"}
                
        except Exception as e:
            self.logger.error(f"Integration task error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _sync_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronize data between enterprise system and external systems"""
        system_name = task.get("system", "")
        data_type = task.get("data_type", "")
        direction = task.get("direction", "bidirectional")  # inbound, outbound, bidirectional
        
        if system_name not in self.external_systems:
            return {"status": "error", "message": f"Unknown system: {system_name}"}
        
        sync_result = {
            "system": system_name,
            "data_type": data_type,
            "direction": direction,
            "started_at": datetime.now().isoformat(),
            "records_processed": 0,
            "errors": []
        }
        
        try:
            if direction in ["outbound", "bidirectional"]:
                # Send data to external system
                outbound_result = await self._send_data_outbound(system_name, data_type)
                sync_result["outbound"] = outbound_result
            
            if direction in ["inbound", "bidirectional"]:
                # Fetch data from external system
                inbound_result = await self._fetch_data_inbound(system_name, data_type)
                sync_result["inbound"] = inbound_result
            
            sync_result["completed_at"] = datetime.now().isoformat()
            sync_result["status"] = "success"
            
            return {"status": "success", "sync_result": sync_result}
            
        except Exception as e:
            sync_result["status"] = "failed"
            sync_result["error"] = str(e)
            return {"status": "error", "sync_result": sync_result}
    
    async def _send_data_outbound(self, system_name: str, data_type: str) -> Dict[str, Any]:
        """Send data from enterprise system to external system"""
        # Simulate sending data to external system
        await asyncio.sleep(0.1)  # Simulate API call
        
        return {
            "direction": "outbound",
            "records_sent": 15,
            "success_count": 14,
            "error_count": 1,
            "last_sync": datetime.now().isoformat()
        }
    
    async def _fetch_data_inbound(self, system_name: str, data_type: str) -> Dict[str, Any]:
        """Fetch data from external system to enterprise system"""
        # Simulate fetching data from external system
        await asyncio.sleep(0.1)  # Simulate API call
        
        return {
            "direction": "inbound",
            "records_fetched": 23,
            "records_updated": 18,
            "records_created": 5,
            "last_sync": datetime.now().isoformat()
        }
    
    async def _send_to_external_system(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Send specific data to external system"""
        system_name = task.get("system", "")
        data = task.get("data", {})
        endpoint = task.get("endpoint", "")
        
        if system_name == "crm":
            return await self._update_crm(data)
        elif system_name == "email_platform":
            return await self._send_email(data)
        elif system_name == "financial_system":
            return await self._create_invoice(data)
        elif system_name == "project_management":
            return await self._create_project_task(data)
        else:
            return {"status": "error", "message": f"Unknown system: {system_name}"}
    
    async def _update_crm(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update CRM system with lead/contact information"""
        # Simulate CRM update
        await asyncio.sleep(0.1)
        
        return {
            "status": "success",
            "crm_record_id": "CRM_12345",
            "action": "updated",
            "message": "Contact updated in CRM successfully"
        }
    
    async def _send_email(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send email through external email platform"""
        recipient = data.get("recipient", "")
        subject = data.get("subject", "")
        content = data.get("content", "")
        
        # Simulate email sending
        await asyncio.sleep(0.1)
        
        return {
            "status": "success",
            "email_id": "EMAIL_67890",
            "recipient": recipient,
            "subject": subject,
            "sent_at": datetime.now().isoformat()
        }
    
    async def _create_invoice(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create invoice in financial system"""
        # Simulate invoice creation
        await asyncio.sleep(0.1)
        
        return {
            "status": "success",
            "invoice_id": "INV_2025_001",
            "amount": data.get("amount", 0),
            "client": data.get("client", ""),
            "created_at": datetime.now().isoformat()
        }
    
    async def _create_project_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create task in project management system"""
        # Simulate task creation
        await asyncio.sleep(0.1)
        
        return {
            "status": "success",
            "task_id": "TASK_456",
            "title": data.get("title", ""),
            "project": data.get("project", ""),
            "created_at": datetime.now().isoformat()
        }
    
    async def _handle_email_automation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle automated email campaigns and sequences"""
        automation_type = task.get("automation_type", "")
        
        if automation_type == "welcome_sequence":
            return await self._trigger_welcome_sequence(task)
        elif automation_type == "follow_up":
            return await self._trigger_follow_up_sequence(task)
        elif automation_type == "newsletter":
            return await self._send_newsletter(task)
        else:
            return {"status": "error", "message": f"Unknown automation type: {automation_type}"}
    
    async def _trigger_welcome_sequence(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger welcome email sequence for new leads"""
        lead_data = task.get("lead_data", {})
        
        # Simulate welcome sequence trigger
        await asyncio.sleep(0.1)
        
        return {
            "status": "success",
            "sequence_id": "WELCOME_SEQ_123",
            "recipient": lead_data.get("email", ""),
            "emails_scheduled": 3,
            "started_at": datetime.now().isoformat()
        }
    
    async def _setup_webhook(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Setup webhook endpoints for external system notifications"""
        webhook_type = task.get("webhook_type", "")
        endpoint = task.get("endpoint", "")
        
        # Simulate webhook setup
        webhook_id = f"WEBHOOK_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "status": "success",
            "webhook_id": webhook_id,
            "type": webhook_type,
            "endpoint": endpoint,
            "created_at": datetime.now().isoformat()
        }
    
    async def _process_webhook(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming webhook notifications"""
        webhook_type = task.get("webhook_type", "")
        payload = task.get("payload", {})
        
        if webhook_type == "new_lead":
            return await self._process_new_lead_webhook(payload)
        elif webhook_type == "payment_received":
            return await self._process_payment_webhook(payload)
        elif webhook_type == "project_update":
            return await self._process_project_update_webhook(payload)
        else:
            return {"status": "error", "message": f"Unknown webhook type: {webhook_type}"}
    
    async def _process_new_lead_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process new lead webhook from external systems"""
        # Extract lead information and trigger enterprise workflows
        lead_info = {
            "name": payload.get("name", ""),
            "email": payload.get("email", ""),
            "company": payload.get("company", ""),
            "source": payload.get("source", "webhook")
        }
        
        # Trigger lead qualification workflow
        return {
            "status": "success",
            "action": "lead_workflow_triggered",
            "lead_info": lead_info,
            "workflow_id": "lead_qualification_process"
        }
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all external system integrations"""
        return {
            "total_systems": len(self.external_systems),
            "active_integrations": len(self.active_integrations),
            "systems": {
                name: {
                    "status": "connected",
                    "last_sync": datetime.now().isoformat(),
                    "sync_frequency": config["sync_frequency"]
                }
                for name, config in self.external_systems.items()
            }
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive external systems integration agent status"""
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "capabilities": self.capabilities,
            "external_systems": len(self.external_systems),
            "active_integrations": len(self.active_integrations),
            "integration_health": "operational"
        }
