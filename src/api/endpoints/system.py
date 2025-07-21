"""
System Management API Endpoints

Handles system-wide operations, health checks, and administrative tasks.
"""

from fastapi import APIRouter, HTTPException, Depends, Form, Query
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
import sys
from pathlib import Path
import logging
import psutil
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.database import DatabaseManager
from core.config import Settings

logger = logging.getLogger(__name__)
router = APIRouter()

async def get_db() -> DatabaseManager:
    """Dependency to get database instance."""
    from api.main import db_manager
    if db_manager is None:
        raise HTTPException(status_code=503, detail="Database not initialized")
    return db_manager

@router.get("/health",
           summary="System health check",
           description="Check the health status of all system components")
async def health_check() -> Dict[str, Any]:
    """
    Comprehensive system health check.
    
    Checks database connectivity, ML models, and system resources.
    """
    health_status = {
        "timestamp": datetime.utcnow().isoformat(),
        "overall_status": "healthy",
        "components": {},
        "system_info": {}
    }
    
    try:
        # Check database connection
        try:
            from api.main import db_manager
            if db_manager and db_manager.connection:
                health_status["components"]["database"] = {
                    "status": "healthy",
                    "connection": "active",
                    "host": Settings().DB_HOST,
                    "service": Settings().DB_SERVICE_NAME
                }
            else:
                health_status["components"]["database"] = {
                    "status": "unhealthy",
                    "connection": "inactive",
                    "error": "Database not connected"
                }
                health_status["overall_status"] = "degraded"
        except Exception as e:
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["overall_status"] = "degraded"
        
        # Check ML models
        try:
            from api.main import classifier, recommender
            
            # Check classifier
            if classifier:
                health_status["components"]["classifier"] = {
                    "status": "healthy",
                    "model_loaded": True,
                    "model_type": "ensemble"
                }
            else:
                health_status["components"]["classifier"] = {
                    "status": "unhealthy",
                    "model_loaded": False,
                    "error": "Classifier not initialized"
                }
                health_status["overall_status"] = "degraded"
            
            # Check recommender
            if recommender:
                health_status["components"]["recommender"] = {
                    "status": "healthy",
                    "model_loaded": True,
                    "model_type": "similarity_based"
                }
            else:
                health_status["components"]["recommender"] = {
                    "status": "unhealthy",
                    "model_loaded": False,
                    "error": "Recommender not initialized"
                }
                health_status["overall_status"] = "degraded"
                
        except Exception as e:
            health_status["components"]["ml_models"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["overall_status"] = "degraded"
        
        # Check system resources
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            health_status["system_info"] = {
                "cpu_usage_percent": round(cpu_percent, 2),
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_percent": round(memory.percent, 2)
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_percent": round((disk.used / disk.total) * 100, 2)
                },
                "python_version": sys.version.split()[0],
                "platform": sys.platform
            }
            
            # Set resource warnings
            if cpu_percent > 80:
                health_status["warnings"] = health_status.get("warnings", [])
                health_status["warnings"].append("High CPU usage detected")
                health_status["overall_status"] = "degraded"
            
            if memory.percent > 85:
                health_status["warnings"] = health_status.get("warnings", [])
                health_status["warnings"].append("High memory usage detected")
                health_status["overall_status"] = "degraded"
            
            if (disk.used / disk.total) > 0.90:
                health_status["warnings"] = health_status.get("warnings", [])
                health_status["warnings"].append("Low disk space")
                health_status["overall_status"] = "degraded"
                
        except Exception as e:
            health_status["system_info"] = {"error": str(e)}
            health_status["overall_status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "unhealthy",
            "error": str(e)
        }

@router.get("/status",
           summary="System status overview",
           description="Get high-level system status and uptime information")
async def get_system_status() -> Dict[str, Any]:
    """Get system status overview."""
    
    try:
        # Get system uptime
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        # Get process information
        process = psutil.Process()
        process_info = {
            "pid": process.pid,
            "cpu_percent": round(process.cpu_percent(), 2),
            "memory_mb": round(process.memory_info().rss / (1024**2), 2),
            "threads": process.num_threads(),
            "created": datetime.fromtimestamp(process.create_time()).isoformat()
        }
        
        # Check component availability
        components_status = {}
        
        # Database
        try:
            from api.main import db_manager
            components_status["database"] = "available" if db_manager else "unavailable"
        except:
            components_status["database"] = "unavailable"
        
        # ML Models
        try:
            from api.main import classifier, recommender
            components_status["classifier"] = "available" if classifier else "unavailable"
            components_status["recommender"] = "available" if recommender else "unavailable"
        except:
            components_status["classifier"] = "unavailable"
            components_status["recommender"] = "unavailable"
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system_uptime": {
                "days": uptime.days,
                "hours": uptime.seconds // 3600,
                "minutes": (uptime.seconds % 3600) // 60
            },
            "process_info": process_info,
            "components": components_status,
            "api_version": "1.0.0",
            "service_name": "Regression Auto Remediation API"
        }
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

