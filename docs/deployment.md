# Deployment Guide

## Environments

### 1. Local Development (Docker Compose)

Best for: Development, testing, demos.

```bash
make docker-up
make run-producer &
make run-streaming
```

Services available:
- Kafka: `localhost:9092`
- Zookeeper: `localhost:2181`
- Postgres: `localhost:5432` (credentials: demo/demo)
- Debezium Connect: `http://localhost:8083`

### 2. Kubernetes (EKS/AKS/GKE)

Best for: Production, high-availability, multi-tenant.

#### Prerequisites

```bash
# Install tools
brew install kubectl helm spark  # macOS
# or apt-get install kubectl helm (Linux)

# Configure kubeconfig
aws eks update-kubeconfig --name my-cluster --region us-west-2

# Verify cluster
kubectl cluster-info
```

#### Deploy Kafka (Strimzi Operator)

```bash
# Install Strimzi Kafka operator
helm repo add strimzi https://strimzi.io/charts
helm install strimzi-kafka-operator strimzi/strimzi-kafka-operator -n kafka --create-namespace

# Create cluster
kubectl apply -f k8s/kafka-cluster.yaml -n kafka

# Wait for cluster to be ready
kubectl wait kafka/fraud-kafka --for=condition=Ready --timeout=300s -n kafka
```

#### Deploy Spark Job

```bash
# Create namespace
kubectl create namespace fraud-detection

# Create service account and RBAC
kubectl apply -f k8s/rbac.yaml -n fraud-detection

# Create AWS secrets (for S3 access)
kubectl create secret generic aws-creds \
  --from-literal=access-key=$AWS_ACCESS_KEY_ID \
  --from-literal=secret-key=$AWS_SECRET_ACCESS_KEY \
  -n fraud-detection

# Deploy Spark job
kubectl apply -f k8s/spark-job.yaml -n fraud-detection

# Monitor job
kubectl logs -f job/fraud-detection-spark-job -n fraud-detection
```

#### Deploy Supporting Services

```bash
# Postgres (source database for CDC)
kubectl apply -f k8s/postgres-deployment.yaml -n fraud-detection

# Debezium Connector (CDC)
kubectl apply -f k8s/debezium-connector.yaml -n fraud-detection

# Monitoring (Prometheus + Grafana)
kubectl apply -f k8s/monitoring/ -n fraud-detection
kubectl port-forward svc/grafana 3000:3000 -n fraud-detection
# Open http://localhost:3000 (admin/admin)
```

### 3. Databricks

Best for: Production with managed infrastructure, auto-scaling.

#### Setup

1. **Upload code to Databricks Workspace**:
   ```bash
   databricks workspace import src/streaming_app.py /Users/your-email@company.com/fraud-detection
   databricks workspace import sample_data/transactions.json /Workspace/fraud-detection/data/
   ```

2. **Create Databricks Cluster**:
   - Runtime: Databricks Runtime 13.3 LTS (Apache Spark 3.4)
   - Python: 3.10
   - Nodes: 3-5 (auto-scale based on load)
   - Instance type: i3.xlarge (local SSD for shuffle)

3. **Install Libraries**:
   ```
   kafka-python==2.0.2
   delta-spark==3.0.0
   ```

4. **Create Job**:
   - Task type: Notebook
   - Notebook path: `/fraud-detection/streaming_app`
   - Cluster: Use above
   - Schedule: Run continuously or on interval
   - Timeout: 24 hours

5. **Monitor**:
   - Databricks Jobs UI: view run history, logs
   - Delta Lake: inspect `alerts` table
   - SQL Analytics: create dashboards on alerts

#### Example Databricks Notebook

```python
# Databricks notebook source

# COMMAND ----------
# Mount S3 for checkpoints
dbutils.fs.mount(
  source="s3a://my-bucket",
  mount_point="/mnt/fraud-data",
  extra_configs={"fs.s3a.access.key": dbutils.secrets.get("aws", "access-key"),
                 "fs.s3a.secret.key": dbutils.secrets.get("aws", "secret-key")}
)

# COMMAND ----------
# Run streaming job
%run /Users/your-email@company.com/fraud-detection/streaming_app
```

### 4. AWS ECS (Fargate)

Best for: Containerized, serverless, cost-effective.

