import sys
import os
import json
import pytest
from agents.orchestrator import OrchestratorAgent

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def test_orchestration():
    import os
    orchestrator = OrchestratorAgent()
    # Execute the master planning and orchestration loop
    if os.path.exists('data/telco_churn.csv'):
        result = orchestrator.plan_and_execute('Why did churn spike in Q1?')
    else:
        result = orchestrator.plan_and_execute('What are the key statistics of the close price and high price of the btc?')
    
    state_file = 'config/task_state.json'
    assert os.path.exists(state_file)
    
    with open(state_file, encoding='utf-8') as f:
        state = json.load(f)
        
    print("\n--- Serialized Task State JSON ---")
    print(json.dumps(state, indent=2))
    
    # Assertions to ensure standard completion and validation passing
    assert state['status'] == 'COMPLETE'
    assert len(state['sub_tasks']) >= 2
    assert all(t['status'] == 'COMPLETE' for t in state['sub_tasks'])

if __name__ == "__main__":
    test_orchestration()
