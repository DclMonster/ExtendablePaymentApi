import pytest
from ..signature_verifier import SignatureVerifier
from typing import Dict, Any, cast
# Example concrete implementation for testing
class TestSignatureVerifier(SignatureVerifier):

    def __init__(self, signature: bool) -> None:
        self.signature = signature

    def verify_signature(self, data: Dict[str, Any], signature: str) -> bool:
        return self.signature

    def get_signature_from_header(self, header: Dict[str, Any]) -> str:
        return cast(str, header.get('Signature', ''))

# Example test case for SignatureVerifier
@pytest.fixture
def signature_verifier() -> TestSignatureVerifier:
    return TestSignatureVerifier(True)

# Test for verify_header_signature method
def test_verify_header_signature(signature_verifier: TestSignatureVerifier) -> None:
    """Test verifying header signature."""
    header = {'Signature': 'test_signature'}
    data = {'data': 'test_data'}
    
    # Test successful verification
    result = signature_verifier.verify_header_signature(data, header)
    assert result is True
    
    signature_verifier.signature = False
    # Test missing signature
    with pytest.raises(ValueError, match='Bad signature'):
        signature_verifier.verify_header_signature(data, {})