# Product: Orchestra (ARIA Autonomous Analytics Studio)

## Register
product

## Users
Analyst managers, product managers, and data analysts who need to review, edit, and approve multi-agent analytics reports. Their primary job is to check verification results and sign off on reports for decision-making.

## Product Purpose
Orchestra is an enterprise multi-agent analytics assistant powered by the ARIA StateGraph framework. The web dashboard acts as a human-in-the-loop gate where draft reports are reviewed, Critic validation outcomes are inspected, data charts are rendered, markdown edits are made, and final approved reports are archived (as Markdown and DOCX).

## Core System Capabilities (v2.0 Architecture)
1. **LangGraph State Machine Orchestration**: State-driven multi-agent execution pipeline (`ARIAState`) managing deterministic node transitions and double-check feedback loops across 8 modular domain suites (Strategic, Data Science, Audit, Engineering, Deterministic, Orchestration, Skills, Synthesis).
2. **Vector DB Semantic Context Retrieval**: Built-in **ChromaDB** vector store that profiles CSV/Parquet datasets, indexes schemas and column data dictionaries, and dynamically retrieves relevant table context prior to query execution.
3. **Automated Matplotlib & Seaborn Visualization**: Intelligent plot generation capability enabling the Data Agent to compute analytics, generate styled statistical charts (trendlines, distributions, comparative bar charts), export high-resolution PNGs to `reports/assets/`, and embed them inline into Markdown & Word (`.docx`) reports.
4. **Self-Healing Engineering & AST Verification**: AST formula parsing (`CriticAgent`) ensuring math consistency between Python logic and report prose, combined with automated script debuggers (`DebugAgent`) to auto-repair sandbox execution tracebacks.

## Brand Personality
Professional & Trustworthy. The interface should feel structured and reliable, utilizing clear visual hierarchy, readable data layouts, embedded chart previews, and prominent color-coded badges (green for success, red for errors) to convey correctness.

## Anti-references
Generic stock Streamlit layouts, low-contrast text on colored badges, unformatted numeric listings, cluttered sidebars, missing or unlinked visual charts, and chaotic structural grids.

## Design Principles
1. **Evidence First:** Numeric correctness, validation logs (from the Critic Agent), and visual chart evidence must be immediately visible and clear.
2. **Typographic & Visual Rhythm:** Report drafts must present text with clean typography, readable fonts, and centered high-resolution Matplotlib/Seaborn graphics.
3. **Frictionless Sign-off:** The review, edit, image inspection, and approve actions should follow a logical top-to-bottom sequence.

## Accessibility & Inclusion
- WCAG AA compliant contrast ratios for status labels and badges.
- Responsive layout supporting standard desktop and laptop screen sizes.
