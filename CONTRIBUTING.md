# Contributing Guide

## Overview

We welcome contributions! This project is a production-grade fraud detection system for real-time streaming data.

## Getting Started

1. **Fork and clone** the repository
2. **Create a feature branch** from `main`
3. **Set up development environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. **Make changes** and test locally
5. **Submit a Pull Request** with a clear description

## Code Standards

### Style & Linting

We use **flake8** for linting:

```bash
flake8 src/ tests/
```

### Testing

All changes must include tests:

```bash
pytest -v tests/
pytest --cov=src tests/  # With coverage
```

Minimum coverage: **80%**

### Documentation

- Update `README.md` for user-facing changes
- Update `docs/` for architectural/design changes
- Use docstrings for all functions/classes (Google style)

```python
def detect(self, tx: Dict[str, Any]) -> Tuple[bool, str, float]:
    """
    Detect fraudulent transaction.
    
    Args:
        tx: Transaction record (dict)
        
    Returns:
        Tuple of (is_fraud, rule_triggered, risk_score)
    """
```

## Feature Development

### Adding a New Fraud Detection Rule

1. **Update `src/detector.py`**:
   - Add rule check method (e.g., `_check_velocity_card()`)
   - Add to `detect()` method
   - Assign risk score weight

2. **Add tests in `tests/test_detector.py`**:
   ```python
   def test_velocity_card(self, detector):
       tx = {'card_id': 'card-001', ...}
       is_fraud, rule, score = detector.detect(tx)
       assert rule == 'VELOCITY_CARD'
   ```

3. **Update `docs/architecture.md`** with rule description

4. **Test end-to-end**:
   ```bash
   docker compose up -d
   python src/producer.py --file sample_data/transactions.json
   spark-submit --packages ... src/streaming_app.py
   ```

### Tuning Thresholds

Update `src/detector.py` `__init__` defaults:

```python
def __init__(self, amount_threshold: float = 10000.0, ...):
```

Then test on historical data:

```bash
python scripts/backtest.py --data historical_transactions.csv
```

## Performance Testing

For changes affecting latency/throughput:

```bash
# Generate test load
python scripts/generate_load.py --count 1000000 --output test.json

# Benchmark
spark-submit src/streaming_app.py ... 2>&1 | tee benchmark.log

# Compare results
python scripts/compare_benchmarks.py benchmark.log baseline.log
```

## Bug Reports

Use GitHub Issues with:
- Clear title and description
- Reproduction steps
- Expected vs actual behavior
- Environment (Python version, Spark version, OS)

## Pull Request Process

1. Update version in `setup.py` (semantic versioning)
2. Update `CHANGELOG.md` with changes
3. Ensure CI passes (GitHub Actions)
4. Request review from codeowners
5. Merge after approval

## License

By contributing, you agree your changes are licensed under the MIT License.

## Questions?

Open a GitHub Discussion or check the [docs/](docs/) directory.

Thanks for contributing! 🙌
