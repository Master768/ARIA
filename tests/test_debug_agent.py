import pytest
from unittest.mock import Mock, MagicMock
from agents.debug_agent import DebugAgent, CodeExecutionError

class TestDebugAgent:
    
    @pytest.fixture
    def setup(self):
        """Setup Debug Agent with mocked dependencies"""
        llm_mock = Mock()
        sandbox_mock = Mock()
        debug_agent = DebugAgent(llm_mock, "mock-model", sandbox_mock, max_retries=3)
        return debug_agent, llm_mock, sandbox_mock
    
    def test_fix_keyerror(self, setup):
        """Test fixing KeyError (missing column)"""
        debug_agent, llm_mock, sandbox_mock = setup
        
        # Create original error
        error = CodeExecutionError(
            error_type="KeyError",
            error_message="'Churn_Rate'",
            traceback="KeyError: 'Churn_Rate'",
            code_executed="df['Churn_Rate'].mean()",
            execution_time_ms=100
        )
        
        # Mock analysis response
        mock_analysis = MagicMock()
        mock_analysis.message.content = '{"classification": "schema_error", "root_cause": "Column name mismatch", "fix_approach": "Use correct column name", "explanation": "Use correct column name"}'
        
        # Mock proposed code response
        mock_code = MagicMock()
        mock_code.message.content = "df['Churn'].mean()"
        
        llm_mock.chat.side_effect = [mock_analysis, mock_code]
        
        # Mock sandbox: first attempt succeeds
        sandbox_mock.return_value = "0.21"
        
        result = debug_agent.handle_error(error, "What is the churn rate?", task_id=1)
        
        assert result.status == "FIXED"
        assert len(result.attempts) == 1
        assert result.final_result == "0.21"
        assert result.final_code == "df['Churn'].mean()"
    
    def test_max_retries_exceeded(self, setup):
        """Test when max retries is exceeded"""
        debug_agent, llm_mock, sandbox_mock = setup
        
        error = CodeExecutionError(
            error_type="TypeError",
            error_message="unsupported operand types",
            traceback="TypeError: unsupported operand types",
            code_executed="df['value'] / df['count']",
            execution_time_ms=100
        )
        
        # Mock responses for 3 attempts (each has 1 analyze + 1 propose fix = 6 calls)
        mock_responses = []
        for i in range(3):
            m_analysis = MagicMock()
            m_analysis.message.content = '{"classification": "type_error", "explanation": "type mismatch"}'
            m_code = MagicMock()
            m_code.message.content = f"fixed_code_{i+1}"
            mock_responses.extend([m_analysis, m_code])
            
        llm_mock.chat.side_effect = mock_responses
        
        # Always fail the sandbox run
        sandbox_mock.return_value = "Error: TypeError: unsupported operand types"
        
        result = debug_agent.handle_error(error, "Divide values", task_id=2)
        
        assert result.status == "FAILED_MAX_RETRIES"
        assert len(result.attempts) == 3
        assert result.escalation_reason == "Failed to fix after 3 attempts"
    
    def test_timeout_error_handling(self, setup):
        """Test handling TimeoutError"""
        debug_agent, llm_mock, sandbox_mock = setup
        
        error = CodeExecutionError(
            error_type="TimeoutError",
            error_message="Exceeded 30 second limit",
            traceback="TimeoutExpired",
            code_executed="for i in range(1000000000):\n    df[df == i]",
            execution_time_ms=30000
        )
        
        mock_analysis = MagicMock()
        mock_analysis.message.content = '{"classification": "timeout", "fix_approach": "Add limits and optimize", "explanation": "Limit rows"}'
        mock_code = MagicMock()
        mock_code.message.content = "df.head(10000).mean()"
        
        llm_mock.chat.side_effect = [mock_analysis, mock_code]
        
        # sandbox succeeds
        sandbox_mock.return_value = "0.45"
        
        result = debug_agent.handle_error(error, "Process data", task_id=3)
        
        assert result.status == "FIXED"
        assert result.final_result == "0.45"
        assert result.final_code == "df.head(10000).mean()"
