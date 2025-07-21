#!/usr/bin/env python3
"""
Test Script for V93K Log Parsers
Tests the V93K log and datalog parsers with sample data
"""

import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from parsers.v93k_parser import V93KLogParser, V93KDatalogParser, V93KParserFactory
from parsers.base_parser import ParsingError

def create_sample_v93k_log():
    """Create a sample V93K log file for testing."""
    sample_content = """
# V93K Test Program Execution Log
# Module: CONTACT_TEST
# Baseline: v2.1.5
# Version: 1.0.3
# Date: 2025-07-21 14:30:25.123

V93K SMT7 Test Program Starting...
Test Suite: CONTACT_REGRESSION
Device: XYZ_DEVICE_V1

2025-07-21 14:30:26.000 INFO: Initializing test environment
2025-07-21 14:30:27.000 INFO: Loading test program
2025-07-21 14:30:28.000 INFO: Starting test execution

Test: CONTACT_RESISTANCE_1 - PASSED (0.025 ohms)
Test: CONTACT_RESISTANCE_2 - PASSED (0.023 ohms)
Test: CONTACT_OPEN_TEST - PASSED
Test: CONTACT_SHORT_TEST - FAILED (short detected on pin 5)

WARNING: Temperature sensor reading unstable
ERROR: Pin 5 short circuit detected

Test execution completed
Duration: 45.2 seconds
Memory usage: 128.5 MB

Test Program End
Results: 3 passed, 1 failed
"""
    
    # Create sample file
    sample_file = Path("sample_v93k.log")
    with open(sample_file, 'w') as f:
        f.write(sample_content)
    
    return sample_file

def create_sample_datalog():
    """Create a sample datalog file for testing."""
    sample_content = """
# V93K Datalog File
# Test: CONTACT_TESTS
# Date: 2025-07-21
# Module: CONTACT_TEST

Test_Name,Value,Unit,Pass/Fail,Limit_Low,Limit_High
CONTACT_RES_1,0.025,ohm,PASS,0.010,0.050
CONTACT_RES_2,0.023,ohm,PASS,0.010,0.050
CONTACT_RES_3,0.067,ohm,FAIL,0.010,0.050
OPEN_TEST,999.9,kohm,PASS,100.0,9999.0
SHORT_TEST,0.001,ohm,FAIL,10.0,9999.0
"""
    
    sample_file = Path("sample_datalog.dlog")
    with open(sample_file, 'w') as f:
        f.write(sample_content)
    
    return sample_file

def test_v93k_log_parser():
    """Test the V93K log parser."""
    print("🧪 Testing V93K Log Parser...")
    
    # Create sample file
    sample_file = create_sample_v93k_log()
    
    try:
        # Test parser detection
        parser = V93KLogParser()
        can_parse = parser.can_parse(sample_file)
        print(f"   ✅ Parser detection: {can_parse}")
        
        # Test parsing
        result = parser.parse_file(sample_file)
        print(f"   ✅ Parsing successful: {result.parsing_successful}")
        print(f"   📊 Module: {result.module_name}")
        print(f"   📊 Baseline: {result.baseline_version}")
        print(f"   📊 Test results: {result.test_results.get('overall_status', 'unknown')}")
        print(f"   📊 Passed tests: {result.test_results.get('passed_tests', 0)}")
        print(f"   📊 Failed tests: {result.test_results.get('failed_tests', 0)}")
        print(f"   📊 Errors found: {len(result.error_messages)}")
        print(f"   📊 Warnings found: {len(result.warnings)}")
        print(f"   📊 Execution time: {result.execution_time}s")
        
        # Display errors and warnings
        if result.error_messages:
            print("   🔴 Errors found:")
            for error in result.error_messages:
                print(f"      Line {error['line_number']}: {error['message']}")
        
        if result.warnings:
            print("   🟡 Warnings found:")
            for warning in result.warnings:
                print(f"      Line {warning['line_number']}: {warning['message']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False
    
    finally:
        # Cleanup
        if sample_file.exists():
            sample_file.unlink()

def test_datalog_parser():
    """Test the datalog parser."""
    print("\n🧪 Testing Datalog Parser...")
    
    # Create sample file
    sample_file = create_sample_datalog()
    
    try:
        # Test parser detection
        parser = V93KDatalogParser()
        can_parse = parser.can_parse(sample_file)
        print(f"   ✅ Parser detection: {can_parse}")
        
        # Test parsing
        result = parser.parse_file(sample_file)
        print(f"   ✅ Parsing successful: {result.parsing_successful}")
        print(f"   📊 Test name: {result.test_results.get('test_name', 'unknown')}")
        print(f"   📊 Total measurements: {result.test_results.get('measurement_count', 0)}")
        print(f"   📊 Passed tests: {result.test_results.get('passed_tests', 0)}")
        print(f"   📊 Failed tests: {result.test_results.get('failed_tests', 0)}")
        print(f"   📊 Pass rate: {result.test_results.get('pass_rate', 0):.1f}%")
        
        # Display some measurements
        measurements = result.test_results.get('measurements', [])
        if measurements:
            print("   📈 Sample measurements:")
            for i, measurement in enumerate(measurements[:3]):  # Show first 3
                print(f"      {i+1}: {measurement.get('raw_data', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False
    
    finally:
        # Cleanup
        if sample_file.exists():
            sample_file.unlink()

def test_parser_factory():
    """Test the parser factory."""
    print("\n🧪 Testing Parser Factory...")
    
    # Create sample files
    log_file = create_sample_v93k_log()
    datalog_file = create_sample_datalog()
    
    try:
        # Test factory parser selection
        log_parser = V93KParserFactory.create_parser(log_file)
        datalog_parser = V93KParserFactory.create_parser(datalog_file)
        
        print(f"   ✅ Log file parser: {type(log_parser).__name__ if log_parser else 'None'}")
        print(f"   ✅ Datalog file parser: {type(datalog_parser).__name__ if datalog_parser else 'None'}")
        
        # Test factory parsing
        log_result = V93KParserFactory.parse_file(log_file)
        datalog_result = V93KParserFactory.parse_file(datalog_file)
        
        print(f"   ✅ Log parsing successful: {log_result.parsing_successful if log_result else False}")
        print(f"   ✅ Datalog parsing successful: {datalog_result.parsing_successful if datalog_result else False}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False
    
    finally:
        # Cleanup
        for file in [log_file, datalog_file]:
            if file.exists():
                file.unlink()

def test_error_handling():
    """Test error handling."""
    print("\n🧪 Testing Error Handling...")
    
    try:
        parser = V93KLogParser()
        
        # Test with non-existent file
        try:
            result = parser.parse_file("non_existent_file.log")
            print("   ❌ Should have failed with non-existent file")
            return False
        except ParsingError:
            print("   ✅ Correctly handled non-existent file")
        
        # Test with empty file
        empty_file = Path("empty.log")
        empty_file.touch()
        
        try:
            result = parser.parse_file(empty_file)
            print("   ❌ Should have failed with empty file")
            return False
        except ParsingError:
            print("   ✅ Correctly handled empty file")
        finally:
            empty_file.unlink()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

def main():
    """Run all parser tests."""
    print("🚀 V93K Parser Test Suite")
    print("=" * 50)
    
    tests = [
        test_v93k_log_parser,
        test_datalog_parser,
        test_parser_factory,
        test_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())
