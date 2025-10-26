.PHONY: api web workers dev seed bq_schema deploy_api deploy_workers deploy_web deploy_agents

dev:
	docker compose up --build

api:
	cd apps/api && uv run uvicorn main:app --host 0.0.0.0 --port 8080 --reload

web:
	cd apps/web && pnpm dev

workers:
	cd apps/workers && uv run python worker.py

seed:
	curl -X POST http://localhost:8004/dev/seed

bq_schema:
	cd infra/bq && ./create_tables.sh

deploy_api:
	cd deploy && ./deploy_api.sh

deploy_workers:
	cd deploy && ./deploy_workers.sh

deploy_web:
	cd deploy && ./deploy_web.sh

deploy_agents:
	cd deploy && ./deploy_agents.sh

GCP_REGION ?= europe-west1
PROJECT ?= fluent-coder-476318-n0

check_health:
	@echo "🔍 Checking StepSquad service health in region $(GCP_REGION)..."
	@for svc in stepsquad-api stepsquad-workers stepsquad-agents stepsquad-web; do \
	  url=$$(gcloud run services describe $$svc --region "$(GCP_REGION)" --format 'value(status.url)' 2>/dev/null); \
	  if [ -z "$$url" ]; then \
	    echo "❌ $$svc: not found"; \
	    continue; \
	  fi; \
	  if [ "$$svc" = "stepsquad-workers" ] || [ "$$svc" = "stepsquad-agents" ]; then \
	    token=$$(gcloud auth print-identity-token 2>/dev/null); \
	    resp=$$(curl -s -H "Authorization: Bearer $$token" "$$url/health" || echo ""); \
	  elif [ "$$svc" = "stepsquad-web" ]; then \
	    resp=$$(curl -s "$$url" | head -n 1 || echo ""); \
	  else \
	    resp=$$(curl -s "$$url/health" || echo ""); \
	  fi; \
	  if echo "$$resp" | grep -q '"ok":true'; then \
	    echo "✅ $$svc: healthy ($$url)"; \
	  elif echo "$$resp" | grep -qi "<!doctype html>"; then \
	    echo "✅ $$svc: healthy (HTML frontend) ($$url)"; \
	  elif [ -n "$$resp" ]; then \
	    echo "⚠️  $$svc: unexpected response → $$resp"; \
	  else \
	    echo "❌ $$svc: unreachable"; \
	  fi; \
	done
