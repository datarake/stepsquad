import os, json
from gcp_clients import publisher
PUBSUB_TOPIC_INGEST = os.getenv("PUBSUB_TOPIC_INGEST", "steps.ingest")
GCP_ENABLED = os.getenv("GCP_ENABLED", "false").lower() == "true"
PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "StepSquad")
def publish_ingest(event: dict):
    if not GCP_ENABLED or not publisher():
        return {"local": True}
    topic_path = publisher().topic_path(PROJECT, PUBSUB_TOPIC_INGEST)
    data = json.dumps(event).encode("utf-8")
    future = publisher().publish(topic_path, data=data)
    return {"message_id": future.result()}
