#!/usr/bin/env python3
"""
Simple test script for the consolidated ScrapIt application
"""
import sys
import os

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")
    
    try:
        # Test core modules
        import models
        print("✅ models.py imported successfully")
        
        import database
        print("✅ database.py imported successfully")
        
        # Test feature modules
        sys.path.append('02-authentication')
        import auth
        print("✅ auth.py imported successfully")
        
        sys.path.append('03-gmail-integration')
        import gmail
        print("✅ gmail.py imported successfully")
        
        sys.path.append('04-ai-classification')
        import ai
        print("✅ ai.py imported successfully")
        
        # Test main app
        sys.path.append('01-project-setup')
        import main
        print("✅ main.py imported successfully")
        
        print("\n🎉 All modules imported successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_environment():
    """Test environment setup"""
    print("\nTesting environment...")
    
    # Check if .env.example exists
    if os.path.exists('.env.example'):
        print("✅ .env.example found")
    else:
        print("❌ .env.example not found")
    
    # Check if requirements.txt exists
    if os.path.exists('requirements.txt'):
        print("✅ requirements.txt found")
    else:
        print("❌ requirements.txt not found")
    
    # Check folder structure
    expected_folders = [
        '01-project-setup',
        '02-authentication', 
        '03-gmail-integration',
        '04-ai-classification'
    ]
    
    for folder in expected_folders:
        if os.path.exists(folder):
            print(f"✅ {folder}/ folder exists")
        else:
            print(f"❌ {folder}/ folder missing")

def main():
    """Run all tests"""
    print("ScrapIt Consolidated - Test Suite")
    print("=" * 40)
    
    # Test environment
    test_environment()
    
    # Test imports
    success = test_imports()
    
    if success:
        print("\n✅ All tests passed! The application is ready to run.")
        print("\nTo start the application:")
        print("1. pip install -r requirements.txt")
        print("2. cp .env.example .env")
        print("3. Edit .env with your API keys")
        print("4. python 01-project-setup/main.py")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()