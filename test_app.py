"""
Simple test to verify the Office Desk Booking System works correctly
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import pandas
        import flask
        import openpyxl
        import holidays
        print("✅ All dependencies imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_app_creation():
    """Test that the Flask app can be created"""
    print("Testing Flask app creation...")
    try:
        import app
        assert app.app is not None
        print("✅ Flask app created successfully")
        return True
    except Exception as e:
        print(f"❌ App creation error: {e}")
        return False

def test_excel_initialization():
    """Test that Excel file can be initialized"""
    print("Testing Excel initialization...")
    try:
        import app
        # Clean up test file if it exists
        test_file = 'test_office_seating.xlsx'
        if os.path.exists(test_file):
            os.remove(test_file)
        
        # Test init
        app.EXCEL_FILE = test_file
        app.init_excel()
        
        assert os.path.exists(test_file)
        print("✅ Excel file initialized successfully")
        
        # Cleanup
        os.remove(test_file)
        return True
    except Exception as e:
        print(f"❌ Excel initialization error: {e}")
        return False

def run_tests():
    """Run all tests"""
    print("=" * 50)
    print("Office Desk Booking System - Test Suite")
    print("=" * 50)
    print()
    
    tests = [
        test_imports,
        test_app_creation,
        test_excel_initialization
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()
    
    print("=" * 50)
    if all(results):
        print("✅ All tests passed!")
        print("=" * 50)
        return True
    else:
        print("❌ Some tests failed")
        print("=" * 50)
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
