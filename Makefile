.PHONY: clean lint test run setup help

PYTHON = python3
PIP = pip3

help:
	@echo "Available commands:"
	@echo "  setup        - Install dependencies"
	@echo "  clean        - Remove build artifacts"
	@echo "  lint         - Run code quality checks"
	@echo "  test         - Run tests"
	@echo "  run          - Run the application"
	@echo "  train        - Train AI models"
	@echo "  deploy       - Deploy to cloud"

setup:
	$(PIP) install -r requirements.txt
	$(PYTHON) -m spacy download en_core_web_sm

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

lint:
	flake8 src
	black --check src
	isort --check src

test:
	pytest src/tests

run:
	uvicorn src.app.api.main:app --reload

train:
	$(PYTHON) src/ai/train_models.py

deploy:
	./cloud_infra/deploy.sh

# Data processing pipeline
data-process:
	$(PYTHON) src/utils/data_processor.py
