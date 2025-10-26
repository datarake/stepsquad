# Terraform – Base

1. Authenticate and select project:
```bash
gcloud auth application-default login
gcloud config set project StepSquad
```

2. Init & apply:
```bash
cd infra/terraform
terraform init
terraform apply -var 'project_id=StepSquad' -var 'region=europe-west1'
```
