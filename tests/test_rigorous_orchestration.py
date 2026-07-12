import sys
import os
import json
import time
from agents.orchestrator import OrchestratorAgent

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def run_rigorous_orchestration_test():
    business_queries = [
        "Why did churn spike in Q1?",
        "What is the profile of month-to-month contract customers?",
        "What is the baseline characteristics of senior citizen customers?"
    ]
    
    passed_count = 0
    total_count = len(business_queries)
    results = []
    
    print("\n==================================================")
    print("    RIGOROUS ORCHESTRATION PIPELINE TESTS         ")
    print("==================================================\n")
    
    orchestrator = OrchestratorAgent()
    
    for i, q in enumerate(business_queries, start=1):
        print(f"Orchestration Test Case {i}/{total_count}: '{q}'")
        
        # Cooldown sleep between queries
        if i > 1:
            print("  [Cooldown] Sleeping 10s before next orchestration pipeline run...")
            time.sleep(10.0)
            
        try:
            state = orchestrator.plan_and_execute(q)
            status = state.get("status", "FAILED")
            sub_tasks = state.get("sub_tasks", [])
            
            # Verify if all tasks passed
            all_sub_tasks_complete = len(sub_tasks) >= 2 and all(t.get("status") == "COMPLETE" for t in sub_tasks)
            
            if status == "COMPLETE" and all_sub_tasks_complete:
                score = 1
                passed_count += 1
                status_str = "PASS"
            else:
                score = 0
                status_str = "FAIL"
                
            results.append({
                "num": i,
                "query": q,
                "sub_tasks_count": len(sub_tasks),
                "status": status_str,
                "score": f"{score}/1",
                "details": f"Master status: {status}, {len([t for t in sub_tasks if t.get('status') == 'COMPLETE'])}/{len(sub_tasks)} sub-tasks complete"
            })
            
        except Exception as e:
            results.append({
                "num": i,
                "query": q,
                "sub_tasks_count": 0,
                "status": "FAIL",
                "score": "0/1",
                "details": f"Crash: {str(e)}"
            })
            
        print("-" * 50)
        
    print("\n==================================================")
    print("             ORCHESTRATION SUMMARY                ")
    print("==================================================")
    print(f"Total Pipelines Run: {total_count}")
    print(f"Passed:              {passed_count}")
    print(f"Failed:              {total_count - passed_count}")
    print(f"Success Rate:        {(passed_count / total_count) * 100:.1f}%")
    print(f"Final Score:         {passed_count}/{total_count}")
    print("==================================================\n")
    
    print(f"{'No.':<4} | {'Business Query':<45} | {'Sub-tasks':<9} | {'Score':<6} | {'Status':<6}")
    print("-" * 80)
    for r in results:
        q_text = r['query'][:45]
        print(f"{r['num']:<4} | {q_text:<45} | {r['sub_tasks_count']:<9} | {r['score']:<6} | {r['status']:<6}")
    print("-" * 80)

if __name__ == "__main__":
    run_rigorous_orchestration_test()
