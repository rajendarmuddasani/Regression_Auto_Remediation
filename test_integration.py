"""
V93K Parser Integration Script
Demonstrates integration between V93K parsers and the database system
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from parsers.v93k_parser import V93KParserFactory
from core.config import Settings
from core.database import DatabaseManager
from core.models import RegressionDaily, RegressionResults

def process_regression_files(directory_path: str) -> Dict[str, Any]:
    """
    Process all V93K files in a directory and prepare data for database storage.
    
    Args:
        directory_path: Path to directory containing V93K files
        
    Returns:
        Dictionary containing processing results
    """
    results = {
        'processed_files': [],
        'failed_files': [],
        'total_errors': 0,
        'total_warnings': 0,
        'processing_summary': {}
    }
    
    directory = Path(directory_path)
    if not directory.exists():
        print(f"❌ Directory not found: {directory_path}")
        return results
    
    print(f"🔍 Scanning directory: {directory_path}")
    
    # Find all potential V93K files
    v93k_files = []
    for file_path in directory.rglob("*"):
        if file_path.is_file():
            parser = V93KParserFactory.create_parser(file_path)
            if parser:
                v93k_files.append(file_path)
    
    print(f"📁 Found {len(v93k_files)} V93K files to process")
    
    # Process each file
    for file_path in v93k_files:
        try:
            print(f"🔄 Processing: {file_path.name}")
            
            # Parse the file
            parse_result = V93KParserFactory.parse_file(file_path)
            
            if parse_result and parse_result.parsing_successful:
                # Prepare data for database storage
                file_data = prepare_database_data(parse_result)
                
                results['processed_files'].append({
                    'file_path': str(file_path),
                    'module_name': parse_result.module_name,
                    'baseline_version': parse_result.baseline_version,
                    'error_count': len(parse_result.error_messages),
                    'warning_count': len(parse_result.warnings),
                    'test_status': parse_result.test_results.get('overall_status', 'unknown'),
                    'database_data': file_data
                })
                
                results['total_errors'] += len(parse_result.error_messages)
                results['total_warnings'] += len(parse_result.warnings)
                
                print(f"   ✅ Successfully processed")
                print(f"      Module: {parse_result.module_name}")
                print(f"      Baseline: {parse_result.baseline_version}")
                print(f"      Errors: {len(parse_result.error_messages)}")
                print(f"      Warnings: {len(parse_result.warnings)}")
                
            else:
                results['failed_files'].append({
                    'file_path': str(file_path),
                    'errors': parse_result.parsing_errors if parse_result else ['Parser creation failed']
                })
                print(f"   ❌ Failed to process")
                
        except Exception as e:
            results['failed_files'].append({
                'file_path': str(file_path),
                'errors': [str(e)]
            })
            print(f"   ❌ Exception during processing: {e}")
    
    # Generate summary
    results['processing_summary'] = {
        'total_files': len(v93k_files),
        'successful': len(results['processed_files']),
        'failed': len(results['failed_files']),
        'success_rate': (len(results['processed_files']) / len(v93k_files)) * 100 if v93k_files else 0,
        'total_errors': results['total_errors'],
        'total_warnings': results['total_warnings']
    }
    
    return results

def prepare_database_data(parse_result) -> Dict[str, Any]:
    """
    Convert parser result to database-ready format.
    
    Args:
        parse_result: ParserResult object from parser
        
    Returns:
        Dictionary ready for database storage
    """
    return {
        'regression_daily': {
            'module_name': parse_result.module_name or 'UNKNOWN',
            'baseline_version': parse_result.baseline_version or '0.0.0',
            'test_program_version': parse_result.test_program_version or '1.0.0',
            'regression_date': datetime.now().date(),
            'log_file_path': parse_result.file_path,
            'overall_status': parse_result.test_results.get('overall_status', 'unknown'),
            'error_count': len(parse_result.error_messages),
            'warning_count': len(parse_result.warnings),
            'execution_time': parse_result.execution_time,
            'memory_usage': parse_result.memory_usage,
            'enabled': True
        },
        'regression_results': [
            {
                'error_type': error['severity'],
                'error_message': error['message'],
                'line_number': error.get('line_number', 0),
                'error_timestamp': error.get('timestamp', datetime.now()),
                'severity_level': 'HIGH' if error['severity'] == 'error' else 'MEDIUM',
                'resolution_status': 'NEW'
            }
            for error in parse_result.error_messages
        ]
    }

def simulate_database_storage(processing_results: Dict[str, Any]):
    """
    Simulate storing parsed data in the database.
    
    Args:
        processing_results: Results from process_regression_files
    """
    print("\n💾 Simulating Database Storage...")
    
    # Check if database is configured
    try:
        settings = Settings()
        print(f"   Database Host: {settings.DBHOST}")
        print(f"   Database Name: {settings.DBNAME}")
        print(f"   Database User: {settings.DBUSER}")
        print(f"   Password Configured: {'Yes' if settings.DBPASSWORD != '<REPLACE_WITH_ACTUAL_PASSWORD>' else 'No (placeholder)'}")
        
        # Create database manager (won't connect without real password)
        db_manager = DatabaseManager(settings)
        
        print("\n   📊 Data that would be stored:")
        
        for file_data in processing_results['processed_files']:
            db_data = file_data['database_data']
            regression_daily = db_data['regression_daily']
            regression_results = db_data['regression_results']
            
            print(f"\n   📄 File: {Path(file_data['file_path']).name}")
            print(f"      Module: {regression_daily['module_name']}")
            print(f"      Baseline: {regression_daily['baseline_version']}")
            print(f"      Status: {regression_daily['overall_status']}")
            print(f"      Errors to store: {len(regression_results)}")
            
            # Show sample error data
            if regression_results:
                print(f"      Sample error: {regression_results[0]['error_message'][:50]}...")
        
        print(f"\n   📈 Summary:")
        print(f"      Total REGRESSION_DAILY records: {len(processing_results['processed_files'])}")
        print(f"      Total REGRESSION_RESULTS records: {sum(len(f['database_data']['regression_results']) for f in processing_results['processed_files'])}")
        
    except Exception as e:
        print(f"   ❌ Database simulation failed: {e}")

def create_sample_regression_directory():
    """Create a sample directory with V93K files for testing."""
    sample_dir = Path("sample_regression_data")
    sample_dir.mkdir(exist_ok=True)
    
    # Create sample V93K log
    v93k_log = sample_dir / "contact_test_2025_07_21.log"
    with open(v93k_log, 'w') as f:
        f.write("""
