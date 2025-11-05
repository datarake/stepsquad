"""
GCP clients initialization for agents service
"""

import os
import logging

GCP_ENABLED = os.getenv("GCP_ENABLED", "false").lower() == "true"
firestore_client = None
bigquery_client = None


def init_clients():
    """Initialize GCP clients"""
    global firestore_client, bigquery_client
    
    if not GCP_ENABLED:
        return
    
    # IMPORTANT: Use Firebase project ID for Firestore, not GCP project ID
    # Firestore is part of Firebase and uses the Firebase project ID
    firebase_project_id = os.getenv("FIREBASE_PROJECT_ID") or "stepsquad-46d14"
    gcp_project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT_ID")
    
    logging.info(f"Initializing GCP clients - Firebase project: {firebase_project_id}, GCP project: {gcp_project_id}")
    
    try:
        from google.cloud import firestore
        # Initialize Firestore with Firebase project ID (not GCP project ID)
        firestore_client = firestore.Client(project=firebase_project_id)
        logging.info(f"Firestore client initialized with project: {firebase_project_id}")
    except ImportError:
        logging.warning("Firestore not available")
        firestore_client = None
    except Exception as e:
        logging.warning(f"Failed to initialize Firestore: {e}", exc_info=True)
        firestore_client = None
    
    try:
        from google.cloud import bigquery
        # BigQuery uses GCP project ID
        bigquery_project_id = gcp_project_id or firebase_project_id
        bigquery_client = bigquery.Client(project=bigquery_project_id)
        logging.info(f"BigQuery client initialized with project: {bigquery_project_id}")
    except ImportError:
        # BigQuery is optional
        bigquery_client = None
    except Exception as e:
        logging.warning(f"Failed to initialize BigQuery: {e}", exc_info=True)
        bigquery_client = None


def fs():
    """Get Firestore client"""
    return firestore_client


def bq():
    """Get BigQuery client"""
    return bigquery_client

