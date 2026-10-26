import os
import sys
import docx

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from thesis.thesis_builder import create_base_document
from thesis.part1_front_matter_and_intro import build_part1
from thesis.part2_system_architecture import build_part2
from thesis.part3_implementation_and_results import build_part3
from thesis.part4_conclusion_and_references import build_part4

def main():
    print("=" * 60)
    print("ARIA THESIS COMPILER — VIT CHENNAI M.SC. DATA SCIENCE")
    print("=" * 60)
    
    doc = create_base_document()
    
    print("\n[1/4] Compiling Part 1: Front Matter & Chapter 1 (Introduction)...")
    build_part1(doc)
    
    print("[2/4] Compiling Part 2: Chapter 2 (System Architecture & Council Protocol)...")
    build_part2(doc)
    
    print("[3/4] Compiling Part 3: Chapter 3 (Implementation & Experimental Results)...")
    build_part3(doc)
    
    print("[4/4] Compiling Part 4: Chapter 4 (Conclusion, References & Appendices)...")
    build_part4(doc)
    
    # Target file paths
    out_dir_local = os.path.abspath("reports/published")
    os.makedirs(out_dir_local, exist_ok=True)
    out_path_local = os.path.join(out_dir_local, "ARIA_Dissertation_MSc_Data_Science.docx")
    
    # Also save to user's Test 1 directory
    out_dir_test1 = r"C:\Users\Ravin\OneDrive\Desktop\Test 1"
    out_path_test1 = os.path.join(out_dir_test1, "ARIA_Dissertation_MSc_Data_Science.docx")
    out_path_test1_edit = os.path.join(out_dir_test1, "ARIA_Dissertation_MSc_Data_Science edit.docx")
    
    doc.save(out_path_local)
    print(f"\n[SUCCESS] Document saved locally to: {out_path_local}")
    
    try:
        doc.save(out_path_test1)
        print(f"[SUCCESS] Document saved to Test 1 workspace: {out_path_test1}")
    except Exception as e:
        print(f"[WARNING] Could not save directly to Test 1: {e}")

    try:
        doc.save(out_path_test1_edit)
        print(f"[SUCCESS] Document saved to Test 1 edit target: {out_path_test1_edit}")
    except Exception as e:
        print(f"[WARNING] Could not save directly to Test 1 edit target: {e}")
        
    print(f"\nTotal Paragraphs: {len(doc.paragraphs)}")
    print(f"Total Tables: {len(doc.tables)}")
    print("Compilation complete!")

if __name__ == "__main__":
    main()
