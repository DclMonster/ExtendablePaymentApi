import pytest
from unittest.mock import MagicMock, patch
from ..coinbase_verifier import CoinbaseVerifier

# Example test case for CoinbaseVerifier
@pytest.fixture
def coinbase_verifier() -> CoinbaseVerifier:
    return CoinbaseVerifier()

# Example test case for verifying signature
def test_coinbase_verifier_verify_signature(coinbase_verifier: CoinbaseVerifier) -> None:
    test_data = {'id': '1234567890', 'data': 'test_data'}
    test_signature = 'valid_signature'
    
    with patch('hmac.compare_digest', return_value=True) as mock_compare:
        result = coinbase_verifier.verify_signature(test_data, test_signature)
        assert result is True
        mock_compare.assert_called_once() 