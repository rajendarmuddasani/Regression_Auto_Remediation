"""
Issue Classification API Endpoints

Handles ML-based issue classification and analysis.
"""

from fastapi import APIRouter, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional, Union
import sys
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models.issue_classifier import IssueClassifier
from core.database import DatabaseManager

logger = logging.getLogger(__name__)
router = APIRouter()

async def get_classifier() -> IssueClassifier:
    """Dependency to get classifier instance."""
    from api.main import issue_classifier
    if issue_classifier is None:
        raise HTTPException(status_code=503, detail="Classifier not initialized")
    return issue_classifier

async def get_db() -> DatabaseManager:
    """Dependency to get database instance."""
    from api.main import db_manager
    if db_manager is None:
        raise HTTPException(status_code=503, detail="Database not initialized")
    return db_manager

@router.post("/classify",
            summary="Classify issue from text",
            description="Classify an issue based on text description")
async def classify_issue(
    text: str = Form(..., description="Issue description text"),
    include_confidence: bool = Form(True, description="Include confidence scores"),
    top_n: int = Form(3, description="Number of top predictions to return"),
    classifier: IssueClassifier = Depends(get_classifier)
) -> Dict[str, Any]:
    """
    Classify an issue from text description.
    
    Returns the predicted issue category with confidence scores.
    """
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    if top_n < 1 or top_n > 10:
        raise HTTPException(status_code=400, detail="top_n must be between 1 and 10")
    
    try:
        # Get prediction
        prediction = classifier.predict(text)
        
        if include_confidence:
            # Get top N predictions with confidence
            predictions = classifier.predict_proba(text, top_n=top_n)
            
            return {
                "text": text,
                "primary_prediction": prediction,
                "predictions": [
                    {
                        "category": pred["category"],
                        "confidence": round(pred["confidence"], 4),
                        "probability": round(pred["confidence"], 4)
                    }
                    for pred in predictions
                ],
                "model_info": {
                    "model_type": "ensemble",
                    "algorithms": ["RandomForest", "MultinomialNB"],
                    "feature_extraction": "TF-IDF",
                    "vocab_size": len(classifier.vectorizer.vocabulary_) if hasattr(classifier.vectorizer, 'vocabulary_') else None
                }
            }
        else:
            return {
                "text": text,
                "prediction": prediction,
                "confidence": "available_on_request"
            }
            
    except Exception as e:
        logger.error(f"Classification error: {e}")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

@router.post("/classify-batch",
            summary="Classify multiple issues",
            description="Classify multiple issue descriptions in batch")
