"""Unit tests for fraud detector logic."""

import pytest
from src.detector import FraudDetector


@pytest.fixture
def detector():
    """Fixture for FraudDetector instance."""
    return FraudDetector(amount_threshold=10000.0)


class TestBasicDetection:
    """Test basic fraud detection rules."""

    def test_high_amount_triggers_alert(self, detector):
        """Test that high-value transaction triggers alert."""
        tx = {'amount': 20000.0}
        is_fraud, rule, score = detector.detect(tx)
        assert is_fraud is True
        assert rule == 'AMOUNT_THRESHOLD'
        assert score >= 40

    def test_clean_low_amount(self, detector):
        """Test that low-value transaction passes."""
        tx = {'amount': 50.0, 'merchant': 'good_shop'}
        is_fraud, rule, score = detector.detect(tx)
        assert is_fraud is False
        assert rule == 'CLEAN'

    def test_blacklist_merchant(self, detector):
        """Test blacklisted merchant detection."""
        tx = {
            'amount': 100.0,
            'merchant': 'fraud_co',
            'billing_country': 'US',
            'shipping_country': 'US'
        }
        is_fraud, rule, score = detector.detect(tx)
        assert is_fraud is True
        assert rule == 'BLACKLIST_MERCHANT'

    def test_country_mismatch(self, detector):
        """Test country mismatch detection."""
        tx = {
            'amount': 500.0,
            'merchant': 'good_shop',
            'billing_country': 'US',
            'shipping_country': 'RU'
        }
        is_fraud, rule, score = detector.detect(tx)
        assert is_fraud is False  # Not critical unless amount high
        assert 'CLEAN' in rule or 'COUNTRY' in rule


class TestRiskScoring:
    """Test risk score calculation."""

    def test_single_rule_risk_score(self, detector):
        """Test risk score for single rule trigger."""
        tx = {'amount': 20000.0}
        is_fraud, rule, score = detector.detect(tx)
        assert 40 <= score <= 100

    def test_multi_rule_cumulative_score(self, detector):
        """Test cumulative risk scoring."""
        tx = {
            'amount': 20000.0,
            'merchant': 'fraud_co',
            'billing_country': 'US',
            'shipping_country': 'RU',
            '3d_secure': False
        }
        is_fraud, rule, score = detector.detect(tx)
        assert score > 60  # Multiple rules trigger
        assert is_fraud is True

    def test_risk_score_capped_at_100(self, detector):
        """Test that risk score is capped at 100."""
        tx = {
            'amount': 50000.0,
            'merchant': 'fraud_co',
            'billing_country': 'US',
            'shipping_country': 'RU',
            '3d_secure': False
        }
        is_fraud, rule, score = detector.detect(tx)
        assert score <= 100.0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_invalid_amount_type(self, detector):
        """Test handling of invalid amount."""
        tx = {'amount': 'invalid', 'merchant': 'good_shop'}
        is_fraud, rule, score = detector.detect(tx)
        assert is_fraud is True  # Treated as suspicious

    def test_missing_fields(self, detector):
        """Test transaction with missing fields."""
        tx = {'tx_id': 'tx-001'}  # Minimal tx
        is_fraud, rule, score = detector.detect(tx)
        assert rule == 'CLEAN'  # Defaults are safe

    def test_none_values(self, detector):
        """Test handling of None values."""
        tx = {
            'amount': 100.0,
            'merchant': None,
            'billing_country': None,
            'shipping_country': None
        }
        is_fraud, rule, score = detector.detect(tx)
        assert is_fraud is False

    def test_empty_string_merchant(self, detector):
        """Test empty string merchant."""
        tx = {
            'amount': 50.0,
            'merchant': '',
            'billing_country': 'US',
            'shipping_country': 'US'
        }
        is_fraud, rule, score = detector.detect(tx)
        assert is_fraud is False


class TestCustomThresholds:
    """Test detector with custom thresholds."""

    def test_custom_amount_threshold(self):
        """Test detector with custom amount threshold."""
        detector = FraudDetector(amount_threshold=5000.0)
        tx = {'amount': 7000.0}
        is_fraud, rule, score = detector.detect(tx)
        assert is_fraud is True

    def test_low_custom_threshold(self):
        """Test detector with very low threshold."""
        detector = FraudDetector(amount_threshold=100.0)
        tx = {'amount': 150.0}
        is_fraud, rule, score = detector.detect(tx)
        assert is_fraud is True


class TestRealWorldScenarios:
    """Test realistic transaction scenarios."""

    def test_normal_online_transaction(self, detector):
        """Test typical legitimate online transaction."""
        tx = {
            'tx_id': 'tx-001',
            'amount': 99.99,
            'merchant': 'amazon',
            'merchant_category': 'online_retail',
            'billing_country': 'US',
            'shipping_country': 'US',
            'card_id': 'card-123',
            'device_id': 'device-456',
            'is_online': True,
            '3d_secure': True
        }
        is_fraud, rule, score = detector.detect(tx)
        assert is_fraud is False
        assert score < 30

    def test_high_value_international_transaction(self, detector):
        """Test high-value international transaction."""
        tx = {
            'tx_id': 'tx-002',
            'amount': 25000.0,
            'merchant': 'luxury_retailer',
            'merchant_category': 'jewelry',
            'billing_country': 'GB',
            'shipping_country': 'GB',
            '3d_secure': True
        }
        is_fraud, rule, score = detector.detect(tx)
        assert is_fraud is True  # High amount triggers alert
        assert score >= 40

    def test_suspicious_transaction_pattern(self, detector):
        """Test transaction matching multiple suspicious patterns."""
        tx = {
            'tx_id': 'tx-003',
            'amount': 15000.0,
            'merchant': 'bad_merchant',
            'merchant_category': 'weapons',
            'billing_country': 'US',
            'shipping_country': 'RU',
            'card_id': 'card-999',
            '3d_secure': False
        }
        is_fraud, rule, score = detector.detect(tx)
        assert is_fraud is True
        assert score > 60  # Multiple rule triggers
