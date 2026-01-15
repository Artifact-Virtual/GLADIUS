
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from chimera.core.orchestrator import ChimeraOrchestrator

app = FastAPI()
orchestrator = ChimeraOrchestrator()

class ExecuteTaskRequest(BaseModel):
    agent: str
    task: str

@app.get("/agents")
def list_agents():
    """
    Returns a list of available agents.
    """
    return {"agents": orchestrator.list_agents()}

@app.post("/execute")
def execute_task(request: ExecuteTaskRequest):
    """
    Executes a task with the specified agent.
    """
    if request.agent not in orchestrator.list_agents():
        raise HTTPException(status_code=404, detail=f"Agent '{request.agent}' not found.")
    try:
        response = orchestrator.execute_task(request.agent, request.task)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing agent '{request.agent}': {str(e)}")
