import os
import ast
import json
import hashlib
import logging
from typing import Dict, Any, Optional, List, Tuple
import pandas as pd

logger = logging.getLogger("debug_validator")

class DebugValidatorAndMemory:
    def __init__(self, memory_file: str = "config/debug_memory.json", lessons_file: str = "config/learning_lessons.json"):
        self.memory_file = os.path.abspath(memory_file)
        self.lessons_file = os.path.abspath(lessons_file)
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        self.memory = self._load_json(self.memory_file, default={"patterns": {}})
        self.lessons = self._load_json(self.lessons_file, default={"lessons": []})

    def _load_json(self, path: str, default: Any) -> Any:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return default

    def _save_json(self, path: str, data: Any) -> None:
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write JSON {path}: {e}")

    @staticmethod
    def validate_dataset(csv_path: str) -> Tuple[bool, str]:
        if not csv_path or not os.path.exists(csv_path):
            return False, f"Dataset file does not exist at '{csv_path}'"
        try:
            df = pd.read_csv(csv_path, nrows=5)
            if df.empty or len(df.columns) == 0:
                return False, f"Dataset '{csv_path}' is empty"
            return True, "Dataset valid"
        except Exception as e:
            return False, f"Dataset validation failed: {e}"

    @staticmethod
    def validate_ast(code: str) -> Tuple[bool, Optional[str]]:
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"SyntaxError at line {e.lineno}, col {e.offset}: {e.msg}"
        except Exception as e:
            return False, f"AST Parsing Error: {e}"

    def get_memory_fix(self, error_type: str, failing_snippet: str) -> Optional[str]:
        raw_key = f"{error_type}:{failing_snippet.strip()}"
        key = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        return self.memory.get("patterns", {}).get(key)

    def save_memory_fix(self, error_type: str, failing_snippet: str, working_fix: str) -> None:
        raw_key = f"{error_type}:{failing_snippet.strip()}"
        key = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        if "patterns" not in self.memory:
            self.memory["patterns"] = {}
        self.memory["patterns"][key] = working_fix
        self._save_json(self.memory_file, self.memory)

    def record_learning_lesson(self, error_type: str, root_cause: str, lesson: str) -> None:
        lesson_entry = {"error_type": error_type, "root_cause": root_cause, "lesson": lesson}
        self.lessons.setdefault("lessons", []).append(lesson_entry)
        self._save_json(self.lessons_file, self.lessons)

    def get_lessons_prompt_summary(self) -> str:
        lessons = self.lessons.get("lessons", [])[-5:]
        if not lessons:
            return ""
        summary = "\n--- Learned Anti-Patterns & Lessons ---\n"
        for l in lessons:
            summary += f"• Avoid [{l.get('error_type')}]: {l.get('lesson')}\n"
        return summary

    @staticmethod
    def verify_no_regression(pre_output: str, post_output: str) -> Tuple[bool, str]:
        if "Error" in post_output or "Traceback" in post_output or "Exception" in post_output:
            return False, "Post-patch execution emitted errors"
        return True, "No regression detected"
