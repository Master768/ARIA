import os
import json
import logging
import time
import re
import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

import sys
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dotenv import load_dotenv
load_dotenv()

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel

try:
    from agents.llm_client import GroqOllamaClient, get_llm
    from agents.data_science.data_agent import DataAgent, run_python_code, execute_sandbox_code
    from agents.audit.critic_agent import CriticAgent
    from agents.synthesis.report_writer import ReportWriter
    from agents.engineering.debug_agent import DebugAgent
    from agents.data_science.preprocessing_agent import DataPreprocessingAgent
    from agents.strategic.planning_engine import (
        ProjectManagerPlanningEngine,
        ExecutionManifest,
        DAGPlan,
        DAGTaskNode,
        NodeContract,
        Estimation
    )
    from agents.orchestration.stage_profiler import StageProfiler
    from agents.deterministic.dataset_profile_store import DatasetProfileStore
    from agents.deterministic.deterministic_engine import DeterministicComputeEngine
    from agents.deterministic.analysis_router import AlgorithmicAnalysisRouter
    from agents.deterministic.pre_planner import RuleBasedPrePlanner
    from agents.orchestration.execution_cache import ExecutionStateCache
    from agents.orchestration.prompt_pruner import PromptPruner
    from agents.orchestration.telemetry_streamer import TelemetryStreamer
    from agents.orchestration.async_dag_scheduler import AsyncDAGScheduler
except ModuleNotFoundError:
    from agents.llm_client import GroqOllamaClient, get_llm
    from agents.data_science.data_agent import DataAgent, run_python_code, execute_sandbox_code
    from agents.audit.critic_agent import CriticAgent
    from agents.synthesis.report_writer import ReportWriter
    from agents.engineering.debug_agent import DebugAgent
    from agents.data_science.preprocessing_agent import DataPreprocessingAgent
    from agents.strategic.planning_engine import (
        ProjectManagerPlanningEngine,
        ExecutionManifest,
        DAGPlan,
        DAGTaskNode,
        NodeContract,
        Estimation
    )
    from agents.orchestration.stage_profiler import StageProfiler
    from agents.deterministic.dataset_profile_store import DatasetProfileStore
    from agents.deterministic.deterministic_engine import DeterministicComputeEngine
    from agents.deterministic.analysis_router import AlgorithmicAnalysisRouter
    from agents.deterministic.pre_planner import RuleBasedPrePlanner
    from agents.orchestration.execution_cache import ExecutionStateCache
    from agents.orchestration.prompt_pruner import PromptPruner
    from agents.orchestration.telemetry_streamer import TelemetryStreamer
    from agents.orchestration.async_dag_scheduler import AsyncDAGScheduler


log_dir = os.path.abspath("logs")
os.makedirs(log_dir, exist_ok=True)
planner_agent_logger = logging.getLogger("planning_agent")
planner_agent_logger.setLevel(logging.INFO)

