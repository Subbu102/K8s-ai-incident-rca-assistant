.PHONY: help install dev test lint format clean build deploy

help:
	@echo "K8s AI Incident RCA Assistant - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install              Install dependencies"
	@echo "  make install-dev          Install dev dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev                  Run development server"
	@echo "  make examples             Run example code"
	@echo ""
	@echo "Testing:"
	@echo "  make test                 Run tests"
	@echo "  make test-cov             Run tests with coverage"
	@echo "  make test-fast            Run tests without slow tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint                 Run linters (flake8, pylint)"
	@echo "  make format               Format code (black, isort)"
	@echo "  make format-check         Check code formatting"
	@echo "  make type-check           Run type checking (mypy)"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build         Build Docker image"
	@echo "  make docker-run           Run Docker container"
	@echo "  make docker-push          Push to registry"
	@echo "  make docker-compose-up    Start docker-compose services"
	@echo "  make docker-compose-down  Stop docker-compose services"
	@echo ""
	@echo "Kubernetes:"
	@echo "  make k8s-deploy           Deploy to Kubernetes"
	@echo "  make k8s-status           Check deployment status"
	@echo "  make k8s-logs             View pod logs"
	@echo "  make k8s-clean            Delete Kubernetes resources"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean                Remove build artifacts"
	@echo "  make clean-all            Full cleanup"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install pytest pytest-asyncio pytest-cov
	pip install black flake8 pylint mypy
	pip install pre-commit

dev:
	python dev.py

examples:
	python examples.py

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=app/ --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

test-fast:
	pytest tests/ -v -m "not slow"

lint:
	flake8 app/ --count --show-source
	pylint app/ --exit-zero

format:
	black app/
	isort app/

format-check:
	black --check app/
	isort --check-only app/

type-check:
	mypy app/ --ignore-missing-imports

docker-build:
	docker build -t k8s-incident-rca:latest .

docker-run:
	docker run -p 8000:8000 \
		-v ~/.kube/config:/app/.kube/config \
		k8s-incident-rca:latest

docker-push:
	docker tag k8s-incident-rca:latest ghcr.io/yourorg/k8s-incident-rca:latest
	docker push ghcr.io/yourorg/k8s-incident-rca:latest

docker-compose-up:
	docker-compose up -d
	@echo "Services started. Check status with: docker-compose ps"

docker-compose-down:
	docker-compose down

docker-compose-logs:
	docker-compose logs -f app

k8s-deploy:
	kubectl apply -f kubernetes/
	kubectl rollout status deployment/k8s-incident-rca

k8s-status:
	kubectl get deployment k8s-incident-rca
	kubectl get pods -l app=k8s-incident-rca
	kubectl get svc k8s-incident-rca

k8s-logs:
	kubectl logs -f deployment/k8s-incident-rca

k8s-shell:
	kubectl exec -it deployment/k8s-incident-rca -- /bin/bash

k8s-clean:
	kubectl delete -f kubernetes/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/ .pytest_cache/ .mypy_cache/ .tox/
	rm -rf build/ dist/ *.egg-info/

clean-all: clean
	rm -rf venv/ .venv/ env/
	rm -rf mlruns/ .mlflow/
	docker-compose down -v

install-hooks:
	pre-commit install
	pre-commit run --all-files

.DEFAULT_GOAL := help
