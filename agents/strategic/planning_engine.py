import os
import json
import logging
import time
from enum import Enum
from typing import Optional, Dict, Any, List, Tuple
from dotenv import load_dotenv

load_dotenv()

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

try:
    from agents.llm_client import GroqOllamaClient, get_llm
except ModuleNotFoundError:
    from llm_client import GroqOllamaClient, get_llm

planner_logger = logging.getLogger("planning_engine")
planner_logger.setLevel(logging.INFO)


class TaskCategory(str, Enum):
    EDA = "EDA"                           # Schema Profiling & Initial Inspection
    CLEANING = "CLEANING"                 # Data Type Normalization, Null Handling & Outlier Trimming
    STATISTICS = "STATISTICS"             # Statistical Computations & Aggregations
    ML_MODELING = "ML_MODELING"           # Correlation Analysis & Predictive Modeling
    VISUALIZATION = "VISUALIZATION"       # Matplotlib / Seaborn Distribution Plots
    REPORT_SYNTHESIS = "REPORT_SYNTHESIS" # Executive Answer & Summary Compilation


class NodeContract:
    """Enterprise Contract defining inputs, outputs, preconditions, postconditions, and execution policies for a DAG Node."""
    def __init__(
        self,
        input_contract: str = "Clean DataFrame or schema context",
        output_contract: str = "JSON summary & verified data frame results",
        preconditions: Optional[List[str]] = None,
        postconditions: Optional[List[str]] = None,
        failure_policy: str = "RETRY_AND_FALLBACK",
        max_retries: int = 3,
        timeout_sec: int = 60,
        resource_type: str = "CPU",
        validator: str = "StatisticsValidator"
    ):
        self.input_contract = input_contract
        self.output_contract = output_contract
        self.preconditions = preconditions or ["non_empty_dataset"]
        self.postconditions = postconditions or ["non_empty_result"]
        self.failure_policy = failure_policy
        self.max_retries = max_retries
        self.timeout_sec = timeout_sec
        self.resource_type = resource_type
        self.validator = validator

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_contract": self.input_contract,
            "output_contract": self.output_contract,
            "preconditions": self.preconditions,
            "postconditions": self.postconditions,
            "failure_policy": self.failure_policy,
            "max_retries": self.max_retries,
            "timeout_sec": self.timeout_sec,
            "resource_type": self.resource_type,
            "validator": self.validator
        }


class DAGTaskNode:
    """Represents a single node in the Analytical Task Graph DAG with Enterprise Contracts."""
    def __init__(
        self,
        task_id: int,
        category: str,
        name: str,
        query: str,
        dependencies: Optional[List[int]] = None,
        contract: Optional[NodeContract] = None,
        confidence_score: float = 0.95
    ):
        self.task_id = task_id
        self.category = category
        self.name = name
        self.query = query
        self.dependencies = dependencies or []
        self.contract = contract or NodeContract()
        self.status = "PENDING"
        self.confidence_score = confidence_score
        self.performance_metadata = {
            "started_at": "",
            "finished_at": "",
            "runtime_sec": 0.0,
            "memory_mb": 0.0,
            "tokens_used": 0,
            "failures_count": 0,
            "retries_used": 0
        }
        self.result = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.task_id,
            "category": self.category,
            "name": self.name,
            "query": self.query,
            "dependencies": self.dependencies,
            "contract": self.contract.to_dict(),
            "status": self.status,
            "confidence_score": self.confidence_score,
            "performance_metadata": self.performance_metadata,
            "result": self.result
        }


class Estimation:
    """Resource, complexity, cost, and runtime estimations."""
    def __init__(
        self,
        dataset_rows: int = 0,
        dataset_cols: int = 0,
        complexity: str = "Medium",
        expected_runtime_sec: float = 12.0,
        expected_memory_mb: float = 250.0,
        expected_cost_tokens: int = 3500,
        risk_level: str = "Low"
    ):
        self.dataset_rows = dataset_rows
        self.dataset_cols = dataset_cols
        self.complexity = complexity
        self.expected_runtime_sec = expected_runtime_sec
        self.expected_memory_mb = expected_memory_mb
        self.expected_cost_tokens = expected_cost_tokens
        self.risk_level = risk_level

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_rows": self.dataset_rows,
            "dataset_cols": self.dataset_cols,
            "complexity": self.complexity,
            "expected_runtime_sec": self.expected_runtime_sec,
            "expected_memory_mb": self.expected_memory_mb,
            "expected_cost_tokens": self.expected_cost_tokens,
            "risk_level": self.risk_level
        }


