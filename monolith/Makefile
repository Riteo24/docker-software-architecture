.PHONY: migrate test up smoke
migrate:
	docker compose run --rm api python -m app.infrastructure.migrate
test:
	docker build --target test -t architecture-monolith-tests .
	docker run --rm architecture-monolith-tests
up:
	docker compose up --build -d --wait
smoke:
	python tests/smoke.py
