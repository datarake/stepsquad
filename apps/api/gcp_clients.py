import os
import logging
GCP_ENABLED = os.getenv("GCP_ENABLED", "false").lower() == "true"
firestore_client = None
bigquery_client = None
pubsub_publisher = None

def init_clients():
    global firestore_client, bigquery_client, pubsub_publisher
    if not GCP_ENABLED:
        return
    
    # IMPORTANT: Use Firebase project ID for Firestore, not GCP project ID
    # Firestore is part of Firebase and uses the Firebase project ID
    firebase_project_id = os.getenv("FIREBASE_PROJECT_ID") or "stepsquad-46d14"
    gcp_project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT_ID")
    
    logging.info(f"Initializing GCP clients - Firebase project: {firebase_project_id}, GCP project: {gcp_project_id}")
    
    try:
        from google.cloud import firestore, pubsub_v1
        # Initialize Firestore with Firebase project ID (not GCP project ID)
        firestore_client = firestore.Client(project=firebase_project_id)
        logging.info(f"Firestore client initialized with project: {firebase_project_id}")
        
        # Pub/Sub uses GCP project ID (not Firebase project ID)
        pubsub_project_id = gcp_project_id or firebase_project_id
        pubsub_publisher = pubsub_v1.PublisherClient()
        logging.info(f"Pub/Sub client initialized (project: {pubsub_project_id})")
        
        # BigQuery is optional - only needed for analytics
        # BigQuery uses GCP project ID
        try:
            from google.cloud import bigquery
            bigquery_project_id = gcp_project_id or firebase_project_id
            bigquery_client = bigquery.Client(project=bigquery_project_id)
            logging.info(f"BigQuery client initialized with project: {bigquery_project_id}")
        except ImportError:
            bigquery_client = None
    except ImportError as e:
        logging.warning(f"Failed to import GCP clients: {e}")
        firestore_client = None
        bigquery_client = None
        pubsub_publisher = None
    except Exception as e:
        logging.error(f"Failed to initialize GCP clients: {e}", exc_info=True)
        firestore_client = None
        bigquery_client = None
        pubsub_publisher = None
def fs():
    return firestore_client
def bq():
    return bigquery_client
def publisher():
    return pubsub_publisher
