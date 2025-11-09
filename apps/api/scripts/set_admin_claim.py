#!/usr/bin/env python3
"""
Set Firebase Custom Claims for Admin User
Sets the 'role' custom claim to 'ADMIN' for a Firebase user.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import firebase_admin
    from firebase_admin import credentials, auth
except ImportError:
    print("❌ Error: firebase-admin package not installed")
    print("   Install it with: pip install firebase-admin")
    sys.exit(1)

def set_admin_claim(email: str):
    """Set ADMIN role custom claim for a Firebase user"""
    
    # Initialize Firebase Admin SDK
    # Try to load from environment variable
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    # If not set, try default location
    if not creds_path:
        default_path = os.path.expanduser("~/.config/stepsquad/firebase-service-account.json")
        if os.path.exists(default_path):
            creds_path = default_path
            print(f"ℹ️  Using default location: {default_path}")
    
    if not creds_path:
        print("❌ Error: GOOGLE_APPLICATION_CREDENTIALS not set")
        print("   Set it with: export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json")
        print("   Or ensure the file exists at: ~/.config/stepsquad/firebase-service-account.json")
        sys.exit(1)
    
    if not os.path.exists(creds_path):
        print(f"❌ Error: Service account key file not found: {creds_path}")
        sys.exit(1)
    
    try:
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate(creds_path)
        
        # Check if Firebase app is already initialized
        try:
            firebase_admin.get_app()
        except ValueError:
            # Not initialized, initialize it
            firebase_admin.initialize_app(cred)
        
        # Get user by email
        try:
            user = auth.get_user_by_email(email)
            print(f"✅ Found user: {user.email} (UID: {user.uid})")
        except auth.UserNotFoundError:
            print(f"❌ Error: User with email '{email}' not found")
            print("   Create the user first in Firebase Console → Authentication → Users")
            sys.exit(1)
        
        # Set custom claim
        auth.set_custom_user_claims(user.uid, {'role': 'ADMIN'})
        print(f"✅ Custom claim 'role: ADMIN' set for {email}")
        
        # Verify the claim was set
        user = auth.get_user(user.uid)
        if user.custom_claims and user.custom_claims.get('role') == 'ADMIN':
            print(f"✅ Verified: Custom claim is set correctly")
            print(f"   User: {user.email}")
            print(f"   UID: {user.uid}")
            print(f"   Custom Claims: {user.custom_claims}")
        else:
            print("⚠️  Warning: Custom claim verification failed")
            print(f"   Current claims: {user.custom_claims}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Set Firebase custom claims for admin user')
    parser.add_argument('email', nargs='?', default='admin@stepsquad.club',
                       help='Email address of the user (default: admin@stepsquad.club)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Firebase Custom Claims Setup")
    print("=" * 60)
    print()
    print(f"Setting ADMIN role for: {args.email}")
    print()
    
    set_admin_claim(args.email)
    
    print()
    print("=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print()
    print("The user can now authenticate and will have ADMIN role.")
    print("Note: The user needs to sign out and sign in again for the")
    print("      custom claim to take effect in their ID token.")

if __name__ == "__main__":
    main()

