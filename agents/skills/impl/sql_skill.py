from typing import Dict, Any, List, Optional
import pandas as pd
from agents.skills.base_skill import BaseSkill

class SQLSkill(BaseSkill):
    """Plugin Skill: DuckDB SQL queries directly executed on in-memory Pandas DataFrames."""

    @property
    def name(self) -> str:
        return "sql"

    @property
    def description(self) -> str:
        return "Executes fast SQL queries (SELECT, GROUP BY, JOIN, WINDOW functions) directly on Pandas DataFrames using DuckDB."

    @property
    def category(self) -> str:
        return "database"

    @property
    def required_libraries(self) -> List[str]:
        return ["duckdb", "pandas"]

    def can_handle(self, query: str, dataset_meta: Optional[Dict[str, Any]] = None) -> float:
        q_lower = query.lower()
        keywords = ["sql", "select", "group by", "join", "where", "filter", "query", "duckdb", "window"]
        matches = sum(1 for kw in keywords if kw in q_lower)
        if matches > 0:
            return min(0.5 + matches * 0.25, 0.98)
        return 0.05

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        df = context.get("df")
        sql_query = context.get("sql_query")

        if df is None or df.empty:
            return {"status": "success", "output": "No DataFrame supplied for SQL execution."}

        # Try DuckDB first, fall back to sqlite3
        try:
            import duckdb
            con = duckdb.connect(database=":memory:")
            con.register("df_view", df)
            con.register("df", df)
            if sql_query:
                result_df = con.execute(sql_query).df()
            else:
                result_df = con.execute("SELECT * FROM df_view LIMIT 5").df()
            
            return {
                "status": "success",
                "skill_executed": self.name,
                "engine": "duckdb",
                "output": f"### 🗄️ SQL Execution Result (DuckDB):\nQuery: `{sql_query or 'SELECT * FROM df_view LIMIT 5'}`\nRows returned: {len(result_df)}",
                "result_df": result_df.head(10).to_dict()
            }
        except ImportError:
            import sqlite3
            try:
                con = sqlite3.connect(":memory:")
                df.to_sql("df_view", con, index=False, if_exists="replace")
                df.to_sql("df", con, index=False, if_exists="replace")
                query_to_run = sql_query or "SELECT * FROM df_view LIMIT 5"
                result_df = pd.read_sql_query(query_to_run, con)
                con.close()
                return {
                    "status": "success",
                    "skill_executed": self.name,
                    "engine": "sqlite3",
                    "output": f"### 🗄️ SQL Execution Result (SQLite Engine):\nQuery: `{query_to_run}`\nRows returned: {len(result_df)}",
                    "result_df": result_df.head(10).to_dict()
                }
            except Exception as se:
                return {"status": "warning", "output": f"SQLite Execution notice: {se}"}
        except Exception as e:
            return {"status": "warning", "output": f"SQL Skill execution notice: {e}"}
