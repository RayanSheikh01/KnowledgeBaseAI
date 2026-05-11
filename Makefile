.PHONY: db-up db-down db-shell

db-up:
	docker compose up -d db

db-down:
	docker compose down

db-shell:
	docker compose exec db psql -U kb -d kb
