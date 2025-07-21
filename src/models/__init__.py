"""
Machine Learning Models Module for Regression Auto-Remediation System

This module contains ML models for:
- Issue classification and categorization
- Solution recommendation based on historical data
- V93K domain-specific pattern recognition
- Automated learning from successful fixes
"""

# Import only the core models that are fully implemented
from .issue_classifier import IssueClassifier, IssueCategory
from .solution_recommender import SolutionRecommender, RecommendationResult

__all__ = [
    'IssueClassifier',
    'IssueCategory', 
    'SolutionRecommender',
    'RecommendationResult'
]
