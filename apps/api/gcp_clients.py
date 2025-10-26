import os
GCP_ENABLED = os.getenv("GCP_ENABLED", "false").lower() == "true"
firestore_client = None
bigquery_client = None
pubsub_publisher = None
def init_clients():
    global firestore_client, bigquery_client, pubsub_publisher
    if not GCP_ENABLED:
        return
    from google.cloud import firestore, bigquery, pubsub_v1
    firestore_client = firestore.Client()
    bigquery_client = bigquery.Client()
    pubsub_publisher = pubsub_v1.PublisherClient()
def fs():
    return firestore_client
def bq():
    return bigquery_client
def publisher():
    return pubsub_publisher
