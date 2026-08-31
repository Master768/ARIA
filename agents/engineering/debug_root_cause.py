import re
import os
import logging
from typing import Dict, Any, Optional, List
import pandas as pd

logger = logging.getLogger("debug_root_cause")

class RootCauseAnalyzer:
    @classmethod
    def analyze(cls, failed_code: str, traceback_text: str, dataset_path: Optional[str] = None) -> Dict[str, Any]:
        analysis = {
            "failing_line_num": None,
            "failing_line": "",
            "failed_symbol": "",
            "root_cause_type": "UNKNOWN",
            "explanation": "",
            "df_columns": [],
            "df_shape": None
        }

        line_matches = re.findall(r'File ".*?", line (\d+)', traceback_text)
        if line_matches:
            analysis["failing_line_num"] = int(line_matches[-1])
            code_lines = failed_code.splitlines()
            if 0 < analysis["failing_line_num"] <= len(code_lines):
                analysis["failing_line"] = code_lines[analysis["failing_line_num"] - 1].strip()

        key_match = re.search(r"KeyError: [\'\"](.*?)[\'\"]", traceback_text)
        if key_match:
            analysis["failed_symbol"] = key_match.group(1)
            analysis["root_cause_type"] = "KEY_NOT_FOUND"

        if dataset_path and os.path.exists(dataset_path):
            try:
                df = pd.read_csv(dataset_path, nrows=2)
                analysis["df_columns"] = list(df.columns)
                analysis["df_shape"] = [len(df), len(df.columns)]
                
                if analysis["failed_symbol"]:
                    sym = analysis["failed_symbol"]
                    
                    def _norm(s: str) -> str:
                        return s.strip().lower().replace("_", "").replace(" ", "")

                    norm_sym = _norm(sym)
                    normalized_cols = {_norm(c): c for c in df.columns}
                    
                    if norm_sym in normalized_cols:
                        actual_col = normalized_cols[norm_sym]
                        analysis["explanation"] = f"Column '{sym}' formatting mismatch. Actual column in dataset is '{actual_col}'."
                        analysis["actual_symbol"] = actual_col
            except Exception as e:
                logger.warning(f"RootCauseAnalyzer dataset inspection warning: {e}")

        return analysis
