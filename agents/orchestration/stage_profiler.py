import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("stage_profiler")

@dataclass
class StageMetric:
    stage_name: str
    duration_sec: float
    start_time: float
    end_time: float
    success: bool = True
    details: Dict[str, Any] = field(default_factory=dict)

class StageProfiler:
    def __init__(self):
        self.metrics: List[StageMetric] = []
        self.total_start_time: float = time.perf_counter()

    def start_stage(self, stage_name: str) -> float:
        return time.perf_counter()

    def end_stage(self, stage_name: str, start_time: float, success: bool = True, details: Optional[Dict[str, Any]] = None) -> StageMetric:
        end_time = time.perf_counter()
        duration = round(end_time - start_time, 4)
        metric = StageMetric(
            stage_name=stage_name,
            duration_sec=duration,
            start_time=start_time,
            end_time=end_time,
            success=success,
            details=details or {}
        )
        self.metrics.append(metric)
        return metric

    def get_summary_table(self) -> str:
        total_duration = round(time.perf_counter() - self.total_start_time, 4)
        lines = [
            "==================================================",
            "        STAGE LATENCY TELEMETRY REPORT           ",
            "==================================================",
            f"{'Stage Name':<30} | {'Duration (s)':<12} | {'Status':<8}",
            "--------------------------------------------------"
        ]
        for m in self.metrics:
            status = "SUCCESS" if m.success else "FAILED"
            lines.append(f"{m.stage_name:<30} | {m.duration_sec:<12.4f} | {status:<8}")
        lines.append("--------------------------------------------------")
        lines.append(f"{'TOTAL PIPELINE TIME':<30} | {total_duration:<12.4f} | COMPLETED")
        lines.append("==================================================")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_duration_sec": round(time.perf_counter() - self.total_start_time, 4),
            "stages": [
                {
                    "stage_name": m.stage_name,
                    "duration_sec": m.duration_sec,
                    "success": m.success,
                    "details": m.details
                }
                for m in self.metrics
            ]
        }
