import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from thesis.thesis_builder import (
    add_heading_1, add_heading_2, add_heading_3,
    add_body_p, add_bullet_point, add_callout_box, add_styled_table
)

def build_part2(doc):
    """
    Constructs Chapter 2: System Architecture & Multi-Agent Design
    Follows VIT Chennai M.Sc. Data Science Dissertation Format.
    """
    
    # =========================================================================
    # CHAPTER 2: SYSTEM ARCHITECTURE & MULTI-AGENT DESIGN
    # =========================================================================
    add_heading_1(doc, "CHAPTER 2: SYSTEM ARCHITECTURE & MULTI-AGENT DESIGN")
    
    add_heading_2(doc, "2.1 Architectural Spine & Core Philosophical Invariants")
    add_body_p(doc, 
        "The architecture of ARIA is constructed upon a foundational principle: autonomous data science cannot succeed as an unconstrained monolithic generation task. Instead, it must operate as a disciplined spine of invariant-preserving, stage-gated transformations. In classical software engineering, pipelines enforce strong typing and hermetic builds; in ARIA, we formalize the Data Science Lifecycle through an artifact-driven state machine where each transition between analytical stages is mediated by explicit Parquet contracts, serializable pipeline definitions, and self-verifying test assertions.")

    add_body_p(doc, 
        "Figure 2.1 illustrates the architectural topology of ARIA. The framework segregates cognitive responsibilities into three distinct layers: (1) The Concierge & Orchestration Layer, (2) The Specialist Execution Layer, and (3) The Adversarial Governance & Council Layer.")

    # High-level ASCII / Textual Architecture diagram in stylized table
    arch_data = [
        ["Concierge Layer", "Alfred (Executive Concierge & Major-Domo)", "Conversational interface, casual intent parsing, human confirmation gates."],
        ["Ingestion Layer", "Arthur (Source Discovery) + Silas (SQL / DuckDB)", "Catalog navigation, ER schema mapping, sargable CTE query execution."],
        ["Exploration Layer", "Maya (EDA & Distributions)", "Tukey statistical moments, VIF collinearity, MCAR missingness tests, UMAP."],
        ["Hygiene Layer", "Leo (Leak-Free Preprocessing)", "Deming quality principles, train/test split isolation, ColumnTransformer serialization."],
        ["Signal Layer", "Priya (Feature Engineering)", "Kaggle Grandmaster tactics, cyclical encoding, Out-of-Fold target aggregations."],
        ["Tournament Layer", "Julian (Modeling & Optuna)", "Breiman bagging & gradient boosting tournament, TPE Bayesian hyperparameter tuning."],
        ["Auditing Layer", "Elena (Model Evaluation & Governance)", "Rudin white-box scrutiny, SHAP beeswarm attributions, cohort error slicing."],
        ["Storytelling Layer", "Marcus (Executive Storytelling)", "Tufte data-to-ink ratio, Anthropic DOCX compilation, slide deck authoring."],
        ["Council Layer", "The ARIA Council (Adversarial Roundtable)", "Multi-agent cross-examination of complex, high-stakes hypotheses."]
    ]
    add_styled_table(doc, ["Architectural Layer", "Assigned Specialist", "Core Functional Invariant"], arch_data, col_widths=[1.5, 2.2, 2.57])

    add_heading_2(doc, "2.2 The Executive Liaison: Alfred the Major-Domo Orchestrator")
    add_body_p(doc, 
        "One of the primary friction points of modern AI tools is the user experience burden. Non-technical executives, product managers, and senior researchers often struggle with brittle prompt engineering, complex syntax flags, or navigating fragmented file trees. To solve this, ARIA introduces Alfred, an executive concierge and major-domo inspired by the quintessential British butler (Alfred Pennyworth) combined with the proactive computational intelligence of JARVIS.")

    add_body_p(doc, 
        "Alfred serves as the sole direct interlocutor between the human user and the underlying specialist agents. Operating with polished courtesy, warmth, and quiet dignity, Alfred performs three vital orchestration functions:")

    add_bullet_point(doc, 
        "Effortless Delegation & Intent Parsing: The user communicates in natural, casual language ('Alfred, check the users in that database and see who is burning out'). Alfred interprets the latent data science task, decomposes the analytical objectives, and commissions Silas and Maya behind the scenes without requiring the user to specify table joins or statistical methods.",
        bold_title="1. Effortless Delegation:")

    add_bullet_point(doc, 
        "Contextual Companionship & Cognitive Relief: Alfred monitors the cadence of analytical work, provides reassuring updates, manages personal preferences, and gracefully handles unexpected data exceptions without exposing raw stack traces to the user.",
        bold_title="2. Attentive Companionship:")

    add_bullet_point(doc, 
        "The Mandatory Human Confirmation Gate: In accordance with high-stakes enterprise governance, Alfred enforces an inviolable rule: no final client Word (.docx) deliverable is ever published without presenting an executive summary preview and soliciting explicit user sign-off.",
        bold_title="3. Human-in-the-Loop Gate:")

    add_heading_2(doc, "2.3 The Roster of Specialized Domain Agents")
    add_body_p(doc, 
        "To avoid the cognitive blurring that plagues generalist LLMs, ARIA establishes eight dedicated specialist agents. Each agent is equipped with a distinct behavioral signature, a curated prompt kernel, and foundational grounding in the published philosophy of a legendary pioneer:")

    add_heading_3(doc, "2.3.1 Arthur (Ralph Kimball): Data Source Discovery & Catalog Navigation")
    add_body_p(doc, 
        "Inspired by Ralph Kimball, the pioneer of dimensional modeling, Arthur navigates enterprise data catalogs, parses entity-relationship (ER) schemas, identifies fact and dimension tables, and pinpoints candidate sources for any business inquiry. Arthur produces 'data/source_discovery_manifest.md', outlining primary keys, foreign key joins, and grain definitions.")

    add_heading_3(doc, "2.3.2 Silas (Joe Celko): SQL Architecture & High-Performance Extraction")
    add_body_p(doc, 
        "Inspired by Joe Celko, author of 'SQL for Smarties', Silas writes optimized, production-grade SQL utilizing Common Table Expressions (CTEs), window functions, and sargable filters. Silas executes queries against DuckDB, PostgreSQL, or Snowflake, enforcing zero 'SELECT *' policies and safe division (NULLIF) to export clean Parquet extracts to 'data/raw/'.")

    add_heading_3(doc, "2.3.3 Maya (John Tukey): Exploratory Data Analysis & Distribution Profiling")
    add_body_p(doc, 
        "Inspired by John Tukey, the father of Exploratory Data Analysis, and Florence Nightingale, Maya champions distribution honesty. She computes higher-order moments (skewness, kurtosis), diagnoses multicollinearity via Variance Inflation Factors (VIF), conducts Little's MCAR tests on missingness, and executes UMAP high-dimensional manifold projections. She hands off 'data/data_understanding_report.md' and publication-grade EDA visualizations.")

    add_heading_3(doc, "2.3.4 Leo (W. Edwards Deming): Data Cleaning & Leak-Free Preprocessing")
    add_body_p(doc, 
        "Inspired by W. Edwards Deming and total quality management, Leo treats data preprocessing as a zero-defect manufacturing process. His golden rule is strict partition isolation: preprocessors (StandardScaler, IterativeImputer, TargetEncoder) fit strictly on training data and transform test data. Leo serializes the end-to-end ColumnTransformer pipeline to 'models/preprocessor.joblib' and exports cleaned Parquet matrices.")

    add_heading_3(doc, "2.3.5 Priya (Kaggle Grandmaster): Feature Engineering Architect")
    add_body_p(doc, 
        "Inspired by top-ranked Kaggle Grandmasters, Priya extracts non-linear domain signals that algorithms cannot learn on their own. She constructs continuous trigonometric cyclical time encodings (sin/cos), computes Out-of-Fold (OOF) target aggregations without lookahead bias, and executes a 4-stage feature selection cascade (Variance -> Collinearity -> Mutual Information -> RFECV), saving feature matrices to 'data/features/'.")

    add_heading_3(doc, "2.3.6 Julian (Leo Breiman & Tianqi Chen): Machine Learning Tournament & Optuna Tuning")
    add_body_p(doc, 
        "Inspired by Leo Breiman (Random Forests) and Tianqi Chen (XGBoost), Julian believes in empirical tournaments over algorithmic dogma. He benchmarks candidate algorithms (Linear, Random Forest, HistGradientBoosting, LightGBM, XGBoost, CatBoost) under identical stratified cross-validation, optimizes hyperparameters using Optuna's Tree-Structured Parzen Estimator (TPE), and enforces strict regularization if the Generalization Gap (Train Score - CV Score) exceeds 0.10.")

    add_heading_3(doc, "2.3.7 Elena (Cynthia Rudin & Scott Lundberg): Model Evaluation & Governance Auditor")
    add_body_p(doc, 
        "Inspired by Cynthia Rudin (interpretable ML) and Scott Lundberg (SHAP), Elena is the cynical auditor who red-teams every champion model. She audits Precision-Recall AUC (PR-AUC), Brier score calibration, and conducts automated cohort error slicing across demographic subgroups. Using TreeSHAP beeswarm and waterfall attributions, she verifies that models make predictions for legitimate causal reasons rather than spurious proxies before issuing her governance verdict.")

    add_heading_3(doc, "2.3.8 Marcus (Edward Tufte & Barbara Minto): Executive Storytelling & Publication")
    add_body_p(doc, 
        "Inspired by Edward Tufte and Barbara Minto, Marcus synthesizes complex quantitative findings into high-impact C-suite deliverables. He applies the Minto Pyramid Principle (Situation -> Complication -> Question -> Answer), adheres to Tufte's data-to-ink ratio maximization, and compiles publication-grade Word (.docx) deliverables utilizing the Anthropic DOCX specification.")

    # Table 2.1
    t2_headers = ["Specialist Agent", "Philosophical Inspiration", "Primary Mandate", "Handoff Deliverable"]
    t2_data = [
        ["Arthur", "Ralph Kimball", "Data catalog navigation & dimensional schema mapping", "source_discovery_manifest.md"],
        ["Silas", "Joe Celko", "Optimized SQL CTE extraction via DuckDB / Parquet", "data/raw/[dataset].parquet"],
        ["Maya", "John Tukey", "Multivariate statistical profiling, VIF, and MCAR tests", "data_understanding_report.md"],
        ["Leo", "W. Edwards Deming", "Leak-free preprocessing & ColumnTransformer serialization", "models/preprocessor.joblib"],
        ["Priya", "Kaggle Grandmaster", "Cyclical transforms, OOF group statistics, RFECV", "data/features/X_train.parquet"],
        ["Julian", "Leo Breiman & Tianqi Chen", "Algorithm tournament & Optuna Bayesian optimization", "models/champion_model.joblib"],
        ["Elena", "Cynthia Rudin", "SHAP explainability, cohort fairness, governance audit", "model_evaluation_report.md"],
        ["Marcus", "Edward Tufte", "Anthropic DOCX reports, slide decks, executive briefs", "reports/published/[Report].docx"]
    ]
    add_styled_table(doc, t2_headers, t2_data, col_widths=[1.1, 1.4, 2.2, 1.57])

    add_heading_2(doc, "2.4 The ARIA Council Protocol: Adversarial Peer Review Roundtable")
    add_body_p(doc, 
        "In traditional multi-agent systems, agents collaborate in a purely affirmative manner: if an agent proposes an approach, other agents offer polite validation. In high-stakes statistical modeling, this unconstrained agreement results in compound errors. For instance, an aggressive feature engineering proposal may produce high apparent correlation by incorporating future information, which a modeling agent gladly utilizes to achieve near-perfect cross-validation scores.")

    add_body_p(doc, 
        "To break this echo chamber, ARIA introduces the Council Protocol (ds-agent-council). The Council is governed by a strict Dynamic Gating Policy: routine, deterministic tasks (e.g. data inspection, direct queries, standard scaling) bypass the Council to avoid unnecessary overhead. However, whenever an analytical inquiry is complex, strategic, or ambiguous—regardless of the dataset—Alfred convenes the specialists into an adversarial roundtable where proposals are actively interrogated from competing viewpoints.")

    add_body_p(doc, 
        "The following transcript snippet demonstrates a live adversarial cross-examination during a feature engineering session:")

    add_callout_box(doc, "Alfred", "Major-Domo & Concierge", 
        "Order in the council. Our client desires an optimal strategy to resolve missing Age values and engineer a predictive FamilySurvival signal. Priya, table your proposal.")

    add_callout_box(doc, "Priya", "Feature Engineering Architect", 
        "We extract titles from Name and impute missing Age using title medians. Then we group passengers by Surname to calculate historical family survival rates, capturing shared evacuation outcomes.")

    add_callout_box(doc, "Leo", "Data Cleaning Engineer", 
        "Hold on, Priya! That surname group calculation contains catastrophic target leakage if done naively across the combined dataset. Any family survival signal must strictly use Out-of-Fold (OOF) cross-validation on train, and fallback to global title medians on test!")

    add_callout_box(doc, "Maya", "Exploratory Data Scientist", 
        "I must challenge Priya's age imputation as well. The title Miss spans ages from 9 months to 63 years old. A flat median assigned to an infant baby Miss traveling with parents distorts infant mortality patterns. We must condition age imputation on both Title and Parch.")

    add_callout_box(doc, "Elena", "Cynical Governance Auditor", 
        "Spot on, Maya. And common surnames like Smith and Davies link completely unrelated strangers from different classes into fake family units. We must group by Surname + Pclass + Ticket_Prefix to eliminate false family links.")

    add_callout_box(doc, "Julian", "Machine Learning Engineer", 
        "From a tree-split perspective, passing a continuous family survival rate into LightGBM will overfit families of size 2. I recommend quantizing this into discrete, regularized states with Laplace smoothing.")

    add_callout_box(doc, "Alfred", "Consensus Verdict", 
        "The Council has spoken. We approve the family signal with: (1) Title + Parch conditioned age imputation, (2) Surname + Pclass + Ticket compound grouping, (3) OOF leak-free cross-validation, and (4) discrete regularized survival states.")

    add_heading_2(doc, "2.5 Invariant Enforcement: Zero Data Leakage and Clean Typography Standards")
    add_body_p(doc, 
        "ARIA enforces two critical architectural invariants across all agents and deliverables:")

    add_bullet_point(doc, 
        "Zero Data Leakage Invariant: Data preprocessing and feature engineering code must adhere to strict temporal and topological isolation. All statistical estimates (means, standard deviations, imputation medians, target frequency tables) are computed solely on the training partition. Transformers are fitted once via .fit_transform() and serialized into preprocessor.joblib, ensuring identical, contamination-free application during holdout testing and production inference.",
        bold_title="1. Zero Data Leakage:")

    add_bullet_point(doc, 
        "Zero Raw LaTeX Standard: Language models routinely output raw academic LaTeX strings (e.g. $\\text{FamilySize} = \\text{SibSp} + \\text{Parch}$). Because Microsoft Word, terminal consoles, and standard Markdown viewers do not natively render LaTeX math, these equations appear as unreadable broken text. ARIA strictly enforces that all formulas and metrics be expressed as clean inline code spans (e.g. FamilySize = SibSp + Parch + 1, VIF = 1 / (1 - R²)) or standard Unicode mathematical typography (±, ², ≥, ≤, ×, ÷).",
        bold_title="2. Clean Typography Standard:")

    doc.add_page_break()
