"""
Integration tests for Firebase Authentication
These tests verify Firebase authentication works correctly.
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def mock_firebase_enabled():
    """Mock GCP_ENABLED=True for Firebase auth tests"""
    with patch.dict(os.environ, {"GCP_ENABLED": "true"}):
        yield

@pytest.fixture
def mock_firebase_token_verification():
    """Mock Firebase token verification"""
    with patch("firebase_auth.verify_id_token") as mock_verify:
        mock_decoded_token = {
            "uid": "firebase-uid-123",
            "email": "test@example.com",
            "role": "MEMBER"
        }
        mock_verify.return_value = mock_decoded_token
        yield mock_verify

def test_health_endpoint_shows_firebase_status():
    """Test health endpoint includes Firebase status"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    
    assert "ok" in data
    assert "time" in data
    assert "tz" in data
    assert "gcp_enabled" in data
    assert "firebase_initialized" in data

def test_health_endpoint_dev_mode():
    """Test health endpoint in dev mode"""
    with patch.dict(os.environ, {"GCP_ENABLED": "false"}):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        
        assert data["gcp_enabled"] is False
        assert data["firebase_initialized"] is False
        assert data.get("mode") == "dev"

def test_health_endpoint_production_mode():
    """Test health endpoint in production mode"""
    with patch.dict(os.environ, {"GCP_ENABLED": "true"}):
        with patch("firebase_auth.init_firebase") as mock_init:
            # Mock successful Firebase initialization
            mock_app = MagicMock()
            mock_init.return_value = mock_app
            
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            
            assert data["gcp_enabled"] is True
            assert data["firebase_initialized"] is True

def test_health_endpoint_firebase_init_failure():
    """Test health endpoint when Firebase initialization fails"""
    with patch.dict(os.environ, {"GCP_ENABLED": "true"}):
        with patch("firebase_auth.init_firebase") as mock_init:
            # Mock Firebase initialization failure
            mock_init.side_effect = Exception("Firebase initialization failed")
            
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            
            assert data["gcp_enabled"] is True
            assert data["firebase_initialized"] is False
            assert "firebase_error" in data
            assert data["ok"] is False  # Should be unhealthy

def test_firebase_auth_requires_bearer_token(mock_firebase_enabled):
    """Test Firebase auth requires Bearer token"""
    response = client.get("/me")
    assert response.status_code == 401
    assert "Authentication required" in response.json()["detail"]

def test_firebase_auth_invalid_token(mock_firebase_enabled):
    """Test Firebase auth with invalid token"""
    with patch("firebase_auth.verify_id_token") as mock_verify:
        mock_verify.side_effect = ValueError("Invalid authentication token")
        
        response = client.get(
            "/me",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401
        assert "Invalid authentication token" in response.json()["detail"]

def test_firebase_auth_expired_token(mock_firebase_enabled):
    """Test Firebase auth with expired token"""
    with patch.dict(os.environ, {"GCP_ENABLED": "true"}):
        with patch("firebase_auth.verify_id_token") as mock_verify:
            # Mock expired token error using ValueError
            mock_verify.side_effect = ValueError("Authentication token has expired")
            
            response = client.get(
                "/me",
                headers={"Authorization": "Bearer expired-token"}
            )
            assert response.status_code == 401
            assert "expired" in response.json()["detail"].lower()

def test_firebase_auth_success(mock_firebase_enabled, mock_firebase_token_verification):
    """Test successful Firebase authentication"""
    with patch("storage.get_user") as mock_get_user:
        with patch("storage.upsert_user") as mock_upsert:
            # Mock user doesn't exist yet (will be created)
            mock_get_user.return_value = None
            
            response = client.get(
                "/me",
                headers={"Authorization": "Bearer valid-firebase-token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["uid"] == "firebase-uid-123"
            assert data["email"] == "test@example.com"
            assert data["role"] == "MEMBER"
            
            # Verify user was created
            mock_upsert.assert_called_once()

def test_firebase_auth_admin_role_from_custom_claim(mock_firebase_enabled):
    """Test Firebase auth assigns ADMIN role from custom claim"""
    with patch.dict(os.environ, {"GCP_ENABLED": "true"}):
        with patch("firebase_auth.verify_id_token") as mock_verify:
            with patch("storage.get_user") as mock_get_user:
                with patch("storage.upsert_user") as mock_upsert:
                    mock_decoded_token = {
                        "uid": "firebase-uid-admin",
                        "email": "admin@example.com",
                        "role": "ADMIN"  # Custom claim
                    }
                    mock_verify.return_value = mock_decoded_token
                    mock_get_user.return_value = None
                    
                    response = client.get(
                        "/me",
                        headers={"Authorization": "Bearer admin-token"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["role"] == "ADMIN"

def test_firebase_auth_admin_role_from_email(mock_firebase_enabled):
    """Test Firebase auth assigns ADMIN role from email"""
    with patch.dict(os.environ, {"GCP_ENABLED": "true", "ADMIN_EMAIL": "admin@stepsquad.club"}):
        with patch("firebase_auth.verify_id_token") as mock_verify:
            with patch("storage.get_user") as mock_get_user:
                with patch("storage.upsert_user") as mock_upsert:
                    mock_decoded_token = {
                        "uid": "firebase-uid-admin",
                        "email": "admin@stepsquad.club",  # Admin email
                        # No custom claim
                    }
                    mock_verify.return_value = mock_decoded_token
                    mock_get_user.return_value = None
                    
                    response = client.get(
                        "/me",
                        headers={"Authorization": "Bearer admin-token"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["role"] == "ADMIN"

def test_firebase_auth_user_role_update(mock_firebase_enabled):
    """Test Firebase auth updates user role when custom claim changes"""
    with patch.dict(os.environ, {"GCP_ENABLED": "true"}):
        with patch("firebase_auth.verify_id_token") as mock_verify:
            with patch("storage.get_user") as mock_get_user:
                with patch("storage.upsert_user") as mock_upsert:
                    # User exists with MEMBER role
                    existing_user = {
                        "uid": "firebase-uid-123",
                        "email": "user@example.com",
                        "role": "MEMBER",
                        "created_at": "2025-01-01T00:00:00",
                        "updated_at": "2025-01-01T00:00:00"
                    }
                    mock_get_user.return_value = existing_user
                    
                    # Token has ADMIN role (custom claim changed)
                    mock_decoded_token = {
                        "uid": "firebase-uid-123",
                        "email": "user@example.com",
                        "role": "ADMIN"  # Changed to ADMIN
                    }
                    mock_verify.return_value = mock_decoded_token
                    
                    response = client.get(
                        "/me",
                        headers={"Authorization": "Bearer updated-token"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["role"] == "ADMIN"
                    
                    # Verify user was updated
                    mock_upsert.assert_called_once()
                    call_args = mock_upsert.call_args
                    assert call_args[0][1]["role"] == "ADMIN"

