"""Real-time fraud detection streaming engine."""

__version__ = '1.0.0'
__author__ = 'techdevworks'

from .detector import FraudDetector, is_suspicious, get_risk_score

__all__ = [
    'FraudDetector',
    'is_suspicious',
    'get_risk_score',
]