class ExecutionManifest:
    """Enterprise Execution Manifest."""
    def __init__(
        self,
        user_query: str,
        mission: str,
        objectives: List[str],
        success_criteria: List[str],
        deliverables: List[str],
        strategy_rationale: str,
        estimation: Estimation,
        feasibility: Dict[str, Any],
        nodes: List[DAGTaskNode],
        parallel_groups: Optional[List[List[int]]] = None,
        execution_policies: Optional[Dict[str, Any]] = None,
        overall_confidence_score: float = 0.95
    ):
        self.user_query = user_query
        self.mission = mission
        self.objectives = objectives
        self.success_criteria = success_criteria
        self.deliverables = deliverables
        self.strategy_rationale = strategy_rationale
        self.estimation = estimation
        self.feasibility = feasibility
        self.nodes = nodes
        self.parallel_groups = parallel_groups or []
        self.execution_policies = execution_policies or {
            "max_runtime_sec": 120,
            "max_retries": 3,
            "max_charts": 5,
            "max_memory_mb": 2048
        }
        self.overall_confidence_score = overall_confidence_score

    def get_topological_schedule(self) -> List[DAGTaskNode]:
        node_map = {n.task_id: n for n in self.nodes}
        visited = set()
        temp_visited = set()
        order = []

        def visit(node_id: int):
            if node_id in temp_visited:
                planner_logger.warning(f"Cycle detected in DAG at node {node_id}.")
                return
            if node_id not in visited:
                temp_visited.add(node_id)
                node = node_map.get(node_id)
                if node:
                    for dep_id in node.dependencies:
                        if dep_id in node_map:
                            visit(dep_id)
                temp_visited.remove(node_id)
                visited.add(node_id)
                order.append(node_map[node_id])

        for node in self.nodes:
            if node.task_id not in visited:
                visit(node.task_id)

        return order

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_query": self.user_query,
            "mission": self.mission,
            "objectives": self.objectives,
            "success_criteria": self.success_criteria,
            "deliverables": self.deliverables,
            "strategy_rationale": self.strategy_rationale,
            "estimation": self.estimation.to_dict(),
            "feasibility": self.feasibility,
            "execution_policies": self.execution_policies,
            "parallel_groups": self.parallel_groups,
            "overall_confidence_score": self.overall_confidence_score,
            "dag_nodes": [n.to_dict() for n in self.nodes]
        }


class DAGPlan:
    def __init__(
        self,
        user_query: str,
        intent: str,
        goal: str,
        nodes: List[DAGTaskNode],
        manifest: Optional[ExecutionManifest] = None
    ):
        self.user_query = user_query
        self.intent = intent
        self.goal = goal
        self.nodes = nodes
        self.manifest = manifest

    def get_topological_schedule(self) -> List[DAGTaskNode]:
        if self.manifest:
            return self.manifest.get_topological_schedule()
        return self.nodes

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "user_query": self.user_query,
            "intent": self.intent,
            "goal": self.goal,
            "dag_nodes": [n.to_dict() for n in self.nodes]
        }
        if self.manifest:
            d["manifest"] = self.manifest.to_dict()
        return d


