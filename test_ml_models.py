#!/usr/bin/env python3
"""
Test Script for Machine Learning Models
Tests the issue classifier and solution recommender with sample data
"""

import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from models.issue_classifier import IssueClassifier, IssueCategory, create_synthetic_training_data
from models.solution_recommender import SolutionRecommender, Solution, RecommendationResult

def test_issue_classifier():
    """Test the issue classification model."""
    print("🧪 Testing Issue Classifier...")
    
    try:
        # Create classifier
        classifier = IssueClassifier()
        print("   ✅ Classifier created successfully")
        
        # Test rule-based classification (before training)
        test_messages = [
            "Compilation error: undefined symbol 'test_function'",
            "Contact failure detected on pin 5",
            "Test execution timeout after 300 seconds",
            "Device not responding to commands",
            "File not found: test_data.dat"
        ]
        
        print("   🔍 Testing rule-based classification:")
        for message in test_messages:
            result = classifier.classify_issue(message)
            print(f"      '{message[:40]}...' → {result.category.value} ({result.confidence:.2f})")
        
        # Test with synthetic training data
        print("   📚 Training with synthetic data...")
        training_data = create_synthetic_training_data()
        print(f"      Training examples: {len(training_data)}")
        
        # Train the model
        training_results = classifier.train_model(training_data)
        print(f"   ✅ Training completed!")
        print(f"      RF Accuracy: {training_results['rf_accuracy']:.3f}")
        print(f"      NB Accuracy: {training_results['nb_accuracy']:.3f}")
        print(f"      Ensemble Accuracy: {training_results['ensemble_accuracy']:.3f}")
        print(f"      Features: {training_results['feature_count']}")
        print(f"      Classes: {training_results['class_count']}")
        
        # Test ML classification
        print("   🤖 Testing ML-based classification:")
        for message in test_messages:
            result = classifier.classify_issue(message)
            print(f"      '{message[:40]}...' → {result.category.value} ({result.confidence:.2f})")
            if result.features_used:
                print(f"         Features: {', '.join(result.features_used[:3])}")
        
        # Test model persistence
        model_path = "test_classifier_model.joblib"
        classifier.save_model(model_path)
        print(f"   💾 Model saved to {model_path}")
        
        # Load model and test
        new_classifier = IssueClassifier(model_path)
        test_result = new_classifier.classify_issue("Contact resistance out of specification")
        print(f"   📥 Loaded model test: {test_result.category.value} ({test_result.confidence:.2f})")
        
        # Cleanup
        Path(model_path).unlink()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_solution_recommender():
    """Test the solution recommendation system."""
    print("\n🧪 Testing Solution Recommender...")
    
    try:
        # Create recommender
        recommender = SolutionRecommender()
        print("   ✅ Recommender created successfully")
        
        # Create sample solutions
        solutions = [
            Solution(
                solution_id="sol_001",
                solution_type="code_fix",
                description="Fix undefined symbol by adding missing header include",
                code_changes=[{"file": "test.cpp", "change": "#include <iostream>"}],
                category=IssueCategory.COMPILATION_ERROR,
                module_applicability=["CONTACT_TEST"],
                success_count=5,
                failure_count=1
            ),
            Solution(
                solution_id="sol_002", 
                solution_type="parameter_update",
                description="Increase contact force to resolve contact failure",
                parameter_changes=[{"parameter": "contact_force", "value": "150mN"}],
                category=IssueCategory.CONTACT_FAILURE,
                module_applicability=["CONTACT_TEST", "CONTACT_VALIDATION"],
                success_count=8,
                failure_count=0
            ),
            Solution(
                solution_id="sol_003",
                solution_type="config_change", 
                description="Increase timeout value for slow tests",
                config_changes=[{"setting": "test_timeout", "value": "600"}],
                category=IssueCategory.TIMEOUT,
                module_applicability=["ALL"],
                success_count=3,
                failure_count=2
            )
        ]
        
        # Add solutions to recommender
        for solution in solutions:
            solution.update_success_metrics(True)  # Update confidence scores
            recommender.add_solution(solution)
        
        print(f"   📝 Added {len(solutions)} solutions to knowledge base")
        
        # Test recommendations
        test_cases = [
            ("Compilation error: undefined symbol 'test_function'", IssueCategory.COMPILATION_ERROR),
            ("Contact failure detected on pin 5", IssueCategory.CONTACT_FAILURE),
            ("Test execution timeout after 300 seconds", IssueCategory.TIMEOUT),
            ("Device not responding to commands", IssueCategory.DEVICE_ERROR)
        ]
        
        print("   🎯 Testing recommendations:")
        for error_message, category in test_cases:
            context = {"module_name": "CONTACT_TEST", "baseline_version": "v2.1.0"}
            recommendation = recommender.recommend_solutions(error_message, category, context)
            
            print(f"      Error: '{error_message[:40]}...'")
            print(f"      Category: {category.value}")
            print(f"      Recommendations: {len(recommendation.solutions)}")
            print(f"      Confidence: {recommendation.recommendation_confidence:.2f}")
            
            if recommendation.solutions:
                top_solution, score = recommendation.solutions[0]
                print(f"      Top solution: {top_solution.description[:50]}... (score: {score:.2f})")
                
                # Test auto-applicable solutions
                auto_solutions = recommendation.get_auto_applicable_solutions(min_confidence=0.7)
                print(f"      Auto-applicable: {len(auto_solutions)}")
            
            print()
        
        # Test solution application recording
        print("   📊 Testing solution application recording:")
        recommender.record_solution_application("sol_002", "Contact failure on pin 12", True, {"module": "CONTACT_TEST"})
        recommender.record_solution_application("sol_003", "Timeout during long test", False, {"module": "SCAN_TEST"})
        
        # Get statistics
        stats = recommender.get_statistics()
        print(f"      Total solutions: {stats['total_solutions']}")
        print(f"      Total applications: {stats['total_applications']}")
        print(f"      Success rate: {stats['overall_success_rate']:.2%}")
        print(f"      Category distribution: {stats['category_distribution']}")
        
        # Test knowledge base persistence
        kb_path = "test_knowledge_base.json"
        recommender.save_knowledge_base(kb_path)
        print(f"   💾 Knowledge base saved to {kb_path}")
        
        # Load and test
        new_recommender = SolutionRecommender(kb_path)
        test_recommendation = new_recommender.recommend_solutions(
            "Contact resistance too high", 
            IssueCategory.CONTACT_FAILURE
        )
        print(f"   📥 Loaded KB test: {len(test_recommendation.solutions)} recommendations")
        
        # Cleanup
        Path(kb_path).unlink()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    """Test integration between classifier and recommender."""
    print("\n🧪 Testing Classifier-Recommender Integration...")
    
    try:
        # Create and train classifier
        classifier = IssueClassifier()
        training_data = create_synthetic_training_data()
        classifier.train_model(training_data)
        
        # Create recommender with solutions
        recommender = SolutionRecommender()
        
        # Add some solutions
        solutions = [
            Solution("fix_001", "code_fix", "Add missing include statement", 
                    category=IssueCategory.COMPILATION_ERROR, success_count=5),
            Solution("fix_002", "parameter_update", "Adjust contact force", 
                    category=IssueCategory.CONTACT_FAILURE, success_count=3),
            Solution("fix_003", "config_change", "Increase timeout", 
                    category=IssueCategory.TIMEOUT, success_count=4)
        ]
        
        for solution in solutions:
            solution.update_success_metrics(True)
            recommender.add_solution(solution)
        
        # Test end-to-end workflow
        test_error = "Contact failure detected on pin 8 during resistance test"
        
        print(f"   🔄 Processing error: '{test_error}'")
        
        # Step 1: Classify the issue
        classification = classifier.classify_issue(test_error)
        print(f"      Classification: {classification.category.value} ({classification.confidence:.2f})")
        
        # Step 2: Get recommendations
        recommendation = recommender.recommend_solutions(
            test_error, 
            classification.category,
            {"module_name": "CONTACT_TEST"}
        )
        print(f"      Recommendations: {len(recommendation.solutions)}")
        print(f"      Recommendation confidence: {recommendation.recommendation_confidence:.2f}")
        
        if recommendation.solutions:
            top_solution, score = recommendation.solutions[0]
            print(f"      Top solution: {top_solution.description}")
            print(f"      Solution confidence: {top_solution.confidence_score:.2f}")
            
            # Check if solution is auto-applicable
            auto_solutions = recommendation.get_auto_applicable_solutions()
            if auto_solutions:
                print(f"      ✅ {len(auto_solutions)} solutions are auto-applicable")
            else:
                print(f"      ⚠️  No solutions meet auto-application threshold")
        
        print("   ✅ Integration test completed successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all ML model tests."""
    print("🚀 Machine Learning Models Test Suite")
    print("=" * 60)
    
    tests = [
        test_issue_classifier,
        test_solution_recommender,
        test_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All ML model tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())
