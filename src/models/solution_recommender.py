"""
Solution Recommendation System for Regression Auto-Remediation

Recommends solutions for V93K regression issues based on:
- Historical successful fixes
- Issue similarity matching
- V93K domain knowledge
- Confidence scoring for automated application
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
from pathlib import Path

from .issue_classifier import IssueCategory, ClassificationResult

logger = logging.getLogger(__name__)


@dataclass
class Solution:
    """Represents a solution for a V93K regression issue."""
    
    solution_id: str
    solution_type: str  # 'code_fix', 'config_change', 'parameter_update', etc.
    description: str
    
    # Solution details
    code_changes: List[Dict[str, str]] = field(default_factory=list)
    config_changes: List[Dict[str, str]] = field(default_factory=list)
    parameter_changes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    category: Optional[IssueCategory] = None
    module_applicability: List[str] = field(default_factory=list)
    baseline_versions: List[str] = field(default_factory=list)
    
    # Success metrics
    success_count: int = 0
    failure_count: int = 0
    confidence_score: float = 0.0
    
    # Timestamps
    created_date: datetime = field(default_factory=datetime.now)
    last_applied: Optional[datetime] = None
    last_updated: datetime = field(default_factory=datetime.now)
    
    def get_success_rate(self) -> float:
        """Calculate success rate of this solution."""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0
    
    def update_success_metrics(self, success: bool) -> None:
        """Update success metrics after solution application."""
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        
        self.last_applied = datetime.now()
        self.last_updated = datetime.now()
        
        # Recalculate confidence score
        success_rate = self.get_success_rate()
        application_count = self.success_count + self.failure_count
        
        # Confidence based on success rate and number of applications
        confidence_from_success = success_rate
        confidence_from_volume = min(1.0, application_count / 10.0)  # More confidence with more data
        
        self.confidence_score = 0.7 * confidence_from_success + 0.3 * confidence_from_volume


@dataclass 
class RecommendationResult:
    """Result of solution recommendation."""
    
    solutions: List[Tuple[Solution, float]]  # (solution, similarity_score)
    issue_category: IssueCategory
    recommendation_confidence: float
    explanation: str
    
    # Context used for recommendation
    error_message: str
    module_name: Optional[str] = None
    baseline_version: Optional[str] = None
    
    # Recommendation metadata
    recommended_at: datetime = field(default_factory=datetime.now)
    total_solutions_considered: int = 0
    
    def get_top_solution(self) -> Optional[Tuple[Solution, float]]:
        """Get the highest-scored solution."""
        return self.solutions[0] if self.solutions else None
    
    def get_auto_applicable_solutions(self, min_confidence: float = 0.8) -> List[Tuple[Solution, float]]:
        """Get solutions with confidence high enough for automatic application."""
        return [
            (solution, score) for solution, score in self.solutions
            if solution.confidence_score >= min_confidence and score >= min_confidence
        ]


class SolutionRecommender:
    """
    Recommends solutions for V93K regression issues based on historical data.
    
    Uses similarity matching and machine learning to find the most appropriate
    solutions for new issues based on successful past resolutions.
    """
    
    def __init__(self, knowledge_base_path: Optional[str] = None):
        self.knowledge_base_path = knowledge_base_path
        self.solutions: Dict[str, Solution] = {}
        self.solution_history: List[Dict[str, Any]] = []
        
        # Text similarity components
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        self.issue_vectors = None
        self.is_fitted = False
        
        # Load existing knowledge base if available
        if knowledge_base_path and Path(knowledge_base_path).exists():
            self.load_knowledge_base(knowledge_base_path)
    
    def add_solution(self, solution: Solution) -> None:
        """Add a new solution to the knowledge base."""
        self.solutions[solution.solution_id] = solution
        logger.info(f"Added solution {solution.solution_id}: {solution.description}")
        
        # Mark for re-fitting
        self.is_fitted = False
    
    def record_solution_application(self, solution_id: str, error_message: str, 
                                  success: bool, context: Optional[Dict[str, Any]] = None) -> None:
        """Record the result of applying a solution."""
        if solution_id not in self.solutions:
            logger.warning(f"Unknown solution ID: {solution_id}")
            return
        
        # Update solution metrics
        solution = self.solutions[solution_id]
        solution.update_success_metrics(success)
        
        # Record in history
        history_entry = {
            'solution_id': solution_id,
            'error_message': error_message,
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'context': context or {}
        }
        self.solution_history.append(history_entry)
        
        logger.info(f"Recorded solution application: {solution_id}, success: {success}")
        
        # Mark for re-fitting to incorporate new data
        self.is_fitted = False
    
    def recommend_solutions(self, error_message: str, issue_category: IssueCategory,
                          context: Optional[Dict[str, Any]] = None,
                          max_recommendations: int = 5) -> RecommendationResult:
        """
        Recommend solutions for a given issue.
        
        Args:
            error_message: Error message to find solutions for
            issue_category: Classified category of the issue
            context: Additional context (module, baseline, etc.)
            max_recommendations: Maximum number of solutions to recommend
            
        Returns:
            RecommendationResult with ranked solutions
        """
        if not self.solutions:
            return RecommendationResult(
                solutions=[],
                issue_category=issue_category,
                recommendation_confidence=0.0,
                explanation="No solutions available in knowledge base",
                error_message=error_message,
                module_name=context.get('module_name') if context else None,
                baseline_version=context.get('baseline_version') if context else None,
                total_solutions_considered=0
            )
        
        # Fit vectorizer if needed
        if not self.is_fitted:
            self._fit_vectorizer()
        
        # Get candidate solutions based on category and context
        candidates = self._get_candidate_solutions(issue_category, context)
        
        if not candidates:
            return RecommendationResult(
                solutions=[],
                issue_category=issue_category,
                recommendation_confidence=0.1,
                explanation=f"No solutions found for category {issue_category.value}",
                error_message=error_message,
                module_name=context.get('module_name') if context else None,
                baseline_version=context.get('baseline_version') if context else None,
                total_solutions_considered=len(self.solutions)
            )
        
        # Calculate similarity scores
        scored_solutions = self._calculate_similarity_scores(error_message, candidates)
        
        # Apply additional scoring factors
        final_scores = self._apply_scoring_factors(scored_solutions, context)
        
        # Sort by final score and take top recommendations
        final_scores.sort(key=lambda x: x[1], reverse=True)
        top_solutions = final_scores[:max_recommendations]
        
        # Calculate overall recommendation confidence
        recommendation_confidence = self._calculate_recommendation_confidence(top_solutions)
        
        # Generate explanation
        explanation = self._generate_explanation(top_solutions, issue_category)
        
        return RecommendationResult(
            solutions=top_solutions,
            issue_category=issue_category,
            recommendation_confidence=recommendation_confidence,
            explanation=explanation,
            error_message=error_message,
            module_name=context.get('module_name') if context else None,
            baseline_version=context.get('baseline_version') if context else None,
            total_solutions_considered=len(candidates)
        )
    
    def _get_candidate_solutions(self, issue_category: IssueCategory, 
                               context: Optional[Dict[str, Any]] = None) -> List[Solution]:
        """Get candidate solutions based on category and context."""
        candidates = []
        
        for solution in self.solutions.values():
            # Check category match
            if solution.category and solution.category != issue_category:
                continue
            
            # Check module applicability
            if context and 'module_name' in context:
                module_name = context['module_name']
                if solution.module_applicability and module_name not in solution.module_applicability:
                    continue
            
            # Check baseline version compatibility
            if context and 'baseline_version' in context:
                baseline = context['baseline_version']
                if solution.baseline_versions and baseline not in solution.baseline_versions:
                    continue
            
            candidates.append(solution)
        
        return candidates
    
    def _fit_vectorizer(self) -> None:
        """Fit the text vectorizer with current solution data."""
        if not self.solutions:
            return
        
        # Collect text data from solutions and history
        texts = []
        
        # Add solution descriptions
        for solution in self.solutions.values():
            texts.append(solution.description)
        
        # Add historical error messages
        for entry in self.solution_history:
            texts.append(entry['error_message'])
        
        if texts:
            self.vectorizer.fit(texts)
            self.is_fitted = True
            logger.info(f"Fitted vectorizer with {len(texts)} text samples")
    
    def _calculate_similarity_scores(self, error_message: str, 
                                   candidates: List[Solution]) -> List[Tuple[Solution, float]]:
        """Calculate similarity scores between error message and candidate solutions."""
        if not self.is_fitted:
            return [(solution, 0.5) for solution in candidates]  # Default score
        
        # Vectorize the error message
        error_vector = self.vectorizer.transform([error_message])
        
        scored_solutions = []
        
        for solution in candidates:
            # Vectorize solution description
            solution_vector = self.vectorizer.transform([solution.description])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(error_vector, solution_vector)[0][0]
            
            # Boost similarity with historical success
            if solution.success_count > 0:
                historical_boost = min(0.2, solution.get_success_rate() * 0.2)
                similarity += historical_boost
            
            scored_solutions.append((solution, float(similarity)))
        
        return scored_solutions
    
    def _apply_scoring_factors(self, scored_solutions: List[Tuple[Solution, float]],
                             context: Optional[Dict[str, Any]] = None) -> List[Tuple[Solution, float]]:
        """Apply additional scoring factors to solution recommendations."""
        adjusted_scores = []
        
        for solution, base_score in scored_solutions:
            final_score = base_score
            
            # Factor in solution confidence
            final_score *= (0.5 + 0.5 * solution.confidence_score)
            
            # Boost recent successful applications
            if solution.last_applied and solution.success_count > 0:
                days_since_applied = (datetime.now() - solution.last_applied).days
                recency_boost = max(0, 0.1 * (30 - days_since_applied) / 30)  # Boost for recent applications
                final_score += recency_boost
            
            # Penalize solutions with poor success rates
            success_rate = solution.get_success_rate()
            if solution.success_count + solution.failure_count >= 3:  # Only penalize with enough data
                if success_rate < 0.5:
                    final_score *= 0.7  # Significant penalty for poor performance
                elif success_rate < 0.7:
                    final_score *= 0.9  # Minor penalty for mediocre performance
            
            adjusted_scores.append((solution, final_score))
        
        return adjusted_scores
    
    def _calculate_recommendation_confidence(self, top_solutions: List[Tuple[Solution, float]]) -> float:
        """Calculate overall confidence in the recommendations."""
        if not top_solutions:
            return 0.0
        
        # Base confidence on top solution score
        top_score = top_solutions[0][1]
        base_confidence = min(1.0, top_score)
        
        # Factor in the gap between top solutions (higher gap = more confidence)
        if len(top_solutions) > 1:
            score_gap = top_solutions[0][1] - top_solutions[1][1]
            gap_confidence = min(0.2, score_gap)
            base_confidence += gap_confidence
        
        # Factor in number of available solutions (more options = less confidence)
        availability_factor = max(0.8, 1.0 - len(top_solutions) * 0.05)
        
        return min(1.0, base_confidence * availability_factor)
    
    def _generate_explanation(self, top_solutions: List[Tuple[Solution, float]],
                            issue_category: IssueCategory) -> str:
        """Generate human-readable explanation for recommendations."""
        if not top_solutions:
            return f"No solutions found for {issue_category.value} issues"
        
        top_solution, top_score = top_solutions[0]
        
        explanation_parts = [
            f"Found {len(top_solutions)} potential solutions for {issue_category.value}.",
            f"Top recommendation: '{top_solution.description}' (score: {top_score:.2f})"
        ]
        
        if top_solution.success_count > 0:
            success_rate = top_solution.get_success_rate()
            explanation_parts.append(
                f"This solution has {success_rate:.1%} success rate "
                f"({top_solution.success_count} successes, {top_solution.failure_count} failures)"
            )
        
        return " ".join(explanation_parts)
    
    def save_knowledge_base(self, path: str) -> None:
        """Save the solution knowledge base to disk."""
        data = {
            'solutions': {},
            'solution_history': self.solution_history,
            'saved_at': datetime.now().isoformat()
        }
        
        # Convert solutions to serializable format
        for solution_id, solution in self.solutions.items():
            data['solutions'][solution_id] = {
                'solution_id': solution.solution_id,
                'solution_type': solution.solution_type,
                'description': solution.description,
                'code_changes': solution.code_changes,
                'config_changes': solution.config_changes,
                'parameter_changes': solution.parameter_changes,
                'category': solution.category.value if solution.category else None,
                'module_applicability': solution.module_applicability,
                'baseline_versions': solution.baseline_versions,
                'success_count': solution.success_count,
                'failure_count': solution.failure_count,
                'confidence_score': solution.confidence_score,
                'created_date': solution.created_date.isoformat(),
                'last_applied': solution.last_applied.isoformat() if solution.last_applied else None,
                'last_updated': solution.last_updated.isoformat()
            }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Knowledge base saved to {path}")
    
    def load_knowledge_base(self, path: str) -> None:
        """Load solution knowledge base from disk."""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            # Load solutions
            self.solutions = {}
            for solution_id, solution_data in data.get('solutions', {}).items():
                solution = Solution(
                    solution_id=solution_data['solution_id'],
                    solution_type=solution_data['solution_type'],
                    description=solution_data['description'],
                    code_changes=solution_data.get('code_changes', []),
                    config_changes=solution_data.get('config_changes', []),
                    parameter_changes=solution_data.get('parameter_changes', []),
                    category=IssueCategory(solution_data['category']) if solution_data.get('category') else None,
                    module_applicability=solution_data.get('module_applicability', []),
                    baseline_versions=solution_data.get('baseline_versions', []),
                    success_count=solution_data.get('success_count', 0),
                    failure_count=solution_data.get('failure_count', 0),
                    confidence_score=solution_data.get('confidence_score', 0.0),
                    created_date=datetime.fromisoformat(solution_data['created_date']),
                    last_applied=datetime.fromisoformat(solution_data['last_applied']) if solution_data.get('last_applied') else None,
                    last_updated=datetime.fromisoformat(solution_data['last_updated'])
                )
                self.solutions[solution_id] = solution
            
            # Load history
            self.solution_history = data.get('solution_history', [])
            
            # Mark for re-fitting
            self.is_fitted = False
            
            logger.info(f"Loaded knowledge base from {path}: {len(self.solutions)} solutions, {len(self.solution_history)} history entries")
            
        except Exception as e:
            logger.error(f"Failed to load knowledge base from {path}: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the solution knowledge base."""
        total_solutions = len(self.solutions)
        total_applications = sum(s.success_count + s.failure_count for s in self.solutions.values())
        successful_applications = sum(s.success_count for s in self.solutions.values())
        
        category_distribution = {}
        for solution in self.solutions.values():
            if solution.category:
                category = solution.category.value
                category_distribution[category] = category_distribution.get(category, 0) + 1
        
        return {
            'total_solutions': total_solutions,
            'total_applications': total_applications,
            'successful_applications': successful_applications,
            'overall_success_rate': successful_applications / total_applications if total_applications > 0 else 0,
            'category_distribution': category_distribution,
            'history_entries': len(self.solution_history),
            'is_fitted': self.is_fitted
        }
