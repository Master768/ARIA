import os
import sys

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from agents.deterministic.deterministic_engine import DeterministicComputeEngine
from agents.deterministic.pre_planner import RuleBasedPrePlanner
from agents.deterministic.dataset_profile_store import DatasetProfileStore
from agents.deterministic.analysis_router import AlgorithmicAnalysisRouter
from agents.deterministic.dataset_intelligence_engine import (
    DatasetIntelligenceEngine,
    SemanticTypeDetector,
    BusinessMeaningInferencer,
    TargetDetector
)

__all__ = [
    "DeterministicComputeEngine",
    "RuleBasedPrePlanner",
    "DatasetProfileStore",
    "AlgorithmicAnalysisRouter",
    "DatasetIntelligenceEngine",
    "SemanticTypeDetector",
    "BusinessMeaningInferencer",
    "TargetDetector"
]
