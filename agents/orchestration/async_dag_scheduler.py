import os
import time
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Set
from concurrent.futures import ThreadPoolExecutor

try:
    from agents.orchestration.stage_profiler import StageProfiler
    from agents.orchestration.execution_cache import ExecutionStateCache
    from agents.orchestration.telemetry_streamer import TelemetryStreamer
    from agents.deterministic.deterministic_engine import DeterministicComputeEngine
except ModuleNotFoundError:
    from stage_profiler import StageProfiler
    from execution_cache import ExecutionStateCache
    from telemetry_streamer import TelemetryStreamer
    from deterministic_engine import DeterministicComputeEngine

logger = logging.getLogger("async_dag_scheduler")

class AsyncDAGScheduler:
    """Tier 7 Concurrency & Orchestration Scheduler."""
    def __init__(
        self,
        profiler: Optional[StageProfiler] = None,
        cache: Optional[ExecutionStateCache] = None,
        streamer: Optional[TelemetryStreamer] = None,
        max_workers: int = 4
    ):
        self.profiler = profiler or StageProfiler()
        self.cache = cache or ExecutionStateCache()
        self.streamer = streamer or TelemetryStreamer()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    async def execute_dag(
        self,
        dag_manifest: Dict[str, Any],
        node_executors: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        manifest_id = dag_manifest.get("manifest_id", "manifest_default")
        nodes: List[Dict[str, Any]] = dag_manifest.get("nodes", [])

        self.streamer.emit("DAG_START", f"Starting execution of DAG '{manifest_id}' with {len(nodes)} nodes")

        node_map: Dict[str, Dict[str, Any]] = {n["id"]: n for n in nodes}
        in_degree: Dict[str, int] = {n["id"]: 0 for n in nodes}
        children: Dict[str, List[str]] = {n["id"]: [] for n in nodes}

        for n in nodes:
            deps = n.get("depends_on", [])
            in_degree[n["id"]] = len(deps)
            for dep in deps:
                if dep in children:
                    children[dep].append(n["id"])

        completed_nodes: Set[str] = set()
        failed_nodes: Set[str] = set()
        node_outputs: Dict[str, Any] = {}
        prior_facts: Dict[str, str] = {}

        # Shared Execution Context
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        sandbox_cleaned_csv = os.path.join(project_root, "sandbox", "cleaned_dataset.csv")
        if os.path.exists(sandbox_cleaned_csv):
            context["cleaned_dataset_path"] = sandbox_cleaned_csv

        while len(completed_nodes) + len(failed_nodes) < len(nodes):
            ready_node_ids = [
                nid for nid, deg in in_degree.items()
                if deg == 0 and nid not in completed_nodes and nid not in failed_nodes
            ]

            if not ready_node_ids:
                break

            self.streamer.emit("PARALLEL_BATCH", f"Executing {len(ready_node_ids)} independent nodes in parallel: {ready_node_ids}")

            # Inject prior node facts into context
            context["prior_node_facts"] = prior_facts

            tasks = [
                self._execute_single_node(node_map[nid], node_executors, context, node_outputs)
                for nid in ready_node_ids
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for nid, res in zip(ready_node_ids, results):
                if isinstance(res, Exception):
                    failed_nodes.add(nid)
                    node_outputs[nid] = {"status": "error", "error": str(res)}
                else:
                    completed_nodes.add(nid)
                    node_outputs[nid] = res
                    # Collect facts
                    if isinstance(res, dict) and "output" in res:
                        prior_facts[nid] = str(res["output"])[:300]

                    # Check if cleaned dataset was produced
                    if os.path.exists(sandbox_cleaned_csv):
                        context["cleaned_dataset_path"] = sandbox_cleaned_csv

                for child_id in children.get(nid, []):
                    in_degree[child_id] -= 1

        context["node_outputs"] = node_outputs
        context["completed_nodes"] = list(completed_nodes)
        context["latency_summary"] = self.profiler.to_dict()
        return context

    async def _execute_single_node(
        self,
        node: Dict[str, Any],
        node_executors: Dict[str, Any],
        context: Dict[str, Any],
        node_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        node_id = node["id"]
        node_name = node.get("name", node_id)
        agent_type = node.get("agent", "data_agent")

        start_time = self.profiler.start_stage(f"Node:{node_name}")
        self.streamer.emit("NODE_START", f"Starting execution of node '{node_name}' ({agent_type})")

        if agent_type == "deterministic_engine":
            csv_path = context.get("main_dataset", "")
            ops = node.get("operations", ["inspect", "statistics"])
            det_res = DeterministicComputeEngine.execute_deterministic_pipeline(csv_path, ops)
            self.profiler.end_stage(f"Node:{node_name}", start_time, success=True)
            return {"status": "success", "deterministic_result": det_res}

        fn = node_executors.get(agent_type) or node_executors.get(node_id)
        if not fn:
            self.profiler.end_stage(f"Node:{node_name}", start_time, success=True)
            return {"status": "success", "output": f"Executed dummy agent node '{node_name}'"}

        loop = asyncio.get_running_loop()
        try:
            if asyncio.iscoroutinefunction(fn):
                res = await fn(node, context, node_outputs)
            else:
                res = await loop.run_in_executor(self.executor, fn, node, context, node_outputs)

            self.profiler.end_stage(f"Node:{node_name}", start_time, success=True)
            return res
        except Exception as e:
            self.profiler.end_stage(f"Node:{node_name}", start_time, success=False, details={"error": str(e)})
            raise e
