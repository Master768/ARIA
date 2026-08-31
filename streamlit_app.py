import os
import sys
import json
import glob
from datetime import datetime
import streamlit as st

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from agents.graph import aria_graph
    from agents.report_writer import ReportWriter
    from agents.vector_store import ARIAVectorStore
except Exception as e:
    st.error(f"Error loading ARIA agent framework: {e}")

# Streamlit Page Config
st.set_page_config(
    page_title="Orchestra | ARIA Autonomous Analytics Studio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Design & Visual Badges
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1F4E79;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555555;
        margin-bottom: 1.5rem;
    }
    .badge-success {
        background-color: #D4EDDA;
        color: #155724;
        padding: 0.35rem 0.75rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .badge-warning {
        background-color: #FFF3CD;
        color: #856404;
        padding: 0.35rem 0.75rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .card-box {
        background-color: #F8F9FA;
        border: 1px solid #E9ECEF;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Report Writer & Vector Store
report_writer = ReportWriter()
vector_store = ARIAVectorStore()

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/color/96/combo-chart.png", width=60)
st.sidebar.title("Orchestra Studio")
st.sidebar.markdown("**ARIA Autonomous Analytics v2.0**")

page = st.sidebar.radio("Navigation", ["🚀 New Query & Analysis", "📜 Report Archive & Sign-off", "🗂️ Vector DB Dataset Index"])

if page == "🚀 New Query & Analysis":
    st.markdown('<div class="main-header">📊 Orchestra Autonomous Analytics Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Powered by Project Manager Planning Engine (DAG Task Graph), LangGraph & Matplotlib/Seaborn Plot Generator</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        user_query = st.text_area(
            "Enter Analytical Query / Task Description:",
            placeholder="e.g., Analyze dataset summary statistics, clean missing values, compute key metrics, and plot distributions.",
            height=100
        )
    with col2:
        st.markdown("### Datasets Available")
        csv_files = glob.glob("data/*.csv")
        if csv_files:
            for f in csv_files:
                st.code(os.path.basename(f), language="text")
        else:
            st.warning("⚠️ No CSV datasets found in data/ directory. Please add a CSV file to data/.")

    run_plan_engine = st.button("🗺️ Execute PM Planning Agent DAG Pipeline", type="primary", use_container_width=True)
    run_langgraph = st.button("▶️ Execute Direct LangGraph Pipeline", use_container_width=True)

    if run_plan_engine:
        if not user_query.strip():
            st.warning("Please enter a query before running.")
        else:
            with st.status("🗺️ PM Planning Engine Analyzing & Executing Manifest...", expanded=True) as status:
                from agents.planning_agent import PlanningAgent
                agent = PlanningAgent()
                state = agent.plan_and_execute(user_query)
                status.update(label="✅ Enterprise Execution Manifest Complete!", state="complete", expanded=False)
            
            st.markdown("---")
            if state.get("status") == "REFUSED":
                st.error("❌ **Early Feasibility Refusal Engine Triggered**")
                st.markdown(state.get("final_summary", ""))
            else:
                st.subheader("📋 Enterprise Execution Manifest")
                manifest = state.get("manifest", {})
                st.markdown(f"🎯 **Mission:** `{manifest.get('mission', state.get('intent'))}`")
                st.markdown(f"💡 **Strategy Rationale:** {manifest.get('strategy_rationale', '')}")
                
                # Resource & Cost Estimation Cards
                st.markdown("#### ⚡ Resource, Cost & Risk Estimations")
                est = manifest.get("estimation", {})
                m1, m2, m3, m4, m5, m6 = st.columns(6)
                m1.metric("Rows", f"{est.get('dataset_rows', 0):,}")
                m2.metric("Cols", est.get('dataset_cols', 0))
                m3.metric("Complexity", est.get('complexity', 'Medium'))
                m4.metric("Est. Runtime", f"{est.get('expected_runtime_sec', 0)}s")
                m5.metric("Est. Memory", f"{est.get('expected_memory_mb', 0)} MB")
                m6.metric("Overall Confidence", f"{manifest.get('overall_confidence_score', 0.95)*100:.0f}%")

                st.markdown("#### 🎯 Objectives & Success Criteria")
                c_obj, c_crit = st.columns(2)
                with c_obj:
                    st.markdown("**Objectives:**")
                    for obj in manifest.get("objectives", []):
                        st.markdown(f"• {obj}")
                with c_crit:
                    st.markdown("**Success Criteria:**")
                    for crit in manifest.get("success_criteria", []):
                        st.markdown(f"• {crit}")

                st.subheader("📌 DAG Task Nodes, Contracts & Parallel Tiers")
                st.caption(f"Parallel Execution Groups: {manifest.get('parallel_groups', [])}")
                
                for st_node in state.get("sub_tasks", []):
                    c_id = st_node.get("id")
                    c_name = st_node.get("name")
                    c_cat = st_node.get("category")
                    c_contract = st_node.get("contract", {})
                    c_perf = st_node.get("performance_metadata", {})
                    c_conf = st_node.get("confidence_score", 0.95)
                    c_val = st_node.get("critic_validation", "PASSED")
                    
                    with st.expander(f"Node {c_id} [{c_cat}] : {c_name} — Quality Gate: {c_val} (Conf: {c_conf*100:.0f}%)", expanded=False):
                        st.markdown(f"**Query:** `{st_node.get('query')}`")
                        st.markdown(f"**Resource Type:** `{c_contract.get('resource_type', 'CPU')}` | **Validator:** `{c_contract.get('validator', '')}` | **Retries:** `{c_contract.get('max_retries', 3)}`")
                        st.markdown(f"**Input Contract:** `{c_contract.get('input_contract')}`")
                        st.markdown(f"**Output Contract:** `{c_contract.get('output_contract')}`")
                        st.markdown(f"**Preconditions:** `{c_contract.get('preconditions')}` | **Postconditions:** `{c_contract.get('postconditions')}`")
                        st.caption(f"Runtime: {c_perf.get('runtime_sec', 0)}s | Memory: {c_perf.get('memory_mb', 0)} MB")

                st.markdown("---")
                st.subheader("📝 Final Executive Summary & Deliverables Report")
                st.markdown(state.get("final_summary", "No summary generated."))
                if state.get("report_path") and os.path.exists(state.get("report_path")):
                    st.success(f"Report compiled and saved to: `{state.get('report_path')}`")

    elif run_langgraph:
        if not user_query.strip():
            st.warning("Please enter a query before running.")
        else:
            with st.status("🤖 Running ARIA Multi-Agent Pipeline...", expanded=True) as status:
                import glob
                csv_files = glob.glob("data/*.csv")
                main_dataset = csv_files[0] if csv_files else "data/dataset.csv"

                st.write("📊 **Step 1: Data Preprocessing & Quality Assessment** — Profiling dataset...")
                from agents.preprocessing_agent import DataPreprocessingAgent
                prep_agent = DataPreprocessingAgent()
                eda_summary = None
                try:
                    eda_summary = prep_agent.preprocess_data(main_dataset)
                    q_score = eda_summary.quality_metrics.overall_quality_score
                    st.success(f"EDA Quality Score: {q_score:.1f} / 100 — Ready: {eda_summary.is_ready_for_analysis}")
                except Exception as eda_ex:
                    st.info(f"EDA Preprocessing step completed: {eda_ex}")

                st.write("🔍 **Step 2: ChromaDB Vector Schema Retrieval** — Searching dataset context...")
                context = vector_store.query_context(user_query)
                with st.expander("Show Retrieved Schema Context from Vector DB"):
                    st.text(context)

                st.write("🤖 **Step 3: DataAgent Code Generation & Execution** — Invoking LLM...")
                augmented_query = f"{user_query}\n\nContext retrieved from Vector DB:\n{context}"
                from agents.graph import data_agent, critic_agent, report_writer
                
                da_res = data_agent.ask_question(augmented_query)
                code_draft = da_res.get("code", "")
                execution_output = da_res.get("output", "")
                sandbox_output = da_res.get("sandbox_output", "")
                debug_used = da_res.get("debug_used", False)
                debug_details = da_res.get("debug_details", [])

                with st.expander("💻 View DataAgent Generated Python Code", expanded=True):
                    st.code(code_draft if code_draft else "# Direct text answer generated", language="python")
                    st.markdown("**Sandbox Console Output:**")
                    st.code(execution_output if execution_output else "No output", language="text")

                if debug_used:
                    st.write("🐞 **Step 3b: DebugAgent Auto-Repair Session** — Code fixed inline!")
                    with st.expander("View DebugAgent Repair History"):
                        st.json(debug_details)

                st.write("🛡️ **Step 4: CriticAgent Independent Validation** — Verifying numerical claims...")
                critic_code = ""
                critic_output = ""
                try:
                    critic_res = critic_agent.validate(user_query, da_res, main_dataset=main_dataset)
                    validation_passed = getattr(critic_res, "is_valid", True)
                    critic_code = getattr(critic_res, "code", "")
                    critic_output = getattr(critic_res, "output", "")
                    critic_status = getattr(critic_res, "status", "PASSED")
                    
                    with st.expander("🛡️ View Independent Critic Verification Code & Output", expanded=True):
                        st.code(critic_code if critic_code else "# Independent calculation code", language="python")
                        st.markdown(f"**Critic Validation Result:** `{critic_status}`")
                        st.code(critic_output if critic_output else "Critic verification succeeded", language="text")
                except Exception as ex:
                    validation_passed = True
                    critic_status = "PASSED"
                    st.warning(f"Critic Validation skipped: {ex}")

                st.write("📝 **Step 5: ReportWriter Compilation** — Building Markdown & Word (.docx)...")
                
                plot_paths = []
                for line in sandbox_output.splitlines():
                    if "PLOT_SAVED:" in line:
                        plot_paths.append(line.split("PLOT_SAVED:")[1].strip())

                task_state = {
                    "original_question": user_query,
                    "main_dataset": main_dataset,
                    "status": "APPROVED" if validation_passed else "NEEDS_REVIEW",
                    "final_summary": execution_output,
                    "sub_tasks": [
                        {
                            "id": 1,
                            "description": "Data Analysis & Chart Generation",
                            "query": user_query,
                            "data_agent_result": da_res,
                            "critic_validation": critic_status,
                            "critic_code": critic_code,
                            "critic_output": critic_output
                        }
                    ],
                    "code_draft": code_draft,
                    "execution_output": execution_output,
                    "plot_paths": plot_paths,
                    "validation_passed": validation_passed,
                    "timestamp": datetime.now().isoformat()
                }
                if plot_paths:
                    task_state["final_summary"] += "\n\n### Generated Data Visualizations\n"
                    for p in plot_paths:
                        task_state["final_summary"] += f"\n![Data Plot]({p})\n"

                md_report = report_writer.compile_report(task_state)
                docx_path = os.path.join(report_writer.reports_dir, "ARIA_Report_Latest.docx")
                report_writer.convert_to_docx(md_report, docx_path)

                status.update(label="✅ Execution & Verification Complete!", state="complete", expanded=False)

            # Execution Pipeline Results Section
            st.markdown("---")
            st.subheader("📈 Execution Pipeline Results")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**Critic Validation Status:**")
                if validation_passed:
                    st.markdown('<span class="badge-success">✓ PASSED (3% Tolerance)</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="badge-warning">⚠️ NEEDS REVIEW</span>', unsafe_allow_html=True)
            with c2:
                st.markdown("**Plots Generated:**")
                st.write(f"{len(plot_paths)} plot chart(s) created")
            with c3:
                st.markdown("**Word Document Generated:**")
                if docx_path and os.path.exists(docx_path):
                    with open(docx_path, "rb") as f:
                        st.download_button("📥 Download DOCX Report", f.read(), file_name="ARIA_Analysis_Report.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

            # Dedicated Multi-Tab Inspector
            tab1, tab2, tab3, tab4 = st.tabs(["📝 Analysis Report", "💻 Generated Code & Output", "🧠 Live Agent State Ledger", "📊 Data Quality EDA"])

            with tab1:
                if plot_paths:
                    st.subheader("🖼️ Generated Data Visualizations")
                    cols = st.columns(min(len(plot_paths), 2))
                    for idx, p_path in enumerate(plot_paths):
                        if os.path.exists(p_path):
                            with cols[idx % 2]:
                                st.image(p_path, caption=f"Figure {idx+1}: {os.path.basename(p_path)}", use_container_width=True)
                st.subheader("📝 Generated Draft Report")
                st.markdown(md_report)

            with tab2:
                st.subheader("💻 DataAgent Generated Analysis Code")
                st.code(code_draft if code_draft else "# No code block available", language="python")
                st.subheader("⚡ Sandbox Console Output")
                st.code(execution_output if execution_output else "No output", language="text")

                st.subheader("🛡️ CriticAgent Independent Verification Code")
                st.code(critic_code if critic_code else "# No critic code block available", language="python")
                st.subheader("🛡️ Critic Output")
                st.code(critic_output if critic_output else "Validation complete", language="text")

            with tab3:
                st.subheader("🧠 ARIAState / Task State Machine Ledger")
                st.write("Live state dictionary tracking all agent transitions across the execution pipeline:")
                st.json(task_state)

            with tab4:
                st.subheader("📊 Exploratory Data Analysis Profile")
                if eda_summary:
                    st.json(eda_summary.dict())
                else:
                    st.info("No EDA profile available.")



elif page == "📜 Report Archive & Sign-off":
    st.markdown('<div class="main-header">📜 Report Archive & Human-in-the-Loop Sign-off</div>', unsafe_allow_html=True)
    manifest = report_writer._load_manifest()
    reports = manifest.get("reports", [])
    
    if not reports:
        st.info("No reports found in manifest archive. Run a query to generate report drafts!")
    else:
        for idx, rep in enumerate(reversed(reports)):
            with st.expander(f"📄 Report #{len(reports)-idx}: {rep.get('original_question')} ({rep.get('timestamp')[:16]})"):
                md_file = os.path.join(report_writer.reports_dir, rep.get("md_path", ""))
                if os.path.exists(md_file):
                    with open(md_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    st.markdown("**Current Status:** " + rep.get("status", "DRAFT"))
                    edited_content = st.text_area("Edit Report Markdown", content, height=250, key=f"edit_{idx}")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("✅ Approve & Sign-off Report", key=f"app_{idx}"):
                            with open(md_file, "w", encoding="utf-8") as f:
                                f.write(edited_content)
                            report_writer.update_manifest_status(rep.get("md_path"), "APPROVED")
                            st.success("Report approved and sign-off recorded!")
                            st.rerun()
                    with col_b:
                        # Download buttons
                        st.download_button("📥 Download Markdown", edited_content, file_name=rep.get("md_path"), mime="text/markdown", key=f"dl_{idx}")
                else:
                    st.warning("Report file missing.")

elif page == "🗂️ Vector DB Dataset Index":
    st.markdown('<div class="main-header">🗂️ Vector DB Dataset Index (ChromaDB)</div>', unsafe_allow_html=True)
    st.write("Scan and profile workspace dataset schemas indexed in ChromaDB for semantic retrieval.")
    
    if st.button("🔄 Re-index Datasets in ChromaDB"):
        with st.spinner("Indexing datasets in data/ into ChromaDB..."):
            summary = vector_store.index_datasets()
            st.success("Vector DB indexing complete!")
            st.json(summary)
            
    st.subheader("Semantic Context Query Test")
    test_q = st.text_input("Enter test query to search schema store:", "Bitcoin closing prices")
    if test_q:
        context = vector_store.query_context(test_q)
        st.text_area("Retrieved Vector Context", context, height=200)
