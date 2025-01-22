import pytest
from ..payment_provider import PaymentProvider

def test_payment_provider_values() -> None:
    """Test PaymentProvider enum values."""
    assert PaymentProvider.APPLE == "apple"
    assert PaymentProvider.GOOGLE == "google"
    assert PaymentProvider.PAYPAL == "paypal"
    assert PaymentProvider.COINBASE == "coinbase"
    assert PaymentProvider.COINSUB == "coinsub"

def test_payment_provider_members() -> None:
    """Test PaymentProvider enum members."""
    providers = list(PaymentProvider)
    assert len(providers) == 5
    assert all(isinstance(p, PaymentProvider) for p in providers)

def test_payment_provider_from_string() -> None:
    """Test PaymentProvider creation from string."""
    assert PaymentProvider("apple") == PaymentProvider.APPLE
    assert PaymentProvider("google") == PaymentProvider.GOOGLE
    assert PaymentProvider("paypal") == PaymentProvider.PAYPAL
    assert PaymentProvider("coinbase") == PaymentProvider.COINBASE
    assert PaymentProvider("coinsub") == PaymentProvider.COINSUB 