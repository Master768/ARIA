"""
Alfred: The Autonomous Research Intelligence for Analytics (ARIA) Companion & Concierge
Run: python alfred.py
"""

import os
import sys
import shutil

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ANSI terminal styling
GOLD = "\033[38;2;217;155;38m"
NAVY = "\033[38;2;31;78;121m"
BLUE = "\033[38;2;43;108;176m"
GREEN = "\033[38;2;46;125;50m"
GRAY = "\033[38;2;113;128;150m"
BOLD = "\033[1m"
RESET = "\033[0m"

BANNER = rf"""{NAVY}{BOLD}
   ___       __  ____              __ 
  / _ | ___ / /_/ __/______ ____  / /_
 / __ |/ -_) __/ _// __/ -_) _ \/ __/ 
/_/ |_|\__/\__/_/ /_/  \__/_//_/\__/  
{GOLD}   Chief Concierge & Personal Companion{RESET}
"""

def print_alfred(text):
    print(f"\n{GOLD}[Alfred]:{RESET} {text}")

def setup_ide_skills():
    """Installs skills into .agents/skills/ so Antigravity and agent harnesses auto-detect them."""
    src = os.path.abspath("orchestra/skills")
    dest = os.path.abspath(".agents/skills")
    os.makedirs(dest, exist_ok=True)
    if os.path.exists(src):
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dest, item)
            if os.path.isdir(s):
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.copytree(s, d)
        print_alfred(f"{GREEN}All agent skills successfully linked to {BOLD}.agents/skills/{RESET}!")
        print_alfred("Your AI environment (Antigravity, Claude Code, Cursor) will now recognize me and all specialists natively.")
    else:
        print_alfred(f"Could not locate {src}. Please ensure you are running from the repository root.")

def init_clean_workspace():
    """Prepares clean data/ and reports/ directories for the user's custom project."""
    dirs = [
        "data/raw",
        "data/processed",
        "reports/assets",
        "reports/published",
        "models"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        keep = os.path.join(d, ".gitkeep")
        if not os.path.exists(keep):
            with open(keep, "w") as f:
                f.write("")
    print_alfred(f"{GREEN}Clean workspace initialized!{RESET}")
    print(f"  {GRAY}• data/raw/         -> Place your raw CSV, Parquet, or JSON files here{RESET}")
    print(f"  {GRAY}• data/processed/   -> Preprocessed and cleaned datasets will land here{RESET}")
    print(f"  {GRAY}• reports/published/-> Your publication-grade Word (.docx) reports will land here{RESET}")
    print_alfred("Whenever you're ready, simply ask me: 'Alfred, profile my dataset in data/raw/' and I shall commission the team.")

def list_agents():
    """Presents the roster of world-class specialists."""
    print_alfred("Allow me to present our team of specialists at your command:\n")
    roster = [
        ("Alfred", "Chief Concierge & Major-Domo", "Greets you, eases cognitive load, and coordinates all tasks."),
        ("Arthur", "Catalog Locator (Ralph Kimball)", "Discovers remote schemas, MongoDB, SQL tables, and lakehouses."),
        ("Silas", "SQL Architect (Joe Celko)", "Writes CTEs, window functions, and fast DuckDB analytical extractions."),
        ("Maya", "Data Understanding (John Tukey)", "Exploratory data analysis, multivariate distributions, and skewness."),
        ("Leo", "Data Cleaning (W. Edwards Deming)", "Leak-free pipelines, MICE imputation, Winsorization, and clean splitting."),
        ("Priya", "Feature Engineering (Kaggle GM)", "Signal extraction, interaction terms, cyclical encodings, and selection."),
        ("Julian", "Model Building (Breiman & Chen)", "LightGBM/XGBoost tournament benchmarking and Optuna tuning."),
        ("Elena", "Model Evaluation (Rudin & Lundberg)", "Cynical audit, TreeSHAP feature attributions, and calibration curves."),
        ("Marcus", "Executive Storyteller (Edward Tufte)", "Compiles publication-grade Word (.docx) reports adhering to Anthropic standards.")
    ]
    for name, title, desc in roster:
        print(f"  {BOLD}{name:<8}{RESET} | {BLUE}{title:<34}{RESET} | {GRAY}{desc}{RESET}")

def run_demonstration():
    """Launches one of the bundled demonstrations."""
    print_alfred("Which demonstration would you care to inspect?")
    print("  [1] Pulse DB: Remote Discovery, Cohort Analytics & Sample DOCX Report")
    print("  [2] Amazon E-Commerce: End-to-End Rating Prediction ML Pipeline")
    print("  [0] Return to main menu")
    choice = input(f"\n{BOLD}Select an option (0-2): {RESET}").strip()
    if choice == "1":
        print_alfred("Executing Pulse DB analytics demonstration...")
        os.system(f"{sys.executable} demonstration/pulse_analytics/scripts/analyze_user_performance.py")
        print_alfred(f"You may find the sample Word report at: {BOLD}demonstration/pulse_analytics/reports/Sample_Pulse_Performance_and_Behavioral_Audit_Report.docx{RESET}")
    elif choice == "2":
        print_alfred("Executing Amazon ML evaluation benchmark...")
        os.system(f"{sys.executable} demonstration/amazon_product_rating/scripts/evaluate_model.py")
        print_alfred(f"You may find the sample Word report at: {BOLD}demonstration/amazon_product_rating/reports/Amazon_Product_Rating_Analysis_Report.docx{RESET}")

def main():
    print(BANNER)
    print_alfred("A very good day to you, sir. I am Alfred, your personal concierge.")
    print_alfred("Welcome to ARIA (Autonomous Research Intelligence for Analytics).")
    
    while True:
        print(f"\n{NAVY}{BOLD}=== How may I be of assistance today? ==={RESET}")
        print("  [1] Initialize a clean workspace for my own dataset")
        print("  [2] Connect me with Alfred in my AI Editor (Install .agents/skills/)")
        print("  [3] Review the roster of specialized agents")
        print("  [4] Run a demonstration (Pulse DB or Amazon ML)")
        print("  [0] Bid farewell for now")
        
        choice = input(f"\n{BOLD}Your command (0-4): {RESET}").strip()
        if choice == "1":
            init_clean_workspace()
        elif choice == "2":
            setup_ide_skills()
        elif choice == "3":
            list_agents()
        elif choice == "4":
            run_demonstration()
        elif choice in ["0", "exit", "quit", "q"]:
            print_alfred("It has been my distinct pleasure, sir. Until we meet again.\n")
            break
        else:
            print_alfred("I beg your pardon, sir. Please select a valid option from the menu.")

if __name__ == "__main__":
    main()
