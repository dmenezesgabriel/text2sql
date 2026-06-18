.DEFAULT_GOAL := all

.PHONY: check-frontend test-frontend frontend-e2e frontend \
        check-backend test-backend backend \
        check test all dev dev-down

dev:
	docker compose up

dev-down:
	docker compose down

check-frontend:
	$(MAKE) -C frontend check

test-frontend:
	$(MAKE) -C frontend test

frontend-e2e:
	$(MAKE) -C frontend e2e

frontend: check-frontend test-frontend frontend-e2e

check-backend:
	$(MAKE) -C backend check

test-backend:
	$(MAKE) -C backend test

backend: check-backend test-backend

check: check-frontend check-backend

test: test-frontend test-backend

all: frontend backend
