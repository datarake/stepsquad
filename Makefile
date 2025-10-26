.PHONY: api web workers dev seed bq_schema deploy_api deploy_workers deploy_web deploy_agents
dev:
	docker compose up --build

api:
	cd apps/api && uv run uvicorn main:app --host 0.0.0.0 --port 8004 --reload

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
