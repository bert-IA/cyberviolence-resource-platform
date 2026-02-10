"""
Module core pour l'architecture de validation dual
Gestion des imports et singletons
"""

from .workflow_manager import get_workflow_manager, ResourceWorkflowManager
from .llm_manager import get_llm_manager, LLMProvider, LLMManager
from .dual_validation import get_validation_system, DualValidationSystem, ValidationAction, ValidationStage

__all__ = [
    "get_workflow_manager",
    "ResourceWorkflowManager", 
    "get_llm_manager",
    "LLMProvider",
    "LLMManager",
    "get_validation_system",
    "DualValidationSystem",
    "ValidationAction",
    "ValidationStage"
]