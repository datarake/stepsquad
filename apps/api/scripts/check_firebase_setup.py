#!/usr/bin/env python3
"""
Firebase Setup Verification Script
Checks if Firebase is properly configured for production use.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_backend_setup():
    """Check backend Firebase configuration"""
    print("🔍 Checking Backend Firebase Configuration...\n")
    
    issues = []
    warnings = []
    
    # Check GCP_ENABLED
    gcp_enabled = os.getenv("GCP_ENABLED", "false").lower() == "true"
    if not gcp_enabled:
        warnings.append("⚠️  GCP_ENABLED=false (using dev mode - Firebase disabled)")
    else:
        print("✅ GCP_ENABLED=true")
    
    # Check Firebase Admin SDK
    try:
        import firebase_admin
        print("✅ firebase-admin package installed")
    except ImportError:
        issues.append("❌ firebase-admin package not installed. Run: pip install firebase-admin")
    
    # Check credentials
    if gcp_enabled:
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if creds_path:
            if os.path.exists(creds_path):
                print(f"✅ GOOGLE_APPLICATION_CREDENTIALS found: {creds_path}")
            else:
                issues.append(f"❌ GOOGLE_APPLICATION_CREDENTIALS path does not exist: {creds_path}")
        else:
            print("ℹ️  GOOGLE_APPLICATION_CREDENTIALS not set (using Application Default Credentials)")
            print("   This is OK for Cloud Run, but you need explicit credentials for local testing")
    
    # Check admin email
    admin_email = os.getenv("ADMIN_EMAIL", "admin@stepsquad.club")
    print(f"✅ ADMIN_EMAIL={admin_email}")
    
    # Check timezone
    comp_tz = os.getenv("COMP_TZ", "Europe/Bucharest")
    print(f"✅ COMP_TZ={comp_tz}")
    
    # Test Firebase initialization
    if gcp_enabled:
        try:
            from firebase_auth import init_firebase
            app = init_firebase()
            if app:
                print("✅ Firebase Admin SDK initialized successfully")
            else:
                warnings.append("⚠️  Firebase Admin SDK initialization returned None (expected in dev mode)")
        except Exception as e:
            issues.append(f"❌ Firebase Admin SDK initialization failed: {e}")
    
    print()
    return issues, warnings

def check_frontend_setup():
    """Check frontend Firebase configuration"""
    print("🔍 Checking Frontend Firebase Configuration...\n")
    
    issues = []
    warnings = []
    
    # Check .env.local file
    env_file = Path(__file__).parent.parent.parent / "web" / ".env.local"
    if env_file.exists():
        print(f"✅ .env.local file found")
        
        # Read and check values
        env_content = env_file.read_text()
        
        use_dev_auth = "VITE_USE_DEV_AUTH=true" in env_content
        if use_dev_auth:
            warnings.append("⚠️  VITE_USE_DEV_AUTH=true (using dev mode - Firebase disabled)")
        else:
            print("✅ VITE_USE_DEV_AUTH=false")
        
        # Check Firebase config
        if not use_dev_auth:
            required_vars = [
                "VITE_FIREBASE_API_KEY",
                "VITE_FIREBASE_AUTH_DOMAIN",
                "VITE_FIREBASE_PROJECT_ID",
                "VITE_FIREBASE_STORAGE_BUCKET",
                "VITE_FIREBASE_MESSAGING_SENDER_ID",
                "VITE_FIREBASE_APP_ID"
            ]
            
            missing_vars = []
            for var in required_vars:
                if var not in env_content or f"{var}=" in env_content and not env_content.split(f"{var}=")[1].split("\n")[0].strip():
                    missing_vars.append(var)
            
            if missing_vars:
                issues.append(f"❌ Missing Firebase configuration variables: {', '.join(missing_vars)}")
            else:
                print("✅ All Firebase configuration variables found")
    else:
        warnings.append("⚠️  .env.local file not found. Create it from .env.example")
    
    print()
    return issues, warnings

def main():
    """Main verification function"""
    print("=" * 60)
    print("StepSquad Firebase Setup Verification")
    print("=" * 60)
    print()
    
    backend_issues, backend_warnings = check_backend_setup()
    frontend_issues, frontend_warnings = check_frontend_setup()
    
    all_issues = backend_issues + frontend_issues
    all_warnings = backend_warnings + frontend_warnings
    
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    if all_issues:
        print(f"\n❌ Found {len(all_issues)} issue(s):")
        for issue in all_issues:
            print(f"  {issue}")
    
    if all_warnings:
        print(f"\n⚠️  Found {len(all_warnings)} warning(s):")
        for warning in all_warnings:
            print(f"  {warning}")
    
    if not all_issues and not all_warnings:
        print("\n✅ All checks passed! Firebase is properly configured.")
    elif not all_issues:
        print("\n✅ Configuration is valid, but there are warnings.")
        print("   The system will work, but check the warnings above.")
    else:
        print("\n❌ Configuration has issues. Please fix them before deploying.")
        sys.exit(1)
    
    print()

if __name__ == "__main__":
    main()

