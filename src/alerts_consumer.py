"""Kafka consumer for fraud alerts."""

import json
import argparse
import logging
from kafka import KafkaConsumer
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def consume_alerts(bootstrap_server: str, topic: str, group_id: str = 'alert-consumer'):
    """
    Consume fraud alerts from Kafka topic.
    
    Args:
        bootstrap_server: Kafka broker address (e.g., 'localhost:9092')
        topic: Kafka topic name (e.g., 'alerts')
        group_id: Consumer group ID
    """
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_server,
        group_id=group_id,
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        max_poll_records=100
    )

    logger.info(f"Connected to Kafka. Consuming from topic '{topic}'. Press Ctrl+C to exit.")
    
    try:
        for message in consumer:
            alert = message.value
            timestamp = datetime.fromisoformat(alert.get('timestamp', 'N/A'))
            
            # Pretty-print alert
            print(f"\n{'='*80}")
            print(f"🚨 FRAUD ALERT")
            print(f"{'='*80}")
            print(f"  Alert ID:     {alert.get('alert_id')}")
            print(f"  Transaction:  {alert.get('tx_id')}")
            print(f"  Cardholder:   {alert.get('cardholder_id')}")
            print(f"  Amount:       ${alert.get('amount', 0):.2f}")
            print(f"  Risk Score:   {alert.get('risk_score', 0):.1f}/100")
            print(f"  Rule:         {alert.get('rule', 'UNKNOWN')}")
            print(f"  Action:       {alert.get('action', 'ALERT').upper()}")
            print(f"  Timestamp:    {timestamp}")
            print(f"{'='*80}\n")
            
    except KeyboardInterrupt:
        logger.info("Shutting down alert consumer.")
    finally:
        consumer.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bootstrap-server', default='localhost:9092',
                        help='Kafka bootstrap server')
    parser.add_argument('--topic', default='alerts',
                        help='Kafka topic for alerts')
    parser.add_argument('--group-id', default='alert-consumer',
                        help='Consumer group ID')
    args = parser.parse_args()
    
    consume_alerts(args.bootstrap_server, args.topic, args.group_id)
