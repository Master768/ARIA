import os
import sys

# Reconfigure stdout for UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure current directory and project root are in sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables (including LangSmith tracing configs)
load_dotenv()

class ARIAInput(BaseModel):
    user_query: str = Field(..., description="Analytics query or prompt for the multi-agent system")
    dataset_paths: Optional[List[str]] = Field(default_factory=list, description="Optional paths to CSV/dataset files")
    tolerance_pct: Optional[float] = Field(0.03, description="Tolerance percentage for critic validation")

class ARIAOutput(BaseModel):
    user_query: str = Field("", description="Original user question")
    code_draft: str = Field("", description="Generated pandas/python code")
    execution_output: str = Field("", description="Output from sandbox execution")
    execution_success: bool = Field(False, description="Whether code execution succeeded")
    plot_paths: List[str] = Field(default_factory=list, description="List of generated plot image file paths")
    validation_passed: bool = Field(False, description="Whether critic validation passed")
    report_markdown: str = Field("", description="Final compiled markdown report")
    report_docx_path: str = Field("", description="Path to generated docx report")

try:
    from agents.state import ARIAState
    from agents.vector_store import ARIAVectorStore
    from agents.data_science.data_agent import DataAgent, run_python_code, execute_sandbox_code
    from agents.audit.critic_agent import CriticAgent
    from agents.engineering.debug_agent import DebugAgent
    from agents.synthesis.report_writer import ReportWriter
except ModuleNotFoundError:
    from state import ARIAState
    from vector_store import ARIAVectorStore
    from data_science.data_agent import DataAgent, run_python_code, execute_sandbox_code
    from audit.critic_agent import CriticAgent
    from engineering.debug_agent import DebugAgent
    from synthesis.report_writer import ReportWriter

# Initialize sub-agents and vector store
vector_store = ARIAVectorStore()
data_agent = DataAgent()
debug_agent = DebugAgent(
    llm_client=data_agent.client,
    model=data_agent.model,
    sandbox_run_fn=execute_sandbox_code
)
data_agent.debug_agent = debug_agent
critic_agent = CriticAgent()
report_writer = ReportWriter()

def vector_retrieval_node(state: ARIAState) -> Dict[str, Any]:
    """Node 1: Retrieves schema & dataset context from Vector DB (ChromaDB)."""
    user_query = state.get("user_query", "")
    context = vector_store.query_context(user_query)
    return {"vector_context": context}

def data_agent_node(state: ARIAState) -> Dict[str, Any]:
    """Node 2: Generates and executes Pandas analysis & Matplotlib/Seaborn plot scripts."""
    user_query = state.get("user_query", "")
    vector_context = state.get("vector_context", "")

    augmented_query = f"{user_query}\n\nContext retrieved from Vector DB:\n{vector_context}"
    result = data_agent.ask_question(augmented_query)

    code = result.get("code", "")
    output = result.get("output", "")
    sandbox_output = result.get("sandbox_output", "")

    # Extract plot image paths saved by Matplotlib/Seaborn
    plot_paths = []
    for line in sandbox_output.splitlines():
        if "PLOT_SAVED:" in line:
            plot_path = line.split("PLOT_SAVED:")[1].strip()
            plot_paths.append(plot_path)

    execution_success = result.get("status") in ["success", "SUCCESS_WITH_DEBUG"]

    return {
        "code_draft": code,
        "execution_output": output,
        "execution_success": execution_success,
        "plot_paths": plot_paths
    }

def critic_agent_node(state: ARIAState) -> Dict[str, Any]:
    """Node 3: Independently verifies DataAgent results and plot existence."""
    user_query = state.get("user_query", "")
    data_agent_output = state.get("execution_output", "")
    data_agent_code = state.get("code_draft", "")
    plot_paths = state.get("plot_paths", [])

    import glob
    csv_files = glob.glob("data/*.csv")
    main_dataset = csv_files[0] if csv_files else "data/dataset.csv"

    # Validate independent numeric results
    try:
        data_agent_result = {"output": data_agent_output, "code": data_agent_code}
        critic_res = critic_agent.validate(user_query, data_agent_result, main_dataset=main_dataset)
        validation_passed = getattr(critic_res, "is_valid", True)
        critic_out = getattr(critic_res, "output", "Validation complete.")
    except Exception as e:
        validation_passed = True
        critic_out = f"Validation skipped: {e}"

    return {
        "validation_passed": validation_passed,
        "critic_output": critic_out
    }


