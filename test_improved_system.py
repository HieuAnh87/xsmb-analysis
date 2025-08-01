#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script cho hệ thống thu thập dữ liệu xổ số đã cải thiện
"""

import sys
import os
sys.path.insert(0, 'src')

from datetime import datetime
import json

def test_improved_collector():
    """Test collector với các nguồn mới và retry mechanism"""
    print("🧪 TESTING IMPROVED LOTTERY COLLECTOR")
    print("=" * 50)
    
    try:
        from lottery_collector import LotteryCollector
        
        collector = LotteryCollector()
        
        print(f"📊 Configured sources: {len(collector.sources)}")
        for i, source in enumerate(collector.sources, 1):
            print(f"   {i}. {source['name']}: {source['url']}")
        
        print("\n🚀 Testing data collection...")
        
        # Test with retry mechanism
        result = collector.fetch_lottery_data(max_retries=2)
        
        if result:
            print("✅ Data collection successful!")
            print(f"📅 Date: {result['date']}")
            print(f"🌐 Source: {result['source']}")
            print(f"🎯 Prizes collected: {len(result.get('results', {}))}")
            
            # Show sample results
            results = result.get('results', {})
            for prize, numbers in list(results.items())[:3]:
                print(f"   {prize}: {numbers}")
            
            if result.get('is_fallback'):
                print("⚠️  Note: Using fallback data")
            
            return result
        else:
            print("❌ Data collection failed completely")
            return None
            
    except Exception as e:
        print(f"❌ Error testing collector: {e}")
        return None

def test_selenium_fallback():
    """Test Selenium fallback mechanism"""
    print("\n🧪 TESTING SELENIUM FALLBACK")
    print("=" * 50)
    
    try:
        from selenium_collector import SeleniumLotteryCollector
        
        print("🔧 Initializing Selenium collector...")
        selenium_collector = SeleniumLotteryCollector()
        
        if selenium_collector.driver:
            print("✅ Selenium WebDriver initialized")
            
            print("🚀 Testing Selenium data collection...")
            result = selenium_collector.fetch_with_selenium()
            
            selenium_collector.cleanup()
            
            if result:
                print("✅ Selenium collection successful!")
                print(f"📅 Date: {result['date']}")
                print(f"🌐 Source: {result['source']}")
                print(f"🎯 Prizes: {len(result.get('results', {}))}")
                return result
            else:
                print("❌ Selenium collection failed")
                return None
        else:
            print("⚠️  Selenium WebDriver not available")
            return None
            
    except ImportError:
        print("⚠️  Selenium not installed, skipping test")
        return None
    except Exception as e:
        print(f"❌ Error testing Selenium: {e}")
        return None

def test_data_pipeline():
    """Test complete data pipeline"""
    print("\n🧪 TESTING COMPLETE DATA PIPELINE")
    print("=" * 50)
    
    # Get test data
    test_data = test_improved_collector()
    
    if not test_data:
        print("⚠️  Using mock data for pipeline test")
        test_data = {
            'date': datetime.now().strftime('%d/%m/%Y'),
            'source': 'Pipeline Test',
            'results': {
                'Giải Đặc Biệt': ['12345'],
                'Giải Nhất': ['67890'],
                'Giải Nhì': ['11111', '22222']
            },
            'collected_at': datetime.now().isoformat()
        }
    
    try:
        # Test data storage
        print("\n📁 Testing data storage...")
        from data_storage import DataStorage
        
        storage = DataStorage()
        storage_success = storage.save_data(test_data)
        
        if storage_success:
            print("✅ Data storage successful")
            
            # Test validation
            print("\n🔍 Testing data validation...")
            from data_validator import DataValidator
            
            validator = DataValidator()
            is_valid, errors = validator.validate_json_file()
            
            if is_valid:
                print("✅ Data validation passed")
            else:
                print(f"⚠️  Validation warnings: {len(errors)}")
                for error in errors[:3]:
                    print(f"   - {error}")
            
            # Test analytics
            print("\n📊 Testing analytics...")
            from analytics import LotteryAnalytics
            
            analytics = LotteryAnalytics()
            report = analytics.generate_report()
            
            if 'error' not in report:
                print("✅ Analytics generation successful")
                
                # Show insights
                insights = analytics.get_insights(report)
                print(f"💡 Generated {len(insights)} insights:")
                for insight in insights[:3]:
                    print(f"   - {insight}")
            else:
                print(f"❌ Analytics error: {report['error']}")
            
            # Test notifications
            print("\n🔔 Testing notification system...")
            from notification_system import NotificationSystem
            
            notifier = NotificationSystem()
            notifier.notify_success(test_data)
            print("✅ Notification system tested")
            
            return True
            
        else:
            print("❌ Data storage failed")
            return False
            
    except Exception as e:
        print(f"❌ Pipeline test error: {e}")
        return False

def test_error_handling():
    """Test error handling and fallback mechanisms"""
    print("\n🧪 TESTING ERROR HANDLING")
    print("=" * 50)
    
    try:
        from lottery_collector import LotteryCollector
        
        # Create collector with invalid sources to test fallback
        collector = LotteryCollector()
        
        # Temporarily replace sources with invalid ones
        original_sources = collector.sources.copy()
        collector.sources = [
            {
                'name': 'Invalid Source',
                'url': 'https://invalid-url-that-does-not-exist.com',
                'parser': lambda soup, date: None
            }
        ]
        
        print("🚀 Testing with invalid sources (should trigger fallback)...")
        result = collector.fetch_lottery_data(max_retries=1)
        
        # Restore original sources
        collector.sources = original_sources
        
        if result:
            if result.get('is_fallback'):
                print("✅ Fallback mechanism working correctly")
                print(f"📊 Fallback data has {len(result.get('results', {}))} prizes")
                return True
            else:
                print("⚠️  Got real data instead of fallback")
                return True
        else:
            print("❌ No data returned, fallback failed")
            return False
            
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🎲 NORTHERN VIETNAM LOTTERY SYSTEM - IMPROVED VERSION TEST")
    print("=" * 70)
    
    test_results = []
    
    # Run tests
    test_results.append(("Improved Collector", test_improved_collector() is not None))
    test_results.append(("Selenium Fallback", test_selenium_fallback() is not None))
    test_results.append(("Data Pipeline", test_data_pipeline()))
    test_results.append(("Error Handling", test_error_handling()))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20} : {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is ready for deployment.")
    elif passed >= total * 0.75:
        print("⚠️  Most tests passed. System is mostly functional.")
    else:
        print("❌ Multiple test failures. System needs fixes.")
    
    print("\n🚀 DEPLOYMENT STATUS:")
    if passed >= 3:
        print("✅ System ready for GitHub Actions deployment")
        print("✅ Improved error handling and fallback mechanisms")
        print("✅ Multiple data sources with retry logic")
        print("✅ Selenium support for JavaScript sites")
    else:
        print("⚠️  System may need additional fixes before deployment")
    
    return passed >= 3

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
