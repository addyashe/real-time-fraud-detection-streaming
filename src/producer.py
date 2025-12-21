import json
import time
import argparse
from kafka import KafkaProducer


def load_transactions(path):
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def produce(bootstrap_server, topic, file, rate=1):
    producer = KafkaProducer(bootstrap_servers=bootstrap_server,
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    for tx in load_transactions(file):
        producer.send(topic, tx)
        print(f"Sent: {tx}")
        time.sleep(1.0 / rate)
    producer.flush()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bootstrap-server', default='localhost:9092')
    parser.add_argument('--topic', default='transactions')
    parser.add_argument('--file', default='sample_data/transactions.json')
    parser.add_argument('--rate', type=float, default=1.0, help='transactions per second')
    args = parser.parse_args()
    produce(args.bootstrap_server, args.topic, args.file, rate=args.rate)
