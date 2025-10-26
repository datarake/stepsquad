import os, time, json
from datetime import datetime
GCP_ENABLED = os.getenv("GCP_ENABLED","false").lower()=="true"
PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT","StepSquad")
SUB_INGEST = os.getenv("PUBSUB_SUB_INGEST","steps.ingest.sub")
BQ_DATASET = os.getenv("BQ_DATASET","stepsquad")
def write_fire_bq(data: dict):
    from google.cloud import firestore, bigquery
    fs = firestore.Client(); bq = bigquery.Client()
    uid, date, steps = data["user_id"], data["date"], int(data["steps"])
    fs.collection("daily_steps").document(f"{uid}_{date}").set({"user_id":uid,"date":date,"steps":steps}, merge=True)
    bq.insert_rows_json(f"{BQ_DATASET}.fact_daily_steps", [{"user_id":uid,"date":date,"steps":steps}])
def handle_event(data: dict):
    write_fire_bq(data)
    print(f"[worker] processed {data.get('user_id')} {data.get('date')} {data.get('steps')}")
def pull_loop():
    if not GCP_ENABLED:
        while True:
            print(f"[worker] local heartbeat {datetime.utcnow().isoformat()}"); time.sleep(10)
    else:
        from google.cloud import pubsub_v1
        subscriber = pubsub_v1.SubscriberClient()
        sub_path = subscriber.subscription_path(PROJECT, SUB_INGEST)
        def _cb(message):
            try:
                data = json.loads(message.data.decode("utf-8")); handle_event(data); message.ack()
            except Exception as e:
                print("[worker] error:", e); message.nack()
        fut = subscriber.subscribe(sub_path, callback=_cb)
        print(f"[worker] listening on {sub_path}")
        try: fut.result()
        except KeyboardInterrupt: fut.cancel()
if __name__=="__main__": pull_loop()
