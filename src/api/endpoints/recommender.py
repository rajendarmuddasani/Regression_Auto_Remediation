"""
Solution Recommendation API Endpoints

Handles ML-based solution recommendations and knowledge base queries.
"""

from fastapi import APIRouter, HTTPException, Depends, Form, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models.solution_recommender import SolutionRecommender
from core.database import DatabaseManager

logger = logging.getLogger(__name__)
router = APIRouter()

async def get_recommender() -> SolutionRecommender:
    """Dependency to get recommender instance."""
    from api.main import solution_recommender
    if solution_recommender is None:
        raise HTTPException(status_code=503, detail="Recommender not initialized")
    return solution_recommender

async def get_db() -> DatabaseManager:
    """Dependency to get database instance."""
    from api.main import db_manager
    if db_manager is None:
        raise HTTPException(status_code=503, detail="Database not initialized")
    return db_manager

@router.post("/recommend",
            summary="Get solution recommendations",
            description="Get solution recommendations for an issue description")
async def get_recommendations(
    issue_text: str = Form(..., description="Issue description text"),
    top_k: int = Form(5, description="Number of recommendations to return"),
    min_similarity: float = Form(0.1, description="Minimum similarity threshold"),
    include_details: bool = Form(True, description="Include detailed solution information"),
    recommender: SolutionRecommender = Depends(get_recommender)
) -> Dict[str, Any]:
    """
    Get solution recommendations for an issue.
    
    Returns ranked solutions based on similarity to the issue description.
    """
    if not issue_text.strip():
        raise HTTPException(status_code=400, detail="Issue text cannot be empty")
    
    if top_k < 1 or top_k > 50:
        raise HTTPException(status_code=400, detail="top_k must be between 1 and 50")
    
    if min_similarity < 0 or min_similarity > 1:
        raise HTTPException(status_code=400, detail="min_similarity must be between 0 and 1")
    
    try:
        # Get recommendations
        recommendations = recommender.recommend_solution(
            issue_text, 
            top_k=top_k, 
            min_similarity=min_similarity
        )
        
        if not recommendations:
            return {
                "issue_text": issue_text,
                "total_recommendations": 0,
                "recommendations": [],
                "message": f"No solutions found with similarity >= {min_similarity}",
                "suggestion": "Try lowering min_similarity or expanding the issue description"
            }
        
        # Format recommendations
        formatted_recommendations = []
        
        for i, rec in enumerate(recommendations):
            formatted_rec = {
                "rank": i + 1,
                "similarity_score": round(rec["similarity"], 4),
                "solution_id": rec.get("solution_id"),
                "title": rec.get("title", "Solution"),
                "category": rec.get("category"),
                "solution_text": rec["solution"]
            }
            
            if include_details:
                formatted_rec.update({
                    "metadata": {
                        "issue_type": rec.get("issue_type"),
                        "complexity": rec.get("complexity", "medium"),
                        "estimated_time": rec.get("estimated_time"),
                        "success_rate": rec.get("success_rate"),
                        "last_updated": rec.get("last_updated"),
                        "source": rec.get("source", "knowledge_base")
                    },
                    "implementation_steps": rec.get("steps", []),
                    "prerequisites": rec.get("prerequisites", []),
                    "potential_issues": rec.get("potential_issues", []),
                    "verification_steps": rec.get("verification", [])
                })
            
            formatted_recommendations.append(formatted_rec)
        
        return {
            "issue_text": issue_text,
            "total_recommendations": len(recommendations),
            "recommendations": formatted_recommendations,
            "query_info": {
                "top_k_requested": top_k,
                "min_similarity": min_similarity,
                "best_similarity": round(recommendations[0]["similarity"], 4) if recommendations else 0,
                "avg_similarity": round(
                    sum(r["similarity"] for r in recommendations) / len(recommendations), 4
                ) if recommendations else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")

@router.post("/recommend-for-category",
            summary="Get recommendations for specific category",
            description="Get solution recommendations filtered by issue category")
async def get_recommendations_by_category(
    issue_text: str = Form(..., description="Issue description text"),
    category: str = Form(..., description="Issue category to filter by"),
    top_k: int = Form(5, description="Number of recommendations to return"),
    min_similarity: float = Form(0.1, description="Minimum similarity threshold"),
    recommender: SolutionRecommender = Depends(get_recommender)
) -> Dict[str, Any]:
    """
    Get solution recommendations filtered by category.
    
    More targeted recommendations for specific types of issues.
    """
    if not issue_text.strip():
        raise HTTPException(status_code=400, detail="Issue text cannot be empty")
    
    if not category.strip():
        raise HTTPException(status_code=400, detail="Category cannot be empty")
    
    try:
        # Get all recommendations first
        all_recommendations = recommender.recommend_solution(
            issue_text, 
            top_k=top_k * 3,  # Get more to filter by category
            min_similarity=min_similarity
        )
        
        # Filter by category
        category_recommendations = [
            rec for rec in all_recommendations 
            if rec.get("category", "").lower() == category.lower() or
               rec.get("issue_type", "").lower() == category.lower()
        ]
        
        # Take top_k from filtered results
        category_recommendations = category_recommendations[:top_k]
        
        if not category_recommendations:
            return {
                "issue_text": issue_text,
                "category": category,
                "total_recommendations": 0,
                "recommendations": [],
                "message": f"No solutions found for category '{category}' with similarity >= {min_similarity}",
                "available_categories": list(set(
                    rec.get("category", "unknown") for rec in all_recommendations
                ))
            }
        
        # Format recommendations
        formatted_recommendations = []
        for i, rec in enumerate(category_recommendations):
            formatted_recommendations.append({
                "rank": i + 1,
                "similarity_score": round(rec["similarity"], 4),
                "solution_id": rec.get("solution_id"),
                "title": rec.get("title", "Solution"),
                "category": rec.get("category"),
                "solution_text": rec["solution"],
                "metadata": {
                    "issue_type": rec.get("issue_type"),
                    "complexity": rec.get("complexity", "medium"),
                    "estimated_time": rec.get("estimated_time"),
                    "success_rate": rec.get("success_rate")
                }
            })
        
        return {
            "issue_text": issue_text,
            "category": category,
            "total_recommendations": len(category_recommendations),
            "recommendations": formatted_recommendations,
            "filter_info": {
                "total_before_filter": len(all_recommendations),
                "total_after_filter": len(category_recommendations),
                "best_similarity": round(category_recommendations[0]["similarity"], 4),
                "category_match_rate": round(
                    len(category_recommendations) / max(len(all_recommendations), 1), 4
                )
            }
        }
        
    except Exception as e:
        logger.error(f"Category recommendation error: {e}")
        raise HTTPException(status_code=500, detail=f"Category recommendation failed: {str(e)}")

@router.post("/batch-recommend",
            summary="Get recommendations for multiple issues",
            description="Get solution recommendations for multiple issues in batch")
async def batch_recommendations(
    issues: List[str] = Form(..., description="List of issue description texts"),
    top_k: int = Form(3, description="Number of recommendations per issue"),
    min_similarity: float = Form(0.1, description="Minimum similarity threshold"),
    recommender: SolutionRecommender = Depends(get_recommender)
) -> Dict[str, Any]:
    """
    Get recommendations for multiple issues in batch.
    
    More efficient than individual recommendation calls.
    """
    if not issues:
        raise HTTPException(status_code=400, detail="No issues provided")
    
    if len(issues) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 issues per batch")
    
    if any(not issue.strip() for issue in issues):
        raise HTTPException(status_code=400, detail="All issue texts must be non-empty")
    
    try:
        batch_results = []
        
        for i, issue_text in enumerate(issues):
            try:
                recommendations = recommender.recommend_solution(
                    issue_text,
                    top_k=top_k,
                    min_similarity=min_similarity
                )
                
                batch_results.append({
                    "index": i,
                    "issue_text": issue_text,
                    "recommendation_count": len(recommendations),
                    "recommendations": [
                        {
                            "rank": j + 1,
                            "similarity_score": round(rec["similarity"], 4),
                            "solution_text": rec["solution"],
                            "category": rec.get("category")
                        }
                        for j, rec in enumerate(recommendations)
                    ],
                    "best_similarity": round(recommendations[0]["similarity"], 4) if recommendations else 0
                })
                
            except Exception as e:
                batch_results.append({
                    "index": i,
                    "issue_text": issue_text,
                    "error": str(e),
                    "recommendations": []
                })
                logger.warning(f"Failed to get recommendations for issue {i}: {e}")
        
        successful = sum(1 for r in batch_results if "error" not in r)
        total_recommendations = sum(r["recommendation_count"] for r in batch_results if "error" not in r)
        
        return {
            "total_issues": len(issues),
            "successful_recommendations": successful,
            "failed_recommendations": len(issues) - successful,
            "total_solutions_found": total_recommendations,
            "results": batch_results,
            "summary": {
                "avg_recommendations_per_issue": round(
                    total_recommendations / successful, 2
                ) if successful > 0 else 0,
                "issues_with_solutions": sum(
                    1 for r in batch_results 
                    if "error" not in r and r["recommendation_count"] > 0
                ),
                "best_overall_similarity": max(
                    r["best_similarity"] for r in batch_results 
                    if "error" not in r and r["recommendation_count"] > 0
                ) if any(r.get("recommendation_count", 0) > 0 for r in batch_results) else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Batch recommendation error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch recommendation failed: {str(e)}")

@router.get("/solutions",
           summary="Browse available solutions",
           description="Browse and search the solution knowledge base")
async def browse_solutions(
    category: Optional[str] = Query(None, description="Filter by category"),
    search_term: Optional[str] = Query(None, description="Search term in solutions"),
    limit: int = Query(20, description="Maximum number of solutions to return"),
    offset: int = Query(0, description="Number of solutions to skip"),
    recommender: SolutionRecommender = Depends(get_recommender)
) -> Dict[str, Any]:
    """
    Browse and search the solution knowledge base.
    
    Allows exploration of available solutions without specific issue context.
    """
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")
    
    if offset < 0:
        raise HTTPException(status_code=400, detail="Offset must be non-negative")
    
    try:
        # Get sample solutions from recommender's knowledge base
        from api.main import sample_solutions
        
        if not sample_solutions:
            return {
                "total_solutions": 0,
                "solutions": [],
                "message": "No solutions available in knowledge base"
            }
        
        # Apply filters
        filtered_solutions = sample_solutions.copy()
        
        if category:
            filtered_solutions = [
                sol for sol in filtered_solutions
                if sol.get("category", "").lower() == category.lower() or
                   sol.get("issue_type", "").lower() == category.lower()
            ]
        
        if search_term:
            search_lower = search_term.lower()
            filtered_solutions = [
                sol for sol in filtered_solutions
                if search_lower in sol.get("solution", "").lower() or
                   search_lower in sol.get("title", "").lower() or
                   search_lower in sol.get("issue_type", "").lower()
            ]
        
        # Apply pagination
        total_count = len(filtered_solutions)
        paginated_solutions = filtered_solutions[offset:offset + limit]
        
        # Format solutions
        formatted_solutions = []
        for i, sol in enumerate(paginated_solutions):
            formatted_solutions.append({
                "id": sol.get("id", f"sol_{offset + i + 1}"),
                "title": sol.get("title", "Solution"),
                "category": sol.get("category", "general"),
                "issue_type": sol.get("issue_type"),
                "solution_preview": sol.get("solution", "")[:200] + "..." if len(sol.get("solution", "")) > 200 else sol.get("solution", ""),
                "complexity": sol.get("complexity", "medium"),
                "estimated_time": sol.get("estimated_time"),
                "success_rate": sol.get("success_rate"),
                "last_updated": sol.get("last_updated")
            })
        
        # Get available categories
        available_categories = list(set(
            sol.get("category", "unknown") for sol in sample_solutions
        ))
        
        return {
            "total_solutions": total_count,
            "returned_solutions": len(paginated_solutions),
            "offset": offset,
            "limit": limit,
            "solutions": formatted_solutions,
            "filters_applied": {
                "category": category,
                "search_term": search_term
            },
            "available_categories": available_categories,
            "pagination": {
                "has_next": offset + limit < total_count,
                "has_previous": offset > 0,
                "next_offset": offset + limit if offset + limit < total_count else None,
                "previous_offset": max(0, offset - limit) if offset > 0 else None
            }
        }
        
    except Exception as e:
        logger.error(f"Browse solutions error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to browse solutions: {str(e)}")

@router.get("/solution/{solution_id}",
           summary="Get detailed solution",
           description="Get detailed information about a specific solution")
async def get_solution_details(
    solution_id: str,
    recommender: SolutionRecommender = Depends(get_recommender)
) -> Dict[str, Any]:
    """
    Get detailed information about a specific solution.
    
    Returns complete solution details including implementation steps.
    """
    try:
        from api.main import sample_solutions
        
        # Find solution by ID
        solution = None
        for sol in sample_solutions:
            if sol.get("id") == solution_id or str(sol.get("id", "")).endswith(solution_id):
                solution = sol
                break
        
        if not solution:
            raise HTTPException(status_code=404, detail=f"Solution {solution_id} not found")
        
        return {
            "solution_id": solution.get("id"),
            "title": solution.get("title", "Solution"),
            "category": solution.get("category"),
            "issue_type": solution.get("issue_type"),
            "solution_text": solution.get("solution"),
            "details": {
                "complexity": solution.get("complexity", "medium"),
                "estimated_time": solution.get("estimated_time"),
                "success_rate": solution.get("success_rate"),
                "last_updated": solution.get("last_updated"),
                "source": solution.get("source", "knowledge_base")
            },
            "implementation": {
                "steps": solution.get("steps", []),
                "prerequisites": solution.get("prerequisites", []),
                "tools_required": solution.get("tools_required", []),
                "verification_steps": solution.get("verification", [])
            },
            "additional_info": {
                "potential_issues": solution.get("potential_issues", []),
                "alternatives": solution.get("alternatives", []),
                "related_solutions": solution.get("related_solutions", []),
                "references": solution.get("references", [])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get solution details error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get solution details: {str(e)}")

@router.get("/stats",
           summary="Get recommendation system statistics",
           description="Get statistics about the solution recommendation system")
async def get_recommender_stats(
    recommender: SolutionRecommender = Depends(get_recommender)
) -> Dict[str, Any]:
    """Get statistics about the recommendation system."""
    
    try:
        from api.main import sample_solutions
        
        # Calculate statistics
        categories = {}
        complexities = {}
        issue_types = {}
        
        for sol in sample_solutions:
            # Count categories
            category = sol.get("category", "unknown")
            categories[category] = categories.get(category, 0) + 1
            
            # Count complexities
            complexity = sol.get("complexity", "unknown")
            complexities[complexity] = complexities.get(complexity, 0) + 1
            
            # Count issue types
            issue_type = sol.get("issue_type", "unknown")
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        return {
            "knowledge_base": {
                "total_solutions": len(sample_solutions),
                "categories": categories,
                "complexities": complexities,
                "issue_types": issue_types
            },
            "recommendation_engine": {
                "algorithm": "Similarity-based (TF-IDF + Cosine Similarity)",
                "supports_batch": True,
                "supports_category_filter": True,
                "min_similarity_supported": 0.0,
                "max_similarity_supported": 1.0
            },
            "system_status": {
                "is_operational": recommender is not None,
                "knowledge_base_loaded": len(sample_solutions) > 0,
                "supports_similarity_scoring": True,
                "supports_ranking": True
            }
        }
        
    except Exception as e:
        logger.error(f"Get recommender stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommender stats: {str(e)}")
