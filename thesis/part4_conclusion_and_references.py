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
    """
    
    # =========================================================================
    # CHAPTER 4: CONCLUSION, FUTURE SCOPE & REFERENCES
    # =========================================================================
    add_heading_1(doc, "CHAPTER 4: CONCLUSION, FUTURE SCOPE & REFERENCES")
    
    add_heading_2(doc, "4.1 Summary of Scientific Contributions")
    add_body_p(doc, 
        "This dissertation has introduced ARIA (Autonomous Research Intelligence for Analytics), an enterprise-grade multi-agent autonomous framework designed to overcome the cognitive fragmentation, data leakage risks, and unverified hallucinations prevalent in contemporary automated data science. Through rigorous architectural design, disciplined stage-gating, and adversarial peer review, ARIA advances the state-of-the-art in four key dimensions:")

    add_bullet_point(doc, "Formalization of the Eight-Specialist Lifecycle: We deconstructed the full end-to-end Data Science and Machine Learning lifecycle into eight dedicated specialist agents, each grounded in the published methodologies of renowned historical domain pioneers (Kimball, Celko, Tukey, Deming, Kaggle Grandmasters, Breiman, Rudin, and Tufte). This modular specialization completely eliminates the prompt interference and cognitive overloading that cripples monolithic LLMs.", bold_title="1. Persona-Grounded Specialization:")

    add_bullet_point(doc, "The ARIA Council Protocol: We designed and implemented the first multi-agent adversarial peer-review mechanism in automated data science. By dynamically convening specialists to cross-examine analytical proposals from competing statistical, pipeline, modeling, and governance perspectives, ARIA intercepts and neutralizes methodological vulnerabilities—such as lookahead data leakage, high VIF collinearity, and tree-depth explosion—before any code is committed to execution.", bold_title="2. Adversarial Peer Review:")

    add_bullet_point(doc, "Inviolable Architectural Invariants: ARIA established and enforced strict operational constraints, including a zero-leakage cross-validation isolation harness, deterministic ColumnTransformer serialization, and a zero raw LaTeX typography invariant that guarantees pristine, human-readable Word (.docx) deliverables across all platforms.", bold_title="3. Invariant Enforcement:")

    add_bullet_point(doc, "The Executive Concierge Architecture: Through Alfred, our major-domo concierge, we proved that non-technical corporate leaders can commission complex, multi-agent data science pipelines using intuitive natural language while retaining full control via human confirmation gates.", bold_title="4. Concierge Orchestration:")

    add_heading_2(doc, "4.2 Practical Implications for Enterprise Analytics & MLOps")
    add_body_p(doc, 
        "The empirical findings of this research offer profound practical implications for industry data science organizations:")

    add_bullet_point(doc, "Democratizing Advanced Modeling Hygiene: Junior analysts and citizen data scientists frequently commit subtle data leakage errors (e.g. fitting scalers on the entire dataset) that cause disastrous production failures. ARIA automates elite-level Kaggle and MLOps hygiene, ensuring that all models deployed into production are mathematically isolated and leak-free.", bold_title="1. Elimination of Silent Failures:")

    add_bullet_point(doc, "Accelerating Analytical Velocity: In typical enterprise settings, transitioning an analytical question from warehouse SQL extraction to an executive brief requires weeks of coordination across multiple teams. ARIA compresses this lifecycle into minutes while maintaining publication-grade documentation and governance audits.", bold_title="2. Drastic Cycle-Time Compression:")

    add_bullet_point(doc, "Regulatory and Audit Compliance: With rising regulatory mandates regarding AI fairness and explainability (e.g. EU AI Act), ARIA's automated SHAP beeswarm attributions and cohort error slicing provide out-of-the-box model governance documentation required by compliance committees.", bold_title="3. Built-In AI Governance:")

    add_heading_2(doc, "4.3 Limitations of Autonomous Multi-Agent Systems")
    add_body_p(doc, 
        "While ARIA represents a substantial leap forward, several technical limitations must be acknowledged:")

    add_bullet_point(doc, "Computational & Token Overhead: Convening multi-agent adversarial debates across 8 specialists increases LLM API token consumption and inference latency compared to simple single-agent prompting. However, this overhead is mitigated by our dynamic gating policy, which reserves the Council strictly for complex decisions.", bold_title="1. Token Economics & Latency:")

    add_bullet_point(doc, "Dependency on LLM Coding Competency: ARIA relies on the underlying LLM's capacity to synthesize syntactically valid Python and SQL. While self-verifying test assertions catch execution exceptions, highly non-standard database dialects can occasionally require fallback retries.", bold_title="2. Foundation Model Reasoning:")

    add_bullet_point(doc, "Tabular Domain Focus: The current implementation is tailored primarily for structured tabular and relational data. Complex multimodal inputs (e.g. raw unstructured video streams or biomedical 3D imaging) require dedicated specialized visual agents.", bold_title="3. Data Modality Scope:")

    add_heading_2(doc, "4.4 Future Directions & Research Roadmap")
    add_body_p(doc, 
        "We chart several promising avenues for future research:")

    add_bullet_point(doc, "Episodic Knowledge Graphs & Long-Term Memory: Integrating vector-indexed graph databases to allow specialists to accumulate institutional domain memory across historical projects.", bold_title="1. Continuous Agent Memory:")

    add_bullet_point(doc, "Automated Production Drift Monitoring: Extending Elena's mandate to real-time streaming inference, detecting covariate shift via Kolmogorov-Smirnov tests and triggering automated model retraining.", bold_title="2. Continuous Production Monitoring:")

    add_bullet_point(doc, "Causal Inference Integration: Introducing a ninth specialist agent inspired by Judea Pearl to conduct causal DAG discovery, do-calculus, and counterfactual policy simulation beyond pure statistical correlation.", bold_title="3. Causal AI Expansion:")

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
        p_ref.paragraph_format.space_after = Pt(3)
        p_ref.paragraph_format.left_indent = Inches(0.35)
        p_ref.paragraph_format.first_line_indent = Inches(-0.35)
        run = p_ref.add_run(ref)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)

    # =========================================================================
    # APPENDIX
    # =========================================================================
    add_heading_1(doc, "APPENDIX: SYSTEM PROMPTS & PIPELINE ARTIFACTS", space_before=16, space_after=8)
    
    add_heading_2(doc, "Appendix A: The ARIA Council Protocol System Kernel", space_before=10, space_after=4)
    add_body_p(doc, 
        "Below is the verified behavioral kernel enforcing adversarial cross-examination within the ARIA Council (ds-agent-council):")

    add_bullet_point(doc, "Dynamic Gating: Routine data inspections bypass the Council. High-stakes feature engineering, imputation strategies, and modeling dilemmas MANDATE the Council roundtable.", bold_title="Invariant 1:")
    add_bullet_point(doc, "Adversarial Integrity: Each specialist must provide concrete statistical, pipeline, or governance critiques. Superficial consensus is strictly prohibited.", bold_title="Invariant 2:")
    add_bullet_point(doc, "Zero Raw LaTeX Standard: Equations and metrics must be output as clean inline code spans (e.g. FamilySize = SibSp + Parch + 1) or Unicode mathematical symbols (±, ², ≥, ≤, ×, ÷). Raw LaTeX syntax ($...$, \\text{...}) is permanently forbidden.", bold_title="Invariant 3:")
    add_bullet_point(doc, "Human-in-the-Loop Confirmation Gate: No final Word deliverable is published without explicit user preview and sign-off.", bold_title="Invariant 4:")

    add_heading_2(doc, "Appendix B: Reproducible Pipeline Execution Artifacts")
    add_body_p(doc, 
        "All experimental pipelines, Parquet extracts, trained model binaries, and Optuna databases generated during this research are archived in the ARIA repository structure (scripts/, data/, models/, reports/). The complete software artifact suite is fully reproducible via standard Python 3.10+ execution environments.")
