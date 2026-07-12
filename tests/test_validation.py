import pytest
from agents.data_agent import DataAgent
from agents.critic_agent import CriticAgent

def test_validation():
    import os
    if os.path.exists('data/telco_churn.csv'):
        questions = [
            'What is the average monthly charge?',
            'How many customers churned?',
            'What is the median tenure in months?'
        ]
    else:
        questions = [
            'What is the average Close price?',
            'How many total rows are in the dataset?',
            'What is the maximum High price?'
        ]

    for q in questions:
        data_result = DataAgent().ask_question(q)
        critic_result = CriticAgent().validate(q, data_result)
        print(f"Q: {q}")
        print(f"  Data Agent: {data_result}")
        print(f"  Critic: {critic_result.status}")
        
        # Verify the validation outcome
        assert "PASSED" in critic_result.status
        assert critic_result.is_valid is True

if __name__ == "__main__":
    test_validation()
