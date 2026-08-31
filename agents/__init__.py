# Orchestra Intelligence Engine Package
import os
import sys

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from agents.strategic.planning_agent import PlanningAgent
from agents.strategic.planning_engine import ProjectManagerPlanningEngine, ExecutionManifest, DAGPlan, DAGTaskNode, NodeContract, Estimation
from agents.data_science.data_agent import DataAgent, run_python_code, execute_sandbox_code
from agents.data_science.preprocessing_agent import DataPreprocessingAgent
from agents.engineering.debug_agent import EnterpriseDebugAgent, DebugAgent, CodeExecutionError, DebugAttempt, DebugAgentOutput
from agents.engineering.debug_classifier import ErrorClassifier, ErrorCategory
from agents.engineering.debug_root_cause import RootCauseAnalyzer
from agents.engineering.debug_patcher import DeterministicPatchEngine
from agents.engineering.debug_validator import DebugValidatorAndMemory
from agents.audit.critic_agent import CriticAgent, ValidationResult
from agents.synthesis.report_writer import ReportWriter
from agents.deterministic.deterministic_engine import DeterministicComputeEngine
from agents.deterministic.pre_planner import RuleBasedPrePlanner
from agents.deterministic.dataset_profile_store import DatasetProfileStore
from agents.deterministic.analysis_router import AlgorithmicAnalysisRouter
from agents.orchestration.async_dag_scheduler import AsyncDAGScheduler
from agents.orchestration.execution_cache import ExecutionStateCache
from agents.orchestration.stage_profiler import StageProfiler
from agents.orchestration.telemetry_streamer import TelemetryStreamer
from agents.orchestration.prompt_pruner import PromptPruner

__all__ = [
    # Tier 1 Strategic
    "PlanningAgent",
    "ProjectManagerPlanningEngine",
    "ExecutionManifest",
    "DAGPlan",
    "DAGTaskNode",
    "NodeContract",
    "Estimation",
    
    # Tier 2 Data Science
    "DataAgent",
    "run_python_code",
    "execute_sandbox_code",
    "DataPreprocessingAgent",
    
    # Tier 3 Engineering Debugger
    "EnterpriseDebugAgent",
    "DebugAgent",
    "CodeExecutionError",
    "DebugAttempt",
    "DebugAgentOutput",
    "ErrorClassifier",
    "ErrorCategory",
    "RootCauseAnalyzer",
    "DeterministicPatchEngine",
    "DebugValidatorAndMemory",
    
    # Tier 4 Audit
    "CriticAgent",
    "ValidationResult",
    
    # Tier 5 Synthesis
    "ReportWriter",
    
    # Tier 6 Deterministic
    "DeterministicComputeEngine",
    "RuleBasedPrePlanner",
    "DatasetProfileStore",
    "AlgorithmicAnalysisRouter",
    
    # Tier 7 Orchestration
    "AsyncDAGScheduler",
    "ExecutionStateCache",
    "StageProfiler",
    "TelemetryStreamer",
    "PromptPruner"
]
