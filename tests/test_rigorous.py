import sys
import time
from agents.data_agent import DataAgent
from agents.critic_agent import CriticAgent

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def run_rigorous_evaluation():
    questions = [
        "What is the average monthly charge?",
        "How many customers churned?",
        "What is the median tenure in months?",
        "How many female customers are in the dataset?",
        "What is the maximum monthly charge?",
        "How many senior citizens are in the dataset?",
        "How many customers have phone service (PhoneService == 'Yes')?",
        "What is the average tenure of customers in months?",
        "What is the total number of customers who have a partner (Partner == 'Yes')?",
        "What is the minimum tenure of customers in months?",
        "How many customers are not senior citizens (SeniorCitizen == 0)?"
    ]
    
    passed_count = 0
    total_count = len(questions)
    results = []
    
    print("\n==================================================")
    print("      RIGOROUS MULTI-AGENT VALIDATION RUN         ")
    print("==================================================\n")
    
    data_agent = DataAgent()
    critic_agent = CriticAgent()
    
    for i, q in enumerate(questions, start=1):
        print(f"Test case {i}/{total_count}: '{q}'")
        
        # Cooldown sleep before starting case
        if i > 1:
            print("  [Cooldown] Sleeping 5s to avoid overloading Ollama...")
            time.sleep(5.0)

        # Run Data Agent with retry for transient 500 errors
        data_res = None
        for attempt in range(2):
            print(f"  Running Data Agent (Attempt {attempt+1})...")
            data_res = data_agent.ask_question(q)
            output_text = data_res.get('output', '').strip()
            
            # If it's a 500 error or empty, retry after sleep
            if "500" in output_text or not output_text:
                print(f"    WARNING: Transient error or empty output detected. Output: '{output_text}'")
                if attempt == 0:
                    print("    Sleeping 10s before retry...")
                    time.sleep(10.0)
                    continue
            break

        print(f"  Data Agent Output: {data_res.get('output', '').strip()}")
        
        # Sleep before Critic
        time.sleep(2.0)
        
        # Run Critic Validation with retry for transient errors
        critic_res = None
        for attempt in range(2):
            print(f"  Running Critic Agent Verification (Attempt {attempt+1})...")
            critic_res = critic_agent.validate(q, data_res)
            
            if "Ollama error" in critic_res.status or critic_res.status == "FAILED (Extraction failure)":
                print(f"    WARNING: Critic validation failed with transient error: {critic_res.status}")
                if attempt == 0:
                    print("    Sleeping 10s before retry...")
                    time.sleep(10.0)
                    continue
            break
            
        print(f"  Critic Verification Status: {critic_res.status}")
        
        score = 1 if critic_res.is_valid else 0
        passed_count += score
        status_str = "PASS" if critic_res.is_valid else "FAIL"
        
        results.append({
            "num": i,
            "question": q,
            "data_output": data_res.get('output', '').strip(),
            "critic_status": critic_res.status,
            "status": status_str,
            "score": f"{score}/1"
        })
        print("-" * 50)
        
    print("\n==================================================")
    print("                EVALUATION SUMMARY                ")
    print("==================================================")
    print(f"Total Test Cases: {total_count}")
    print(f"Passed:           {passed_count}")
    print(f"Failed:           {total_count - passed_count}")
    print(f"Success Rate:     {(passed_count / total_count) * 100:.1f}%")
    print(f"Final Score:      {passed_count}/{total_count}")
    print("==================================================\n")
    
    print(f"{'No.':<4} | {'Test Case / Question':<60} | {'Score':<6} | {'Status':<6}")
    print("-" * 85)
    for r in results:
        # Truncate question if it's too long
        q_text = r['question'][:60]
        print(f"{r['num']:<4} | {q_text:<60} | {r['score']:<6} | {r['status']:<6}")
    print("-" * 85)

if __name__ == "__main__":
    run_rigorous_evaluation()
