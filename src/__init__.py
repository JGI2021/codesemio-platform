"""
CodeSemio Platform - Knowledge Acquisition System
Multi-Application, Multi-Model, Multi-Embedding
"""

__version__ = "1.0.0"
__author__ = "Javier Gimeno"

from .platform import CodeSemioPlatform
from .dspy_modules import CodeSemioRAG
from .models import LLMModel, Application

__all__ = [
    "CodeSemioPlatform",
    "CodeSemioRAG", 
    "LLMModel",
    "Application"
]