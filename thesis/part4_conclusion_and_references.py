import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from thesis.thesis_builder import (
    add_heading_1, add_heading_2, add_heading_3,
    add_body_p, add_bullet_point, add_styled_table
)

def build_part4(doc):
    """
    Constructs Chapter 4: Conclusion, Future Scope, References & Appendices
    Follows VIT Chennai M.Sc. Data Science Dissertation Format.
    Formatted to ensure Chapter 4 is exactly 2 pages, References 1 page, and Appendix 1 page.
    """
    
    # =========================================================================
    # CHAPTER 4: CONCLUSION, FUTURE SCOPE & REFERENCES
    # =========================================================================
    add_heading_1(doc, "CHAPTER 4: CONCLUSION, FUTURE SCOPE & REFERENCES")
    
    add_heading_2(doc, "4.1 Summary of Scientific Contributions")
    add_body_p(doc, 
        "This dissertation has presented ARIA (Autonomous Research Intelligence for Analytics), an enterprise-grade multi-agent autonomous framework designed to overcome the cognitive fragmentation, data leakage risks, and unverified hallucinations prevalent in contemporary automated data science. Through rigorous architectural design, disciplined stage-gating, and adversarial peer review, ARIA advances the state-of-the-art across key methodological dimensions:")

    add_bullet_point(doc, "Formalization of the Eight-Specialist Lifecycle: Deconstructed the full end-to-end data science lifecycle into eight dedicated specialist agents grounded in the published methodologies of renowned historical domain pioneers (Kimball, Celko, Tukey, Deming, Grandmasters, Breiman, Rudin, and Tufte). This modular specialization eliminates prompt interference and cognitive overloading.", bold_title="1. Persona-Grounded Specialization:")

    add_bullet_point(doc, "The ARIA Council Protocol: Designed and implemented the first multi-agent adversarial peer-review mechanism in automated data science. By dynamically convening specialists to cross-examine analytical proposals from competing statistical, pipeline, and modeling perspectives, ARIA neutralizes lookahead leakage, collinearity, and overfitting before code execution.", bold_title="2. Adversarial Peer Review:")

    add_bullet_point(doc, "Inviolable Architectural Invariants: Established strict operational constraints, including a zero-leakage cross-validation isolation harness, deterministic ColumnTransformer serialization, and a zero raw LaTeX typography invariant guaranteeing clean Word deliverables across all platforms.", bold_title="3. Invariant Enforcement:")

    add_heading_2(doc, "4.2 Practical Implications for Enterprise Analytics & MLOps")
    add_body_p(doc, 
        "The empirical findings of this research offer profound practical implications for industry data science organizations:")

    add_bullet_point(doc, "Elimination of Silent Failures: Automates elite-level MLOps hygiene, ensuring that all models deployed into production are mathematically isolated, cross-validated without lookahead bias, and leak-free.", bold_title="1. Modeling Hygiene:")

    add_bullet_point(doc, "Drastic Cycle-Time Compression: Compresses the journey from warehouse SQL extraction to an executive brief from weeks to minutes while maintaining publication-grade documentation.", bold_title="2. Analytical Velocity:")

    add_bullet_point(doc, "Built-In AI Governance: Out-of-the-box SHAP attributions, calibration curves, and cohort error slicing satisfy emerging regulatory mandates (e.g., EU AI Act) for compliance committees.", bold_title="3. Regulatory Compliance:")

    add_heading_2(doc, "4.3 Limitations of Autonomous Multi-Agent Systems")
    add_body_p(doc, 
        "While ARIA represents a substantial leap forward, several technical limitations must be acknowledged:")

    add_bullet_point(doc, "Token Economics & Latency: Convening multi-agent adversarial debates across 8 specialists increases LLM token consumption and latency, though this is mitigated by our dynamic gating policy.", bold_title="1. Computational Overhead:")

    add_bullet_point(doc, "Foundation Model Reasoning: ARIA relies on the LLM's capacity to synthesize valid Python and SQL; non-standard database dialects can occasionally require fallback retries.", bold_title="2. Code Synthesis Dependencies:")

    add_bullet_point(doc, "Data Modality Scope: The current implementation focuses on structured tabular and relational data. Complex unstructured multimodal inputs require dedicated visual and audio agents.", bold_title="3. Tabular Focus:")

    add_heading_2(doc, "4.4 Future Directions & Research Roadmap")
    add_body_p(doc, 
        "We chart several promising avenues for future research:")

    add_bullet_point(doc, "Continuous Agent Memory: Integrating vector-indexed graph databases to allow specialists to accumulate institutional domain memory across historical enterprise projects.", bold_title="1. Episodic Knowledge Graphs:")

    add_bullet_point(doc, "Continuous Production Monitoring: Extending Elena's mandate to streaming inference, detecting covariate shift via Kolmogorov-Smirnov tests and triggering automated model retraining.", bold_title="2. Automated Drift Monitoring:")

    add_bullet_point(doc, "Causal AI Expansion: Introducing a dedicated specialist agent to conduct causal DAG discovery, do-calculus, and counterfactual policy simulation beyond pure correlation.", bold_title="3. Causal Inference Integration:")

    doc.add_page_break()

    # =========================================================================
    # 4.5 ACADEMIC REFERENCES
    # =========================================================================
    add_heading_1(doc, "REFERENCES")
    
    refs = [
        "[1] J. Tukey, Exploratory Data Analysis. Reading, MA: Addison-Wesley, 1977.",
        "[2] R. Kimball and M. Ross, The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling, 3rd ed. New York: Wiley, 2013.",
        "[3] J. Celko, Joe Celko's SQL for Smarties: Advanced SQL Programming, 5th ed. Amsterdam: Morgan Kaufmann, 2014.",
        "[4] W. E. Deming, Out of the Crisis. Cambridge, MA: MIT Press, 2000.",
        "[5] L. Breiman, 'Random Forests,' Machine Learning, vol. 45, no. 1, pp. 5–32, 2001.",
        "[6] T. Chen and C. Guestrin, 'XGBoost: A Scalable Tree Boosting System,' in Proc. 22nd ACM SIGKDD Int. Conf., 2016, pp. 785–794.",
        "[7] G. Ke, Q. Meng, T. Finley, et al., 'LightGBM: A Highly Efficient Gradient Boosting Decision Tree,' in NeurIPS, vol. 30, 2017.",
        "[8] S. M. Lundberg and S.-I. Lee, 'A Unified Approach to Interpreting Model Predictions,' in NeurIPS, vol. 30, 2017.",
        "[9] C. Rudin, 'Stop Explaining Black Box Machine Learning Models for High Stakes Decisions,' Nature Machine Intelligence, vol. 1, pp. 206–215, 2019.",
        "[10] E. R. Tufte, The Visual Display of Quantitative Information, 2nd ed. Cheshire, CT: Graphics Press, 2001.",
        "[11] B. Minto, The Pyramid Principle: Logic in Writing and Thinking, 3rd ed. London: Financial Times, 2002.",
        "[12] S. Yao, J. Zhao, D. Yu, et al., 'ReAct: Synergizing Reasoning and Acting in Language Models,' in ICLR, 2023.",
        "[13] Q. Wu, G. Bansal, J. Zhang, et al., 'AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation,' arXiv:2308.08155, 2023.",
        "[14] C. Hong, M. Zhuge, J. Chen, et al., 'MetaGPT: Meta Programming for Multi-Agent Collaborative Framework,' arXiv:2308.00352, 2023.",
        "[15] T. Akiba, S. Sano, T. Yanase, et al., 'Optuna: A Next-generation Hyperparameter Optimization Framework,' in KDD, 2019, pp. 2623–2631.",
        "[16] F. Pedregosa, G. Varoquaux, et al., 'Scikit-learn: Machine Learning in Python,' JMLR, vol. 12, pp. 2825–2830, 2011.",
        "[17] M. Raasveldt and H. Mühleisen, 'DuckDB: An Embeddable Analytical Database,' in Proc. ACM SIGMOD, 2019, pp. 1981–1984.",
        "[18] S. Kaufman, S. Rosset, and C. Perlich, 'Leakage in Data Mining: Formulation, Detection, and Avoidance,' ACM TKDD, vol. 6, no. 4, 2012."
    ]
    for ref in refs:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.line_spacing = 1.15
        p_ref.paragraph_format.space_after = Pt(2.5)
        p_ref.paragraph_format.left_indent = Inches(0.35)
        p_ref.paragraph_format.first_line_indent = Inches(-0.35)
        run = p_ref.add_run(ref)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)

    doc.add_page_break()

    # =========================================================================
    # APPENDIX
    # =========================================================================
    add_heading_1(doc, "APPENDIX: SYSTEM PROMPTS, MATHEMATICAL SPECIFICATIONS & ARTIFACTS")
    
    add_heading_2(doc, "Appendix A: The ARIA Council Protocol System Kernel")
    add_body_p(doc, 
        "The verified operational kernel enforcing adversarial peer-review within the ARIA Council (ds-agent-council) establishes four mandatory behavioral invariants:")

    add_bullet_point(doc, "Dynamic Gating: Routine data inspections bypass the Council. High-stakes feature engineering, imputation, and modeling dilemmas mandate the Council roundtable.", bold_title="Invariant 1 (Gating):")
    add_bullet_point(doc, "Adversarial Integrity: Each specialist must provide concrete statistical, pipeline, or governance critiques. Superficial consensus is strictly prohibited.", bold_title="Invariant 2 (Integrity):")
    add_bullet_point(doc, "Zero Raw LaTeX Standard: Equations and metrics must be output as clean inline code spans (e.g., FamilySize = SibSp + Parch + 1) or Unicode mathematical symbols (±, ², ≥, ≤, ×, ÷). Raw LaTeX syntax ($...$, \\text{...}) is permanently forbidden.", bold_title="Invariant 3 (Typography):")
    add_bullet_point(doc, "Human Confirmation Gate: No final Word deliverable is published without explicit user preview and sign-off.", bold_title="Invariant 4 (Control):")

    add_heading_2(doc, "Appendix B: Reproducible Pipeline Execution Artifacts")
    add_body_p(doc, 
        "All experimental pipelines, Parquet extracts, trained model binaries, and Optuna databases generated during this research are archived in the ARIA repository structure (scripts/, data/, models/, reports/). The complete software artifact suite is fully reproducible via standard Python 3.10+ execution environments.")

    add_heading_2(doc, "Appendix C: Verified Mathematical Formulation Dictionary")
    add_bullet_point(doc, "FamilySize = SibSp + Parch + 1; Fare_Per_Person = Fare / max(FamilySize, Ticket_Freq); Is_Alone = 1 if FamilySize == 1 else 0.", bold_title="Feature Engineering:")
    add_bullet_point(doc, "x_sin = sin(2 * π * t / T), x_cos = cos(2 * π * t / T); Smoothed OOF Target: S_i = λ_i * y_mean_i + (1 - λ_i) * y_mean_global.", bold_title="Encodings:")
    add_bullet_point(doc, "VIF_j = 1 / (1 - R_j²); Brier = (1/N) * Σ (p_i - y_i)²; F_β = (1 + β²) * (Precision * Recall) / (β² * Precision + Recall).", bold_title="Model Diagnostics:")

