"""
agents/orchestrator.py - Backward Compatibility Wrapper
The Orchestrator agent has been replaced by the PlanningAgent (Project Manager Planning Engine).
"""
import os
import sys

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

try:
    from agents.strategic.planning_agent import PlanningAgent
except ModuleNotFoundError:
    from strategic.planning_agent import PlanningAgent

# Alias OrchestratorAgent to PlanningAgent for backward compatibility
OrchestratorAgent = PlanningAgent

if __name__ == "__main__":
    import sys
    import glob
    import os
    if len(sys.argv) > 1:
        query = sys.argv[1]
    else:
        try:
            user_input = input("Please enter your analytical query: ").strip()
            if user_input:
                query = user_input
            else:
                csv_files = [os.path.basename(f) for f in glob.glob("data/*.csv")]
                query = f"What are the key summary statistics of {csv_files[0]}?" if csv_files else "Analyze the dataset and summarize key findings."
        except Exception:
            csv_files = [os.path.basename(f) for f in glob.glob("data/*.csv")]
            query = f"What are the key summary statistics of {csv_files[0]}?" if csv_files else "Analyze the dataset and summarize key findings."

    print(f"Running PlanningAgent (Orchestrator compatibility wrapper) CLI for query: '{query}'\n")
    agent = PlanningAgent()
    result_state = agent.plan_and_execute(query)
    print("\n--- FINAL SUMMARY ---")
    print(result_state.get("final_summary", "No summary generated."))
    print(f"\nReport saved to: {result_state.get('report_path')}")
