import os
import json
import time
import streamlit as st
from datetime import datetime
from agents.report_writer import ReportWriter
from agents.orchestrator import OrchestratorAgent

# Page Config
st.set_page_config(
    page_title="Orchestra Report Studio",
    page_icon="📊",
    layout="wide"
)

# Custom Dark-Mode Theme Injections
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
        
        /* Font Overrides */
        html, body, [class*="css"], .stMarkdown {
            font-family: 'Outfit', sans-serif !important;
        }
        
        /* Main Container Background */
        [data-testid="stAppViewContainer"] {
            background-color: #0b0f19 !important;
            color: #e2e8f0 !important;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #111827 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        }
        
        /* Header transparent */
        [data-testid="stHeader"] {
            background-color: transparent !important;
        }
        
        /* Tabs styling */
        button[data-baseweb="tab"] {
            font-family: 'Outfit', sans-serif !important;
            font-size: 1.1rem !important;
            color: #9ca3af !important;
            font-weight: 500 !important;
            background-color: transparent !important;
            border: none !important;
            padding: 10px 20px !important;
        }
        button[aria-selected="true"] {
            color: #3b82f6 !important;
            font-weight: 700 !important;
            border-bottom: 2px solid #3b82f6 !important;
        }
        
        /* Glassmorphic Card Container */
        .glass-card {
            background: rgba(22, 29, 48, 0.65) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            padding: 24px !important;
            margin-bottom: 20px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
        }
        
        /* Inner Nested Card Container */
        .nested-card {
            background: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 8px !important;
            padding: 16px !important;
            margin-bottom: 12px !important;
        }
        
        /* Header style */
        .main-header {
            background: linear-gradient(135deg, #60a5fa, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
            margin-bottom: 10px;
        }
        
        /* High Contrast Badges */
        .status-badge {
            display: inline-flex;
            align-items: center;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-right: 8px;
        }
        
        .badge-draft {
            background-color: rgba(245, 158, 11, 0.15) !important;
            color: #fbbf24 !important;
            border: 1px solid rgba(245, 158, 11, 0.4) !important;
        }
        
        .badge-approved {
            background-color: rgba(16, 185, 129, 0.15) !important;
            color: #34d399 !important;
            border: 1px solid rgba(16, 185, 129, 0.4) !important;
        }
        
        .badge-rejected {
            background-color: rgba(239, 68, 68, 0.15) !important;
            color: #f87171 !important;
            border: 1px solid rgba(239, 68, 68, 0.4) !important;
        }
        
        .badge-passed {
            background-color: rgba(16, 185, 129, 0.15) !important;
            color: #34d399 !important;
            border: 1px solid rgba(16, 185, 129, 0.4) !important;
        }
        
        .badge-failed {
            background-color: rgba(239, 68, 68, 0.15) !important;
            color: #f87171 !important;
            border: 1px solid rgba(239, 68, 68, 0.4) !important;
        }
        
        .badge-pending {
            background-color: rgba(156, 163, 175, 0.15) !important;
            color: #9ca3af !important;
            border: 1px solid rgba(156, 163, 175, 0.4) !important;
        }
        
        /* Grid headers and code block alignment */
        .comparison-header {
            font-size: 0.95rem;
            font-weight: 600;
            color: #9ca3af;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize ReportWriter
writer = ReportWriter()
reports_dir = writer.reports_dir

st.title("📊 Orchestra Report Studio")
st.markdown("Collaborative workspace for reviewing agentic reports, verifying logic, and executing live queries.")

# Load manifest data
manifest_data = writer._load_manifest()
reports = manifest_data.get("reports", [])

# Main navigation tabs
tab_archive, tab_live = st.tabs(["📋 Report Archive & Review", "⚡ Live Query Runner"])

with tab_archive:
    # Sidebar selection logic is shared but displayed inside Archive Tab context
    st.sidebar.header("📁 Report Archive")
    if not reports:
        st.sidebar.info("No reports found in the archive.")
        selected_report_entry = None
    else:
        options = []
        option_map = {}
        for idx, r in enumerate(reports):
            label = f"[{r.get('status')}] {r.get('original_question')[:35]}... ({r.get('timestamp')})"
            options.append(label)
            option_map[label] = r
            
        selected_label = st.sidebar.selectbox("Select Report to Review", options)
        selected_report_entry = option_map.get(selected_label)

    if selected_report_entry is None:
        st.info("Select a report from the sidebar to review its content and agentic trace.")
    else:
        # Load markdown file content
        md_filename = selected_report_entry.get("md_path")
        md_path = os.path.join(reports_dir, md_filename)
        
        # Load state file content if available
        state_filename = selected_report_entry.get("state_path")
        state_data = None
        if state_filename:
            state_path = os.path.join(reports_dir, state_filename)
            if os.path.exists(state_path):
                try:
                    with open(state_path, "r", encoding="utf-8") as f:
                        state_data = json.load(f)
                except:
                    pass
        
        st.markdown(f'<h2 class="main-header">{selected_report_entry.get("original_question")}</h2>', unsafe_allow_html=True)
        
        # Status Metadata Bar
        status = selected_report_entry.get("status")
        val_status = selected_report_entry.get("validation_status")
        timestamp = selected_report_entry.get("timestamp")
        
        status_class = f"badge-{status.lower()}"
        val_class = "badge-approved" if val_status in ("COMPLETE", "PASSED") else "badge-rejected"
        val_text = "VERIFIED" if val_status in ("COMPLETE", "PASSED") else "NEEDS REVIEW / FAILED"
        
        st.markdown(f"""
            <div style="margin-bottom: 24px;">
                <span class="status-badge {status_class}">Status: {status}</span>
                <span class="status-badge {val_class}">Critic: {val_text}</span>
                <span style="font-size: 0.95rem; color: #9ca3af; margin-left: 12px;">Generated on: {timestamp}</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Layout splitting: left column is report content/editor, right is validation trace details
        col_left, col_right = st.columns([5, 4])
        
        with col_left:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### 📝 Report Content")
            if not os.path.exists(md_path):
                st.error(f"Markdown report file not found at: `{md_path}`")
            else:
                with open(md_path, "r", encoding="utf-8") as f:
                    md_content = f.read()
                
                if status == "DRAFT":
                    edited_content = st.text_area(
                        "Edit Report Content (Markdown)",
                        value=md_content,
                        height=500,
                        key=f"editor_{md_filename}"
                    )
                    
                    btn_col1, btn_col2, _ = st.columns([2, 2, 5])
                    with btn_col1:
                        if st.button("✅ Approve & Compile", use_container_width=True, key=f"app_{md_filename}"):
                            # Approve pathways
                            approved_md_filename = md_filename.replace("_DRAFT.md", "_APPROVED.md")
                            approved_md_path = os.path.join(reports_dir, approved_md_filename)
                            approved_docx_filename = md_filename.replace("_DRAFT.md", "_APPROVED.docx")
                            approved_docx_path = os.path.join(reports_dir, approved_docx_filename)
                            
                            with open(approved_md_path, "w", encoding="utf-8") as f:
                                f.write(edited_content)
                                
                            writer.convert_to_docx(edited_content, approved_docx_path)
                            
                            writer.update_manifest_status(
                                draft_filename=md_filename,
                                new_status="APPROVED",
                                new_filename=approved_md_filename,
                                docx_filename=approved_docx_filename
                            )
                            
                            if os.path.exists(md_path):
                                os.remove(md_path)
                            st.success("Signed off and compiled to DOCX!")
                            st.balloons()
                            time.sleep(1.0)
                            st.rerun()
                            
                    with btn_col2:
                        if st.button("❌ Reject Draft", use_container_width=True, key=f"rej_{md_filename}"):
                            writer.update_manifest_status(
                                draft_filename=md_filename,
                                new_status="REJECTED"
                            )
                            st.warning("Draft rejected.")
                            time.sleep(1.0)
                            st.rerun()
                else:
                    st.markdown(md_content)
                    
                    if status == "APPROVED":
                        st.info("✨ This report has been approved and signed off.")
                        docx_filename = selected_report_entry.get("docx_path")
                        docx_path = os.path.join(reports_dir, docx_filename) if docx_filename else ""
                        
                        dl_col1, dl_col2 = st.columns(2)
                        with dl_col1:
                            st.download_button(
                                label="📥 Download Markdown",
                                data=md_content,
                                file_name=md_filename,
                                mime="text/markdown",
                                use_container_width=True
                            )
                        if docx_path and os.path.exists(docx_path):
                            with dl_col2:
                                with open(docx_path, "rb") as f:
                                    st.download_button(
                                        label="📥 Download Premium DOCX",
                                        data=f.read(),
                                        file_name=docx_filename,
                                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                        use_container_width=True
                                    )
                    elif status == "REJECTED":
                        st.error("🚫 This report was rejected by reviewers.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_right:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### 🔍 Agent Verification Trace")
            
            if not state_data:
                st.info("Detailed verification trace is not available for this legacy report.")
            else:
                st.markdown(f"**Task Overall Status:** `{state_data.get('status')}`")
                st.markdown("---")
                
                for task in state_data.get("sub_tasks", []):
                    task_id = task.get("id")
                    task_desc = task.get("description")
                    task_query = task.get("query")
                    critic_val = task.get("critic_validation", "PENDING")
                    
                    c_badge = "passed" if critic_val == "PASSED" else ("failed" if critic_val == "FAILED" else "pending")
                    
                    with st.expander(f"Sub-task {task_id}: {task_desc}", expanded=(critic_val == "FAILED")):
                        st.markdown(f"**Query:** `{task_query}`")
                        st.markdown(f'**Critic Verification:** <span class="status-badge badge-{c_badge}">{critic_val}</span>', unsafe_allow_html=True)
                        if "critic_status_msg" in task:
                            st.markdown(f"**Verification Detail:** *{task.get('critic_status_msg')}*")
                            
                        # Show Data Agent vs Critic Code/Output Side-by-Side
                        st.markdown("#### Code & Sandbox Comparison")
                        st.markdown('<div class="nested-card">', unsafe_allow_html=True)
                        comp_col1, comp_col2 = st.columns(2)
                        with comp_col1:
                            st.markdown('<div class="comparison-header">Data Agent (Python)</div>', unsafe_allow_html=True)
                            agent_code = task.get("data_agent_result", {}).get("code", "# No code")
                            st.code(agent_code, language="python")
                            st.markdown('<div class="comparison-header">Sandbox Raw Output</div>', unsafe_allow_html=True)
                            agent_raw = task.get("data_agent_result", {}).get("output", "No output")
                            st.text(agent_raw)
                        with comp_col2:
                            st.markdown('<div class="comparison-header">Critic Agent (Python)</div>', unsafe_allow_html=True)
                            critic_code = task.get("critic_code", "# No code")
                            st.code(critic_code, language="python")
                            st.markdown('<div class="comparison-header">Sandbox Raw Output</div>', unsafe_allow_html=True)
                            critic_raw = task.get("critic_output", "No output")
                            st.text(critic_raw)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Show metrics
                        da_val = task.get("data_agent_result", {}).get("output", "")
                        cr_val = task.get("critic_value")
                        diff_val = task.get("critic_diff")
                        if cr_val is not None:
                            st.markdown(f"""
                                <div style="display: flex; gap: 20px; font-size: 0.9rem; margin-top: 8px;">
                                    <div><b>Data value (extracted):</b> {da_val[:40]}</div>
                                    <div><b>Critic value (extracted):</b> {cr_val}</div>
                                    <div><b>Difference:</b> {diff_val:.2f}%</div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                        # If debug was used, display debugging trace details
                        if task.get("debug_used"):
                            st.markdown("🔍 **Self-Correction & Debug Trace**")
                            for attempt in task.get("debug_details", []):
                                st.markdown(f"""
                                    <div class="nested-card" style="border-left: 3px solid #f59e0b;">
                                        <b>Attempt {attempt.get('attempt')}: Error</b><br>
                                        <code>{attempt.get('error')}</code><br>
                                        <b>Fix Implemented:</b><br>
                                        <i>{attempt.get('fix')}</i>
                                    </div>
                                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

with tab_live:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### ⚡ Live Query Execution Runner")
    st.markdown("Compose analytical business questions and trigger the multi-agent orchestration pipeline to run live against local datasets.")
    
    # Show available local datasets
    datasets = []
    try:
        datasets = [f for f in os.listdir("data") if f.endswith(".csv")]
    except:
        pass
        
    st.markdown("##### 📂 Discovered Datasets")
    if datasets:
        cols_ds = st.columns(len(datasets))
        for idx, ds in enumerate(datasets):
            with cols_ds[idx]:
                st.markdown(f"""
                    <div class="nested-card">
                        <b>{ds}</b><br>
                        <span style="font-size:0.8rem; color:#9ca3af;">Path: data/{ds}</span>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("No datasets found in the data/ directory.")
        
    query_input = st.text_area(
        "Ask a business question:",
        placeholder="e.g. For product categories in amazon.csv, what is the count of duplicates and percentage of missing values?",
        height=100
    )
    
    if st.button("🚀 Execute Analysis Pipeline", use_container_width=True):
        if not query_input.strip():
            st.error("Please enter a question to analyze.")
        else:
            status_container = st.empty()
            with status_container:
                st.info("Initializing multi-agent pipeline and running Preprocessing check...")
            
            try:
                # Orchestrate execution
                agent = OrchestratorAgent()
                
                # We can intercept stdout/logs or just run it and read task_state
                # To be user-friendly, let's wrap it in st.spinner
                with st.spinner("Agents working (Planning -> Executing -> Validating)..."):
                    result_state = agent.plan_and_execute(query_input)
                
                status_container.empty()
                
                # Check status
                final_status = result_state.get("status")
                if final_status == "COMPLETE":
                    st.success("✅ Live Query Pipeline executed successfully! The draft report has been added to the archive.")
                else:
                    st.warning("⚠️ Live Query Pipeline completed with validation warnings. Review findings below.")
                
                # Render results live in the runner tab
                st.markdown("### 📊 Pipeline Results Summary")
                
                # Executive summary
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown("#### Executive Summary")
                st.markdown(result_state.get("final_summary", "No summary generated."))
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Subtask trace
                for task in result_state.get("sub_tasks", []):
                    task_id = task.get("id")
                    task_desc = task.get("description")
                    task_query = task.get("query")
                    critic_val = task.get("critic_validation", "PENDING")
                    c_badge = "passed" if critic_val == "PASSED" else ("failed" if critic_val == "FAILED" else "pending")
                    
                    with st.expander(f"Sub-task {task_id}: {task_desc}", expanded=True):
                        st.markdown(f"**Query:** `{task_query}`")
                        st.markdown(f'**Critic Verification:** <span class="status-badge badge-{c_badge}">{critic_val}</span>', unsafe_allow_html=True)
                        if "critic_status_msg" in task:
                            st.markdown(f"**Verification Detail:** *{task.get('critic_status_msg')}*")
                            
                        # Show Data Agent vs Critic Code/Output Side-by-Side
                        st.markdown("#### Code & Sandbox Comparison")
                        st.markdown('<div class="nested-card">', unsafe_allow_html=True)
                        comp_col1, comp_col2 = st.columns(2)
                        with comp_col1:
                            st.markdown('<div class="comparison-header">Data Agent (Python)</div>', unsafe_allow_html=True)
                            agent_code = task.get("data_agent_result", {}).get("code", "# No code")
                            st.code(agent_code, language="python")
                            st.markdown('<div class="comparison-header">Sandbox Raw Output</div>', unsafe_allow_html=True)
                            agent_raw = task.get("data_agent_result", {}).get("output", "No output")
                            st.text(agent_raw)
                        with comp_col2:
                            st.markdown('<div class="comparison-header">Critic Agent (Python)</div>', unsafe_allow_html=True)
                            critic_code = task.get("critic_code", "# No code")
                            st.code(critic_code, language="python")
                            st.markdown('<div class="comparison-header">Sandbox Raw Output</div>', unsafe_allow_html=True)
                            critic_raw = task.get("critic_output", "No output")
                            st.text(critic_raw)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Show metrics
                        da_val = task.get("data_agent_result", {}).get("output", "")
                        cr_val = task.get("critic_value")
                        diff_val = task.get("critic_diff")
                        if cr_val is not None:
                            st.markdown(f"""
                                <div style="display: flex; gap: 20px; font-size: 0.9rem; margin-top: 8px;">
                                    <div><b>Data value (extracted):</b> {da_val[:40]}</div>
                                    <div><b>Critic value (extracted):</b> {cr_val}</div>
                                    <div><b>Difference:</b> {diff_val:.2f}%</div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                # Button to go to Archive tab to edit/approve
                st.info("💡 Switch to the 'Report Archive & Review' tab to edit or sign off on this report and compile it to DOCX.")
                
            except Exception as e:
                status_container.empty()
                st.error(f"Execution failed: {str(e)}")
                
    st.markdown('</div>', unsafe_allow_html=True)
