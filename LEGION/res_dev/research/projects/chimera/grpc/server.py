import grpc
from concurrent import futures
import sys
import os

# Add the parent directory to the Python path to allow imports from chimera.core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from chimera.grpc import agent_service_pb2
from chimera.grpc import agent_service_pb2_grpc
from chimera.core.orchestrator import ChimeraOrchestrator

class AgentServiceServicer(agent_service_pb2_grpc.AgentServiceServicer):
    def __init__(self):
        self.orchestrator = ChimeraOrchestrator()

    def ListAgents(self, request, context):
        agent_names = self.orchestrator.list_agents()
        return agent_service_pb2.ListAgentsResponse(agent_names=agent_names)

    def ExecuteTask(self, request, context):
        try:
            response = self.orchestrator.execute_task(request.agent_name, request.task)
            return agent_service_pb2.ExecuteTaskResponse(response=response)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error executing agent '{request.agent_name}': {str(e)}")
            return agent_service_pb2.ExecuteTaskResponse(response=f"Error: {str(e)}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    agent_service_pb2_grpc.add_AgentServiceServicer_to_server(
        AgentServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("gRPC server listening on port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
