"""
V93K Log Parser for Regression Auto-Remediation System

Specialized parsers for V93K test program files including:
- V93K execution logs
- Datalog files
- Build output
- Test program execution results
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import logging

from .base_parser import BaseParser, ParserResult, ParsingError

logger = logging.getLogger(__name__)


class V93KLogParser(BaseParser):
    """
    Parser for V93K test program execution log files.
    
    Extracts test results, error messages, timing information,
    and execution context from V93K log files.
    """
    
    def __init__(self):
        super().__init__("V93KLogParser")
        
        # V93K log patterns - these are common patterns found in V93K logs
        self.patterns = {
            'test_start': re.compile(r'(?i)test\s+(?:program\s+)?start', re.MULTILINE),
            'test_end': re.compile(r'(?i)test\s+(?:program\s+)?(?:end|complete)', re.MULTILINE),
            'error': re.compile(r'(?i)error[:\s](.+)', re.MULTILINE),
            'warning': re.compile(r'(?i)warning[:\s](.+)', re.MULTILINE),
            'failure': re.compile(r'(?i)(?:fail|failed)[:\s](.+)', re.MULTILINE),
            'pass': re.compile(r'(?i)(?:pass|passed)[:\s](.+)', re.MULTILINE),
            'module': re.compile(r'(?i)module[:\s]+([^\s,]+)', re.MULTILINE),
            'baseline': re.compile(r'(?i)baseline[:\s]+([^\s,]+)', re.MULTILINE),
            'version': re.compile(r'(?i)version[:\s]+([^\s,]+)', re.MULTILINE),
            'timing': re.compile(r'(?i)(?:time|duration)[:\s]+([0-9.]+)\s*(?:s|sec|seconds?)?', re.MULTILINE),
            'memory': re.compile(r'(?i)memory[:\s]+([0-9.]+)\s*(?:mb|gb|bytes?)?', re.MULTILINE),
            'timestamp': re.compile(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?)', re.MULTILINE)
        }
        
        # V93K specific error patterns
        self.v93k_error_patterns = {
            'compile_error': re.compile(r'(?i)compilation\s+(?:error|failed)', re.MULTILINE),
            'runtime_error': re.compile(r'(?i)runtime\s+error', re.MULTILINE),
            'timeout_error': re.compile(r'(?i)timeout|time\s+out', re.MULTILINE),
            'resource_error': re.compile(r'(?i)resource\s+(?:not\s+available|error)', re.MULTILINE),
            'syntax_error': re.compile(r'(?i)syntax\s+error', re.MULTILINE)
        }
    
    def can_parse(self, file_path: Union[str, Path]) -> bool:
        """
        Check if this parser can handle the given file.
        
        Looks for V93K-specific indicators in filename and content.
        """
        path = Path(file_path)
        
        # Check file extension
        if path.suffix.lower() not in ['.log', '.txt', '.out']:
            return False
        
        # Check filename for V93K indicators
        filename = path.name.lower()
        v93k_indicators = ['v93k', 'test_program', 'regression', 'smt', 'datalog']
        
        if any(indicator in filename for indicator in v93k_indicators):
            return True
        
        # Check file content for V93K indicators
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                first_lines = f.read(2048)  # Read first 2KB
                
            content_indicators = ['v93k', 'test program', 'smt7', 'smt8', 'advantest']
            return any(indicator.lower() in first_lines.lower() for indicator in content_indicators)
        except Exception:
            return False
    
    def parse_file(self, file_path: Union[str, Path]) -> ParserResult:
        """
        Parse a V93K log file and extract structured data.
        
        Args:
            file_path: Path to the V93K log file
            
        Returns:
            ParserResult containing extracted data
            
        Raises:
            ParsingError: If parsing fails
        """
        if not self.validate_file(file_path):
            raise ParsingError(f"Invalid file: {file_path}", str(file_path))
        
        # Initialize result
        result = ParserResult(
            file_path=str(file_path),
            file_type='v93k_log'
        )
        
        try:
            # Read file content
            content = self.read_file_content(file_path)
            result.raw_content = content
            
            # Extract basic information
            self._extract_metadata(content, result)
            self._extract_test_results(content, result)
            self._extract_errors_and_warnings(content, result)
            self._extract_performance_data(content, result)
            self._extract_v93k_specific_data(content, result)
            
            self.logger.info(f"Successfully parsed V93K log: {file_path}")
            
        except Exception as e:
            error_msg = f"Failed to parse V93K log {file_path}: {e}"
            result.add_parsing_error(error_msg)
            self.logger.error(error_msg)
        
        return result
    
    def _extract_metadata(self, content: str, result: ParserResult) -> None:
        """Extract basic metadata from log content."""
        # Extract module name
        module_match = self.patterns['module'].search(content)
        if module_match:
            result.module_name = module_match.group(1).strip()
        
        # Extract baseline version
        baseline_match = self.patterns['baseline'].search(content)
        if baseline_match:
            result.baseline_version = baseline_match.group(1).strip()
        
        # Extract test program version
        version_match = self.patterns['version'].search(content)
        if version_match:
            result.test_program_version = version_match.group(1).strip()
    
    def _extract_test_results(self, content: str, result: ParserResult) -> None:
        """Extract test execution results."""
        test_results = {}
        
        # Count passed tests
        pass_matches = self.patterns['pass'].findall(content)
        test_results['passed_tests'] = len(pass_matches)
        test_results['passed_details'] = pass_matches
        
        # Count failed tests
        fail_matches = self.patterns['failure'].findall(content)
        test_results['failed_tests'] = len(fail_matches)
        test_results['failed_details'] = fail_matches
        
        # Overall test status
        if test_results['failed_tests'] > 0:
            test_results['overall_status'] = 'failed'
        elif test_results['passed_tests'] > 0:
            test_results['overall_status'] = 'passed'
        else:
            test_results['overall_status'] = 'unknown'
        
        # Test execution timeframe
        start_match = self.patterns['test_start'].search(content)
        end_match = self.patterns['test_end'].search(content)
        
        if start_match and end_match:
            test_results['has_complete_execution'] = True
        else:
            test_results['has_complete_execution'] = False
        
        result.test_results = test_results
    
    def _extract_errors_and_warnings(self, content: str, result: ParserResult) -> None:
        """Extract error and warning messages."""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check for errors
            error_match = self.patterns['error'].search(line)
            if error_match:
                result.add_error(
                    message=error_match.group(1).strip(),
                    line_number=line_num,
                    severity='error'
                )
            
            # Check for warnings
            warning_match = self.patterns['warning'].search(line)
            if warning_match:
                result.add_error(
                    message=warning_match.group(1).strip(),
                    line_number=line_num,
                    severity='warning'
                )
            
            # Check for V93K-specific errors
            for error_type, pattern in self.v93k_error_patterns.items():
                if pattern.search(line):
                    result.add_error(
                        message=f"{error_type}: {line.strip()}",
                        line_number=line_num,
                        severity='error'
                    )
    
    def _extract_performance_data(self, content: str, result: ParserResult) -> None:
        """Extract performance and timing data."""
        # Extract execution time
        timing_match = self.patterns['timing'].search(content)
        if timing_match:
            try:
                result.execution_time = float(timing_match.group(1))
            except ValueError:
                pass
        
        # Extract memory usage
        memory_match = self.patterns['memory'].search(content)
        if memory_match:
            try:
                result.memory_usage = float(memory_match.group(1))
            except ValueError:
                pass
    
    def _extract_v93k_specific_data(self, content: str, result: ParserResult) -> None:
        """Extract V93K-specific information."""
        v93k_data = {}
        
        # Look for V93K software version
        smt_patterns = [
            r'(?i)smt\s*([78])[^\w]',
            r'(?i)v93k\s+(\d+\.\d+)',
            r'(?i)advantest\s+v(\d+\.\d+)'
        ]
        
        for pattern in smt_patterns:
            match = re.search(pattern, content)
            if match:
                v93k_data['v93k_version'] = match.group(1)
                break
        
        # Look for test suite information
        suite_pattern = r'(?i)test\s+suite[:\s]+([^\n,]+)'
        suite_match = re.search(suite_pattern, content)
        if suite_match:
            v93k_data['test_suite'] = suite_match.group(1).strip()
        
        # Look for device information
        device_pattern = r'(?i)device[:\s]+([^\n,]+)'
        device_match = re.search(device_pattern, content)
        if device_match:
            v93k_data['device'] = device_match.group(1).strip()
        
        # Add to test results
        if v93k_data:
            result.test_results['v93k_specific'] = v93k_data


class V93KDatalogParser(BaseParser):
    """
    Parser for V93K datalog files.
    
    Extracts test data, measurements, and results from V93K datalog files.
    """
    
    def __init__(self):
        super().__init__("V93KDatalogParser")
        
        # Datalog specific patterns
        self.patterns = {
            'header': re.compile(r'^#.*$', re.MULTILINE),
            'test_name': re.compile(r'(?i)test[_\s]*name[:\s]*([^\s,]+)', re.MULTILINE),
            'measurement': re.compile(r'([0-9.-]+)\s*,\s*([A-Z]+)\s*,\s*([^\n,]+)', re.MULTILINE),
            'timestamp': re.compile(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', re.MULTILINE),
            'pass_fail': re.compile(r'(?i)(pass|fail)[,\s]', re.MULTILINE)
        }
    
    def can_parse(self, file_path: Union[str, Path]) -> bool:
        """Check if this parser can handle the given datalog file."""
        path = Path(file_path)
        
        # Check file extension
        if path.suffix.lower() not in ['.datalog', '.dlog', '.dat', '.csv']:
            return False
        
        # Check filename for datalog indicators
        filename = path.name.lower()
        datalog_indicators = ['datalog', 'dlog', 'test_data', 'measurements']
        
        if any(indicator in filename for indicator in datalog_indicators):
            return True
        
        # Check file content structure
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                first_lines = f.read(1024)
                
            # Look for datalog-like structure (headers, CSV-like data)
            lines = first_lines.split('\n')[:10]  # Check first 10 lines
            
            # Look for common datalog headers
            header_indicators = ['test_name', 'measurement', 'value', 'unit', 'pass/fail']
            has_headers = any(
                any(indicator in line.lower() for indicator in header_indicators)
                for line in lines
            )
            
            # Look for CSV-like structure
            has_csv_structure = any(',' in line for line in lines)
            
            return has_headers or has_csv_structure
            
        except Exception:
            return False
    
    def parse_file(self, file_path: Union[str, Path]) -> ParserResult:
        """
        Parse a V93K datalog file and extract structured data.
        
        Args:
            file_path: Path to the datalog file
            
        Returns:
            ParserResult containing extracted data
            
        Raises:
            ParsingError: If parsing fails
        """
        if not self.validate_file(file_path):
            raise ParsingError(f"Invalid datalog file: {file_path}", str(file_path))
        
        result = ParserResult(
            file_path=str(file_path),
            file_type='datalog'
        )
        
        try:
            content = self.read_file_content(file_path)
            result.raw_content = content
            
            # Parse datalog content
            self._extract_datalog_metadata(content, result)
            self._extract_measurements(content, result)
            self._extract_test_summary(content, result)
            
            self.logger.info(f"Successfully parsed datalog: {file_path}")
            
        except Exception as e:
            error_msg = f"Failed to parse datalog {file_path}: {e}"
            result.add_parsing_error(error_msg)
            self.logger.error(error_msg)
        
        return result
    
    def _extract_datalog_metadata(self, content: str, result: ParserResult) -> None:
        """Extract metadata from datalog headers."""
        lines = content.split('\n')
        
        # Extract header information
        headers = []
        for line in lines:
            if line.strip().startswith('#') or 'test_name' in line.lower():
                headers.append(line.strip())
        
        result.test_results['headers'] = headers
        
        # Extract test name
        test_name_match = self.patterns['test_name'].search(content)
        if test_name_match:
            result.test_results['test_name'] = test_name_match.group(1)
    
    def _extract_measurements(self, content: str, result: ParserResult) -> None:
        """Extract measurement data from datalog."""
        measurements = []
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Skip header lines
            if line.strip().startswith('#') or not line.strip():
                continue
            
            # Try to parse as CSV data
            if ',' in line:
                try:
                    fields = [field.strip() for field in line.split(',')]
                    if len(fields) >= 3:  # At least value, unit, result
                        measurement = {
                            'line_number': line_num,
                            'raw_data': line.strip(),
                            'fields': fields
                        }
                        
                        # Try to extract numeric value
                        try:
                            measurement['value'] = float(fields[0])
                        except ValueError:
                            pass
                        
                        measurements.append(measurement)
                        
                except Exception as e:
                    result.add_error(f"Failed to parse measurement line: {line}", line_num, 'warning')
        
        result.test_results['measurements'] = measurements
        result.test_results['measurement_count'] = len(measurements)
    
    def _extract_test_summary(self, content: str, result: ParserResult) -> None:
        """Extract test summary information."""
        # Count pass/fail results
        pass_fail_matches = self.patterns['pass_fail'].findall(content)
        
        passed = sum(1 for match in pass_fail_matches if match.lower() == 'pass')
        failed = sum(1 for match in pass_fail_matches if match.lower() == 'fail')
        
        result.test_results.update({
            'total_tests': passed + failed,
            'passed_tests': passed,
            'failed_tests': failed,
            'pass_rate': (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0
        })
        
        # Overall status
        if failed > 0:
            result.test_results['overall_status'] = 'failed'
        elif passed > 0:
            result.test_results['overall_status'] = 'passed'
        else:
            result.test_results['overall_status'] = 'no_results'


class V93KParserFactory:
    """
    Factory class to create appropriate V93K parsers based on file type.
    """
    
    @staticmethod
    def create_parser(file_path: Union[str, Path]) -> Optional[BaseParser]:
        """
        Create the appropriate parser for a given file.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            Appropriate parser instance or None if no parser available
        """
        # Try V93K log parser first
        log_parser = V93KLogParser()
        if log_parser.can_parse(file_path):
            return log_parser
        
        # Try datalog parser
        datalog_parser = V93KDatalogParser()
        if datalog_parser.can_parse(file_path):
            return datalog_parser
        
        return None
    
    @staticmethod
    def parse_file(file_path: Union[str, Path]) -> Optional[ParserResult]:
        """
        Parse a file using the appropriate parser.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            ParserResult or None if no suitable parser found
        """
        parser = V93KParserFactory.create_parser(file_path)
        if parser:
            return parser.parse_file(file_path)
        return None
