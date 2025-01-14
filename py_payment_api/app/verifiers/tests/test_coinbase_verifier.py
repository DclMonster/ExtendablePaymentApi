import pytest
from ..coinbase_verifier import CoinbaseVerifier

# Example test case for CoinbaseVerifier
@pytest.fixture
def coinbase_verifier():
    return CoinbaseVerifier()

# Example test case for verifying signature
def test_coinbase_verifier_verify_signature(coinbase_verifier):
    result = coinbase_verifier.verify_signature('data', 'signature')
    assert result is True 