"""Enhanced fraud detector with rule-based and statistical detection."""

import json
from typing import Dict, Any, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Blacklisted merchants (known fraudulent or high-risk)
BLACKLIST_MERCHANTS = {
    'suspicious_shop', 'fraud_co', 'bad_merchant',
    'stolen_goods_inc', 'darknet_market'
}

# Whitelist of trusted merchants (bypass some checks)
WHITELIST_MERCHANTS = {
    'amazon', 'apple', 'microsoft', 'bank_of_america', 'chase'
}

# Suspicious categories
SUSPICIOUS_CATEGORIES = {
    'gambling', 'adult_content', 'weapons', 'money_transfer'
}


class FraudDetector:
    """Rule-based fraud detector for transaction streams."""

    def __init__(self, amount_threshold: float = 10000.0, 
                 card_velocity_threshold: int = 5, 
                 geographic_velocity_threshold: int = 3600):
        """
        Initialize fraud detector.
        
        Args:
            amount_threshold: High transaction amount threshold ($)
            card_velocity_threshold: Max transactions in short window
            geographic_velocity_threshold: Max time between transactions from different countries (seconds)
        """
        self.amount_threshold = amount_threshold
        self.card_velocity_threshold = card_velocity_threshold
        self.geographic_velocity_threshold = geographic_velocity_threshold

    def detect(self, tx: Dict[str, Any]) -> Tuple[bool, str, float]:
        """
        Detect fraudulent transaction.
        
        Args:
            tx: Transaction record (dict)
            
        Returns:
            Tuple of (is_fraud, rule_triggered, risk_score) where:
            - is_fraud: bool, True if fraud suspected
            - rule_triggered: str, name of rule (or 'CLEAN')
            - risk_score: float, 0-100 risk percentile
        """
        rules = []
        risk_score = 0.0

        # Rule 1: Amount threshold
        if self._check_amount(tx):
            rules.append('AMOUNT_THRESHOLD')
            risk_score += 40

        # Rule 2: Blacklisted merchant
        if self._check_blacklist(tx):
            rules.append('BLACKLIST_MERCHANT')
            risk_score += 35

        # Rule 3: Suspicious category
        if self._check_category(tx):
            rules.append('SUSPICIOUS_CATEGORY')
            risk_score += 25

        # Rule 4: Geographic velocity (impossible travel)
        if self._check_geographic_velocity(tx):
            rules.append('GEOGRAPHIC_VELOCITY')
            risk_score += 50

        # Rule 5: Missing 3D Secure on high-risk
        if self._check_3d_secure(tx):
            rules.append('NO_3D_SECURE')
            risk_score += 15

        # Rule 6: Country mismatch (billing ≠ shipping)
        if self._check_country_mismatch(tx):
            rules.append('COUNTRY_MISMATCH')
            risk_score += 20

        # Cap risk score at 100
        risk_score = min(risk_score, 100.0)

        # Fraud if any critical rule triggered or cumulative score > 60
        is_fraud = len(rules) > 0 and (
            'AMOUNT_THRESHOLD' in rules or
            'BLACKLIST_MERCHANT' in rules or
            'GEOGRAPHIC_VELOCITY' in rules or
            risk_score > 60
        )

        rule_name = rules[0] if rules else 'CLEAN'
        return is_fraud, rule_name, risk_score

    def _check_amount(self, tx: Dict) -> bool:
        """Check if transaction amount exceeds threshold."""
        try:
            amount = float(tx.get('amount', 0))
            return amount >= self.amount_threshold
        except (ValueError, TypeError):
            return True

    def _check_blacklist(self, tx: Dict) -> bool:
        """Check if merchant is blacklisted."""
        merchant = (tx.get('merchant') or '').lower()
        merchant_id = (tx.get('merchant_id') or '').lower()
        
        return merchant in BLACKLIST_MERCHANTS or merchant_id in BLACKLIST_MERCHANTS

    def _check_category(self, tx: Dict) -> bool:
        """Check if merchant category is suspicious."""
        category = (tx.get('merchant_category') or '').lower()
        return category in SUSPICIOUS_CATEGORIES

    def _check_geographic_velocity(self, tx: Dict) -> bool:
        """Check for impossible travel (geographic velocity)."""
        # In real system, would check distance/time against cardholder history
        # Simplified: flag if shipping != billing and high amount
        billing_country = tx.get('billing_country')
        shipping_country = tx.get('shipping_country')
        
        if billing_country and shipping_country and billing_country != shipping_country:
            amount = float(tx.get('amount', 0))
            # Only flag if unusual combo (e.g., US billed to shipping in Russia)
            if amount > 1000 and billing_country == 'US' and shipping_country in {'RU', 'KP', 'IR'}:
                return True
        return False

    def _check_3d_secure(self, tx: Dict) -> bool:
        """Check if high-risk transaction lacks 3D Secure."""
        amount = float(tx.get('amount', 0))
        has_3d = tx.get('3d_secure', False)
        
        # Flag if high amount without 3D Secure
        return amount > 5000 and not has_3d

    def _check_country_mismatch(self, tx: Dict) -> bool:
        """Check for billing/shipping country mismatch."""
        billing = tx.get('billing_country')
        shipping = tx.get('shipping_country')
        
        if billing and shipping:
            return billing != shipping
        return False


# Singleton instance for use in Spark UDF
_detector = FraudDetector()


def is_suspicious(tx_json: str) -> bool:
    """
    Spark UDF wrapper: parse JSON and detect fraud.
    
    Args:
        tx_json: JSON string of transaction
        
    Returns:
        True if fraud detected, False otherwise
    """
    try:
        tx = json.loads(tx_json)
        is_fraud, _, _ = _detector.detect(tx)
        return is_fraud
    except Exception as e:
        logger.error(f"Error detecting fraud: {e}")
        return False


def get_risk_score(tx_json: str) -> float:
    """Spark UDF: return risk score (0-100)."""
    try:
        tx = json.loads(tx_json)
        _, _, score = _detector.detect(tx)
        return score
    except Exception as e:
        logger.error(f"Error calculating risk score: {e}")
        return 50.0  # Default to medium risk on error
