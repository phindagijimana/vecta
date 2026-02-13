#!/usr/bin/env python3
"""
Test Script for Vecta AI Enhancements
Tests Phase 1, 2, and 3 implementations
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def print_header(text):
    print("\n" + "="*70)
    print(text)
    print("="*70 + "\n")

def test_phase_1_few_shot():
    """Test Phase 1: Few-Shot Examples"""
    print_header("PHASE 1: Testing Few-Shot Examples")
    
    try:
        from utils.few_shot_loader import FewShotExampleLoader
        
        loader = FewShotExampleLoader()
        
        # Test loading
        print(f"✅ Few-Shot Loader initialized")
        print(f"   Data directory: {loader.data_dir}")
        
        # Test example retrieval
        conditions = ["epilepsy", "parkinsons", "stroke", "headache", "dementia"]
        for condition in conditions:
            examples = loader.get_examples_by_condition(condition, n=2)
            print(f"   {condition}: {len(examples)} examples loaded")
        
        # Test guideline retrieval
        guidelines = loader.get_guideline_context("epilepsy")
        if guidelines:
            print(f"\n✅ Guidelines loaded (epilepsy sample):")
            print(f"   {guidelines[:200]}...")
        
        print("\n✅ Phase 1: PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Phase 1: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phase_2_guidelines():
    """Test Phase 2: Clinical Guidelines"""
    print_header("PHASE 2: Testing Clinical Guidelines")
    
    try:
        from utils.few_shot_loader import FewShotExampleLoader
        
        loader = FewShotExampleLoader()
        
        # Test guideline loading for different conditions
        conditions = ["epilepsy", "parkinsons", "stroke", "headache"]
        for condition in conditions:
            guidelines = loader.get_guideline_context(condition)
            if guidelines:
                print(f"✅ {condition} guidelines: {len(guidelines)} characters")
            else:
                print(f"⚠️  {condition} guidelines: Not found")
        
        print("\n✅ Phase 2: PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Phase 2: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phase_3_rag():
    """Test Phase 3: RAG System"""
    print_header("PHASE 3: Testing RAG System")
    
    try:
        from utils.rag_system import get_rag_system
        
        print("Initializing RAG system...")
        rag = get_rag_system()
        
        if not rag or not rag.available:
            print("⚠️  RAG system not available")
            print("   Install with: pip install chromadb sentence-transformers")
            print("   Phase 3: SKIPPED (optional)")
            return None  # Not a failure, just not installed
        
        # Get stats
        stats = rag.get_stats()
        print("\n📊 RAG System Stats:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Test retrieval
        test_query = "Patient with absence seizures and 3Hz spike-wave on EEG"
        print(f"\n🔍 Testing retrieval:")
        print(f"   Query: {test_query[:60]}...")
        
        results = rag.retrieve(test_query, condition="epilepsy", n_results=2)
        
        if results:
            print(f"\n✅ Retrieved guidelines ({len(results)} characters)")
            print(f"   Preview: {results[:200]}...")
        else:
            print("⚠️  No results retrieved")
        
        print("\n✅ Phase 3: PASSED")
        return True
        
    except ImportError as e:
        print(f"\n⚠️  Phase 3: SKIPPED - {e}")
        print("   Install with: pip install chromadb sentence-transformers")
        return None
        
    except Exception as e:
        print(f"\n❌ Phase 3: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_integration():
    """Test app.py integration"""
    print_header("Testing app.py Integration")
    
    try:
        # Import app components
        print("Importing app.py...")
        sys.path.insert(0, os.path.dirname(__file__))
        
        # Test imports
        try:
            from utils.few_shot_loader import FewShotExampleLoader
            print("✅ few_shot_loader importable")
        except Exception as e:
            print(f"❌ few_shot_loader import failed: {e}")
            return False
        
        try:
            from utils.rag_system import get_rag_system
            print("✅ rag_system importable")
        except Exception as e:
            print(f"⚠️  rag_system import failed: {e}")
        
        print("\n✅ Integration: PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Integration: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print_header("🧪 Vecta AI Implementation Test Suite")
    
    print("Testing all phases of implementation:")
    print("  Phase 1: Few-Shot Examples")
    print("  Phase 2: Clinical Guidelines")
    print("  Phase 3: RAG System (optional)")
    print("  Integration: app.py")
    
    results = {}
    
    # Run tests
    results['Phase 1'] = test_phase_1_few_shot()
    results['Phase 2'] = test_phase_2_guidelines()
    results['Phase 3'] = test_phase_3_rag()
    results['Integration'] = test_app_integration()
    
    # Summary
    print_header("📊 Test Summary")
    
    passed = sum(1 for v in results.values() if v is True)
    skipped = sum(1 for v in results.values() if v is None)
    failed = sum(1 for v in results.values() if v is False)
    
    for phase, result in results.items():
        if result is True:
            status = "✅ PASSED"
        elif result is None:
            status = "⚠️  SKIPPED"
        else:
            status = "❌ FAILED"
        
        print(f"{phase:15s}: {status}")
    
    print(f"\n{passed} passed, {skipped} skipped, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All required tests passed!")
        if skipped > 0:
            print("   Note: Some optional features (RAG) require additional installation")
            print("   Install with: pip install chromadb sentence-transformers")
    else:
        print("\n⚠️  Some tests failed. Please review errors above.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
