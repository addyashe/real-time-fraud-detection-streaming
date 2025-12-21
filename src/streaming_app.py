"""
Real-time fraud detection streaming application using PySpark.

Reads transaction stream from Kafka, applies fraud detection rules,
and outputs alerts to Kafka and storage backends.
"""

import argparse
import logging
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, BooleanType, TimestampType
from datetime import datetime
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Real-time fraud detection streaming app')
    parser.add_argument('--bootstrap-server', default='localhost:9092',
                        help='Kafka bootstrap server')
    parser.add_argument('--input-topic', default='transactions',
                        help='Input Kafka topic')
    parser.add_argument('--alert-topic', default='alerts',
                        help='Output Kafka topic for alerts')
    parser.add_argument('--checkpoint-dir', default='/tmp/fraud-checkpoint',
                        help='Checkpoint directory for fault tolerance')
    parser.add_argument('--threshold', type=float, default=10000.0,
                        help='Amount threshold for high-value transactions')
    parser.add_argument('--output-mode', default='append',
                        choices=['append', 'complete', 'update'],
                        help='Output mode for streaming query')
    parser.add_argument('--window-duration', default='1 minute',
                        help='Aggregation window duration')
    return parser.parse_args()


def create_spark_session(app_name='fraud_detection'):
    """Create Spark session with Kafka support."""
    return (SparkSession.builder
            .appName(app_name)
            .config('spark.sql.streaming.checkpointLocation', '/tmp/fraud-checkpoint')
            .config('spark.sql.adaptive.enabled', 'true')  # Enable Adaptive Query Execution
            .config('spark.sql.adaptive.coalescePartitions.enabled', 'true')
            .getOrCreate())


def main():
    args = parse_args()
    spark = create_spark_session()
    spark.sparkContext.setLogLevel('INFO')

    logger.info("Starting fraud detection streaming application...")
    logger.info(f"  Input topic: {args.input_topic}")
    logger.info(f"  Alert topic: {args.alert_topic}")
    logger.info(f"  Bootstrap server: {args.bootstrap_server}")

    # Define transaction schema
    transaction_schema = StructType([
        StructField('tx_id', StringType(), False),
        StructField('timestamp', TimestampType(), True),
        StructField('cardholder_id', StringType(), False),
        StructField('card_id', StringType(), False),
        StructField('amount', DoubleType(), False),
        StructField('currency', StringType(), True),
        StructField('merchant_id', StringType(), False),
        StructField('merchant', StringType(), True),
        StructField('merchant_category', StringType(), True),
        StructField('billing_country', StringType(), True),
        StructField('billing_city', StringType(), True),
        StructField('shipping_country', StringType(), True),
        StructField('shipping_city', StringType(), True),
        StructField('ip_address', StringType(), True),
        StructField('device_id', StringType(), True),
        StructField('is_online', BooleanType(), True),
        StructField('is_recurring', BooleanType(), True),
        StructField('3d_secure', BooleanType(), True),
    ])

    # Read from Kafka
    kafka_df = (spark.readStream
                .format('kafka')
                .option('kafka.bootstrap.servers', args.bootstrap_server)
                .option('subscribe', args.input_topic)
                .option('startingOffsets', 'latest')
                .load())

    logger.info("Connected to Kafka. Reading from stream...")

    # Parse JSON messages
    json_df = kafka_df.selectExpr("CAST(value AS STRING) as json_str")
    parsed_df = (json_df
                 .select(F.from_json(F.col('json_str'), transaction_schema).alias('data'))
                 .select('data.*'))

    # Fraud detection rules
    fraud_df = (parsed_df
                .withColumn('amount_flag', F.col('amount') >= F.lit(args.threshold))
                .withColumn('blacklist_flag', 
                           F.col('merchant').isin(['suspicious_shop', 'fraud_co', 'bad_merchant']))
                .withColumn('geo_velocity_flag',
                           (F.col('billing_country') != F.col('shipping_country')) &
                           (F.col('amount') > F.lit(1000)))
                .withColumn('country_mismatch_flag',
                           F.col('billing_country') != F.col('shipping_country'))
                .withColumn('no_3d_secure_flag',
                           (F.col('amount') > F.lit(5000)) & (F.col('3d_secure') == F.lit(False)))
                .withColumn('risk_score',
                           F.when(F.col('amount_flag'), 40)
                            .otherwise(0) +
                           F.when(F.col('blacklist_flag'), 35)
                            .otherwise(0) +
                           F.when(F.col('geo_velocity_flag'), 50)
                            .otherwise(0) +
                           F.when(F.col('country_mismatch_flag'), 20)
                            .otherwise(0) +
                           F.when(F.col('no_3d_secure_flag'), 15)
                            .otherwise(0)))

    # Identify frauds (critical rules or high cumulative risk)
    alerts_df = (fraud_df
                 .filter((F.col('amount_flag') | F.col('blacklist_flag') | F.col('geo_velocity_flag')) |
                        (F.col('risk_score') > 60))
                 .withColumn('alert_id', F.expr("uuid()"))
                 .withColumn('rule',
                            F.when(F.col('amount_flag'), 'AMOUNT_THRESHOLD')
                             .when(F.col('blacklist_flag'), 'BLACKLIST_MERCHANT')
                             .when(F.col('geo_velocity_flag'), 'GEOGRAPHIC_VELOCITY')
                             .otherwise('MULTI_RULE'))
                 .withColumn('action',
                            F.when(F.col('risk_score') > 80, 'DECLINE')
                             .when(F.col('risk_score') > 60, 'REVIEW')
                             .otherwise('ALERT'))
                 .withColumn('alert_timestamp', F.current_timestamp())
                 .select('alert_id', 'tx_id', 'alert_timestamp', 'cardholder_id', 
                        'amount', 'rule', 'risk_score', 'action'))

    # Write alerts to Kafka
    kafka_sink = (alerts_df
                  .select(F.to_json(F.struct('*')).alias('value'))
                  .writeStream
                  .format('kafka')
                  .option('kafka.bootstrap.servers', args.bootstrap_server)
                  .option('topic', args.alert_topic)
                  .option('checkpointLocation', f"{args.checkpoint_dir}/kafka")
                  .outputMode(args.output_mode))

    # Also write to console for demo/debugging
    console_sink = (alerts_df
                    .writeStream
                    .format('console')
                    .option('truncate', False)
                    .option('checkpointLocation', f"{args.checkpoint_dir}/console")
                    .outputMode(args.output_mode))

    # Start both sinks
    query_kafka = kafka_sink.start()
    logger.info(f"Writing alerts to Kafka topic '{args.alert_topic}'")

    query_console = console_sink.start()
    logger.info("Streaming alerts to console")

    # Await termination (runs until manually stopped)
    try:
        query_kafka.awaitTermination()
    except KeyboardInterrupt:
        logger.info("Shutting down streaming application...")
        query_kafka.stop()
        query_console.stop()


if __name__ == '__main__':
    main()
