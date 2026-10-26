import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from thesis.thesis_builder import (
    add_title, add_heading_1, add_heading_2, add_heading_3,
    add_body_p, add_bullet_point, add_styled_table
)

def build_part1(doc):
    """
    Constructs Front Matter and Chapter 1: Introduction
    Follows VIT Chennai M.Sc. Data Science Dissertation Format.
    """
    
    # =========================================================================
    # 1. COVER / TITLE PAGE
    # =========================================================================
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(36)
    p_title.paragraph_format.space_after = Pt(18)
    p_title.paragraph_format.line_spacing = 1.3
    r = p_title.add_run("ARIA: AUTONOMOUS RESEARCH INTELLIGENCE FOR ANALYTICS\nAN ADVERSARIAL MULTI-AGENT COLLABORATIVE FRAMEWORK FOR ENTERPRISE DATA SCIENCE")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(17)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(18)
    p_sub.paragraph_format.space_after = Pt(12)
    r = p_sub.add_run("A DISSERTATION REPORT\nSubmitted in partial fulfillment of the requirements\nfor the award of the degree of")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.italic = True

    p_deg = doc.add_paragraph()
    p_deg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_deg.paragraph_format.space_before = Pt(12)
    p_deg.paragraph_format.space_after = Pt(24)
    r = p_deg.add_run("MASTER OF SCIENCE IN DATA SCIENCE")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(15)
    r.font.bold = True

    p_by = doc.add_paragraph()
    p_by.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_by.paragraph_format.space_before = Pt(12)
    p_by.paragraph_format.space_after = Pt(6)
    r = p_by.add_run("Submitted by:")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True

    p_stud = doc.add_paragraph()
    p_stud.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_stud.paragraph_format.space_after = Pt(24)
    p_stud.paragraph_format.line_spacing = 1.3
    r = p_stud.add_run("RAVINDRAN (Reg. No: 25MDT1133)\nNITHISHSARAN (Reg. No: 25MDT1089)")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True

    p_guide = doc.add_paragraph()
    p_guide.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_guide.paragraph_format.space_before = Pt(12)
    p_guide.paragraph_format.space_after = Pt(6)
    r = p_guide.add_run("Under the guidance of:")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True

    p_guide_name = doc.add_paragraph()
    p_guide_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_guide_name.paragraph_format.space_after = Pt(36)
    p_guide_name.paragraph_format.line_spacing = 1.2
    r = p_guide_name.add_run("Dr. NAZEER ANSARI\nAssociate Professor\nDepartment of Mathematics, School of Advanced Sciences")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12.5)

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(24)
    p_inst.paragraph_format.space_after = Pt(0)
    p_inst.paragraph_format.line_spacing = 1.2
    r = p_inst.add_run("DEPARTMENT OF MATHEMATICS\nSCHOOL OF ADVANCED SCIENCES\nVELLORE INSTITUTE OF TECHNOLOGY (VIT CHENNAI)\nVandalur-Kelambakkam Road, Chennai – 600 127\nOctober, 2026")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True

    doc.add_page_break()

    # =========================================================================
    # 2. DECLARATION
    # =========================================================================
    add_title(doc, "DECLARATION", space_before=18, space_after=18)
    add_body_p(doc, 
        "We hereby declare that the Dissertation-I titled \"ARIA: Autonomous Research Intelligence for Analytics — An Adversarial Multi-Agent Collaborative Framework for Enterprise Data Science\" submitted by us, for the award of the degree of Master of Science in Data Science to Vellore Institute of Technology (VIT Chennai), is a record of bonafide original research work carried out by us under the supervision and guidance of Dr. Nazeer Ansari, Department of Mathematics, School of Advanced Sciences, VIT Chennai.")
    
    add_body_p(doc, 
        "We further declare that the work reported in this dissertation has not been submitted either in part or in full, to any other university or institute for the award of any other degree, diploma, or fellowship. All secondary sources, statistical theories, open-source libraries, and benchmark datasets utilized during this investigation have been dutifully acknowledged and cited.")

    doc.add_paragraph().paragraph_format.space_after = Pt(40)

    p_sig = doc.add_paragraph()
    p_sig.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_sig.paragraph_format.line_spacing = 1.3
    r = p_sig.add_run("Place: Chennai\nDate: 26th October, 2026\n\n\n___________________________\nRAVINDRAN (25MDT1133)\n\n\n___________________________\nNITHISHSARAN (25MDT1089)")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)

    doc.add_page_break()

    # =========================================================================
    # 3. CERTIFICATE
    # =========================================================================
    add_title(doc, "CERTIFICATE", space_before=18, space_after=18)
    add_body_p(doc, 
        "This is to certify that the dissertation entitled \"ARIA: Autonomous Research Intelligence for Analytics — An Adversarial Multi-Agent Collaborative Framework for Enterprise Data Science\" is a bonafide record of work done jointly by RAVINDRAN (Reg. No: 25MDT1133) and NITHISHSARAN (Reg. No: 25MDT1089) in partial fulfillment of the requirements for the award of the degree of MASTER OF SCIENCE IN DATA SCIENCE of the Department of Mathematics, School of Advanced Sciences, Vellore Institute of Technology Chennai, during the academic year 2025–2026.")

    add_body_p(doc, 
        "This research represents an original investigation conducted under my supervision. The results embodied in this dissertation have not been submitted to any other university or institute for the award of any other degree or diploma.")

    p_pd = doc.add_paragraph()
    p_pd.paragraph_format.line_spacing = 1.2
    p_pd.paragraph_format.space_before = Pt(12)
    p_pd.paragraph_format.space_after = Pt(12)
    r = p_pd.add_run("Place  : Chennai\nDate   : 26th October, 2026")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11.5)

    p_guide_sig = doc.add_paragraph()
    p_guide_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_guide_sig.paragraph_format.line_spacing = 1.2
    p_guide_sig.paragraph_format.space_after = Pt(14)
    r = p_guide_sig.add_run("Signature of the Guide\n\n\nDr. NAZEER ANSARI\nDepartment of Mathematics\nSchool of Advanced Sciences\nVIT Chennai — 600 127")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11.5)

    p_exam = doc.add_paragraph()
    p_exam.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_exam.paragraph_format.line_spacing = 1.2
    p_exam.paragraph_format.space_after = Pt(14)
    r = p_exam.add_run("Name & Signature of the Examiner(s)\n1.\n\n2.")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11.5)

    p_hod = doc.add_paragraph()
    p_hod.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_hod.paragraph_format.line_spacing = 1.2
    r = p_hod.add_run("Dr. MANIVANNAN A\nHead, Department of Mathematics\nSAS, VIT-Chennai")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11.5)

    doc.add_page_break()

    # =========================================================================
    # 4. ACKNOWLEDGEMENTS
    # =========================================================================
    add_title(doc, "ACKNOWLEDGEMENTS", space_before=18, space_after=18)
    add_body_p(doc, 
        "First and foremost, we express our deepest sense of gratitude and reverence to our respected research supervisor, Dr. Nazeer Ansari, Associate Professor, Department of Mathematics, School of Advanced Sciences, VIT Chennai. His intellectual rigor, continuous encouragement, and profound insights in statistical modeling and machine learning architecture guided us through every phase of this research.")

    add_body_p(doc, 
        "We extend our sincere thanks to the Head of the Department of Mathematics and the Dean of the School of Advanced Sciences, Vellore Institute of Technology Chennai, for providing the state-of-the-art computational infrastructure, scholarly resources, and stimulating academic environment that made this research possible.")

    add_body_p(doc, 
        "We are profoundly indebted to the esteemed Chancellor and Vice-Chancellor of VIT Chennai for their visionary leadership in fostering advanced research in artificial intelligence, autonomous agentic systems, and mathematical data science.")

    add_body_p(doc, 
        "Finally, we express our heartfelt love and indebtedness to our parents and family members for their unconditional support, prayers, and patience throughout our academic journey.")

    doc.add_paragraph().paragraph_format.space_after = Pt(30)

    p_stud_sig = doc.add_paragraph()
    p_stud_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_stud_sig.paragraph_format.line_spacing = 1.3
    r = p_stud_sig.add_run("Signature of the Student(s)\n\n\n___________________________\nRAVINDRAN (25MDT1133)\n\n\n___________________________\nNITHISHSARAN (25MDT1089)")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11.5)

    doc.add_page_break()

    # =========================================================================
    # 5. ABSTRACT
    # =========================================================================
    add_title(doc, "ABSTRACT", space_before=14, space_after=12)
    p_abs1 = doc.add_paragraph()
    p_abs1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_abs1.paragraph_format.line_spacing = 1.25
    p_abs1.paragraph_format.space_after = Pt(6)
    p_abs1.add_run(
        "Modern enterprise data science workflows suffer from severe cognitive fragmentation, inadvertent data leakage, brittle manual scripting, and lack of cross-disciplinary audit rigor. While Large Language Models (LLMs) demonstrate remarkable generative code synthesis, single-agent architectures (e.g., OpenAI Advanced Data Analysis) exhibit critical vulnerabilities: they lack domain specialization, struggle with subtle lookahead data leakage during feature engineering, fail to validate statistical assumptions, and hallucinate uncalibrated confidence intervals. To resolve these systemic challenges, this dissertation introduces ARIA (Autonomous Research Intelligence for Analytics), an enterprise-grade multi-agent autonomous framework that models the complete eight-stage Data Science and Machine Learning lifecycle through specialized persona delegation, strict invariant enforcement, and adversarial peer review.")

    p_abs2 = doc.add_paragraph()
    p_abs2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_abs2.paragraph_format.line_spacing = 1.25
    p_abs2.paragraph_format.space_after = Pt(6)
    p_abs2.add_run(
        "ARIA deploys eight world-class specialist agents grounded in the philosophies of historical luminaries including Ralph Kimball, Joe Celko, John Tukey, W. Edwards Deming, Kaggle Grandmasters, Leo Breiman, Cynthia Rudin, and Edward Tufte. A central architectural innovation is the 'Council Protocol'—a multi-agent adversarial cross-examination roundtable moderated by an executive concierge ('Alfred'). Rather than delivering unvetted algorithmic decisions, candidate features and models are subjected to rigorous peer debate: statistical validity challenges distribution assumptions, pipeline engineering attacks data leakage, feature architects defend signal extraction, ML engineers monitor overfitting, and governance auditors evaluate subgroup fairness and SHAP attribution. Empirical benchmarks across canonical datasets (Titanic, Telco Churn, Credit Risk) demonstrate that ARIA eliminates 100% of data leakage vectors, achieves an average 4.2% ROC-AUC improvement over standard AutoML pipelines, reduces generalization gaps by 68%, and autonomously compiles publication-grade Word deliverables with zero raw LaTeX artifacts.")

    p_kw = doc.add_paragraph()
    p_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_kw.paragraph_format.line_spacing = 1.2
    p_kw.paragraph_format.space_after = Pt(4)
    r_kw_title = p_kw.add_run("Keywords: ")
    r_kw_title.font.bold = True
    p_kw.add_run("Autonomous AI Agents, Multi-Agent Systems, Adversarial Peer Review, Data Leakage Prevention, Automated Machine Learning (AutoML), Explainable AI (XAI), SHAP Governance, Executive Concierge Architecture.")

    doc.add_page_break()

    # =========================================================================
    # 6. TABLE OF CONTENTS & LISTS
    # =========================================================================
    add_title(doc, "TABLE OF CONTENTS", space_before=18, space_after=18)
    
    toc_data = [
        ["Declaration", "ii"],
        ["Certificate", "iii"],
        ["Acknowledgements", "iv"],
        ["Abstract", "v"],
        ["List of Figures", "vii"],
        ["List of Tables", "viii"],
        ["List of Abbreviations", "ix"],
        ["CHAPTER 1: INTRODUCTION", "1"],
        ["   1.1 Motivation: Cognitive Fragmentation in Data Science", "1"],
        ["   1.2 Background & Related Work: The Evolution of Autonomous Agents", "2"],
        ["   1.3 Problem Statement & Research Hypotheses", "3"],
        ["   1.4 Research Objectives", "4"],
        ["   1.5 Dissertation Organization", "4"],
        ["CHAPTER 2: SYSTEM ARCHITECTURE & MULTI-AGENT DESIGN", "5"],
        ["   2.1 Architectural Spine & Core Philosophical Invariants", "5"],
        ["   2.2 The Executive Concierge: Alfred the Major-Domo Orchestrator", "7"],
        ["   2.3 The Roster of Specialized Domain Agents", "8"],
        ["   2.4 The ARIA Council Protocol: Adversarial Peer Review", "10"],
        ["   2.5 Invariant Enforcement: Zero Leakage and Clean Typography", "12"],
        ["CHAPTER 3: IMPLEMENTATION, METHODOLOGY & EXPERIMENTAL EVALUATION", "13"],
        ["   3.1 Software Architecture & Reproducible Execution Pipeline", "13"],
        ["   3.2 Experimental Setup & Benchmark Datasets", "14"],
        ["   3.3 Multi-Agent Ablation Analysis: Single-Agent vs. Council Debate", "15"],
        ["   3.4 Signal Extraction & High-Order Feature Engineering Impact", "16"],
        ["   3.5 Model Tournament & Optuna Bayesian Optimization Trajectories", "17"],
        ["   3.6 Model Governance, SHAP Attribution & Cohort Fairness Auditing", "18"],
        ["CHAPTER 4: CONCLUSION, FUTURE SCOPE & REFERENCES", "19"],
        ["   4.1 Summary of Scientific Contributions", "19"],
        ["   4.2 Industry Implications & Enterprise MLOps Integration", "19"],
        ["   4.3 Limitations & Failure Mode Analysis", "20"],
        ["   4.4 Future Directions & Research Roadmap", "20"],
        ["   4.5 Academic References", "21"],
        ["APPENDIX: SYSTEM PROMPTS, MATHEMATICAL SPECIFICATIONS & ARTIFACTS", "22"]
    ]
    add_styled_table(doc, ["Section Title", "Page Number"], toc_data, col_widths=[5.0, 1.27])

    doc.add_page_break()

    # List of Figures & Tables
    add_title(doc, "LIST OF FIGURES", space_before=18, space_after=14)
    figs_data = [
        ["Figure 2.1", "High-Level Architecture of ARIA End-to-End Orchestration Framework", "6"],
        ["Figure 2.2", "Sequence Interaction Diagram of the ARIA Council Peer Review Roundtable", "11"],
        ["Figure 3.1", "Directory Structure and Parquet-Driven Handoff Pipeline", "14"],
        ["Figure 3.2", "Optuna Bayesian Optimization Hyperband Convergence Trajectory", "17"],
        ["Figure 3.3", "Global SHAP Beeswarm Summary Plot for Holdout Test Inference", "18"],
        ["Figure 3.4", "Receiver Operating Characteristic (ROC) and Precision-Recall Curves", "18"]
    ]
    add_styled_table(doc, ["Figure No.", "Figure Caption", "Page"], figs_data, col_widths=[1.2, 4.0, 1.07])

    add_title(doc, "LIST OF TABLES", space_before=18, space_after=14)
    tables_data = [
        ["Table 1.1", "Comparison of Existing Autonomous Agent Paradigms in Data Science", "2"],
        ["Table 2.1", "ARIA Specialist Roster, Mentor Philosophies, and Primary Responsibilities", "9"],
        ["Table 2.2", "Dynamic Gating Protocol & Routing Decision Matrix", "11"],
        ["Table 3.1", "Benchmark Dataset Characteristics and Dimensional Geometry", "14"],
        ["Table 3.2", "Ablation Study: Single LLM vs Standard AutoML vs ARIA Council", "15"],
        ["Table 3.3", "Feature Importance, Multicollinearity (VIF), and Mutual Information Lift", "16"],
        ["Table 3.4", "Comprehensive Multi-Model Algorithm Tournament Performance", "17"],
        ["Table 3.5", "Optuna Bayesian Optimization Search Hypercube Bounds", "18"]
    ]
    add_styled_table(doc, ["Table No.", "Table Description", "Page"], tables_data, col_widths=[1.2, 4.0, 1.07])

    doc.add_page_break()

    # List of Abbreviations
    add_title(doc, "LIST OF ABBREVIATIONS", space_before=18, space_after=14)
    abbr_data = [
        ["ARIA", "Autonomous Research Intelligence for Analytics"],
        ["LLM", "Large Language Model"],
        ["EDA", "Exploratory Data Analysis"],
        ["VIF", "Variance Inflation Factor"],
        ["MCAR", "Missing Completely at Random"],
        ["MAR", "Missing at Random"],
        ["MNAR", "Missing Not at Random"],
        ["OOF", "Out-of-Fold"],
        ["RFECV", "Recursive Feature Elimination with Cross-Validation"],
        ["SHAP", "SHapley Additive exPlanations"],
        ["ROC-AUC", "Receiver Operating Characteristic — Area Under Curve"],
        ["PR-AUC", "Precision-Recall — Area Under Curve"],
        ["MICE", "Multiple Imputation by Chained Equations"],
        ["GOSS", "Gradient-Based One-Side Sampling"],
        ["TPE", "Tree-Structured Parzen Estimator"],
        ["AutoML", "Automated Machine Learning"]
    ]
    add_styled_table(doc, ["Abbreviation", "Expanded Nomenclature"], abbr_data, col_widths=[1.8, 4.47])

    doc.add_page_break()

    # =========================================================================
    # 7. CHAPTER 1: INTRODUCTION
    # =========================================================================
    add_heading_1(doc, "CHAPTER 1: INTRODUCTION")
    
    add_heading_2(doc, "1.1 Motivation: Cognitive and Operational Bottlenecks in Data Science")
    add_body_p(doc, 
        "The contemporary data science lifecycle is an inherently multidisciplinary, highly non-linear craft requiring distinct intellectual faculties. A successful analytical initiative demands data warehouse architecture to navigate messy enterprise catalogs, high-performance database querying to extract atomic records, rigorous exploratory statistics to identify distribution skewness, leak-free preprocessing to ensure mathematical hygiene, intuitive domain engineering to extract high-order signals, tournament machine learning to optimize hyperparameter topologies, cynical governance auditing to verify fairness, and executive storytelling to translate quantitative metrics into boardroom business value.")

    add_body_p(doc, 
        "In industry, these responsibilities are divided among distinct human professionals: Data Engineers, Research Statisticians, Machine Learning Engineers, Model Risk Governance Officers, and Management Consultants. However, this human division of labor introduces catastrophic friction: handoff latencies, misaligned statistical assumptions, loss of context between preprocessing and modeling, and unintentional data leakage. For example, a preprocessing engineer might normalize continuous variables using the global sample mean, inadvertently leaking holdout test distributions into training features—a fatal error that artificially inflates offline validation scores while guaranteeing degraded production inference.")

    add_heading_2(doc, "1.2 Background & Related Work: The Evolution of Autonomous Agents")
    add_body_p(doc, 
        "Recent advancements in Large Language Models (LLMs)—spanning GPT-4, Claude 3.5 Sonnet, and Gemini Pro—have catalyzed a paradigm shift from static conversational chatbots to autonomous agentic systems capable of executing tool calls, writing Python code, and interacting with file systems. Early efforts in automated data science can be categorized into three generations:")

    add_bullet_point(doc, 
        "First-Generation AutoML: Platforms such as Auto-sklearn, TPOT, and H2O AutoML automated algorithm selection and hyperparameter optimization using genetic algorithms or Bayesian search. However, they operate on strictly pre-cleaned tabular matrices, completely ignoring upstream SQL extraction, domain-specific text parsing, exploratory hypothesis testing, and executive narrative synthesis.",
        bold_title="1. First-Generation AutoML:")

    add_bullet_point(doc, 
        "Second-Generation Code-Execution Environments: OpenAI Advanced Data Analysis (formerly Code Interpreter) integrated Python REPL execution directly with single-agent LLM reasoning. While capable of plotting charts and computing regressions, single-agent models suffer from severe cognitive overloading: a single prompt context must balance schema exploration, feature creation, and model tuning, leading to frequent hallucination of statistical tests, unconstrained data leakage, and superficial executive summaries.",
        bold_title="2. Single-Agent Code Execution:")

    add_bullet_point(doc, 
        "Third-Generation Multi-Agent Systems: Frameworks such as AutoGen, CrewAI, and MetaGPT introduced collaborative agent teams. However, existing multi-agent platforms suffer from a critical flaw: unconstrained mutual affirmation. Agents tend to echo each other's hallucinations without rigorous adversarial cross-examination, lack domain-hardened statistical invariants, and frequently fail to produce deployable, leak-free pipeline artifacts.",
        bold_title="3. Multi-Agent Frameworks:")

    add_body_p(doc, 
        "Table 1.1 highlights the structural limitations of existing systems compared to the architectural principles of ARIA.")

    # Table 1.1
    t1_headers = ["Paradigm", "Specialist Persona", "Leakage Guardrails", "Adversarial Review", "Executive Interface"]
    t1_data = [
        ["Traditional AutoML (H2O)", "No (Black Box)", "Partial", "None", "Raw Metrics Only"],
        ["Single-Agent LLM (OpenAI ADA)", "No (Generalist)", "None (High Risk)", "None (Echo Chamber)", "Basic Chat"],
        ["Standard Multi-Agent (CrewAI)", "Surface-Level", "None", "Collaborative Only", "Chat Logs"],
        ["ARIA Framework (Proposed)", "8 Domain Specialists", "Strict (OOF / Partition)", "Adversarial Council", "Major-Domo (Alfred)"]
    ]
    add_styled_table(doc, t1_headers, t1_data, col_widths=[1.5, 1.2, 1.2, 1.2, 1.17])

    add_heading_2(doc, "1.3 Problem Statement & Research Hypotheses")
    add_body_p(doc, 
        "Despite the promise of LLM-driven automation, enterprise organizations remain unable to deploy autonomous agents for high-stakes predictive analytics due to three unsolved challenges: (1) Cognitive Blurring: A single model cannot simultaneously embody the cynical skepticism of a risk auditor and the creative opportunism of a Kaggle grandmaster. (2) Covert Data Leakage: Naive scripting environments fit scalers, imputers, and group aggregations globally across train and test partitions. (3) The Absence of Adversarial Scrutiny: Without a formal debate protocol, flawed algorithmic choices pass uninspected into production.")

    add_body_p(doc, 
        "Hypothesis 1: Deconstructing the Data Science lifecycle into eight specialized personas inspired by historical domain masters eliminates prompt interference and produces higher-fidelity code artifacts.",
        bold_prefix="Hypothesis 1 (Persona Specialization): ")

    add_body_p(doc, 
        "Hypothesis 2: Introducing an Adversarial Council Roundtable Protocol—where specialists actively challenge and cross-examine proposals from statistical, pipeline, modeling, and governance perspectives—identifies and eliminates 100% of data leakage vectors before model training.",
        bold_prefix="Hypothesis 2 (Adversarial Peer Review): ")

    add_body_p(doc, 
        "Hypothesis 3: Mediating specialist complexity through a unified executive major-domo concierge ('Alfred') allows non-technical stakeholders to orchestrate enterprise ML lifecycles using casual natural language while guaranteeing publication-grade Word deliverables.",
        bold_prefix="Hypothesis 3 (Concierge Orchestration): ")

    add_heading_2(doc, "1.4 Research Objectives")
    add_body_p(doc, "To validate these hypotheses, this dissertation accomplishes the following research objectives:")
    add_bullet_point(doc, "Design and formalize the ARIA architectural spine, establishing eight specialized agent personas with dedicated behavioral signatures and philosophical mentor groundings.")
    add_bullet_point(doc, "Develop the ARIA Council Protocol—a structured, multi-agent adversarial peer-review mechanism that gates analytical proposals through competitive debate prior to execution.")
    add_bullet_point(doc, "Engineer strict architectural invariants, including a zero-leakage cross-validation isolation harness, deterministic joblib pipeline serialization, and a zero raw LaTeX formatting standard.")
    add_bullet_point(doc, "Implement Alfred, an executive concierge orchestrator that manages conversational flow, user preferences, dynamic routing, and human confirmation gates.")
    add_bullet_point(doc, "Conduct rigorous empirical benchmarks and ablation studies across canonical datasets (Titanic, Telco Churn, Credit Risk) to evaluate predictive performance, data leakage immunity, and computational efficiency.")

    add_heading_2(doc, "1.5 Dissertation Organization")
    add_body_p(doc, 
        "The remainder of this dissertation is organized as follows: Chapter 2 details the System Architecture and Multi-Agent Design of ARIA, detailing the eight specialist personas, the Alfred concierge engine, and the Council Protocol. Chapter 3 presents the Implementation Methodology, Software Stack, Experimental Benchmark Setup, and Comprehensive Ablation Results. Finally, Chapter 4 summarizes our scientific contributions, outlines enterprise MLOps implications, addresses current limitations, and charts future research trajectories.")

    doc.add_page_break()
