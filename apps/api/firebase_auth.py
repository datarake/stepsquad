"""
Firebase Authentication Module
Handles Firebase ID token verification for production authentication
"""
import os
import logging
from typing import Optional, Dict
import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin.exceptions import FirebaseError

# Initialize Firebase Admin SDK (lazy initialization)
_firebase_app: Optional[firebase_admin.App] = None

def init_firebase():
    """Initialize Firebase Admin SDK"""
    global _firebase_app
    
    if _firebase_app is not None:
        return _firebase_app
    
    GCP_ENABLED = os.getenv("GCP_ENABLED", "false").lower() == "true"
    if not GCP_ENABLED:
        logging.info("Firebase Admin SDK not initialized (GCP_ENABLED=false)")
        return None
    
    # Check if Firebase is already initialized (might have been initialized elsewhere)
    try:
        apps = firebase_admin._apps
        if apps:
            # Use the existing app
            _firebase_app = list(apps.values())[0]
            logging.info("Firebase Admin SDK already initialized, reusing existing app")
            return _firebase_app
    except Exception:
        pass
    
    try:
        # Try to use Application Default Credentials (for Cloud Run, GKE, etc.)
        # This will use the service account attached to the environment
        # Explicitly set project ID to match Firebase project
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT_ID") or "stepsquad-46d14"
        
        logging.info(f"Attempting to initialize Firebase Admin SDK with project: {project_id}")
        
        # Try to initialize with ADC
        try:
            # Initialize with explicit project ID to ensure it matches Firebase project
            _firebase_app = firebase_admin.initialize_app(options={'projectId': project_id})
            
            # Verify the project ID matches
            if _firebase_app.project_id != project_id:
                logging.warning(
                    f"Firebase app project ID ({_firebase_app.project_id}) doesn't match expected ({project_id}). "
                    "This may cause token verification issues."
                )
            
            logging.info(f"Firebase Admin SDK initialized with Application Default Credentials (project: {_firebase_app.project_id})")
            return _firebase_app
        except ValueError as e:
            # If app already exists, get it
            if "already exists" in str(e).lower():
                _firebase_app = firebase_admin.get_app()
                logging.info(f"Firebase Admin SDK already initialized, retrieved existing app (project: {_firebase_app.project_id})")
                
                # Verify project ID matches
                if _firebase_app.project_id != project_id:
                    logging.warning(
                        f"Existing Firebase app project ID ({_firebase_app.project_id}) doesn't match expected ({project_id}). "
                        "This may cause token verification issues."
                    )
                
                return _firebase_app
            logging.error(f"Firebase initialization ValueError: {e}", exc_info=True)
            raise
        except Exception as e:
            logging.error(f"Failed to initialize Firebase with ADC: {e}", exc_info=True)
            raise
    except Exception as e:
        logging.warning(f"Failed to initialize Firebase with ADC: {e}", exc_info=True)
        # Fallback: try using explicit credentials file
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if creds_path:
            # Check if it's a file path or secret reference
            if os.path.exists(creds_path):
                try:
                    cred = credentials.Certificate(creds_path)
                    _firebase_app = firebase_admin.initialize_app(cred)
                    logging.info(f"Firebase Admin SDK initialized with credentials from {creds_path}")
                    return _firebase_app
                except ValueError as e2:
                    # If app already exists, get it
                    if "already exists" in str(e2).lower():
                        _firebase_app = firebase_admin.get_app()
                        logging.info("Firebase Admin SDK already initialized, retrieved existing app")
                        return _firebase_app
                    logging.error(f"Failed to initialize Firebase with credentials file: {e2}", exc_info=True)
                    raise
                except Exception as e2:
                    logging.error(f"Failed to initialize Firebase with credentials file: {e2}", exc_info=True)
                    raise
            else:
                # Might be a secret reference, try to read from mounted path
                # In Cloud Run, secrets are mounted as files
                try:
                    cred = credentials.Certificate(creds_path)
                    _firebase_app = firebase_admin.initialize_app(cred)
                    logging.info(f"Firebase Admin SDK initialized with credentials from {creds_path}")
                    return _firebase_app
                except ValueError as e2:
                    # If app already exists, get it
                    if "already exists" in str(e2).lower():
                        _firebase_app = firebase_admin.get_app()
                        logging.info("Firebase Admin SDK already initialized, retrieved existing app")
                        return _firebase_app
                    logging.warning(f"Credentials path {creds_path} not found or invalid: {e2}", exc_info=True)
                except Exception as e2:
                    logging.warning(f"Credentials path {creds_path} not found or invalid: {e2}", exc_info=True)
        else:
            logging.warning("Firebase Admin SDK initialization failed: No credentials available")
            logging.warning("Set GOOGLE_APPLICATION_CREDENTIALS or ensure service account has Firebase Admin role")
            # Don't raise - allow retry on first token verification
            return None
    
    return _firebase_app

