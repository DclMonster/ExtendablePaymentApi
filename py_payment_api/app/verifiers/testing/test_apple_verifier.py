"""Test Apple verifier."""
import os
import time
from datetime import datetime, timedelta

import pytest
from unittest.mock import patch, MagicMock
import jwt
import requests
from typing import Dict, Any

from ..apple_verifier import AppleVerifier

@pytest.fixture
def mock_env_vars():
    """Set up mock environment variables for testing."""
    with patch.dict('os.environ', {
        'APPLE_PUBLIC_KEY': 'test_apple_key',
        'APPLE_KEY_ID': 'test_key_id',
        'APPLE_ISSUER_ID': 'test_issuer_id',
        'APPLE_BUNDLE_ID': 'com.test.app'
    }):
        yield

@pytest.fixture
def apple_verifier(mock_env_vars) -> AppleVerifier:
    """Create an AppleVerifier instance for testing."""
    return AppleVerifier()

@pytest.fixture
def mock_jwt_decode():
    """Mock JWT decode function."""
    with patch('jwt.decode') as mock:
        yield mock

@pytest.fixture
def mock_requests_post():
    """Mock requests.post function."""
    with patch('requests.post') as mock:
        yield mock

class TestAppleVerifierInit:
    def test_init_success(self, mock_env_vars):
        """Test successful initialization."""
        verifier = AppleVerifier()
        assert verifier._key_id == 'test_key_id'
        assert verifier._issuer_id == 'test_issuer_id'
        assert verifier._bundle_id == 'com.test.app'

    def test_init_missing_env_vars(self):
        """Test initialization with missing environment variables."""
        with pytest.raises(ValueError, match="Missing required Apple configuration in environment variables"):
            AppleVerifier()

class TestAppleVerifierSignature:
    def test_verify_signature_success(self, apple_verifier: AppleVerifier, mock_jwt_decode):
        """Test successful signature verification."""
        test_data = {
            'transactionId': '1234567890',
            'payload': 'test_payload'
        }
        test_signature = 'valid_signature'
        
        mock_jwt_decode.return_value = {
            'iss': 'Apple Inc.',
            'iat': int(time.time()),
            'exp': int(time.time()) + 3600,
            'aud': '1234567890'
        }
        
        result = apple_verifier.verify_signature(test_data, test_signature)
        assert result is True
        mock_jwt_decode.assert_called_once_with(
            test_signature,
            'test_apple_key',
            algorithms=['ES256'],
            audience=test_data['transactionId'],
            options={
                'verify_exp': True,
                'verify_aud': True,
                'verify_iss': True
            }
        )

    def test_verify_signature_invalid_signature(self, apple_verifier: AppleVerifier, mock_jwt_decode):
        """Test signature verification with invalid signature."""
        test_data = {'transactionId': '1234567890'}
        test_signature = 'invalid_signature'
        
        mock_jwt_decode.side_effect = jwt.InvalidSignatureError
        result = apple_verifier.verify_signature(test_data, test_signature)
        assert result is False

    def test_verify_signature_expired_token(self, apple_verifier: AppleVerifier, mock_jwt_decode):
        """Test signature verification with expired token."""
        test_data = {'transactionId': '1234567890'}
        test_signature = 'expired_signature'
        
        mock_jwt_decode.side_effect = jwt.ExpiredSignatureError
        result = apple_verifier.verify_signature(test_data, test_signature)
        assert result is False

    def test_verify_signature_decode_error(self, apple_verifier: AppleVerifier, mock_jwt_decode):
        """Test signature verification with decode error."""
        test_data = {'transactionId': '1234567890'}
        test_signature = 'malformed_signature'
        
        mock_jwt_decode.side_effect = jwt.DecodeError
        result = apple_verifier.verify_signature(test_data, test_signature)
        assert result is False

    def test_verify_signature_invalid_payload(self, apple_verifier: AppleVerifier, mock_jwt_decode):
        """Test signature verification with invalid payload."""
        test_data = {'transactionId': '1234567890'}
        test_signature = 'valid_signature'
        
        mock_jwt_decode.return_value = {
            'iss': 'Not Apple Inc.',  # Invalid issuer
            'iat': int(time.time()),
            'exp': int(time.time()) + 3600,
            'aud': '1234567890'
        }
        
        result = apple_verifier.verify_signature(test_data, test_signature)
        assert result is False

class TestAppleVerifierHeaders:
    def test_get_signature_from_header_success(self, apple_verifier: AppleVerifier):
        """Test successful signature extraction from headers."""
        headers = {'x-apple-signature': 'valid_signature'}
        signature = apple_verifier.get_signature_from_header(headers)
        assert signature == 'valid_signature'

    def test_get_signature_from_header_missing(self, apple_verifier: AppleVerifier):
        """Test signature extraction with missing header."""
        headers = {}
        with pytest.raises(ValueError, match="Missing Apple signature in headers"):
            apple_verifier.get_signature_from_header(headers)

    def test_get_signature_from_header_invalid_type(self, apple_verifier: AppleVerifier):
        """Test signature extraction with invalid signature type."""
        headers = {'x-apple-signature': ['invalid', 'type']}
        with pytest.raises(ValueError, match="Invalid Apple signature format"):
            apple_verifier.get_signature_from_header(headers)

class TestAppleVerifierReceipt:
    def test_verify_receipt_success(self, apple_verifier: AppleVerifier, mock_requests_post):
        """Test successful receipt verification."""
        receipt_data = "base64_encoded_receipt"
        expected_response = {'status': 0, 'receipt': {'in_app': []}}
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_response
        mock_requests_post.return_value = mock_response

        result = apple_verifier.verify_receipt(receipt_data)
        assert result == expected_response
        
        mock_requests_post.assert_called_once_with(
            f"{AppleVerifier._APPLE_STORE_CONNECT_API}/receipts/verify",
            headers={
                'Authorization': pytest.approx(str, rel=None),  # Token will be dynamic
                'Content-Type': 'application/json'
            },
            json={'receipt-data': receipt_data, 'password': 'test_apple_key'}
        )

    def test_verify_receipt_failure(self, apple_verifier: AppleVerifier, mock_requests_post):
        """Test receipt verification failure."""
        receipt_data = "invalid_receipt"
        
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Invalid receipt"
        mock_requests_post.return_value = mock_response

        with pytest.raises(ValueError, match="Receipt verification failed: Invalid receipt"):
            apple_verifier.verify_receipt(receipt_data)

    def test_verify_receipt_network_error(self, apple_verifier: AppleVerifier, mock_requests_post):
        """Test receipt verification with network error."""
        receipt_data = "base64_encoded_receipt"
        mock_requests_post.side_effect = requests.RequestException("Network error")

        with pytest.raises(ValueError, match="Receipt verification error: Network error"):
            apple_verifier.verify_receipt(receipt_data)

class TestAppleVerifierToken:
    def test_generate_api_token(self, apple_verifier: AppleVerifier):
        """Test API token generation."""
        token = apple_verifier._generate_api_token()
        
        # Decode and verify the token
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        assert decoded['iss'] == 'test_issuer_id'
        assert decoded['aud'] == 'appstoreconnect-v1'
        assert decoded['bid'] == 'com.test.app'
        assert 'iat' in decoded
        assert 'exp' in decoded
        assert decoded['exp'] - decoded['iat'] == 3600  # 1 hour expiration

        # Verify the token header
        header = jwt.get_unverified_header(token)
        assert header['kid'] == 'test_key_id'
        assert header['alg'] == 'ES256' 