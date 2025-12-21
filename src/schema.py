"""Kafka schema definitions for transactions and alerts."""

from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType, BooleanType, TimestampType

TRANSACTION_SCHEMA = StructType([
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

ALERT_SCHEMA = StructType([
    StructField('alert_id', StringType(), False),
    StructField('tx_id', StringType(), False),
    StructField('timestamp', TimestampType(), False),
    StructField('cardholder_id', StringType(), False),
    StructField('amount', DoubleType(), False),
    StructField('rule', StringType(), False),
    StructField('risk_score', DoubleType(), False),
    StructField('action', StringType(), False),  # ALERT, DECLINE, REVIEW
])
