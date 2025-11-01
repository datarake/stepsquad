"""
GCP clients initialization for agents service
"""

import os
from google.cloud import firestore
from google.cloud import bigquery

GCP_ENABLED = os.getenv("GCP_ENABLED", "false").lower() == "true"
firestore_client = None
bigquery_client = None


def init_clients():
    """Initialize GCP clients"""
    global firestore_client, bigquery_client
    
    if not GCP_ENABLED:
        return
    
    try:
        firestore_client = firestore.Client()
        bigquery_client = bigquery.Client()
    except Exception as e:
        import logging
        logging.warning(f"Failed to initialize GCP clients: {e}")
        firestore_client = None
        bigquery_client = None


def fs():
    """Get Firestore client"""
    return firestore_client


def bq():
    """Get BigQuery client"""
    return bigquery_client

