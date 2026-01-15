"""
Workflow Orchestration Agent - Enterprise Legion
Coordinates and manages complex business workflows
"""

import sys
import os
import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import uuid

# Add enterprise directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from legion.core_framework import BaseAgent


class WorkflowOrchestrationAgent(BaseAgent):
    """Advanced workflow orchestration agent with active workflow management"""
    
    def __init__(self, agent_id: str = "workflow_orchestration_agent"):
        capabilities = [
            "workflow_orchestration",
            "process_automation",
            "coordination",
            "error_handling",
            "workflow_triggers",
            "cross_departmental_coordination"
        ]
        super().__init__(agent_id, "WorkflowOrchestrationAgent", "automation", 
                         capabilities)
        self.registered_workflows = {}
        self.active_executions = {}
        self.workflow_templates = {}
        self.trigger_conditions = {}
        
    async def initialize(self) -> bool:
        """Initialize the workflow orchestration agent"""
        try:
            await super().initialize()
            self._load_workflow_templates()
            self._setup_error_recovery()
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize workflow orchestrator: {e}")
            return False
    
    def _load_workflow_templates(self):
        """Load predefined workflow templates"""
        self.workflow_templates = {
            "client_onboarding": {
                "name": "Client Onboarding Process",
                "steps": [
                    {"stage": "compliance", "action": "verify_client_eligibility"},
                    {"stage": "finance", "action": "setup_billing"},
                    {"stage": "communication", "action": "send_welcome_package"},
                    {"stage": "operations", "action": "assign_account_manager"}
                ],
                "error_handling": "retry_with_escalation",
                "timeout": 3600  # 1 hour
            },
            "monthly_reporting": {
                "name": "Monthly Business Reporting",
                "steps": [
                    {"stage": "finance", "action": "generate_financial_reports"},
                    {"stage": "business_intelligence", "action": "analyze_performance"},
                    {"stage": "communication", "action": "create_executive_summary"},
                    {"stage": "operations", "action": "schedule_review_meeting"}
                ],
                "schedule": "monthly_1st_09:00",
                "error_handling": "continue_with_warning"
            },
            "lead_processing": {
                "name": "New Lead Processing Workflow",
                "steps": [
                    {"stage": "legal", "action": "compliance_screening"},
                    {"stage": "business_intelligence", "action": "lead_scoring"},
                    {"stage": "finance", "action": "value_assessment"},
                    {"stage": "communication", "action": "personalized_outreach"}
                ],
                "trigger": "new_lead_event",
                "priority": "high"
            }
        }
    
    def _setup_error_recovery(self):
        """Setup error handling and recovery mechanisms"""
        self.error_strategies = {
            "retry_with_escalation": self._retry_with_escalation,
            "continue_with_warning": self._continue_with_warning,
            "abort_and_notify": self._abort_and_notify
        }
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process workflow orchestration tasks"""
        action = task.get("action", "")
        
        try:
            if action == "register_workflow":
                return await self._register_workflow(task)
            elif action == "execute_workflow":
                return await self._execute_workflow(task)
            elif action == "monitor_workflow":
                return await self._monitor_workflow(task)
            elif action == "setup_trigger":
                return await self._setup_workflow_trigger(task)
            elif action == "cross_department_coordination":
                return await self._coordinate_cross_department(task)
            else:
                return {"status": "error", "message": f"Unknown action: {action}"}
                
        except Exception as e:
            self.logger.error(f"Workflow orchestration error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _register_workflow(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new workflow definition"""
        workflow_id = task.get("workflow_id")
        definition = task.get("definition")
        
        if not workflow_id or not definition:
            return {"status": "error", "message": "Missing workflow_id or definition"}
        
        self.registered_workflows[workflow_id] = {
            "definition": definition,
            "registered_at": datetime.now().isoformat(),
            "executions": 0
        }
        
        self.logger.info(f"Registered workflow: {workflow_id}")
        return {"status": "success", "workflow_id": workflow_id}
    
    async def _execute_workflow(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow with error handling and coordination"""
        workflow_id = task.get("workflow_id")
        parameters = task.get("parameters", {})
        
        if workflow_id not in self.registered_workflows:
            return {"status": "error", "message": f"Workflow {workflow_id} not registered"}
        
        execution_id = str(uuid.uuid4())
        workflow_def = self.registered_workflows[workflow_id]["definition"]
        
        self.active_executions[execution_id] = {
            "workflow_id": workflow_id,
            "started_at": datetime.now(),
            "status": "running",
            "current_step": 0,
            "parameters": parameters
        }
        
        try:
            # Execute workflow steps with coordination
            for i, step in enumerate(workflow_def.get("steps", [])):
                self.active_executions[execution_id]["current_step"] = i
                
                # Execute step with error handling
                step_result = await self._execute_workflow_step(step, parameters)
                
                if not step_result.get("success", False):
                    # Handle step failure
                    error_strategy = workflow_def.get("error_handling", "abort_and_notify")
                    recovery_result = await self.error_strategies[error_strategy](
                        execution_id, step, step_result
                    )
                    
                    if not recovery_result:
                        break
            
            # Mark execution as completed
            self.active_executions[execution_id]["status"] = "completed"
            self.active_executions[execution_id]["completed_at"] = datetime.now()
            
            # Update execution count
            self.registered_workflows[workflow_id]["executions"] += 1
            
            return {
                "status": "success",
                "execution_id": execution_id,
                "workflow_id": workflow_id
            }
            
        except Exception as e:
            self.active_executions[execution_id]["status"] = "failed"
            self.active_executions[execution_id]["error"] = str(e)
            return {"status": "error", "message": str(e)}
    
    async def _execute_workflow_step(self, step: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step with department coordination"""
        stage = step.get("stage")
        action = step.get("action")
        
        self.logger.info(f"Executing workflow step: {stage}.{action}")
        
        # Simulate step execution (in production, this would coordinate with actual agents)
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            "success": True,
            "stage": stage,
            "action": action,
            "result": f"Completed {action} in {stage} department"
        }
    
    async def _setup_workflow_trigger(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Setup automated workflow triggers"""
        trigger_id = task.get("trigger_id")
        conditions = task.get("conditions")
        target_workflow = task.get("target_workflow")
        
        self.trigger_conditions[trigger_id] = {
            "conditions": conditions,
            "target_workflow": target_workflow,
            "created_at": datetime.now().isoformat(),
            "enabled": True
        }
        
        return {"status": "success", "trigger_id": trigger_id}
    
    async def _coordinate_cross_department(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate workflows across multiple departments"""
        departments = task.get("departments", [])
        coordination_type = task.get("coordination_type", "sequential")
        
        if coordination_type == "parallel":
            # Execute department tasks in parallel
            tasks = []
            for dept in departments:
                tasks.append(self._execute_department_task(dept, task))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return {"status": "success", "results": results}
        else:
            # Execute department tasks sequentially
            results = []
            for dept in departments:
                result = await self._execute_department_task(dept, task)
                results.append(result)
            
            return {"status": "success", "results": results}
    
    async def _execute_department_task(self, department: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task for a specific department"""
        # In production, this would route to actual department agents
        self.logger.info(f"Coordinating task with {department} department")
        await asyncio.sleep(0.1)
        return {"department": department, "status": "completed"}
    
    async def _retry_with_escalation(self, execution_id: str, step: Dict[str, Any], error: Dict[str, Any]) -> bool:
        """Retry failed step with escalation"""
        max_retries = 3
        execution = self.active_executions[execution_id]
        retries = execution.get("retries", 0)
        
        if retries < max_retries:
            execution["retries"] = retries + 1
            self.logger.warning(f"Retrying step {step} (attempt {retries + 1})")
            
            # Retry the step
            retry_result = await self._execute_workflow_step(step, execution["parameters"])
            return retry_result.get("success", False)
        else:
            self.logger.error(f"Step failed after {max_retries} retries, escalating")
            return False
    
    async def _continue_with_warning(self, execution_id: str, step: Dict[str, Any], error: Dict[str, Any]) -> bool:
        """Continue workflow execution with warning"""
        self.logger.warning(f"Step {step} failed, continuing with warning: {error}")
        return True
    
    async def _abort_and_notify(self, execution_id: str, step: Dict[str, Any], error: Dict[str, Any]) -> bool:
        """Abort workflow and notify stakeholders"""
        self.logger.error(f"Aborting workflow {execution_id} due to step failure: {error}")
        self.active_executions[execution_id]["status"] = "aborted"
        return False
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive workflow orchestration status"""
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "capabilities": self.capabilities,
            "registered_workflows": len(self.registered_workflows),
            "active_executions": len(self.active_executions),
            "workflow_templates": len(self.workflow_templates),
            "trigger_conditions": len(self.trigger_conditions)
        }
