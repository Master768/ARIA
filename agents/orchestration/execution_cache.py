import os
import hashlib
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("execution_cache")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

class ExecutionStateCache:
    def __init__(self, cache_dir: Optional[str] = None):
        if cache_dir:
            self.cache_dir = os.path.abspath(cache_dir)
        else:
            self.cache_dir = os.path.join(PROJECT_ROOT, "config", "execution_cache")
        os.makedirs(self.cache_dir, exist_ok=True)

    def _generate_cache_key(self, dataset_hash: str, query: str, node_name: str) -> str:
        raw_key = f"{dataset_hash}:{query.strip().lower()}:{node_name}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def get(self, dataset_hash: str, query: str, node_name: str) -> Optional[Dict[str, Any]]:
        key = self._generate_cache_key(dataset_hash, query, node_name)
        file_path = os.path.join(self.cache_dir, f"{key}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return None

    def put(self, dataset_hash: str, query: str, node_name: str, result_data: Dict[str, Any]) -> None:
        key = self._generate_cache_key(dataset_hash, query, node_name)
        file_path = os.path.join(self.cache_dir, f"{key}.json")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(result_data, f, indent=2)
        except Exception:
            pass

    def clear(self) -> None:
        for fname in os.listdir(self.cache_dir):
            if fname.endswith(".json"):
                try:
                    os.remove(os.path.join(self.cache_dir, fname))
                except Exception:
                    pass
