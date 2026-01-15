import grpc
import sys
import os

# Add the parent directory to the Python path to allow imports from chimera.grpc
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from chimera.grpc import agent_service_pb2
from chimera.grpc import agent_service_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = agent_service_pb2_grpc.AgentServiceStub(channel)

        # Test ListAgents
        print("\n--- Listing Agents ---")
        response = stub.ListAgents(agent_service_pb2.ListAgentsRequest())
        print("Available Agents:", response.agent_names)

        # Test ExecuteTask with Code-Genius
        print("\n--- Executing Code-Genius Task ---")
        try:
            response = stub.ExecuteTask(agent_service_pb2.ExecuteTaskRequest(
                agent_name="Code-Genius", 
                task="Create a Python function to calculate the Fibonacci sequence."
            ))
            print("Code-Genius Response:", response.response)
        except grpc.RpcError as e:
            print(f"Error executing Code-Genius: {e.details}")

        # Test ExecuteTask with Research_Agent
        print("\n--- Executing Research_Agent Task ---")
        try:
            response = stub.ExecuteTask(agent_service_pb2.ExecuteTaskRequest(
                agent_name="Research_Agent", 
                task="Summarize the history of artificial intelligence."
            ))
            print("Research_Agent Response:", response.response)
        except grpc.RpcError as e:
            print(f"Error executing Research_Agent: {e.details}")

        # Test ExecuteTask with a non-existent agent
        print("\n--- Executing Non-Existent Agent Task ---")
        try:
            response = stub.ExecuteTask(agent_service_pb2.ExecuteTaskRequest(
                agent_name="NonExistentAgent", 
                task="Some task."
            ))
            print("NonExistentAgent Response:", response.response)
        except grpc.RpcError as e:
            print(f"Error executing NonExistentAgent: {e.details}")

if __name__ == '__main__':
    run()
