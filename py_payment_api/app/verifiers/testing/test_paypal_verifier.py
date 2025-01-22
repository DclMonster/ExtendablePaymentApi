import pytest
from unittest.mock import MagicMock, patch
from cryptography.hazmat.primitives.asymmetric import rsa
from ..paypal_verifier import PayPalVerifier

# Example test case for PayPalVerifier
@pytest.fixture
def paypal_verifier() -> PayPalVerifier:
    with patch.dict('os.environ', {'PAYPAL_WEBHOOK_ID': 'WH-1234567890'}):
        return PayPalVerifier()

# Example test case for verifying signature
def test_paypal_verifier_verify_signature(paypal_verifier: PayPalVerifier) -> None:
    test_data = {
        'transmissionId': '1234567890',
        'timestamp': '2024-01-01T00:00:00Z',
        'certUrl': 'https://api.paypal.com/v1/notifications/certs/CERT-123',
        'authAlgo': 'SHA256withRSA',
        'transmission_sig': 'valid_signature',
        'webhookId': 'WH-1234567890',
        'eventBody': {'id': 'WH-EVENT-1234567890'}
    }
    
    mock_response = MagicMock()
    mock_response.content = b'-----BEGIN CERTIFICATE-----\nMIIFJjCCBA6gAwIBAgIQCGHBdPQ2...\n-----END CERTIFICATE-----'
    mock_response.raise_for_status = MagicMock()
    
    mock_cert = MagicMock()
    mock_public_key = MagicMock(spec=rsa.RSAPublicKey)
    mock_cert.public_key.return_value = mock_public_key
    mock_public_key.verify = MagicMock()
    
    mock_decoded_sig = b'decoded_signature'
    
    with patch('requests.get', return_value=mock_response) as mock_get:
        with patch('cryptography.x509.load_pem_x509_certificate', return_value=mock_cert) as mock_load_cert:
            with patch('base64.b64decode', return_value=mock_decoded_sig) as mock_decode:
                result = paypal_verifier.verify_signature(test_data, test_data['transmission_sig'])
                assert result is True
                mock_get.assert_called_once_with(test_data['certUrl'])
                mock_load_cert.assert_called_once()
                mock_decode.assert_called_once_with(test_data['transmission_sig'])