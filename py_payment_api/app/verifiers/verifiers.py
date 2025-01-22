"""Verifier instances for payment providers."""
from .apple_verifier import AppleVerifier
from .google_verifier import GoogleVerifier
from .coinbase_verifier import CoinbaseVerifier
from .paypal_verifier import PayPalVerifier
from .coinsub_verifier import CoinsubVerifier

__all__ = [
    'apple_verifier',
    'google_verifier',
    'coinbase_verifier',
    'paypal_verifier',
    'coinsub_verifier'
]

# Create verifier instances during import
apple_verifier = AppleVerifier()
google_verifier = GoogleVerifier()
coinbase_verifier = CoinbaseVerifier()
paypal_verifier = PayPalVerifier()
coinsub_verifier = CoinsubVerifier()