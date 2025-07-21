"""
File Parser API Endpoints

Handles file upload, parsing, and processing operations.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import tempfile
import shutil
from pathlib import Path
import sys
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from parsers.v93k_parser import V93KParserFactory
from parsers.base_parser import ParsingError

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/upload", 
            summary="Upload and parse V93K files",
            description="Upload one or more V93K log files for parsing and analysis")
async def upload_and_parse_files(
    files: List[UploadFile] = File(..., description="V93K log files to parse"),
    module_name: Optional[str] = Form(None, description="Module name for context"),
    baseline_version: Optional[str] = Form(None, description="Baseline version for context")
) -> Dict[str, Any]:
    """
    Upload and parse V93K log files.
    
    Returns parsed data including test results, errors, and performance metrics.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    results = []
    failed_files = []
    
    for file in files:
        if not file.filename:
            continue
            
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
                # Copy uploaded file content
                shutil.copyfileobj(file.file, tmp_file)
                tmp_path = tmp_file.name
            
            try:
                # Parse the file
                parse_result = V93KParserFactory.parse_file(tmp_path)
                
                if parse_result:
                    # Add context if provided
                    if module_name:
                        parse_result.module_name = module_name
                    if baseline_version:
                        parse_result.baseline_version = baseline_version
                    
                    # Convert to API response format
                    result_data = {
                        "filename": file.filename,
                        "file_type": parse_result.file_type,
                        "parsing_successful": parse_result.parsing_successful,
                        "module_name": parse_result.module_name,
                        "baseline_version": parse_result.baseline_version,
                        "test_program_version": parse_result.test_program_version,
                        "test_results": parse_result.test_results,
                        "error_count": len(parse_result.error_messages),
                        "warning_count": len(parse_result.warnings),
                        "errors": [
                            {
                                "message": error["message"],
                                "line_number": error.get("line_number"),
                                "severity": error["severity"],
                                "timestamp": error.get("timestamp")
                            }
                            for error in parse_result.error_messages
                        ],
                        "warnings": [
                            {
                                "message": warning["message"],
                                "line_number": warning.get("line_number"),
                                "severity": warning["severity"],
                                "timestamp": warning.get("timestamp")
                            }
                            for warning in parse_result.warnings
                        ],
                        "execution_time": parse_result.execution_time,
                        "memory_usage": parse_result.memory_usage,
                        "parsed_at": parse_result.parsed_at.isoformat(),
                        "parsing_errors": parse_result.parsing_errors
                    }
                    
                    results.append(result_data)
                    logger.info(f"Successfully parsed {file.filename}")
                    
                else:
                    failed_files.append({
                        "filename": file.filename,
                        "error": "No suitable parser found for file"
                    })
                    
            finally:
                # Clean up temporary file
                Path(tmp_path).unlink(missing_ok=True)
                
        except ParsingError as e:
            failed_files.append({
                "filename": file.filename,
                "error": f"Parsing error: {str(e)}"
            })
            logger.error(f"Parsing error for {file.filename}: {e}")
            
        except Exception as e:
            failed_files.append({
                "filename": file.filename,
                "error": f"Unexpected error: {str(e)}"
            })
            logger.error(f"Unexpected error parsing {file.filename}: {e}")
    
    return {
        "total_files": len(files),
        "successful_parses": len(results),
        "failed_parses": len(failed_files),
        "results": results,
        "failed_files": failed_files,
        "summary": {
            "total_errors": sum(r["error_count"] for r in results),
            "total_warnings": sum(r["warning_count"] for r in results),
            "modules_processed": list(set(r["module_name"] for r in results if r["module_name"])),
            "baselines_processed": list(set(r["baseline_version"] for r in results if r["baseline_version"]))
        }
    }

@router.post("/parse-directory",
            summary="Parse all V93K files in a directory",
            description="Parse all compatible V93K files in a specified directory path")
