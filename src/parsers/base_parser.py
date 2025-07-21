"""
Base Parser Classes for Regression Auto-Remediation System

Provides abstract base classes and common utilities for all parsers.
All specific parsers (V93K, Ultraflex, etc.) inherit from these base classes.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ParsingError(Exception):
    """Custom exception for parsing-related errors."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, line_number: Optional[int] = None):
        self.file_path = file_path
        self.line_number = line_number
        super().__init__(message)


@dataclass
class ParserResult:
    """
    Result container for parsed data from log files.
    
    Contains extracted information from regression data files including
    test results, error messages, timing data, and metadata.
    """
    
    # File metadata
    file_path: str
    file_type: str  # 'log', 'datalog', 'build_output', etc.
    parsed_at: datetime = field(default_factory=datetime.now)
    
    # Test execution data
    test_results: Dict[str, Any] = field(default_factory=dict)
    error_messages: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    
    # Performance data
    execution_time: Optional[float] = None
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    
    # V93K specific data
    module_name: Optional[str] = None
    baseline_version: Optional[str] = None
    test_program_version: Optional[str] = None
    
    # Build information
    build_status: Optional[str] = None  # 'success', 'failed', 'partial'
    build_errors: List[str] = field(default_factory=list)
    build_warnings: List[str] = field(default_factory=list)
    
    # Raw data
    raw_content: Optional[str] = None
    
    # Success indicators
    parsing_successful: bool = True
    parsing_errors: List[str] = field(default_factory=list)
    
    def add_error(self, message: str, line_number: Optional[int] = None, severity: str = 'error'):
        """Add an error message found during parsing."""
        error_entry = {
            'message': message,
            'line_number': line_number,
            'severity': severity,
            'timestamp': datetime.now()
        }
        
        if severity == 'error':
            self.error_messages.append(error_entry)
        elif severity == 'warning':
            self.warnings.append(error_entry)
    
    def add_parsing_error(self, error: str):
        """Add a parsing error (system-level error, not test error)."""
        self.parsing_errors.append(error)
        self.parsing_successful = False
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the parsing results."""
        return {
            'file_path': self.file_path,
            'file_type': self.file_type,
            'parsed_at': self.parsed_at.isoformat(),
            'module_name': self.module_name,
            'baseline_version': self.baseline_version,
            'parsing_successful': self.parsing_successful,
            'error_count': len(self.error_messages),
            'warning_count': len(self.warnings),
            'build_status': self.build_status,
            'execution_time': self.execution_time
        }


class BaseParser(ABC):
    """
    Abstract base class for all log file parsers.
    
    Provides common functionality and enforces interface for specific parsers.
    """
    
    def __init__(self, parser_name: str):
        self.parser_name = parser_name
        self.logger = logging.getLogger(f"{__name__}.{parser_name}")
        
    @abstractmethod
    def parse_file(self, file_path: Union[str, Path]) -> ParserResult:
        """
        Parse a single file and return structured data.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            ParserResult containing extracted data
            
        Raises:
            ParsingError: If parsing fails
        """
        pass
    
    @abstractmethod
    def can_parse(self, file_path: Union[str, Path]) -> bool:
        """
        Check if this parser can handle the given file.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if this parser can handle the file, False otherwise
        """
        pass
    
    def validate_file(self, file_path: Union[str, Path]) -> bool:
        """
        Validate that a file exists and is readable.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if file is valid, False otherwise
        """
        try:
            path = Path(file_path)
            return path.exists() and path.is_file() and path.stat().st_size > 0
        except Exception as e:
            self.logger.warning(f"File validation failed for {file_path}: {e}")
            return False
    
    def read_file_content(self, file_path: Union[str, Path]) -> str:
        """
        Read file content with proper error handling.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            File content as string
            
        Raises:
            ParsingError: If file cannot be read
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
        except Exception as e:
            raise ParsingError(f"Failed to read file {file_path}: {e}", str(file_path))
    
    def extract_timestamp_from_line(self, line: str) -> Optional[datetime]:
        """
        Extract timestamp from a log line.
        Common utility method for timestamp extraction.
        
        Args:
            line: Log line to parse
            
        Returns:
            Extracted datetime or None if not found
        """
        # Common timestamp patterns in V93K logs
        import re
        
        # Pattern: 2025-07-21 14:30:25.123
        pattern1 = r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?)'
        
        # Pattern: Jul 21 14:30:25
        pattern2 = r'([A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})'
        
        for pattern in [pattern1, pattern2]:
            match = re.search(pattern, line)
            if match:
                try:
                    if pattern == pattern1:
                        return datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S.%f')
                    else:
                        # Add current year for pattern2
                        timestamp_str = f"{datetime.now().year} {match.group(1)}"
                        return datetime.strptime(timestamp_str, '%Y %b %d %H:%M:%S')
                except ValueError:
                    continue
        
        return None
    
    def parse_directory(self, directory_path: Union[str, Path]) -> List[ParserResult]:
        """
        Parse all compatible files in a directory.
        
        Args:
            directory_path: Path to directory to scan
            
        Returns:
            List of ParserResult objects
        """
        results = []
        directory = Path(directory_path)
        
        if not directory.exists() or not directory.is_dir():
            self.logger.error(f"Directory not found or not a directory: {directory_path}")
            return results
        
        for file_path in directory.rglob("*"):
            if file_path.is_file() and self.can_parse(file_path):
                try:
                    result = self.parse_file(file_path)
                    results.append(result)
                    self.logger.info(f"Successfully parsed {file_path}")
                except ParsingError as e:
                    self.logger.error(f"Failed to parse {file_path}: {e}")
                except Exception as e:
                    self.logger.error(f"Unexpected error parsing {file_path}: {e}")
        
        return results


class FileTypeDetector:
    """
    Utility class to detect file types for appropriate parser selection.
    """
    
    @staticmethod
    def detect_file_type(file_path: Union[str, Path]) -> str:
        """
        Detect the type of a file based on extension and content.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            String indicating file type ('v93k_log', 'datalog', 'build_output', 'unknown')
        """
        path = Path(file_path)
        
        # Check file extension first
        extension = path.suffix.lower()
        if extension in ['.log']:
            return 'v93k_log'
        elif extension in ['.datalog', '.dlog']:
            return 'datalog'
        elif extension in ['.out', '.txt']:
            # Need to check content to distinguish build output vs other text
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    first_lines = f.read(1024)  # Read first 1KB
                    
                if any(keyword in first_lines.lower() for keyword in ['build', 'compile', 'make', 'gcc']):
                    return 'build_output'
                elif any(keyword in first_lines.lower() for keyword in ['v93k', 'test program', 'datalog']):
                    return 'v93k_log'
            except Exception:
                pass
        
        return 'unknown'
    
    @staticmethod
    def is_v93k_file(file_path: Union[str, Path]) -> bool:
        """Check if file appears to be V93K-related."""
        file_type = FileTypeDetector.detect_file_type(file_path)
        return file_type in ['v93k_log', 'datalog']
