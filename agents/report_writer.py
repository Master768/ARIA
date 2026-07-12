import os
import json
from datetime import datetime
import docx

class ReportWriter:
    def __init__(self):
        self.reports_dir = os.path.abspath("reports")
        os.makedirs(self.reports_dir, exist_ok=True)
        self.manifest_path = os.path.join(self.reports_dir, "manifest.json")
        self._init_manifest()

    def _init_manifest(self):
        """Initializes manifest.json if it doesn't exist."""
        if not os.path.exists(self.manifest_path):
            with open(self.manifest_path, "w", encoding="utf-8") as f:
                json.dump({"reports": []}, f, indent=2)

    def _load_manifest(self) -> dict:
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_manifest(self, data: dict):
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def compile_report(self, task_state: dict) -> str:
        """
        Compiles the validated findings from the task state into a structured Markdown draft report.
        Also registers the report draft in manifest.json.
        """
        # Determine file name parameters
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
        original_q = task_state.get("original_question", "data_analysis")
        
        # Clean question string to make a safe topic slug
        topic_slug = "".join(c if c.isalnum() else "_" for c in original_q.lower())
        topic_slug = "_".join(filter(None, topic_slug.split("_")))[:30]
        
        file_name = f"{timestamp_str}_{topic_slug}_DRAFT.md"
        file_path = os.path.join(self.reports_dir, file_name)
        
        # Build markdown content
        md_lines = []
        md_lines.append(f"# Analysis Report: {original_q}")
        md_lines.append(f"\n**Date:** {task_state.get('timestamp', timestamp_str)}")
        md_lines.append(f"**Status:** {task_state.get('status', 'DRAFT')}\n")
        md_lines.append("## Executive Summary")
        md_lines.append(task_state.get("final_summary", "No summary provided."))
        md_lines.append("\n## Detailed Findings")
        
        for task in task_state.get("sub_tasks", []):
            md_lines.append(f"### Sub-task {task.get('id')}: {task.get('description')}")
            md_lines.append(f"- **Query:** {task.get('query')}")
            
            agent_res = task.get("data_agent_result", {})
            if isinstance(agent_res, dict):
                output_content = agent_res.get("output", "No output generated.")
            else:
                output_content = str(agent_res)
            
            md_lines.append(f"- **Result:** {output_content}")
            md_lines.append(f"- **Critic Verification:** {task.get('critic_validation', 'PENDING')}")
            md_lines.append("")
            
        md_content = "\n".join(md_lines)
        
        # Save markdown report
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md_content)
            
        # Register draft in manifest.json
        manifest = self._load_manifest()
        # Prevent duplicate entries for the same path
        manifest["reports"] = [r for r in manifest["reports"] if r.get("md_path") != file_name]
        
        manifest["reports"].append({
            "timestamp": task_state.get("timestamp", datetime.now().isoformat()),
            "original_question": original_q,
            "status": "DRAFT",
            "validation_status": task_state.get("status"), # COMPLETE / NEEDS_REVIEW
            "md_path": file_name,
            "docx_path": None
        })
        self._save_manifest(manifest)
        
        return md_content

    def convert_to_docx(self, markdown_content: str, docx_path: str):
        """
        Parses Markdown content and writes a professionally styled Word document.
        """
        doc = docx.Document()
        
        # Define basic styling helper for bold markers
        def add_formatted_paragraph(doc, text, style=None):
            p = doc.add_paragraph(style=style)
            parts = text.split("**")
            for idx, part in enumerate(parts):
                is_bold = (idx % 2 == 1)
                p.add_run(part).bold = is_bold
            return p

        lines = markdown_content.splitlines()
        for line in lines:
            line_strip = line.strip()
            if not line_strip:
                continue
                
            if line_strip.startswith("# "):
                doc.add_heading(line_strip[2:], level=1)
            elif line_strip.startswith("## "):
                doc.add_heading(line_strip[3:], level=2)
            elif line_strip.startswith("### "):
                doc.add_heading(line_strip[4:], level=3)
            elif line_strip.startswith("- ") or line_strip.startswith("* "):
                # bullet item
                add_formatted_paragraph(doc, line_strip[2:], style="List Bullet")
            else:
                add_formatted_paragraph(doc, line_strip)
                
        doc.save(docx_path)

    def update_manifest_status(self, draft_filename: str, new_status: str, new_filename: str = None, docx_filename: str = None):
        """Updates report status and file paths inside reports/manifest.json."""
        manifest = self._load_manifest()
        found = False
        for report in manifest["reports"]:
            if report.get("md_path") == draft_filename:
                report["status"] = new_status
                if new_filename:
                    report["md_path"] = new_filename
                if docx_filename:
                    report["docx_path"] = docx_filename
                found = True
                break
        if found:
            self._save_manifest(manifest)
