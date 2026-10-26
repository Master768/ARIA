# Product: Orchestra (The Agentic Data Science & Analytics Framework)

## Register
framework / methodology / cli

## Users
Data Scientists, Analytics Engineers, ML Engineers, and Business Data Analysts who use modern AI coding harnesses (Google Antigravity, Claude Code, Cursor, Windsurf, Cline) to explore, model, and report on complex datasets.

## Product Purpose
Orchestra is an open-source agentic framework and repository scaffold designed specifically for Data Science and Analytics. Just as BMad standardizes software engineering workflows, Orchestra standardizes the end-to-end data science lifecycle (Exploratory Data Analysis, Statistical Hypothesis Testing, Analytical Modeling, Independent Audit/Verification, and Executive Visual Reporting) through specialized AI skills and CLI tooling.

Users do not need to configure API keys, manage external LLM billing, or host local web servers: Orchestra executes directly inside the user's existing AI coding environment, leveraging frontier models (Claude 3.7 Sonnet, Gemini 2.5 Pro/Flash, GPT-4o) and local Python sandboxes.

## Core Framework Capabilities
1. **Repository Scaffold & CLI (`orchestra-cli`)**:
   - Single-command workspace initialization (`orchestra init`) providing standard data science folder hierarchy (`data/raw`, `data/processed`, `notebooks/`, `reports/assets/`, `models/`).
   - Automated skill installer (`orchestra install-skills`) targeting Antigravity (`.agent/skills`), Claude Code (`.claude/skills`), and Cursor/Windsurf agents.
   - Project health checker (`orchestra doctor`) verifying Python environment, dependencies, and data integrity.

2. **Standardized 5-Phase Agentic DS Lifecycle**:
   - **Phase 1: Profiling & EDA (`orchestra-profile`)**: Automated schema inspection, column distributions, missing value detection, and data dictionary indexing.
   - **Phase 2: Question & Hypothesis (`orchestra-hypothesize`)**: Translates vague business questions into formal statistical hypotheses, defining primary KPIs, guardrail metrics, and segmentation dimensions.
   - **Phase 3: Analytical Execution (`orchestra-analyze`)**: Generates and runs clean, modular Python scripts (pandas, numpy, scipy, statsmodels, scikit-learn) with sandbox execution and traceback auto-healing.
   - **Phase 4: Independent Critic & Audit (`orchestra-critic`)**: Adversarial validation layer that checks AST formulas, verifies numeric assertions against script outputs (anti-hallucination gate), and audits for data leakage or p-hacking.
   - **Phase 5: Visual Synthesis & Storytelling (`orchestra-report`)**: Generates high-resolution Matplotlib/Seaborn graphics with consistent color palettes, embeds them into executive Markdown/Word reports, and exports slide decks.

3. **Zero-API-Key, BYO-Agent (Bring Your Own Agent)**:
   - Zero vendor lock-in. No need for Groq or OpenAI API keys.
   - Fully compatible with whatever model is active in Antigravity, Claude Code, Cursor, or Cline.

## Brand Personality
Methodical, Rigorous, and Scientifically Sound. The framework emphasizes statistical skepticism, reproducible data pipelines, and clear visual communication over black-box magical claims.

## Anti-references
Fragmented ad-hoc Jupyter notebooks without documentation, hallucinated LLM statistical claims without verifiable script logs, messy unstructured project folders, and brittle proprietary web UIs requiring external API tokens.

## Design Principles
1. **Reproducibility First:** Every finding in a generated report must trace back to executable Python code and raw data files.
2. **Skeptical by Default (Critic Gate):** An independent statistical critic checks computations before results are deemed reliable.
3. **Visual Clarity:** All charts must adhere to clear visual hierarchy, accessible color palettes, and self-explanatory captions.
4. **Native IDE Ergonomics:** Feels completely at home inside terminal CLI and modern agentic development environments.
