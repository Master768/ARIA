import re
import difflib
import logging
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger("debug_patcher")

class DeterministicPatchEngine:
    @classmethod
    def try_deterministic_patch(
        cls,
        failed_code: str,
        category: str,
        analysis: Dict[str, Any]
    ) -> Optional[Tuple[str, str, float]]:
        failing_line = analysis.get("failing_line", "")
        failed_symbol = analysis.get("failed_symbol", "")
        df_columns = analysis.get("df_columns", [])

        if category == "KEY_ERROR" and failed_symbol and df_columns:
            if "actual_symbol" in analysis:
                actual_col = analysis["actual_symbol"]
                patched_code = failed_code.replace(f"'{failed_symbol}'", f"'{actual_col}'").replace(f'"{failed_symbol}"', f'"{actual_col}"')
                expl = f"Deterministic fix: Replaced missing column '{failed_symbol}' with actual dataset column '{actual_col}'"
                return patched_code, expl, 0.98

            close_matches = difflib.get_close_matches(failed_symbol, df_columns, n=1, cutoff=0.6)
            if close_matches:
                best_match = close_matches[0]
                patched_code = failed_code.replace(f"'{failed_symbol}'", f"'{best_match}'").replace(f'"{failed_symbol}"', f'"{best_match}"')
                expl = f"Deterministic fix: Replaced typo column '{failed_symbol}' with closest matching column '{best_match}'"
                return patched_code, expl, 0.95

        if "name 'pd' is not defined" in failing_line or "name 'pd'" in str(analysis):
            patched_code = "import pandas as pd\n" + failed_code
            return patched_code, "Deterministic fix: Injected missing 'import pandas as pd'", 0.99

        if "name 'np' is not defined" in failing_line or "name 'np'" in str(analysis):
            patched_code = "import numpy as np\n" + failed_code
            return patched_code, "Deterministic fix: Injected missing 'import numpy as np'", 0.99

        if "name 'plt' is not defined" in failing_line or "name 'plt'" in str(analysis):
            patched_code = "import matplotlib.pyplot as plt\n" + failed_code
            return patched_code, "Deterministic fix: Injected missing 'import matplotlib.pyplot as plt'", 0.99

        if "name 'sns' is not defined" in failing_line or "name 'sns'" in str(analysis):
            patched_code = "import seaborn as sns\n" + failed_code
            return patched_code, "Deterministic fix: Injected missing 'import seaborn as sns'", 0.99

        return None

    @classmethod
    def apply_line_patch(cls, original_code: str, line_num: int, new_line_content: str) -> str:
        lines = original_code.splitlines()
        if 0 < line_num <= len(lines):
            lines[line_num - 1] = new_line_content
            return "\n".join(lines)
        return original_code