class PlannerMemory:
    def __init__(self, memory_file: str = "config/planner_memory.json"):
        self.memory_file = os.path.abspath(memory_file)
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        self.memory = self._load()

    def _load(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def record_experience(self, query: str, strategy: str, dataset: str, confidence: float):
        self.memory.append({
            "query": query,
            "strategy": strategy,
            "dataset": dataset,
            "confidence": confidence,
            "timestamp": time.time()
        })
        if len(self.memory) > 50:
            self.memory = self.memory[-50:]
        try:
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            planner_logger.warning(f"Failed to record planner memory: {e}")

    def find_similar_strategy(self, query: str) -> Optional[str]:
        q_words = set(query.lower().split())
        for entry in reversed(self.memory):
            mem_words = set(entry.get("query", "").lower().split())
            if len(q_words.intersection(mem_words)) >= 2 and entry.get("confidence", 0) > 0.85:
                return entry.get("strategy")
        return None


class ProjectManagerPlanningEngine:
    def __init__(self, host: Optional[str] = None, model: Optional[str] = None):
        self.client = GroqOllamaClient(host=host, model=model)
        self.llm = get_llm(model_name=model)
        self.model = model or os.getenv("GROQ_MODEL") or os.getenv("OLLAMA_MODEL") or "llama-3.3-70b-versatile"
        self.planner_memory = PlannerMemory()

    def validate_query_feasibility(
        self,
        question: str,
        columns: List[str]
    ) -> Dict[str, Any]:
        q_lower = question.lower()
        cols_lower = [c.lower() for c in columns]

        time_keywords = ["forecast", "predict future", "time series", "trend over time", "next month", "next year"]
        date_cols = [c for c in cols_lower if any(k in c for k in ["date", "time", "year", "month", "timestamp", "day"])]
        if any(tk in q_lower for tk in time_keywords) and not date_cols:
            return {
                "is_feasible": False,
                "reason": "Requested temporal forecasting, but no date/time/timestamp column was found in the dataset.",
                "missing_requirements": ["date_or_timestamp_column"],
                "suggested_alternatives": "Perform descriptive statistical ranking or distribution analysis instead of time series forecasting."
            }

        if "churn" in q_lower and not any(c in cols_lower for c in ["churn", "retention", "customer_id", "status"]):
            return {
                "is_feasible": False,
                "reason": "Requested customer churn analysis, but the dataset contains no churn/customer status features.",
                "missing_requirements": ["customer_churn_feature"],
                "suggested_alternatives": "Analyze player or record performance distribution metrics available in the current dataset."
            }

        return {
            "is_feasible": True,
            "reason": "Query is fully feasible with available dataset schema.",
            "missing_requirements": [],
            "suggested_alternatives": ""
        }

    def estimate_complexity(
        self,
        question: str,
        main_dataset: str,
        columns: List[str]
    ) -> Estimation:
        rows = 0
        if main_dataset and os.path.exists(main_dataset):
            try:
                import pandas as pd
                df_sample = pd.read_csv(main_dataset, nrows=5)
                with open(main_dataset, "rb") as f:
                    rows = sum(1 for _ in f) - 1
            except Exception:
                rows = 50000

        cols_count = len(columns)
        
        if rows > 100000 or cols_count > 50:
            complexity = "High"
            runtime_sec = 25.0
            memory_mb = 850.0
            cost_tokens = 6500
            risk = "Medium"
        elif rows > 10000:
            complexity = "Medium"
            runtime_sec = 12.0
            memory_mb = 450.0
            cost_tokens = 3800
            risk = "Low"
        else:
            complexity = "Low"
            runtime_sec = 5.0
            memory_mb = 150.0
            cost_tokens = 2200
            risk = "Low"

        return Estimation(
            dataset_rows=rows,
            dataset_cols=cols_count,
            complexity=complexity,
            expected_runtime_sec=runtime_sec,
            expected_memory_mb=memory_mb,
            expected_cost_tokens=cost_tokens,
            risk_level=risk
        )

    def plan_manifest(
        self,
        question: str,
        main_dataset: str,
        columns: List[str],
        data_quality_score: float = 80.0
    ) -> ExecutionManifest:
        planner_logger.info(f"Project Manager Planning Engine constructing Manifest for: '{question}'")

        feasibility = self.validate_query_feasibility(question, columns)
        if not feasibility["is_feasible"]:
            planner_logger.warning(f"Query refused: {feasibility['reason']}")
            return ExecutionManifest(
                user_query=question,
                mission=f"Refusal Rationale: {feasibility['reason']}",
                objectives=["Refuse infeasible query", "Provide alternative analytical options"],
                success_criteria=["Inform user of missing requirements"],
                deliverables=["refusal_notice.json"],
                strategy_rationale=f"Early Feasibility Check failed: {feasibility['reason']}. Alternative: {feasibility['suggested_alternatives']}",
                estimation=self.estimate_complexity(question, main_dataset, columns),
                feasibility=feasibility,
                nodes=[],
                parallel_groups=[],
                overall_confidence_score=0.0
            )

        estimation = self.estimate_complexity(question, main_dataset, columns)
        memory_strategy = self.planner_memory.find_similar_strategy(question)
        strategy_rationale = (
            f"Selected Pearson correlation for continuous variables, IQR outlier trimming for numerical safety, "
            f"and Seaborn KDE distribution plotting. Strategy grounded in memory: '{memory_strategy or 'Standard PM Pipeline'}'."
        )

        mission = f"Accurately answer business query '{question}' through a verified, multi-tier data pipeline."
        objectives = [
            "Perform Schema Inspection & Quality Profiling",
            "Normalize Types & Handle Missing Values",
            "Compute Required Statistical Aggregations & Metrics",
            "Generate Distribution & Metric Charts",
            "Synthesize Validated Executive Report"
        ]
        success_criteria = [
            "✓ Statistics accurately computed",
            "✓ Charts generated & saved to reports/assets/",
            "✓ Critic validation passed",
            "✓ Overall confidence score > 85%"
        ]
        deliverables = [
            "reports/latest_report.md",
            "reports/ARIA_Report_Latest.docx",
            "reports/assets/performance_score_distribution.png",
            "config/task_state.json"
        ]

        nodes = [
            DAGTaskNode(
                task_id=1,
                category="EDA",
                name="Schema Inspection & Quality Profiling",
                query=f"Inspect schema and profile data quality for: {question}",
                dependencies=[],
                contract=NodeContract(
                    input_contract="Raw CSV Dataset file path",
                    output_contract="Schema profile JSON & column datatypes",
                    preconditions=["file_exists", "readable_csv"],
                    postconditions=["non_empty_columns"],
                    resource_type="CPU",
                    validator="EDAValidator"
                )
            ),
            DAGTaskNode(
                task_id=2,
                category="CLEANING",
                name="Type Normalization & Missing Value Cleaning",
                query=f"Normalize column types and clean nulls/outliers for: {question}",
                dependencies=[1],
                contract=NodeContract(
                    input_contract="Schema profile & dataset path",
                    output_contract="Cleaned pandas DataFrame in sandbox memory",
                    preconditions=["valid_schema"],
                    postconditions=["numeric_types_converted"],
                    resource_type="SANDBOX",
                    validator="CleaningValidator"
                )
            ),
            DAGTaskNode(
                task_id=3,
                category="STATISTICS",
                name="Statistical Computation & Metric Aggregation",
                query=f"Compute statistical metrics and aggregations for: {question}",
                dependencies=[2],
                contract=NodeContract(
                    input_contract="Cleaned pandas DataFrame",
                    output_contract="Summary statistics dictionary & top metrics",
                    preconditions=["numeric_columns_present"],
                    postconditions=["valid_summary_statistics"],
                    resource_type="SANDBOX",
                    validator="StatisticsValidator"
                )
            ),
            DAGTaskNode(
                task_id=4,
                category="VISUALIZATION",
                name="Distribution Plotting & Chart Generation",
                query=f"Generate visual plots illustrating distribution for: {question}",
                dependencies=[2],
                contract=NodeContract(
                    input_contract="Cleaned pandas DataFrame",
                    output_contract="Saved PNG plot file paths",
                    preconditions=["numeric_columns_present"],
                    postconditions=["png_files_saved"],
                    resource_type="SANDBOX",
                    validator="VisualizationValidator"
                )
            ),
            DAGTaskNode(
                task_id=5,
                category="REPORT_SYNTHESIS",
                name="Executive Report & Answer Synthesis",
                query=f"Synthesize final executive answer and report for: {question}",
                dependencies=[3, 4],
                contract=NodeContract(
                    input_contract="Verified statistics & saved plot paths",
                    output_contract="Markdown & DOCX Executive Report",
                    preconditions=["statistics_available", "plots_available"],
                    postconditions=["report_file_created"],
                    resource_type="LLM",
                    validator="ReportValidator"
                )
            )
        ]

        parallel_groups = [
            [1],
            [2],
            [3, 4],
            [5]
        ]

        manifest = ExecutionManifest(
            user_query=question,
            mission=mission,
            objectives=objectives,
            success_criteria=success_criteria,
            deliverables=deliverables,
            strategy_rationale=strategy_rationale,
            estimation=estimation,
            feasibility=feasibility,
            nodes=nodes,
            parallel_groups=parallel_groups,
            overall_confidence_score=0.95
        )

        self.planner_memory.record_experience(question, strategy_rationale, main_dataset, 0.95)
        return manifest

    def plan_dag(
        self,
        question: str,
        main_dataset: str,
        columns: List[str],
        data_quality_score: float = 80.0
    ) -> DAGPlan:
        manifest = self.plan_manifest(question, main_dataset, columns, data_quality_score)
        intent = "Analytical Query Execution"
        goal = question
        if manifest.nodes:
            intent = f"Mission: {manifest.mission}"
            goal = f"Objectives: {', '.join(manifest.objectives[:2])}"
            
        return DAGPlan(
            user_query=question,
            intent=intent,
            goal=goal,
            nodes=manifest.nodes,
            manifest=manifest
        )

PlanningAgent = ProjectManagerPlanningEngine