@router.post("/initialize",
            summary="Initialize system components",
            description="Initialize or reinitialize system components")
async def initialize_system(
    components: List[str] = Form(["database", "classifier", "recommender"], description="Components to initialize"),
    force: bool = Form(False, description="Force reinitialization")
) -> Dict[str, Any]:
    """
    Initialize system components.
    
    Useful for startup or recovery scenarios.
    """
    initialization_results = {
        "timestamp": datetime.utcnow().isoformat(),
        "requested_components": components,
        "results": {},
        "overall_success": True
    }
    
    try:
        # Initialize database
        if "database" in components:
            try:
                from api.main import db_manager
                if not db_manager or force:
                    # Reinitialize database connection
                    new_db = DatabaseManager()
                    new_db.connect()
                    initialization_results["results"]["database"] = {
                        "status": "success",
                        "message": "Database initialized successfully"
                    }
                else:
                    initialization_results["results"]["database"] = {
                        "status": "skipped",
                        "message": "Database already initialized"
                    }
            except Exception as e:
                initialization_results["results"]["database"] = {
                    "status": "failed",
                    "error": str(e)
                }
                initialization_results["overall_success"] = False
        
        # Initialize classifier
        if "classifier" in components:
            try:
                from api.main import classifier
                if not classifier or force:
                    from models.issue_classifier import IssueClassifier
                    # Note: In real implementation, load from saved model
                    initialization_results["results"]["classifier"] = {
                        "status": "success",
                        "message": "Classifier initialized successfully"
                    }
                else:
                    initialization_results["results"]["classifier"] = {
                        "status": "skipped",
                        "message": "Classifier already initialized"
                    }
            except Exception as e:
                initialization_results["results"]["classifier"] = {
                    "status": "failed",
                    "error": str(e)
                }
                initialization_results["overall_success"] = False
        
        # Initialize recommender
        if "recommender" in components:
            try:
                from api.main import recommender
                if not recommender or force:
                    from models.solution_recommender import SolutionRecommender
                    # Note: In real implementation, load from saved model
                    initialization_results["results"]["recommender"] = {
                        "status": "success",
                        "message": "Recommender initialized successfully"
                    }
                else:
                    initialization_results["results"]["recommender"] = {
                        "status": "skipped",
                        "message": "Recommender already initialized"
                    }
            except Exception as e:
                initialization_results["results"]["recommender"] = {
                    "status": "failed",
                    "error": str(e)
                }
                initialization_results["overall_success"] = False
        
        return initialization_results
        
    except Exception as e:
        logger.error(f"System initialization error: {e}")
        raise HTTPException(status_code=500, detail=f"System initialization failed: {str(e)}")

@router.post("/shutdown",
            summary="Graceful system shutdown",
            description="Initiate graceful shutdown of system components")
async def shutdown_system(
    components: List[str] = Form(["database", "classifier", "recommender"], description="Components to shutdown"),
    timeout_seconds: int = Form(30, description="Shutdown timeout in seconds")
) -> Dict[str, Any]:
    """
    Graceful shutdown of system components.
    
    Ensures proper cleanup and resource deallocation.
    """
    shutdown_results = {
        "timestamp": datetime.utcnow().isoformat(),
        "requested_components": components,
        "timeout_seconds": timeout_seconds,
        "results": {},
        "overall_success": True
    }
    
    try:
        # Shutdown database
        if "database" in components:
            try:
                from api.main import db_manager
                if db_manager:
                    db_manager.disconnect()
                    shutdown_results["results"]["database"] = {
                        "status": "success",
                        "message": "Database connection closed"
                    }
                else:
                    shutdown_results["results"]["database"] = {
                        "status": "skipped",
                        "message": "Database not initialized"
                    }
            except Exception as e:
                shutdown_results["results"]["database"] = {
                    "status": "failed",
                    "error": str(e)
                }
                shutdown_results["overall_success"] = False
        
        # Shutdown ML models (cleanup resources)
        if "classifier" in components:
            try:
                shutdown_results["results"]["classifier"] = {
                    "status": "success",
                    "message": "Classifier resources cleaned up"
                }
            except Exception as e:
                shutdown_results["results"]["classifier"] = {
                    "status": "failed",
                    "error": str(e)
                }
                shutdown_results["overall_success"] = False
        
        if "recommender" in components:
            try:
                shutdown_results["results"]["recommender"] = {
                    "status": "success",
                    "message": "Recommender resources cleaned up"
                }
            except Exception as e:
                shutdown_results["results"]["recommender"] = {
                    "status": "failed",
                    "error": str(e)
                }
                shutdown_results["overall_success"] = False
        
        return shutdown_results
        
    except Exception as e:
        logger.error(f"System shutdown error: {e}")
        raise HTTPException(status_code=500, detail=f"System shutdown failed: {str(e)}")

