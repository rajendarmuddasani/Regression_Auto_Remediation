"""
Issue Classification Model for Regression Auto-Remediation System

Classifies V93K regression issues into categories for targeted resolution.
Uses machine learning to identify patterns in error messages and test failures.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import re
import logging
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
from pathlib import Path

logger = logging.getLogger(__name__)


class IssueCategory(Enum):
    """Categories of V93K regression issues."""
    
    # Compilation and Build Issues
    COMPILATION_ERROR = "compilation_error"
    SYNTAX_ERROR = "syntax_error"
    LINKING_ERROR = "linking_error"
    BUILD_FAILURE = "build_failure"
    
    # Test Execution Issues
    TIMEOUT = "timeout"
    RESOURCE_ERROR = "resource_error"
    RUNTIME_ERROR = "runtime_error"
    INITIALIZATION_ERROR = "initialization_error"
    
    # V93K Specific Issues
    CONTACT_FAILURE = "contact_failure"
    MEASUREMENT_ERROR = "measurement_error"
    CALIBRATION_ERROR = "calibration_error"
    DEVICE_ERROR = "device_error"
    
    # Configuration Issues
    CONFIG_ERROR = "config_error"
    PARAMETER_ERROR = "parameter_error"
    ENVIRONMENT_ERROR = "environment_error"
    
    # Data and File Issues
    FILE_ERROR = "file_error"
    DATA_CORRUPTION = "data_corruption"
    PERMISSION_ERROR = "permission_error"
    
    # Unknown/Other
    UNKNOWN = "unknown"
    OTHER = "other"


@dataclass
class ClassificationResult:
    """Result of issue classification."""
    
    category: IssueCategory
    confidence: float
    explanation: str
    features_used: List[str]
    alternative_categories: List[Tuple[IssueCategory, float]]


class IssueClassifier:
    """
    Machine learning classifier for V93K regression issues.
    
    Uses TF-IDF vectorization and ensemble methods to classify
    error messages and test failures into actionable categories.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 3),
            lowercase=True
        )
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            class_weight='balanced'
        )
        self.backup_classifier = MultinomialNB(alpha=1.0)
        
        # V93K-specific keyword patterns for rule-based classification
        self.keyword_patterns = self._build_keyword_patterns()
        
        # Model metadata
        self.is_trained = False
        self.training_date = None
        self.feature_names = []
        self.class_names = []
        
        # Load existing model if available
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
    
    def _build_keyword_patterns(self) -> Dict[IssueCategory, List[str]]:
        """Build keyword patterns for rule-based classification fallback."""
        return {
            IssueCategory.COMPILATION_ERROR: [
                'compilation error', 'compile error', 'compilation failed',
                'compiler error', 'build error', 'make error'
            ],
            IssueCategory.SYNTAX_ERROR: [
                'syntax error', 'parse error', 'unexpected token',
                'missing semicolon', 'undeclared identifier'
            ],
            IssueCategory.LINKING_ERROR: [
                'link error', 'linking failed', 'undefined reference',
                'cannot find symbol', 'linker error'
            ],
            IssueCategory.TIMEOUT: [
                'timeout', 'time out', 'timed out', 'execution timeout',
                'test timeout', 'connection timeout'
            ],
            IssueCategory.CONTACT_FAILURE: [
                'contact failure', 'contact error', 'pin contact',
                'contact resistance', 'open contact', 'short contact'
            ],
            IssueCategory.MEASUREMENT_ERROR: [
                'measurement error', 'measurement failed', 'invalid measurement',
                'measurement timeout', 'measurement overflow'
            ],
            IssueCategory.CALIBRATION_ERROR: [
                'calibration error', 'calibration failed', 'cal error',
                'calibration timeout', 'calibration drift'
            ],
            IssueCategory.DEVICE_ERROR: [
                'device error', 'device not found', 'device failure',
                'device timeout', 'device communication error'
            ],
            IssueCategory.RESOURCE_ERROR: [
                'resource error', 'out of memory', 'memory error',
                'disk space', 'resource not available'
            ],
            IssueCategory.FILE_ERROR: [
                'file not found', 'file error', 'cannot open file',
                'file permission', 'file corrupted'
            ],
            IssueCategory.PERMISSION_ERROR: [
                'permission denied', 'access denied', 'insufficient privileges',
                'permission error', 'authorization failed'
            ]
        }
    
    def classify_issue(self, error_message: str, context: Optional[Dict[str, Any]] = None) -> ClassificationResult:
        """
        Classify a single issue based on error message and context.
        
        Args:
            error_message: Error message text to classify
            context: Additional context (module name, baseline, etc.)
            
        Returns:
            ClassificationResult with category and confidence
        """
        if not error_message.strip():
            return ClassificationResult(
                category=IssueCategory.UNKNOWN,
                confidence=0.0,
                explanation="Empty error message",
                features_used=[],
                alternative_categories=[]
            )
        
        # Try ML classification if model is trained
        if self.is_trained:
            try:
                return self._ml_classify(error_message, context)
            except Exception as e:
                logger.warning(f"ML classification failed: {e}, falling back to rule-based")
        
        # Fallback to rule-based classification
        return self._rule_based_classify(error_message, context)
    
    def _ml_classify(self, error_message: str, context: Optional[Dict[str, Any]] = None) -> ClassificationResult:
        """Classify using trained ML model."""
        # Prepare text for classification
        text_features = self._prepare_text_features(error_message, context)
        
        # Vectorize the text
        text_vector = self.vectorizer.transform([text_features])
        
        # Get predictions from both classifiers
        rf_proba = self.classifier.predict_proba(text_vector)[0]
        nb_proba = self.backup_classifier.predict_proba(text_vector)[0]
        
        # Ensemble prediction (weighted average)
        ensemble_proba = 0.7 * rf_proba + 0.3 * nb_proba
        
        # Get top prediction
        top_idx = np.argmax(ensemble_proba)
        top_category = IssueCategory(self.class_names[top_idx])
        confidence = ensemble_proba[top_idx]
        
        # Get alternative categories
        sorted_indices = np.argsort(ensemble_proba)[::-1]
        alternatives = [
            (IssueCategory(self.class_names[idx]), ensemble_proba[idx])
            for idx in sorted_indices[1:4]  # Top 3 alternatives
        ]
        
        # Get feature importance for explanation
        feature_importance = self.classifier.feature_importances_
        text_features_importance = (text_vector.toarray()[0] * feature_importance).flatten()
        top_features_idx = np.argsort(text_features_importance)[::-1][:5]
        top_features = [self.feature_names[idx] for idx in top_features_idx if text_features_importance[idx] > 0]
        
        explanation = f"ML model classified with {confidence:.2%} confidence based on features: {', '.join(top_features[:3])}"
        
        return ClassificationResult(
            category=top_category,
            confidence=float(confidence),
            explanation=explanation,
            features_used=top_features,
            alternative_categories=alternatives
        )
    
    def _rule_based_classify(self, error_message: str, context: Optional[Dict[str, Any]] = None) -> ClassificationResult:
        """Classify using keyword patterns."""
        message_lower = error_message.lower()
        
        # Score each category based on keyword matches
        category_scores = {}
        matched_keywords = []
        
        for category, keywords in self.keyword_patterns.items():
            score = 0
            category_matches = []
            
            for keyword in keywords:
                if keyword in message_lower:
                    score += 1
                    category_matches.append(keyword)
            
            if score > 0:
                category_scores[category] = score
                matched_keywords.extend(category_matches)
        
        if not category_scores:
            return ClassificationResult(
                category=IssueCategory.UNKNOWN,
                confidence=0.1,
                explanation="No matching patterns found",
                features_used=[],
                alternative_categories=[]
            )
        
        # Get top category
        top_category = max(category_scores.keys(), key=lambda k: category_scores[k])
        max_score = category_scores[top_category]
        
        # Calculate confidence based on match strength
        confidence = min(0.8, max_score / 3.0)  # Cap at 80% for rule-based
        
        # Get alternatives
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        alternatives = [
            (cat, min(0.8, score / 3.0))
            for cat, score in sorted_categories[1:4]
        ]
        
        explanation = f"Rule-based classification found {max_score} keyword matches: {', '.join(matched_keywords[:3])}"
        
        return ClassificationResult(
            category=top_category,
            confidence=confidence,
            explanation=explanation,
            features_used=matched_keywords[:5],
            alternative_categories=alternatives
        )
    
    def _prepare_text_features(self, error_message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Prepare text features for ML classification."""
        features = [error_message]
        
        if context:
            # Add context information as features
            if 'module_name' in context:
                features.append(f"module_{context['module_name']}")
            if 'baseline_version' in context:
                features.append(f"baseline_{context['baseline_version']}")
            if 'file_type' in context:
                features.append(f"filetype_{context['file_type']}")
        
        return " ".join(features)
    
    def train_model(self, training_data: List[Tuple[str, IssueCategory]], 
                   validation_split: float = 0.2) -> Dict[str, Any]:
        """
        Train the classification model with labeled data.
        
        Args:
            training_data: List of (error_message, category) tuples
            validation_split: Fraction of data to use for validation
            
        Returns:
            Training results and metrics
        """
        if len(training_data) < 10:
            raise ValueError("Need at least 10 training examples")
        
        logger.info(f"Training issue classifier with {len(training_data)} examples")
        
        # Prepare training data
        messages = [msg for msg, _ in training_data]
        labels = [cat.value for _, cat in training_data]
        
        # Split data - handle stratification carefully
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                messages, labels, test_size=validation_split, random_state=42, stratify=labels
            )
        except ValueError as e:
            # If stratification fails due to small class sizes, use random split
            logger.warning(f"Stratification failed: {e}. Using random split instead.")
            X_train, X_test, y_train, y_test = train_test_split(
                messages, labels, test_size=validation_split, random_state=42
            )
        
        # Vectorize text
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        # Train both classifiers
        self.classifier.fit(X_train_vec, y_train)
        self.backup_classifier.fit(X_train_vec, y_train)
        
        # Store model metadata
        self.is_trained = True
        self.training_date = datetime.now()
        self.feature_names = self.vectorizer.get_feature_names_out().tolist()
        self.class_names = list(set(labels))
        
        # Evaluate model
        y_pred_rf = self.classifier.predict(X_test_vec)
        y_pred_nb = self.backup_classifier.predict(X_test_vec)
        
        rf_accuracy = accuracy_score(y_test, y_pred_rf)
        nb_accuracy = accuracy_score(y_test, y_pred_nb)
        
        # Generate ensemble predictions
        rf_proba = self.classifier.predict_proba(X_test_vec)
        nb_proba = self.backup_classifier.predict_proba(X_test_vec)
        ensemble_proba = 0.7 * rf_proba + 0.3 * nb_proba
        y_pred_ensemble = [self.class_names[np.argmax(proba)] for proba in ensemble_proba]
        ensemble_accuracy = accuracy_score(y_test, y_pred_ensemble)
        
        results = {
            'training_examples': len(training_data),
            'validation_examples': len(X_test),
            'rf_accuracy': rf_accuracy,
            'nb_accuracy': nb_accuracy,
            'ensemble_accuracy': ensemble_accuracy,
            'feature_count': len(self.feature_names),
            'class_count': len(self.class_names),
            'training_date': self.training_date.isoformat(),
            'classification_report': classification_report(y_test, y_pred_ensemble, output_dict=True)
        }
        
        logger.info(f"Model training completed. Ensemble accuracy: {ensemble_accuracy:.3f}")
        
        return results
    
    def save_model(self, path: str) -> None:
        """Save the trained model to disk."""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        model_data = {
            'vectorizer': self.vectorizer,
            'classifier': self.classifier,
            'backup_classifier': self.backup_classifier,
            'feature_names': self.feature_names,
            'class_names': self.class_names,
            'training_date': self.training_date,
            'keyword_patterns': self.keyword_patterns
        }
        
        joblib.dump(model_data, path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str) -> None:
        """Load a trained model from disk."""
        try:
            model_data = joblib.load(path)
            
            self.vectorizer = model_data['vectorizer']
            self.classifier = model_data['classifier']
            self.backup_classifier = model_data['backup_classifier']
            self.feature_names = model_data['feature_names']
            self.class_names = model_data['class_names']
            self.training_date = model_data['training_date']
            self.keyword_patterns = model_data.get('keyword_patterns', self.keyword_patterns)
            
            self.is_trained = True
            logger.info(f"Model loaded from {path}")
            
        except Exception as e:
            logger.error(f"Failed to load model from {path}: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            'is_trained': self.is_trained,
            'training_date': self.training_date.isoformat() if self.training_date else None,
            'feature_count': len(self.feature_names),
            'class_count': len(self.class_names),
            'classes': self.class_names,
            'model_path': self.model_path
        }


def create_synthetic_training_data() -> List[Tuple[str, IssueCategory]]:
    """
    Create synthetic training data for initial model training.
    
    Returns:
        List of (error_message, category) tuples for training
    """
    return [
        # Compilation errors (5 examples)
        ("Compilation error: undefined symbol 'test_function'", IssueCategory.COMPILATION_ERROR),
        ("Build failed: compiler error in module.cpp", IssueCategory.COMPILATION_ERROR),
        ("Error: compilation terminated due to errors", IssueCategory.COMPILATION_ERROR),
        ("Make error: build target failed", IssueCategory.BUILD_FAILURE),
        ("Compiler cannot find header file", IssueCategory.COMPILATION_ERROR),
        
        # Syntax errors (3 examples)
        ("Syntax error: expected ';' before token", IssueCategory.SYNTAX_ERROR),
        ("Parse error: unexpected end of file", IssueCategory.SYNTAX_ERROR),
        ("Error: missing closing brace in function", IssueCategory.SYNTAX_ERROR),
        
        # Linking errors (3 examples)
        ("Linker error: undefined reference to main", IssueCategory.LINKING_ERROR),
        ("Link failed: cannot find library", IssueCategory.LINKING_ERROR),
        ("Undefined reference to external function", IssueCategory.LINKING_ERROR),
        
        # Timeout errors (4 examples)
        ("Test execution timeout after 300 seconds", IssueCategory.TIMEOUT),
        ("Connection timeout while accessing device", IssueCategory.TIMEOUT),
        ("Timeout error: test did not complete", IssueCategory.TIMEOUT),
        ("Operation timed out waiting for response", IssueCategory.TIMEOUT),
        
        # Contact failures (5 examples)
        ("Contact failure detected on pin 5", IssueCategory.CONTACT_FAILURE),
        ("Pin contact resistance out of specification", IssueCategory.CONTACT_FAILURE),
        ("Open contact detected during test", IssueCategory.CONTACT_FAILURE),
        ("Short circuit on contact pin 12", IssueCategory.CONTACT_FAILURE),
        ("Contact force insufficient on probe", IssueCategory.CONTACT_FAILURE),
        
        # Measurement errors (4 examples)
        ("Measurement error: value out of range", IssueCategory.MEASUREMENT_ERROR),
        ("Invalid measurement result from ADC", IssueCategory.MEASUREMENT_ERROR),
        ("Measurement timeout during voltage test", IssueCategory.MEASUREMENT_ERROR),
        ("Measurement overflow in current test", IssueCategory.MEASUREMENT_ERROR),
        
        # Device errors (4 examples)
        ("Device not responding to commands", IssueCategory.DEVICE_ERROR),
        ("Device communication error", IssueCategory.DEVICE_ERROR),
        ("Device initialization failed", IssueCategory.DEVICE_ERROR),
        ("Device hardware malfunction detected", IssueCategory.DEVICE_ERROR),
        
        # Resource errors (4 examples)
        ("Out of memory during test execution", IssueCategory.RESOURCE_ERROR),
        ("Disk space insufficient for log files", IssueCategory.RESOURCE_ERROR),
        ("Resource allocation failed", IssueCategory.RESOURCE_ERROR),
        ("CPU usage exceeded limits", IssueCategory.RESOURCE_ERROR),
        
        # File errors (4 examples)
        ("File not found: test_data.dat", IssueCategory.FILE_ERROR),
        ("Cannot open configuration file", IssueCategory.FILE_ERROR),
        ("File corrupted during transfer", IssueCategory.FILE_ERROR),
        ("Invalid file format detected", IssueCategory.FILE_ERROR),
        
        # Permission errors (3 examples)
        ("File permission denied", IssueCategory.PERMISSION_ERROR),
        ("Access denied to device", IssueCategory.PERMISSION_ERROR),
        ("Insufficient privileges for operation", IssueCategory.PERMISSION_ERROR),
        
        # Configuration errors (3 examples)
        ("Invalid parameter value in config", IssueCategory.PARAMETER_ERROR),
        ("Configuration file corrupted", IssueCategory.CONFIG_ERROR),
        ("Environment variable not set", IssueCategory.ENVIRONMENT_ERROR),
        
        # Runtime errors (3 examples)
        ("Runtime error: null pointer exception", IssueCategory.RUNTIME_ERROR),
        ("Runtime exception during test", IssueCategory.RUNTIME_ERROR),
        ("Segmentation fault in test code", IssueCategory.RUNTIME_ERROR),
        
        # Calibration errors (3 examples)
        ("Calibration drift detected", IssueCategory.CALIBRATION_ERROR),
        ("Calibration failed for instrument", IssueCategory.CALIBRATION_ERROR),
        ("Calibration timeout occurred", IssueCategory.CALIBRATION_ERROR),
    ]
