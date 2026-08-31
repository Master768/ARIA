from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseSkill(ABC):
    """
    Abstract Base Class for all IDE-like Plugin Skills.
    Skills define specific analytical or computational capabilities that Host Agents dynamically load.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier name for the skill (e.g. 'statistics', 'machine_learning')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human and LLM readable summary of skill capabilities."""
        pass

    @property
    @abstractmethod
    def category(self) -> str:
        """Category tag (e.g. 'data_science', 'analytics', 'database', 'optimization')."""
        pass

    @property
    def required_libraries(self) -> List[str]:
        """Optional list of third-party python packages required by this skill."""
        return []

    @abstractmethod
    def can_handle(self, query: str, dataset_meta: Optional[Dict[str, Any]] = None) -> float:
        """
        Evaluate how suitable this skill is for a given task intent.
        Returns a confidence score between 0.0 (unsuitable) and 1.0 (perfect match).
        """
        pass

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute skill logic or return specialized execution prompt / python code template.
        Context contains: 'query', 'df', 'dataset_path', 'target_col', 'problem_type', etc.
        """
        pass