async def parse_directory(
    directory_path: str = Form(..., description="Path to directory containing V93K files"),
    recursive: bool = Form(True, description="Search subdirectories recursively"),
    module_name: Optional[str] = Form(None, description="Module name for context"),
    baseline_version: Optional[str] = Form(None, description="Baseline version for context")
) -> Dict[str, Any]:
    """
    Parse all V93K files in a directory.
    
    Scans the specified directory for compatible V93K files and parses them.
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        raise HTTPException(status_code=404, detail=f"Directory not found: {directory_path}")
    
    if not directory.is_dir():
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {directory_path}")
    
    try:
        # Find all compatible files
        v93k_files = []
        
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
            
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                parser = V93KParserFactory.create_parser(file_path)
                if parser:
                    v93k_files.append(file_path)
        
        if not v93k_files:
            return {
                "directory": str(directory),
                "total_files": 0,
                "successful_parses": 0,
                "failed_parses": 0,
                "results": [],
                "failed_files": [],
                "message": "No compatible V93K files found in directory"
            }
        
        # Parse each file
        results = []
        failed_files = []
        
        for file_path in v93k_files:
            try:
                parse_result = V93KParserFactory.parse_file(file_path)
                
                if parse_result and parse_result.parsing_successful:
                    # Add context if provided
                    if module_name:
                        parse_result.module_name = module_name
                    if baseline_version:
                        parse_result.baseline_version = baseline_version
                    
                    result_data = {
                        "filepath": str(file_path),
                        "filename": file_path.name,
                        "file_type": parse_result.file_type,
                        "module_name": parse_result.module_name,
                        "baseline_version": parse_result.baseline_version,
                        "error_count": len(parse_result.error_messages),
                        "warning_count": len(parse_result.warnings),
                        "test_status": parse_result.test_results.get("overall_status", "unknown"),
                        "execution_time": parse_result.execution_time,
                        "parsed_at": parse_result.parsed_at.isoformat()
                    }
                    
                    results.append(result_data)
                    
                else:
                    failed_files.append({
                        "filepath": str(file_path),
                        "error": "Parsing failed or no parser available"
                    })
                    
            except Exception as e:
                failed_files.append({
                    "filepath": str(file_path),
                    "error": str(e)
                })
                logger.error(f"Error parsing {file_path}: {e}")
        
        return {
            "directory": str(directory),
            "recursive": recursive,
            "total_files": len(v93k_files),
            "successful_parses": len(results),
            "failed_parses": len(failed_files),
            "results": results,
            "failed_files": failed_files,
            "summary": {
                "total_errors": sum(r["error_count"] for r in results),
                "total_warnings": sum(r["warning_count"] for r in results),
                "modules_found": list(set(r["module_name"] for r in results if r["module_name"])),
                "baselines_found": list(set(r["baseline_version"] for r in results if r["baseline_version"])),
                "test_statuses": list(set(r["test_status"] for r in results))
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing directory {directory_path}: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing directory: {str(e)}")

@router.get("/supported-formats",
           summary="Get supported file formats",
           description="List all supported V93K file formats and their descriptions")
async def get_supported_formats() -> Dict[str, Any]:
    """Get information about supported V93K file formats."""
    
    return {
        "supported_formats": [
            {
                "extension": ".log",
                "description": "V93K test execution log files",
                "parser": "V93KLogParser",
                "typical_content": "Test results, error messages, timing information"
            },
            {
                "extension": ".dlog",
                "description": "V93K datalog measurement files",
                "parser": "V93KDatalogParser", 
                "typical_content": "Test measurements, pass/fail results, limits"
            },
            {
                "extension": ".datalog",
                "description": "V93K datalog measurement files (alternative extension)",
                "parser": "V93KDatalogParser",
                "typical_content": "Test measurements, pass/fail results, limits"
            },
            {
                "extension": ".txt",
                "description": "Text files containing V93K data",
                "parser": "Auto-detected based on content",
                "typical_content": "Various V93K outputs in text format"
            },
            {
                "extension": ".out",
                "description": "V93K build output files",
                "parser": "Auto-detected based on content",
                "typical_content": "Build logs, compilation results"
            }
        ],
        "detection_method": "Content-based detection with extension hints",
        "auto_detection": True,
        "max_file_size": "100MB",
        "encoding_support": ["utf-8", "ascii", "latin-1"]
    }
