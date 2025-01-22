import hmac
import hashlib
import json
from .abstract.signature_verifier import SignatureVerifier
from typing import Dict, Any, Optional, cast

class CoinbaseVerifier(SignatureVerifier):
    """
    Verifier class for Coinbase webhook signatures.
    """

    def __init__(self) -> None:
        """
        Initializes the verifier with the secret from environment variables.
        """
        super().__init__('COINBASE_SECRET')

    def verify_signature(self, data: Dict[str, Any], signature: str) -> bool:
        """
        Verifies the signature of the webhook request.

        Parameters
        ----------
        data : Dict[str, Any]
            The raw request data.
        signature : str
            The signature from the request headers.

        Returns
        -------
        bool
            True if the signature is valid, False otherwise.
        """
        try:
            computed_signature = hmac.new(
                key=self._secret.encode(),
                msg=json.dumps(data).encode(),
                digestmod=hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(computed_signature, signature)
        except Exception as e:
            print(f"Signature verification failed: {str(e)}")
            return False

    def get_signature_from_header(self, header: Dict[str, Any]) -> str:
        """
        Extracts the signature from the header.

        Parameters
        ----------
        header : Dict[str, Any]
            The header containing the signature.

        Returns
        -------
        str
            The extracted signature.
        """
        return cast(str, header.get('CB-SIGNATURE', '')) 