# V93K Contact Test Log
# Module: CONTACT_VALIDATION
# Baseline: v3.2.1
# Version: 2.1.0
# Date: 2025-07-21 09:15:30

V93K SMT8 Test Execution Started
Test Suite: CONTACT_REGRESSION_FULL
Device: CONTACT_TEST_DEVICE

Test: CONTACT_RES_LOW - PASSED (0.015 ohms)
Test: CONTACT_RES_HIGH - FAILED (0.085 ohms, limit: 0.080)
Test: CONTACT_OPEN - PASSED
Test: CONTACT_SHORT - PASSED

ERROR: Contact resistance out of specification on pin 12
WARNING: Intermittent connection detected on pin 8

Execution completed in 32.1 seconds
Memory used: 95.2 MB
        """)
    
    # Create sample datalog
    datalog = sample_dir / "contact_measurements.dlog"
    with open(datalog, 'w') as f:
        f.write("""
# Contact Test Datalog
# Module: CONTACT_VALIDATION
# Date: 2025-07-21

Test_Name,Value,Unit,Result,Low_Limit,High_Limit
CONTACT_RES_1,0.015,ohm,PASS,0.010,0.080
CONTACT_RES_2,0.085,ohm,FAIL,0.010,0.080
CONTACT_RES_3,0.022,ohm,PASS,0.010,0.080
OPEN_TEST_1,999.8,kohm,PASS,100.0,9999.0
SHORT_TEST_1,0.002,ohm,PASS,0.000,0.100
        """)
    
    # Create sample build log
    build_log = sample_dir / "build_output.txt"
    with open(build_log, 'w') as f:
        f.write("""
V93K Build System Output
Module: CONTACT_VALIDATION
Baseline: v3.2.1

Building test program...
Compiling contact_tests.cpp... OK
Compiling validation_routines.cpp... OK
Linking... OK

Build completed successfully
Build time: 15.3 seconds
        """)
    
    return sample_dir

def main():
    """Main demonstration function."""
    print("🚀 V93K Parser Integration Demo")
    print("=" * 60)
    
    # Create sample data
    print("📁 Creating sample regression data...")
    sample_dir = create_sample_regression_directory()
    print(f"   ✅ Created sample directory: {sample_dir}")
    
    try:
        # Process the files
        print(f"\n🔄 Processing V93K files in {sample_dir}...")
        results = process_regression_files(str(sample_dir))
        
        # Display results
        print("\n📊 Processing Results:")
        summary = results['processing_summary']
        print(f"   Total files found: {summary['total_files']}")
        print(f"   Successfully processed: {summary['successful']}")
        print(f"   Failed to process: {summary['failed']}")
        print(f"   Success rate: {summary['success_rate']:.1f}%")
        print(f"   Total errors detected: {summary['total_errors']}")
        print(f"   Total warnings detected: {summary['total_warnings']}")
        
        # Show failed files if any
        if results['failed_files']:
            print(f"\n❌ Failed files:")
            for failed in results['failed_files']:
                print(f"   {failed['file_path']}: {failed['errors']}")
        
        # Simulate database storage
        simulate_database_storage(results)
        
        print(f"\n🎉 Integration demo completed successfully!")
        print(f"📝 Next steps:")
        print(f"   1. Update ../.env with real Oracle password")
        print(f"   2. Test database connection with test_oracle_quick.py")
        print(f"   3. Run full integration with real regression data")
        
        return 0
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return 1
    
    finally:
        # Cleanup sample directory
        import shutil
        if sample_dir.exists():
            shutil.rmtree(sample_dir)
            print(f"🧹 Cleaned up sample directory")

if __name__ == "__main__":
    exit(main())
