"""Test Apple verifier."""
import os

import pytest
from unittest.mock import patch
import jwt
from ..apple_verifier import AppleVerifier

@pytest.fixture
def apple_verifier() -> AppleVerifier:
    """Create an AppleVerifier instance for testing."""
    return AppleVerifier()

def test_apple_verifier_verify_signature_success(apple_verifier: AppleVerifier) -> None:
    """Test successful signature verification."""
    test_data = {
        'transactionId': '1234567890',
        'payload': 'test_payload'
    }
    test_signature = 'valid_signature'
    
    with patch('jwt.decode') as mock_decode:
        mock_decode.return_value = {'valid': True}
        result = apple_verifier.verify_signature(test_data, test_signature)
        assert result is True
        mock_decode.assert_called_once_with(
            test_signature,
            'test_apple_key',
            algorithms=['ES256'],
            audience=test_data['transactionId']
        )

def test_apple_verifier_verify_signature_failure(apple_verifier: AppleVerifier) -> None:
    """Test failed signature verification."""
    test_data = {
        'transactionId': '1234567890',
        'payload': 'test_payload'
    }
    test_signature = 'invalid_signature'
    
    with patch('jwt.decode') as mock_decode:
        mock_decode.side_effect = jwt.exceptions.InvalidSignatureError('Invalid signature')
        result = apple_verifier.verify_signature(test_data, test_signature)
        assert result is False
        mock_decode.assert_called_once_with(
            test_signature,
            'test_apple_key',
            algorithms=['ES256'],
            audience=test_data['transactionId']
        ) 