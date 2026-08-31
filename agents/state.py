from typing import TypedDict, List, Optional, Dict, Any

class ARIAState(TypedDict):
    """
    LangGraph State Schema for ARIA Multi-Agent Execution.
    Tracks state across vector retrieval, data analysis, plot generation, 
    independent validation, auto-repair, and report publishing.
    """
    user_query: str
    dataset_paths: List[str]
    vector_context: str
    current_subtask: str
    code_draft: str
    execution_success: bool
    execution_output: str
    error_traceback: str
    plot_paths: List[str]
    claimed_result: Dict[str, Any]
    critic_code: str
    critic_output: str
    validation_passed: bool
    tolerance_pct: float
    retry_count: int
    max_retries: int
    report_markdown: str
    report_docx_path: str