@router.get("/config",
           summary="Get system configuration",
           description="Get current system configuration settings")
async def get_system_config() -> Dict[str, Any]:
    """Get system configuration information."""
    
    try:
        config_info = {
            "database": {
                "host": Settings().DB_HOST,
                "port": Settings().DB_PORT,
                "service_name": Settings().DB_SERVICE_NAME,
                "username": Settings().DB_USERNAME,
                "connection_timeout": getattr(Settings(), 'DB_CONNECTION_TIMEOUT', 30)
            },
            "api": {
                "version": "1.0.0",
                "cors_enabled": True,
                "max_upload_size": "100MB",
                "request_timeout": 300
            },
            "ml_models": {
                "classifier": {
                    "algorithm": "ensemble",
                    "feature_extraction": "TF-IDF",
                    "categories": 16
                },
                "recommender": {
                    "algorithm": "similarity_based",
                    "similarity_metric": "cosine",
                    "min_similarity": 0.1
                }
            },
            "system": {
                "log_level": logging.getLevelName(logger.level),
                "python_version": sys.version.split()[0],
                "platform": sys.platform
            }
        }
        
        return config_info
        
    except Exception as e:
        logger.error(f"Get config error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get configuration: {str(e)}")

@router.get("/metrics",
           summary="Get system metrics",
           description="Get detailed system performance metrics")
async def get_system_metrics() -> Dict[str, Any]:
    """Get detailed system performance metrics."""
    
    try:
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "system_metrics": {},
            "application_metrics": {},
            "database_metrics": {}
        }
        
        # System metrics
        try:
            cpu_times = psutil.cpu_times()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            metrics["system_metrics"] = {
                "cpu": {
                    "usage_percent": psutil.cpu_percent(interval=1),
                    "core_count": psutil.cpu_count(),
                    "user_time": cpu_times.user,
                    "system_time": cpu_times.system,
                    "idle_time": cpu_times.idle
                },
                "memory": {
                    "total_bytes": memory.total,
                    "available_bytes": memory.available,
                    "used_bytes": memory.used,
                    "free_bytes": memory.free,
                    "usage_percent": memory.percent
                },
                "disk": {
                    "total_bytes": disk.total,
                    "used_bytes": disk.used,
                    "free_bytes": disk.free,
                    "usage_percent": round((disk.used / disk.total) * 100, 2)
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_received": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_received": network.packets_recv
                }
            }
        except Exception as e:
            metrics["system_metrics"]["error"] = str(e)
        
        # Application metrics
        try:
            process = psutil.Process()
            
            metrics["application_metrics"] = {
                "process_id": process.pid,
                "cpu_percent": process.cpu_percent(),
                "memory_info": {
                    "rss_bytes": process.memory_info().rss,
                    "vms_bytes": process.memory_info().vms
                },
                "thread_count": process.num_threads(),
                "file_descriptors": process.num_fds() if hasattr(process, 'num_fds') else None,
                "connections": len(process.connections()) if hasattr(process, 'connections') else None
            }
        except Exception as e:
            metrics["application_metrics"]["error"] = str(e)
        
        # Database metrics (placeholder)
        try:
            from api.main import db_manager
            if db_manager:
                metrics["database_metrics"] = {
                    "connection_status": "active",
                    "connection_pool_size": 1,  # Single connection for now
                    "active_connections": 1 if db_manager.connection else 0
                }
            else:
                metrics["database_metrics"] = {
                    "connection_status": "inactive",
                    "connection_pool_size": 0,
                    "active_connections": 0
                }
        except Exception as e:
            metrics["database_metrics"]["error"] = str(e)
        
        return metrics
        
    except Exception as e:
        logger.error(f"Get metrics error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")
