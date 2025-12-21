# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0]

### Added

- **Core Fraud Detection Engine**:
  - Rule-based detector with 6 configurable fraud rules
  - Risk scoring system (0-100 scale)
  - Support for custom thresholds

- **Real-Time Streaming**:
  - PySpark Structured Streaming integration
  - Kafka producer and consumer for transactions/alerts
  - Dual-sink output (Kafka + console)
  - Stateful processing with checkpointing

- **Fraud Detection Rules**:
  - Amount threshold (high-value transactions)
  - Blacklist merchant detection
  - Geographic velocity (impossible travel)
  - Country mismatch (billing ≠ shipping)
  - Missing 3D Secure authentication
  - Suspicious merchant categories

- **Testing & Quality**:
  - 20+ unit tests for detector logic
  - Edge case handling (invalid amounts, missing fields)
  - Real-world scenario tests
  - pytest + flake8 linting

- **Documentation**:
  - Comprehensive README with architecture diagrams
  - API reference for detector class
  - Performance tuning guide
  - Deployment instructions (Docker, K8s, Databricks, AWS)
  - Contributing guidelines

- **Local Development**:
  - Docker Compose with Kafka, Zookeeper, Postgres, Debezium
  - Sample transaction data (8 test cases)
  - Makefile for common tasks
  - Python virtual environment setup

- **CI/CD**:
  - GitHub Actions workflow (lint, test)
  - Pytest with coverage reporting
  - Flake8 linting on all PRs

- **Kubernetes Support**:
  - Spark job manifests
  - Service account and RBAC configs
  - Support for EKS, AKS, GKE

### Fixed

- N/A (initial release)

### Changed

- N/A (initial release)

### Deprecated

- N/A (initial release)

### Removed

- N/A (initial release)

### Security

- PCI DSS compliance notes
- Encryption recommendations (TLS, AES-256)
- RBAC and audit logging guidelines

---

## [Unreleased]

### Planned Features

- **Phase 2**: ML-based fraud detection (XGBoost, Neural Networks)
- **Phase 3**: Entity resolution with Neo4j (fraud rings, linked accounts)
- **Phase 4**: CDC integration (Debezium connectors for all major databases)
- **Phase 5**: Advanced observability (Jaeger tracing, SHAP explainability)
- **Integration Tests**: Embedded Kafka for end-to-end testing
- **Benchmark Suite**: Load testing scripts and performance baselines
- **Grafana Dashboards**: Pre-built monitoring dashboards
- **Multi-Language Support**: Scala, Java implementations
- **Feature Store**: Integration with Tecton or Feast for feature management
- **A/B Testing Framework**: For model experimentation