```bash
# Build Docker image
docker build -t fraud-detector:latest .

# Push to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-west-2.amazonaws.com
docker tag fraud-detector:latest 123456789.dkr.ecr.us-west-2.amazonaws.com/fraud-detector:latest
docker push 123456789.dkr.ecr.us-west-2.amazonaws.com/fraud-detector:latest

# Deploy to ECS
aws ecs create-task-definition --cli-input-json file://ecs-task-def.json
aws ecs create-service --cluster fraud-detection --service-name streaming-job --task-definition fraud-detector --desired-count 1
```

## Monitoring & Observability

### Prometheus Metrics

Add to Spark config:

```python
spark.metrics.conf = 'monitoring/prometheus.yml'
```

Metrics exposed on `:8090/metrics`:
- `spark_fraud_alerts_total`: cumulative alerts
- `spark_transaction_throughput`: messages/sec
- `spark_processing_latency_seconds`: p99 latency

### Grafana Dashboards

Import dashboards from `monitoring/grafana/`:
1. Open Grafana (http://localhost:3000)
2. Data Sources → Add Prometheus
3. Dashboards → Import → select JSON

Pre-built dashboards:
- `fraud-pipeline-health.json`: pipeline metrics
- `alerts-summary.json`: alerts per rule
- `performance.json`: latency, throughput

### Alerting Rules

Configure in Prometheus (`monitoring/alert-rules.yml`):

```yaml
groups:
- name: fraud_detection
  rules:
  - alert: HighFraudRate
    expr: rate(spark_fraud_alerts_total[5m]) > 10
    for: 5m
    annotations:
      summary: "Fraud rate above threshold"
      
  - alert: ProcessingLatency
    expr: spark_processing_latency_seconds > 5
    annotations:
      summary: "Processing latency spike"
```

## Scaling & Optimization

### Horizontal Scaling

1. **Kafka partitions**: Increase if throughput > 100k/sec
   ```bash
   kafka-topics --alter --topic transactions --partitions 24
   ```

2. **Spark executors**: Increase for higher parallelism
   ```
   --num-executors 10 --executor-cores 4 --executor-memory 8g
   ```

3. **Consumer groups**: Multiple streaming jobs for different rules
   ```
   spark-submit ... --group-id fraud-detection-1
   spark-submit ... --group-id fraud-detection-2  # For ML model
   ```

### Cost Optimization

- **Reserved Instances**: 40% discount for 1-year commitment
- **Spot Instances**: 70% discount for batch/non-critical jobs
- **Auto-scaling**: Scale down during off-peak (nights, weekends)
- **Checkpoints**: Use S3 with intelligent tiering (archive old data)

### Performance Tuning

See [docs/tuning.md](docs/tuning.md) for detailed recommendations.

## Disaster Recovery

### Backup & Restore

```bash
# Backup Kafka topics to S3
kafka-mirror-maker --consumer.config kafka-consumer.properties \
  --producer.config s3-producer.properties \
  --whitelist="transactions|alerts"

# Restore from S3
aws s3 cp s3://my-bucket/topics/ . --recursive
kafka-console-producer --topic transactions --broker-list localhost:9092 < transactions-backup.json
```

### Checkpoint Recovery

Spark automatically recovers from checkpoints on restart:

```bash
# Clear checkpoint and restart (loses in-flight data)
rm -rf /tmp/fraud-checkpoint/*
spark-submit ... src/streaming_app.py
```

### High Availability

For production, ensure:
- Kafka: 3+ brokers, replication factor 3
- Spark: multiple executors, avoid single point of failure
- Monitoring: alert on job failures, restart automatically

## Troubleshooting

### Kafka Connection Errors

```bash
# Test connectivity
kafka-console-consumer --topic transactions --bootstrap-server localhost:9092 --max-messages 1
```

### Spark Job Failures

```bash
# Check logs
kubectl logs job/fraud-detection-spark-job -n fraud-detection

# Increase driver memory if OOM
--driver-memory 4g --driver-java-options "-XX:+UseG1GC"
```

### Data Loss

- Ensure `acks='all'` in Kafka producer
- Enable checkpointing in Spark
- Monitor Kafka lag: should be near 0

## Support & Docs

- **GitHub Issues**: Report bugs or request features
- **Docs**: See [docs/](docs/) for architecture, tuning, CDC setup
- **Examples**: See [notebooks/](notebooks/) for demos
