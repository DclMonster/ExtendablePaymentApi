import pytest
from unittest.mock import MagicMock, patch
from ..google_verifier import GoogleVerifier

# Example test case for GoogleVerifier
@pytest.fixture
def google_verifier() -> GoogleVerifier:
    return GoogleVerifier()

# Example test case for verifying signature
def test_google_verifier_verify_signature(google_verifier: GoogleVerifier) -> None:
    test_data = {'orderId': '1234567890', 'packageName': 'com.test.app'}
    test_signature = 'valid_signature'
    
    with patch('jwt.decode', return_value={'orderId': '1234567890'}) as mock_decode:
        result = google_verifier.verify_signature(test_data, test_signature)
        assert result is True
        mock_decode.assert_called_once_with(
            test_signature,
            google_verifier._secret,
            algorithms=['RS256']
        )