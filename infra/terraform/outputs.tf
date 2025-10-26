output "topic_steps_ingest" { value = google_pubsub_topic.steps_ingest.name }
output "sub_steps_ingest" { value = google_pubsub_subscription.steps_ingest_sub.name }
output "bq_dataset" { value = google_bigquery_dataset.stepsquad.dataset_id }
