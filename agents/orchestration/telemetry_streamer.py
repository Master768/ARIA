import time
import logging
from typing import Callable, Optional, Dict, Any, List

logger = logging.getLogger("telemetry_streamer")

class TelemetryStreamer:
    def __init__(self, callback: Optional[Callable[[str, Dict[str, Any]], None]] = None):
        self.callback = callback
        self.events: List[Dict[str, Any]] = []

    def emit(self, event_name: str, message: str, payload: Optional[Dict[str, Any]] = None) -> None:
        timestamp = round(time.time(), 3)
        event = {
            "timestamp": timestamp,
            "event": event_name,
            "message": message,
            "payload": payload or {}
        }
        self.events.append(event)
        formatted_log = f"[Telemetry] [{event_name}] {message}"
        logger.info(formatted_log)

        if self.callback:
            try:
                self.callback(event_name, event)
            except Exception:
                pass

    def emit_milestone(self, icon: str, title: str, elapsed_sec: float) -> None:
        msg = f"{icon} {title} (completed in {elapsed_sec:.2f}s)"
        self.emit("MILESTONE", msg, {"elapsed_sec": elapsed_sec})