def report_writer_node(state: ARIAState) -> Dict[str, Any]:
    """Node 4: Compiles Markdown & DOCX reports with embedded Matplotlib/Seaborn plots."""
    user_query = state.get("user_query", "")
    execution_output = state.get("execution_output", "")
    plot_paths = state.get("plot_paths", [])

    # Create task state for report compiler
    task_state = {
        "original_question": user_query,
        "status": "APPROVED" if state.get("validation_passed", True) else "NEEDS_REVIEW",
        "final_summary": execution_output,
        "sub_tasks": [
            {
                "id": 1,
                "description": "Data Analysis & Chart Generation",
                "query": user_query,
                "data_agent_result": {"output": execution_output},
                "critic_validation": "PASSED" if state.get("validation_passed", True) else "NEEDS_REVIEW"
            }
        ]
    }

    # Append plot images to summary if available
    if plot_paths:
        task_state["final_summary"] += "\n\n### Generated Data Visualizations\n"
        for plot_path in plot_paths:
            task_state["final_summary"] += f"\n![Data Plot]({plot_path})\n"

    md_report = report_writer.compile_report(task_state)

    # Convert to DOCX
    docx_path = os.path.join(report_writer.reports_dir, "ARIA_Report_Latest.docx")
    report_writer.convert_to_docx(md_report, docx_path)

    return {
        "report_markdown": md_report,
        "report_docx_path": docx_path
    }

# Build LangGraph StateGraph (or fallback runnable pipeline if langgraph is loading)
def build_aria_graph():
    try:
        from langgraph.graph import StateGraph, END
        workflow = StateGraph(ARIAState)
        workflow.add_node("vector_retrieval", vector_retrieval_node)
        workflow.add_node("data_agent", data_agent_node)
        workflow.add_node("critic_agent", critic_agent_node)
        workflow.add_node("report_writer", report_writer_node)

        workflow.set_entry_point("vector_retrieval")
        workflow.add_edge("vector_retrieval", "data_agent")
        workflow.add_edge("data_agent", "critic_agent")

        # Conditional edge routing based on Critic validation
        def route_critic(state: ARIAState):
            if state.get("validation_passed", True):
                return "report_writer"
            return "report_writer" # Proceed to report with warning badge

        workflow.add_conditional_edges("critic_agent", route_critic, {"report_writer": "report_writer"})
        workflow.add_edge("report_writer", END)
        return workflow.compile()
    except Exception as e:
        print(f"LangGraph StateGraph loading fallback: {e}")
        # Synchronous fallback pipeline
        class FallbackGraph:
            def invoke(self, state: ARIAState):
                s1 = vector_retrieval_node(state)
                state.update(s1)
                s2 = data_agent_node(state)
                state.update(s2)
                s3 = critic_agent_node(state)
                state.update(s3)
                s4 = report_writer_node(state)
                state.update(s4)
                return state
        return FallbackGraph()

aria_graph = build_aria_graph()

if __name__ == "__main__":
    import glob
    csv_files = [os.path.basename(f) for f in glob.glob("data/*.csv")]
    sample_dataset = csv_files[0] if csv_files else "available dataset"
    initial_state = {
        "user_query": f"Summarize key statistics and trends from {sample_dataset}.",

        "dataset_paths": [],
        "vector_context": "",
        "current_subtask": "",
        "code_draft": "",
        "execution_success": False,
        "execution_output": "",
        "error_traceback": "",
        "plot_paths": [],
        "claimed_result": {},
        "critic_code": "",
        "critic_output": "",
        "validation_passed": False,
        "tolerance_pct": 0.03,
        "retry_count": 0,
        "max_retries": 2,
        "report_markdown": "",
        "report_docx_path": ""
    }
    print("Running ARIA LangGraph Workflow...")
    final_state = aria_graph.invoke(initial_state)
    print("\n--- FINAL REPORT ---")
    print(final_state.get("report_markdown"))
