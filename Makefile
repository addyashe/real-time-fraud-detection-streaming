.PHONY: help install test lint format clean docker-up docker-down run-producer run-streaming run-consumer

help:
	@echo "Real-Time Fraud Detection - Available commands:"
	@echo ""
	@echo "  make install          Install dependencies"
	@echo "  make test             Run all tests"
	@echo "  make lint             Run flake8 linter"
	@echo "  make format           Format code with black (if installed)"
	@echo "  make clean            Clean cache files and logs"
	@echo "  make docker-up        Start Docker Compose services"
	@echo "  make docker-down      Stop Docker Compose services"
	@echo "  make run-producer     Start sample transaction producer"
	@echo "  make run-streaming    Start Spark streaming job"
	@echo "  make run-consumer     Start alert consumer"
	@echo "  make demo             Full demo: docker + producer + streaming"
	@echo ""

install:
	python -m venv .venv
	.venv/Scripts/activate && pip install --upgrade pip && pip install -r requirements.txt

test:
	pytest -v tests/ --cov=src --cov-report=html

lint:
	flake8 src/ tests/

format:
	black src/ tests/ || echo "black not installed, skipping format"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov/ build/ dist/ *.egg-info

docker-up:
	docker compose up -d
	@echo "Services started. Kafka at localhost:9092"
	docker compose ps

docker-down:
	docker compose down
	@echo "Services stopped."

run-producer:
	python src/producer.py \
		--bootstrap-server localhost:9092 \
		--topic transactions \
		--file sample_data/transactions.json \
		--rate 5

run-streaming:
	spark-submit \
		--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2 \
		--master local[*] \
		src/streaming_app.py \
		--bootstrap-server localhost:9092 \
		--input-topic transactions \
		--alert-topic alerts \
		--threshold 10000

run-consumer:
	python src/alerts_consumer.py \
		--bootstrap-server localhost:9092 \
		--topic alerts

demo: docker-up
	@echo "Waiting for Kafka to be ready..."
	sleep 10
	@echo "Starting producer..."
	$(MAKE) run-producer &
	@echo "Starting streaming job (in another terminal)..."
	@echo "Run: make run-streaming"
	@echo "Or in another terminal: make run-consumer"
