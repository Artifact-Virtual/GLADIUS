import os
import importlib.util
import inspect

class ChimeraOrchestrator:
    def __init__(self):
        self.agents = self._discover_agents()

    def _discover_agents(self):
        """
        Discovers and loads available agents from the 'agents' directory.
        """
        agents = {}
        agent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'agents'))

        if not os.path.exists(agent_dir):
            return agents

        for agent_name in os.listdir(agent_dir):
            module_dir = os.path.join(agent_dir, agent_name)
            if os.path.isdir(module_dir):
                main_py_path = os.path.join(module_dir, 'main.py')
                if os.path.exists(main_py_path):
                    try:
                        # Dynamically load the module
                        spec = importlib.util.spec_from_file_location(f"chimera.agents.{agent_name}.main", main_py_path)
                        agent_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(agent_module)

                        # Find the agent class in the module (assuming it ends with 'Agent')
                        for name, obj in inspect.getmembers(agent_module, inspect.isclass):
                            if name.endswith('Agent'):
                                # Clean the agent name to use as a key, stripping whitespace and quotes
                                clean_agent_name = agent_name.strip().strip('""')
                                agents[clean_agent_name] = obj() # Instantiate the agent
                                break
                    except Exception as e:
                        print(f"Error loading agent '{agent_name}': {e}")
        return agents

    def list_agents(self):
        """
        Returns a list of available agents.
        """
        return list(self.agents.keys())

    def execute_task(self, agent_name, task):
        """
        Executes a task with the specified agent.
        This is a generic execution method. It will look for a public method
        on the agent and call it with the task as an argument.
        For now, it looks for a method that seems appropriate.
        A more robust implementation would require a standard interface.
        """
        agent_instance = self.agents.get(agent_name)
        if not agent_instance:
            return f"Agent '{agent_name}' not found or failed to load."

        if hasattr(agent_instance, 'execute'):
            return agent_instance.execute(task)
        else:
            return f"Agent '{agent_name}' does not have an 'execute' method."

if __name__ == '__main__':
    orchestrator = ChimeraOrchestrator()
    print("Available and loaded agents:")
    for agent_name, agent_instance in orchestrator.agents.items():
        status = "Loaded" if agent_instance else "Not Loaded"
        print(f"- {agent_name} [{status}]")

    # Example execution for Code-Genius
    if "Code-Genius" in orchestrator.agents:
        print("\nExecuting task with Code-Genius...")
        task_prompt = "Create a javascript function to reverse a string."
        response = orchestrator.execute_task("Code-Genius", task_prompt)
        print(response)

    # Example execution for Research_Agent
    if "Research_Agent" in orchestrator.agents:
        print("\nExecuting task with Research_Agent...")
        task_prompt = "Find the latest research on quantum computing."
        response = orchestrator.execute_task("Research_Agent", task_prompt)
        print(response)

    # Example execution for Analytics_Agent
    if "Analytics_Agent" in orchestrator.agents:
        print("\nExecuting task with Analytics_Agent...")
        task_prompt = "Analyze sales data for Q1 2024."
        response = orchestrator.execute_task("Analytics_Agent", task_prompt)
        print(response)