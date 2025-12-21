# Fraud Detection Demo Notebook

Interactive walkthrough of the fraud detection system.

## Setup

```python
# Install dependencies
!pip install kafka-python pyspark pytest
```

## Part 1: Test the Detector

```python
import sys
sys.path.insert(0, '/path/to/real-time-fraud-detection-streaming/src')

from detector import FraudDetector

detector = FraudDetector(amount_threshold=10000.0)

# Test 1: High-value transaction
tx1 = {'amount': 15000.0, 'merchant': 'amazon', 'billing_country': 'US', 'shipping_country': 'US'}
is_fraud, rule, score = detector.detect(tx1)
print(f"TX1: {is_fraud=}, {rule=}, {score=}")
# Expected: (True, 'AMOUNT_THRESHOLD', 40.0)

# Test 2: Suspicious merchant
tx2 = {'amount': 100.0, 'merchant': 'fraud_co', 'billing_country': 'US', 'shipping_country': 'US'}
is_fraud, rule, score = detector.detect(tx2)
print(f"TX2: {is_fraud=}, {rule=}, {score=}")
# Expected: (True, 'BLACKLIST_MERCHANT', 35.0)

# Test 3: Clean transaction
tx3 = {'amount': 50.0, 'merchant': 'starbucks', 'billing_country': 'US', 'shipping_country': 'US'}
is_fraud, rule, score = detector.detect(tx3)
print(f"TX3: {is_fraud=}, {rule=}, {score=}")
# Expected: (False, 'CLEAN', 0.0)
```

## Part 2: Produce Transactions to Kafka

```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Sample transactions
transactions = [
    {'tx_id': 'tx-001', 'amount': 50.0, 'merchant': 'amazon', 'billing_country': 'US', 'shipping_country': 'US'},
    {'tx_id': 'tx-002', 'amount': 20000.0, 'merchant': 'premium_shop', 'billing_country': 'US', 'shipping_country': 'US'},
    {'tx_id': 'tx-003', 'amount': 100.0, 'merchant': 'fraud_co', 'billing_country': 'US', 'shipping_country': 'US'},
]

for tx in transactions:
    producer.send('transactions', tx)
    print(f"Sent: {tx}")

producer.flush()
```

## Part 3: Consume Alerts

```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'alerts',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    max_poll_records=10
)

for msg in consumer:
    alert = msg.value
    print(f"Alert: {alert}")
```

## Part 4: Analyze Detector Performance

```python
import pandas as pd
from collections import Counter

# Run detector on sample data
test_cases = [
    # (description, transaction)
    ('Clean low-value', {'amount': 50.0, 'merchant': 'amazon'}),
    ('High-value', {'amount': 15000.0}),
    ('Blacklisted merchant', {'amount': 100.0, 'merchant': 'fraud_co'}),
    ('Country mismatch', {'amount': 500.0, 'billing_country': 'US', 'shipping_country': 'RU'}),
    ('Multiple red flags', {'amount': 20000.0, 'merchant': 'bad_merchant', 'billing_country': 'US', 'shipping_country': 'IR', '3d_secure': False}),
]

results = []
for desc, tx in test_cases:
    is_fraud, rule, score = detector.detect(tx)
    results.append({'description': desc, 'is_fraud': is_fraud, 'rule': rule, 'risk_score': score})

df = pd.DataFrame(results)
print(df.to_string(index=False))
```

## Part 5: Performance Metrics

```python
# Measure latency
import time

times = []
for _ in range(1000):
    tx = {'amount': 100.0, 'merchant': 'test'}
    start = time.time()
    detector.detect(tx)
    times.append((time.time() - start) * 1000)  # ms

print(f"Detection latency:")
print(f"  Mean: {sum(times)/len(times):.3f}ms")
print(f"  p99: {sorted(times)[int(len(times)*0.99)]:.3f}ms")
print(f"  Max: {max(times):.3f}ms")
```

## Part 6: Real-World Scenario

```python
# Simulate a fraud ring
import datetime

fraud_ring = [
    {'tx_id': f'ring-{i}', 'amount': 5000.0 + i*100, 'merchant': 'suspicious_shop', 'cardholder_id': 'ch-ring-001', 'timestamp': datetime.datetime.now().isoformat()}
    for i in range(5)
]

print("Fraud ring transactions:")
for tx in fraud_ring:
    is_fraud, rule, score = detector.detect(tx)
    status = '🚨 ALERT' if is_fraud else '✓ CLEAN'
    print(f"  {status} {tx['tx_id']}: ${tx['amount']:.2f} - {rule} ({score})")
```

## Summary

This notebook demonstrates:
1. ✅ Unit testing the detector logic
2. ✅ Producing transactions to Kafka
3. ✅ Consuming alerts from Kafka
4. ✅ Performance characteristics (latency < 5ms per transaction)
5. ✅ Real-world fraud scenarios

For full documentation, see [README.md](../README.md).
