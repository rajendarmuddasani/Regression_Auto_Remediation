"""
Main FastAPI Application for Regression Auto-Remediation System

Creates and configures the FastAPI application with all routes and middleware.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
import logging
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import Settings
from core.database import DatabaseManager
from models.issue_classifier import IssueClassifier, create_synthetic_training_data
from models.solution_recommender import SolutionRecommender
from parsers.v93k_parser import V93KParserFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
settings = Settings()
db_manager = None
issue_classifier = None
solution_recommender = None
sample_solutions = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    
    # Startup
    logger.info("🚀 Starting Regression Auto-Remediation API...")
    
    try:
        # Initialize global instances
        global db_manager, issue_classifier, solution_recommender
        
        # Initialize database manager
        logger.info("📊 Initializing database connection...")
        db_manager = DatabaseManager()
        
        # Initialize and train issue classifier
        logger.info("🧠 Initializing issue classifier...")
        issue_classifier = IssueClassifier()
        
        # Train with synthetic data if no model exists
        try:
            training_data = create_synthetic_training_data()
            training_results = issue_classifier.train_model(training_data)
            logger.info(f"✅ Classifier trained: {training_results['ensemble_accuracy']:.3f} accuracy")
        except Exception as e:
            logger.warning(f"⚠️ Classifier training failed: {e}")
        
        # Initialize solution recommender
        logger.info("💡 Initializing solution recommender...")
        knowledge_base_path = "knowledge_base.json"
        solution_recommender = SolutionRecommender(knowledge_base_path)
        
        # Add sample solutions if knowledge base is empty
        if not solution_recommender.solutions:
            logger.info("📝 Adding sample solutions to knowledge base...")
            _add_sample_solutions()
        
        logger.info("✅ API startup completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ API startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down Regression Auto-Remediation API...")
    
    try:
        # Save knowledge base
        if solution_recommender:
            knowledge_base_path = "knowledge_base.json"
            solution_recommender.save_knowledge_base(knowledge_base_path)
            logger.info("💾 Knowledge base saved successfully")
        
        # Close database connections
        if db_manager:
            # Add any cleanup if needed
            pass
        
        logger.info("✅ API shutdown completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ API shutdown failed: {e}")

def _add_sample_solutions():
    """Add sample solutions to the knowledge base."""
    global sample_solutions
    from models.solution_recommender import Solution
    from models.issue_classifier import IssueCategory
    
    sample_solutions = [
        Solution(
            solution_id="contact_force_fix",
            solution_type="parameter_update",
            description="Increase contact force to resolve contact resistance issues",
            parameter_changes=[{"parameter": "contact_force", "value": "150mN"}],
            category=IssueCategory.CONTACT_FAILURE,
            module_applicability=["CONTACT_TEST", "CONTACT_VALIDATION"],
            success_count=8,
            failure_count=1
        ),
        Solution(
            solution_id="timeout_increase",
            solution_type="config_change",
            description="Increase test timeout for slow operations",
            config_changes=[{"setting": "test_timeout", "value": "600"}],
            category=IssueCategory.TIMEOUT,
            module_applicability=["ALL"],
            success_count=5,
            failure_count=2
        ),
        Solution(
            solution_id="include_header_fix",
            solution_type="code_fix",
            description="Add missing header include for undefined symbols",
            code_changes=[{"file": "*.cpp", "change": "#include <missing_header.h>"}],
            category=IssueCategory.COMPILATION_ERROR,
            module_applicability=["ALL"],
            success_count=12,
            failure_count=0
        ),
        Solution(
            solution_id="calibration_reset",
            solution_type="parameter_update",
            description="Reset calibration parameters to factory defaults",
            parameter_changes=[{"parameter": "cal_reset", "value": "true"}],
            category=IssueCategory.CALIBRATION_ERROR,
            module_applicability=["ALL"],
            success_count=6,
            failure_count=1
        )
    ]
    
    for solution in sample_solutions:
        solution.update_success_metrics(True)  # Update confidence scores
        solution_recommender.add_solution(solution)

# Create FastAPI application
app = FastAPI(
    title="Regression Auto-Remediation API",
    description="REST API for automated V93K regression issue detection and remediation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database manager
def get_db_manager() -> DatabaseManager:
    """Dependency to get database manager instance."""
    if db_manager is None:
        raise HTTPException(status_code=503, detail="Database not initialized")
    return db_manager

# Dependency to get issue classifier
def get_issue_classifier() -> IssueClassifier:
    """Dependency to get issue classifier instance."""
    if issue_classifier is None:
        raise HTTPException(status_code=503, detail="Issue classifier not initialized")
    return issue_classifier

# Dependency to get solution recommender
def get_solution_recommender() -> SolutionRecommender:
    """Dependency to get solution recommender instance."""
    if solution_recommender is None:
        raise HTTPException(status_code=503, detail="Solution recommender not initialized")
    return solution_recommender

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - redirect to documentation."""
    return RedirectResponse(url="/docs")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "timestamp": "2025-07-21T00:00:00Z",
        "components": {
            "database": "available" if db_manager else "unavailable",
            "classifier": "available" if issue_classifier else "unavailable",
            "recommender": "available" if solution_recommender else "unavailable"
        }
    }

# Include API routes
from .endpoints import parser, classifier, recommender, system, monitoring

app.include_router(parser.router, prefix="/api/v1/parser", tags=["Parser"])
app.include_router(classifier.router, prefix="/api/v1/classifier", tags=["Classifier"])
app.include_router(recommender.router, prefix="/api/v1/recommender", tags=["Recommender"])
app.include_router(system.router, prefix="/api/v1/system", tags=["System"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["Monitoring"])
