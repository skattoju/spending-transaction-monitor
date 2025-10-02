#!/usr/bin/env python3
"""
Simple Integration Validation Test for CategoryNormalizer
Tests the integration points without requiring full database setup
"""

import sys
import os
import inspect

# Add the proper paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "packages", "api", "src"))


def test_import_integration():
    """Test that all integration imports work correctly"""
    print("🧪 Testing Import Integration...")
    
    import_tests = [
        ("Transaction routes", "routes.transactions", "CategoryNormalizer"),
        ("Alert routes", "routes.alerts", "CategoryNormalizer"),
        ("Alert validation", "services.alerts.agents.create_alert_rule", "CategoryNormalizer"),
    ]
    
    all_passed = True
    for test_name, module_name, import_name in import_tests:
        try:
            module = __import__(module_name, fromlist=[import_name])
            getattr(module, import_name)
            print(f"  ✅ {test_name}: {import_name} imported successfully")
        except Exception as e:
            all_passed = False
            print(f"  ❌ {test_name}: Failed to import {import_name} - {e}")
    
    return all_passed


def test_function_signatures():
    """Test that function signatures are correct"""
    print("\n🧪 Testing Function Signatures...")
    
    try:
        # Test create_alert_rule function signature
        from services.alerts.agents.create_alert_rule import create_alert_rule
        
        sig = inspect.signature(create_alert_rule)
        params = list(sig.parameters.keys())
        expected_params = ['alert_text', 'user_id', 'session']
        
        if params == expected_params:
            print(f"  ✅ create_alert_rule signature: {params}")
            return True
        else:
            print(f"  ❌ create_alert_rule signature: Expected {expected_params}, got {params}")
            return False
            
    except Exception as e:
        print(f"  ❌ Function signature test failed: {e}")
        return False


def test_graph_state_updates():
    """Test that graph states include session parameter"""
    print("\n🧪 Testing Graph State Updates...")
    
    try:
        # Test ValidationState
        from services.alerts.validate_rule_graph import ValidationState
        validation_state = ValidationState()
        
        has_session = 'session' in validation_state
        print(f"  {'✅' if has_session else '❌'} ValidationState includes session: {has_session}")
        
        # Test AppState in parse_alert_graph
        from services.alerts.parse_alert_graph import AppState
        app_state = AppState()
        
        has_session_parse = 'session' in app_state
        print(f"  {'✅' if has_session_parse else '❌'} AppState (parse) includes session: {has_session_parse}")
        
        # Test AppState in generate_alert_graph
        from services.alerts.generate_alert_graph import AppState as GenerateAppState
        generate_app_state = GenerateAppState()
        
        has_session_generate = 'session' in generate_app_state
        print(f"  {'✅' if has_session_generate else '❌'} AppState (generate) includes session: {has_session_generate}")
        
        return has_session and has_session_parse and has_session_generate
        
    except Exception as e:
        print(f"  ❌ Graph state test failed: {e}")
        return False


def test_code_integration():
    """Test that the integration code is present in the files"""
    print("\n🧪 Testing Code Integration...")
    
    # Test transaction creation integration
    try:
        with open("packages/api/src/routes/transactions.py", "r") as f:
            transaction_content = f.read()
        
        has_import = "from ..services.category_normalizer import CategoryNormalizer" in transaction_content
        has_normalization = "CategoryNormalizer.normalize(session, payload.merchant_category)" in transaction_content
        has_normalized_usage = "merchant_category=normalized_category" in transaction_content
        
        print(f"  {'✅' if has_import else '❌'} Transaction routes: CategoryNormalizer import")
        print(f"  {'✅' if has_normalization else '❌'} Transaction routes: Category normalization call")
        print(f"  {'✅' if has_normalized_usage else '❌'} Transaction routes: Normalized category usage")
        
        transaction_passed = has_import and has_normalization and has_normalized_usage
        
    except Exception as e:
        print(f"  ❌ Transaction integration test failed: {e}")
        transaction_passed = False
    
    # Test alert rule creation integration
    try:
        with open("packages/api/src/routes/alerts.py", "r") as f:
            alert_content = f.read()
        
        has_import = "from ..services.category_normalizer import CategoryNormalizer" in alert_content
        has_normalization = "CategoryNormalizer.normalize(session, normalized_merchant_category)" in alert_content
        has_normalized_usage = "merchant_category=normalized_merchant_category" in alert_content
        
        print(f"  {'✅' if has_import else '❌'} Alert routes: CategoryNormalizer import")
        print(f"  {'✅' if has_normalization else '❌'} Alert routes: Category normalization call")
        print(f"  {'✅' if has_normalized_usage else '❌'} Alert routes: Normalized category usage")
        
        alert_passed = has_import and has_normalization and has_normalized_usage
        
    except Exception as e:
        print(f"  ❌ Alert integration test failed: {e}")
        alert_passed = False
    
    # Test alert rule validation integration
    try:
        with open("packages/api/src/services/alerts/agents/create_alert_rule.py", "r") as f:
            validation_content = f.read()
        
        has_import = "from ...category_normalizer import CategoryNormalizer" in validation_content
        has_async = "async def create_alert_rule(alert_text: str, user_id: str, session: AsyncSession)" in validation_content
        has_normalization = "CategoryNormalizer.normalize(session, merchant_category)" in validation_content
        
        print(f"  {'✅' if has_import else '❌'} Alert validation: CategoryNormalizer import")
        print(f"  {'✅' if has_async else '❌'} Alert validation: Async function signature")
        print(f"  {'✅' if has_normalization else '❌'} Alert validation: Category normalization call")
        
        validation_passed = has_import and has_async and has_normalization
        
    except Exception as e:
        print(f"  ❌ Alert validation integration test failed: {e}")
        validation_passed = False
    
    return transaction_passed and alert_passed and validation_passed


def main():
    """Run all validation tests"""
    print("🚀 CategoryNormalizer Integration Validation")
    print("=" * 50)
    
    tests = [
        ("Import Integration", test_import_integration),
        ("Function Signatures", test_function_signatures),
        ("Graph State Updates", test_graph_state_updates),
        ("Code Integration", test_code_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    passed_tests = sum(1 for _, result in results if result)
    total_tests = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL VALIDATION TESTS PASSED!")
        print("\n✅ CategoryNormalizer Integration Status:")
        print("  • Import integration: ✅ Working")
        print("  • Function signatures: ✅ Correct")
        print("  • Graph state updates: ✅ Complete")
        print("  • Code integration: ✅ Implemented")
        print("\n🚀 The implementation is ready for testing with database!")
        print("\n📋 Next Steps:")
        print("  1. Set up database: pnpm db:start")
        print("  2. Run migrations: pnpm upgrade")
        print("  3. Seed category data: pnpm seed:categories")
        print("  4. Populate embeddings: pnpm populate:embeddings")
        print("  5. Test with real data")
        return True
    else:
        print(f"\n❌ {total_tests - passed_tests} validation tests failed.")
        print("Check the detailed results above for specific issues.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
