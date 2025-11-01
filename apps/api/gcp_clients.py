import os
GCP_ENABLED = os.getenv("GCP_ENABLED", "false").lower() == "true"
firestore_client = None
bigquery_client = None
pubsub_publisher = None
def init_clients():
    global firestore_client, bigquery_client, pubsub_publisher
    if not GCP_ENABLED:
        return
    try:
        from google.cloud import firestore, pubsub_v1
        firestore_client = firestore.Client()
        pubsub_publisher = pubsub_v1.PublisherClient()
        
        # BigQuery is optional - only needed for analytics
        try:
            from google.cloud import bigquery
            bigquery_client = bigquery.Client()
        except ImportError:
            bigquery_client = None
    except ImportError as e:
        import logging
        logging.warning(f"Failed to import GCP clients: {e}")
        firestore_client = None
        bigquery_client = None
        pubsub_publisher = None
def fs():
    return firestore_client
def bq():
    return bigquery_client
def publisher():
    return pubsub_publisher
