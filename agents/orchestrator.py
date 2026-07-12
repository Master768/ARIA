import os
import json
import logging
import time
from datetime import datetime, timezone
try:
    from agents.llm_client import GroqOllamaClient
except ModuleNotFoundError:
    from llm_client import GroqOllamaClient
from dotenv import load_dotenv
try:
    from agents.data_agent import DataAgent, run_python_code
    from agents.critic_agent import CriticAgent
    from agents.report_writer import ReportWriter
    from agents.debug_agent import DebugAgent
    from agents.preprocessing_agent import DataPreprocessingAgent
except ModuleNotFoundError:
    from data_agent import DataAgent, run_python_code
    from critic_agent import CriticAgent
    from report_writer import ReportWriter
    from debug_agent import DebugAgent
    from preprocessing_agent import DataPreprocessingAgent

# Load env variables
load_dotenv()

# Configure Orchestrator Logger
log_dir = os.path.abspath("logs")
os.makedirs(log_dir, exist_ok=True)
orch_logger = logging.getLogger("orchestrator")
orch_logger.setLevel(logging.INFO)

if not orch_logger.handlers:
    fh = logging.FileHandler(os.path.join(log_dir, "phase3_orchestration.log"), encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    orch_logger.addHandler(fh)

class OrchestratorAgent:
    def __init__(self, host: str = None, model: str = None):
        # Build the shared LLM client (Groq cloud API with Ollama-compatible interface)
        self.client = GroqOllamaClient(host=host, model=model)

        if not model:
            model = os.getenv("GROQ_MODEL", os.getenv("OLLAMA_MODEL", "llama-3.3-70b-versatile"))

        self.model = model

        # Instantiate downstream agents, injecting the shared LLM client
        self.debug_agent = DebugAgent(self.client, model=self.model, sandbox_run_fn=run_python_code)
        self.data_agent = DataAgent(host=host, model=model, debug_agent=self.debug_agent)
        self.critic_agent = CriticAgent(host=host, model=model)
        self.report_writer = ReportWriter()
        self.preprocessing_agent = DataPreprocessingAgent(llm_client=self.client)
        
        self.config_dir = os.path.abspath("config")
        os.makedirs(self.config_dir, exist_ok=True)
        self.state_file = os.path.join(self.config_dir, "task_state.json")

    def _write_state(self, state: dict):
        """Helper to write the current task state ledger to config/task_state.json."""
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    def plan_and_execute(self, question: str) -> dict:
        """
        Takes a natural language business question, plans 2-5 sub-tasks,
        and coordinates execution across DataAgent and CriticAgent.
        """
        orch_logger.info(f"Received master query: {question}")
        
        # Discover all CSV files in data/ and dynamically select based on question
        data_files = []
        try:
            data_files = [f for f in os.listdir("data") if f.endswith(".csv")]
        except:
            pass
        
        # Score each CSV file by relevance to the question and pick the best match
        DOMAIN_SYNONYMS = {
            # Financial / crypto keywords → look for files with these tokens in the name
            "bitcoin": ["btc", "binance", "crypto", "usdt"],
            "crypto":  ["btc", "binance", "usdt", "eth"],
            "btc":     ["btc", "binance"],
            "price":   ["btc", "binance", "stock", "ohlc"],
            "stock":   ["stock", "ohlc", "sp500"],
            "churn":   ["churn", "telecom", "telco"],
            "customer":["churn", "telecom", "crm"],
            "amazon":  ["amazon"],
            "sales":   ["sales", "revenue"],
        }

        def _score_file(filename: str) -> int:
            score = 0
            name_no_ext = os.path.splitext(filename)[0].lower()
            name_tokens = set(name_no_ext.replace('_', ' ').replace('-', ' ').split())
            q_lower = question.lower()
            q_words = set(q_lower.split())

            # Exact filename substring in question
            if name_no_ext in q_lower:
                score += 100

            # Token overlap: filename tokens found in the question
            for tok in name_tokens:
                if len(tok) >= 3 and tok in q_lower:
                    score += 10

            # Domain synonym matching: question word → known file tokens
            for q_word in q_words:
                for synonym_key, file_tokens in DOMAIN_SYNONYMS.items():
                    if q_word == synonym_key or q_word.startswith(synonym_key):
                        for ft in file_tokens:
                            if ft in name_tokens or ft in name_no_ext:
                                score += 30

            # Column overlap: peek at columns and check against question words
            try:
                import pandas as pd
                df_s = pd.read_csv(f"data/{filename}", nrows=1)
                for col in df_s.columns:
                    if col.lower() in q_lower or col.lower().replace(' ', '') in q_lower:
                        score += 5
            except Exception:
                pass

            return score

        scores = {f: _score_file(f) for f in data_files}
        selected_file = max(scores, key=scores.get) if scores else None

        if selected_file:
            main_dataset = f"data/{selected_file}"
        else:
            main_dataset = f"data/{data_files[0]}" if data_files else "data/telco_churn.csv"

        
        columns = []
        try:
            import pandas as pd
            df = pd.read_csv(main_dataset, nrows=1)
            columns = df.columns.tolist()
        except:
            pass

        # Run Preprocessing / EDA before planning sub-tasks
        print(f"\n🔍  [Orchestrator] Running data quality check on '{main_dataset}'...", flush=True)
        eda_summary = None
        try:
            orch_logger.info(f"[Orchestrator] Running EDA on '{main_dataset}'...")
            eda_summary = self.preprocessing_agent.preprocess_data(main_dataset)
            quality_score = eda_summary.quality_metrics.overall_quality_score
            is_ready = eda_summary.is_ready_for_analysis
            print(f"📊  [Orchestrator] Data quality score: {quality_score:.1f}/100 | Ready: {is_ready}", flush=True)
            orch_logger.info(
                f"[Orchestrator] EDA complete — Quality: "
                f"{quality_score:.1f}/100 | "
                f"Ready: {is_ready}"
            )
            if not is_ready:
                print(f"⚠️   [Orchestrator] Data quality WARNING: {eda_summary.warnings}", flush=True)
                orch_logger.warning(
                    f"[Orchestrator] Data quality gate WARNING: "
                    f"{eda_summary.warnings}"
                )
            # Persist EDA report
            os.makedirs("reports", exist_ok=True)
            report_path = os.path.join(
                "reports",
                f"eda_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
            )
            self.preprocessing_agent.generate_eda_report(eda_summary, report_path)
            orch_logger.info(f"[Orchestrator] EDA report saved → {report_path}")
        except Exception as _eda_err:
            orch_logger.warning(f"[Orchestrator] EDA skipped (non-fatal): {_eda_err}")
            print(f"⚠️   [Orchestrator] EDA skipped: {_eda_err}", flush=True)

        # Peek at a sample date value so the planner knows the format
        sample_date = ""
        try:
            import pandas as pd
            df_peek = pd.read_csv(main_dataset, nrows=2)
            if "Date" in df_peek.columns:
                sample_date = str(df_peek["Date"].iloc[0])
        except Exception:
            pass

        date_format_hint = ""
        if sample_date:
            date_format_hint = (
                f"\nDate column format example: '{sample_date}' "
                f"(use df['Date'].str.contains('2025') to filter by year, "
                f"df['Date'].str.contains('2025-10') or df['Date'].str.contains('10-2025') to filter by month). "
                f"NEVER try to compute min/max of the Date column to find year boundaries — use str.contains() directly.\n"
            )

        # 1. Deconstruct query into 2-5 sub-tasks
        print(f"\n🧩  [Orchestrator] Planning sub-tasks from question...", flush=True)
        planning_prompt = (
            f"You are the Planning Agent. Deconstruct this business question into 1 to 3 distinct, sequential analytical sub-questions that can each be computed as a SINGLE numeric value from the dataset.\n"
            f"Question: '{question}'\n\n"
            f"The dataset is local at '{main_dataset}'. It has ONLY the following columns:\n"
            f"{columns}\n"
            f"{date_format_hint}\n"
            "RULES — read carefully:\n"
            "1. Each sub-question must return EXACTLY ONE numeric value (avg, max, min, count, % change, sum). No lists or tables.\n"
            "2. NEVER create a sub-task that asks for min/max date, row count, or column metadata just to help plan other sub-tasks. These are useless to the final answer.\n"
            "3. For date filtering, always write the filter condition directly in the query (e.g. 'where Date contains 2025'). Do NOT ask the Data Agent to look up date boundaries first.\n"
            "4. If the question can be answered with a single computation, create only 1 sub-task. Only split if the answer genuinely requires comparing two separate numeric values.\n"
            "5. Do NOT create a 'verify' or 'confirm' sub-task — the Critic Agent handles verification automatically.\n\n"
            "Return a JSON object with a single key 'sub_tasks' containing an array of objects. Each object must have:\n"
            "- 'id': incrementing integer starting at 1\n"
            "- 'description': short description of what this sub-task computes\n"
            "- 'query': the specific data question (must reference column names from the schema above)\n"
            "Return ONLY valid JSON. Do not include markdown code fences."
        )
        
        sub_tasks_list = []
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "user", "content": planning_prompt}
                ],
                options={"temperature": 0.0}
            )
            content = response.message.content.strip()
            
            # Strip markdown packaging if present
            if content.startswith("```"):
                lines = content.splitlines()
                if len(lines) > 2:
                    content = "\n".join(lines[1:-1])
                    if content.startswith("json"):
                        content = content[4:].strip()
            
            plan_data = json.loads(content)
            sub_tasks_list = plan_data.get("sub_tasks", [])
        except Exception as e:
            err_msg = f"Failed to generate planning JSON: {str(e)}"
            orch_logger.error(err_msg)
            print(f"⚠️   [Orchestrator] Planning failed, using baseline plan: {e}", flush=True)
            # Standard baseline plan in case of Ollama planning failure
            sub_tasks_list = [
                {
                    "id": 1,
                    "description": "Calculate total churn count",
                    "query": "How many customers churned?"
                },
                {
                    "id": 2,
                    "description": "Calculate average monthly charges for churned customers",
                    "query": "What is the average monthly charge of customers who churned?"
                }
            ]

        print(f"📋  [Orchestrator] Plan generated — {len(sub_tasks_list)} sub-task(s):", flush=True)
        for t in sub_tasks_list:
            print(f"     [{t['id']}] {t['description']}: '{t['query']}'", flush=True)
        orch_logger.info(f"Generated task plan containing {len(sub_tasks_list)} sub-tasks.")
        
        # 2. Initialize the state ledger
        state = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "original_question": question,
            "status": "IN_PROGRESS",
            "sub_tasks": sub_tasks_list,
            "final_summary": ""
        }
        self._write_state(state)
        
        # 3. Iterate and execute the sub-tasks
        halted = False
        for i, task in enumerate(state["sub_tasks"]):
            task_query = task["query"]
            task_desc = task["description"]
            
            orch_logger.info(f"Executing sub-task {task['id']}: '{task_desc}' (Query: '{task_query}')")
            
            # Cooldown sleep between tasks
            if i > 0:
                orch_logger.info("  [Cooldown] Sleeping 5s between sub-tasks...")
                time.sleep(5.0)

            # Collect prior validated results for context (same as what Critic receives)
            prior_results_for_agent = [
                {
                    "id": t["id"],
                    "query": t["query"],
                    "output": t.get("data_agent_result", {}).get("output", "")
                }
                for t in state["sub_tasks"][:i]
                if t.get("critic_validation") == "PASSED"
            ]

            # Run Data Agent with retry for transient 500/empty errors
            data_res = None
            for attempt in range(2):
                orch_logger.info(f"  Dispatching to Data Agent (Attempt {attempt+1})...")
                data_res = self.data_agent.ask_question(task_query, prior_results=prior_results_for_agent)
                output_text = data_res.get('output', '').strip()
                
                if "500" in output_text or not output_text or output_text.strip().lower() == "nan":
                    orch_logger.warning(f"    WARNING: Data Agent returned transient error or empty output: '{output_text}'")
                    if attempt == 0:
                        orch_logger.info("    Sleeping 10s before retry...")
                        time.sleep(10.0)
                        continue
                break

            task["data_agent_result"] = data_res
            if data_res.get("debug_used"):
                task["debug_used"] = True
                task["debug_attempts"] = data_res.get("debug_attempts", 0)
                task["debug_details"] = data_res.get("debug_details", [])
                
            self._write_state(state) # update ledger
            
            if data_res.get("status") == "FAILED_AFTER_DEBUG":
                task["critic_validation"] = "FAILED"
                task["status"] = "NEEDS_REVIEW"
                task["error"] = data_res.get("error", "Failed after debug")
                self._write_state(state)
                
                state["status"] = "NEEDS_REVIEW"
                self._write_state(state)
                orch_logger.error("Orchestrator execution halted due to DataAgent/DebugAgent failure.")
                return state
            
            # Collect prior validated sub-task results to give the Critic context
            prior_results = [
                {
                    "id": t["id"],
                    "query": t["query"],
                    "output": t.get("data_agent_result", {}).get("output", "")
                }
                for t in state["sub_tasks"][:i]  # only tasks completed before this one
                if t.get("critic_validation") == "PASSED"
            ]

            # Run Critic Agent with retry for transient 500/empty errors
            critic_res = None
            for attempt in range(2):
                print(f"  🔍  [Orchestrator] Dispatching to Critic Agent for validation...", flush=True)
                orch_logger.info(f"  Dispatching to Critic Agent for verification (Attempt {attempt+1})...")
                critic_res = self.critic_agent.validate(task_query, data_res, main_dataset=main_dataset, columns=columns, prior_results=prior_results)
                
                if "LLM error" in critic_res.status or "Ollama error" in critic_res.status or critic_res.status == "FAILED (Extraction failure)":
                    print(f"  ⚠️   [Orchestrator] Critic validation hit transient error (retry {attempt+1}/2): {critic_res.status}", flush=True)
                    orch_logger.warning(f"    WARNING: Critic validation failed with transient error: {critic_res.status}")
                    if attempt == 0:
                        orch_logger.info("    Sleeping 10s before retry...")
                        time.sleep(10.0)
                        continue
                break
            
            if critic_res.is_valid:
                task["critic_validation"] = "PASSED"
                task["status"] = "COMPLETE"
                print(f"  ✅  [Orchestrator] Sub-task {task['id']} validation PASSED (Critic = {critic_res.critic_value}, diff: {critic_res.diff:.2f}%)", flush=True)
                orch_logger.info(f"  Sub-task {task['id']} verified successfully.")
            else:
                task["critic_validation"] = "FAILED"
                task["status"] = "NEEDS_REVIEW"
                print(f"  ❌  [Orchestrator] Sub-task {task['id']} validation FAILED: {critic_res.status}", flush=True)
                orch_logger.error(f"  Sub-task {task['id']} validation FAILED: {critic_res.status}")
                halted = True
            
            self._write_state(state) # update ledger
            
            if halted:
                state["status"] = "NEEDS_REVIEW"
                self._write_state(state)
                orch_logger.error("Orchestrator execution halted due to validation failure.")
                return state

        # 4. Synthesize final summary
        orch_logger.info("All sub-tasks completed and verified. Synthesizing final summary...")
        summary_prompt = (
            f"You are the Analytics Coordinator. Synthesize the findings from these sequential sub-questions to answer the original question: '{question}'\n\n"
            "Here are the sub-questions and their validated calculations:\n"
        )
        for task in state["sub_tasks"]:
            summary_prompt += f"- Sub-task {task['id']} ({task['query']}): {task['data_agent_result'].get('output', '').strip()}\n"
        summary_prompt += "\nWrite a concise, professional executive summary answering the original business question directly."
        
        try:
            summary_response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "user", "content": summary_prompt}
                ]
            )
            final_summary = summary_response.message.content.strip()
        except Exception as e:
            final_summary = f"Summary generation failed: {str(e)}"
            orch_logger.error(final_summary)
            
        state["final_summary"] = final_summary
        state["status"] = "COMPLETE"
        self._write_state(state)
        orch_logger.info("Orchestrator pipeline execution complete.")
        
        # 5. Compile the Markdown report using ReportWriter
        orch_logger.info("Passing compiled findings to ReportWriter...")
        self.report_writer.compile_report(state)
        
        return state


if __name__ == "__main__":
    import sys

    # Ensure project root is on sys.path so 'agents.*' imports resolve correctly
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Accept question from CLI arg or prompt interactively
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = input("Enter your business question: ").strip()

    if not question:
        print("No question provided. Exiting.")
        sys.exit(1)

    print(f"\nRunning orchestrator for: '{question}'\n")
    agent = OrchestratorAgent()
    result = agent.plan_and_execute(question)

    print("\n" + "=" * 60)
    print(f"Status : {result.get('status')}")
    print(f"Summary: {result.get('final_summary', '(none)')}")
    print("=" * 60)
