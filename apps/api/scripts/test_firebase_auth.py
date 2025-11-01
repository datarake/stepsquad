#!/usr/bin/env python3
"""
Test Firebase Authentication Setup
Tests that Firebase authentication is properly configured and working.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_firebase_initialization():
    """Test Firebase Admin SDK initialization"""
    print("=" * 60)
    print("Test 1: Firebase Admin SDK Initialization")
    print("=" * 60)
    
    try:
        from firebase_auth import init_firebase
        app = init_firebase()
        if app:
            print("✅ Firebase Admin SDK initialized successfully")
            print(f"✅ App name: {app.name}")
            return True
        else:
            print("❌ Firebase Admin SDK initialization returned None")
            return False
    except Exception as e:
        print(f"❌ Firebase Admin SDK initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_health_endpoint():
    """Test /health endpoint"""
    print()
    print("=" * 60)
    print("Test 2: Health Endpoint")
    print("=" * 60)
    
    try:
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Health endpoint returned {response.status_code}")
            return False
        
        data = response.json()
        print(f"Response: {data}")
        
        if not data.get("ok"):
            print("❌ Health endpoint returned ok=false")
            return False
        
        if data.get("gcp_enabled") != True:
            print("⚠️  GCP_ENABLED is not true")
            return False
        
        if data.get("firebase_initialized"):
            print("✅ Firebase is initialized")
            return True
        else:
            print("❌ Firebase is not initialized")
            if "firebase_error" in data:
                print(f"Error: {data.get('firebase_error')}")
            return False
            
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_authentication_required():
    """Test that /me endpoint requires authentication"""
    print()
    print("=" * 60)
    print("Test 3: Authentication Enforcement")
    print("=" * 60)
    
    try:
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        response = client.get("/me")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Authentication is required (correct behavior)")
            data = response.json()
            print(f"Response: {data}")
            return True
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            data = response.json()
            print(f"Response: {data}")
            return False
            
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_token_verification():
    """Test Firebase token verification"""
    print()
    print("=" * 60)
    print("Test 4: Token Verification")
    print("=" * 60)
    
    try:
        from firebase_auth import verify_id_token
        
        # Test with invalid token (should fail)
        try:
            verify_id_token("invalid-token")
            print("❌ Invalid token should have been rejected")
            return False
        except ValueError as e:
            print(f"✅ Invalid token correctly rejected: {e}")
            return True
        except Exception as e:
            print(f"✅ Invalid token correctly rejected: {type(e).__name__}: {e}")
            return True
            
    except Exception as e:
        print(f"❌ Token verification test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print()
    print("=" * 60)
    print("Firebase Authentication Test Suite")
    print("=" * 60)
    print()
    
    # Check environment variables
    gcp_enabled = os.getenv("GCP_ENABLED", "false").lower() == "true"
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    print("Environment Check:")
    print(f"  GCP_ENABLED: {gcp_enabled}")
    print(f"  GOOGLE_APPLICATION_CREDENTIALS: {creds_path}")
    print()
    
    if not gcp_enabled:
        print("⚠️  Warning: GCP_ENABLED is not true")
        print("   Set it with: export GCP_ENABLED=true")
        print()
    
    if not creds_path:
        print("⚠️  Warning: GOOGLE_APPLICATION_CREDENTIALS is not set")
        print("   Set it with: export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json")
        print()
    
    # Run tests
    results = []
    results.append(("Firebase Initialization", test_firebase_initialization()))
    results.append(("Health Endpoint", test_health_endpoint()))
    results.append(("Authentication Enforcement", test_authentication_required()))
    results.append(("Token Verification", test_token_verification()))
    
    # Print summary
    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print()
    print(f"Total: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print()
        print("=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        print()
        print("Firebase authentication is properly configured and working.")
        print("You can now test the full authentication flow:")
        print("  1. Start backend: uvicorn main:app --host 0.0.0.0 --port 8080")
        print("  2. Start frontend: cd ../web && pnpm dev")
        print("  3. Sign in at http://localhost:5174")
        return 0
    else:
        print()
        print("=" * 60)
        print("❌ Some tests failed")
        print("=" * 60)
        print()
        print("Please check the errors above and fix the issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