if not planner_agent_logger.handlers:
    fh = logging.FileHandler(os.path.join(log_dir, "planning_agent.log"), encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    planner_agent_logger.addHandler(fh)


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

class PlanningAgent:
    """
    Tier 1 Strategic Intelligence: PlanningAgent.
    Manages high-level intent recognition, multi-agent orchestration, and performance profiling.
    """
    def __init__(self, host: Optional[str] = None, model: Optional[str] = None):
        self.client = GroqOllamaClient(host=host, model=model)
        self.llm = get_llm(model_name=model)
        self.model = model or os.getenv("GROQ_MODEL", os.getenv("OLLAMA_MODEL", "gpt-oss:20b-cloud"))

        self.debug_agent = DebugAgent(self.client, model=self.model, sandbox_run_fn=execute_sandbox_code)
        self.data_agent = DataAgent(host=host, model=model, debug_agent=self.debug_agent)
        self.critic_agent = CriticAgent(host=host, model=model)
        self.report_writer = ReportWriter()
        self.preprocessing_agent = DataPreprocessingAgent(llm_client=self.client)
        self.planning_engine = ProjectManagerPlanningEngine(host=host, model=model)
        
        self.profile_store = DatasetProfileStore()
        self.execution_cache = ExecutionStateCache()
        self.telemetry = TelemetryStreamer()
        self.profiler = StageProfiler()
        self.dag_scheduler = AsyncDAGScheduler(profiler=self.profiler, cache=self.execution_cache, streamer=self.telemetry)

        self.config_dir = os.path.join(PROJECT_ROOT, "config")
        os.makedirs(self.config_dir, exist_ok=True)
        self.state_file = os.path.join(self.config_dir, "task_state.json")

    def _write_state(self, state: dict):
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    def plan_and_execute(self, question: str) -> dict:
        self.profiler = StageProfiler()
        t_init = self.profiler.start_stage("DatasetSelection & Profiling")
        
        planner_agent_logger.info(f"[PlanningAgent] Received query for Manifest planning: '{question}'")
        
        data_dir = os.path.join(PROJECT_ROOT, "data")
        data_files = []
        try:
            data_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
        except Exception:
            pass
        
        DOMAIN_SYNONYMS = {
            "bitcoin": ["btc", "binance", "crypto", "usdt"],
            "crypto":  ["btc", "binance", "usdt", "eth"],
            "btc":     ["btc", "binance"],
            "price":   ["btc", "binance", "stock", "ohlc"],
            "stock":   ["stock", "ohlc", "sp500"],
            "churn":   ["churn", "telecom", "telco"],
            "customer":["churn", "telecom", "crm"],
            "amazon":  ["amazon"],
            "sales":   ["sales", "revenue"],
            "fifa":    ["fifa", "player", "performance", "world_cup"],
            "player":  ["fifa", "player", "performance", "goals"],
        }

        def _score_file(filename: str) -> int:
            score = 0
            name_no_ext = os.path.splitext(filename)[0].lower()
            name_tokens = set(name_no_ext.replace('_', ' ').replace('-', ' ').split())
            q_lower = question.lower()
            q_words_regex = set(re.findall(r'[a-zA-Z0-9_]+', q_lower))

            if name_no_ext in q_lower or filename.lower() in q_lower:
                score += 1000
            for token in name_tokens:
                if len(token) >= 3 and token in q_words_regex:
                    score += 50
                for kw, syns in DOMAIN_SYNONYMS.items():
                    if kw in q_words_regex and token in syns:
                        score += 30
            return score

        if data_files:
            scored = sorted(data_files, key=_score_file, reverse=True)
            selected_file = scored[0] if _score_file(scored[0]) > 0 else data_files[0]
            main_dataset = os.path.join(data_dir, selected_file)
        else:
            main_dataset = ""

        ds_profile = self.profile_store.get_or_create_profile(main_dataset) if main_dataset else {}
        dataset_sha256 = ds_profile.get("sha256", "nohash")
        columns = ds_profile.get("columns", [])
        self.profiler.end_stage("DatasetSelection & Profiling", t_init, success=True)

        cached_state = self.execution_cache.get(dataset_sha256, question, "full_execution")
        if cached_state:
            self.telemetry.emit("CACHE_HIT", f"Reusing cached analysis result for '{question}'")
            return cached_state

        fast_dag = RuleBasedPrePlanner.create_fast_dag(question, main_dataset)
        if fast_dag:
            self.telemetry.emit("FAST_PATH", f"Matched Rule-Based Fast-Path DAG '{fast_dag['intent']}' (skipping LLM planning)")
            manifest_dict = fast_dag
        else:
            t_plan = self.profiler.start_stage("PM Planning Engine")
            print(f"\n📋  [PlanningAgent] Generating Enterprise Execution Manifest & Strategy...", flush=True)
            manifest = self.planning_engine.plan_manifest(
                question=question,
                main_dataset=main_dataset,
                columns=columns,
                data_quality_score=85.0
            )
            self.profiler.end_stage("PM Planning Engine", t_plan, success=True)

            if not manifest.feasibility.get("is_feasible", True):
                refusal_reason = manifest.feasibility.get("reason", "Query infeasible with current dataset.")
                refusal_summary = f"### ❌ Analytical Refusal Notice\n\n**Reason:** {refusal_reason}"
                refusal_state = {
                    "task_id": 1,
                    "original_question": question,
                    "main_dataset": main_dataset,
                    "status": "REFUSED",
                    "final_summary": refusal_summary,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                return refusal_state

            scheduled_nodes = manifest.get_topological_schedule()
            manifest_dict = {
                "manifest_id": manifest.mission,
                "main_dataset": main_dataset,
                "nodes": [
                    {
                        "id": f"node_{n.task_id}",
                        "name": n.name,
                        "agent": n.category.lower(),
                        "query": n.query,
                        "depends_on": [f"node_{dep}" for dep in n.dependencies]
                    }
                    for n in scheduled_nodes
                ]
            }

        t_exec = self.profiler.start_stage("Async Parallel DAG Execution")
        
        def data_agent_executor(node, ctx, prev_outputs):
            sub_query = node.get("query", question)
            return self.data_agent.ask_question(sub_query)

        def report_writer_executor(node, ctx, prev_outputs):
            return {"status": "success", "summary": "Report sections compiled"}

        executors = {
            "eda": data_agent_executor,
            "cleaning": data_agent_executor,
            "statistics": data_agent_executor,
            "visualization": data_agent_executor,
            "report_synthesis": report_writer_executor,
            "data_agent": data_agent_executor,
            "preprocessing_agent": data_agent_executor,
            "report_writer": report_writer_executor
        }

        context = {
            "main_dataset": main_dataset,
            "dataset_profile": ds_profile,
            "question": question
        }

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            exec_ctx = loop.run_until_complete(
                self.dag_scheduler.execute_dag(manifest_dict, executors, context)
            )
        finally:
            loop.close()

        self.profiler.end_stage("Async Parallel DAG Execution", t_exec, success=True)

        t_rep = self.profiler.start_stage("Final Report Compilation")
        node_outputs = exec_ctx.get("node_outputs", {})
        
        import pandas as pd
        native_stats = DeterministicComputeEngine.compute_summary_statistics(
            pd.read_csv(main_dataset) if main_dataset and os.path.exists(main_dataset) else None
        ) if main_dataset and os.path.exists(main_dataset) else {}

        summary_text = f"# Executive Analytics Summary\n\n**Query:** '{question}'\n\n"
        
        ds_intel = ds_profile.get("dataset_intelligence", {})
        if ds_intel:
            target_det = ds_intel.get("target_detection", {})
            prob_type = ds_intel.get("inferred_problem_type", "N/A")
            target_col = target_det.get("target_column", "N/A")
            feat_imp = ds_intel.get("feature_importance", {})
            suggested_pipes = ds_intel.get("suggested_pipelines", [])

            summary_text += "### 🧠 Dataset Intelligence & Automated Problem Inference\n"
            summary_text += f"- **Inferred Target Column:** `{target_col}` (Method: {target_det.get('detection_method')}, Confidence: {target_det.get('confidence', 0)*100:.0f}%)\n"
            summary_text += f"- **Inferred Problem Type:** `{prob_type}`\n"
            if feat_imp:
                top_imp = ", ".join([f"`{k}` ({v*100:.1f}%)" for k, v in list(feat_imp.items())[:3]])
                summary_text += f"- **Top Machine-Learned Drivers:** {top_imp}\n"
            if suggested_pipes:
                summary_text += "- **Recommended Pipelines:**\n"
                for pipe in suggested_pipes:
                    summary_text += f"  - {pipe}\n"
            summary_text += "\n"

        if native_stats:
            summary_text += "### 📊 Computed Key Numeric Statistics (Native Engine):\n"
            for col, s in list(native_stats.items())[:5]:
                summary_text += f"- **{col}**: Mean={s.get('mean', 0):.2f}, Std={s.get('std', 0):.2f}, Median={s.get('50%', 0):.2f}\n"
            summary_text += "\n"

        for nid, nres in node_outputs.items():
            if isinstance(nres, dict):
                out_content = nres.get("output") or nres.get("summary") or nres.get("deterministic_result") or str(nres)
                summary_text += f"### 🔍 Analysis Node `{nid}` Findings:\n{out_content}\n\n"
            elif nres:
                summary_text += f"### 🔍 Analysis Node `{nid}` Findings:\n{nres}\n\n"

        state = {
            "task_id": 1,
            "original_question": question,
            "main_dataset": main_dataset,
            "status": "COMPLETED",
            "final_summary": summary_text,
            "latency_breakdown": self.profiler.to_dict(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        md_report = self.report_writer.compile_report(state)
        report_file = os.path.join("reports", f"report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md")
        os.makedirs("reports", exist_ok=True)
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(md_report)

        latest_report = os.path.join("reports", "latest_report.md")
        with open(latest_report, "w", encoding="utf-8") as f:
            f.write(md_report)

        state["report_path"] = report_file
        self._write_state(state)
        self.profiler.end_stage("Final Report Compilation", t_rep, success=True)

        self.execution_cache.put(dataset_sha256, question, "full_execution", state)

        print("\n" + self.profiler.get_summary_table())

        return state
