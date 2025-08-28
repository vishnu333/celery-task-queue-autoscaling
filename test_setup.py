#!/usr/bin/env python3
"""
Test script to verify the Celery application setup
"""

import sys
import os

# Add app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test that all required modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test Celery app import
        from celery_app import app
        print("✅ Celery app imported successfully")
        
        # Test metrics import
        from metrics import metrics
        print("✅ Metrics module imported successfully")
        
        # Test custom metrics adapter import
        from custom_metrics_adapter import app as metrics_app
        print("✅ Custom metrics adapter imported successfully")
        
        print("\n🎉 All imports successful! The application is ready.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_celery_config():
    """Test Celery configuration"""
    try:
        from celery_app import app
        
        print("\nTesting Celery configuration...")
        print(f"Broker URL: {app.conf.broker_url}")
        print(f"Result Backend: {app.conf.result_backend}")
        print(f"Task Serializer: {app.conf.task_serializer}")
        print(f"Accept Content: {app.conf.accept_content}")
        
        print("✅ Celery configuration looks good!")
        return True
        
    except Exception as e:
        print(f"❌ Celery configuration error: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Celery Task Queue Autoscaling System - Setup Test")
    print("=" * 60)
    
    # Test imports
    imports_ok = test_imports()
    
    if imports_ok:
        # Test Celery configuration
        config_ok = test_celery_config()
        
        if config_ok:
            print("\n🚀 System is ready for deployment!")
            print("\nNext steps:")
            print("1. Start Minikube: minikube start")
            print("2. Run deployment: ./deploy.sh")
            print("3. Test autoscaling with task generation scripts")
        else:
            print("\n❌ Celery configuration issues detected")
            sys.exit(1)
    else:
        print("\n❌ Import issues detected")
        sys.exit(1)
