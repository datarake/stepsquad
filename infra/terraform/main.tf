terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.33"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_project_service" "services" {
  for_each = toset([
    "run.googleapis.com",
    "pubsub.googleapis.com",
    "firestore.googleapis.com",
    "bigquery.googleapis.com",
    "cloudscheduler.googleapis.com",
    "secretmanager.googleapis.com",
  ])
  project = var.project_id
  service = each.value
}

resource "google_pubsub_topic" "steps_ingest" {
  name = "steps.ingest"
}

resource "google_pubsub_subscription" "steps_ingest_sub" {
  name  = "steps.ingest.sub"
  topic = google_pubsub_topic.steps_ingest.name
  ack_deadline_seconds = 20
}

resource "google_bigquery_dataset" "stepsquad" {
  dataset_id = var.bq_dataset
  location   = var.region
}
