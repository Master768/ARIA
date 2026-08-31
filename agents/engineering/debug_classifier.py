import re
import logging
from enum import Enum
from typing import Dict, Any, Tuple

logger = logging.getLogger("debug_classifier")

class ErrorCategory(str, Enum):
    SYNTAX_ERROR = "SYNTAX_ERROR"
    KEY_ERROR = "KEY_ERROR"
    TYPE_ERROR = "TYPE_ERROR"
    DEPENDENCY_ERROR = "DEPENDENCY_ERROR"
    DATASET_SCHEMA_ERROR = "DATASET_SCHEMA_ERROR"
    VISUALIZATION_ERROR = "VISUALIZATION_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    UNKNOWN = "UNKNOWN"

class ErrorClassifier:
    RETRY_POLICIES: Dict[ErrorCategory, int] = {
        ErrorCategory.SYNTAX_ERROR: 2,
        ErrorCategory.KEY_ERROR: 1,
        ErrorCategory.DEPENDENCY_ERROR: 1,
        ErrorCategory.TYPE_ERROR: 2,
        ErrorCategory.DATASET_SCHEMA_ERROR: 2,
        ErrorCategory.VISUALIZATION_ERROR: 2,
        ErrorCategory.TIMEOUT_ERROR: 0,
        ErrorCategory.RUNTIME_ERROR: 2,
        ErrorCategory.UNKNOWN: 1
    }

    @classmethod
    def classify(cls, traceback_text: str, error_message: str) -> Tuple[ErrorCategory, int]:
        combined = f"{error_message}\n{traceback_text}".lower()
        if "syntaxerror" in combined or "indentationerror" in combined:
            category = ErrorCategory.SYNTAX_ERROR
        elif "keyerror" in combined:
            category = ErrorCategory.KEY_ERROR
        elif "modulenotfounderror" in combined or "importerror" in combined:
            category = ErrorCategory.DEPENDENCY_ERROR
        elif "typeerror" in combined or "valueerror" in combined:
            category = ErrorCategory.TYPE_ERROR
        elif "emptydataerror" in combined or "file_not_found" in combined or "no columns" in combined:
            category = ErrorCategory.DATASET_SCHEMA_ERROR
        elif "matplotlib" in combined or "seaborn" in combined or "plot" in combined:
            category = ErrorCategory.VISUALIZATION_ERROR
        elif "timeoutexpired" in combined or "timeout" in combined:
            category = ErrorCategory.TIMEOUT_ERROR
        elif "nameerror" in combined or "attributeerror" in combined or "indexerror" in combined:
            category = ErrorCategory.RUNTIME_ERROR
        else:
            category = ErrorCategory.UNKNOWN

        max_retries = cls.RETRY_POLICIES.get(category, 1)
        return category, max_retries
