"""
GCP clients initialization for agents service
"""

import os

GCP_ENABLED = os.getenv("GCP_ENABLED", "false").lower() == "true"
firestore_client = None
bigquery_client = None


def init_clients():
    """Initialize GCP clients"""
    global firestore_client, bigquery_client
    
    if not GCP_ENABLED:
        return
    
    try:
        from google.cloud import firestore
        firestore_client = firestore.Client()
    except ImportError:
        import logging
        logging.warning("Firestore not available")
        firestore_client = None
    except Exception as e:
        import logging
        logging.warning(f"Failed to initialize Firestore: {e}")
        firestore_client = None
    
    try:
        from google.cloud import bigquery
        bigquery_client = bigquery.Client()
    except ImportError:
        # BigQuery is optional
        bigquery_client = None
    except Exception as e:
        import logging
        logging.warning(f"Failed to initialize BigQuery: {e}")
        bigquery_client = None


def fs():
    """Get Firestore client"""
    return firestore_client


def bq():
    """Get BigQuery client"""
    return bigquery_client