async def classify_batch(
    texts: List[str] = Form(..., description="List of issue description texts"),
    include_confidence: bool = Form(True, description="Include confidence scores"),
    top_n: int = Form(1, description="Number of top predictions per text"),
    classifier: IssueClassifier = Depends(get_classifier)
) -> Dict[str, Any]:
    """
    Classify multiple issues in batch.
    
    More efficient than individual classifications for multiple texts.
    """
    if not texts or len(texts) == 0:
        raise HTTPException(status_code=400, detail="No texts provided")
    
    if len(texts) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 texts per batch")
    
    if any(not text.strip() for text in texts):
        raise HTTPException(status_code=400, detail="All texts must be non-empty")
    
    try:
        results = []
        
        for i, text in enumerate(texts):
            try:
                prediction = classifier.predict(text)
                
                result = {
                    "index": i,
                    "text": text,
                    "prediction": prediction
                }
                
                if include_confidence:
                    predictions = classifier.predict_proba(text, top_n=top_n)
                    result["confidence_scores"] = [
                        {
                            "category": pred["category"],
                            "confidence": round(pred["confidence"], 4)
                        }
                        for pred in predictions
                    ]
                
                results.append(result)
                
            except Exception as e:
                results.append({
                    "index": i,
                    "text": text,
                    "error": str(e),
                    "prediction": None
                })
                logger.warning(f"Failed to classify text {i}: {e}")
        
        successful = sum(1 for r in results if "error" not in r)
        failed = len(results) - successful
        
        return {
            "total_texts": len(texts),
            "successful_classifications": successful,
            "failed_classifications": failed,
            "results": results,
            "summary": {
                "categories_found": list(set(
                    r["prediction"] for r in results 
                    if "error" not in r and r["prediction"]
                )),
                "avg_confidence": None if not include_confidence else round(
                    sum(
                        r["confidence_scores"][0]["confidence"] 
                        for r in results 
                        if "error" not in r and "confidence_scores" in r
                    ) / successful, 4
                ) if successful > 0 else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Batch classification error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch classification failed: {str(e)}")

@router.post("/classify-from-file",
            summary="Classify issues from parsed file data",
            description="Classify issues extracted from parsed V93K files")
async def classify_from_file_data(
    file_data: Dict[str, Any],
    extract_errors: bool = Form(True, description="Extract and classify error messages"),
    extract_warnings: bool = Form(False, description="Extract and classify warning messages"),
    include_metadata: bool = Form(True, description="Include file metadata in results"),
    classifier: IssueClassifier = Depends(get_classifier)
) -> Dict[str, Any]:
    """
    Classify issues from parsed V93K file data.
    
    Extracts relevant text from file parsing results and classifies issues.
    """
    try:
        texts_to_classify = []
        text_sources = []
        
        # Extract error messages
        if extract_errors and "errors" in file_data:
            for error in file_data["errors"]:
                if isinstance(error, dict) and "message" in error:
                    texts_to_classify.append(error["message"])
                    text_sources.append({
                        "type": "error",
                        "line_number": error.get("line_number"),
                        "severity": error.get("severity"),
                        "timestamp": error.get("timestamp")
                    })
                elif isinstance(error, str):
                    texts_to_classify.append(error)
                    text_sources.append({"type": "error"})
        
        # Extract warning messages
        if extract_warnings and "warnings" in file_data:
            for warning in file_data["warnings"]:
                if isinstance(warning, dict) and "message" in warning:
                    texts_to_classify.append(warning["message"])
                    text_sources.append({
                        "type": "warning",
                        "line_number": warning.get("line_number"),
                        "severity": warning.get("severity"),
                        "timestamp": warning.get("timestamp")
                    })
                elif isinstance(warning, str):
                    texts_to_classify.append(warning)
                    text_sources.append({"type": "warning"})
        
        if not texts_to_classify:
            return {
                "file_info": file_data.get("filename", "unknown") if include_metadata else None,
                "total_issues": 0,
                "classifications": [],
                "message": "No issues found to classify"
            }
        
        # Classify all extracted texts
        classifications = []
        
        for i, text in enumerate(texts_to_classify):
            try:
                prediction = classifier.predict(text)
                predictions = classifier.predict_proba(text, top_n=3)
                
                classification = {
                    "text": text,
                    "prediction": prediction,
                    "confidence": round(predictions[0]["confidence"], 4),
                    "source": text_sources[i],
                    "alternatives": [
                        {
                            "category": pred["category"],
                            "confidence": round(pred["confidence"], 4)
                        }
                        for pred in predictions[1:]
                    ]
                }
                
                classifications.append(classification)
                
            except Exception as e:
                classifications.append({
                    "text": text,
                    "error": str(e),
                    "source": text_sources[i]
                })
                logger.warning(f"Failed to classify extracted text: {e}")
        
        # Generate summary
        successful_classifications = [c for c in classifications if "error" not in c]
        category_counts = {}
        for c in successful_classifications:
            category = c["prediction"]
            category_counts[category] = category_counts.get(category, 0) + 1
        
        result = {
            "total_issues": len(texts_to_classify),
            "successful_classifications": len(successful_classifications),
            "failed_classifications": len(classifications) - len(successful_classifications),
            "classifications": classifications,
            "summary": {
                "category_distribution": category_counts,
                "most_common_category": max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else None,
                "avg_confidence": round(
                    sum(c["confidence"] for c in successful_classifications) / len(successful_classifications), 4
                ) if successful_classifications else 0,
                "issue_types_extracted": {
                    "errors": sum(1 for s in text_sources if s["type"] == "error"),
                    "warnings": sum(1 for s in text_sources if s["type"] == "warning")
                }
            }
        }
        
        # Include file metadata if requested
        if include_metadata:
            result["file_info"] = {
                "filename": file_data.get("filename"),
                "file_type": file_data.get("file_type"),
                "module_name": file_data.get("module_name"),
                "baseline_version": file_data.get("baseline_version"),
                "error_count": file_data.get("error_count", 0),
                "warning_count": file_data.get("warning_count", 0),
                "parsing_successful": file_data.get("parsing_successful")
            }
        
        return result
        
    except Exception as e:
        logger.error(f"File data classification error: {e}")
        raise HTTPException(status_code=500, detail=f"Classification from file data failed: {str(e)}")

@router.get("/categories",
           summary="Get available issue categories",
           description="List all available issue categories and their descriptions")
async def get_categories(
    classifier: IssueClassifier = Depends(get_classifier)
) -> Dict[str, Any]:
    """Get information about available issue categories."""
    
    categories = [
        {"name": "compilation_error", "description": "Issues related to code compilation failures"},
        {"name": "runtime_error", "description": "Runtime execution errors and exceptions"},
        {"name": "timeout", "description": "Test execution timeouts and performance issues"},
        {"name": "memory_error", "description": "Memory allocation and usage problems"},
        {"name": "configuration_error", "description": "Configuration and setup issues"},
        {"name": "hardware_error", "description": "Hardware-related test failures"},
        {"name": "software_error", "description": "Software environment and dependency issues"},
        {"name": "network_error", "description": "Network connectivity and communication issues"},
        {"name": "data_error", "description": "Data validation and format issues"},
        {"name": "permission_error", "description": "File and system permission problems"},
        {"name": "resource_error", "description": "System resource availability issues"},
        {"name": "version_mismatch", "description": "Version compatibility and mismatch issues"},
        {"name": "test_setup_error", "description": "Test environment and setup problems"},
        {"name": "assertion_failure", "description": "Test assertion and validation failures"},
        {"name": "integration_error", "description": "System integration and interface issues"},
        {"name": "other", "description": "Uncategorized or unknown issues"}
    ]
    
    return {
        "total_categories": len(categories),
        "categories": categories,
        "model_info": {
            "is_trained": hasattr(classifier, 'model') and classifier.model is not None,
            "feature_extraction": "TF-IDF vectorization",
            "algorithm": "Ensemble (Random Forest + Multinomial Naive Bayes)",
            "supports_probability": True,
            "supports_batch": True
        }
    }

@router.get("/model-stats",
           summary="Get model statistics",
           description="Get detailed statistics about the classification model")
async def get_model_stats(
    classifier: IssueClassifier = Depends(get_classifier)
) -> Dict[str, Any]:
    """Get detailed model statistics and performance metrics."""
    
    try:
        stats = {
            "model_type": "ensemble",
            "algorithms": ["RandomForest", "MultinomialNB"],
            "is_trained": hasattr(classifier, 'model') and classifier.model is not None,
            "feature_extraction": {
                "method": "TF-IDF",
                "vocabulary_size": None,
                "max_features": None,
                "ngram_range": "(1, 2)"
            }
        }
        
        # Add vectorizer info if available
        if hasattr(classifier, 'vectorizer') and classifier.vectorizer:
            if hasattr(classifier.vectorizer, 'vocabulary_'):
                stats["feature_extraction"]["vocabulary_size"] = len(classifier.vectorizer.vocabulary_)
            if hasattr(classifier.vectorizer, 'max_features'):
                stats["feature_extraction"]["max_features"] = classifier.vectorizer.max_features
        
        # Add model info if trained
        if hasattr(classifier, 'model') and classifier.model is not None:
            stats["training_status"] = "trained"
            stats["supports_prediction"] = True
            stats["supports_probability"] = True
        else:
            stats["training_status"] = "not_trained"
            stats["supports_prediction"] = False
            stats["supports_probability"] = False
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting model stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model stats: {str(e)}")
