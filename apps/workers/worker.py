import base64, json, os
from fastapi import FastAPI, Request
from google.cloud import firestore, bigquery

app = FastAPI()
BQ_DATASET = os.getenv("BQ_DATASET", "stepsquad")

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/pubsub/push")
async def pubsub_push(request: Request):
    envelope = await request.json()
    msg = envelope.get("message", {})
    data_b64 = msg.get("data", "")
    if not data_b64:
        return {"status": "no-data"}
    payload = json.loads(base64.b64decode(data_b64).decode("utf-8"))

    uid = payload["user_id"]
    date = payload["date"]
    steps = int(payload["steps"])

    fs = firestore.Client()
    bq = bigquery.Client()
    fs.collection("daily_steps").document(f"{uid}_{date}").set(
        {"user_id": uid, "date": date, "steps": steps}, merge=True
    )
    bq.insert_rows_json(f"{BQ_DATASET}.fact_daily_steps",
                        [{"user_id": uid, "date": date, "steps": steps}])
    return {"status": "ok"}