def verify_id_token(id_token: str) -> Dict:
    """
    Verify Firebase ID token and return decoded token
    
    Args:
        id_token: Firebase ID token string
        
    Returns:
        Decoded token dictionary with user information
        
    Raises:
        ValueError: If token is invalid or expired
        FirebaseError: If Firebase service error occurs
    """
    global _firebase_app
    
    if _firebase_app is None:
        init_firebase()
    
    if _firebase_app is None:
        # Try to initialize again with explicit error handling
        try:
            logging.info("Firebase app is None, attempting to initialize...")
            init_firebase()
        except Exception as e:
            logging.error(f"Firebase Admin SDK initialization failed during token verification: {e}", exc_info=True)
            raise ValueError(f"Firebase Admin SDK not initialized: {str(e)}")
    
    if _firebase_app is None:
        # Log environment for debugging
        gcp_enabled = os.getenv("GCP_ENABLED", "false")
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT_ID") or "not set"
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or "not set"
        logging.error(
            f"Firebase Admin SDK not initialized. "
            f"GCP_ENABLED={gcp_enabled}, PROJECT_ID={project_id}, "
            f"GOOGLE_APPLICATION_CREDENTIALS={creds_path}"
        )
        raise ValueError("Firebase Admin SDK not initialized. Check service account permissions.")
    
    try:
        # Log Firebase app status for debugging
        if _firebase_app:
            logging.info(f"Verifying token with Firebase app: project={_firebase_app.project_id}")
        else:
            logging.error("Firebase app is None when trying to verify token")
            raise ValueError("Firebase Admin SDK not initialized")
        
        # Verify the ID token
        # Use check_revoked=False to allow unverified emails
        decoded_token = auth.verify_id_token(id_token, check_revoked=False, app=_firebase_app)
        logging.info(f"Token verified successfully for user: {decoded_token.get('email', 'unknown')}")
        return decoded_token
    except auth.InvalidIdTokenError as e:
        error_msg = str(e)
        error_code = getattr(e, "code", "INVALID_TOKEN")
        logging.error(
            f"Invalid Firebase ID token: {error_msg} (code: {error_code})",
            exc_info=True,
            extra={
                "error_type": "InvalidIdTokenError",
                "error_message": error_msg,
                "error_code": error_code,
                "token_preview": id_token[:50] + "..." if len(id_token) > 50 else id_token
            }
        )
        raise ValueError(f"Invalid authentication token: {error_msg}")
    except auth.ExpiredIdTokenError as e:
        logging.warning(
            "Expired Firebase ID token",
            extra={
                "error_type": "ExpiredIdTokenError",
                "error_message": str(e),
                "error_code": getattr(e, "code", "EXPIRED_TOKEN")
            }
        )
        raise ValueError("Authentication token has expired")
    except FirebaseError as e:
        logging.error(
            "Firebase error verifying token",
            extra={
                "error_type": "FirebaseError",
                "error_message": str(e),
                "error_code": getattr(e, "code", "FIREBASE_ERROR")
            },
            exc_info=True
        )
        raise ValueError(f"Authentication error: {str(e)}")
    except Exception as e:
        logging.error(
            "Unexpected error verifying Firebase token",
            extra={
                "error_type": type(e).__name__,
                "error_message": str(e)
            },
            exc_info=True
        )
        raise ValueError("Authentication verification failed")

def get_user_role_from_token(decoded_token: Dict) -> str:
    """
    Determine user role from Firebase token
    
    Role assignment logic:
    - If custom claim 'role' exists, use it
    - Else if email is admin@stepsquad.com, assign ADMIN
    - Else assign MEMBER
    
    Args:
        decoded_token: Decoded Firebase token
        
    Returns:
        Role string ("ADMIN" or "MEMBER")
    """
    # Check for custom claim first
    if 'role' in decoded_token and decoded_token['role'] in ['ADMIN', 'MEMBER']:
        return decoded_token['role']
    
    # Fallback to email-based role assignment
    email = decoded_token.get('email', '').lower()
    admin_email = os.getenv("ADMIN_EMAIL", "admin@stepsquad.com").lower()
    
    if email == admin_email:
        return "ADMIN"
    
    return "MEMBER"

def get_user_info_from_token(decoded_token: Dict) -> Dict:
    """
    Extract user information from decoded Firebase token
    
    Args:
        decoded_token: Decoded Firebase token
        
    Returns:
        Dictionary with uid, email, and role
    """
    uid = decoded_token.get('uid')
    email = decoded_token.get('email', '').lower()
    role = get_user_role_from_token(decoded_token)
    
    return {
        'uid': uid,
        'email': email,
        'role': role
    }
